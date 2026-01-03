"""API для Администратора проекта."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from shared.database import get_db
from shared.models import Project, User
from services.project_admin.ai_agent import ProjectAdminAgent
from datetime import date
import uuid

router = APIRouter(prefix="/api/projects", tags=["Project Admin"])

# Pydantic схемы
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    methodology: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    owner_id: Optional[uuid.UUID] = None

class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    methodology: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    status: Optional[str]
    owner_id: Optional[uuid.UUID]
    created_at: str
    
    class Config:
        from_attributes = True

class ProjectAnalysisRequest(BaseModel):
    include_structure: bool = True
    include_risks: bool = True

class ProjectAnalysisResponse(BaseModel):
    recommendations: List[str]
    suggested_structure: dict
    risks: List[str]
    methodology_suggestions: str
    team_roles: List[str]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
):
    """Создать новый проект."""
    project = Project(
        name=project_data.name,
        description=project_data.description,
        methodology=project_data.methodology,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        status="planning",
        owner_id=project_data.owner_id
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return ProjectResponse.model_validate(project)


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список проектов."""
    projects = db.query(Project).offset(skip).limit(limit).all()
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Получить проект по ID."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.post("/{project_id}/analyze", response_model=ProjectAnalysisResponse)
async def analyze_project(
    project_id: uuid.UUID,
    analysis_request: ProjectAnalysisRequest,
    db: Session = Depends(get_db)
):
    """ИИ анализ проекта."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    agent = ProjectAdminAgent()
    
    project_data = {
        "name": project.name,
        "description": project.description,
        "methodology": project.methodology,
        "start_date": str(project.start_date) if project.start_date else None,
        "end_date": str(project.end_date) if project.end_date else None,
        "status": project.status,
    }
    
    analysis = agent.analyze_project(project_data)
    
    if analysis_request.include_structure and project.methodology:
        structure = agent.generate_project_structure(
            project.methodology,
            "software_development"
        )
        analysis["suggested_structure"] = structure
    
    return ProjectAnalysisResponse(**analysis)

