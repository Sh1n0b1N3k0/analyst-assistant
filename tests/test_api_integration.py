"""Integration тесты для API endpoints."""
import pytest
from fastapi.testclient import TestClient
from api_gateway.main import app


@pytest.fixture
def client():
    """Создать тестовый клиент."""
    return TestClient(app)


def test_root_endpoint(client):
    """Тест корневого endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "services" in data


def test_health_check(client):
    """Тест health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_cors_headers(client):
    """Тест CORS заголовков."""
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )
    
    # CORS должен быть настроен
    assert response.status_code in [200, 204]


def test_security_headers(client):
    """Тест security headers."""
    response = client.get("/health")
    
    assert "X-Content-Type-Options" in response.headers
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_rate_limit_headers(client):
    """Тест rate limit заголовков."""
    response = client.get("/health")
    
    # После первого запроса должны быть заголовки rate limit
    assert "X-RateLimit-Limit-Minute" in response.headers
    assert "X-RateLimit-Remaining-Minute" in response.headers


def test_process_time_header(client):
    """Тест заголовка времени обработки."""
    response = client.get("/health")
    
    assert "X-Process-Time" in response.headers
    process_time = float(response.headers["X-Process-Time"])
    assert process_time >= 0


def test_404_error(client):
    """Тест обработки 404 ошибки."""
    response = client.get("/nonexistent-endpoint")
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data or "detail" in data

