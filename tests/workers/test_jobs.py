from workers.job_detection.extract import classify_engineering_role, detect_technologies
from models.enums import EngineeringCategory


def test_classify_engineering_roles() -> None:
    assert classify_engineering_role("Senior Backend Engineer") == EngineeringCategory.BACKEND
    assert classify_engineering_role("Staff Frontend Engineer") == EngineeringCategory.FRONTEND
    assert classify_engineering_role("ML Engineer, LLM platform") == EngineeringCategory.MACHINE_LEARNING
    assert classify_engineering_role("Account Executive") is None


def test_detect_technologies_requires_evidence() -> None:
    found = detect_technologies("We use React, Next.js and PostgreSQL on AWS.")
    assert "React" in found["frontend_technologies"]
    assert "PostgreSQL" in found["databases"]
    assert "AWS" in found["cloud_providers"]
    assert "Rails" not in found.get("backend_technologies", [])
