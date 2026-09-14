import asyncio

from sources.startup_directories.fixture import FixtureSource
from sources.news.techcrunch import extract_funding_from_text
from sources.base import SourceDisabledError
from sources.funding.dealroom import DealroomSource


def test_fixture_source_returns_normalized_company() -> None:
    records = asyncio.run(FixtureSource().discover())
    assert len(records) == 1
    company = records[0]
    assert company.website_url
    assert company.remote_policy
    assert company.jobs
    assert company.funding_rounds


def test_news_funding_extraction() -> None:
    extracted = extract_funding_from_text("Northwind Labs raises $4.2 million seed round led by Sequoia")
    assert extracted["name"] == "Northwind Labs"
    assert extracted["amount"] == 4_200_000
    assert extracted["round_type"] == "seed"


def test_dealroom_is_disabled_without_key() -> None:
    source = DealroomSource()
    assert not source.is_enabled()
    try:
        asyncio.run(source.discover())
        raise AssertionError("expected SourceDisabledError")
    except SourceDisabledError:
        pass
