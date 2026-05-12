#!/usr/bin/env python3
"""
check_videoobject_when_yt_embed.py — z255jjjj-WW Round5: rich snippet lint

When a page embeds a YouTube iframe, it should have VideoObject JSON-LD
schema for Google rich video snippets in SERP.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
YT_RE = re.compile(r'youtube(?:-nocookie)?\.com/embed/', re.IGNORECASE)
VIDEO_OBJECT_RE = re.compile(r'"@type"\s*:\s*"VideoObject"')


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
            if YT_RE.search(html) and not VIDEO_OBJECT_RE.search(html):
                miss.append(f"{lang}/{fp.name}")
    print(f"❌ Pages with YouTube embed but no VideoObject schema: {len(miss)}")
    for s in miss[:6]:
        print(f"   {s}")
    if not miss:
        print("\n✅ All YouTube-embedding pages have VideoObject schema.")
    if "--ci" in sys.argv:
        return 1 if miss else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
