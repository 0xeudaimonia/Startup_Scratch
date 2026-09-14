from common.currency import parse_funding_amount, to_usd
from common.funding import normalize_funding_stage
from models.enums import FundingStage


def test_parse_funding_amount_millions() -> None:
    amount, currency = parse_funding_amount("raises $4.2 million")
    assert amount == 4_200_000
    assert currency == "USD"


def test_parse_euro_amount() -> None:
    amount, currency = parse_funding_amount("€12m Series A")
    assert amount == 12_000_000
    assert currency == "EUR"


def test_to_usd_converts_eur() -> None:
    assert to_usd(1_000_000, "EUR") == 1_080_000


def test_normalize_funding_stage() -> None:
    assert normalize_funding_stage("Series A") == FundingStage.SERIES_A
    assert normalize_funding_stage("pre-seed") == FundingStage.PRE_SEED
    assert normalize_funding_stage("seed") == FundingStage.SEED
    assert normalize_funding_stage("bootstrapped") == FundingStage.BOOTSTRAPPED
