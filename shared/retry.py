"""Утилиты для retry логики при работе с внешними сервисами."""
import asyncio
import time
from typing import Callable, TypeVar, Optional, List, Type
from functools import wraps
from shared.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class RetryError(Exception):
    """Исключение при исчерпании попыток retry."""
    pass


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Декоратор для retry логики.
    
    Args:
        max_attempts: Максимальное количество попыток
        delay: Начальная задержка между попытками (в секундах)
        backoff: Множитель для увеличения задержки
        exceptions: Кортеж исключений, при которых нужно повторять попытку
        on_retry: Callback функция, вызываемая при каждой попытке
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"Retry exhausted for {func.__name__} after {max_attempts} attempts",
                            extra={
                                "function": func.__name__,
                                "attempt": attempt,
                                "error": str(e),
                            }
                        )
                        raise RetryError(f"Failed after {max_attempts} attempts: {str(e)}") from e
                    
                    logger.warning(
                        f"Retry attempt {attempt}/{max_attempts} for {func.__name__}",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "error": str(e),
                            "next_delay": current_delay,
                        }
                    )
                    
                    if on_retry:
                        on_retry(attempt, e)
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # Не должно доходить до сюда, но на всякий случай
            raise RetryError(f"Failed after {max_attempts} attempts") from last_exception
        
        return wrapper
    
    return decorator


async def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Асинхронный декоратор для retry логики.
    
    Args:
        max_attempts: Максимальное количество попыток
        delay: Начальная задержка между попытками (в секундах)
        backoff: Множитель для увеличения задержки
        exceptions: Кортеж исключений, при которых нужно повторять попытку
        on_retry: Callback функция, вызываемая при каждой попытке
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"Retry exhausted for {func.__name__} after {max_attempts} attempts",
                            extra={
                                "function": func.__name__,
                                "attempt": attempt,
                                "error": str(e),
                            }
                        )
                        raise RetryError(f"Failed after {max_attempts} attempts: {str(e)}") from e
                    
                    logger.warning(
                        f"Retry attempt {attempt}/{max_attempts} for {func.__name__}",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "error": str(e),
                            "next_delay": current_delay,
                        }
                    )
                    
                    if on_retry:
                        on_retry(attempt, e)
                    
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            # Не должно доходить до сюда, но на всякий случай
            raise RetryError(f"Failed after {max_attempts} attempts") from last_exception
        
        return wrapper
    
    return decorator

