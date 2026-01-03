"""ИИ агент для Базы знаний требований."""
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any, Optional, List
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


class KnowledgeBaseAgent:
    """ИИ агент для анализа требований в базе знаний."""
    
    def __init__(self):
        """Инициализация агента."""
        config = ai_settings.get_config_for_agent("knowledge_base")
        self.llm = create_llm(config)
    
    def analyze_duplicates(self, new_requirement: Dict, existing_requirements: List[Dict]) -> Dict[str, Any]:
        """Анализ дубликатов требования."""
        
        # Получить промпт из хранилища
        prompt_template = prompt_store.get_active_prompt("knowledge_base", "duplicate_analysis")
        
        if prompt_template:
            existing_text = "\n".join([
                f"REQ-{i+1}: {r.get('name', '')} - {r.get('shall', '')}"
                for i, r in enumerate(existing_requirements)
            ])
            human_prompt = prompt_store.render_prompt(
                prompt_template.id,
                {
                    "new_requirement": json.dumps(new_requirement, ensure_ascii=False, indent=2),
                    "existing_requirements": existing_text
                }
            )
            system_prompt = ""
        else:
            # Fallback на встроенный промпт
            system_prompt = """You are an expert in requirement analysis.
Analyze if the new requirement is a duplicate of any existing requirements.
Consider semantic similarity, not just exact text matches.

Return JSON:
{
    "is_duplicate": true/false,
    "duplicate_of": ["requirement_id1", "requirement_id2"],
    "similarity_score": 0.0-1.0,
    "reason": "explanation"
}"""

            existing_text = "\n".join([
                f"REQ-{i+1}: {r.get('name', '')} - {r.get('shall', '')}"
                for i, r in enumerate(existing_requirements)
            ])
            
            human_prompt = f"""New requirement:
{json.dumps(new_requirement, ensure_ascii=False, indent=2)}

Existing requirements:
{existing_text}

Analyze for duplicates."""

        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=human_prompt))
        
        try:
            response = self.llm.invoke(messages)
            content = response.content
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            
            return json.loads(content)
        except:
            return {
                "is_duplicate": False,
                "duplicate_of": [],
                "similarity_score": 0.0,
                "reason": "Analysis failed"
            }
    
    def analyze_conflicts(self, requirement: Dict, other_requirements: List[Dict]) -> Dict[str, Any]:
        """Анализ противоречий требования."""
        
        # Получить промпт из хранилища
        prompt_template = prompt_store.get_active_prompt("knowledge_base", "conflict_analysis")
        
        if prompt_template:
            others_text = "\n".join([
                f"{r.get('identifier', '')}: {r.get('shall', '')}"
                for r in other_requirements
            ])
            human_prompt = prompt_store.render_prompt(
                prompt_template.id,
                {
                    "requirement": json.dumps(requirement, ensure_ascii=False, indent=2),
                    "other_requirements": others_text
                }
            )
            system_prompt = ""
        else:
            # Fallback на встроенный промпт
            system_prompt = """You are an expert in requirement analysis.
Identify conflicts and contradictions between requirements.

Return JSON:
{
    "has_conflicts": true/false,
    "conflicts": [
        {
            "requirement_id": "...",
            "conflict_type": "contradiction|incompatibility|overlap",
            "description": "...",
            "severity": "low|medium|high|critical"
        }
    ]
}"""

            others_text = "\n".join([
                f"{r.get('identifier', '')}: {r.get('shall', '')}"
                for r in other_requirements
            ])
            
            human_prompt = f"""Requirement to check:
{json.dumps(requirement, ensure_ascii=False, indent=2)}

Other requirements:
{others_text}

Analyze for conflicts."""

        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=human_prompt))
        
        try:
            response = self.llm.invoke(messages)
            content = response.content
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            
            return json.loads(content)
        except:
            return {
                "has_conflicts": False,
                "conflicts": []
            }
    
    def generate_recommendations(self, requirement: Dict, context: Dict) -> List[str]:
        """Генерация рекомендаций по дополнению или уточнению требования."""
        
        system_prompt = """You are an expert business analyst.
Analyze the requirement and provide recommendations for:
- Missing details
- Unclear statements
- Potential improvements
- Related requirements that might be needed

Return JSON array of recommendations:
["recommendation1", "recommendation2", ...]"""

        human_prompt = f"""Requirement:
{json.dumps(requirement, ensure_ascii=False, indent=2)}

Context:
{json.dumps(context, ensure_ascii=False, indent=2)}

Provide recommendations."""

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
        except:
            return []
    
    def analyze_completeness(self, requirements: List[Dict], project_context: Dict) -> Dict[str, Any]:
        """Анализ полноты набора требований."""
        
        system_prompt = """Analyze the completeness of requirements set.
Identify missing requirements, gaps, and areas that need more coverage.

Return JSON:
{
    "completeness_score": 0.0-1.0,
    "missing_areas": ["area1", "area2"],
    "recommendations": ["rec1", "rec2"]
}"""

        reqs_text = "\n".join([
            f"{r.get('identifier', '')}: {r.get('name', '')} ({r.get('category', '')})"
            for r in requirements
        ])
        
        human_prompt = f"""Requirements:
{reqs_text}

Project context:
{json.dumps(project_context, ensure_ascii=False, indent=2)}

Analyze completeness."""

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
        except:
            return {
                "completeness_score": 0.5,
                "missing_areas": [],
                "recommendations": []
            }

