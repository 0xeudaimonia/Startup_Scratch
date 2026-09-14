from __future__ import annotations

import re
from datetime import datetime

import feedparser

from common.currency import parse_funding_amount, to_usd
from common.funding import normalize_funding_stage
from models.raw_company import RawCompany, RawFundingRound, RawInvestor
from sources.base import StartupSource

FUNDING_PATTERNS = [
    re.compile(
        r"(?P<name>[A-Z][\w\s.&'-]{1,60}?)\s+(?:raises|raised|secures|secured|closes|closed)\s+"
        r"(?P<amount>[$€£]?\d[\d.,]*\s*(?:million|billion|m|bn)?)\s*(?P<round>pre-seed|seed|series\s*[a-g]|growth)?",
        re.I,
    )
]


def extract_funding_from_text(title: str, summary: str = "") -> dict:
    blob = f"{title}. {summary}"
    for pattern in FUNDING_PATTERNS:
        match = pattern.search(blob)
        if not match:
            continue
        amount, currency = parse_funding_amount(match.group("amount"))
        round_type = match.group("round")
        return {
            "name": match.group("name").strip(" -–|"),
            "amount": amount,
            "currency": currency,
            "round_type": str(normalize_funding_stage(round_type)) if round_type else None,
        }
    return {}


class RssNewsSource(StartupSource):
    category = "news"
    feed_url: str = ""

    async def discover(self) -> list[RawCompany]:
        parsed = feedparser.parse(self.feed_url)
        companies: list[RawCompany] = []
        for entry in parsed.entries[:25]:
            title = entry.get("title") or ""
            summary = entry.get("summary") or entry.get("description") or ""
            extracted = extract_funding_from_text(title, summary)
            if not extracted:
                continue
            published = None
            if entry.get("published_parsed"):
                published = datetime(*entry.published_parsed[:6]).date()
            amount = extracted.get("amount")
            currency = extracted.get("currency")
            companies.append(
                RawCompany(
                    external_id=entry.get("id") or entry.get("link"),
                    source_name=self.name,
                    source_url=entry.get("link"),
                    confidence=0.45,
                    name=extracted["name"],
                    short_description=title,
                    description=re.sub(r"<[^>]+>", "", summary)[:1500],
                    latest_funding_amount=amount,
                    latest_funding_currency=currency,
                    latest_funding_usd=to_usd(amount, currency),
                    latest_funding_date=published,
                    funding_stage=extracted.get("round_type"),
                    funding_rounds=[
                        RawFundingRound(
                            round_type=extracted.get("round_type"),
                            amount=amount,
                            currency=currency,
                            amount_usd=to_usd(amount, currency),
                            announced_date=published,
                            source=self.name,
                            source_url=entry.get("link"),
                        )
                    ],
                    source_urls=[entry.get("link")] if entry.get("link") else [],
                    raw_payload={"title": title, "link": entry.get("link"), "summary": summary},
                )
            )
        return companies


class TechCrunchSource(RssNewsSource):
    name = "techcrunch"
    description = "TechCrunch funding/startups RSS. Articles are evidence, not canonical records."
    feed_url = "https://techcrunch.com/tag/funding/feed/"


class EUStartupsSource(RssNewsSource):
    name = "eu_startups"
    description = "EU-Startups RSS feed for European funding coverage."
    feed_url = "https://www.eu-startups.com/feed/"


class SiftedSource(RssNewsSource):
    name = "sifted"
    description = "Sifted RSS feed. Respects robots.txt; skipped if disallowed."
    feed_url = "https://sifted.eu/feed"
