"""Хранилище промптов в Supabase."""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
import uuid
import json
from shared.supabase_config import SupabaseClient


class PromptTemplate(BaseModel):
    """Шаблон промпта."""
    id: str
    name: str
    description: str
    agent_type: str
    prompt_type: str
    template: str
    variables: List[str]
    version: int
    is_active: bool
    metadata: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str


class SupabasePromptStore:
    """Хранилище промптов в Supabase."""
    
    def __init__(self):
        """Инициализация хранилища."""
        self.supabase = SupabaseClient.get_service_client()
        self.schema = "prompts"  # Отдельная схема для промптов
        self._ensure_schema_exists()
        self._load_default_prompts()
    
    def _ensure_schema_exists(self):
        """Создать схему prompts если не существует."""
        if not self.supabase:
            return
        
        # Создание схемы через SQL (выполняется один раз)
        # В production это должно быть в миграции
        try:
            # Проверка существования схемы через запрос
            result = self.supabase.rpc("check_schema_exists", {"schema_name": self.schema}).execute()
        except:
            # Схема не существует, нужно создать через миграцию
            pass
    
    def _load_default_prompts(self):
        """Загрузить промпты по умолчанию если их нет."""
        if not self.supabase:
            return
        
        # Проверить, есть ли уже промпты
        try:
            result = self.supabase.table(f"{self.schema}.prompts").select("id").limit(1).execute()
            if result.data:
                return  # Промпты уже есть
        except Exception as e:
            # Таблица не существует или схема не создана
            print(f"Schema or table not found: {e}. Please run migration first.")
            return
        
        # Загрузить промпты по умолчанию
        default_prompts = self._get_default_prompts()
        for prompt_data in default_prompts:
            try:
                # Убедиться, что variables в правильном формате
                if isinstance(prompt_data.get("variables"), list):
                    prompt_data["variables"] = prompt_data["variables"]
                if isinstance(prompt_data.get("metadata"), dict):
                    prompt_data["metadata"] = prompt_data["metadata"]
                
                self.supabase.table(f"{self.schema}.prompts").insert(prompt_data).execute()
            except Exception as e:
                print(f"Error loading default prompt {prompt_data.get('id', 'unknown')}: {e}")
    
    def _get_default_prompts(self) -> List[Dict[str, Any]]:
        """Получить промпты по умолчанию."""
        now = datetime.utcnow().isoformat()
        
        return [
            {
                "id": "project_admin_analyze",
                "name": "Анализ проекта",
                "description": "Промпт для анализа проекта и генерации рекомендаций",
                "agent_type": "project_admin",
                "prompt_type": "analysis",
                "template": """You are an expert project manager and business analyst.
Your task is to analyze project parameters and provide recommendations for:
1. Project structure and organization
2. Methodology best practices
3. Team composition suggestions
4. Timeline and milestone recommendations
5. Risk identification
6. Requirements management workflow

Project data:
{project_data}

Return the analysis as JSON with structure:
{{
    "recommendations": ["recommendation1", "recommendation2"],
    "suggested_structure": {{...}},
    "risks": ["risk1", "risk2"],
    "methodology_suggestions": "...",
    "team_roles": ["role1", "role2"]
}}""",
                "variables": ["project_data"],
                "version": 1,
                "is_active": True,
                "metadata": {"temperature": 0.7},
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "requirement_processor_formalize",
                "name": "Формализация требования",
                "description": "Промпт для формализации неформализованного требования",
                "agent_type": "requirement_processor",
                "prompt_type": "formalization",
                "template": """You are an expert business analyst specializing in requirement formalization according to ISO/IEC/IEEE 29148 standard.

Your task is to convert informal, unstructured requirements into formal, structured requirements.

Analyze the input requirement and extract:
1. Clear, concise identifier (e.g., REQ-001)
2. Name (brief title)
3. Shall statement (formal requirement statement)
4. Rationale (why this requirement exists)
5. Verification method (how to verify the requirement)
6. Category (functional, non_functional, business, technical)
7. Priority (1-5, where 1 is highest)
8. Source (stakeholder, regulation, etc.)
9. Acceptance criteria (list of criteria)
10. Tags (relevant tags)
11. Entities involved (actors, data objects, processes)
12. Estimated effort (if possible)

Informal requirement:
{informal_text}

Context:
{context}

Return the formalized requirement as a JSON object.""",
                "variables": ["informal_text", "context"],
                "version": 1,
                "is_active": True,
                "metadata": {"temperature": 0.7},
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "knowledge_base_duplicates",
                "name": "Анализ дубликатов",
                "description": "Промпт для анализа дубликатов требований",
                "agent_type": "knowledge_base",
                "prompt_type": "duplicate_analysis",
                "template": """You are an expert in requirement analysis.
Analyze if the new requirement is a duplicate of any existing requirements.
Consider semantic similarity, not just exact text matches.

New requirement:
{new_requirement}

Existing requirements:
{existing_requirements}

Return JSON:
{{
    "is_duplicate": true/false,
    "duplicate_of": ["requirement_id1", "requirement_id2"],
    "similarity_score": 0.0-1.0,
    "reason": "explanation"
}}""",
                "variables": ["new_requirement", "existing_requirements"],
                "version": 1,
                "is_active": True,
                "metadata": {"temperature": 0.5},
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "knowledge_base_conflicts",
                "name": "Анализ противоречий",
                "description": "Промпт для анализа противоречий между требованиями",
                "agent_type": "knowledge_base",
                "prompt_type": "conflict_analysis",
                "template": """You are an expert in requirement analysis.
Identify conflicts and contradictions between requirements.

Requirement to check:
{requirement}

Other requirements:
{other_requirements}

Return JSON:
{{
    "has_conflicts": true/false,
    "conflicts": [
        {{
            "requirement_id": "...",
            "conflict_type": "contradiction|incompatibility|overlap",
            "description": "...",
            "severity": "low|medium|high|critical"
        }}
    ]
}}""",
                "variables": ["requirement", "other_requirements"],
                "version": 1,
                "is_active": True,
                "metadata": {"temperature": 0.5},
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "spec_generator_user_story",
                "name": "Генерация User Story",
                "description": "Промпт для генерации User Story",
                "agent_type": "spec_generator",
                "prompt_type": "user_story",
                "template": """You are an expert in writing User Stories.
Generate a well-structured User Story based on the requirement.
Follow the format: As a [actor], I want [action], So that [benefit].

Requirement:
{requirement}

Context:
{context}

Generate a User Story.""",
                "variables": ["requirement", "context"],
                "version": 1,
                "is_active": True,
                "metadata": {"temperature": 0.8},
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "spec_generator_rest_api",
                "name": "Генерация REST API",
                "description": "Промпт для генерации OpenAPI спецификации",
                "agent_type": "spec_generator",
                "prompt_type": "rest_api",
                "template": """You are an expert in API design.
Generate OpenAPI 3.0 specification (JSON format) for the requirement.
Include paths, methods, request/response schemas, and examples.

Requirement:
{requirement}

Context:
{context}

Generate OpenAPI 3.0 specification in JSON format.""",
                "variables": ["requirement", "context"],
                "version": 1,
                "is_active": True,
                "metadata": {"temperature": 0.7},
                "created_at": now,
                "updated_at": now,
            },
        ]
    
    def get_prompt(self, prompt_id: str) -> Optional[PromptTemplate]:
        """Получить промпт по ID."""
        if not self.supabase:
            return None
        
        try:
            result = self.supabase.table(f"{self.schema}.prompts").select("*").eq(
                "id", prompt_id
            ).eq("is_active", True).order("version", desc=True).limit(1).execute()
            
            if result.data:
                return PromptTemplate(**result.data[0])
            return None
        except Exception as e:
            print(f"Error getting prompt {prompt_id}: {e}")
            return None
    
    def get_prompts_by_agent(self, agent_type: str, prompt_type: Optional[str] = None) -> List[PromptTemplate]:
        """Получить промпты для агента."""
        if not self.supabase:
            return []
        
        try:
            # Использовать функцию для получения промптов агента
            result = self.supabase.rpc(
                "get_agent_prompts",
                {
                    "agent_type_param": agent_type,
                    "prompt_type_param": prompt_type
                }
            ).execute()
            
            if result.data:
                return [PromptTemplate(**p) for p in result.data]
            
            # Fallback на прямой запрос
            query = self.supabase.table(f"{self.schema}.prompts").select("*").eq(
                "agent_type", agent_type
            ).eq("is_active", True)
            
            if prompt_type:
                query = query.eq("prompt_type", prompt_type)
            
            result = query.order("version", desc=True).execute()
            
            # Группировать по id и взять последнюю версию каждого
            prompts_dict = {}
            for item in result.data:
                prompt_id = item["id"]
                if prompt_id not in prompts_dict or item["version"] > prompts_dict[prompt_id]["version"]:
                    prompts_dict[prompt_id] = item
            
            return [PromptTemplate(**p) for p in prompts_dict.values()]
        except Exception as e:
            print(f"Error getting prompts for agent {agent_type}: {e}")
            return []
    
    def get_active_prompt(self, agent_type: str, prompt_type: str) -> Optional[PromptTemplate]:
        """Получить активный промпт для агента и типа."""
        prompts = self.get_prompts_by_agent(agent_type, prompt_type)
        if prompts:
            # Возвращаем последнюю версию
            return max(prompts, key=lambda p: p.version)
        return None
    
    def render_prompt(self, prompt_id: str, variables: Dict[str, Any]) -> str:
        """Отрендерить промпт с переменными."""
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            raise ValueError(f"Prompt {prompt_id} not found")
        
        try:
            return prompt.template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing variable in prompt: {e}")
    
    def add_prompt(self, prompt: PromptTemplate):
        """Добавить новый промпт."""
        if not self.supabase:
            return
        
        try:
            prompt_dict = prompt.dict()
            # Преобразовать variables в JSONB формат
            if isinstance(prompt_dict.get("variables"), list):
                prompt_dict["variables"] = prompt_dict["variables"]
            if isinstance(prompt_dict.get("metadata"), dict):
                prompt_dict["metadata"] = prompt_dict["metadata"]
            
            self.supabase.table(f"{self.schema}.prompts").insert(prompt_dict).execute()
        except Exception as e:
            print(f"Error adding prompt: {e}")
            raise
    
    def update_prompt(self, prompt_id: str, updates: Dict[str, Any]) -> Optional[PromptTemplate]:
        """Обновить промпт (создает новую версию)."""
        if not self.supabase:
            return None
        
        # Получить текущую версию
        current = self.get_prompt(prompt_id)
        if not current:
            return None
        
        # Создать новую версию
        new_version = current.dict()
        new_version.update(updates)
        new_version["version"] = current.version + 1
        new_version["updated_at"] = datetime.utcnow().isoformat()
        new_version["created_at"] = current.created_at  # Сохранить оригинальную дату создания
        
        try:
            self.supabase.table(f"{self.schema}.prompts").insert(new_version).execute()
            return PromptTemplate(**new_version)
        except Exception as e:
            print(f"Error updating prompt: {e}")
            return None
    
    def list_prompts(self) -> List[PromptTemplate]:
        """Получить список всех промптов."""
        if not self.supabase:
            return []
        
        try:
            result = self.supabase.table(f"{self.schema}.prompts").select("*").eq(
                "is_active", True
            ).order("version", desc=True).execute()
            
            # Группировать по id и взять последнюю версию
            prompts_dict = {}
            for item in result.data:
                prompt_id = item["id"]
                if prompt_id not in prompts_dict or item["version"] > prompts_dict[prompt_id]["version"]:
                    prompts_dict[prompt_id] = item
            
            return [PromptTemplate(**p) for p in prompts_dict.values()]
        except Exception as e:
            print(f"Error listing prompts: {e}")
            return []


# Глобальный экземпляр (использует Supabase если доступен, иначе in-memory)
from shared.prompt_store import PromptStore as InMemoryPromptStore

def get_prompt_store():
    """Получить хранилище промптов (Supabase или in-memory)."""
    if SupabaseClient.is_available():
        return SupabasePromptStore()
    else:
        return InMemoryPromptStore()

# Глобальный экземпляр
prompt_store = get_prompt_store()

