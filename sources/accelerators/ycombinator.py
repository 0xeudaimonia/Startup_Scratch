from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from common.config import settings
from common.http import fetch_json
from models.enums import EmployeeRange, FundingStage, RemotePolicy
from models.raw_company import RawCompany, RawInvestor, RawJob
from sources.base import StartupSource

YC_META = "https://yc-oss.github.io/api/meta.json"
YC_BATCH = "https://yc-oss.github.io/api/batches/{batch}.json"
YC_HIRING = "https://yc-oss.github.io/api/companies/hiring.json"

_SEASON_RANK = {"winter": 1, "spring": 2, "summer": 3, "fall": 4, "autumn": 4}
_SEASON_MONTH = {"winter": 1, "spring": 4, "summer": 6, "fall": 9, "autumn": 9}


def _parse_batch_date(batch: str) -> date | None:
    parts = batch.replace("-", " ").split()
    if len(parts) < 2 or not parts[-1].isdigit():
        return None
    year = int(parts[-1])
    season = parts[0].lower()
    month = _SEASON_MONTH.get(season, 1)
    return date(year, month, 1)


def _batch_sort_key(slug: str) -> tuple[int, int]:
    parts = slug.replace("_", "-").split("-")
    if len(parts) < 2 or not parts[-1].isdigit():
        return (0, 0)
    return (int(parts[-1]), _SEASON_RANK.get(parts[0].lower(), 0))


def latest_batch(batches: dict[str, Any] | list[Any] | None) -> dict[str, str] | None:
    """Return {slug, api, name} for the newest named YC batch."""
    if not batches:
        return None
    if isinstance(batches, list):
        slugs = []
        for item in batches:
            if isinstance(item, str):
                slugs.append(item)
            elif isinstance(item, dict):
                slugs.append(str(item.get("slug") or item.get("name") or ""))
        slugs = [slug for slug in slugs if slug and slug.lower() != "unspecified"]
        if not slugs:
            return None
        slug = max(slugs, key=_batch_sort_key)
        return {"slug": slug, "api": YC_BATCH.format(batch=slug), "name": slug}

    named = [(slug, info or {}) for slug, info in batches.items() if slug.lower() != "unspecified"]
    if not named:
        return None
    slug, info = max(named, key=lambda item: _batch_sort_key(item[0]))
    return {
        "slug": slug,
        "api": str(info.get("api") or YC_BATCH.format(batch=slug)),
        "name": str(info.get("name") or slug),
    }


def _team_size_range(value: Any) -> tuple[int | None, int | None, str | None]:
    mapping = {
        "1-10": (1, 10, EmployeeRange.RANGE_1_10),
        "11-50": (11, 50, EmployeeRange.RANGE_11_50),
        "51-100": (51, 100, EmployeeRange.RANGE_51_100),
        "101-200": (101, 200, EmployeeRange.RANGE_101_200),
        "201-500": (201, 500, EmployeeRange.RANGE_201_500),
        "501-1000": (501, 1000, EmployeeRange.RANGE_501_1000),
        "1000+": (1000, None, EmployeeRange.RANGE_1000_PLUS),
    }
    if value is None or value == "":
        return None, None, None
    if isinstance(value, str) and value in mapping:
        return mapping[value]
    if isinstance(value, str) and value.isdigit():
        value = int(value)
    if isinstance(value, int):
        if value <= 10:
            return 1, 10, EmployeeRange.RANGE_1_10
        if value <= 50:
            return 11, 50, EmployeeRange.RANGE_11_50
        if value <= 100:
            return 51, 100, EmployeeRange.RANGE_51_100
        if value <= 200:
            return 101, 200, EmployeeRange.RANGE_101_200
        if value <= 500:
            return 201, 500, EmployeeRange.RANGE_201_500
        if value <= 1000:
            return 501, 1000, EmployeeRange.RANGE_501_1000
        return 1000, None, EmployeeRange.RANGE_1000_PLUS
    return None, None, None


class YCombinatorSource(StartupSource):
    name = "ycombinator"
    category = "accelerators"
    description = "Public YC company directory via the yc-oss daily JSON dataset."

    async def discover(self) -> list[RawCompany]:
        meta = await fetch_json(YC_META)
        if not isinstance(meta, dict):
            raise ValueError("Unexpected YC meta.json payload")
        records: list[dict] = []
        batch = latest_batch(meta.get("batches"))
        if batch:
            payload = await fetch_json(batch["api"])
            if isinstance(payload, list):
                records.extend(payload)
        try:
            hiring = await fetch_json(YC_HIRING)
            if isinstance(hiring, list):
                records.extend(hiring[: settings.yc_max_companies])
        except Exception:
            pass
        seen: set[str] = set()
        companies: list[RawCompany] = []
        for item in records:
            slug = str(item.get("slug") or item.get("id") or "")
            if not slug or slug in seen:
                continue
            seen.add(slug)
            companies.append(self._to_raw(item))
            if len(companies) >= settings.yc_max_companies:
                break
        return companies

    async def get_company(self, external_id: str) -> RawCompany | None:
        for company in await self.discover():
            if company.external_id == external_id:
                return company
        return None

    def _to_raw(self, item: dict) -> RawCompany:
        batch = item.get("batch") or ""
        founded = _parse_batch_date(str(batch))
        min_emp, max_emp, emp_range = _team_size_range(item.get("team_size") or item.get("teamSize"))
        yc_url = item.get("url") if "ycombinator.com" in str(item.get("url") or "") else (
            f"https://www.ycombinator.com/companies/{item.get('slug')}" if item.get("slug") else None
        )
        company_site = item.get("website")
        jobs = []
        for job in item.get("jobs") or []:
            jobs.append(
                RawJob(
                    title=job.get("title") or "Software Engineer",
                    location=job.get("location"),
                    job_url=job.get("url") or job.get("applyUrl"),
                    remote_type="global_remote" if "remote" in str(job.get("location") or "").lower() else None,
                    source=self.name,
                )
            )
        remote_policy = RemotePolicy.UNKNOWN
        locations = " ".join(item.get("regions") or []) + " " + str(item.get("all_locations") or "")
        if "remote" in locations.lower() and "united states" not in locations.lower():
            remote_policy = RemotePolicy.REMOTE_FIRST
        return RawCompany(
            external_id=str(item.get("id") or item.get("slug")),
            source_name=self.name,
            source_url=yc_url,
            confidence=0.9,
            name=item.get("name") or "Unknown",
            short_description=item.get("one_liner") or item.get("long_description"),
            description=item.get("long_description") or item.get("one_liner"),
            website_url=company_site,
            yc_url=yc_url,
            linkedin_url=item.get("linkedin_url"),
            twitter_url=item.get("x_url") or item.get("twitter_url"),
            crunchbase_url=item.get("cb_url"),
            github_url=item.get("github_url"),
            logo_url=item.get("small_logo_thumb_url") or item.get("logo_url"),
            headquarters_city=item.get("city"),
            headquarters_country=item.get("country"),
            headquarters_region=(item.get("regions") or [None])[0] if item.get("regions") else None,
            founded_date=founded,
            founded_year=item.get("year_founded") or (founded.year if founded else None),
            employee_count_min=min_emp,
            employee_count_max=max_emp,
            employee_range=emp_range,
            estimated_employee_count=min_emp if min_emp is not None else (
                item.get("team_size") if isinstance(item.get("team_size"), int) else None
            ),
            industries=item.get("industries") or ([item["industry"]] if item.get("industry") else []),
            categories=item.get("tags") or [],
            keywords=item.get("tags") or [],
            funding_stage=FundingStage.SEED,
            investors=[RawInvestor(name="Y Combinator", investor_type="accelerator", is_lead=True)],
            remote_policy=remote_policy,
            jobs=jobs,
            source_urls=[yc_url] if yc_url else [],
            raw_payload={"id": item.get("id"), "slug": item.get("slug"), "batch": item.get("batch")},
            discovered_at=datetime.now(UTC),
        )
