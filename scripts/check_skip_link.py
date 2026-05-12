#!/usr/bin/env python3
"""
check_skip_link.py — z255jjjj-WW Round7: WCAG 2.4.1 Bypass Blocks

Every indexable page should have a skip-to-content link as one of the first
focusable elements (so keyboard / screen-reader users can skip nav).
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
SKIP_LINK_RE = re.compile(r'class="skip-link"', re.IGNORECASE)


def main() -> int:
    miss: list[str] = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if NOINDEX_RE.search(html[:600]):
                continue
            if not SKIP_LINK_RE.search(html):
                miss.append(f"{lang}/{fp.name}")
    print(f"❌ Missing skip-to-content link (WCAG 2.4.1): {len(miss)}")
    for s in miss[:6]:
        print(f"   {s}")
    if not miss:
        print("\n✅ All indexable pages have a skip-link.")
    if "--ci" in sys.argv:
        return 1 if miss else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
