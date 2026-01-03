"""Graph RAG для хранения требований в виде графа."""
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, TransientError
from typing import List, Dict, Optional, Any
from pydantic_settings import BaseSettings
import json
from shared.logging_config import get_logger
from shared.exceptions import ExternalServiceError, DatabaseError
from shared.retry import retry

logger = get_logger(__name__)


class Neo4jSettings(BaseSettings):
    """Настройки Neo4j."""
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


neo4j_settings = Neo4jSettings()


class KnowledgeBaseGraph:
    """Графовая база знаний требований."""
    
    def __init__(self):
        """Инициализация подключения к Neo4j."""
        try:
            self.driver = GraphDatabase.driver(
                neo4j_settings.neo4j_uri,
                auth=(neo4j_settings.neo4j_user, neo4j_settings.neo4j_password)
            )
            # Проверить подключение
            self.driver.verify_connectivity()
            self._create_constraints()
            self.available = True
            logger.info("Neo4j connection established")
        except Exception as e:
            logger.warning(f"Could not connect to Neo4j: {e}", exc_info=True)
            self.driver = None
            self.available = False
    
    def _create_constraints(self):
        """Создать ограничения и индексы."""
        if not self.available or not self.driver:
            return
        
        try:
            with self.driver.session() as session:
                # Ограничения уникальности
                session.run("""
                    CREATE CONSTRAINT IF NOT EXISTS FOR (r:Requirement) 
                    REQUIRE r.id IS UNIQUE
                """)
                session.run("""
                    CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) 
                    REQUIRE e.id IS UNIQUE
                """)
                
                # Индексы для полнотекстового поиска
                session.run("""
                    CREATE FULLTEXT INDEX requirementIndex IF NOT EXISTS
                    FOR (r:Requirement) ON EACH [r.name, r.shall, r.description]
                """)
                logger.info("Neo4j constraints and indexes created")
        except Exception as e:
            logger.error(f"Error creating Neo4j constraints: {e}", exc_info=True)
            raise DatabaseError(f"Failed to create Neo4j constraints: {str(e)}")
    
    @retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=(ServiceUnavailable, TransientError))
    def import_requirement(self, requirement_data: Dict[str, Any], project_id: str) -> str:
        """Импортировать требование в граф."""
        if not self.available or not self.driver:
            logger.warning("Neo4j not available, skipping requirement import")
            return requirement_data.get("id", "")
        
        req_id = requirement_data.get("id") or requirement_data.get("identifier", "")
        
        try:
            with self.driver.session() as session:
            session.run("""
                MERGE (r:Requirement {id: $id})
                SET r.project_id = $project_id,
                    r.identifier = $identifier,
                    r.name = $name,
                    r.shall = $shall,
                    r.category = $category,
                    r.priority = $priority,
                    r.status = $status,
                    r.description = $description,
                    r.created_at = datetime()
            """, 
                id=req_id,
                project_id=project_id,
                identifier=requirement_data.get("identifier", ""),
                name=requirement_data.get("name", ""),
                shall=requirement_data.get("shall", ""),
                category=requirement_data.get("category"),
                priority=requirement_data.get("priority"),
                status=requirement_data.get("status", "draft"),
                description=requirement_data.get("description", "")
            )
            
            # Создать узлы для сущностей
            entities = requirement_data.get("entities", [])
            for entity in entities:
                entity_id = f"entity_{req_id}_{entity.get('name', '').replace(' ', '_')}"
                session.run("""
                    MERGE (e:Entity {id: $entity_id})
                    SET e.name = $name,
                        e.type = $type,
                        e.created_at = datetime()
                    WITH e
                    MATCH (r:Requirement {id: $req_id})
                    MERGE (r)-[:INVOLVES]->(e)
                """,
                    entity_id=entity_id,
                    name=entity.get("name", ""),
                    type=entity.get("type", "unknown"),
                    req_id=req_id
                )
            
            logger.info(f"Requirement {req_id} imported to Neo4j")
            return req_id
        except (ServiceUnavailable, TransientError) as e:
            logger.error(f"Neo4j transient error importing requirement {req_id}: {e}")
            raise ExternalServiceError("Neo4j", f"Failed to import requirement: {str(e)}")
        except Exception as e:
            logger.error(f"Error importing requirement {req_id} to Neo4j: {e}", exc_info=True)
            raise DatabaseError(f"Failed to import requirement: {str(e)}")
    
    @retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=(ServiceUnavailable, TransientError))
    def find_duplicates(self, requirement_data: Dict[str, Any], threshold: float = 0.8) -> List[Dict]:
        """Найти дубликаты требования."""
        if not self.available or not self.driver:
            logger.warning("Neo4j not available, returning empty duplicates list")
            return []
        
        try:
            # Используем полнотекстовый поиск
            search_text = f"{requirement_data.get('name', '')} {requirement_data.get('shall', '')}"
            
            with self.driver.session() as session:
                result = session.run("""
                    CALL db.index.fulltext.queryNodes('requirementIndex', $query)
                    YIELD node, score
                    WHERE score > $threshold
                    RETURN node.id as id,
                           node.identifier as identifier,
                           node.name as name,
                           score
                    ORDER BY score DESC
                    LIMIT 10
                """, query=search_text, threshold=threshold)
                
                duplicates = [dict(record) for record in result]
                logger.debug(f"Found {len(duplicates)} potential duplicates")
                return duplicates
        except (ServiceUnavailable, TransientError) as e:
            logger.error(f"Neo4j transient error finding duplicates: {e}")
            raise ExternalServiceError("Neo4j", f"Failed to find duplicates: {str(e)}")
        except Exception as e:
            logger.error(f"Error finding duplicates: {e}", exc_info=True)
            raise DatabaseError(f"Failed to find duplicates: {str(e)}")
    
    @retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=(ServiceUnavailable, TransientError))
    def find_conflicts(self, requirement_id: str) -> List[Dict]:
        """Найти противоречия требования."""
        if not self.available or not self.driver:
            logger.warning("Neo4j not available, returning empty conflicts list")
            return []
        
        try:
            with self.driver.session() as session:
                # Поиск требований с противоположными формулировками
                result = session.run("""
                    MATCH (r:Requirement {id: $id})
                    MATCH (other:Requirement)
                    WHERE other.id <> $id
                    AND other.project_id = r.project_id
                    AND (
                        (r.category = 'functional' AND other.category = 'non_functional' AND 
                         r.shall CONTAINS 'must' AND other.shall CONTAINS 'must not') OR
                        (r.priority = 1 AND other.priority = 1 AND 
                         r.shall <> other.shall)
                    )
                    RETURN other.id as id,
                           other.identifier as identifier,
                           other.name as name,
                           other.shall as shall,
                           'potential_conflict' as conflict_type
                    LIMIT 20
                """, id=requirement_id)
                
                conflicts = [dict(record) for record in result]
                logger.debug(f"Found {len(conflicts)} potential conflicts for requirement {requirement_id}")
                return conflicts
        except (ServiceUnavailable, TransientError) as e:
            logger.error(f"Neo4j transient error finding conflicts: {e}")
            raise ExternalServiceError("Neo4j", f"Failed to find conflicts: {str(e)}")
        except Exception as e:
            logger.error(f"Error finding conflicts: {e}", exc_info=True)
            raise DatabaseError(f"Failed to find conflicts: {str(e)}")
    
    @retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=(ServiceUnavailable, TransientError))
    def get_related_requirements(self, requirement_id: str, max_depth: int = 2) -> List[Dict]:
        """Получить связанные требования."""
        if not self.available or not self.driver:
            logger.warning("Neo4j not available, returning empty related requirements list")
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH path = (r:Requirement {id: $id})-[*1..%d]-(related:Requirement)
                    RETURN DISTINCT related.id as id,
                           related.identifier as identifier,
                           related.name as name,
                           length(path) as distance
                    ORDER BY distance
                    LIMIT 20
                """ % max_depth, id=requirement_id)
                
                related = [dict(record) for record in result]
                logger.debug(f"Found {len(related)} related requirements for {requirement_id}")
                return related
        except (ServiceUnavailable, TransientError) as e:
            logger.error(f"Neo4j transient error getting related requirements: {e}")
            raise ExternalServiceError("Neo4j", f"Failed to get related requirements: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting related requirements: {e}", exc_info=True)
            raise DatabaseError(f"Failed to get related requirements: {str(e)}")
    
    def close(self):
        """Закрыть подключение."""
        if self.driver:
            try:
                self.driver.close()
                logger.info("Neo4j connection closed")
            except Exception as e:
                logger.error(f"Error closing Neo4j connection: {e}", exc_info=True)

