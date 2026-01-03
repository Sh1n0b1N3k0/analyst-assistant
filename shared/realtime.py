"""Supabase Realtime для обновлений в реальном времени."""
from typing import Callable, Optional
try:
    from shared.supabase_config import SupabaseClient
    from supabase import Client
except ImportError:
    SupabaseClient = None
    Client = None


class RealtimeManager:
    """Управление Realtime подписками Supabase."""
    
    def __init__(self):
        """Инициализация Realtime менеджера."""
        self.client: Optional[Client] = SupabaseClient.get_client()
        self.subscriptions = {}
    
    def subscribe_to_requirements(
        self,
        project_id: str,
        callback: Callable[[Dict], None]
    ) -> Optional[str]:
        """Подписаться на изменения требований проекта."""
        if not self.client:
            return None
        
        try:
            channel = self.client.realtime.channel(f"requirements:{project_id}")
            
            channel.on(
                "postgres_changes",
                {
                    "event": "*",
                    "schema": "public",
                    "table": "requirements",
                    "filter": f"project_id=eq.{project_id}"
                },
                callback
            )
            
            channel.subscribe()
            self.subscriptions[f"requirements:{project_id}"] = channel
            
            return f"requirements:{project_id}"
        except Exception as e:
            print(f"Error subscribing to requirements: {e}")
            return None
    
    def subscribe_to_projects(self, callback: Callable[[Dict], None]) -> Optional[str]:
        """Подписаться на изменения проектов."""
        if not self.client:
            return None
        
        try:
            channel = self.client.realtime.channel("projects")
            
            channel.on(
                "postgres_changes",
                {
                    "event": "*",
                    "schema": "public",
                    "table": "projects"
                },
                callback
            )
            
            channel.subscribe()
            self.subscriptions["projects"] = channel
            
            return "projects"
        except Exception as e:
            print(f"Error subscribing to projects: {e}")
            return None
    
    def unsubscribe(self, channel_id: str):
        """Отписаться от канала."""
        if channel_id in self.subscriptions:
            try:
                self.subscriptions[channel_id].unsubscribe()
                del self.subscriptions[channel_id]
            except Exception as e:
                print(f"Error unsubscribing: {e}")
    
    def unsubscribe_all(self):
        """Отписаться от всех каналов."""
        for channel_id in list(self.subscriptions.keys()):
            self.unsubscribe(channel_id)


# Глобальный экземпляр
realtime_manager = RealtimeManager()

