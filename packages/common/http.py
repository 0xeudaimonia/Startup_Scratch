from __future__ import annotations

import asyncio
from collections.abc import Iterable
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from common.config import settings
from common.logging import get_logger

logger = get_logger("startup_radar.http")
_robots_cache: dict[str, RobotFileParser | None] = {}


def build_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers={"User-Agent": settings.user_agent, "Accept": "application/json, text/html;q=0.9"},
        follow_redirects=True,
        timeout=30.0,
    )


async def allowed_by_robots(url: str, user_agent: str | None = None) -> bool:
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = f"{origin}/robots.txt"
    if origin not in _robots_cache:
        parser = RobotFileParser()
        try:
            async with build_client() as client:
                response = await client.get(robots_url)
            if response.status_code >= 400:
                _robots_cache[origin] = None
            else:
                parser.parse(response.text.splitlines())
                _robots_cache[origin] = parser
        except httpx.HTTPError:
            logger.warning("robots_fetch_failed", extra={"url": robots_url})
            _robots_cache[origin] = None
    parser = _robots_cache[origin]
    if parser is None:
        return True
    return parser.can_fetch(user_agent or settings.user_agent, url)


@retry(wait=wait_exponential(multiplier=1, min=1, max=30), stop=stop_after_attempt(3), reraise=True)
async def fetch_json(url: str, *, headers: dict[str, str] | None = None) -> dict | list:
    async with build_client() as client:
        if not await allowed_by_robots(url):
            raise PermissionError(f"robots.txt disallows {url}")
        await asyncio.sleep(settings.scraper_request_delay_seconds)
        response = await client.get(url, headers=headers)
        if response.status_code in {401, 403, 429, 503}:
            logger.warning(
                "source_blocked",
                extra={"url": url, "status": response.status_code},
            )
            response.raise_for_status()
        response.raise_for_status()
        return response.json()


@retry(wait=wait_exponential(multiplier=1, min=1, max=30), stop=stop_after_attempt(3), reraise=True)
async def fetch_text(url: str) -> str:
    async with build_client() as client:
        if not await allowed_by_robots(url):
            raise PermissionError(f"robots.txt disallows {url}")
        await asyncio.sleep(settings.scraper_request_delay_seconds)
        response = await client.get(url)
        if response.status_code in {401, 403, 429, 503}:
            logger.warning("source_blocked", extra={"url": url, "status": response.status_code})
            response.raise_for_status()
        response.raise_for_status()
        return response.text


async def bounded_gather(coroutines: Iterable, limit: int | None = None) -> list:
    semaphore = asyncio.Semaphore(limit or settings.scraper_concurrency)

    async def run(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*(run(coro) for coro in coroutines), return_exceptions=True)
