from __future__ import annotations

from common.config import settings
from common.http import fetch_json
from models.raw_company import RawCompany
from sources.accelerators.ycombinator import YC_HIRING, YCombinatorSource


class YCJobsSource(YCombinatorSource):
    """YC companies currently hiring, using the public yc-oss hiring.json dataset."""

    name = "yc_jobs"
    category = "job_boards"
    description = "Y Combinator hiring companies from the public yc-oss hiring.json dataset."

    async def discover(self) -> list[RawCompany]:
        hiring = await fetch_json(YC_HIRING)
        if not isinstance(hiring, list):
            return []
        seen: set[str] = set()
        companies: list[RawCompany] = []
        for item in hiring:
            if not item.get("isHiring") and not item.get("jobs"):
                continue
            slug = str(item.get("slug") or item.get("id") or "")
            if not slug or slug in seen:
                continue
            seen.add(slug)
            companies.append(self._to_raw(item))
            if len(companies) >= settings.yc_max_companies:
                break
        return companies
