from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime

import httpx
from bs4 import BeautifulSoup

from common.currency import parse_funding_amount, to_usd
from common.funding import normalize_funding_stage
from common.http import fetch_text
from common.logging import get_logger
from models.enums import FundingStage
from models.raw_company import RawCompany, RawFundingRound
from sources.base import StartupSource

logger = get_logger("startup_radar.growthlist")

MAX_PUBLIC_ROWS = 100
PUBLIC_LIST_URL = "https://growthlist.co/funded-startups/"


@dataclass(frozen=True)
class PublicList:
    path: str
    default_stage: FundingStage | None = None
    default_country: str | None = None
    default_city: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def url(self) -> str:
        return f"https://growthlist.co/{self.path.strip('/')}/"


PUBLIC_LISTS: tuple[PublicList, ...] = (
    PublicList("funded-startups"),
    PublicList("pre-seed-startups", default_stage=FundingStage.PRE_SEED),
    PublicList("seed-startups", default_stage=FundingStage.SEED),
    PublicList("series-a-startups", default_stage=FundingStage.SERIES_A),
    PublicList("series-b-startups", default_stage=FundingStage.SERIES_B),
    PublicList("ai-startups", tags=("AI",)),
    PublicList("list-of-funded-saas-startups", tags=("SaaS",)),
    PublicList("b2b-startups", tags=("B2B",)),
    PublicList("b2b-saas-startups", tags=("B2B", "SaaS")),
    PublicList("fintech-startups", tags=("FinTech",)),
    PublicList("e-commerce-startups", tags=("E-commerce",)),
    PublicList("e-commerce-software-startups", tags=("E-commerce", "Software")),
    PublicList("united-states-startups", default_country="United States"),
    PublicList(
        "san-francisco-startups",
        default_country="United States",
        default_city="San Francisco",
    ),
    PublicList("finland-startups", default_country="Finland"),
)


def parse_growthlist_date(value: str | None) -> date | None:
    if not value:
        return None
    text = value.strip()
    for fmt in ("%b %Y", "%B %Y", "%Y-%m-%d", "%b %d, %Y"):
        try:
            parsed = datetime.strptime(text, fmt)
            return date(parsed.year, parsed.month, parsed.day if "%d" in fmt else 1)
        except ValueError:
            continue
    return None


def parse_public_table(html: str) -> list[dict[str, str]]:
    """Parse a public Growth List HTML table. Never reads member-only pages."""
    soup = BeautifulSoup(html, "lxml")
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue
        headers = [cell.get_text(" ", strip=True).lower() for cell in rows[0].find_all(["th", "td"])]
        if "name" not in headers or "website" not in headers:
            continue
        records: list[dict[str, str]] = []
        for row in rows[1 : MAX_PUBLIC_ROWS + 1]:
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
            if len(cells) < len(headers):
                continue
            item = {headers[i]: cells[i] for i in range(len(headers))}
            if item.get("name"):
                records.append(item)
        if records:
            return records
    return []


def _stage_known(value: FundingStage | str | None) -> bool:
    return value not in (None, "", FundingStage.UNKNOWN, "unknown")


def _clip(value: str | None, limit: int) -> str | None:
    if not value:
        return None
    text = value.strip()
    return text[:limit] if text else None


def _looks_like_sentence(value: str) -> bool:
    if len(value) > 80 or value.count(" ") > 8:
        return True
    return bool(re.search(r"\b(i have reviewed|classified it|accordingly)\b", value, re.I))


def parse_industries(text: str | None, extra: tuple[str, ...] = ()) -> list[str]:
    parts = [part.strip() for part in (text or "").split(",") if part.strip()]
    labels = [part for part in parts if not _looks_like_sentence(part)]
    return _unique([*labels, *extra])


def parse_country(value: str | None, default: str | None = None) -> str | None:
    text = (value or "").strip()
    if not text:
        return _clip(default, 100)
    if parse_growthlist_date(text) or _looks_like_sentence(text) or len(text.split()) > 4:
        return _clip(default, 100)
    if re.search(r"[$€£]|\d", text):
        return _clip(default, 100)
    if _stage_known(normalize_funding_stage(text)) and not re.search(r"united|kingdom|states|korea|africa", text, re.I):
        return _clip(default, 100)
    return _clip(text, 100)


def parse_list_amount(text: str | None) -> tuple[float | None, str | None]:
    raw = (text or "").strip()
    if not raw or parse_growthlist_date(raw) or not re.search(r"\d", raw):
        return None, None
    if re.search(r"\b(pre-?seed|seed|series|equity|grant)\b", raw, re.I) and not re.search(r"[$€£]", raw):
        return None, None
    return parse_funding_amount(raw)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        key = value.strip()
        if not key:
            continue
        folded = key.lower()
        if folded in seen:
            continue
        seen.add(folded)
        ordered.append(key)
    return ordered


def _company_key(company: RawCompany) -> str:
    return (company.website_url or company.name).lower().rstrip("/")


def _row_to_company(row: dict[str, str], page: PublicList | None = None) -> RawCompany | None:
    page = page or PUBLIC_LISTS[0]
    name = (row.get("name") or "").strip()
    website = (row.get("website") or "").strip()
    if not name or not website:
        return None
    if not re.match(r"^https?://", website, re.I):
        website = f"https://{website}"
    amount_text = row.get("funding amount (usd)") or row.get("funding amount") or ""
    amount, currency = parse_list_amount(amount_text)
    if amount is not None:
        currency = currency or "USD"
    stage_text = row.get("funding type") or ""
    stage = normalize_funding_stage(stage_text)
    if not _stage_known(stage):
        stage = normalize_funding_stage(amount_text)
    if not _stage_known(stage) and page.default_stage:
        stage = page.default_stage
    announced = parse_growthlist_date(row.get("last funding date")) or parse_growthlist_date(stage_text)
    industries = parse_industries(row.get("industry"), page.tags)
    country = parse_country(row.get("country"), page.default_country)
    city = page.default_city
    business_model = [tag for tag in page.tags if tag in {"B2B", "SaaS", "E-commerce"}]
    primary = _clip(industries[0] if industries else None, 100)
    return RawCompany(
        external_id=website or name,
        source_name="growthlist",
        source_url=page.url,
        confidence=0.55,
        name=name,
        short_description=primary,
        website_url=website,
        headquarters_country=country,
        headquarters_city=city,
        latest_funding_round=str(stage) if stage else None,
        latest_funding_amount=amount,
        latest_funding_currency=currency,
        latest_funding_usd=to_usd(amount, currency),
        latest_funding_date=announced,
        funding_stage=stage,
        funding_rounds=[
            RawFundingRound(
                round_type=str(stage) if stage else None,
                amount=amount,
                currency=currency,
                amount_usd=to_usd(amount, currency),
                announced_date=announced,
                source="growthlist",
                source_url=page.url,
            )
        ]
        if amount or announced or stage
        else [],
        primary_industry=primary,
        industries=industries,
        categories=list(page.tags),
        keywords=industries,
        business_model=business_model,
        source_urls=[page.url],
        raw_payload={"name": name, "website": website, "country": country, "lists": [page.path]},
    )


def merge_companies(first: RawCompany, second: RawCompany) -> RawCompany:
    data = first.model_dump()
    other = second.model_dump()
    for key in ("source_urls", "industries", "keywords", "categories", "business_model"):
        data[key] = _unique([*(data.get(key) or []), *(other.get(key) or [])])
    lists = _unique([*(data.get("raw_payload") or {}).get("lists", []), *(other.get("raw_payload") or {}).get("lists", [])])
    data["raw_payload"] = {**(other.get("raw_payload") or {}), **(data.get("raw_payload") or {}), "lists": lists}
    fillable = (
        "headquarters_country",
        "headquarters_city",
        "latest_funding_amount",
        "latest_funding_currency",
        "latest_funding_usd",
        "latest_funding_date",
        "latest_funding_round",
        "short_description",
        "primary_industry",
    )
    for key in fillable:
        if not data.get(key) and other.get(key):
            data[key] = other[key]
    if not _stage_known(data.get("funding_stage")) and _stage_known(other.get("funding_stage")):
        data["funding_stage"] = other["funding_stage"]
        data["latest_funding_round"] = other.get("latest_funding_round") or data.get("latest_funding_round")
    if not data.get("funding_rounds") and other.get("funding_rounds"):
        data["funding_rounds"] = other["funding_rounds"]
    if data.get("source_urls"):
        data["source_url"] = data["source_urls"][0]
    return RawCompany.model_validate(data)


def companies_from_html_pages(pages: list[tuple[PublicList, str]]) -> list[RawCompany]:
    merged: dict[str, RawCompany] = {}
    for page, html in pages:
        for row in parse_public_table(html):
            raw = _row_to_company(row, page)
            if raw is None:
                continue
            key = _company_key(raw)
            existing = merged.get(key)
            merged[key] = merge_companies(existing, raw) if existing else raw
    return list(merged.values())


class GrowthListSource(StartupSource):
    name = "growthlist"
    category = "funding"
    description = (
        "Public Growth List sample tables across funding-stage, industry, and location pages. "
        "Does not scrape paid Google Sheets reports, the member area, or contact emails."
    )

    async def discover(self) -> list[RawCompany]:
        pages: list[tuple[PublicList, str]] = []
        errors: list[str] = []
        for item in PUBLIC_LISTS:
            try:
                html = await fetch_text(item.url)
            except (httpx.HTTPStatusError, httpx.HTTPError, PermissionError) as exc:
                status = getattr(getattr(exc, "response", None), "status_code", None)
                detail = f"HTTP {status}" if status else type(exc).__name__
                message = f"{item.url} ({detail})"
                logger.warning("growthlist_page_skipped", extra={"url": item.url, "error": str(exc)})
                errors.append(message)
                continue
            pages.append((item, html))
        if not pages:
            raise RuntimeError(
                "Growth List public pages were all blocked or empty. "
                f"This adapter only reads public sample tables and does not bypass Cloudflare, login, or paid lists. Errors: {errors}"
            )
        companies = companies_from_html_pages(pages)
        if errors:
            logger.warning("growthlist_partial", extra={"fetched": len(pages), "skipped": errors})
        return companies
