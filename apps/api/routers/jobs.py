from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.schemas import JobOut, PaginatedJobs
from database.models import Job
from database.session import get_db

router = APIRouter(tags=["jobs"])


@router.get("/jobs", response_model=PaginatedJobs)
async def list_jobs(
    search: str | None = None,
    role_category: str | None = None,
    remote_type: str | None = None,
    active: bool = True,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedJobs:
    stmt = select(Job).options(selectinload(Job.company)).where(Job.active.is_(active))
    if search:
        stmt = stmt.where(Job.title.ilike(f"%{search}%"))
    if role_category:
        stmt = stmt.where(Job.role_category == role_category)
    if remote_type:
        stmt = stmt.where(Job.remote_type == remote_type)
    rows = (await db.scalars(stmt.order_by(Job.last_seen_at.desc()))).all()
    total = len(rows)
    page_rows = rows[(page - 1) * page_size : page * page_size]
    items = []
    for job in page_rows:
        payload = JobOut.model_validate(job).model_dump()
        if job.company:
            payload["company_name"] = job.company.name
            payload["company_slug"] = job.company.slug
        items.append(JobOut.model_validate(payload))
    return PaginatedJobs(items=items, total=total, page=page, page_size=page_size)
