"""Конфигурация структурированного логирования."""
import logging
import sys
from typing import Optional
from pydantic_settings import BaseSettings


class LoggingSettings(BaseSettings):
    """Настройки логирования."""
    log_level: str = "INFO"
    log_format: str = "json"  # json или text
    log_file: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


logging_settings = LoggingSettings()


class JSONFormatter(logging.Formatter):
    """JSON форматтер для структурированного логирования."""
    def format(self, record: logging.LogRecord) -> str:
        import json
        from datetime import datetime
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Добавить exception info если есть
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Добавить extra поля
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


def setup_logging():
    """Настроить логирование для приложения."""
    # Получить уровень логирования
    level = getattr(logging, logging_settings.log_level.upper(), logging.INFO)
    
    # Создать форматтер
    if logging_settings.log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Настроить root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Удалить существующие handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (если указан)
    if logging_settings.log_file:
        file_handler = logging.FileHandler(logging_settings.log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Получить logger с указанным именем."""
    return logging.getLogger(name)


# Инициализировать логирование при импорте
setup_logging()

