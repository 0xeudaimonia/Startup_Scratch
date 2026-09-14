from __future__ import annotations

from dataclasses import dataclass

from models.enums import RemotePolicy

GLOBAL_PHRASES = [
    "remote worldwide",
    "work from anywhere",
    "work anywhere",
    "distributed team",
    "fully remote",
    "remote-first worldwide",
    "hire globally",
    "worldwide remote",
    "anywhere in the world",
]

REMOTE_FIRST_PHRASES = [
    "remote first",
    "remote-first",
    "async team",
    "asynchronous team",
    "distributed company",
]

EUROPE_PHRASES = ["remote across europe", "europe remote", "remote europe", "eu remote"]
EMEA_PHRASES = ["remote emea", "emea remote", "europe middle east africa"]
US_PHRASES = ["us remote", "remote us", "united states remote", "usa remote"]
HYBRID_PHRASES = ["hybrid", "office optional", "remote or office"]
ONSITE_PHRASES = ["in office", "on-site", "onsite only", "must be in office"]


@dataclass
class RemoteEvidence:
    policy: RemotePolicy
    confidence: float
    evidence_text: str | None = None
    evidence_url: str | None = None
    countries: list[str] | None = None
    regions: list[str] | None = None
    office_required: bool | None = None


def _count_hits(text: str, phrases: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for phrase in phrases if phrase in lowered)


def classify_remote_policy(
    *,
    website_text: str | None = None,
    careers_text: str | None = None,
    about_text: str | None = None,
    job_remote_types: list[str] | None = None,
    evidence_url: str | None = None,
) -> RemoteEvidence:
    """Classify remote policy using page-level evidence, not a single job keyword."""
    corpus_parts = [part for part in (website_text, careers_text, about_text) if part]
    corpus = "\n".join(corpus_parts).lower()
    jobs = [item.lower() for item in (job_remote_types or [])]
    global_jobs = sum(1 for job in jobs if "global" in job or "worldwide" in job or "anywhere" in job)
    remote_jobs = sum(1 for job in jobs if "remote" in job)

    if corpus:
        if _count_hits(corpus, ONSITE_PHRASES) >= 2 and _count_hits(corpus, GLOBAL_PHRASES) == 0:
            return RemoteEvidence(RemotePolicy.ONSITE, 0.7, "On-site language on company pages", evidence_url, office_required=True)
        if _count_hits(corpus, GLOBAL_PHRASES) >= 1:
            confidence = 0.85 if _count_hits(corpus, GLOBAL_PHRASES) >= 2 or global_jobs >= 2 else 0.7
            return RemoteEvidence(
                RemotePolicy.GLOBAL_REMOTE,
                confidence,
                "Company pages describe worldwide / work-from-anywhere remote work",
                evidence_url,
                regions=["Worldwide"],
                office_required=False,
            )
        if _count_hits(corpus, REMOTE_FIRST_PHRASES) >= 1:
            return RemoteEvidence(
                RemotePolicy.REMOTE_FIRST,
                0.75,
                "Company describes itself as remote-first or distributed",
                evidence_url,
                office_required=False,
            )
        if _count_hits(corpus, EMEA_PHRASES):
            return RemoteEvidence(RemotePolicy.EMEA_REMOTE, 0.7, "EMEA remote language", evidence_url, regions=["EMEA"])
        if _count_hits(corpus, EUROPE_PHRASES):
            return RemoteEvidence(RemotePolicy.EUROPE_REMOTE, 0.7, "Europe remote language", evidence_url, regions=["Europe"])
        if _count_hits(corpus, US_PHRASES):
            return RemoteEvidence(RemotePolicy.US_REMOTE, 0.7, "US remote language", evidence_url, regions=["United States"])
        if _count_hits(corpus, HYBRID_PHRASES):
            return RemoteEvidence(RemotePolicy.HYBRID, 0.65, "Hybrid work language", evidence_url, office_required=False)

    # A single job containing "remote" is not enough for GLOBAL_REMOTE.
    if global_jobs >= 3:
        return RemoteEvidence(
            RemotePolicy.GLOBAL_REMOTE,
            0.55,
            "Multiple independent job listings are worldwide remote",
            evidence_url,
            regions=["Worldwide"],
        )
    if remote_jobs >= 3:
        return RemoteEvidence(RemotePolicy.REMOTE_FIRST, 0.45, "Several jobs are remote", evidence_url)
    if remote_jobs == 1:
        return RemoteEvidence(
            RemotePolicy.UNKNOWN,
            0.2,
            "Only a single job listing mentioned remote work",
            evidence_url,
        )
    return RemoteEvidence(RemotePolicy.UNKNOWN, 0.0)
