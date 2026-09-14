from sources.accelerators.ycombinator import _team_size_range, latest_batch
from models.enums import EmployeeRange


def test_latest_batch_from_meta_dict() -> None:
    batch = latest_batch(
        {
            "summer-2025": {"name": "Summer 2025", "api": "https://example.com/s25.json"},
            "fall-2026": {"name": "Fall 2026", "api": "https://example.com/f26.json"},
            "winter-2026": {"name": "Winter 2026", "api": "https://example.com/w26.json"},
            "unspecified": {"name": "Unspecified", "api": "https://example.com/u.json"},
        }
    )
    assert batch is not None
    assert batch["slug"] == "fall-2026"
    assert batch["api"] == "https://example.com/f26.json"


def test_latest_batch_from_legacy_list() -> None:
    batch = latest_batch(["winter-2025", "summer-2026"])
    assert batch is not None
    assert batch["slug"] == "summer-2026"


def test_team_size_accepts_int_and_range() -> None:
    assert _team_size_range(2)[2] == EmployeeRange.RANGE_1_10
    assert _team_size_range("11-50")[2] == EmployeeRange.RANGE_11_50
    assert _team_size_range(120)[2] == EmployeeRange.RANGE_101_200
