#!/usr/bin/env python3
"""
fix_jsonld_brand_drift.py — Wave WW SEO 2: rebrand "BJJ Wiki" → "BJJ App Wiki"
in JSON-LD author/publisher.

3,487 pages have stale `"name":"BJJ Wiki"` in JSON-LD (Article author /
publisher). Brand was rebranded to "BJJ App Wiki" but JSON-LD didn't
follow. This affects E-A-T signals (Google checks author consistency
across schema + page content).

Idempotent: only replaces "BJJ Wiki" not preceded by "App ".
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

# Match: "name": "BJJ Wiki" (not "BJJ App Wiki")
# Negative lookbehind for "App " to skip already-correct entries.
BRAND_RE = re.compile(r'"name":\s*"BJJ Wiki"(?!\s*App)')


def fix_one(fp: Path) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    new_html, n = BRAND_RE.subn('"name": "BJJ App Wiki"', html)
    if n == 0:
        return "skip-clean"
    fp.write_text(new_html, encoding="utf-8")
    return f"patched-{n}"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = fix_one(fp)
            stats[r] = stats.get(r, 0) + 1
    print("JSON-LD brand drift fix results:")
    total_patched = 0
    for k, v in sorted(stats.items()):
        if k.startswith("patched-"):
            total_patched += v
        print(f"  {k}: {v:,}")
    print(f"  TOTAL pages patched: {total_patched:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
