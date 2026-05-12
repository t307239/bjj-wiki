#!/usr/bin/env python3
"""
check_thin_content_indexable.py — z255jjjj-WW Round14: SEO quality lint

Detects indexable pages with <100 words of <main> body content.
Such "thin content" hurts overall site quality score in Google's ranking.

Tolerance: JA pages are excluded (translation-depth issue tracked in
BACKLOG WIKI-8, separate Gemini batch). EN+PT thin pages either need
content expansion or noindex.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "pt"]  # JA excluded (BACKLOG WIKI-8)
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
STYLE_RE = re.compile(r"<style[^>]*>.*?</style>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
MAIN_RE = re.compile(r"<main[^>]*>(.*?)</main>", re.DOTALL | re.IGNORECASE)

# Pages that are intentionally short (functional / index / app-like)
ALLOWLIST = {
    "index.html",
    "sparring-simulator.html",
    "404.html",
    "newsletter.html",
}


def main() -> int:
    hits: list[str] = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            if fp.name in ALLOWLIST:
                continue
            try:
                html = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if NOINDEX_RE.search(html[:600]):
                continue
            m = MAIN_RE.search(html)
            if not m:
                continue
            body = SCRIPT_RE.sub("", STYLE_RE.sub("", m.group(1)))
            text = re.sub(r"\s+", " ", TAG_RE.sub(" ", body)).strip()
            wc = len(text.split())
            if wc < 100:
                hits.append(f"{lang}/{fp.name}: {wc} words")

    print(f"❌ Indexable pages with <100 words of <main> content: {len(hits)}")
    for h in hits[:8]:
        print(f"   {h}")
    if not hits:
        print("\n✅ No thin-content indexable pages (EN+PT).")
    if "--ci" in sys.argv:
        return 1 if hits else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
