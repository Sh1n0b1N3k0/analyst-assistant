"""Хранилище промптов для ИИ агентов."""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
import uuid
import json


class PromptTemplate(BaseModel):
    """Шаблон промпта."""
    id: str
    name: str
    description: str
    agent_type: str  # project_admin, requirement_processor, knowledge_base, spec_generator
    prompt_type: str  # system, user, analysis, generation, etc.
    template: str  # Шаблон с переменными {variable}
    variables: List[str]  # Список переменных в шаблоне
    version: int
    is_active: bool
    metadata: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str


class PromptStore:
    """Хранилище промптов."""
    
    def __init__(self):
        """Инициализация хранилища."""
        self.prompts: Dict[str, PromptTemplate] = {}
        self._load_default_prompts()
    
    def _load_default_prompts(self):
        """Загрузить промпты по умолчанию."""
        default_prompts = self._get_default_prompts()
        for prompt in default_prompts:
            self.prompts[prompt["id"]] = PromptTemplate(**prompt)
    
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
        return self.prompts.get(prompt_id)
    
    def get_prompts_by_agent(self, agent_type: str, prompt_type: Optional[str] = None) -> List[PromptTemplate]:
        """Получить промпты для агента."""
        prompts = [
            p for p in self.prompts.values()
            if p.agent_type == agent_type and p.is_active
        ]
        
        if prompt_type:
            prompts = [p for p in prompts if p.prompt_type == prompt_type]
        
        return prompts
    
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
        self.prompts[prompt.id] = prompt
    
    def update_prompt(self, prompt_id: str, updates: Dict[str, Any]) -> Optional[PromptTemplate]:
        """Обновить промпт."""
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            return None
        
        # Создать новую версию
        prompt_dict = prompt.dict()
        prompt_dict.update(updates)
        prompt_dict["version"] = prompt.version + 1
        prompt_dict["updated_at"] = datetime.utcnow().isoformat()
        
        updated_prompt = PromptTemplate(**prompt_dict)
        self.prompts[prompt_id] = updated_prompt
        
        return updated_prompt
    
    def list_prompts(self) -> List[PromptTemplate]:
        """Получить список всех промптов."""
        return list(self.prompts.values())


# Глобальный экземпляр (будет переопределен если Supabase доступен)
try:
    from shared.prompt_store_supabase import get_prompt_store
    prompt_store = get_prompt_store()
except ImportError:
    prompt_store = PromptStore()

