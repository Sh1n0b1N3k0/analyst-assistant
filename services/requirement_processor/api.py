"""API для Обработчика входящих требований."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from shared.database import get_db
from services.requirement_processor.ai_agent import RequirementProcessorAgent
import uuid

router = APIRouter(prefix="/api/requirements/process", tags=["Requirement Processor"])

# Хранилище статусов обработки (в production использовать Redis или БД)
processing_status = {}


class ProcessRequirementRequest(BaseModel):
    project_id: uuid.UUID
    informal_text: str
    context: Optional[Dict[str, Any]] = None

class ProcessRequirementResponse(BaseModel):
    processing_id: uuid.UUID
    status: str
    message: str

class ProcessingStatusResponse(BaseModel):
    processing_id: uuid.UUID
    status: str  # pending, processing, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("", response_model=ProcessRequirementResponse)
async def process_requirement(
    request: ProcessRequirementRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Обработать входящее требование."""
    processing_id = uuid.uuid4()
    
    # Установить статус pending
    processing_status[str(processing_id)] = {
        "status": "pending",
        "result": None,
        "error": None
    }
    
    # Запустить обработку в фоне
    background_tasks.add_task(
        process_requirement_task,
        processing_id,
        request.project_id,
        request.informal_text,
        request.context,
        db
    )
    
    return ProcessRequirementResponse(
        processing_id=processing_id,
        status="pending",
        message="Requirement processing started"
    )


async def process_requirement_task(
    processing_id: uuid.UUID,
    project_id: uuid.UUID,
    informal_text: str,
    context: Optional[Dict],
    db: Session
):
    """Фоновая задача обработки требования."""
    try:
        processing_status[str(processing_id)]["status"] = "processing"
        
        # Инициализация агента
        agent = RequirementProcessorAgent()
        
        # Формализация требования
        formalized = agent.formalize_requirement(informal_text, context)
        
        # Извлечение сущностей
        entities = agent.extract_entities(informal_text)
        formalized["entities"] = entities
        
        # Сохранение результата
        processing_status[str(processing_id)] = {
            "status": "completed",
            "result": formalized,
            "error": None
        }
        
    except Exception as e:
        processing_status[str(processing_id)] = {
            "status": "failed",
            "result": None,
            "error": str(e)
        }


@router.get("/{processing_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(processing_id: uuid.UUID):
    """Получить статус обработки."""
    status_data = processing_status.get(str(processing_id))
    
    if not status_data:
        raise HTTPException(status_code=404, detail="Processing not found")
    
    return ProcessingStatusResponse(
        processing_id=processing_id,
        status=status_data["status"],
        result=status_data.get("result"),
        error=status_data.get("error")
    )


@router.post("/batch")
async def process_batch(
    requirements: List[ProcessRequirementRequest],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Пакетная обработка требований."""
    processing_ids = []
    
    for req in requirements:
        processing_id = uuid.uuid4()
        processing_ids.append(processing_id)
        
        processing_status[str(processing_id)] = {
            "status": "pending",
            "result": None,
            "error": None
        }
        
        background_tasks.add_task(
            process_requirement_task,
            processing_id,
            req.project_id,
            req.informal_text,
            req.context,
            db
        )
    
    return {
        "processing_ids": processing_ids,
        "count": len(processing_ids),
        "message": "Batch processing started"
    }

