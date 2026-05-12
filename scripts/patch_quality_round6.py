#!/usr/bin/env python3
"""
patch_quality_round6.py — Wave WW Round 6: 4 horizontal quality fixes

Audit found 4 horizontal bugs across full corpus:
  1. apple-touch-icon points to .svg → switch to /apple-touch-icon.png (180x180)
  2. <a class="active"> in lang-nav has no aria-current="page" → add it (a11y)
  3. <button> without type → add type="button" (prevent accidental form submit)
  4. og:image URL has unencoded spaces → percent-encode

All idempotent. Skip noindex.
Per CLAUDE.md rule -4: template was updated first; this patch covers
existing corpus until next regeneration.
"""
from __future__ import annotations
import re
import sys
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')

# Fix 1: apple-touch-icon → PNG
APPLE_SVG_RE = re.compile(
    r'<link rel="apple-touch-icon" href="https://wiki\.bjj-app\.net/og-image\.svg">',
    re.IGNORECASE,
)
APPLE_PNG = '<link rel="apple-touch-icon" sizes="180x180" href="https://wiki.bjj-app.net/apple-touch-icon.png">'

# Fix 2: aria-current on active lang-nav link
NAV_ACTIVE_RE = re.compile(
    r'(<a href="\.\./[a-z]{2}/[^"]+"\s+class="active")(?![^>]*aria-current)',
)

# Fix 3: <button> without type
# Be conservative: only add type="button" to buttons that don't already have type=
BUTTON_NO_TYPE_RE = re.compile(
    r'(<button)(?!\s+[^>]*type=)(\s|>)',
)

# Fix 4: og:image URL encoding (only encode spaces in title query param)
OG_IMAGE_SPACE_RE = re.compile(
    r'(<meta property="og:image" content=")([^"]+)(")',
)


def encode_og_image_url(url: str) -> str:
    """Percent-encode spaces in the title query parameter."""
    if " " not in url:
        return url
    # Only fix the spaces — preserve existing & and = structure
    return url.replace(" ", "%20")


def patch_one(fp: Path) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"

    changes = 0
    new_html = html

    # 1. apple-touch-icon
    new_html, n = APPLE_SVG_RE.subn(APPLE_PNG, new_html)
    if n:
        changes += n

    # 2. aria-current on active nav
    new_html, n = NAV_ACTIVE_RE.subn(r'\1 aria-current="page"', new_html)
    if n:
        changes += n

    # 3. button type
    new_html, n = BUTTON_NO_TYPE_RE.subn(r'\1 type="button"\2', new_html)
    if n:
        changes += n

    # 4. og:image URL space encoding
    def encode_match(m: re.Match) -> str:
        original = m.group(2)
        encoded = encode_og_image_url(original)
        if encoded == original:
            return m.group(0)
        return f'{m.group(1)}{encoded}{m.group(3)}'

    new_html_after_og, n_og_space_check = OG_IMAGE_SPACE_RE.subn(encode_match, new_html)
    if new_html_after_og != new_html:
        changes += 1
        new_html = new_html_after_og

    if changes == 0:
        return "already"
    fp.write_text(new_html, encoding="utf-8")
    return f"patched-{changes}"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = patch_one(fp)
            stats[r] = stats.get(r, 0) + 1
    print("Round 6 quality patch results:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
