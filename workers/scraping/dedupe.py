from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.orm import Session

from common.urls import normalize_company_name, normalize_domain
from database.models import Company, CompanySource, DuplicateCandidate


@dataclass
class DuplicateMatch:
    company: Company | None
    confidence: float
    reason: str
    should_merge: bool


HIGH_CONFIDENCE = 0.92
REVIEW_CONFIDENCE = 0.78


def find_duplicate(
    session: Session,
    *,
    name: str,
    website_url: str | None = None,
    linkedin_url: str | None = None,
    source_name: str | None = None,
    external_id: str | None = None,
    country: str | None = None,
) -> DuplicateMatch:
    domain = normalize_domain(website_url)
    normalized = normalize_company_name(name)

    if domain:
        company = session.scalar(select(Company).where(Company.normalized_domain == domain))
        if company:
            return DuplicateMatch(company, 0.99, "normalized_domain", True)

    if website_url:
        company = session.scalar(select(Company).where(Company.website_url == website_url))
        if company:
            return DuplicateMatch(company, 0.97, "official_website", True)

    if source_name and external_id:
        source_row = session.scalar(
            select(CompanySource).where(
                CompanySource.source_name == source_name,
                CompanySource.external_id == external_id,
            )
        )
        if source_row:
            company = session.get(Company, source_row.company_id)
            if company:
                return DuplicateMatch(company, 0.98, "external_id", True)

    if linkedin_url:
        company = session.scalar(select(Company).where(Company.linkedin_url == linkedin_url))
        if company:
            return DuplicateMatch(company, 0.95, "linkedin_url", True)

    if normalized:
        company = session.scalar(select(Company).where(Company.normalized_name == normalized))
        if company:
            return DuplicateMatch(company, 0.93, "normalized_name", True)
        if country:
            company = session.scalar(
                select(Company).where(
                    Company.normalized_name == normalized,
                    Company.headquarters_country == country,
                )
            )
            if company:
                return DuplicateMatch(company, 0.9, "name_and_country", True)

        candidates = session.scalars(select(Company).limit(400)).all()
        best: tuple[Company, float] | None = None
        for candidate in candidates:
            if not candidate.normalized_name:
                continue
            score = fuzz.token_sort_ratio(normalized, candidate.normalized_name) / 100.0
            if best is None or score > best[1]:
                best = (candidate, score)
        if best:
            company, score = best
            if score >= HIGH_CONFIDENCE:
                return DuplicateMatch(company, score, "fuzzy_name", True)
            if score >= REVIEW_CONFIDENCE:
                return DuplicateMatch(company, score, "fuzzy_name", False)

    return DuplicateMatch(None, 0.0, "none", False)


def record_duplicate_candidate(
    session: Session,
    match: DuplicateMatch,
    *,
    incoming_name: str,
    incoming_domain: str | None,
) -> DuplicateCandidate | None:
    if match.company is None or match.should_merge:
        return None
    candidate = DuplicateCandidate(
        company_id=match.company.id,
        incoming_name=incoming_name,
        incoming_domain=incoming_domain,
        match_reason=match.reason,
        confidence=match.confidence,
        status="pending",
    )
    session.add(candidate)
    return candidate
