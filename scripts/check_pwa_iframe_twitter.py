#!/usr/bin/env python3
"""
check_pwa_iframe_twitter.py — z255jjjj-WW Round8: 3 quality lints

Verifies every indexable page has:
  1. <link rel="manifest"> (PWA install prompt)
  2. YouTube iframes (if any) have width + height (CLS prevention)
  3. twitter:creator (attribution completeness when twitter:site is set)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')


def main() -> int:
    miss: dict[str, list[str]] = {"manifest": [], "iframe-dim": [], "tw-creator": []}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if NOINDEX_RE.search(html[:600]):
                continue
            src = f"{lang}/{fp.name}"
            if 'rel="manifest"' not in html:
                miss["manifest"].append(src)
            for m in re.finditer(r"<iframe[^>]*?>", html, re.DOTALL):
                tag = m.group(0)
                if "youtube" in tag and ("width=" not in tag or "height=" not in tag):
                    miss["iframe-dim"].append(src)
                    break
            if '<meta name="twitter:site"' in html and '<meta name="twitter:creator"' not in html:
                miss["tw-creator"].append(src)

    total = sum(len(v) for v in miss.values())
    for k, v in miss.items():
        print(f"❌ Missing {k}: {len(v)}")
        for s in v[:3]:
            print(f"   {s}")
    if total == 0:
        print("\n✅ All indexable pages have manifest + iframe dims + tw:creator.")
    if "--ci" in sys.argv:
        return 1 if total > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
