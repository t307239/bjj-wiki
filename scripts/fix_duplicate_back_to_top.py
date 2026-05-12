#!/usr/bin/env python3
"""
fix_duplicate_back_to_top.py — Wave WW Round 16: HTML duplicate ID fix

282 pages have 2 `id="back-to-top"` buttons (HTML invalid, breaks
keyboard navigation + screen reader landmark behavior).

Strategy: keep the FIRST occurrence (which is consistent with the
template), remove the SECOND.

Idempotent.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')

# Match the back-to-top button: opens with <button [...] id="back-to-top" [...]>↑</button>
BUTTON_RE = re.compile(
    r'<button[^>]*\bid="back-to-top"[^>]*>[^<]*</button>',
    re.IGNORECASE,
)


def patch_one(fp: Path) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"
    matches = list(BUTTON_RE.finditer(html))
    if len(matches) <= 1:
        return "skip-not-dup"
    # Remove all but first
    # Process from end to start so positions stay valid
    new_html = html
    for m in reversed(matches[1:]):
        new_html = new_html[:m.start()] + new_html[m.end():]
    fp.write_text(new_html, encoding="utf-8")
    return f"patched-{len(matches)-1}-removed"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = patch_one(fp)
            stats[r] = stats.get(r, 0) + 1
    print("Duplicate back-to-top fix:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
