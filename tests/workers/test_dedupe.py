from workers.scraping.dedupe import DuplicateMatch, find_duplicate
from common.urls import normalize_company_name, normalize_domain


class _FakeCompany:
    def __init__(self, name: str, domain: str | None = None, country: str | None = None) -> None:
        self.name = name
        self.normalized_name = normalize_company_name(name)
        self.normalized_domain = domain
        self.website_url = f"https://{domain}" if domain else None
        self.linkedin_url = None
        self.headquarters_country = country
        self.id = "1"


class _Query:
    def __init__(self, companies: list[_FakeCompany], attr: str | None = None, value=None) -> None:
        self.companies = companies
        self.attr = attr
        self.value = value

    def where(self, *args, **kwargs):
        return self

    def limit(self, _n):
        return self


class _Session:
    def __init__(self, companies: list[_FakeCompany]) -> None:
        self.companies = companies

    def scalar(self, _stmt):
        return None

    def scalars(self, _stmt):
        class _Result:
            def __init__(self, rows):
                self.rows = rows

            def all(self):
                return self.rows

        return _Result(self.companies)

    def get(self, _cls, _id):
        return None

    def add(self, _obj):
        return None


def test_domain_match_is_high_confidence(monkeypatch) -> None:
    existing = _FakeCompany("Example", "example.com")

    def fake_scalar(_stmt):
        return existing

    session = _Session([existing])
    monkeypatch.setattr(session, "scalar", fake_scalar)
    match = find_duplicate(session, name="Example Inc", website_url="https://www.example.com/about")
    assert match.should_merge
    assert match.reason == "normalized_domain"
    assert match.confidence >= 0.99


def test_low_confidence_fuzzy_does_not_automerge() -> None:
    assert normalize_domain("https://not-related.test") == "not-related.test"
    match = DuplicateMatch(company=_FakeCompany("Other"), confidence=0.8, reason="fuzzy_name", should_merge=False)
    assert not match.should_merge
