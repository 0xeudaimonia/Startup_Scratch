from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.query import SORT_MAP, apply_company_filters, load_company, serialize_card, serialize_detail
from api.schemas import CompanyCard, CompanyDetail, FundingRoundOut, InvestorOut, JobOut, PaginatedCompanies
from database.models import Company, CompanyInvestor
from database.session import get_db

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=PaginatedCompanies)
async def list_companies(
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
    sort: str = Query("newest_discovered"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedCompanies:
    stmt = select(Company).options(
        selectinload(Company.company_investors).selectinload(CompanyInvestor.investor)
    )
    stmt = apply_company_filters(
        stmt,
        search=search,
        discovered_after=discovered_after,
        funded_after=funded_after,
        funded_before=funded_before,
        founded_after=founded_after,
        founded_before=founded_before,
        funding_stage=funding_stage,
        minimum_funding=minimum_funding,
        maximum_funding=maximum_funding,
        country=country,
        continent=continent,
        industry=industry,
        remote_policy=remote_policy,
        is_hiring=is_hiring,
        hiring_engineers=hiring_engineers,
        employee_max=employee_max,
        employee_range=employee_range,
        technology=technology,
        investor=investor,
        minimum_opportunity_score=minimum_opportunity_score,
        has_remote_engineering_jobs=has_remote_engineering_jobs,
    )
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = await db.scalar(count_stmt) or 0
    order = SORT_MAP.get(sort, Company.first_discovered_at.desc())
    rows = (
        await db.scalars(stmt.order_by(order).offset((page - 1) * page_size).limit(page_size))
    ).unique().all()
    return PaginatedCompanies(
        items=[CompanyCard.model_validate(serialize_card(row)) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{company_id}", response_model=CompanyDetail)
async def get_company(company_id: str, db: AsyncSession = Depends(get_db)) -> CompanyDetail:
    company = await load_company(db, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyDetail.model_validate(serialize_detail(company))


@router.get("/{company_id}/jobs", response_model=list[JobOut])
async def get_company_jobs(company_id: str, db: AsyncSession = Depends(get_db)) -> list[JobOut]:
    company = await load_company(db, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return [JobOut.model_validate(job) for job in company.jobs]


@router.get("/{company_id}/funding", response_model=list[FundingRoundOut])
async def get_company_funding(company_id: str, db: AsyncSession = Depends(get_db)) -> list[FundingRoundOut]:
    company = await load_company(db, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return [FundingRoundOut.model_validate(row) for row in company.funding_rounds]


@router.get("/{company_id}/investors", response_model=list[InvestorOut])
async def get_company_investors(company_id: str, db: AsyncSession = Depends(get_db)) -> list[InvestorOut]:
    company = await load_company(db, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return [
        InvestorOut(
            id=link.investor.id,
            investor_name=link.investor.investor_name,
            investor_type=link.investor.investor_type,
            investor_url=link.investor.investor_url,
            investor_website=link.investor.investor_website,
            investor_country=link.investor.investor_country,
            notable=link.investor.notable,
            is_lead=link.is_lead,
        )
        for link in company.company_investors
        if link.investor
    ]


@router.get("/{company_id}/sources")
async def get_company_sources(company_id: str, db: AsyncSession = Depends(get_db)):
    company = await load_company(db, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company.company_sources
