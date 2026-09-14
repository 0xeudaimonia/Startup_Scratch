from __future__ import annotations

from sqlalchemy import select

from database.models import Company
from database.session import SessionLocal
from workers.celery_impl import celery_app
from workers.scraping.ingest import refresh_company_metrics


@celery_app.task
def rescore_all() -> int:
    session = SessionLocal()
    companies = session.scalars(select(Company)).all()
    for company in companies:
        refresh_company_metrics(company, session)
    session.commit()
    count = len(companies)
    session.close()
    return count
