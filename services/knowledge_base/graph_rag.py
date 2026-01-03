"""Graph RAG для хранения требований в виде графа."""
from neo4j import GraphDatabase
from typing import List, Dict, Optional, Any
from pydantic_settings import BaseSettings
import json


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
            self._create_constraints()
            self.available = True
        except Exception as e:
            print(f"Warning: Could not connect to Neo4j: {e}")
            self.driver = None
            self.available = False
    
    def _create_constraints(self):
        """Создать ограничения и индексы."""
        if not self.available or not self.driver:
            return
        
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
    
    def import_requirement(self, requirement_data: Dict[str, Any], project_id: str) -> str:
        """Импортировать требование в граф."""
        if not self.available or not self.driver:
            return requirement_data.get("id", "")
        
        req_id = requirement_data.get("id") or requirement_data.get("identifier", "")
        
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
        
        return req_id
    
    def find_duplicates(self, requirement_data: Dict[str, Any], threshold: float = 0.8) -> List[Dict]:
        """Найти дубликаты требования."""
        if not self.available or not self.driver:
            return []
        
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
            
            return [dict(record) for record in result]
    
    def find_conflicts(self, requirement_id: str) -> List[Dict]:
        """Найти противоречия требования."""
        if not self.available or not self.driver:
            return []
        
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
            
            return [dict(record) for record in result]
    
    def get_related_requirements(self, requirement_id: str, max_depth: int = 2) -> List[Dict]:
        """Получить связанные требования."""
        if not self.available or not self.driver:
            return []
        
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
            
            return [dict(record) for record in result]
    
    def close(self):
        """Закрыть подключение."""
        if self.driver:
            self.driver.close()

