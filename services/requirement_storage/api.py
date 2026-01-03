"""API для Хранилища требований."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from pydantic import BaseModel
from typing import List, Optional
from shared.database import get_db
from shared.models import Requirement, Project, User
import uuid
from datetime import date

router = APIRouter(prefix="/api/storage", tags=["Requirement Storage"])


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
    
    class Config:
        from_attributes = True


@router.post("/requirements", response_model=RequirementResponse, status_code=201)
async def create_requirement(
    requirement: RequirementCreate,
    db: Session = Depends(get_db)
):
    """Создать требование в хранилище."""
    # Проверка уникальности identifier в проекте
    existing = db.query(Requirement).filter(
        Requirement.project_id == requirement.project_id,
        Requirement.identifier == requirement.identifier
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Requirement with identifier {requirement.identifier} already exists in this project"
        )
    
    db_requirement = Requirement(
        project_id=requirement.project_id,
        identifier=requirement.identifier,
        name=requirement.name,
        shall=requirement.shall,
        rationale=requirement.rationale,
        verification_method=requirement.verification_method,
        status=requirement.status,
        category=requirement.category,
        priority=requirement.priority,
        source=requirement.source,
        acceptance_criteria=requirement.acceptance_criteria or [],
        tags=requirement.tags or [],
        estimated_effort=requirement.estimated_effort,
        due_date=requirement.due_date,
        assigned_to_id=requirement.assigned_to_id,
        created_by_id=requirement.created_by_id
    )
    
    db.add(db_requirement)
    db.commit()
    db.refresh(db_requirement)
    
    return RequirementResponse.model_validate(db_requirement)


@router.get("/requirements", response_model=List[RequirementResponse])
async def list_requirements(
    project_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Получить список требований с фильтрацией."""
    query = db.query(Requirement)
    
    if project_id:
        query = query.filter(Requirement.project_id == project_id)
    if status:
        query = query.filter(Requirement.status == status)
    if category:
        query = query.filter(Requirement.category == category)
    
    requirements = query.offset(skip).limit(limit).all()
    return [RequirementResponse.model_validate(r) for r in requirements]


@router.get("/requirements/{requirement_id}", response_model=RequirementResponse)
async def get_requirement(
    requirement_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Получить требование по ID."""
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return RequirementResponse.model_validate(requirement)


@router.get("/requirements/by-identifier/{identifier}")
async def get_requirement_by_identifier(
    identifier: str,
    project_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Получить требование по identifier."""
    requirement = db.query(Requirement).filter(
        Requirement.identifier == identifier,
        Requirement.project_id == project_id
    ).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return RequirementResponse.model_validate(requirement)


@router.put("/requirements/{requirement_id}", response_model=RequirementResponse)
async def update_requirement(
    requirement_id: uuid.UUID,
    requirement_update: RequirementCreate,
    db: Session = Depends(get_db)
):
    """Обновить требование."""
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Обновление полей
    for field, value in requirement_update.dict(exclude_unset=True).items():
        setattr(requirement, field, value)
    
    requirement.version += 1
    db.commit()
    db.refresh(requirement)
    
    return RequirementResponse.model_validate(requirement)


@router.delete("/requirements/{requirement_id}", status_code=204)
async def delete_requirement(
    requirement_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Удалить требование."""
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    db.delete(requirement)
    db.commit()
    
    return None

