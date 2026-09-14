from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Select, Text, and_, cast, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Company, CompanyInvestor, Investor


def apply_company_filters(
    stmt: Select,
    *,
    search: str | None = None,
    discovered_after: datetime | None = None,
    funded_after: date | None = None,
    funded_before: date | None = None,
    founded_after: date | None = None,
    founded_before: date | None = None,
    funding_stage: str | None = None,
    minimum_funding: float | None = None,
    maximum_funding: float | None = None,
    country: str | None = None,
    continent: str | None = None,
    industry: str | None = None,
    remote_policy: str | None = None,
    is_hiring: bool | None = None,
    hiring_engineers: bool | None = None,
    employee_max: int | None = None,
    employee_range: str | None = None,
    technology: str | None = None,
    investor: str | None = None,
    minimum_opportunity_score: int | None = None,
    has_remote_engineering_jobs: bool | None = None,
) -> Select:
    conditions = []
    if search:
        term = f"%{search.strip()}%"
        conditions.append(
            or_(
                Company.name.ilike(term),
                Company.normalized_domain.ilike(term),
                Company.short_description.ilike(term),
                Company.description.ilike(term),
                Company.primary_industry.ilike(term),
                cast(Company.industries, Text).ilike(term),
                cast(Company.keywords, Text).ilike(term),
                cast(Company.programming_languages, Text).ilike(term),
                cast(Company.frameworks, Text).ilike(term),
                cast(Company.founders, Text).ilike(term),
            )
        )
    if discovered_after:
        conditions.append(Company.first_discovered_at >= discovered_after)
    if funded_after:
        conditions.append(Company.latest_funding_date >= funded_after)
    if funded_before:
        conditions.append(Company.latest_funding_date <= funded_before)
    if founded_after:
        conditions.append(Company.founded_date >= founded_after)
    if founded_before:
        conditions.append(Company.founded_date <= founded_before)
    if funding_stage:
        stages = [part.strip() for part in funding_stage.split(",") if part.strip()]
        if stages:
            conditions.append(Company.funding_stage.in_(stages))
    if minimum_funding is not None:
        conditions.append(Company.latest_funding_usd >= minimum_funding)
    if maximum_funding is not None:
        conditions.append(Company.latest_funding_usd <= maximum_funding)
    if country:
        conditions.append(Company.headquarters_country.ilike(country))
    if continent:
        conditions.append(Company.headquarters_continent.ilike(continent))
    if industry:
        conditions.append(cast(Company.industries, Text).ilike(f"%{industry}%"))
    if remote_policy:
        policies = [part.strip() for part in remote_policy.split(",") if part.strip()]
        if policies:
            conditions.append(Company.remote_policy.in_(policies))
    if is_hiring is not None:
        conditions.append(Company.is_hiring.is_(is_hiring))
    if hiring_engineers is not None:
        conditions.append(Company.hiring_engineers.is_(hiring_engineers))
    if employee_max is not None:
        conditions.append(
            or_(Company.employee_count_max <= employee_max, Company.estimated_employee_count <= employee_max)
        )
    if employee_range:
        conditions.append(Company.employee_range == employee_range)
    if technology:
        tech = f"%{technology}%"
        conditions.append(
            or_(
                cast(Company.programming_languages, Text).ilike(tech),
                cast(Company.frontend_technologies, Text).ilike(tech),
                cast(Company.backend_technologies, Text).ilike(tech),
                cast(Company.frameworks, Text).ilike(tech),
                cast(Company.databases, Text).ilike(tech),
                cast(Company.cloud_providers, Text).ilike(tech),
                cast(Company.ai_technologies, Text).ilike(tech),
                cast(Company.devops_technologies, Text).ilike(tech),
            )
        )
    if investor:
        stmt = (
            stmt.join(CompanyInvestor, CompanyInvestor.company_id == Company.id)
            .join(Investor, Investor.id == CompanyInvestor.investor_id)
            .where(Investor.investor_name.ilike(f"%{investor}%"))
        )
    if minimum_opportunity_score is not None:
        conditions.append(Company.opportunity_score >= minimum_opportunity_score)
    if has_remote_engineering_jobs:
        conditions.append(Company.engineering_job_count > 0)
        conditions.append(Company.remote_job_count > 0)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    return stmt


SORT_MAP = {
    "newest_discovered": Company.first_discovered_at.desc(),
    "latest_funding": Company.latest_funding_date.desc().nullslast(),
    "funding_amount": Company.latest_funding_usd.desc().nullslast(),
    "founded_date": Company.founded_date.desc().nullslast(),
    "opportunity_score": Company.opportunity_score.desc(),
    "growth_score": Company.growth_score.desc(),
    "engineering_job_count": Company.engineering_job_count.desc(),
}


def serialize_card(company: Company) -> dict:
    investors = [
        link.investor.investor_name
        for link in company.company_investors
        if link.investor is not None
    ]
    return {
        "id": company.id,
        "slug": company.slug,
        "name": company.name,
        "logo_url": company.logo_url,
        "website_url": company.website_url,
        "normalized_domain": company.normalized_domain,
        "careers_url": company.careers_url,
        "jobs_url": company.jobs_url,
        "short_description": company.short_description,
        "headquarters_country": company.headquarters_country,
        "headquarters_city": company.headquarters_city,
        "founded_date": company.founded_date,
        "employee_range": company.employee_range,
        "funding_stage": company.funding_stage,
        "latest_funding_amount": company.latest_funding_amount,
        "latest_funding_usd": company.latest_funding_usd,
        "latest_funding_currency": company.latest_funding_currency,
        "latest_funding_date": company.latest_funding_date,
        "investors": investors[:4],
        "remote_policy": company.remote_policy,
        "engineering_job_count": company.engineering_job_count,
        "open_job_count": company.open_job_count,
        "opportunity_score": company.opportunity_score,
        "growth_score": company.growth_score,
        "is_hiring": company.is_hiring,
        "hiring_engineers": company.hiring_engineers,
        "first_discovered_at": company.first_discovered_at,
        "first_source": company.first_source,
        "primary_industry": company.primary_industry,
    }


def serialize_detail(company: Company) -> dict:
    card = serialize_card(company)
    card.update(
        {
            "legal_name": company.legal_name,
            "aliases": company.aliases or [],
            "description": company.description,
            "linkedin_url": company.linkedin_url,
            "github_url": company.github_url,
            "twitter_url": company.twitter_url,
            "crunchbase_url": company.crunchbase_url,
            "product_hunt_url": company.product_hunt_url,
            "wellfound_url": company.wellfound_url,
            "yc_url": company.yc_url,
            "source_urls": company.source_urls or [],
            "headquarters_region": company.headquarters_region,
            "headquarters_continent": company.headquarters_continent,
            "founded_year": company.founded_year,
            "company_age_days": company.company_age_days,
            "total_funding_usd": company.total_funding_usd,
            "number_of_funding_rounds": company.number_of_funding_rounds,
            "investor_count": company.investor_count,
            "notable_investor_count": company.notable_investor_count,
            "employee_count_min": company.employee_count_min,
            "employee_count_max": company.employee_count_max,
            "estimated_employee_count": company.estimated_employee_count,
            "founders": company.founders or [],
            "industries": company.industries or [],
            "categories": company.categories or [],
            "keywords": company.keywords or [],
            "business_model": company.business_model or [],
            "frontend_technologies": company.frontend_technologies or [],
            "backend_technologies": company.backend_technologies or [],
            "databases": company.databases or [],
            "cloud_providers": company.cloud_providers or [],
            "ai_technologies": company.ai_technologies or [],
            "devops_technologies": company.devops_technologies or [],
            "programming_languages": company.programming_languages or [],
            "frameworks": company.frameworks or [],
            "tech_stack_confidence": company.tech_stack_confidence,
            "remote_policy_text": company.remote_policy_text,
            "remote_regions": company.remote_regions or [],
            "remote_countries": company.remote_countries or [],
            "remote_confidence": company.remote_confidence,
            "remote_evidence_url": company.remote_evidence_url,
            "office_required": company.office_required,
            "hiring_status": company.hiring_status,
            "careers_page_available": company.careers_page_available,
            "jobs_added_last_7_days": company.jobs_added_last_7_days,
            "jobs_added_last_30_days": company.jobs_added_last_30_days,
            "hiring_velocity": company.hiring_velocity,
            "funding_recency_days": company.funding_recency_days,
            "founded_recency_days": company.founded_recency_days,
            "recent_news_count": company.recent_news_count,
            "opportunity_score_breakdown": company.opportunity_score_breakdown or {},
            "discovery_sources": company.discovery_sources or [],
            "last_updated_at": company.last_updated_at,
            "last_seen_at": company.last_seen_at,
            "funding_rounds": company.funding_rounds,
            "jobs": company.jobs,
            "investor_records": [
                {
                    "id": link.investor.id,
                    "investor_name": link.investor.investor_name,
                    "investor_type": link.investor.investor_type,
                    "investor_url": link.investor.investor_url,
                    "investor_website": link.investor.investor_website,
                    "investor_country": link.investor.investor_country,
                    "notable": link.investor.notable,
                    "is_lead": link.is_lead,
                }
                for link in company.company_investors
                if link.investor
            ],
            "sources": company.company_sources,
        }
    )
    return card


async def load_company(db: AsyncSession, company_id: str) -> Company | None:
    stmt = select(Company).options(
        selectinload(Company.funding_rounds),
        selectinload(Company.jobs),
        selectinload(Company.company_investors).selectinload(CompanyInvestor.investor),
        selectinload(Company.company_sources),
    )
    try:
        uid = uuid.UUID(company_id)
        stmt = stmt.where(Company.id == uid)
    except ValueError:
        stmt = stmt.where(Company.slug == company_id)
    return await db.scalar(stmt)
