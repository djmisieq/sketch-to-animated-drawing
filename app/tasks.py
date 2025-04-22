"""Celery tasks for processing jobs."""

from celery import Celery
from celery.utils.log import get_task_logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import asyncio
import os
import io
import tempfile
from datetime import datetime
import uuid
from pathlib import Path

from app.config import settings
from app.db import async_session
from app.models import Job, JobStatus
from app.storage import storage
from app.vectorizer import vectorizer
from app.animator import animator
from app.renderer import renderer

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
            # Download the input file from storage
            logger.info(f"Downloading input file: {job.input_path}")
            input_file, content_type = storage.download_file(job.input_path)
            input_data = input_file.read()
            
            # 1. Vectorize the image
            logger.info("Step 1: Vectorizing image")
            svg_content = vectorizer.process_image(input_data)
            
            # Save intermediate SVG result
            svg_path = f"processing/{job_id}/vectorized.svg"
            with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as temp_svg:
                temp_svg.write(svg_content.encode('utf-8'))
                temp_svg.flush()
                
                with open(temp_svg.name, 'rb') as svg_file:
                    storage.upload_file(svg_file, svg_path, "image/svg+xml")
            
            # 2. Create animated SVG
            logger.info("Step 2: Creating animated SVG")
            animated_svg = animator.create_animated_svg(svg_content)
            
            # Save animated SVG result
            animated_svg_path = f"processing/{job_id}/animated.svg"
            with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as temp_animated:
                temp_animated.write(animated_svg.encode('utf-8'))
                temp_animated.flush()
                
                with open(temp_animated.name, 'rb') as animated_file:
                    storage.upload_file(animated_file, animated_svg_path, "image/svg+xml")
            
            # 3. Render MP4 with hand animation
            logger.info("Step 3: Rendering MP4 with hand animation")
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_output:
                output_path = temp_output.name
            
            # Render video
            renderer.render(animated_svg, output_path)
            
            # Upload the rendered video to storage
            final_path = f"output/{job_id}/output.mp4"
            with open(output_path, 'rb') as video_file:
                storage.upload_file(video_file, final_path, "video/mp4")
            
            # Clean up temporary files
            os.unlink(output_path)
            
            # Update job status and output path
            job.status = JobStatus.COMPLETED
            job.output_path = final_path
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
