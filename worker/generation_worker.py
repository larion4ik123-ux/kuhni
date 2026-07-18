"""Lightweight polling worker for AI generation jobs."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import mimetypes
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select

from backend.app.core.database import async_session_factory
from backend.app.core.settings import get_settings
from backend.app.models import (
    FunnelSession,
    GeneratedImage,
    GenerationJob,
    Job,
    Lead,
    MediaFile,
    MessengerAccount,
)
from backend.app.providers.factory import get_provider
from backend.app.services.notify import NotifyService
from bot.adapters.max import MaxAdapter
from shared.constants import AI_RESULT_DISCLAIMER, WORKER_POLL_INTERVAL_SEC
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
            saved_paths: list[str] = []
            for index, image_path in enumerate(result.image_paths):
                path = Path(image_path)
                content = path.read_bytes()
                media = MediaFile(
                    category="generated",
                    original_filename=path.name,
                    stored_path=str(path),
                    mime=mimetypes.guess_type(path.name)[0] or "image/jpeg",
                    size_bytes=len(content),
                    sha256=hashlib.sha256(content).hexdigest(),
                    is_real_work=False,
                )
                db.add(media)
                await db.flush()
                db.add(GeneratedImage(job_id=generation.id, media_file_id=media.id, variant_index=index))
                generation.result_media_file_id = generation.result_media_file_id or media.id
                saved_paths.append(str(path))
                logger.info("Generated image for job %s: %s", generation.id, image_path)
            current_job.status = "done" if result.status == "done" else "failed"
            current_job.error = result.error
            await db.flush()
            if result.status == "done" and saved_paths:
                await _deliver_result(db, generation, saved_paths[0], settings)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Generation job failed")
            generation.status = "failed"
            generation.error = str(exc)
            generation.finished_at = datetime.now(UTC)
            current_job.status = "failed" if current_job.attempts >= current_job.max_attempts else "pending"
            current_job.error = str(exc)
        db.add_all([generation, current_job])
        await db.commit()


async def _deliver_result(db, generation: GenerationJob, image_path: str, settings) -> None:
    """Send the locally persisted result to the MAX user and the project manager."""
    if not settings.MAX_BOT_TOKEN:
        logger.warning("MAX_BOT_TOKEN is empty; generated image was persisted but not sent")
        return
    session = await db.get(FunnelSession, generation.session_id) if generation.session_id else None
    account = (
        await db.get(MessengerAccount, session.messenger_account_id)
        if session and session.messenger_account_id
        else None
    )
    adapter = MaxAdapter(settings)
    if account and account.messenger == "max":
        await adapter.send_image(f"user:{account.account_id}", image_path, AI_RESULT_DISCLAIMER)
    lead = await db.get(Lead, generation.lead_id) if generation.lead_id else None
    if lead:
        await NotifyService(adapter, settings.MAX_MANAGER_CHAT_IDS).notify_generation_ready(
            lead, image_path
        )


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
