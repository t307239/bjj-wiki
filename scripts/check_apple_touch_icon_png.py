#!/usr/bin/env python3
"""
check_apple_touch_icon_png.py — z255jjjj-WW Round6:
apple-touch-icon must be a PNG (Apple iOS spec, not SVG).
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
APPLE_RE = re.compile(r'<link rel="apple-touch-icon"[^>]+href="([^"]+)"', re.IGNORECASE)


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
            m = APPLE_RE.search(html)
            if m and not m.group(1).lower().endswith(".png"):
                miss.append(f"{lang}/{fp.name}: {m.group(1)[-40:]}")
    print(f"❌ apple-touch-icon non-PNG: {len(miss)}")
    for s in miss[:6]:
        print(f"   {s}")
    if not miss:
        print("\n✅ All apple-touch-icon links use PNG.")
    if "--ci" in sys.argv:
        return 1 if miss else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
