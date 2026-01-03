"""API для Базы знаний требований."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from shared.database import get_db
from services.knowledge_base.graph_rag import KnowledgeBaseGraph
from services.knowledge_base.vector_store import VectorStore
from services.knowledge_base.ai_agent import KnowledgeBaseAgent
import uuid

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])

# Глобальные экземпляры
graph_rag = KnowledgeBaseGraph()
vector_store = VectorStore()
ai_agent = KnowledgeBaseAgent()


class ImportRequirementRequest(BaseModel):
    project_id: uuid.UUID
    requirement_data: Dict[str, Any]

class ImportRequirementResponse(BaseModel):
    requirement_id: str
    imported: bool
    duplicates_found: List[Dict]
    conflicts_found: List[Dict]


class DuplicateAnalysisResponse(BaseModel):
    is_duplicate: bool
    duplicate_of: List[str]
    similarity_score: float
    reason: str

class ConflictAnalysisResponse(BaseModel):
    has_conflicts: bool
    conflicts: List[Dict[str, Any]]

class RecommendationsResponse(BaseModel):
    recommendations: List[str]

class CompletenessAnalysisResponse(BaseModel):
    completeness_score: float
    missing_areas: List[str]
    recommendations: List[str]


@router.post("/import", response_model=ImportRequirementResponse)
async def import_requirement(
    request: ImportRequirementRequest,
    db: Session = Depends(get_db)
):
    """Импортировать требование в базу знаний."""
    req_data = request.requirement_data
    req_id = req_data.get("id") or req_data.get("identifier", "")
    
    # Импорт в граф
    imported_id = graph_rag.import_requirement(req_data, str(request.project_id))
    
    # Поиск дубликатов
    duplicates = graph_rag.find_duplicates(req_data)
    
    # Анализ противоречий
    conflicts = graph_rag.find_conflicts(imported_id)
    
    # Обновление векторного хранилища
    vector_store.batch_update([req_data])
    
    return ImportRequirementResponse(
        requirement_id=imported_id,
        imported=True,
        duplicates_found=duplicates,
        conflicts_found=conflicts
    )


@router.get("/duplicates/{requirement_id}", response_model=DuplicateAnalysisResponse)
async def check_duplicates(
    requirement_id: str,
    db: Session = Depends(get_db)
):
    """Проверить требование на дубликаты."""
    # Получить требование из БД
    from shared.models import Requirement
    requirement = db.query(Requirement).filter(
        Requirement.identifier == requirement_id
    ).first()
    
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    req_data = {
        "id": str(requirement.id),
        "identifier": requirement.identifier,
        "name": requirement.name,
        "shall": requirement.shall,
        "category": requirement.category
    }
    
    # Поиск через граф
    graph_duplicates = graph_rag.find_duplicates(req_data)
    
    # ИИ анализ
    # Получить похожие требования для анализа
    similar_reqs = [{"id": d["id"], "name": d["name"]} for d in graph_duplicates[:5]]
    ai_analysis = ai_agent.analyze_duplicates(req_data, similar_reqs)
    
    return DuplicateAnalysisResponse(
        is_duplicate=ai_analysis.get("is_duplicate", False),
        duplicate_of=[d["id"] for d in graph_duplicates],
        similarity_score=ai_analysis.get("similarity_score", 0.0),
        reason=ai_analysis.get("reason", "")
    )


@router.get("/conflicts/{requirement_id}", response_model=ConflictAnalysisResponse)
async def check_conflicts(
    requirement_id: str,
    db: Session = Depends(get_db)
):
    """Проверить требование на противоречия."""
    # Получить требование
    from shared.models import Requirement
    requirement = db.query(Requirement).filter(
        Requirement.identifier == requirement_id
    ).first()
    
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    req_data = {
        "id": str(requirement.id),
        "identifier": requirement.identifier,
        "name": requirement.name,
        "shall": requirement.shall,
        "category": requirement.category,
        "priority": requirement.priority
    }
    
    # Поиск через граф
    graph_conflicts = graph_rag.find_conflicts(requirement_id)
    
    # ИИ анализ
    other_reqs = [{"id": c["id"], "shall": c["shall"]} for c in graph_conflicts[:10]]
    ai_analysis = ai_agent.analyze_conflicts(req_data, other_reqs)
    
    return ConflictAnalysisResponse(
        has_conflicts=ai_analysis.get("has_conflicts", False),
        conflicts=ai_analysis.get("conflicts", [])
    )


@router.get("/recommendations/{requirement_id}", response_model=RecommendationsResponse)
async def get_recommendations(
    requirement_id: str,
    db: Session = Depends(get_db)
):
    """Получить рекомендации по требованию."""
    from shared.models import Requirement, Project
    requirement = db.query(Requirement).filter(
        Requirement.identifier == requirement_id
    ).first()
    
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    project = db.query(Project).filter(Project.id == requirement.project_id).first()
    
    req_data = {
        "identifier": requirement.identifier,
        "name": requirement.name,
        "shall": requirement.shall,
        "rationale": requirement.rationale,
        "category": requirement.category
    }
    
    context = {
        "project_name": project.name if project else "",
        "methodology": project.methodology if project else ""
    }
    
    # Получить связанные требования
    related = graph_rag.get_related_requirements(requirement_id)
    
    recommendations = ai_agent.generate_recommendations(req_data, context)
    
    return RecommendationsResponse(recommendations=recommendations)


@router.get("/completeness/{project_id}", response_model=CompletenessAnalysisResponse)
async def analyze_completeness(
    project_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Анализ полноты требований проекта."""
    from shared.models import Requirement, Project
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    requirements = db.query(Requirement).filter(
        Requirement.project_id == project_id
    ).all()
    
    reqs_data = [{
        "identifier": r.identifier,
        "name": r.name,
        "category": r.category
    } for r in requirements]
    
    context = {
        "project_name": project.name,
        "methodology": project.methodology,
        "description": project.description
    }
    
    analysis = ai_agent.analyze_completeness(reqs_data, context)
    
    return CompletenessAnalysisResponse(
        completeness_score=analysis.get("completeness_score", 0.0),
        missing_areas=analysis.get("missing_areas", []),
        recommendations=analysis.get("recommendations", [])
    )


@router.get("/graph/{project_id}")
async def get_knowledge_graph(project_id: uuid.UUID):
    """Получить граф знаний проекта для визуализации."""
    # В production возвращать данные для визуализации графа
    return {
        "nodes": [],
        "edges": [],
        "message": "Graph visualization data"
    }

