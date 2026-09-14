from sources.funding.growthlist import (
    PUBLIC_LISTS,
    PublicList,
    companies_from_html_pages,
    parse_growthlist_date,
    parse_public_table,
    _row_to_company,
)
from models.enums import FundingStage


SAMPLE_HTML = """
<html><body>
<table>
  <tr><th>Name</th><th>Website</th><th>Industry</th><th>Country</th>
      <th>Funding Amount (USD)</th><th>Funding Type</th><th>Last Funding Date</th></tr>
  <tr><td>Netris</td><td>netris.io</td><td>SaaS, Cloud Infrastructure</td><td>United States</td>
      <td>$15,000,000</td><td>Series A</td><td>Jun 2026</td></tr>
</table>
</body></html>
"""

PRESEED_HTML = """
<html><body>
<table>
  <tr><th>Name</th><th>Website</th><th>Industry</th><th>Country</th>
      <th>Funding Amount (USD)</th><th>Funding Type</th><th>Last Funding Date</th></tr>
  <tr><td>Stoa</td><td>stoaexchange.com</td><td>FinTech</td><td>United States</td>
      <td>$500,000</td><td></td><td>Jun 2026</td></tr>
</table>
</body></html>
"""

AI_HTML = """
<html><body>
<table>
  <tr><th>Name</th><th>Website</th><th>Industry</th><th>Country</th>
      <th>Funding Amount (USD)</th><th>Funding Type</th><th>Last Funding Date</th></tr>
  <tr><td>Netris</td><td>netris.io</td><td>Cloud Infrastructure</td><td>United States</td>
      <td>$15,000,000</td><td>Series A</td><td>Jun 2026</td></tr>
</table>
</body></html>
"""


def test_parse_public_table() -> None:
    rows = parse_public_table(SAMPLE_HTML)
    assert len(rows) == 1
    company = _row_to_company(rows[0])
    assert company is not None
    assert company.name == "Netris"
    assert company.website_url == "https://netris.io"
    assert company.latest_funding_usd == 15_000_000
    assert company.funding_stage == "series_a"
    assert company.headquarters_country == "United States"


def test_parse_growthlist_month_year() -> None:
    assert parse_growthlist_date("Jun 2026").isoformat() == "2026-06-01"


def test_skip_rows_without_website() -> None:
    assert _row_to_company({"name": "Ghost Co", "website": ""}) is None


def test_stage_list_fills_missing_funding_type() -> None:
    page = PublicList("pre-seed-startups", default_stage=FundingStage.PRE_SEED)
    company = _row_to_company(
        {"name": "Stoa", "website": "stoaexchange.com", "funding type": ""},
        page,
    )
    assert company is not None
    assert company.funding_stage == FundingStage.PRE_SEED
    assert company.source_url == "https://growthlist.co/pre-seed-startups/"


def test_merge_companies_across_lists() -> None:
    pages = [
        (PUBLIC_LISTS[0], SAMPLE_HTML),
        (PublicList("ai-startups", tags=("AI",)), AI_HTML),
        (PublicList("pre-seed-startups", default_stage=FundingStage.PRE_SEED), PRESEED_HTML),
    ]
    companies = {item.name: item for item in companies_from_html_pages(pages)}
    assert set(companies) == {"Netris", "Stoa"}
    netris = companies["Netris"]
    assert "AI" in netris.categories
    assert "SaaS" in netris.industries
    assert netris.source_urls == [
        "https://growthlist.co/funded-startups/",
        "https://growthlist.co/ai-startups/",
    ]


def test_public_lists_cover_requested_paths() -> None:
    paths = {item.path for item in PUBLIC_LISTS}
    assert paths >= {
        "funded-startups",
        "pre-seed-startups",
        "seed-startups",
        "series-a-startups",
        "series-b-startups",
        "ai-startups",
        "list-of-funded-saas-startups",
        "b2b-startups",
        "b2b-saas-startups",
        "fintech-startups",
        "e-commerce-startups",
        "e-commerce-software-startups",
        "united-states-startups",
        "san-francisco-startups",
        "finland-startups",
    }
    assert all("utm_" not in item.url for item in PUBLIC_LISTS)


def test_skips_sentence_industry_and_shifted_columns() -> None:
    page = PublicList("series-b-startups", default_stage=FundingStage.SERIES_B)
    company = _row_to_company(
        {
            "name": "AnBogen Therapeutics",
            "website": "anbogen.com",
            "industry": "I have reviewed Anbogen Therapeutics (clinical-stage biotech focused on cancer therapies) and classified it accordingly.",
            "country": "Taiwan",
            "funding amount (usd)": "Series B",
            "funding type": "Apr 2026",
            "last funding date": "",
        },
        page,
    )
    assert company is not None
    assert company.primary_industry is None or len(company.primary_industry) <= 100
    assert company.headquarters_country == "Taiwan"
    assert company.funding_stage == FundingStage.SERIES_B
    assert company.latest_funding_date.isoformat() == "2026-04-01"
    assert company.latest_funding_usd is None
