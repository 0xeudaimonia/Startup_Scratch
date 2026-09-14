from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (
        Index("ix_companies_normalized_domain", "normalized_domain"),
        Index("ix_companies_normalized_name", "normalized_name"),
        Index("ix_companies_first_discovered_at", "first_discovered_at"),
        Index("ix_companies_latest_funding_date", "latest_funding_date"),
        Index("ix_companies_founded_date", "founded_date"),
        Index("ix_companies_opportunity_score", "opportunity_score"),
        Index("ix_companies_remote_policy", "remote_policy"),
        Index("ix_companies_funding_stage", "funding_stage"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str | None] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(255))
    aliases: Mapped[list[str]] = mapped_column(JSONB, default=list)
    company_type: Mapped[str] = mapped_column(String(50), default="startup")
    description: Mapped[str | None] = mapped_column(Text)
    short_description: Mapped[str | None] = mapped_column(Text)
    logo_url: Mapped[str | None] = mapped_column(String(500))

    website_url: Mapped[str | None] = mapped_column(String(500))
    normalized_domain: Mapped[str | None] = mapped_column(String(255))
    careers_url: Mapped[str | None] = mapped_column(String(500))
    jobs_url: Mapped[str | None] = mapped_column(String(500))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    github_url: Mapped[str | None] = mapped_column(String(500))
    twitter_url: Mapped[str | None] = mapped_column(String(500))
    crunchbase_url: Mapped[str | None] = mapped_column(String(500))
    product_hunt_url: Mapped[str | None] = mapped_column(String(500))
    wellfound_url: Mapped[str | None] = mapped_column(String(500))
    yc_url: Mapped[str | None] = mapped_column(String(500))
    source_urls: Mapped[list[str]] = mapped_column(JSONB, default=list)

    headquarters_country: Mapped[str | None] = mapped_column(String(100))
    headquarters_city: Mapped[str | None] = mapped_column(String(100))
    headquarters_region: Mapped[str | None] = mapped_column(String(100))
    headquarters_continent: Mapped[str | None] = mapped_column(String(50))
    remote_locations: Mapped[list[str]] = mapped_column(JSONB, default=list)
    operating_countries: Mapped[list[str]] = mapped_column(JSONB, default=list)

    founded_date: Mapped[date | None] = mapped_column(Date)
    founded_year: Mapped[int | None] = mapped_column(Integer)
    founded_month: Mapped[int | None] = mapped_column(Integer)
    company_age_days: Mapped[int | None] = mapped_column(Integer)

    total_funding_amount: Mapped[float | None] = mapped_column(Float)
    total_funding_currency: Mapped[str | None] = mapped_column(String(10))
    total_funding_usd: Mapped[float | None] = mapped_column(Float)
    latest_funding_round: Mapped[str | None] = mapped_column(String(50))
    latest_funding_amount: Mapped[float | None] = mapped_column(Float)
    latest_funding_currency: Mapped[str | None] = mapped_column(String(10))
    latest_funding_usd: Mapped[float | None] = mapped_column(Float)
    latest_funding_date: Mapped[date | None] = mapped_column(Date)
    number_of_funding_rounds: Mapped[int] = mapped_column(Integer, default=0)
    funding_stage: Mapped[str] = mapped_column(String(50), default="unknown")

    investor_count: Mapped[int] = mapped_column(Integer, default=0)
    notable_investor_count: Mapped[int] = mapped_column(Integer, default=0)

    employee_count_min: Mapped[int | None] = mapped_column(Integer)
    employee_count_max: Mapped[int | None] = mapped_column(Integer)
    employee_range: Mapped[str | None] = mapped_column(String(30))
    estimated_employee_count: Mapped[int | None] = mapped_column(Integer)
    founders: Mapped[list[str]] = mapped_column(JSONB, default=list)
    founder_count: Mapped[int] = mapped_column(Integer, default=0)
    leadership_team: Mapped[list[str]] = mapped_column(JSONB, default=list)
    engineering_team_size: Mapped[int | None] = mapped_column(Integer)

    primary_industry: Mapped[str | None] = mapped_column(String(100))
    industries: Mapped[list[str]] = mapped_column(JSONB, default=list)
    categories: Mapped[list[str]] = mapped_column(JSONB, default=list)
    keywords: Mapped[list[str]] = mapped_column(JSONB, default=list)
    business_model: Mapped[list[str]] = mapped_column(JSONB, default=list)

    frontend_technologies: Mapped[list[str]] = mapped_column(JSONB, default=list)
    backend_technologies: Mapped[list[str]] = mapped_column(JSONB, default=list)
    databases: Mapped[list[str]] = mapped_column(JSONB, default=list)
    cloud_providers: Mapped[list[str]] = mapped_column(JSONB, default=list)
    ai_technologies: Mapped[list[str]] = mapped_column(JSONB, default=list)
    devops_technologies: Mapped[list[str]] = mapped_column(JSONB, default=list)
    programming_languages: Mapped[list[str]] = mapped_column(JSONB, default=list)
    frameworks: Mapped[list[str]] = mapped_column(JSONB, default=list)
    tech_stack_confidence: Mapped[float | None] = mapped_column(Float)

    remote_policy: Mapped[str] = mapped_column(String(50), default="UNKNOWN")
    remote_policy_text: Mapped[str | None] = mapped_column(Text)
    remote_countries: Mapped[list[str]] = mapped_column(JSONB, default=list)
    remote_regions: Mapped[list[str]] = mapped_column(JSONB, default=list)
    timezone_requirements: Mapped[str | None] = mapped_column(String(255))
    office_required: Mapped[bool | None] = mapped_column(Boolean)
    remote_confidence: Mapped[float | None] = mapped_column(Float)
    remote_evidence_url: Mapped[str | None] = mapped_column(String(500))

    open_job_count: Mapped[int] = mapped_column(Integer, default=0)
    engineering_job_count: Mapped[int] = mapped_column(Integer, default=0)
    remote_job_count: Mapped[int] = mapped_column(Integer, default=0)
    global_remote_job_count: Mapped[int] = mapped_column(Integer, default=0)
    is_hiring: Mapped[bool] = mapped_column(Boolean, default=False)
    hiring_engineers: Mapped[bool] = mapped_column(Boolean, default=False)
    jobs_added_last_7_days: Mapped[int] = mapped_column(Integer, default=0)
    jobs_added_last_30_days: Mapped[int] = mapped_column(Integer, default=0)
    hiring_velocity: Mapped[float] = mapped_column(Float, default=0)
    hiring_status: Mapped[str] = mapped_column(String(50), default="unknown")
    careers_page_available: Mapped[bool] = mapped_column(Boolean, default=False)

    public_contact_email: Mapped[str | None] = mapped_column(String(255))
    careers_email: Mapped[str | None] = mapped_column(String(255))
    founder_linkedin_urls: Mapped[list[str]] = mapped_column(JSONB, default=list)
    hiring_manager_names: Mapped[list[str]] = mapped_column(JSONB, default=list)
    recruiter_names: Mapped[list[str]] = mapped_column(JSONB, default=list)

    funding_recency_days: Mapped[int | None] = mapped_column(Integer)
    founded_recency_days: Mapped[int | None] = mapped_column(Integer)
    employee_growth_signal: Mapped[float | None] = mapped_column(Float)
    product_launch_recency: Mapped[int | None] = mapped_column(Integer)
    recent_news_count: Mapped[int] = mapped_column(Integer, default=0)
    github_activity: Mapped[float | None] = mapped_column(Float)
    new_job_count: Mapped[int] = mapped_column(Integer, default=0)
    website_activity_signal: Mapped[float | None] = mapped_column(Float)
    growth_score: Mapped[int] = mapped_column(Integer, default=0)
    opportunity_score: Mapped[int] = mapped_column(Integer, default=0)
    opportunity_score_breakdown: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    first_discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    first_source: Mapped[str | None] = mapped_column(String(100))
    discovery_sources: Mapped[list[str]] = mapped_column(JSONB, default=list)
    deduplication_confidence: Mapped[float | None] = mapped_column(Float)

    funding_rounds: Mapped[list[FundingRound]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
    jobs: Mapped[list[Job]] = relationship(back_populates="company", cascade="all, delete-orphan")
    company_investors: Mapped[list[CompanyInvestor]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
    company_sources: Mapped[list[CompanySource]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
    source_records: Mapped[list[SourceRecord]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
    field_observations: Mapped[list[FieldObservation]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )


class FundingRound(Base):
    __tablename__ = "funding_rounds"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    round_type: Mapped[str | None] = mapped_column(String(50))
    amount: Mapped[float | None] = mapped_column(Float)
    currency: Mapped[str | None] = mapped_column(String(10))
    amount_usd: Mapped[float | None] = mapped_column(Float)
    announced_date: Mapped[date | None] = mapped_column(Date)
    investors: Mapped[list[str]] = mapped_column(JSONB, default=list)
    lead_investors: Mapped[list[str]] = mapped_column(JSONB, default=list)
    source: Mapped[str | None] = mapped_column(String(100))
    source_url: Mapped[str | None] = mapped_column(String(500))

    company: Mapped[Company] = relationship(back_populates="funding_rounds")


class Investor(Base):
    __tablename__ = "investors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investor_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    normalized_name: Mapped[str | None] = mapped_column(String(255), index=True)
    investor_type: Mapped[str | None] = mapped_column(String(50))
    investor_url: Mapped[str | None] = mapped_column(String(500))
    investor_website: Mapped[str | None] = mapped_column(String(500))
    investor_country: Mapped[str | None] = mapped_column(String(100))
    notable: Mapped[bool] = mapped_column(Boolean, default=False)

    company_investors: Mapped[list[CompanyInvestor]] = relationship(back_populates="investor")


class CompanyInvestor(Base):
    __tablename__ = "company_investors"
    __table_args__ = (UniqueConstraint("company_id", "investor_id", name="uq_company_investor"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE")
    )
    investor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("investors.id", ondelete="CASCADE")
    )
    is_lead: Mapped[bool] = mapped_column(Boolean, default=False)
    round_type: Mapped[str | None] = mapped_column(String(50))

    company: Mapped[Company] = relationship(back_populates="company_investors")
    investor: Mapped[Investor] = relationship(back_populates="company_investors")


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (Index("ix_jobs_company_active", "company_id", "active"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str | None] = mapped_column(String(100))
    role_category: Mapped[str | None] = mapped_column(String(50))
    seniority: Mapped[str | None] = mapped_column(String(50))
    employment_type: Mapped[str | None] = mapped_column(String(50))
    location: Mapped[str | None] = mapped_column(String(255))
    remote_type: Mapped[str | None] = mapped_column(String(50))
    remote_regions: Mapped[list[str]] = mapped_column(JSONB, default=list)
    salary_min: Mapped[float | None] = mapped_column(Float)
    salary_max: Mapped[float | None] = mapped_column(Float)
    salary_currency: Mapped[str | None] = mapped_column(String(10))
    job_url: Mapped[str | None] = mapped_column(String(500))
    source: Mapped[str | None] = mapped_column(String(100))
    posted_date: Mapped[date | None] = mapped_column(Date)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str | None] = mapped_column(Text)
    external_id: Mapped[str | None] = mapped_column(String(255))

    company: Mapped[Company] = relationship(back_populates="jobs")


class CompanySource(Base):
    __tablename__ = "company_sources"
    __table_args__ = (
        UniqueConstraint("company_id", "source_name", "external_id", name="uq_company_source"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500))
    external_id: Mapped[str | None] = mapped_column(String(255))
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    raw_data_hash: Mapped[str | None] = mapped_column(String(64))
    confidence: Mapped[float | None] = mapped_column(Float)

    company: Mapped[Company] = relationship(back_populates="company_sources")


class SourceRecord(Base):
    __tablename__ = "source_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"), index=True
    )
    source_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_url: Mapped[str | None] = mapped_column(String(500))
    external_id: Mapped[str | None] = mapped_column(String(255))
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    normalized_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    matched: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    company: Mapped[Company | None] = relationship(back_populates="source_records")


class FieldObservation(Base):
    __tablename__ = "field_observations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[Any] = mapped_column(JSONB)
    source_name: Mapped[str] = mapped_column(String(100))
    source_url: Mapped[str | None] = mapped_column(String(500))
    confidence: Mapped[float | None] = mapped_column(Float)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    company: Mapped[Company] = relationship(back_populates="field_observations")


class DuplicateCandidate(Base):
    __tablename__ = "duplicate_candidates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE")
    )
    other_company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE")
    )
    incoming_name: Mapped[str | None] = mapped_column(String(255))
    incoming_domain: Mapped[str | None] = mapped_column(String(255))
    match_reason: Mapped[str | None] = mapped_column(String(100))
    confidence: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), default="running")
    records_found: Mapped[int] = mapped_column(Integer, default=0)
    records_created: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_records: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[list[str]] = mapped_column(JSONB, default=list)
    duration_seconds: Mapped[float | None] = mapped_column(Float)


class SavedView(Base):
    __tablename__ = "saved_views"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    filters: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
