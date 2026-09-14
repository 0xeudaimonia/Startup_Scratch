from __future__ import annotations

NOTABLE_INVESTORS = {
    "y combinator": {"type": "accelerator", "aliases": ["yc", "ycombinator"]},
    "sequoia": {"type": "vc", "aliases": ["sequoia capital"]},
    "accel": {"type": "vc", "aliases": ["accel partners"]},
    "andreessen horowitz": {"type": "vc", "aliases": ["a16z", "a16z crypto"]},
    "benchmark": {"type": "vc", "aliases": ["benchmark capital"]},
    "index ventures": {"type": "vc", "aliases": ["index"]},
    "general catalyst": {"type": "vc", "aliases": ["gc"]},
    "lightspeed": {"type": "vc", "aliases": ["lightspeed venture partners", "lvp"]},
    "founders fund": {"type": "vc", "aliases": []},
    "bessemer": {"type": "vc", "aliases": ["bessemer venture partners", "bvp"]},
    "greylock": {"type": "vc", "aliases": ["greylock partners"]},
    "gv": {"type": "vc", "aliases": ["google ventures"]},
    "khosla ventures": {"type": "vc", "aliases": ["khosla"]},
    "nea": {"type": "vc", "aliases": ["new enterprise associates"]},
    "techstars": {"type": "accelerator", "aliases": []},
    "500 global": {"type": "accelerator", "aliases": ["500 startups"]},
    "seedcamp": {"type": "accelerator", "aliases": []},
    "antler": {"type": "accelerator", "aliases": []},
}


def normalize_investor_name(name: str) -> str:
    return " ".join(name.strip().lower().split())


def is_notable_investor(name: str) -> bool:
    needle = normalize_investor_name(name)
    for canonical, meta in NOTABLE_INVESTORS.items():
        if needle == canonical or needle in meta["aliases"]:
            return True
        if canonical in needle or any(alias in needle for alias in meta["aliases"] if alias):
            return True
    return False


def canonical_investor_name(name: str) -> str:
    needle = normalize_investor_name(name)
    for canonical, meta in NOTABLE_INVESTORS.items():
        if needle == canonical or needle in meta["aliases"] or canonical in needle:
            return canonical.title() if canonical != "gv" else "GV"
    return name.strip()
