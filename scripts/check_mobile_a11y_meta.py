#!/usr/bin/env python3
"""
check_mobile_a11y_meta.py — z255jjjj-WW Round4: theme-color / dir / referrer

Verifies every indexable page has:
  - <meta name="theme-color">
  - <html dir="...">
  - <meta name="referrer">

--ci flag → exit 1 if any indexable page missing.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')


def main() -> int:
    miss: dict[str, list[str]] = {"theme-color": [], "html-dir": [], "referrer": []}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if NOINDEX_RE.search(html[:600]):
                continue
            src = f"{lang}/{fp.name}"
            head = html[:8000]
            if not re.search(r'<meta name=["\']theme-color["\']', head, re.IGNORECASE):
                miss["theme-color"].append(src)
            if not re.search(r'<html[^>]+\bdir=', head, re.IGNORECASE):
                miss["html-dir"].append(src)
            if not re.search(r'<meta name=["\']referrer["\']', head, re.IGNORECASE):
                miss["referrer"].append(src)

    total = sum(len(v) for v in miss.values())
    for k, v in miss.items():
        print(f"❌ Missing {k}: {len(v)}")
        for s in v[:3]:
            print(f"   {s}")
    if total == 0:
        print("\n✅ All indexable pages have theme-color + dir + referrer.")
    if "--ci" in sys.argv:
        return 1 if total > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
