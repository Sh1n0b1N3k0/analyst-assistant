"""API для управления промптами."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from shared.prompt_store import PromptTemplate
from shared.prompt_store_supabase import get_prompt_store
import uuid

# Получить хранилище (Supabase или in-memory)
prompt_store = get_prompt_store()

router = APIRouter(prefix="/api/prompts", tags=["Prompt Store"])


class PromptCreate(BaseModel):
    name: str
    description: str
    agent_type: str
    prompt_type: str
    template: str
    variables: List[str] = []
    metadata: Optional[Dict[str, Any]] = None
    is_active: bool = True


class PromptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template: Optional[str] = None
    variables: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class PromptRenderRequest(BaseModel):
    prompt_id: str
    variables: Dict[str, Any]


@router.get("", response_model=List[PromptTemplate])
async def list_prompts(
    agent_type: Optional[str] = Query(None),
    prompt_type: Optional[str] = Query(None),
    active_only: bool = Query(True)
):
    """Получить список промптов."""
    if agent_type:
        prompts = prompt_store.get_prompts_by_agent(agent_type, prompt_type)
    else:
        prompts = prompt_store.list_prompts()
    
    if active_only:
        prompts = [p for p in prompts if p.is_active]
    
    return prompts


@router.get("/{prompt_id}", response_model=PromptTemplate)
async def get_prompt(prompt_id: str):
    """Получить промпт по ID."""
    prompt = prompt_store.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.get("/agent/{agent_type}", response_model=List[PromptTemplate])
async def get_agent_prompts(
    agent_type: str,
    prompt_type: Optional[str] = Query(None)
):
    """Получить промпты для конкретного агента."""
    prompts = prompt_store.get_prompts_by_agent(agent_type, prompt_type)
    return prompts


@router.get("/agent/{agent_type}/type/{prompt_type}", response_model=PromptTemplate)
async def get_active_prompt(
    agent_type: str,
    prompt_type: str
):
    """Получить активный промпт для агента и типа."""
    prompt = prompt_store.get_active_prompt(agent_type, prompt_type)
    if not prompt:
        raise HTTPException(
            status_code=404,
            detail=f"Active prompt not found for agent={agent_type}, type={prompt_type}"
        )
    return prompt


@router.post("", response_model=PromptTemplate, status_code=201)
async def create_prompt(prompt_data: PromptCreate):
    """Создать новый промпт."""
    from datetime import datetime
    
    prompt_id = f"{prompt_data.agent_type}_{prompt_data.prompt_type}_{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat()
    
    prompt = PromptTemplate(
        id=prompt_id,
        name=prompt_data.name,
        description=prompt_data.description,
        agent_type=prompt_data.agent_type,
        prompt_type=prompt_data.prompt_type,
        template=prompt_data.template,
        variables=prompt_data.variables,
        version=1,
        is_active=prompt_data.is_active,
        metadata=prompt_data.metadata,
        created_at=now,
        updated_at=now,
    )
    
    prompt_store.add_prompt(prompt)
    return prompt


@router.put("/{prompt_id}", response_model=PromptTemplate)
async def update_prompt(prompt_id: str, updates: PromptUpdate):
    """Обновить промпт (создает новую версию)."""
    update_dict = updates.dict(exclude_unset=True)
    
    updated = prompt_store.update_prompt(prompt_id, update_dict)
    if not updated:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return updated


@router.post("/render", response_model=Dict[str, str])
async def render_prompt(request: PromptRenderRequest):
    """Отрендерить промпт с переменными."""
    try:
        rendered = prompt_store.render_prompt(request.prompt_id, request.variables)
        return {
            "prompt_id": request.prompt_id,
            "rendered": rendered
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{prompt_id}", status_code=204)
async def deactivate_prompt(prompt_id: str):
    """Деактивировать промпт (мягкое удаление)."""
    prompt = prompt_store.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    prompt_store.update_prompt(prompt_id, {"is_active": False})
    return None

