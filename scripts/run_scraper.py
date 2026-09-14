#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "packages"), str(ROOT / "apps"), str(ROOT / "workers"), str(ROOT / "sources")]

from workers.scraping.tasks import run_source_sync  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a Startup Radar source adapter")
    parser.add_argument("--source", default="fixture", help="Source adapter name")
    args = parser.parse_args()
    result = run_source_sync(args.source)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
