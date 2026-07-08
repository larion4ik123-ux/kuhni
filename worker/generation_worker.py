"""Lightweight polling worker for AI generation jobs."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy import select

from backend.app.core.database import async_session_factory
from backend.app.core.settings import get_settings
from backend.app.models import GeneratedImage, GenerationJob, Job
from backend.app.providers.factory import get_provider
from shared.constants import WORKER_POLL_INTERVAL_SEC
from shared.schemas import GenerationRequest

logger = logging.getLogger(__name__)


async def _next_job() -> Job | None:
    async with async_session_factory() as db:
        result = await db.execute(
            select(Job)
            .where(Job.type == "generation", Job.status == "pending")
            .order_by(Job.created_at)
            .limit(1)
        )
        job = result.scalar_one_or_none()
        if job is None:
            return None
        job.status = "running"
        job.locked_at = datetime.now(UTC)
        job.attempts += 1
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job


async def _process_job(job: Job) -> None:
    settings = get_settings()
    provider = get_provider(settings)
    async with async_session_factory() as db:
        generation_id = (job.payload or {}).get("generation_job_id")
        generation = await db.get(GenerationJob, generation_id)
        current_job = await db.get(Job, job.id)
        if generation is None or current_job is None:
            return

        generation.status = "running"
        generation.started_at = generation.started_at or datetime.now(UTC)
        generation.attempt += 1
        db.add(generation)
        await db.flush()

        try:
            result = await provider.generate(
                GenerationRequest(
                    prompt=generation.prompt or "",
                    reference_image_path=(generation.params or {}).get("reference_image_path"),
                    quality=(generation.params or {}).get("quality", settings.AI_QUALITY),
                    n=settings.AI_RESULTS_COUNT,
                )
            )
            generation.status = "done" if result.status == "done" else result.status
            generation.cost = result.cost
            generation.error = result.error
            generation.finished_at = datetime.now(UTC)
            for index, image_path in enumerate(result.image_paths):
                db.add(GeneratedImage(job_id=generation.id, media_file_id=None, variant_index=index))
                logger.info("Generated image for job %s: %s", generation.id, image_path)
            current_job.status = "done"
            current_job.error = None
        except Exception as exc:  # noqa: BLE001
            logger.exception("Generation job failed")
            generation.status = "failed"
            generation.error = str(exc)
            generation.finished_at = datetime.now(UTC)
            current_job.status = "failed" if current_job.attempts >= current_job.max_attempts else "pending"
            current_job.error = str(exc)
        db.add_all([generation, current_job])
        await db.commit()


async def run() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.LOG_LEVEL)
    logger.info("Generation worker started")
    while True:
        job = await _next_job()
        if job is None:
            await asyncio.sleep(WORKER_POLL_INTERVAL_SEC)
            continue
        await _process_job(job)


if __name__ == "__main__":
    asyncio.run(run())
