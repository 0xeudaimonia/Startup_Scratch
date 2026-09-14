from workers.remote_detection.detect import classify_remote_policy
from models.enums import RemotePolicy


def test_global_remote_from_careers_page() -> None:
    result = classify_remote_policy(
        careers_text="We are a fully remote company. Work from anywhere, worldwide.",
        evidence_url="https://example.com/careers",
    )
    assert result.policy == RemotePolicy.GLOBAL_REMOTE
    assert result.confidence >= 0.7


def test_single_remote_job_is_not_global() -> None:
    result = classify_remote_policy(job_remote_types=["remote us"])
    assert result.policy == RemotePolicy.UNKNOWN
    assert result.confidence <= 0.3


def test_multiple_worldwide_jobs_can_support_global() -> None:
    result = classify_remote_policy(
        job_remote_types=["global remote", "worldwide", "anywhere", "global remote"]
    )
    assert result.policy == RemotePolicy.GLOBAL_REMOTE


def test_onsite_language() -> None:
    result = classify_remote_policy(about_text="This is an on-site role. Must be in office five days a week.")
    assert result.policy == RemotePolicy.ONSITE
