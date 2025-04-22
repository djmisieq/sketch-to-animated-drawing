"""Main FastAPI application."""

import uuid
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, List, Any, Optional
import os
import aiofiles
from datetime import datetime

from app.config import settings
from app.db import get_db, init_db
from app.models import Job, JobStatus, JobCreate, JobResponse, JobsListResponse
from app.storage import storage
from app.tasks import celery_app


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize DB on startup."""
    await init_db()


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint.

    Returns:
        Dict[str, str]: Status
    """
    return {"status": "ok"}


@app.post(f"{settings.API_V1_STR}/jobs", response_model=JobResponse)
async def create_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """Create a new job.

    Args:
        background_tasks: FastAPI background tasks
        file: Uploaded sketch file
        db: Database session

    Returns:
        JobResponse: Created job
    """
    # Validate file size
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > settings.MAX_IMAGE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds the limit of {settings.MAX_IMAGE_SIZE_MB} MB",
        )
    
    # Validate file type
    allowed_types = {"image/jpeg", "image/png"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG files are supported",
        )
    
    # Reset file pointer
    await file.seek(0)
    
    # Generate unique filename for storage
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_id = str(uuid.uuid4())
    storage_path = f"uploads/{unique_id}{file_ext}"
    
    # Upload file to Minio
    storage.upload_file(file.file, storage_path, file.content_type)
    
    # Create job in database
    job = Job(
        status=JobStatus.PENDING,
        original_filename=file.filename,
        input_path=storage_path,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Start processing task
    celery_app.send_task("app.tasks.process_sketch", args=[job.id])
    
    return JobResponse.model_validate(job)


@app.get(f"{settings.API_V1_STR}/jobs/{{job_id}}", response_model=JobResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)) -> JobResponse:
    """Get job by ID.

    Args:
        job_id: Job ID
        db: Database session

    Returns:
        JobResponse: Job
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse.model_validate(job)


@app.get(f"{settings.API_V1_STR}/jobs", response_model=JobsListResponse)
async def list_jobs(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> JobsListResponse:
    """List jobs.

    Args:
        skip: Skip first N jobs
        limit: Limit to N jobs
        db: Database session

    Returns:
        JobsListResponse: Jobs list
    """
    # Get total count
    total_query = select(Job).order_by(Job.created_at.desc())
    total_result = await db.execute(total_query)
    total = len(total_result.scalars().all())
    
    # Get paginated jobs
    jobs_query = (
        select(Job)
        .order_by(Job.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    jobs_result = await db.execute(jobs_query)
    jobs = jobs_result.scalars().all()
    
    return JobsListResponse(jobs=[JobResponse.model_validate(job) for job in jobs], total=total)


@app.get(f"{settings.API_V1_STR}/result/{{job_id}}")
async def get_result(job_id: int, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get result URL for a completed job.

    Args:
        job_id: Job ID
        db: Database session

    Returns:
        Dict[str, Any]: Result URL
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail=f"Job is not completed, current status: {job.status}")
        
    if not job.output_path:
        raise HTTPException(status_code=400, detail="Job has no output file")
    
    # Generate presigned URL
    url = storage.get_file_url(job.output_path)
    
    return {"url": url, "expires_in_seconds": 86400}  # 24 hours


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
