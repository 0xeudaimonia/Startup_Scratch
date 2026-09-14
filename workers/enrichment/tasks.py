from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from database.models import Company
from database.session import SessionLocal
from models.raw_company import RawCompany
from workers.celery_impl import celery_app
from workers.enrichment.website import apply_website_enrichment, enrich_from_website
from workers.scraping.ingest import ingest_raw_company, refresh_company_metrics


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def enrich_stale_companies(self, limit: int = 20) -> int:
    session = SessionLocal()
    cutoff = datetime.now(UTC) - timedelta(days=1)
    companies = session.scalars(
        select(Company)
        .where(Company.website_url.is_not(None))
        .where(Company.last_updated_at < cutoff)
        .limit(limit)
    ).all()
    count = 0
    for company in companies:
        if not company.website_url:
            continue
        try:
            enrichment = asyncio.run(enrich_from_website(company.website_url))
        except Exception:
            continue
        raw = RawCompany(
            source_name="website_enrichment",
            source_url=company.website_url,
            confidence=0.8,
            name=company.name,
            website_url=company.website_url,
            linkedin_url=company.linkedin_url,
        )
        apply_website_enrichment(raw, enrichment)
        ingest_raw_company(session, raw)
        count += 1
    session.commit()
    session.close()
    return count
