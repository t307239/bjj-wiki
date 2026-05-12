#!/usr/bin/env python3
"""
check_no_duplicate_html_id.py — z255jjjj-WW Round16: HTML ID uniqueness lint

HTML spec requires unique IDs per page. Duplicate IDs break:
  - JS getElementById() (returns first match silently)
  - aria-labelledby / aria-controls bindings
  - CSS #id selectors
  - Anchor scroll (#id navigation jumps to first match)

Most common offender: duplicate "back-to-top" buttons after layout
patches stacked over time.
"""
from __future__ import annotations
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
ID_RE = re.compile(r'\bid="([^"]+)"')


def main() -> int:
    hits: list[str] = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if NOINDEX_RE.search(html[:600]):
                continue
            ids = ID_RE.findall(html)
            dup = [i for i, n in Counter(ids).items() if n > 1 and i.strip()]
            if dup:
                hits.append(f"{lang}/{fp.name}: dup {dup[:3]}")

    print(f"❌ Pages with duplicate HTML id attributes: {len(hits)}")
    for h in hits[:6]:
        print(f"   {h}")
    if not hits:
        print("\n✅ All indexable pages have unique HTML IDs.")
    if "--ci" in sys.argv:
        return 1 if hits else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
