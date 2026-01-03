"""API Gateway - единая точка входа для всех сервисов."""
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    print("Starting API Gateway...")
    yield
    # Shutdown
    print("Shutting down API Gateway...")


app = FastAPI(
    title="Requirements Management System API",
    version="1.0.0",
    description="Система управления требованиями к программному обеспечению",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров сервисов
app.include_router(project_admin_router)
app.include_router(requirement_processor_router)
app.include_router(knowledge_base_router)
app.include_router(prompt_store_router)

# Использовать Supabase API если доступен, иначе обычный PostgreSQL API
if SUPABASE_AVAILABLE and SupabaseClient and SupabaseClient.is_available():
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

