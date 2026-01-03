"""Тесты для retry логики."""
import pytest
import time
from shared.retry import retry, RetryError


def test_retry_success():
    """Тест успешного выполнения без retry."""
    call_count = [0]
    
    @retry(max_attempts=3)
    def successful_function():
        call_count[0] += 1
        return "success"
    
    result = successful_function()
    
    assert result == "success"
    assert call_count[0] == 1


def test_retry_with_failure_then_success():
    """Тест retry с последующим успехом."""
    call_count = [0]
    
    @retry(max_attempts=3, delay=0.1)
    def flaky_function():
        call_count[0] += 1
        if call_count[0] < 2:
            raise ValueError("Temporary error")
        return "success"
    
    result = flaky_function()
    
    assert result == "success"
    assert call_count[0] == 2


def test_retry_exhausted():
    """Тест исчерпания попыток retry."""
    call_count = [0]
    
    @retry(max_attempts=3, delay=0.1)
    def always_failing_function():
        call_count[0] += 1
        raise ValueError("Always fails")
    
    with pytest.raises(RetryError) as exc_info:
        always_failing_function()
    
    assert call_count[0] == 3
    assert "Failed after 3 attempts" in str(exc_info.value)


def test_retry_with_specific_exceptions():
    """Тест retry только для определенных исключений."""
    call_count = [0]
    
    @retry(max_attempts=3, delay=0.1, exceptions=(ValueError,))
    def function_with_wrong_exception():
        call_count[0] += 1
        raise TypeError("Wrong exception type")
    
    with pytest.raises(TypeError):
        function_with_wrong_exception()
    
    # Должна быть только одна попытка, так как TypeError не в списке исключений для retry
    assert call_count[0] == 1

