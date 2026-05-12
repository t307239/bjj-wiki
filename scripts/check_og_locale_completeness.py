#!/usr/bin/env python3
"""
check_og_locale_completeness.py — z255jjjj-WW Round3: og:locale presence lint

Verifies every indexable page has:
  - og:locale (required)
  - og:locale:alternate × 2 (other 2 locales)

Skipped on noindex.
--ci flag → exit 1 if any indexable page is missing.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
LOCALE_RE = re.compile(r'<meta property=["\']og:locale["\'](?!:alternate)', re.IGNORECASE)
ALTERNATE_RE = re.compile(r'<meta property=["\']og:locale:alternate["\']', re.IGNORECASE)


def main() -> int:
    missing_locale: list[str] = []
    missing_alts: list[str] = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                head = fp.read_text(encoding="utf-8", errors="ignore")[:8000]
            except Exception:
                continue
            if NOINDEX_RE.search(head):
                continue
            src = f"{lang}/{fp.name}"
            if not LOCALE_RE.search(head):
                missing_locale.append(src)
            if len(ALTERNATE_RE.findall(head)) < 2:
                missing_alts.append(src)

    print(f"❌ Missing og:locale: {len(missing_locale)}")
    for s in missing_locale[:6]:
        print(f"   {s}")
    print(f"❌ Missing 2× og:locale:alternate: {len(missing_alts)}")
    for s in missing_alts[:6]:
        print(f"   {s}")
    total_err = len(missing_locale) + len(missing_alts)
    if total_err == 0:
        print("\n✅ All indexable pages have og:locale + 2 alternates.")
    if "--ci" in sys.argv:
        return 1 if total_err > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
