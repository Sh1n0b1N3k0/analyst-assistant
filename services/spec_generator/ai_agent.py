"""ИИ агент для генерации спецификаций."""
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any, Optional, List
from shared.ai_config import ai_settings, ModelProvider
from shared.prompt_store import prompt_store
from services.spec_generator.templates import SpecificationType, TemplateManager
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


class SpecificationGeneratorAgent:
    """ИИ агент для генерации спецификаций."""
    
    def __init__(self):
        """Инициализация агента."""
        config = ai_settings.get_config_for_agent("spec_generator")
        self.llm = create_llm(config)
        self.template_manager = TemplateManager()
    
    def generate_user_story(self, requirement: Dict[str, Any], context: Optional[Dict] = None) -> str:
        """Генерация User Story."""
        
        # Получить промпт из хранилища
        prompt_template = prompt_store.get_active_prompt("spec_generator", "user_story")
        
        if prompt_template:
            context_text = json.dumps(context, ensure_ascii=False, indent=2) if context else ""
            human_prompt = prompt_store.render_prompt(
                prompt_template.id,
                {
                    "requirement": json.dumps(requirement, ensure_ascii=False, indent=2),
                    "context": context_text
                }
            )
            system_prompt = ""
        else:
            # Fallback на встроенный промпт
            system_prompt = """You are an expert in writing User Stories.
Generate a well-structured User Story based on the requirement.
Follow the format: As a [actor], I want [action], So that [benefit]."""

            human_prompt = f"""Requirement:
{json.dumps(requirement, ensure_ascii=False, indent=2)}

{json.dumps(context, ensure_ascii=False, indent=2) if context else ''}

Generate a User Story."""

        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=human_prompt))
        
        response = self.llm.invoke(messages)
        return response.content
    
    def generate_use_case(self, requirement: Dict[str, Any], context: Optional[Dict] = None) -> str:
        """Генерация Use Case."""
        
        system_prompt = """You are an expert in writing Use Cases.
Generate a detailed Use Case specification with actors, preconditions, main flow, alternative flows, and postconditions."""

        human_prompt = f"""Requirement:
{json.dumps(requirement, ensure_ascii=False, indent=2)}

Generate a Use Case specification."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def generate_rest_api(self, requirement: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Генерация REST API контракта (OpenAPI)."""
        
        # Получить промпт из хранилища
        prompt_template = prompt_store.get_active_prompt("spec_generator", "rest_api")
        
        if prompt_template:
            context_text = json.dumps(context, ensure_ascii=False, indent=2) if context else ""
            human_prompt = prompt_store.render_prompt(
                prompt_template.id,
                {
                    "requirement": json.dumps(requirement, ensure_ascii=False, indent=2),
                    "context": context_text
                }
            )
            system_prompt = ""
        else:
            # Fallback на встроенный промпт
            system_prompt = """You are an expert in API design.
Generate OpenAPI 3.0 specification (JSON format) for the requirement.
Include paths, methods, request/response schemas, and examples."""

            human_prompt = f"""Requirement:
{json.dumps(requirement, ensure_ascii=False, indent=2)}

Generate OpenAPI 3.0 specification in JSON format."""

        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=human_prompt))
        
        response = self.llm.invoke(messages)
        content = response.content
        
        # Извлечение JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        try:
            return json.loads(content)
        except:
            return {"openapi": "3.0.0", "info": {"title": "API", "version": "1.0.0"}, "paths": {}}
    
    def generate_grpc_api(self, requirement: Dict[str, Any]) -> str:
        """Генерация gRPC API (Protocol Buffers)."""
        
        system_prompt = """You are an expert in gRPC and Protocol Buffers.
Generate .proto file specification for the requirement."""

        human_prompt = f"""Requirement:
{json.dumps(requirement, ensure_ascii=False, indent=2)}

Generate Protocol Buffers specification."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def generate_async_api(self, requirement: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация AsyncAPI контракта."""
        
        system_prompt = """You are an expert in event-driven APIs.
Generate AsyncAPI 2.0 specification (JSON format) for the requirement.
Include channels, messages, and schemas."""

        human_prompt = f"""Requirement:
{json.dumps(requirement, ensure_ascii=False, indent=2)}

Generate AsyncAPI 2.0 specification in JSON format."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        content = response.content
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        
        try:
            return json.loads(content)
        except:
            return {"asyncapi": "2.0.0", "info": {"title": "API", "version": "1.0.0"}, "channels": {}}
    
    def generate_uml_sequence(self, requirement: Dict[str, Any], components: List[Dict]) -> str:
        """Генерация UML Sequence диаграммы (PlantUML)."""
        
        system_prompt = """You are an expert in UML diagrams.
Generate PlantUML sequence diagram code based on the requirement and components."""

        components_text = "\n".join([f"- {c.get('name', '')}" for c in components])
        
        human_prompt = f"""Requirement:
{json.dumps(requirement, ensure_ascii=False, indent=2)}

Components:
{components_text}

Generate PlantUML sequence diagram code."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def generate_uml_er(self, requirement: Dict[str, Any], entities: List[Dict]) -> str:
        """Генерация UML ER диаграммы (PlantUML)."""
        
        system_prompt = """You are an expert in Entity-Relationship diagrams.
Generate PlantUML ER diagram code."""

        entities_text = "\n".join([f"- {e.get('name', '')} ({e.get('type', '')})" for e in entities])
        
        human_prompt = f"""Requirement:
{json.dumps(requirement, ensure_ascii=False, indent=2)}

Entities:
{entities_text}

Generate PlantUML ER diagram code."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def generate_c4_context(self, requirement: Dict[str, Any], system_context: Dict) -> str:
        """Генерация C4 Context диаграммы."""
        
        system_prompt = """You are an expert in C4 model diagrams.
Generate C4 Context diagram using PlantUML C4-PlantUML syntax."""

        human_prompt = f"""Requirement:
{json.dumps(requirement, ensure_ascii=False, indent=2)}

System Context:
{json.dumps(system_context, ensure_ascii=False, indent=2)}

Generate C4 Context diagram code."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def generate_specification(
        self,
        spec_type: SpecificationType,
        requirement: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> str:
        """Универсальный метод генерации спецификации."""
        
        generators = {
            SpecificationType.USER_STORY: self.generate_user_story,
            SpecificationType.USE_CASE: self.generate_use_case,
            SpecificationType.REST_API: lambda r, c: json.dumps(self.generate_rest_api(r, c), indent=2),
            SpecificationType.GRPC_API: self.generate_grpc_api,
            SpecificationType.ASYNC_API: lambda r: json.dumps(self.generate_async_api(r), indent=2),
        }
        
        generator = generators.get(spec_type)
        if generator:
            return generator(requirement, context)
        else:
            return f"Specification type {spec_type} not yet implemented"

