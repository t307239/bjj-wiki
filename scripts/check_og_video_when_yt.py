#!/usr/bin/env python3
"""
check_og_video_when_yt.py — z255jjjj-WW Round10:
When a page has YouTube embed, it must also have og:video for Facebook
inline video player + article:author + article:published_time for E-A-T.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')


def main() -> int:
    miss: dict[str, list[str]] = {"og:video": [], "article:author": [], "article:published_time": []}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if NOINDEX_RE.search(html[:600]):
                continue
            src = f"{lang}/{fp.name}"
            if "youtube.com/embed" in html and 'property="og:video"' not in html:
                miss["og:video"].append(src)
            if 'og:type" content="article"' in html:
                if 'property="article:author"' not in html:
                    miss["article:author"].append(src)
                # Per CLAUDE.md "嘘より沈黙": only require article:published_time
                # when we actually have a verified datePublished in JSON-LD.
                # Don't fabricate dates for legacy pages without one.
                if '"datePublished"' in html and 'property="article:published_time"' not in html:
                    miss["article:published_time"].append(src)

    total = sum(len(v) for v in miss.values())
    for k, v in miss.items():
        print(f"❌ Missing {k}: {len(v)}")
        for s in v[:3]:
            print(f"   {s}")
    if total == 0:
        print("\n✅ All YouTube + article pages have full Open Graph + E-A-T metadata.")
    if "--ci" in sys.argv:
        return 1 if total > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
