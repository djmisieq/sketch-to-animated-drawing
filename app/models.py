"""Database models and Pydantic schemas."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from typing import Optional, List

from pydantic import BaseModel, Field, validator
from app.db import Base


class JobStatus(str, Enum):
    """Job status enum."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    """Job database model."""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    original_filename = Column(String, nullable=False)
    input_path = Column(String, nullable=False)
    output_path = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class JobCreate(BaseModel):
    """Schema for job creation."""

    original_filename: str = Field(..., description="Original filename of the uploaded sketch")


class JobResponse(BaseModel):
    """Schema for job response."""

    id: int
    status: JobStatus
    original_filename: str
    created_at: datetime
    updated_at: datetime
    output_path: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class JobsListResponse(BaseModel):
    """Schema for jobs list response."""

    jobs: List[JobResponse]
    total: int
