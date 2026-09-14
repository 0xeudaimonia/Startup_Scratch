from __future__ import annotations

from datetime import datetime

from common.http import fetch_json
from models.raw_company import RawCompany
from sources.base import StartupSource

HN_SEARCH = (
    "https://hn.algolia.com/api/v1/search_by_date"
    "?query=Show%20HN&tags=story&hitsPerPage=20"
)


class HackerNewsLaunchSource(StartupSource):
    name = "hackernews"
    category = "launch_platforms"
    description = "Hacker News Algolia API for recent Show HN launches."

    async def discover(self) -> list[RawCompany]:
        payload = await fetch_json(HN_SEARCH)
        companies: list[RawCompany] = []
        for hit in payload.get("hits") or []:
            url = hit.get("url")
            title = hit.get("title") or ""
            if not url or "show hn" not in title.lower():
                continue
            name = title.split(":", 1)[-1].strip() if ":" in title else title.replace("Show HN", "").strip(" :-")
            if not name:
                continue
            created = hit.get("created_at")
            launch_date = (
                datetime.fromisoformat(created.replace("Z", "+00:00")).date() if created else None
            )
            companies.append(
                RawCompany(
                    external_id=str(hit.get("objectID")),
                    source_name=self.name,
                    source_url=f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    confidence=0.55,
                    name=name[:120],
                    short_description=title,
                    description=hit.get("story_text") or title,
                    website_url=url,
                    product_launch_date=launch_date,
                    source_urls=[url],
                    raw_payload=hit,
                )
            )
        return companies
