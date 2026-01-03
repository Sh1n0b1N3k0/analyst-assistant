"""Middleware для безопасности и rate limiting."""
import time
from typing import Callable, Dict
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from shared.logging_config import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для rate limiting."""
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests: Dict[str, list] = defaultdict(list)
        self.hour_requests: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработать запрос с проверкой rate limit."""
        # Получить IP адрес клиента
        client_ip = request.client.host if request.client else "unknown"
        
        # Пропустить health check и другие системные endpoints
        if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        current_time = time.time()
        
        # Проверка лимита в минуту
        self.minute_requests[client_ip] = [
            req_time for req_time in self.minute_requests[client_ip]
            if current_time - req_time < 60
        ]
        
        if len(self.minute_requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip} (per minute)")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Проверка лимита в час
        self.hour_requests[client_ip] = [
            req_time for req_time in self.hour_requests[client_ip]
            if current_time - req_time < 3600
        ]
        
        if len(self.hour_requests[client_ip]) >= self.requests_per_hour:
            logger.warning(f"Rate limit exceeded for {client_ip} (per hour)")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Добавить текущий запрос
        self.minute_requests[client_ip].append(current_time)
        self.hour_requests[client_ip].append(current_time)
        
        # Добавить заголовки с информацией о лимитах
        response = await call_next(request)
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            self.requests_per_minute - len(self.minute_requests[client_ip])
        )
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            self.requests_per_hour - len(self.hour_requests[client_ip])
        )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления security headers."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Добавить security headers к ответу."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Удалить информацию о сервере
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Логировать запрос и ответ."""
        start_time = time.time()
        
        # Логировать запрос
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
                "query_params": dict(request.query_params),
            }
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Логировать ответ
            logger.info(
                f"Response: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": process_time,
                }
            )
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "process_time": process_time,
                },
                exc_info=True
            )
            raise

