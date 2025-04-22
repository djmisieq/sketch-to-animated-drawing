"""Celery tasks for processing jobs."""

from celery import Celery
from celery.utils.log import get_task_logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import asyncio
import os
from datetime import datetime

from app.config import settings
from app.db import async_session
from app.models import Job, JobStatus

# Create celery app
celery_app = Celery(
    "worker",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
)

# Configure Celery
celery_app.conf.task_routes = {
    "app.tasks.process_sketch": "main-queue",
}
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

logger = get_task_logger(__name__)


@celery_app.task(name="app.tasks.process_sketch")
def process_sketch(job_id: int) -> dict:
    """Process a sketch job.

    This is the main Celery task that orchestrates the entire processing pipeline:
    1. Load job from database
    2. Update job status to PROCESSING
    3. Convert JPG/PNG to SVG (vectorization)
    4. Create animated SVG
    5. Render MP4 with hand animation
    6. Update job status and output path

    Args:
        job_id: Job ID

    Returns:
        dict: Job information
    """
    logger.info(f"Starting processing for job ID: {job_id}")
    
    # Run async function in syncronous context
    return asyncio.run(_process_job(job_id))


async def _process_job(job_id: int) -> dict:
    """Process job asynchronously.

    Args:
        job_id: Job ID

    Returns:
        dict: Job information
    """
    async with async_session() as session:
        # Get job from database
        job = await _get_job(session, job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return {"status": "error", "message": f"Job {job_id} not found"}

        # Update job status to PROCESSING
        job.status = JobStatus.PROCESSING
        job.updated_at = datetime.utcnow()
        await session.commit()

        try:
            # TODO: Implement the actual processing pipeline
            # 1. Vectorize the image
            # 2. Create animated SVG
            # 3. Render MP4 with hand animation
            
            # For now, just log the process steps
            logger.info(f"Job {job_id}: would vectorize image at {job.input_path}")
            logger.info(f"Job {job_id}: would create animated SVG")
            logger.info(f"Job {job_id}: would render MP4 with hand animation")
            
            # Update job status and output path
            job.status = JobStatus.COMPLETED
            job.output_path = f"output/{job_id}/output.mp4"  # This will be set by the renderer
            job.updated_at = datetime.utcnow()
            await session.commit()
            
            return {
                "status": "success",
                "job_id": job_id,
                "output_path": job.output_path,
            }
            
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            
            # Update job status to FAILED
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.updated_at = datetime.utcnow()
            await session.commit()
            
            return {
                "status": "error",
                "job_id": job_id,
                "message": str(e),
            }


async def _get_job(session: AsyncSession, job_id: int) -> Job:
    """Get job from database.

    Args:
        session: Database session
        job_id: Job ID

    Returns:
        Job: Job object or None
    """
    result = await session.execute(select(Job).where(Job.id == job_id))
    return result.scalars().first()
