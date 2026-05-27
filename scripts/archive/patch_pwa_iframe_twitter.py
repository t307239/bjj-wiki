#!/usr/bin/env python3
"""
patch_pwa_iframe_twitter.py — Wave WW Round 8: 3 horizontal fixes

Audit found 3 horizontal gaps:
  1. 4,452 pages missing <link rel="manifest"> (PWA discovery)
  2. 3,325 pages with YouTube iframe missing width/height (CLS)
  3. 4,041 pages with twitter:site but no twitter:creator (attribution)

All idempotent. Skip noindex.
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

# 1. Manifest link — anchor: insert after apple-touch-icon, fallback: after <link rel="icon">
APPLE_ICON_RE = re.compile(
    r'(<link rel="apple-touch-icon"[^>]*>)\s*\n?', re.IGNORECASE
)
ICON_RE = re.compile(r'(<link rel="icon"[^>]*>)\s*\n?', re.IGNORECASE)
MANIFEST_LINK = '<link rel="manifest" href="/manifest.json">\n'
HAS_MANIFEST_RE = re.compile(r'<link rel="manifest"', re.IGNORECASE)

# 2. iframe YouTube width/height — match any iframe whose src contains youtube.com/embed
IFRAME_RE = re.compile(
    r'(<iframe[^>]*?src="https://www\.youtube(?:-nocookie)?\.com/embed/[^"]+")([^>]*?>)',
    re.IGNORECASE | re.DOTALL,
)

def add_iframe_dims(match: re.Match) -> str:
    full = match.group(0)
    if "width=" in full or "height=" in full:
        return full
    pre = match.group(1)
    rest = match.group(2)
    return f'{pre}\n        width="560"\n        height="315"{rest}'

# 3. Twitter:creator after twitter:site
TWITTER_SITE_RE = re.compile(
    r'(<meta name="twitter:site" content="([^"]+)"\s*/?>)\s*\n?', re.IGNORECASE
)
HAS_TW_CREATOR_RE = re.compile(r'<meta name="twitter:creator"', re.IGNORECASE)


def patch_one(fp: Path) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"

    changes = 0

    # 1. Manifest link
    if not HAS_MANIFEST_RE.search(html):
        m = APPLE_ICON_RE.search(html)
        if m:
            html = html[:m.end()] + MANIFEST_LINK + html[m.end():]
            changes += 1
        else:
            m = ICON_RE.search(html)
            if m:
                html = html[:m.end()] + MANIFEST_LINK + html[m.end():]
                changes += 1

    # 2. iframe dimensions
    new_html, n = IFRAME_RE.subn(add_iframe_dims, html)
    if new_html != html:
        changes += 1
        html = new_html

    # 3. twitter:creator
    if not HAS_TW_CREATOR_RE.search(html):
        def add_creator(m: re.Match) -> str:
            return f'{m.group(1)}\n<meta name="twitter:creator" content="{m.group(2)}">\n'

        new_html = TWITTER_SITE_RE.sub(add_creator, html, count=1)
        if new_html != html:
            changes += 1
            html = new_html

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
    print("Round 8 PWA + iframe + twitter:creator patch:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
