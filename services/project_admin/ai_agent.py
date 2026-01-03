"""ИИ агент для Администратора проекта."""
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any, Optional
from shared.ai_config import ai_settings, ModelProvider
from shared.prompt_store import prompt_store
import json


def create_llm(config: dict):
    """Создать LLM на основе конфигурации."""
    provider = config["provider"]
    model = config["model"]
    temperature = config["temperature"]
    api_key = config.get("api_key")
    base_url = config.get("base_url")
    
    if provider == ModelProvider.OPENAI:
        params = {
            "model": model,
            "api_key": api_key,
            "temperature": temperature,
        }
        if base_url:
            params["base_url"] = base_url
        return ChatOpenAI(**params)
    
    elif provider == ModelProvider.ANTHROPIC:
        return ChatAnthropic(
            model=model,
            anthropic_api_key=api_key,
            temperature=temperature,
        )
    
    elif provider == ModelProvider.AZURE_OPENAI:
        from langchain_openai import AzureChatOpenAI
        return AzureChatOpenAI(
            azure_endpoint=config.get("azure_endpoint"),
            azure_deployment=config.get("azure_deployment", model),
            api_version=config.get("api_version", "2024-02-15-preview"),
            api_key=api_key,
            temperature=temperature,
        )
    
    elif provider == ModelProvider.OPENROUTER:
        # OpenRouter использует OpenAI-совместимый API
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url or "https://openrouter.ai/api/v1",
            temperature=temperature,
        )
    
    elif provider == ModelProvider.OLLAMA:
        return ChatOllama(
            model=model,
            base_url=base_url,
            temperature=temperature,
        )
    
    else:
        return ChatOpenAI(
            model=model or "gpt-4-turbo-preview",
            api_key=api_key,
            temperature=temperature,
        )


class ProjectAdminAgent:
    """ИИ агент для анализа и рекомендаций по проектам."""
    
    def __init__(self):
        """Инициализация агента."""
        config = ai_settings.get_config_for_agent("project_admin")
        self.llm = create_llm(config)
    
    def analyze_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ проекта и генерация рекомендаций."""
        
        # Получить промпт из хранилища
        prompt_template = prompt_store.get_active_prompt("project_admin", "analysis")
        
        if prompt_template:
            # Использовать промпт из хранилища
            human_prompt = prompt_store.render_prompt(
                prompt_template.id,
                {"project_data": json.dumps(project_data, ensure_ascii=False, indent=2)}
            )
            system_prompt = ""  # Промпт уже содержит все инструкции
        else:
            # Fallback на встроенный промпт
            system_prompt = """You are an expert project manager and business analyst.
Your task is to analyze project parameters and provide recommendations for:
1. Project structure and organization
2. Methodology best practices
3. Team composition suggestions
4. Timeline and milestone recommendations
5. Risk identification
6. Requirements management workflow

Return the analysis as JSON with structure:
{
    "recommendations": ["recommendation1", "recommendation2"],
    "suggested_structure": {...},
    "risks": ["risk1", "risk2"],
    "methodology_suggestions": "...",
    "team_roles": ["role1", "role2"]
}"""

            human_prompt = f"""Analyze the following project:

{json.dumps(project_data, ensure_ascii=False, indent=2)}

Provide comprehensive analysis and recommendations."""

        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=human_prompt))
        
        try:
            response = self.llm.invoke(messages)
            content = response.content
            
            # Извлечение JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            return json.loads(content)
        except Exception as e:
            return {
                "recommendations": [],
                "suggested_structure": {},
                "risks": [],
                "methodology_suggestions": "",
                "team_roles": [],
                "error": str(e)
            }
    
    def generate_project_structure(self, methodology: str, project_type: str) -> Dict[str, Any]:
        """Генерация структуры проекта на основе методологии."""
        
        system_prompt = """You are an expert in software development methodologies.
Generate a project structure template based on the methodology and project type."""

        human_prompt = f"""Generate project structure for:
- Methodology: {methodology}
- Project Type: {project_type}

Return JSON with structure:
{{
    "phases": [...],
    "milestones": [...],
    "workflows": [...],
    "artifacts": [...]
}}"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            content = response.content
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            
            return json.loads(content)
        except Exception as e:
            return {
                "phases": [],
                "milestones": [],
                "workflows": [],
                "artifacts": []
            }

