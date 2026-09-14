from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from tenacity import retry, stop_after_attempt, wait_exponential

from common.logging import get_logger
from database.models import Job, ScrapeRun
from database.session import SessionLocal
from models.enums import ScrapeStatus
from sources.base import SourceDisabledError
from sources.registry import get_source, sources_by_category
from workers.celery_impl import celery_app
from workers.scraping.ingest import ingest_raw_company

logger = get_logger("startup_radar.scraper")


def _run_async(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    # FastAPI already has an event loop; run discovery on a worker thread.
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


@retry(wait=wait_exponential(multiplier=2, min=2, max=60), stop=stop_after_attempt(3), reraise=True)
def _discover_and_ingest(source_name: str) -> dict:
    source = get_source(source_name)
    session = SessionLocal()
    run = ScrapeRun(source=source_name, status=ScrapeStatus.RUNNING)
    session.add(run)
    session.commit()
    session.refresh(run)
    started = datetime.now(UTC)
    created = updated = duplicates = found = 0
    errors: list[str] = []
    try:
        if not source.is_enabled():
            raise SourceDisabledError(source.requires or f"{source_name} is disabled")
        records = _run_async(source.discover())
        found = len(records)
        for raw in records:
            try:
                _, action = ingest_raw_company(session, raw)
                if action == "created":
                    created += 1
                elif action == "updated":
                    updated += 1
                elif action == "review":
                    duplicates += 1
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{raw.name}: {exc}")
                logger.exception("ingest_failed", extra={"source": source_name, "company": raw.name})
        session.commit()
        status = ScrapeStatus.SUCCESS if not errors else ScrapeStatus.PARTIAL
    except SourceDisabledError as exc:
        errors.append(str(exc))
        status = ScrapeStatus.FAILED
        session.rollback()
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{type(exc).__name__}: {exc}")
        status = ScrapeStatus.FAILED
        session.rollback()
        logger.exception("source_failed", extra={"source": source_name})
    duration = (datetime.now(UTC) - started).total_seconds()
    run = session.get(ScrapeRun, run.id)
    if run:
        run.completed_at = datetime.now(UTC)
        run.status = status
        run.records_found = found
        run.records_created = created
        run.records_updated = updated
        run.duplicate_records = duplicates
        run.errors = errors
        run.duration_seconds = duration
        session.commit()
    session.close()
    logger.info(
        "scrape_complete",
        extra={
            "source": source_name,
            "status": status,
            "duration": duration,
            "records": found,
            "created": created,
            "errors": len(errors),
        },
    )
    return {
        "source": source_name,
        "status": status,
        "records_found": found,
        "records_created": created,
        "records_updated": updated,
        "duplicate_records": duplicates,
        "errors": errors,
        "duration_seconds": duration,
        "run_id": str(run.id) if run else None,
    }


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def run_source(self, source_name: str) -> dict:
    return _discover_and_ingest(source_name)


@celery_app.task
def run_category(category: str) -> list[dict]:
    results = []
    for source in sources_by_category(category):
        if source.is_enabled():
            results.append(_discover_and_ingest(source.name))
    return results


@celery_app.task
def mark_stale_jobs() -> int:
    session = SessionLocal()
    cutoff = datetime.now(UTC) - timedelta(days=21)
    jobs = session.query(Job).filter(Job.active.is_(True), Job.last_seen_at < cutoff).all()
    for job in jobs:
        job.active = False
    session.commit()
    count = len(jobs)
    session.close()
    return count


def run_source_sync(source_name: str) -> dict:
    return _discover_and_ingest(source_name)
