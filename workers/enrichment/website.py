from __future__ import annotations

from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from common.http import fetch_text
from common.urls import normalize_url
from models.raw_company import RawCompany
from workers.job_detection.extract import detect_technologies
from workers.remote_detection.detect import classify_remote_policy

CANDIDATE_PATHS = ["/", "/about", "/company", "/careers", "/jobs", "/team"]


def _same_host(base: str, href: str) -> bool:
    return urlparse(href).netloc in {"", urlparse(base).netloc}


def extract_links(html: str, base_url: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "lxml")
    found: dict[str, str] = {}
    for a in soup.select("a[href]"):
        href = normalize_url(urljoin(base_url, a.get("href")))
        if not href:
            continue
        label = f"{a.get_text(' ')} {href}".lower()
        if "linkedin.com" in href:
            found.setdefault("linkedin_url", href)
        elif "github.com" in href:
            found.setdefault("github_url", href)
        elif "twitter.com" in href or "x.com" in href:
            found.setdefault("twitter_url", href)
        elif any(token in label for token in ["career", "jobs", "join us", "we're hiring", "we are hiring"]):
            if _same_host(base_url, href):
                found.setdefault("careers_url", href)
    return found


def extract_description(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    meta = soup.find("meta", attrs={"name": "description"}) or soup.find(
        "meta", attrs={"property": "og:description"}
    )
    if meta and meta.get("content"):
        return meta["content"].strip()
    p = soup.find("p")
    if p:
        text = p.get_text(" ", strip=True)
        return text[:500] if text else None
    return None


async def enrich_from_website(website_url: str) -> dict:
    """Fetch a small set of public pages. Never crawls the whole site."""
    pages: dict[str, str] = {}
    parsed = urlparse(website_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    for path in CANDIDATE_PATHS:
        url = origin if path == "/" else urljoin(origin, path)
        try:
            pages[url] = await fetch_text(url)
        except Exception:
            continue
        if len(pages) >= 4:
            break

    combined = "\n".join(pages.values())
    links: dict[str, str] = {}
    description = None
    for url, html in pages.items():
        links.update(extract_links(html, url))
        description = description or extract_description(html)

    careers_html = next((html for url, html in pages.items() if "career" in url or "job" in url), "")
    about_html = next((html for url, html in pages.items() if "about" in url or "company" in url or "team" in url), "")
    homepage_html = next(iter(pages.values()), "")
    remote = classify_remote_policy(
        website_text=homepage_html,
        careers_text=careers_html,
        about_text=about_html,
        evidence_url=next((url for url in pages if "career" in url), website_url),
    )
    technologies = detect_technologies(combined)
    return {
        "description": description,
        "links": links,
        "remote": remote,
        "technologies": technologies,
        "evidence_urls": list(pages.keys()),
    }


def apply_website_enrichment(raw: RawCompany, enrichment: dict) -> RawCompany:
    links = enrichment.get("links") or {}
    raw.linkedin_url = raw.linkedin_url or links.get("linkedin_url")
    raw.github_url = raw.github_url or links.get("github_url")
    raw.twitter_url = raw.twitter_url or links.get("twitter_url")
    raw.careers_url = raw.careers_url or links.get("careers_url")
    raw.description = raw.description or enrichment.get("description")
    remote = enrichment.get("remote")
    if remote and (raw.remote_policy is None or str(raw.remote_policy) == "UNKNOWN"):
        raw.remote_policy = remote.policy
        raw.remote_policy_text = remote.evidence_text
        raw.remote_confidence = remote.confidence
        raw.remote_evidence_url = remote.evidence_url
        raw.remote_regions = remote.regions or []
        raw.office_required = remote.office_required
    for bucket, values in (enrichment.get("technologies") or {}).items():
        current = getattr(raw, bucket) or []
        setattr(raw, bucket, list(dict.fromkeys([*current, *values])))
    if enrichment.get("technologies"):
        raw.tech_stack_confidence = raw.tech_stack_confidence or 0.4
    return raw
