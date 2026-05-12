#!/usr/bin/env python3
"""
check_index_locale_parity.py — z255jjjj-WW Round15: hub page parity lint

Detect when one locale's index page has dramatically fewer cat-cards or
internal links than another. Catches regressions like the PT index bug
(only 1 of 11 cat-cards).

Tolerance: max(cards) - min(cards) ≤ 1 across en/ja/pt for index.html.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def count_cat_cards(fp: Path) -> int:
    if not fp.exists():
        return 0
    html = fp.read_text(encoding="utf-8", errors="ignore")
    return len(re.findall(r'class="cat-card"', html))


def main() -> int:
    counts = {lang: count_cat_cards(REPO_ROOT / lang / "index.html") for lang in ("en", "ja", "pt")}
    print(f"index.html cat-card counts: {counts}")
    spread = max(counts.values()) - min(counts.values())
    if spread > 1:
        print(f"❌ index.html locale parity drift: spread={spread}")
        if "--ci" in sys.argv:
            return 1
    else:
        print("✅ All locale index.html have parity cat-card count.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
