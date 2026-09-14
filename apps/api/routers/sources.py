from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import SavedViewIn, SavedViewOut, ScrapeRequest, ScrapeRunOut, SourceOut
from database.models import SavedView, ScrapeRun
from database.session import get_db
from sources.registry import all_sources, get_source
from workers.scraping.tasks import run_source_sync

router = APIRouter(tags=["sources"])


@router.get("/sources", response_model=list[SourceOut])
async def list_sources(db: AsyncSession = Depends(get_db)) -> list[SourceOut]:
    items: list[SourceOut] = []
    for source in all_sources():
        last = await db.scalar(
            select(ScrapeRun).where(ScrapeRun.source == source.name).order_by(ScrapeRun.started_at.desc())
        )
        items.append(
            SourceOut(
                name=source.name,
                category=source.category,
                enabled=source.is_enabled(),
                description=source.description,
                requires=source.requires,
                last_run=ScrapeRunOut.model_validate(last) if last else None,
            )
        )
    return items


@router.get("/scrape-runs", response_model=list[ScrapeRunOut])
async def list_scrape_runs(db: AsyncSession = Depends(get_db)) -> list[ScrapeRunOut]:
    rows = (await db.scalars(select(ScrapeRun).order_by(ScrapeRun.started_at.desc()).limit(50))).all()
    return [ScrapeRunOut.model_validate(row) for row in rows]


@router.post("/scrape-runs", response_model=ScrapeRunOut)
async def trigger_scrape(payload: ScrapeRequest) -> ScrapeRunOut:
    try:
        get_source(payload.source)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    result = run_source_sync(payload.source)
    if result.get("status") == "failed" and not result.get("run_id"):
        raise HTTPException(status_code=400, detail=result.get("errors") or "Scrape failed")
    from database.session import SessionLocal

    session = SessionLocal()
    try:
        run = (
            session.query(ScrapeRun)
            .filter(ScrapeRun.source == payload.source)
            .order_by(ScrapeRun.started_at.desc())
            .first()
        )
        if run is None:
            raise HTTPException(status_code=500, detail=result.get("errors") or "Scrape failed")
        return ScrapeRunOut.model_validate(run)
    finally:
        session.close()


@router.get("/saved-views", response_model=list[SavedViewOut])
async def list_saved_views(db: AsyncSession = Depends(get_db)) -> list[SavedViewOut]:
    rows = (await db.scalars(select(SavedView).order_by(SavedView.name))).all()
    return [SavedViewOut.model_validate(row) for row in rows]


@router.post("/saved-views", response_model=SavedViewOut)
async def create_saved_view(payload: SavedViewIn, db: AsyncSession = Depends(get_db)) -> SavedViewOut:
    view = SavedView(name=payload.name, description=payload.description, filters=payload.filters)
    db.add(view)
    await db.commit()
    await db.refresh(view)
    return SavedViewOut.model_validate(view)
