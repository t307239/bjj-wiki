#!/usr/bin/env python3
"""
refresh_date_modified.py — Wave WW Round 2 SEO: refresh Article.dateModified

Article JSON-LD has both `datePublished` and `dateModified`. Currently
many pages have `dateModified == datePublished` even though the page has
been heavily updated since. Google uses `dateModified` as a freshness
signal in ranking + "Updated YYYY-MM-DD" SERP labels.

Update strategy:
- Set dateModified to today's ISO datetime (JST) for all indexable pages
  with Article schema.
- Preserve datePublished (the original author date).
- Idempotent: running twice within the same day is a no-op.

Skip noindex pages.
"""
from __future__ import annotations
import datetime as dt
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
# Match dateModified in any JSON-LD block
DATE_MOD_RE = re.compile(r'"dateModified":\s*"([^"]+)"')

# Format: 2026-05-12T00:00:00+09:00 (JST)
TODAY_ISO = dt.datetime.now().strftime("%Y-%m-%d") + "T00:00:00+09:00"


def patch_one(fp: Path) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"
    if not DATE_MOD_RE.search(html):
        return "skip-no-date"
    new_html, n = DATE_MOD_RE.subn(f'"dateModified":"{TODAY_ISO}"', html)
    if n == 0:
        return "skip-clean"
    # Skip if already today's date
    if new_html == html:
        return "already"
    fp.write_text(new_html, encoding="utf-8")
    return f"patched-{n}"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = patch_one(fp)
            stats[r] = stats.get(r, 0) + 1
    print(f"Refreshed dateModified to {TODAY_ISO}:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
