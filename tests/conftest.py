"""Конфигурация pytest."""
import pytest
import sys
from pathlib import Path

# Добавить корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Мокировать переменные окружения."""
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USER", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "test-password")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


@pytest.fixture
def sample_requirement_data():
    """Пример данных требования."""
    return {
        "id": "req-123",
        "identifier": "REQ-001",
        "name": "User Authentication",
        "shall": "The system shall authenticate users using email and password",
        "category": "functional",
        "priority": 1,
        "status": "draft",
        "description": "User authentication requirement",
        "entities": [
            {"name": "User", "type": "actor"},
            {"name": "System", "type": "component"}
        ]
    }


@pytest.fixture
def sample_project_data():
    """Пример данных проекта."""
    return {
        "id": "proj-123",
        "name": "Test Project",
        "description": "Test project description",
        "methodology": "Agile",
        "status": "active"
    }

