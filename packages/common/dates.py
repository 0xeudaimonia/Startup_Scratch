from __future__ import annotations

from datetime import UTC, date, datetime, timedelta


def utcnow() -> datetime:
    return datetime.now(UTC)


def as_date(value: date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    return value


def days_between(start: date | datetime | None, end: date | datetime | None = None) -> int | None:
    start_date = as_date(start)
    if start_date is None:
        return None
    end_date = as_date(end) or utcnow().date()
    return (end_date - start_date).days


def days_ago(num: int) -> date:
    return utcnow().date() - timedelta(days=num)


def start_of_year(year: int | None = None) -> date:
    return date(year or utcnow().year, 1, 1)
