#!/usr/bin/env python3
"""
patch_mobile_a11y_meta.py — Wave WW Round 4: 3 small but high-impact meta tags

Audit found 100% of 4,452 indexable pages missing:
  1. <meta name="theme-color" content="#0f172a">
     → Mobile Chrome/Safari color the address bar; visible polish signal
  2. <html dir="ltr">
     → Accessibility, screen reader hint, locale-correctness signal
  3. <meta name="referrer" content="strict-origin-when-cross-origin">
     → Privacy + analytics integrity (Google default since 2020)

All idempotent. Skip noindex pages.

Per CLAUDE.md rule -4: template was updated first; this patch covers
existing corpus until next regeneration.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')

# Anchors / detection
HTML_TAG_RE = re.compile(r'(<html\s+lang="[a-z]{2}")(?![^>]*\bdir=)')
CHARSET_RE = re.compile(r'(<meta charset=["\']UTF-8["\']\s*/?>)\s*\n?', re.IGNORECASE)
HAS_THEME_RE = re.compile(r'<meta name=["\']theme-color["\']', re.IGNORECASE)
HAS_REFERRER_RE = re.compile(r'<meta name=["\']referrer["\']', re.IGNORECASE)

THEME_META = '<meta name="theme-color" content="#0f172a">'
REFERRER_META = '<meta name="referrer" content="strict-origin-when-cross-origin">'


def patch_one(fp: Path) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"

    changes = 0
    # 1. html dir="ltr"
    new_html, n_dir = HTML_TAG_RE.subn(r'\1 dir="ltr"', html, count=1)
    if n_dir:
        changes += 1
        html = new_html

    # 2 + 3. theme-color + referrer after <meta charset>
    m = CHARSET_RE.search(html)
    if m:
        insert = ""
        if not HAS_THEME_RE.search(html):
            insert += THEME_META + "\n"
            changes += 1
        if not HAS_REFERRER_RE.search(html):
            insert += REFERRER_META + "\n"
            changes += 1
        if insert:
            html = html[:m.end()] + insert + html[m.end():]

    if changes == 0:
        return "already"
    fp.write_text(html, encoding="utf-8")
    return f"patched-{changes}"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = patch_one(fp)
            stats[r] = stats.get(r, 0) + 1
    print("Mobile/a11y meta patch results:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
