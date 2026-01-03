"""Общая конфигурация базы данных."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from typing import Optional
try:
    from shared.supabase_config import SupabaseClient
except ImportError:
    SupabaseClient = None


class DatabaseSettings(BaseSettings):
    """Настройки базы данных."""
    # Для Supabase используем connection string из Supabase dashboard
    # Или можно использовать прямой PostgreSQL URL
    database_url: Optional[str] = None
    use_supabase: bool = True  # Использовать Supabase вместо прямого PostgreSQL
    
    class Config:
        env_file = ".env"
        case_sensitive = False


db_settings = DatabaseSettings()

# Определяем, использовать ли Supabase или прямой PostgreSQL
use_supabase = db_settings.use_supabase and SupabaseClient and SupabaseClient.is_available()

if use_supabase:
    # Для Supabase используем SQLAlchemy через connection string
    # Supabase предоставляет connection string в формате:
    # postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
    # Это можно получить из Supabase dashboard -> Settings -> Database
    from shared.supabase_config import supabase_settings
    
    # Если database_url не указан, пытаемся использовать Supabase connection string
    if not db_settings.database_url:
        # В production нужно будет указать SUPABASE_DB_URL в .env
        # Или использовать Supabase REST API вместо SQLAlchemy
        engine = None
        SessionLocal = None
    else:
        engine = create_engine(
            db_settings.database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # Прямое подключение к PostgreSQL
    database_url = db_settings.database_url or "postgresql://postgres:postgres@localhost:5432/requirements_db"
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """Dependency для получения сессии БД."""
    if SessionLocal is None:
        # Если используется Supabase без SQLAlchemy, возвращаем None
        # В этом случае нужно использовать Supabase client напрямую
        yield None
        return
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_supabase():
    """Dependency для получения Supabase клиента."""
    return SupabaseClient.get_service_client()

