"""Тесты для Graph RAG."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from services.knowledge_base.graph_rag import KnowledgeBaseGraph, Neo4jSettings
from shared.exceptions import ExternalServiceError, DatabaseError


@pytest.fixture
def mock_neo4j_driver():
    """Мок Neo4j драйвера."""
    driver = Mock()
    session = Mock()
    driver.session.return_value.__enter__.return_value = session
    driver.session.return_value.__exit__.return_value = None
    driver.verify_connectivity.return_value = True
    return driver


def test_knowledge_base_graph_init_success(mock_neo4j_driver, mock_env_vars):
    """Тест успешной инициализации KnowledgeBaseGraph."""
    with patch('services.knowledge_base.graph_rag.GraphDatabase.driver', return_value=mock_neo4j_driver):
        graph = KnowledgeBaseGraph()
        
        assert graph.available is True
        assert graph.driver is not None


def test_knowledge_base_graph_init_failure(mock_env_vars):
    """Тест неудачной инициализации KnowledgeBaseGraph."""
    with patch('services.knowledge_base.graph_rag.GraphDatabase.driver', side_effect=Exception("Connection failed")):
        graph = KnowledgeBaseGraph()
        
        assert graph.available is False
        assert graph.driver is None


def test_import_requirement_not_available(mock_env_vars):
    """Тест импорта требования когда Neo4j недоступен."""
    graph = KnowledgeBaseGraph()
    graph.available = False
    
    requirement_data = {
        "id": "req-123",
        "identifier": "REQ-001",
        "name": "Test Requirement"
    }
    
    result = graph.import_requirement(requirement_data, "proj-123")
    assert result == "req-123"


def test_find_duplicates_not_available(mock_env_vars):
    """Тест поиска дубликатов когда Neo4j недоступен."""
    graph = KnowledgeBaseGraph()
    graph.available = False
    
    requirement_data = {"name": "Test", "shall": "Test requirement"}
    result = graph.find_duplicates(requirement_data)
    
    assert result == []


def test_find_conflicts_not_available(mock_env_vars):
    """Тест поиска противоречий когда Neo4j недоступен."""
    graph = KnowledgeBaseGraph()
    graph.available = False
    
    result = graph.find_conflicts("req-123")
    
    assert result == []


def test_get_related_requirements_not_available(mock_env_vars):
    """Тест получения связанных требований когда Neo4j недоступен."""
    graph = KnowledgeBaseGraph()
    graph.available = False
    
    result = graph.get_related_requirements("req-123")
    
    assert result == []


def test_close_connection(mock_neo4j_driver, mock_env_vars):
    """Тест закрытия подключения."""
    with patch('services.knowledge_base.graph_rag.GraphDatabase.driver', return_value=mock_neo4j_driver):
        graph = KnowledgeBaseGraph()
        graph.close()
        
        mock_neo4j_driver.close.assert_called_once()

