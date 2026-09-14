from __future__ import annotations

import re
from urllib.parse import urlparse

import tldextract

_EXTRACTOR = tldextract.TLDExtract(suffix_list_urls=())


def normalize_url(url: str | None) -> str | None:
    if not url:
        return None
    value = url.strip()
    if not value:
        return None
    if not re.match(r"^https?://", value, flags=re.I):
        value = f"https://{value}"
    parsed = urlparse(value)
    if not parsed.netloc:
        return None
    scheme = parsed.scheme.lower() if parsed.scheme else "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    if path in {"", "/"}:
        return f"{scheme}://{netloc}"
    return f"{scheme}://{netloc}{path}"


def normalize_domain(url: str | None) -> str | None:
    """Collapse website variants to a registrable domain like example.com."""
    if not url:
        return None
    value = url.strip()
    if not value:
        return None
    extracted = _EXTRACTOR(value)
    if not extracted.domain or not extracted.suffix:
        host = urlparse(value if "://" in value else f"https://{value}").hostname
        if not host:
            return None
        host = host.lower().removeprefix("www.")
        return host or None
    return f"{extracted.domain}.{extracted.suffix}".lower()


def normalize_company_name(name: str | None) -> str | None:
    if not name:
        return None
    cleaned = name.strip().lower()
    cleaned = re.sub(r"[\"'`]", "", cleaned)
    cleaned = re.sub(
        r"\b(incorporated|inc|llc|ltd|limited|gmbh|ag|corp|corporation|co|company|plc)\b\.?",
        "",
        cleaned,
    )
    cleaned = re.sub(r"[^a-z0-9]+", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip() or None
