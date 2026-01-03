"""Тесты для обработки исключений."""
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from shared.exceptions import (
    AppException,
    NotFoundError,
    ValidationError,
    DatabaseError,
    ExternalServiceError,
    app_exception_handler,
)


def test_app_exception():
    """Тест базового исключения приложения."""
    exc = AppException("Test error", status_code=400)
    assert exc.message == "Test error"
    assert exc.status_code == 400


def test_not_found_error():
    """Тест исключения NotFoundError."""
    exc = NotFoundError("Requirement", "req-123")
    assert "Requirement" in exc.message
    assert "req-123" in exc.message
    assert exc.status_code == 404


def test_validation_error():
    """Тест исключения ValidationError."""
    exc = ValidationError("Invalid input", {"field": "name"})
    assert exc.message == "Invalid input"
    assert exc.status_code == 400
    assert exc.details == {"field": "name"}


def test_database_error():
    """Тест исключения DatabaseError."""
    exc = DatabaseError("Connection failed")
    assert exc.message == "Connection failed"
    assert exc.status_code == 500


def test_external_service_error():
    """Тест исключения ExternalServiceError."""
    exc = ExternalServiceError("Neo4j", "Connection timeout")
    assert "Neo4j" in exc.message
    assert exc.status_code == 502


@pytest.mark.asyncio
async def test_app_exception_handler():
    """Тест обработчика исключений."""
    app = FastAPI()
    app.add_exception_handler(AppException, app_exception_handler)
    
    @app.get("/test")
    async def test_endpoint():
        raise NotFoundError("Resource", "123")
    
    client = TestClient(app)
    response = client.get("/test")
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "Resource" in data["error"]

