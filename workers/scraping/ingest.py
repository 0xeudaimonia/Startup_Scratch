from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.orm import Session

from common.currency import to_usd
from common.dates import days_between, utcnow
from common.funding import normalize_funding_stage
from common.investors import canonical_investor_name, is_notable_investor, normalize_investor_name
from common.urls import normalize_company_name, normalize_domain, normalize_url
from database.models import (
    Company,
    CompanyInvestor,
    CompanySource,
    FieldObservation,
    FundingRound,
    Investor,
    Job,
    SourceRecord,
)
from models.enums import HiringStatus
from models.raw_company import RawCompany, RawInvestor, RawJob
from scoring.opportunity import ScoringInput, calculate_growth_score, calculate_opportunity_score
from workers.job_detection.extract import classify_engineering_role
from workers.scraping.dedupe import find_duplicate, record_duplicate_candidate


def _hash_payload(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


def _unique_slug(session: Session, name: str, domain: str | None) -> str:
    base = slugify(name) or slugify(domain or "company") or "company"
    slug = base
    n = 2
    while session.scalar(select(Company.id).where(Company.slug == slug)):
        slug = f"{base}-{n}"
        n += 1
    return slug


def _merge_unique(existing: list[str] | None, incoming: list[str] | None) -> list[str]:
    values: list[str] = []
    for item in (*(existing or []), *(incoming or [])):
        if item and item not in values:
            values.append(item)
    return values


def _prefer(current, incoming, incoming_confidence: float, current_confidence: float = 0.5):
    if incoming in (None, "", [], {}):
        return current
    if current in (None, "", [], {}):
        return incoming
    if incoming_confidence >= current_confidence:
        return incoming
    return current


def _upsert_investor(session: Session, raw: RawInvestor | str) -> Investor:
    if isinstance(raw, str):
        name = raw
        investor_type = None
        url = None
        website = None
        country = None
    else:
        name = raw.name
        investor_type = raw.investor_type
        url = raw.url
        website = raw.website
        country = raw.country
    canonical = canonical_investor_name(name)
    investor = session.scalar(
        select(Investor).where(Investor.normalized_name == normalize_investor_name(canonical))
    )
    if investor is None:
        investor = Investor(
            investor_name=canonical,
            normalized_name=normalize_investor_name(canonical),
            investor_type=investor_type or ("accelerator" if is_notable_investor(canonical) else "vc"),
            investor_url=url,
            investor_website=website,
            investor_country=country,
            notable=is_notable_investor(canonical),
        )
        session.add(investor)
        session.flush()
    else:
        investor.notable = investor.notable or is_notable_investor(canonical)
        investor.investor_url = investor.investor_url or url
        investor.investor_website = investor.investor_website or website
    return investor


def refresh_company_metrics(company: Company, session: Session | None = None) -> None:
    today = utcnow().date()
    company.company_age_days = days_between(company.founded_date, today)
    company.funding_recency_days = days_between(company.latest_funding_date, today)
    company.founded_recency_days = days_between(company.founded_date, today)
    company.founder_count = len(company.founders or [])
    company.careers_page_available = bool(company.careers_url or company.jobs_url)

    if session is not None:
        rounds = list(session.scalars(select(FundingRound).where(FundingRound.company_id == company.id)).all())
        jobs = list(
            session.scalars(select(Job).where(Job.company_id == company.id, Job.active.is_(True))).all()
        )
    else:
        rounds = list(company.funding_rounds or [])
        jobs = [job for job in (company.jobs or []) if job.active]

    if rounds:
        dated = [row for row in rounds if row.announced_date]
        latest = max(dated, key=lambda row: row.announced_date) if dated else rounds[-1]
        company.number_of_funding_rounds = len(rounds)
        company.latest_funding_round = latest.round_type
        company.latest_funding_amount = latest.amount
        company.latest_funding_currency = latest.currency
        company.latest_funding_usd = latest.amount_usd or to_usd(latest.amount, latest.currency)
        company.latest_funding_date = latest.announced_date
        if latest.round_type:
            company.funding_stage = str(normalize_funding_stage(latest.round_type))
        company.total_funding_usd = sum(row.amount_usd or 0 for row in rounds) or company.total_funding_usd
        company.total_funding_amount = company.total_funding_usd
        company.total_funding_currency = "USD"

    company.open_job_count = len(jobs)
    company.engineering_job_count = sum(1 for job in jobs if job.role_category)
    company.remote_job_count = sum(
        1 for job in jobs if (job.remote_type or "").lower() not in {"", "onsite", "hybrid"}
    )
    company.global_remote_job_count = sum(
        1
        for job in jobs
        if (job.remote_type or "").lower() in {"global_remote", "worldwide", "anywhere"}
    )
    cutoff_7 = datetime.now(UTC).date()
    company.jobs_added_last_7_days = sum(
        1 for job in jobs if job.first_seen_at and days_between(job.first_seen_at, today) <= 7
    )
    company.jobs_added_last_30_days = sum(
        1 for job in jobs if job.first_seen_at and days_between(job.first_seen_at, today) <= 30
    )
    company.new_job_count = company.jobs_added_last_30_days
    company.hiring_velocity = round(company.jobs_added_last_30_days / 4.0, 2)
    company.is_hiring = company.open_job_count > 0 or bool(company.careers_page_available)
    company.hiring_engineers = company.engineering_job_count > 0
    if company.hiring_engineers:
        company.hiring_status = HiringStatus.HIRING_ENGINEERS
    elif company.is_hiring:
        company.hiring_status = HiringStatus.HIRING
    else:
        company.hiring_status = HiringStatus.NOT_HIRING

    if session is not None:
        links = session.scalars(
            select(CompanyInvestor).where(CompanyInvestor.company_id == company.id)
        ).all()
        company.investor_count = len(links)
        investor_ids = [link.investor_id for link in links]
        notable = 0
        if investor_ids:
            notable = sum(
                1
                for investor in session.scalars(select(Investor).where(Investor.id.in_(investor_ids)))
                if investor.notable
            )
        company.notable_investor_count = notable

    score, breakdown = calculate_opportunity_score(
        ScoringInput(
            latest_funding_date=company.latest_funding_date,
            funding_stage=company.funding_stage,
            estimated_employee_count=company.estimated_employee_count,
            employee_count_max=company.employee_count_max,
            founded_date=company.founded_date,
            hiring_engineers=company.hiring_engineers,
            engineering_job_count=company.engineering_job_count,
            remote_policy=company.remote_policy,
            notable_investor_count=company.notable_investor_count,
            product_launch_recency_days=company.product_launch_recency,
        )
    )
    company.opportunity_score = score
    company.opportunity_score_breakdown = breakdown
    company.growth_score = calculate_growth_score(
        funding_recency_days=company.funding_recency_days,
        founded_recency_days=company.founded_recency_days,
        hiring_velocity=company.hiring_velocity,
        engineering_job_count=company.engineering_job_count,
        notable_investor_count=company.notable_investor_count,
        recent_news_count=company.recent_news_count,
        employee_growth_signal=company.employee_growth_signal,
    )
    company.last_updated_at = utcnow()


def ingest_raw_company(session: Session, raw: RawCompany) -> tuple[Company | None, str]:
    """Persist a normalized RawCompany. Returns (company, created|updated|skipped|review)."""
    website = normalize_url(raw.website_url)
    domain = normalize_domain(website or raw.website_url)
    match = find_duplicate(
        session,
        name=raw.name,
        website_url=website,
        linkedin_url=raw.linkedin_url,
        source_name=raw.source_name,
        external_id=raw.external_id,
        country=raw.headquarters_country,
    )
    if match.company and not match.should_merge:
        record_duplicate_candidate(
            session, match, incoming_name=raw.name, incoming_domain=domain
        )
        _store_source_record(session, raw, matched=False, company=None)
        return match.company, "review"

    created = False
    company = match.company
    if company is None:
        created = True
        company = Company(
            name=raw.name,
            normalized_name=normalize_company_name(raw.name),
            slug=_unique_slug(session, raw.name, domain),
            first_source=raw.source_name,
            first_discovered_at=raw.discovered_at or utcnow(),
            discovery_sources=[raw.source_name],
            deduplication_confidence=1.0,
        )
        session.add(company)
        session.flush()
    else:
        company.deduplication_confidence = match.confidence
        company.discovery_sources = _merge_unique(company.discovery_sources, [raw.source_name])

    confidence = raw.confidence
    company.name = company.name or raw.name
    company.legal_name = _prefer(company.legal_name, raw.legal_name, confidence)
    company.aliases = _merge_unique(company.aliases, raw.aliases)
    company.description = _prefer(company.description, raw.description, confidence)
    company.short_description = _prefer(company.short_description, raw.short_description, confidence)
    company.logo_url = _prefer(company.logo_url, raw.logo_url, confidence)
    company.website_url = _prefer(company.website_url, website, 0.95 if website else 0)
    company.normalized_domain = company.normalized_domain or domain
    company.careers_url = _prefer(company.careers_url, normalize_url(raw.careers_url), confidence)
    company.jobs_url = _prefer(company.jobs_url, normalize_url(raw.jobs_url), confidence)
    company.linkedin_url = _prefer(company.linkedin_url, raw.linkedin_url, confidence)
    company.github_url = _prefer(company.github_url, raw.github_url, confidence)
    company.twitter_url = _prefer(company.twitter_url, raw.twitter_url, confidence)
    company.crunchbase_url = _prefer(company.crunchbase_url, raw.crunchbase_url, confidence)
    company.product_hunt_url = _prefer(company.product_hunt_url, raw.product_hunt_url, confidence)
    company.wellfound_url = _prefer(company.wellfound_url, raw.wellfound_url, confidence)
    company.yc_url = _prefer(company.yc_url, raw.yc_url, confidence)
    company.source_urls = _merge_unique(company.source_urls, raw.source_urls or ([raw.source_url] if raw.source_url else []))

    company.headquarters_country = _prefer(company.headquarters_country, raw.headquarters_country, confidence)
    company.headquarters_city = _prefer(company.headquarters_city, raw.headquarters_city, confidence)
    company.headquarters_region = _prefer(company.headquarters_region, raw.headquarters_region, confidence)
    company.headquarters_continent = _prefer(company.headquarters_continent, raw.headquarters_continent, confidence)
    company.remote_locations = _merge_unique(company.remote_locations, raw.remote_locations)
    company.operating_countries = _merge_unique(company.operating_countries, raw.operating_countries)

    company.founded_date = _prefer(company.founded_date, raw.founded_date, confidence)
    company.founded_year = company.founded_date.year if company.founded_date else raw.founded_year
    company.founded_month = company.founded_date.month if company.founded_date else raw.founded_month

    if raw.funding_stage:
        company.funding_stage = str(normalize_funding_stage(str(raw.funding_stage)))
    company.total_funding_usd = _prefer(company.total_funding_usd, raw.total_funding_usd, confidence)
    company.latest_funding_amount = _prefer(company.latest_funding_amount, raw.latest_funding_amount, confidence)
    company.latest_funding_usd = _prefer(company.latest_funding_usd, raw.latest_funding_usd, confidence)
    company.latest_funding_date = _prefer(company.latest_funding_date, raw.latest_funding_date, confidence)
    company.latest_funding_currency = _prefer(company.latest_funding_currency, raw.latest_funding_currency, confidence)

    company.employee_count_min = _prefer(company.employee_count_min, raw.employee_count_min, confidence)
    company.employee_count_max = _prefer(company.employee_count_max, raw.employee_count_max, confidence)
    company.employee_range = _prefer(company.employee_range, raw.employee_range, confidence)
    company.estimated_employee_count = _prefer(
        company.estimated_employee_count, raw.estimated_employee_count, confidence
    )
    company.founders = _merge_unique(company.founders, raw.founders)
    company.leadership_team = _merge_unique(company.leadership_team, raw.leadership_team)
    company.engineering_team_size = _prefer(company.engineering_team_size, raw.engineering_team_size, confidence)

    company.primary_industry = _prefer(company.primary_industry, raw.primary_industry, confidence)
    company.industries = _merge_unique(company.industries, raw.industries)
    company.categories = _merge_unique(company.categories, raw.categories)
    company.keywords = _merge_unique(company.keywords, raw.keywords)
    company.business_model = _merge_unique(company.business_model, raw.business_model)

    company.frontend_technologies = _merge_unique(company.frontend_technologies, raw.frontend_technologies)
    company.backend_technologies = _merge_unique(company.backend_technologies, raw.backend_technologies)
    company.databases = _merge_unique(company.databases, raw.databases)
    company.cloud_providers = _merge_unique(company.cloud_providers, raw.cloud_providers)
    company.ai_technologies = _merge_unique(company.ai_technologies, raw.ai_technologies)
    company.devops_technologies = _merge_unique(company.devops_technologies, raw.devops_technologies)
    company.programming_languages = _merge_unique(company.programming_languages, raw.programming_languages)
    company.frameworks = _merge_unique(company.frameworks, raw.frameworks)
    company.tech_stack_confidence = raw.tech_stack_confidence or company.tech_stack_confidence

    if raw.remote_policy:
        company.remote_policy = str(raw.remote_policy)
    company.remote_policy_text = _prefer(company.remote_policy_text, raw.remote_policy_text, confidence)
    company.remote_countries = _merge_unique(company.remote_countries, raw.remote_countries)
    company.remote_regions = _merge_unique(company.remote_regions, raw.remote_regions)
    company.timezone_requirements = _prefer(company.timezone_requirements, raw.timezone_requirements, confidence)
    company.office_required = _prefer(company.office_required, raw.office_required, confidence)
    company.remote_confidence = raw.remote_confidence or company.remote_confidence
    company.remote_evidence_url = _prefer(company.remote_evidence_url, raw.remote_evidence_url, confidence)

    company.public_contact_email = _prefer(company.public_contact_email, raw.public_contact_email, confidence)
    company.careers_email = _prefer(company.careers_email, raw.careers_email, confidence)
    company.founder_linkedin_urls = _merge_unique(company.founder_linkedin_urls, raw.founder_linkedin_urls)
    if raw.product_launch_date:
        company.product_launch_recency = days_between(raw.product_launch_date)
    if raw.recent_news_count:
        company.recent_news_count = raw.recent_news_count

    company.last_seen_at = utcnow()

    _upsert_source(session, company, raw)
    _store_source_record(session, raw, matched=True, company=company)
    _observe(session, company, "website_url", company.website_url, raw)
    _observe(session, company, "remote_policy", company.remote_policy, raw)

    for round_data in raw.funding_rounds:
        exists = any(
            existing.announced_date == round_data.announced_date
            and existing.round_type == (round_data.round_type or None)
            for existing in company.funding_rounds
        )
        if exists:
            continue
        session.add(
            FundingRound(
                company_id=company.id,
                round_type=str(normalize_funding_stage(round_data.round_type)) if round_data.round_type else None,
                amount=round_data.amount,
                currency=round_data.currency,
                amount_usd=round_data.amount_usd or to_usd(round_data.amount, round_data.currency),
                announced_date=round_data.announced_date,
                investors=[inv.name if isinstance(inv, RawInvestor) else str(inv) for inv in round_data.investors],
                lead_investors=round_data.lead_investors,
                source=round_data.source or raw.source_name,
                source_url=round_data.source_url or raw.source_url,
            )
        )

    for investor in [*raw.investors, *[inv for rnd in raw.funding_rounds for inv in rnd.investors]]:
        record = _upsert_investor(session, investor)
        existing_link = session.scalar(
            select(CompanyInvestor).where(
                CompanyInvestor.company_id == company.id,
                CompanyInvestor.investor_id == record.id,
            )
        )
        if existing_link is None:
            is_lead = investor.is_lead if isinstance(investor, RawInvestor) else False
            session.add(CompanyInvestor(company_id=company.id, investor_id=record.id, is_lead=is_lead))

    for job in raw.jobs:
        _upsert_job(session, company, job, raw.source_name)

    session.flush()
    session.refresh(company)
    refresh_company_metrics(company, session)
    return company, "created" if created else "updated"


def _upsert_job(session: Session, company: Company, job: RawJob, source_name: str) -> None:
    existing = None
    if job.job_url:
        existing = session.scalar(select(Job).where(Job.company_id == company.id, Job.job_url == job.job_url))
    if existing is None and job.title:
        existing = session.scalar(select(Job).where(Job.company_id == company.id, Job.title == job.title, Job.active.is_(True)))
    category = job.role_category or classify_engineering_role(job.title, job.description)
    if existing:
        existing.last_seen_at = utcnow()
        existing.active = True
        existing.location = job.location or existing.location
        existing.remote_type = job.remote_type or existing.remote_type
        return
    session.add(
        Job(
            company_id=company.id,
            title=job.title,
            department=job.department,
            role_category=str(category) if category else None,
            seniority=job.seniority,
            employment_type=job.employment_type,
            location=job.location,
            remote_type=job.remote_type,
            remote_regions=job.remote_regions,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            salary_currency=job.salary_currency,
            job_url=job.job_url,
            source=job.source or source_name,
            posted_date=job.posted_date,
            description=job.description,
            external_id=job.external_id,
            active=True,
        )
    )


def _upsert_source(session: Session, company: Company, raw: RawCompany) -> None:
    row = session.scalar(
        select(CompanySource).where(
            CompanySource.company_id == company.id,
            CompanySource.source_name == raw.source_name,
            CompanySource.external_id == (raw.external_id or raw.name),
        )
    )
    payload_hash = _hash_payload(raw.raw_payload or raw.model_dump(mode="json"))
    if row is None:
        session.add(
            CompanySource(
                company_id=company.id,
                source_name=raw.source_name,
                source_url=raw.source_url,
                external_id=raw.external_id or raw.name,
                last_scraped_at=utcnow(),
                raw_data_hash=payload_hash,
                confidence=raw.confidence,
            )
        )
        return
    row.last_seen_at = utcnow()
    row.last_scraped_at = utcnow()
    row.source_url = raw.source_url or row.source_url
    row.raw_data_hash = payload_hash
    row.confidence = raw.confidence


def _store_source_record(session: Session, raw: RawCompany, *, matched: bool, company: Company | None) -> None:
    session.add(
        SourceRecord(
            company_id=company.id if company else None,
            source_name=raw.source_name,
            source_url=raw.source_url,
            external_id=raw.external_id,
            raw_payload=raw.raw_payload or {},
            normalized_payload=raw.model_dump(mode="json"),
            matched=matched,
        )
    )


def _observe(session: Session, company: Company, field_name: str, value, raw: RawCompany) -> None:
    if value in (None, "", [], {}):
        return
    session.add(
        FieldObservation(
            company_id=company.id,
            field_name=field_name,
            value=value if isinstance(value, (dict, list)) else str(value),
            source_name=raw.source_name,
            source_url=raw.source_url,
            confidence=raw.confidence,
        )
    )
