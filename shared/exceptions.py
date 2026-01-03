"""Кастомные исключения и обработчики ошибок."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any, Dict
from shared.logging_config import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    """Базовое исключение приложения."""
    def __init__(self, message: str, status_code: int = 500, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(AppException):
    """Ошибка базы данных."""
    def __init__(self, message: str = "Database error", details: Dict[str, Any] = None):
        super().__init__(message, status_code=500, details=details)


class NotFoundError(AppException):
    """Ресурс не найден."""
    def __init__(self, resource: str, resource_id: Any = None):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message, status_code=404)


class ValidationError(AppException):
    """Ошибка валидации."""
    def __init__(self, message: str = "Validation error", details: Dict[str, Any] = None):
        super().__init__(message, status_code=400, details=details)


class UnauthorizedError(AppException):
    """Ошибка авторизации."""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class ForbiddenError(AppException):
    """Ошибка доступа."""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)


class ExternalServiceError(AppException):
    """Ошибка внешнего сервиса."""
    def __init__(self, service: str, message: str = "External service error", details: Dict[str, Any] = None):
        full_message = f"{service}: {message}"
        super().__init__(full_message, status_code=502, details=details)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Обработчик кастомных исключений."""
    logger.error(
        f"AppException: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "path": request.url.path,
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Обработчик HTTP исключений."""
    logger.warning(
        f"HTTPException: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "path": request.url.path,
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Обработчик ошибок валидации."""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors(),
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "path": request.url.path,
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Обработчик общих исключений."""
    logger.exception(
        f"Unhandled exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "path": request.url.path,
        }
    )

