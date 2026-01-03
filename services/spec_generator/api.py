"""API для Генератора спецификаций."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from shared.database import get_db
from shared.models import Requirement, Project
from services.spec_generator.ai_agent import SpecificationGeneratorAgent
from services.spec_generator.templates import SpecificationType, TemplateManager
import uuid

router = APIRouter(prefix="/api/specs", tags=["Specification Generator"])

agent = SpecificationGeneratorAgent()
template_manager = TemplateManager()


class GenerateSpecRequest(BaseModel):
    requirement_id: uuid.UUID
    spec_type: str  # user_story, use_case, rest_api, etc.
    context: Optional[Dict[str, Any]] = None
    template_customizations: Optional[Dict[str, Any]] = None


class GenerateSpecResponse(BaseModel):
    specification_id: uuid.UUID
    requirement_id: uuid.UUID
    spec_type: str
    content: str
    format: str  # text, json, plantuml, etc.


class TemplateResponse(BaseModel):
    name: str
    description: str


@router.post("/generate", response_model=GenerateSpecResponse)
async def generate_specification(
    request: GenerateSpecRequest,
    db: Session = Depends(get_db)
):
    """Генерировать спецификацию."""
    # Получить требование
    requirement = db.query(Requirement).filter(
        Requirement.id == request.requirement_id
    ).first()
    
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Получить проект для контекста
    project = db.query(Project).filter(Project.id == requirement.project_id).first()
    
    req_data = {
        "id": str(requirement.id),
        "identifier": requirement.identifier,
        "name": requirement.name,
        "shall": requirement.shall,
        "rationale": requirement.rationale,
        "category": requirement.category,
        "acceptance_criteria": requirement.acceptance_criteria or []
    }
    
    context = request.context or {}
    context["project"] = {
        "name": project.name if project else "",
        "methodology": project.methodology if project else ""
    }
    
    # Генерация спецификации
    try:
        spec_type = SpecificationType(request.spec_type)
        content = agent.generate_specification(spec_type, req_data, context)
        
        # Определить формат
        format_map = {
            SpecificationType.USER_STORY: "text",
            SpecificationType.USE_CASE: "text",
            SpecificationType.REST_API: "json",
            SpecificationType.GRPC_API: "text",
            SpecificationType.ASYNC_API: "json",
            SpecificationType.UML_SEQUENCE: "plantuml",
            SpecificationType.UML_ER: "plantuml",
            SpecificationType.UML_ACTIVITY: "plantuml",
            SpecificationType.C4_CONTEXT: "plantuml",
        }
        
        spec_format = format_map.get(spec_type, "text")
        
        return GenerateSpecResponse(
            specification_id=uuid.uuid4(),
            requirement_id=request.requirement_id,
            spec_type=request.spec_type,
            content=content,
            format=spec_format
        )
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid specification type: {request.spec_type}")


@router.get("/templates", response_model=Dict[str, TemplateResponse])
async def list_templates():
    """Получить список доступных шаблонов."""
    templates = template_manager.list_templates()
    return {
        key: TemplateResponse(**value)
        for key, value in templates.items()
    }


@router.get("/templates/{template_type}")
async def get_template(template_type: str):
    """Получить шаблон по типу."""
    try:
        spec_type = SpecificationType(template_type)
        template = template_manager.get_template(spec_type)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid template type: {template_type}")


@router.post("/templates/{template_type}")
async def create_template(template_type: str, template_data: Dict[str, Any]):
    """Создать или обновить шаблон."""
    template_manager.add_template(template_type, template_data)
    return {"message": "Template created/updated successfully"}


@router.get("/requirements/{requirement_id}/specs")
async def list_requirement_specs(
    requirement_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Получить список спецификаций для требования."""
    # В production получать из БД
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id
    ).first()
    
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    return {
        "requirement_id": str(requirement_id),
        "specifications": []
    }

