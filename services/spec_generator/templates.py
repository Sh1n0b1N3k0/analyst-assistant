"""Шаблоны для генерации спецификаций."""
from typing import Dict, Any
from enum import Enum


class SpecificationType(str, Enum):
    """Типы спецификаций."""
    USER_STORY = "user_story"
    USE_CASE = "use_case"
    REST_API = "rest_api"
    SOAP_API = "soap_api"
    GRPC_API = "grpc_api"
    ASYNC_API = "async_api"
    UML_SEQUENCE = "uml_sequence"
    UML_ER = "uml_er"
    UML_ACTIVITY = "uml_activity"
    C4_CONTEXT = "c4_context"
    C4_CONTAINER = "c4_container"
    C4_COMPONENT = "c4_component"


class TemplateManager:
    """Управление шаблонами спецификаций."""
    
    def __init__(self):
        """Инициализация менеджера шаблонов."""
        self.templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """Загрузить шаблоны по умолчанию."""
        return {
            SpecificationType.USER_STORY: {
                "name": "User Story",
                "template": """As a {actor}
I want {action}
So that {benefit}

Acceptance Criteria:
{acceptance_criteria}

Technical Notes:
{technical_notes}""",
                "description": "User Story format"
            },
            SpecificationType.USE_CASE: {
                "name": "Use Case",
                "template": """Use Case: {name}
Actor: {actor}
Preconditions: {preconditions}
Main Flow:
{main_flow}
Alternative Flows:
{alternative_flows}
Postconditions: {postconditions}""",
                "description": "Use Case specification"
            },
            SpecificationType.REST_API: {
                "name": "REST API",
                "template": """openapi: 3.0.0
info:
  title: {api_name}
  version: {version}
paths:
  {endpoints}""",
                "description": "OpenAPI/Swagger specification"
            },
            SpecificationType.UML_SEQUENCE: {
                "name": "UML Sequence Diagram",
                "template": """@startuml
{participants}
{interactions}
@enduml""",
                "description": "PlantUML sequence diagram"
            },
            SpecificationType.C4_CONTEXT: {
                "name": "C4 Context Diagram",
                "template": """@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

{context_diagram}
@enduml""",
                "description": "C4 Context diagram"
            }
        }
    
    def get_template(self, spec_type: SpecificationType) -> Dict[str, Any]:
        """Получить шаблон по типу."""
        return self.templates.get(spec_type, {})
    
    def list_templates(self) -> Dict[str, Dict[str, Any]]:
        """Получить список всех шаблонов."""
        return {
            key.value: {
                "name": template["name"],
                "description": template["description"]
            }
            for key, template in self.templates.items()
        }
    
    def add_template(self, spec_type: str, template: Dict[str, Any]):
        """Добавить новый шаблон."""
        self.templates[spec_type] = template
    
    def update_template(self, spec_type: str, template: Dict[str, Any]):
        """Обновить существующий шаблон."""
        if spec_type in self.templates:
            self.templates[spec_type].update(template)

