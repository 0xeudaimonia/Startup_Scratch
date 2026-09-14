from __future__ import annotations

import re

_AMOUNT_RE = re.compile(
    r"(?P<currency>[$€£]|usd|eur|gbp)?\s*(?P<value>\d+(?:[.,]\d+)?)\s*(?P<suffix>billion|bn|million|mn|m|thousand|k|b)?",
    re.I,
)

_CURRENCY_SYMBOLS = {"$": "USD", "€": "EUR", "£": "GBP"}

# Static mid-market approximations used only when a live FX feed is unavailable.
USD_RATES = {
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.27,
    "CAD": 0.73,
    "AUD": 0.66,
    "SGD": 0.74,
    "SEK": 0.095,
    "CHF": 1.12,
    "INR": 0.012,
    "ILS": 0.27,
}


def normalize_currency(value: str | None) -> str | None:
    if not value:
        return None
    raw = value.strip().upper()
    if raw in {"$", "USD", "US$", "USDOLLARS"}:
        return "USD"
    if raw in {"€", "EUR", "EURO", "EUROS"}:
        return "EUR"
    if raw in {"£", "GBP", "POUND", "POUNDS"}:
        return "GBP"
    return raw[:3]


def parse_funding_amount(text: str | None) -> tuple[float | None, str | None]:
    if not text:
        return None, None
    match = _AMOUNT_RE.search(text.replace(",", ""))
    if not match:
        return None, None
    number = float(match.group("value").replace(",", "."))
    suffix = (match.group("suffix") or "").lower()
    multiplier = {
        "k": 1_000,
        "thousand": 1_000,
        "m": 1_000_000,
        "mn": 1_000_000,
        "million": 1_000_000,
        "b": 1_000_000_000,
        "bn": 1_000_000_000,
        "billion": 1_000_000_000,
    }.get(suffix, 1)
    amount = number * multiplier
    raw_currency = match.group("currency")
    currency = _CURRENCY_SYMBOLS.get(raw_currency or "", None)
    if raw_currency and raw_currency.lower() in {"usd", "eur", "gbp"}:
        currency = raw_currency.upper()
    return amount, currency or "USD"


def to_usd(amount: float | None, currency: str | None) -> float | None:
    if amount is None:
        return None
    code = normalize_currency(currency) or "USD"
    rate = USD_RATES.get(code)
    if rate is None:
        return None
    return round(amount * rate, 2)


def format_money(amount: float | None, currency: str | None = "USD") -> str | None:
    if amount is None:
        return None
    currency = normalize_currency(currency) or "USD"
    if amount >= 1_000_000_000:
        return f"{currency} {amount / 1_000_000_000:.1f}B"
    if amount >= 1_000_000:
        return f"{currency} {amount / 1_000_000:.1f}M"
    if amount >= 1_000:
        return f"{currency} {amount / 1_000:.0f}K"
    return f"{currency} {amount:.0f}"
