"""ИИ агент для обработки входящих требований."""
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


class RequirementProcessorAgent:
    """ИИ агент для формализации входящих требований."""
    
    def __init__(self):
        """Инициализация агента."""
        config = ai_settings.get_config_for_agent("requirement_processor")
        self.llm = create_llm(config)
    
    def formalize_requirement(self, informal_text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Формализация неформализованного требования в формат ISO/IEC/IEEE 29148."""
        
        # Получить промпт из хранилища
        prompt_template = prompt_store.get_active_prompt("requirement_processor", "formalization")
        
        if prompt_template:
            # Использовать промпт из хранилища
            context_text = json.dumps(context, ensure_ascii=False, indent=2) if context else ""
            human_prompt = prompt_store.render_prompt(
                prompt_template.id,
                {
                    "informal_text": informal_text,
                    "context": context_text
                }
            )
            system_prompt = ""
        else:
            # Fallback на встроенный промпт
            system_prompt = """You are an expert business analyst specializing in requirement formalization according to ISO/IEC/IEEE 29148 standard.

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

Return the result as a JSON object with the following structure:
{
    "identifier": "REQ-001",
    "name": "Clear requirement name",
    "shall": "Formal requirement statement starting with 'The system shall...'",
    "rationale": "Why this requirement exists",
    "verification_method": "Method to verify (testing, inspection, analysis, demonstration)",
    "category": "functional|non_functional|business|technical",
    "priority": 1-5,
    "source": "source of requirement",
    "acceptance_criteria": ["criterion1", "criterion2"],
    "tags": ["tag1", "tag2"],
    "estimated_effort": 5.0,
    "entities": [
        {"name": "User", "type": "actor"},
        {"name": "Order", "type": "data_object"}
    ]
}"""

            context_text = ""
            if context:
                context_text = f"""
Context from project:
{json.dumps(context, ensure_ascii=False, indent=2)}
"""

            human_prompt = f"""Please formalize the following requirement according to ISO/IEC/IEEE 29148:

{informal_text}

{context_text}

Provide the formalized requirement in JSON format."""

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
            
            result = json.loads(content)
            return result
        except Exception as e:
            # Fallback
            return {
                "identifier": "REQ-UNKNOWN",
                "name": informal_text[:100],
                "shall": informal_text,
                "rationale": "Requirement needs review",
                "verification_method": "testing",
                "category": "functional",
                "priority": 3,
                "source": "unknown",
                "acceptance_criteria": [],
                "tags": [],
                "estimated_effort": None,
                "entities": [],
                "error": str(e)
            }
    
    def extract_entities(self, requirement_text: str) -> List[Dict[str, str]]:
        """Извлечение сущностей из требования."""
        
        system_prompt = """Extract entities (actors, data objects, business processes) from the requirement.
Return JSON array:
[
    {"name": "EntityName", "type": "actor|data_object|business_process|external_system|resource"}
]"""

        human_prompt = f"""Extract entities from this requirement:

{requirement_text}

Return JSON array of entities."""

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

