#!/usr/bin/env python3
"""
check_no_generic_h1.py — z255jjjj-WW Round12: SEO + content quality lint

Detect generic placeholder h1 like "Master this Technique" that fails to
identify the page's specific topic. Such h1s kill SEO (Google can't tell
what the page is about from the heading) and confuse readers.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
H1_RE = re.compile(r'<h1[^>]*>([^<]+)</h1>')

GENERIC_H1S = {
    "Master this Technique",
    "Master this technique",
    "Master This Technique",
    "学ぶべきポイント",
    "Domine esta Técnica",
    "Untitled",
    "Tutorial",
    "Master Technique",
}


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
            m = H1_RE.search(html)
            if m and m.group(1).strip() in GENERIC_H1S:
                hits.append(f"{lang}/{fp.name}: '{m.group(1).strip()}'")
    print(f"❌ Pages with generic placeholder <h1>: {len(hits)}")
    for h in hits[:6]:
        print(f"   {h}")
    if not hits:
        print("\n✅ No generic placeholder h1 found.")
    if "--ci" in sys.argv:
        return 1 if hits else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
