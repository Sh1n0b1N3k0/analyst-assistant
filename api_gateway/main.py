"""API Gateway - единая точка входа для всех сервисов."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Импорт роутеров сервисов
from services.project_admin.api import router as project_admin_router
from services.requirement_processor.api import router as requirement_processor_router
from services.knowledge_base.api import router as knowledge_base_router
from services.prompt_store.api import router as prompt_store_router
from services.requirement_storage.api import router as requirement_storage_router
from services.requirement_storage.supabase_api import router as requirement_storage_supabase_router
from services.spec_generator.api import router as spec_generator_router
from shared.supabase_config import SupabaseClient
from shared.logging_config import get_logger, setup_logging
from shared.exceptions import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    AppException,
)
from shared.middleware import RateLimitMiddleware, SecurityHeadersMiddleware, LoggingMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

# Настроить логирование
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    logger.info("Starting API Gateway...")
    yield
    # Shutdown
    logger.info("Shutting down API Gateway...")


app = FastAPI(
    title="Requirements Management System API",
    version="1.0.0",
    description="Система управления требованиями к программному обеспечению",
    lifespan=lifespan
)

# CORS - безопасная конфигурация
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-RateLimit-Limit-Minute", "X-RateLimit-Remaining-Minute"],
)

# Добавить middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60, requests_per_hour=1000)

# Обработчики исключений
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Подключение роутеров сервисов
app.include_router(project_admin_router)
app.include_router(requirement_processor_router)
app.include_router(knowledge_base_router)
app.include_router(prompt_store_router)

# Использовать Supabase API если доступен, иначе обычный PostgreSQL API
if SupabaseClient and SupabaseClient.is_available():
    app.include_router(requirement_storage_supabase_router)
else:
    app.include_router(requirement_storage_router)

app.include_router(spec_generator_router)


@app.get("/")
async def root():
    """Корневой endpoint."""
    return {
        "message": "Requirements Management System API Gateway",
        "version": "1.0.0",
        "services": [
            "Project Admin",
            "Requirement Processor",
            "Knowledge Base",
            "Requirement Storage",
            "Specification Generator",
            "Prompt Store"
        ]
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

