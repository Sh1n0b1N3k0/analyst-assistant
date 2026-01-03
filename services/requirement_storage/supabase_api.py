"""API для Хранилища требований через Supabase."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from shared.supabase_config import get_supabase
from shared.sync_manager import sync_manager
import uuid
from datetime import date


router = APIRouter(prefix="/api/storage", tags=["Requirement Storage (Supabase)"])


class RequirementCreate(BaseModel):
    project_id: uuid.UUID
    identifier: str
    name: str
    shall: str
    rationale: str
    verification_method: str
    status: Optional[str] = "draft"
    category: Optional[str] = None
    priority: Optional[int] = 3
    source: Optional[str] = None
    acceptance_criteria: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    estimated_effort: Optional[float] = None
    due_date: Optional[date] = None
    assigned_to_id: Optional[uuid.UUID] = None
    created_by_id: Optional[uuid.UUID] = None


class RequirementResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    identifier: str
    name: str
    shall: str
    rationale: str
    verification_method: str
    status: Optional[str]
    category: Optional[str]
    priority: Optional[int]
    source: Optional[str]
    acceptance_criteria: Optional[List[str]]
    tags: Optional[List[str]]
    estimated_effort: Optional[float]
    actual_effort: Optional[float]
    due_date: Optional[date]
    assigned_to_id: Optional[uuid.UUID]
    version: int
    created_at: str
    updated_at: str


@router.post("/requirements", response_model=RequirementResponse, status_code=201)
async def create_requirement(
    requirement: RequirementCreate,
    supabase=Depends(get_supabase)
):
    """Создать требование в Supabase."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not available")
    
    # Проверка уникальности identifier в проекте
    existing = supabase.table("requirements").select("*").eq(
        "project_id", str(requirement.project_id)
    ).eq("identifier", requirement.identifier).execute()
    
    if existing.data:
        raise HTTPException(
            status_code=400,
            detail=f"Requirement with identifier {requirement.identifier} already exists"
        )
    
    # Создание требования
    requirement_data = requirement.dict()
    requirement_data["project_id"] = str(requirement.project_id)
    if requirement_data.get("assigned_to_id"):
        requirement_data["assigned_to_id"] = str(requirement_data["assigned_to_id"])
    if requirement_data.get("created_by_id"):
        requirement_data["created_by_id"] = str(requirement_data["created_by_id"])
    if requirement_data.get("due_date"):
        requirement_data["due_date"] = requirement_data["due_date"].isoformat()
    
    result = supabase.table("requirements").insert(requirement_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create requirement")
    
    created_req = result.data[0]
    
    # Синхронизация с Neo4j
    sync_manager.sync_requirement_to_graph(created_req, str(requirement.project_id))
    
    return RequirementResponse(**created_req)


@router.get("/requirements", response_model=List[RequirementResponse])
async def list_requirements(
    project_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    supabase=Depends(get_supabase)
):
    """Получить список требований с фильтрацией."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not available")
    
    query = supabase.table("requirements").select("*")
    
    if project_id:
        query = query.eq("project_id", str(project_id))
    if status:
        query = query.eq("status", status)
    if category:
        query = query.eq("category", category)
    
    query = query.range(skip, skip + limit - 1)
    
    result = query.execute()
    
    return [RequirementResponse(**req) for req in (result.data or [])]


@router.get("/requirements/{requirement_id}", response_model=RequirementResponse)
async def get_requirement(
    requirement_id: uuid.UUID,
    supabase=Depends(get_supabase)
):
    """Получить требование по ID."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not available")
    
    result = supabase.table("requirements").select("*").eq(
        "id", str(requirement_id)
    ).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    return RequirementResponse(**result.data[0])


@router.put("/requirements/{requirement_id}", response_model=RequirementResponse)
async def update_requirement(
    requirement_id: uuid.UUID,
    requirement_update: RequirementCreate,
    supabase=Depends(get_supabase)
):
    """Обновить требование."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not available")
    
    # Обновление данных
    update_data = requirement_update.dict(exclude_unset=True)
    update_data["project_id"] = str(update_data["project_id"])
    
    if "due_date" in update_data and update_data["due_date"]:
        update_data["due_date"] = update_data["due_date"].isoformat()
    
    result = supabase.table("requirements").update(update_data).eq(
        "id", str(requirement_id)
    ).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    updated_req = result.data[0]
    
    # Синхронизация с Neo4j
    sync_manager.sync_requirement_to_graph(updated_req, updated_req["project_id"])
    
    return RequirementResponse(**updated_req)


@router.delete("/requirements/{requirement_id}", status_code=204)
async def delete_requirement(
    requirement_id: uuid.UUID,
    supabase=Depends(get_supabase)
):
    """Удалить требование."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not available")
    
    result = supabase.table("requirements").delete().eq(
        "id", str(requirement_id)
    ).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    return None


@router.post("/requirements/{requirement_id}/sync")
async def sync_requirement(
    requirement_id: uuid.UUID,
    supabase=Depends(get_supabase)
):
    """Принудительная синхронизация требования с Neo4j."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not available")
    
    # Получить требование
    result = supabase.table("requirements").select("*").eq(
        "id", str(requirement_id)
    ).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    req = result.data[0]
    success = sync_manager.sync_requirement_to_graph(req, req["project_id"])
    
    return {"success": success, "requirement_id": str(requirement_id)}

