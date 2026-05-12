#!/usr/bin/env python3
"""
wrap_main_tag.py — Wave WW Round 5: HTML5 <main> wrap for a11y + semantic

3,854 indexable pages missing <main> tag. WCAG 1.3.1 + HTML5 semantic spec
both call for a single <main> landmark per page (screen readers + skip-to-main
features rely on it).

Strategy: surgical wrap — insert <main> after </header> and </main> before
first <footer>. Safe because:
  - Doesn't reorder content
  - Skips pages already with <main>
  - Skips pages without both anchors

Idempotent. Skip noindex.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
HEADER_END_RE = re.compile(r'</header>', re.IGNORECASE)
FOOTER_START_RE = re.compile(r'<footer[\s>]', re.IGNORECASE)
MAIN_RE = re.compile(r'<main[\s>]', re.IGNORECASE)


def wrap_one(fp: Path) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"
    if MAIN_RE.search(html):
        return "already"
    h_end = HEADER_END_RE.search(html)
    f_start = FOOTER_START_RE.search(html)
    if not h_end or not f_start:
        return "skip-no-anchors"
    if h_end.end() >= f_start.start():
        return "skip-bad-order"

    new_html = (
        html[:h_end.end()] + "\n<main>\n"
        + html[h_end.end():f_start.start()]
        + "</main>\n" + html[f_start.start():]
    )
    fp.write_text(new_html, encoding="utf-8")
    return "wrapped"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = wrap_one(fp)
            stats[r] = stats.get(r, 0) + 1
    print("<main> wrap results:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
