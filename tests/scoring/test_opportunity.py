from datetime import date, timedelta

from scoring.opportunity import ScoringInput, calculate_opportunity_score


def test_opportunity_score_rewards_recent_funded_remote_hiring() -> None:
    score, breakdown = calculate_opportunity_score(
        ScoringInput(
            latest_funding_date=date.today() - timedelta(days=10),
            funding_stage="seed",
            estimated_employee_count=18,
            founded_date=date.today() - timedelta(days=200),
            hiring_engineers=True,
            engineering_job_count=3,
            remote_policy="GLOBAL_REMOTE",
            notable_investor_count=1,
            product_launch_recency_days=20,
        )
    )
    assert score > 80
    assert breakdown["recent_funding_30_days"] == 20
    assert breakdown["global_remote"] == 20
    assert breakdown["actively_hiring_engineers"] == 20
    assert "normalized_score" in breakdown


def test_opportunity_score_does_not_double_count_older_funding() -> None:
    score, breakdown = calculate_opportunity_score(
        ScoringInput(latest_funding_date=date.today() - timedelta(days=60), funding_stage="series_b")
    )
    assert "recent_funding_90_days" in breakdown
    assert "recent_funding_30_days" not in breakdown
    assert score < 40
