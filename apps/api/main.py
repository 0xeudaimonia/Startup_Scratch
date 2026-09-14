from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import companies, jobs, sources, stats
from common.logging import configure_logging
from common.config import settings

configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(
    title="Startup Radar API",
    version="0.1.0",
    description="Discover, enrich, and score newly funded remote-friendly startups.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(sources.router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
