from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InvestorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    investor_name: str
    investor_type: str | None = None
    investor_url: str | None = None
    investor_website: str | None = None
    investor_country: str | None = None
    notable: bool = False
    is_lead: bool | None = None


class FundingRoundOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    round_type: str | None = None
    amount: float | None = None
    currency: str | None = None
    amount_usd: float | None = None
    announced_date: date | None = None
    investors: list[str] = []
    lead_investors: list[str] = []
    source: str | None = None
    source_url: str | None = None


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    title: str
    department: str | None = None
    role_category: str | None = None
    seniority: str | None = None
    employment_type: str | None = None
    location: str | None = None
    remote_type: str | None = None
    remote_regions: list[str] = []
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    job_url: str | None = None
    source: str | None = None
    posted_date: date | None = None
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    active: bool = True
    company_name: str | None = None
    company_slug: str | None = None


class CompanySourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_name: str
    source_url: str | None = None
    external_id: str | None = None
    first_seen_at: datetime
    last_seen_at: datetime
    last_scraped_at: datetime | None = None
    confidence: float | None = None


class CompanyCard(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    logo_url: str | None = None
    website_url: str | None = None
    normalized_domain: str | None = None
    careers_url: str | None = None
    jobs_url: str | None = None
    short_description: str | None = None
    headquarters_country: str | None = None
    headquarters_city: str | None = None
    founded_date: date | None = None
    employee_range: str | None = None
    funding_stage: str | None = None
    latest_funding_amount: float | None = None
    latest_funding_usd: float | None = None
    latest_funding_currency: str | None = None
    latest_funding_date: date | None = None
    investors: list[str] = []
    remote_policy: str | None = None
    engineering_job_count: int = 0
    open_job_count: int = 0
    opportunity_score: int = 0
    growth_score: int = 0
    is_hiring: bool = False
    hiring_engineers: bool = False
    first_discovered_at: datetime | None = None
    first_source: str | None = None
    primary_industry: str | None = None


class CompanyDetail(CompanyCard):
    legal_name: str | None = None
    aliases: list[str] = []
    description: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    twitter_url: str | None = None
    crunchbase_url: str | None = None
    product_hunt_url: str | None = None
    wellfound_url: str | None = None
    yc_url: str | None = None
    source_urls: list[str] = []
    headquarters_region: str | None = None
    headquarters_continent: str | None = None
    founded_year: int | None = None
    company_age_days: int | None = None
    total_funding_usd: float | None = None
    number_of_funding_rounds: int = 0
    investor_count: int = 0
    notable_investor_count: int = 0
    employee_count_min: int | None = None
    employee_count_max: int | None = None
    estimated_employee_count: int | None = None
    founders: list[str] = []
    industries: list[str] = []
    categories: list[str] = []
    keywords: list[str] = []
    business_model: list[str] = []
    frontend_technologies: list[str] = []
    backend_technologies: list[str] = []
    databases: list[str] = []
    cloud_providers: list[str] = []
    ai_technologies: list[str] = []
    devops_technologies: list[str] = []
    programming_languages: list[str] = []
    frameworks: list[str] = []
    tech_stack_confidence: float | None = None
    remote_policy_text: str | None = None
    remote_regions: list[str] = []
    remote_countries: list[str] = []
    remote_confidence: float | None = None
    remote_evidence_url: str | None = None
    office_required: bool | None = None
    hiring_status: str | None = None
    careers_page_available: bool = False
    jobs_added_last_7_days: int = 0
    jobs_added_last_30_days: int = 0
    hiring_velocity: float = 0
    funding_recency_days: int | None = None
    founded_recency_days: int | None = None
    recent_news_count: int = 0
    opportunity_score_breakdown: dict[str, Any] = {}
    discovery_sources: list[str] = []
    last_updated_at: datetime | None = None
    last_seen_at: datetime | None = None
    funding_rounds: list[FundingRoundOut] = []
    jobs: list[JobOut] = []
    investor_records: list[InvestorOut] = []
    sources: list[CompanySourceOut] = []


class PaginatedCompanies(BaseModel):
    items: list[CompanyCard]
    total: int
    page: int
    page_size: int


class PaginatedJobs(BaseModel):
    items: list[JobOut]
    total: int
    page: int
    page_size: int


class StatsOut(BaseModel):
    companies_discovered_today: int
    companies_discovered_this_week: int
    companies_funded_this_week: int
    recently_founded: int
    global_remote: int
    hiring_engineers: int
    engineering_jobs: int
    average_opportunity_score: float
    total_companies: int


class ScrapeRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source: str
    started_at: datetime
    completed_at: datetime | None = None
    status: str
    records_found: int
    records_created: int
    records_updated: int
    duplicate_records: int
    errors: list[str] = []
    duration_seconds: float | None = None


class SourceOut(BaseModel):
    name: str
    category: str
    enabled: bool
    description: str
    requires: str | None = None
    last_run: ScrapeRunOut | None = None


class SavedViewIn(BaseModel):
    name: str
    description: str | None = None
    filters: dict[str, Any] = Field(default_factory=dict)


class SavedViewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    filters: dict[str, Any]
    created_at: datetime


class ScrapeRequest(BaseModel):
    source: str = "fixture"
