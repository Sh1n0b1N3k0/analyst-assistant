"""Менеджер синхронизации между Supabase и Neo4j."""
from typing import Dict, Any, Optional
try:
    from shared.supabase_config import SupabaseClient
except ImportError:
    SupabaseClient = None

from services.knowledge_base.graph_rag import KnowledgeBaseGraph
import asyncio
from datetime import datetime


class SyncManager:
    """Управление синхронизацией данных между Supabase и Neo4j."""
    
    def __init__(self):
        """Инициализация менеджера синхронизации."""
        self.supabase = SupabaseClient.get_service_client()
        self.graph = KnowledgeBaseGraph()
    
    def sync_requirement_to_graph(self, requirement_data: Dict[str, Any], project_id: str) -> bool:
        """Синхронизировать требование из Supabase в Neo4j."""
        if not self.graph.available:
            return False
        
        try:
            # Импорт требования в граф
            req_id = self.graph.import_requirement(requirement_data, project_id)
            
            # Обновить метаданные синхронизации в Supabase (если есть таблица sync_status)
            if self.supabase:
                try:
                    self.supabase.table("requirement_sync_status").upsert({
                        "requirement_id": requirement_data.get("id"),
                        "synced_to_graph": True,
                        "synced_at": datetime.utcnow().isoformat(),
                        "graph_node_id": req_id
                    }).execute()
                except:
                    pass  # Таблица может не существовать
            
            return True
        except Exception as e:
            print(f"Error syncing requirement to graph: {e}")
            return False
    
    def sync_requirement_from_graph(self, requirement_id: str) -> Optional[Dict]:
        """Получить данные требования из графа для синхронизации обратно в Supabase."""
        if not self.graph.available:
            return None
        
        try:
            # Получить связанные требования из графа
            related = self.graph.get_related_requirements(requirement_id)
            
            # Получить дубликаты
            req_data = {"id": requirement_id}
            duplicates = self.graph.find_duplicates(req_data)
            
            # Получить конфликты
            conflicts = self.graph.find_conflicts(requirement_id)
            
            return {
                "related_requirements": related,
                "duplicates": duplicates,
                "conflicts": conflicts
            }
        except Exception as e:
            print(f"Error syncing from graph: {e}")
            return None
    
    def batch_sync_requirements(self, project_id: str) -> Dict[str, Any]:
        """Пакетная синхронизация всех требований проекта."""
        if not self.supabase:
            return {"success": False, "error": "Supabase not available"}
        
        try:
            # Получить все требования проекта из Supabase
            response = self.supabase.table("requirements").select("*").eq(
                "project_id", project_id
            ).execute()
            
            requirements = response.data if response.data else []
            
            synced = 0
            failed = 0
            
            for req in requirements:
                if self.sync_requirement_to_graph(req, project_id):
                    synced += 1
                else:
                    failed += 1
            
            return {
                "success": True,
                "synced": synced,
                "failed": failed,
                "total": len(requirements)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Глобальный экземпляр
sync_manager = SyncManager()

