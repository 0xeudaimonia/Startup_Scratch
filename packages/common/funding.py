from __future__ import annotations

import re

from models.enums import FundingStage

_STAGE_PATTERNS: list[tuple[re.Pattern[str], FundingStage]] = [
    (re.compile(r"pre[-\s]?seed|preseed", re.I), FundingStage.PRE_SEED),
    (re.compile(r"\bseed\b", re.I), FundingStage.SEED),
    (re.compile(r"series\s*a\b", re.I), FundingStage.SERIES_A),
    (re.compile(r"series\s*b\b", re.I), FundingStage.SERIES_B),
    (re.compile(r"series\s*c\b", re.I), FundingStage.SERIES_C),
    (re.compile(r"series\s*[d-z]\b|series\s*d\+|late[-\s]?stage", re.I), FundingStage.SERIES_D_PLUS),
    (re.compile(r"\bgrowth\b|private equity", re.I), FundingStage.GROWTH),
    (re.compile(r"bootstrapped|bootstrapping|no funding", re.I), FundingStage.BOOTSTRAPPED),
]


def normalize_funding_stage(text: str | None) -> FundingStage:
    if not text:
        return FundingStage.UNKNOWN
    value = text.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "preseed": FundingStage.PRE_SEED,
        "pre_seed": FundingStage.PRE_SEED,
        "seed": FundingStage.SEED,
        "series_a": FundingStage.SERIES_A,
        "seriesa": FundingStage.SERIES_A,
        "series_b": FundingStage.SERIES_B,
        "series_c": FundingStage.SERIES_C,
        "series_d": FundingStage.SERIES_D_PLUS,
        "series_d_plus": FundingStage.SERIES_D_PLUS,
        "growth": FundingStage.GROWTH,
        "bootstrapped": FundingStage.BOOTSTRAPPED,
        "unknown": FundingStage.UNKNOWN,
    }
    if value in aliases:
        return aliases[value]
    for pattern, stage in _STAGE_PATTERNS:
        if pattern.search(text):
            return stage
    return FundingStage.UNKNOWN


def round_type_rank(stage: FundingStage | str | None) -> int:
    order = [
        FundingStage.UNKNOWN,
        FundingStage.BOOTSTRAPPED,
        FundingStage.PRE_SEED,
        FundingStage.SEED,
        FundingStage.SERIES_A,
        FundingStage.SERIES_B,
        FundingStage.SERIES_C,
        FundingStage.SERIES_D_PLUS,
        FundingStage.GROWTH,
    ]
    try:
        return order.index(FundingStage(stage)) if stage else 0
    except ValueError:
        return 0
