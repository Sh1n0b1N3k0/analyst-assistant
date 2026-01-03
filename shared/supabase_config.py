"""Конфигурация Supabase."""
from pydantic_settings import BaseSettings
from supabase import create_client, Client
from typing import Optional


class SupabaseSettings(BaseSettings):
    """Настройки Supabase."""
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: Optional[str] = None  # Для server-side операций
    
    class Config:
        env_file = ".env"
        case_sensitive = False


supabase_settings = SupabaseSettings()


class SupabaseClient:
    """Клиент Supabase."""
    
    _client: Optional[Client] = None
    _service_client: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Optional[Client]:
        """Получить обычный клиент Supabase."""
        if not supabase_settings.supabase_url or not supabase_settings.supabase_key:
            return None
        
        if cls._client is None:
            cls._client = create_client(
                supabase_settings.supabase_url,
                supabase_settings.supabase_key
            )
        return cls._client
    
    @classmethod
    def get_service_client(cls) -> Optional[Client]:
        """Получить service client для server-side операций."""
        if not supabase_settings.supabase_url:
            return None
        
        service_key = supabase_settings.supabase_service_key or supabase_settings.supabase_key
        
        if cls._service_client is None:
            cls._service_client = create_client(
                supabase_settings.supabase_url,
                service_key
            )
        return cls._service_client
    
    @classmethod
    def is_available(cls) -> bool:
        """Проверить доступность Supabase."""
        return bool(supabase_settings.supabase_url and supabase_settings.supabase_key)


# Глобальный экземпляр
supabase = SupabaseClient.get_client()
supabase_service = SupabaseClient.get_service_client()

