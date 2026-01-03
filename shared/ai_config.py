"""Общая конфигурация ИИ агентов для всех сервисов."""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from enum import Enum


class ModelProvider(str, Enum):
    """Поддерживаемые провайдеры ИИ моделей."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    AZURE_OPENAI = "azure_openai"
    OPENROUTER = "openrouter"


class AISettings(BaseSettings):
    """Настройки ИИ агентов."""
    
    # Базовый провайдер
    provider: ModelProvider = Field(default=ModelProvider.OPENAI, validation_alias="AI_PROVIDER")
    
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", validation_alias="AI_OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, validation_alias="AI_OPENAI_TEMPERATURE")
    openai_max_tokens: Optional[int] = Field(default=None, validation_alias="AI_OPENAI_MAX_TOKENS")
    
    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-opus-20240229", validation_alias="AI_ANTHROPIC_MODEL")
    anthropic_temperature: float = Field(default=0.7, validation_alias="AI_ANTHROPIC_TEMPERATURE")
    
    # Azure OpenAI
    azure_openai_api_key: Optional[str] = Field(default=None, validation_alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: Optional[str] = Field(default=None, validation_alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment_name: Optional[str] = Field(default=None, validation_alias="AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_openai_api_version: str = Field(default="2024-02-15-preview", validation_alias="AZURE_OPENAI_API_VERSION")
    azure_openai_model: Optional[str] = Field(default=None, validation_alias="AI_AZURE_OPENAI_MODEL")
    azure_openai_temperature: float = Field(default=0.7, validation_alias="AI_AZURE_OPENAI_TEMPERATURE")
    
    # OpenRouter
    openrouter_api_key: Optional[str] = Field(default=None, validation_alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", validation_alias="OPENROUTER_BASE_URL")
    openrouter_model: Optional[str] = Field(default=None, validation_alias="AI_OPENROUTER_MODEL")
    openrouter_temperature: float = Field(default=0.7, validation_alias="AI_OPENROUTER_TEMPERATURE")
    
    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434", validation_alias="AI_OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama2", validation_alias="AI_OLLAMA_MODEL")
    ollama_temperature: float = Field(default=0.7, validation_alias="AI_OLLAMA_TEMPERATURE")
    
    # Настройки для разных агентов
    # Project Admin
    project_admin_provider: Optional[ModelProvider] = Field(default=None, validation_alias="AI_PROJECT_ADMIN_PROVIDER")
    project_admin_model: Optional[str] = Field(default=None, validation_alias="AI_PROJECT_ADMIN_MODEL")
    project_admin_api_key: Optional[str] = Field(default=None, validation_alias="AI_PROJECT_ADMIN_API_KEY")
    project_admin_temperature: Optional[float] = Field(default=None, validation_alias="AI_PROJECT_ADMIN_TEMPERATURE")
    
    # Requirement Processor
    requirement_processor_provider: Optional[ModelProvider] = Field(default=None, validation_alias="AI_REQUIREMENT_PROCESSOR_PROVIDER")
    requirement_processor_model: Optional[str] = Field(default=None, validation_alias="AI_REQUIREMENT_PROCESSOR_MODEL")
    requirement_processor_api_key: Optional[str] = Field(default=None, validation_alias="AI_REQUIREMENT_PROCESSOR_API_KEY")
    requirement_processor_temperature: Optional[float] = Field(default=None, validation_alias="AI_REQUIREMENT_PROCESSOR_TEMPERATURE")
    
    # Knowledge Base
    knowledge_base_provider: Optional[ModelProvider] = Field(default=None, validation_alias="AI_KNOWLEDGE_BASE_PROVIDER")
    knowledge_base_model: Optional[str] = Field(default=None, validation_alias="AI_KNOWLEDGE_BASE_MODEL")
    knowledge_base_api_key: Optional[str] = Field(default=None, validation_alias="AI_KNOWLEDGE_BASE_API_KEY")
    knowledge_base_temperature: Optional[float] = Field(default=None, validation_alias="AI_KNOWLEDGE_BASE_TEMPERATURE")
    
    # Spec Generator
    spec_generator_provider: Optional[ModelProvider] = Field(default=None, validation_alias="AI_SPEC_GENERATOR_PROVIDER")
    spec_generator_model: Optional[str] = Field(default=None, validation_alias="AI_SPEC_GENERATOR_MODEL")
    spec_generator_api_key: Optional[str] = Field(default=None, validation_alias="AI_SPEC_GENERATOR_API_KEY")
    spec_generator_temperature: Optional[float] = Field(default=None, validation_alias="AI_SPEC_GENERATOR_TEMPERATURE")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }
    
    def get_config_for_agent(self, agent_name: str) -> dict:
        """Получить конфигурацию для конкретного агента."""
        provider_attr = f"{agent_name}_provider"
        model_attr = f"{agent_name}_model"
        api_key_attr = f"{agent_name}_api_key"
        temperature_attr = f"{agent_name}_temperature"
        
        # Получить провайдер (агент-специфичный или базовый)
        provider = getattr(self, provider_attr, None) or self.provider
        
        # Получить модель (агент-специфичная или по умолчанию для провайдера)
        model = getattr(self, model_attr, None) or self._get_default_model(provider)
        
        # Получить API ключ (приоритет: агент-специфичный > провайдер-специфичный)
        agent_api_key = getattr(self, api_key_attr, None)
        api_key = agent_api_key or self._get_api_key(provider)
        
        # Получить температуру (агент-специфичная или по умолчанию)
        agent_temperature = getattr(self, temperature_attr, None)
        temperature = agent_temperature if agent_temperature is not None else self._get_default_temperature(provider)
        
        # Получить base_url и дополнительные параметры
        base_url = self._get_base_url(provider)
        extra_params = self._get_extra_params(provider)
        
        config = {
            "provider": provider,
            "model": model,
            "temperature": temperature,
            "api_key": api_key,
        }
        
        if base_url:
            config["base_url"] = base_url
        
        # Добавить дополнительные параметры для специфичных провайдеров
        config.update(extra_params)
        
        return config
    
    def _get_default_model(self, provider: ModelProvider) -> str:
        """Получить модель по умолчанию для провайдера."""
        defaults = {
            ModelProvider.OPENAI: self.openai_model,
            ModelProvider.ANTHROPIC: self.anthropic_model,
            ModelProvider.OLLAMA: self.ollama_model,
        }
        return defaults.get(provider, self.openai_model)
    
    def _get_default_temperature(self, provider: ModelProvider) -> float:
        """Получить температуру по умолчанию."""
        defaults = {
            ModelProvider.OPENAI: self.openai_temperature,
            ModelProvider.ANTHROPIC: self.anthropic_temperature,
            ModelProvider.OLLAMA: self.ollama_temperature,
        }
        return defaults.get(provider, 0.7)
    
    def _get_api_key(self, provider: ModelProvider) -> Optional[str]:
        """Получить API ключ для провайдера."""
        keys = {
            ModelProvider.OPENAI: self.openai_api_key,
            ModelProvider.ANTHROPIC: self.anthropic_api_key,
            ModelProvider.AZURE_OPENAI: self.azure_openai_api_key,
            ModelProvider.OPENROUTER: self.openrouter_api_key,
            ModelProvider.OLLAMA: None,  # Ollama не требует API ключ
        }
        return keys.get(provider)
    
    def _get_base_url(self, provider: ModelProvider) -> Optional[str]:
        """Получить базовый URL для провайдера."""
        urls = {
            ModelProvider.OPENAI: None,  # Используется стандартный URL
            ModelProvider.ANTHROPIC: None,  # Используется стандартный URL
            ModelProvider.AZURE_OPENAI: self.azure_openai_endpoint,
            ModelProvider.OPENROUTER: self.openrouter_base_url,
            ModelProvider.OLLAMA: self.ollama_base_url,
        }
        return urls.get(provider)
    
    def _get_extra_params(self, provider: ModelProvider) -> dict:
        """Получить дополнительные параметры для специфичных провайдеров."""
        if provider == ModelProvider.AZURE_OPENAI:
            return {
                "azure_endpoint": self.azure_openai_endpoint,
                "azure_deployment": self.azure_openai_deployment_name or self._get_default_model(provider),
                "api_version": self.azure_openai_api_version,
            }
        return {}


ai_settings = AISettings()

