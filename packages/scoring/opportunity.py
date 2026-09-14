from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from common.dates import days_between, utcnow
from models.enums import FundingStage, RemotePolicy

MAX_RAW_SCORE = 115


@dataclass
class ScoringInput:
    latest_funding_date: date | None = None
    funding_stage: str | None = None
    estimated_employee_count: int | None = None
    employee_count_max: int | None = None
    founded_date: date | None = None
    hiring_engineers: bool = False
    engineering_job_count: int = 0
    remote_policy: str = RemotePolicy.UNKNOWN
    notable_investor_count: int = 0
    product_launch_recency_days: int | None = None
    today: date = field(default_factory=lambda: utcnow().date())


def calculate_opportunity_score(data: ScoringInput) -> tuple[int, dict[str, int]]:
    """Score remote engineering opportunity from 0-100 with a transparent breakdown."""
    breakdown: dict[str, int] = {}
    funding_days = days_between(data.latest_funding_date, data.today)
    if funding_days is not None and funding_days <= 30:
        breakdown["recent_funding_30_days"] = 20
    elif funding_days is not None and funding_days <= 90:
        breakdown["recent_funding_90_days"] = 10

    stage = (data.funding_stage or "").lower()
    if stage in {FundingStage.SEED, FundingStage.SERIES_A, "seed", "series_a"}:
        breakdown["seed_or_series_a"] = 15

    headcount = data.estimated_employee_count or data.employee_count_max
    if headcount is not None and headcount < 200:
        breakdown["company_below_200_employees"] = 10

    founded_days = days_between(data.founded_date, data.today)
    if founded_days is not None and founded_days <= 365 * 3:
        breakdown["founded_within_3_years"] = 10

    if data.hiring_engineers:
        breakdown["actively_hiring_engineers"] = 20

    policy = (data.remote_policy or "").upper()
    if policy == RemotePolicy.GLOBAL_REMOTE:
        breakdown["global_remote"] = 20
    elif policy == RemotePolicy.REMOTE_FIRST:
        breakdown["remote_first"] = 15

    if data.engineering_job_count >= 2:
        breakdown["multiple_engineering_jobs"] = 10

    if data.notable_investor_count > 0:
        breakdown["recognized_vc_investor"] = 5

    if data.product_launch_recency_days is not None and data.product_launch_recency_days <= 90:
        breakdown["recent_product_launch"] = 5

    raw = sum(breakdown.values())
    normalized = min(100, round(raw / MAX_RAW_SCORE * 100))
    breakdown["raw_score"] = raw
    breakdown["normalized_score"] = normalized
    return normalized, breakdown


def calculate_growth_score(
    *,
    funding_recency_days: int | None,
    founded_recency_days: int | None,
    hiring_velocity: float,
    engineering_job_count: int,
    notable_investor_count: int,
    recent_news_count: int,
    employee_growth_signal: float | None = None,
) -> int:
    score = 0
    if funding_recency_days is not None:
        if funding_recency_days <= 30:
            score += 25
        elif funding_recency_days <= 90:
            score += 15
        elif funding_recency_days <= 365:
            score += 8
    if founded_recency_days is not None:
        if founded_recency_days <= 365:
            score += 20
        elif founded_recency_days <= 365 * 3:
            score += 10
    score += min(20, int(hiring_velocity * 4) + min(10, engineering_job_count * 2))
    if notable_investor_count:
        score += 10
    score += min(10, recent_news_count * 3)
    if employee_growth_signal:
        score += min(15, int(employee_growth_signal * 15))
    return min(100, score)
