"""Общие модели базы данных (импорт из основной схемы)."""
# Импортируем модели из основной схемы БД
# В production это может быть отдельный пакет с моделями

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Boolean, JSONB, ARRAY, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from shared.database import Base
import uuid


# Enum типы
class RequirementStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    ARCHIVED = "archived"


class RequirementCategory(str, enum.Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    BUSINESS = "business"
    TECHNICAL = "technical"


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Основные модели (упрощенные версии для начала)
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(500), nullable=False)
    description = Column(Text)
    methodology = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(50))
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class Requirement(Base):
    __tablename__ = "requirements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    identifier = Column(String(100), nullable=False)
    name = Column(String(500), nullable=False)
    shall = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    verification_method = Column(Text, nullable=False)
    status = Column(String(50))
    category = Column(String(50))
    priority = Column(Integer)
    source = Column(String(200))
    acceptance_criteria = Column(ARRAY(Text))
    tags = Column(ARRAY(String))
    estimated_effort = Column(Numeric)
    actual_effort = Column(Numeric)
    due_date = Column(Date)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

