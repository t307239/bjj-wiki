#!/usr/bin/env python3
"""
check_apple_touch_icon_png.py
- z255jjjj-WW Round6: apple-touch-icon must be a PNG (Apple iOS spec, not SVG)
- z260q: indexable page (excluding noindex/redirect) must HAVE apple-touch-icon
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
REDIRECT_RE = re.compile(r'<meta[^>]+http-equiv=["\']refresh["\']', re.IGNORECASE)
APPLE_RE = re.compile(r'<link rel="apple-touch-icon"[^>]+href="([^"]+)"', re.IGNORECASE)


def main() -> int:
    non_png: list[str] = []
    missing: list[str] = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            head = html[:2000]
            if NOINDEX_RE.search(head) or REDIRECT_RE.search(head):
                continue
            m = APPLE_RE.search(html)
            if not m:
                missing.append(f"{lang}/{fp.name}")
                continue
            href = m.group(1).lower()
            if not href.endswith(".png"):
                non_png.append(f"{lang}/{fp.name}: {m.group(1)[-40:]}")

    print(f"❌ apple-touch-icon non-PNG: {len(non_png)}")
    for s in non_png[:6]:
        print(f"   {s}")
    print(f"❌ apple-touch-icon missing (indexable): {len(missing)}")
    for s in missing[:6]:
        print(f"   {s}")
    if not non_png and not missing:
        print("\n✅ All indexable pages have PNG apple-touch-icon.")
    if "--ci" in sys.argv:
        return 1 if (non_png or missing) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
