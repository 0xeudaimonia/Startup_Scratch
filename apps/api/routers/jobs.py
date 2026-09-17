from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.schemas import CheckedUpdate, JobOut, PaginatedJobs
from database.models import Job
from database.session import get_db

router = APIRouter(tags=["jobs"])


def serialize_job(job: Job) -> JobOut:
    payload = JobOut.model_validate(job).model_dump()
    if job.company:
        payload["company_name"] = job.company.name
        payload["company_slug"] = job.company.slug
    return JobOut.model_validate(payload)


@router.get("/jobs", response_model=PaginatedJobs)
async def list_jobs(
    search: str | None = None,
    role_category: str | None = None,
    remote_type: str | None = None,
    active: bool = True,
    is_checked: bool | None = None,
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
    if is_checked is not None:
        stmt = stmt.where(Job.is_checked.is_(is_checked))
    rows = (await db.scalars(stmt.order_by(Job.last_seen_at.desc()))).all()
    total = len(rows)
    page_rows = rows[(page - 1) * page_size : page * page_size]
    return PaginatedJobs(
        items=[serialize_job(job) for job in page_rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch("/jobs/{job_id}", response_model=JobOut)
async def update_job(
    job_id: uuid.UUID,
    payload: CheckedUpdate,
    db: AsyncSession = Depends(get_db),
) -> JobOut:
    job = await db.scalar(select(Job).options(selectinload(Job.company)).where(Job.id == job_id))
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    job.is_checked = payload.is_checked
    await db.commit()
    job = await db.scalar(select(Job).options(selectinload(Job.company)).where(Job.id == job.id))
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return serialize_job(job)
