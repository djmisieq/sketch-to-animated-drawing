"""Main FastAPI application."""

import uuid
import logging
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
from app.tasks import celery_app, redis_available

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    logger.info("Initializing application...")
    
    # Create database tables
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Log service status
    if not redis_available:
        logger.warning("Running in LOCAL DEVELOPMENT MODE (no Redis, no Docker)")
        logger.warning("Tasks will run synchronously, files stored in memory only")


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint.

    Returns:
        Dict[str, str]: Status
    """
    services_status = {
        "app": "ok",
        "redis": "ok" if redis_available else "not_available (using in-memory fallback)",
        "storage": "ok" if storage.__class__.__name__ == "MinioStorage" else "not_available (using in-memory fallback)",
    }
    
    return {
        "status": "ok", 
        "services": services_status,
        "mode": "production" if redis_available else "development"
    }


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
    
    # Upload file to storage
    try:
        storage.upload_file(file.file, storage_path, file.content_type)
        logger.info(f"File uploaded to storage: {storage_path}")
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    # Create job in database
    job = Job(
        status=JobStatus.PENDING,
        original_filename=file.filename,
        input_path=storage_path,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    logger.info(f"Created job with ID: {job.id}")
    
    # Start processing task
    try:
        celery_app.send_task("app.tasks.process_sketch", args=[job.id])
        logger.info(f"Task scheduled for job ID: {job.id}")
    except Exception as e:
        logger.error(f"Failed to schedule task: {e}")
        # No need to fail the request if task scheduling fails
        # The user can still check status and retry later
    
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
    try:
        url = storage.get_file_url(job.output_path)
        return {"url": url, "expires_in_seconds": 86400}  # 24 hours
    except Exception as e:
        logger.error(f"Failed to get file URL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get file URL: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
