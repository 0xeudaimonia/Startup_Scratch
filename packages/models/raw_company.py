from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from models.enums import (
    CompanyType,
    EmployeeRange,
    EngineeringCategory,
    FundingStage,
    RemotePolicy,
)


class RawInvestor(BaseModel):
    name: str
    investor_type: str | None = None
    url: str | None = None
    website: str | None = None
    country: str | None = None
    is_lead: bool = False
    notable: bool | None = None


class RawFundingRound(BaseModel):
    round_type: str | None = None
    amount: float | None = None
    currency: str | None = None
    amount_usd: float | None = None
    announced_date: date | None = None
    investors: list[RawInvestor] = Field(default_factory=list)
    lead_investors: list[str] = Field(default_factory=list)
    source: str | None = None
    source_url: str | None = None


class RawJob(BaseModel):
    external_id: str | None = None
    title: str
    department: str | None = None
    role_category: EngineeringCategory | str | None = None
    seniority: str | None = None
    employment_type: str | None = None
    location: str | None = None
    remote_type: str | None = None
    remote_regions: list[str] = Field(default_factory=list)
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    job_url: str | None = None
    source: str | None = None
    posted_date: date | None = None
    description: str | None = None


class RawCompany(BaseModel):
    """Normalized record produced by a source adapter before persistence."""

    external_id: str | None = None
    source_name: str
    source_url: str | None = None
    confidence: float = 0.7

    name: str
    legal_name: str | None = None
    aliases: list[str] = Field(default_factory=list)
    company_type: CompanyType | str = CompanyType.STARTUP
    description: str | None = None
    short_description: str | None = None

    website_url: str | None = None
    careers_url: str | None = None
    jobs_url: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    twitter_url: str | None = None
    crunchbase_url: str | None = None
    product_hunt_url: str | None = None
    wellfound_url: str | None = None
    yc_url: str | None = None
    logo_url: str | None = None
    source_urls: list[str] = Field(default_factory=list)

    headquarters_country: str | None = None
    headquarters_city: str | None = None
    headquarters_region: str | None = None
    headquarters_continent: str | None = None
    remote_locations: list[str] = Field(default_factory=list)
    operating_countries: list[str] = Field(default_factory=list)

    founded_date: date | None = None
    founded_year: int | None = None
    founded_month: int | None = None

    total_funding_amount: float | None = None
    total_funding_currency: str | None = None
    total_funding_usd: float | None = None
    latest_funding_round: str | None = None
    latest_funding_amount: float | None = None
    latest_funding_currency: str | None = None
    latest_funding_usd: float | None = None
    latest_funding_date: date | None = None
    number_of_funding_rounds: int | None = None
    funding_stage: FundingStage | str | None = None
    funding_rounds: list[RawFundingRound] = Field(default_factory=list)

    investors: list[RawInvestor] = Field(default_factory=list)

    employee_count_min: int | None = None
    employee_count_max: int | None = None
    employee_range: EmployeeRange | str | None = None
    estimated_employee_count: int | None = None
    founders: list[str] = Field(default_factory=list)
    leadership_team: list[str] = Field(default_factory=list)
    engineering_team_size: int | None = None

    primary_industry: str | None = None
    industries: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    business_model: list[str] = Field(default_factory=list)

    frontend_technologies: list[str] = Field(default_factory=list)
    backend_technologies: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    cloud_providers: list[str] = Field(default_factory=list)
    ai_technologies: list[str] = Field(default_factory=list)
    devops_technologies: list[str] = Field(default_factory=list)
    programming_languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    tech_stack_confidence: float | None = None

    remote_policy: RemotePolicy | str | None = None
    remote_policy_text: str | None = None
    remote_countries: list[str] = Field(default_factory=list)
    remote_regions: list[str] = Field(default_factory=list)
    timezone_requirements: str | None = None
    office_required: bool | None = None
    remote_confidence: float | None = None
    remote_evidence_url: str | None = None

    jobs: list[RawJob] = Field(default_factory=list)

    public_contact_email: str | None = None
    careers_email: str | None = None
    founder_linkedin_urls: list[str] = Field(default_factory=list)

    product_launch_date: date | None = None
    recent_news_count: int | None = None

    raw_payload: dict[str, Any] = Field(default_factory=dict)
    discovered_at: datetime | None = None
