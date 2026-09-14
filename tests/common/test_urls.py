from common.urls import normalize_company_name, normalize_domain, normalize_url


def test_normalize_domain_strips_scheme_www_and_path() -> None:
    assert normalize_domain("https://www.example.com/") == "example.com"
    assert normalize_domain("http://example.com") == "example.com"
    assert normalize_domain("https://example.com/about") == "example.com"
    assert normalize_domain("https://jobs.example.co.uk/careers") == "example.co.uk"


def test_normalize_url_adds_https_and_trims_slash() -> None:
    assert normalize_url("example.com") == "https://example.com"
    assert normalize_url("https://Example.com/about/") == "https://example.com/about"


def test_normalize_company_name_drops_legal_suffixes() -> None:
    assert normalize_company_name("Northwind Labs, Inc.") == "northwind labs"
    assert normalize_company_name("Atlasflow GmbH") == "atlasflow"
