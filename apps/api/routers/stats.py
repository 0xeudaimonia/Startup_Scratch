from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import StatsOut
from database.models import Company, Job
from database.session import get_db
from models.enums import RemotePolicy

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=StatsOut)
async def get_stats(db: AsyncSession = Depends(get_db)) -> StatsOut:
    now = datetime.now(UTC)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week = today - timedelta(days=7)
    year_ago = (today - timedelta(days=365)).date()
    week_date = week.date()

    async def count(stmt) -> int:
        return int(await db.scalar(stmt) or 0)

    avg_score = await db.scalar(select(func.avg(Company.opportunity_score))) or 0
    return StatsOut(
        companies_discovered_today=await count(select(func.count(Company.id)).where(Company.first_discovered_at >= today)),
        companies_discovered_this_week=await count(
            select(func.count(Company.id)).where(Company.first_discovered_at >= week)
        ),
        companies_funded_this_week=await count(
            select(func.count(Company.id)).where(Company.latest_funding_date >= week_date)
        ),
        recently_founded=await count(select(func.count(Company.id)).where(Company.founded_date >= year_ago)),
        global_remote=await count(
            select(func.count(Company.id)).where(Company.remote_policy == RemotePolicy.GLOBAL_REMOTE)
        ),
        hiring_engineers=await count(select(func.count(Company.id)).where(Company.hiring_engineers.is_(True))),
        engineering_jobs=await count(
            select(func.count(Job.id)).where(Job.active.is_(True), Job.role_category.is_not(None))
        ),
        average_opportunity_score=round(float(avg_score), 1),
        total_companies=await count(select(func.count(Company.id))),
    )
