#!/usr/bin/env python3
"""
patch_og_locale.py — Wave WW Round 3 SEO: add og:locale + og:locale:alternate

Audit found: 100% of 4,452 indexable pages are missing og:locale.
Facebook + LinkedIn use this for international content surfacing.
Google uses it as a hreflang corroboration signal.

Patch:
  - og:locale = en_US / ja_JP / pt_BR (based on directory)
  - og:locale:alternate × 2 (the other 2 locales)
  - og:type if missing (default 'article')

Idempotent. Inserts after existing <meta property="og:type"> or, if missing,
after <meta property="og:url"> as anchor.

Per CLAUDE.md rule -4: template was updated first; this patch covers existing
corpus until next regeneration.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
LOCALE_MAP = {"en": "en_US", "ja": "ja_JP", "pt": "pt_BR"}

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
ALREADY_RE = re.compile(r'<meta property=["\']og:locale["\']', re.IGNORECASE)
OG_TYPE_RE = re.compile(r'(<meta property=["\']og:type["\'][^>]*>)\s*\n?', re.IGNORECASE)
OG_URL_RE = re.compile(r'(<meta property=["\']og:url["\'][^>]*>)\s*\n?', re.IGNORECASE)
OG_TITLE_RE = re.compile(r'(<meta property=["\']og:title["\'][^>]*>)\s*\n?', re.IGNORECASE)
# Fallbacks: any other og: meta tag we can find
OG_SITE_RE = re.compile(r'(<meta property=["\']og:site_name["\'][^>]*>)\s*\n?', re.IGNORECASE)
OG_IMAGE_RE = re.compile(r'(<meta property=["\']og:image["\'][^>]*>)\s*\n?', re.IGNORECASE)


def build_og_block(lang: str, include_type: bool) -> str:
    primary = LOCALE_MAP[lang]
    alts = [LOCALE_MAP[l] for l in LANGS if l != lang]
    lines = []
    if include_type:
        lines.append('<meta property="og:type" content="article">')
    lines.append(f'<meta property="og:locale" content="{primary}">')
    for a in alts:
        lines.append(f'<meta property="og:locale:alternate" content="{a}">')
    return "\n".join(lines) + "\n"


def patch_one(fp: Path, lang: str) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"
    if ALREADY_RE.search(html):
        return "already"

    has_og_type = bool(re.search(r'<meta property=["\']og:type["\']', html))
    block = build_og_block(lang, include_type=not has_og_type)

    # Anchor: prefer in this order
    for anchor_re in (OG_TYPE_RE, OG_URL_RE, OG_TITLE_RE, OG_SITE_RE, OG_IMAGE_RE):
        m = anchor_re.search(html)
        if m:
            new_html = html[:m.end()] + block + html[m.end():]
            fp.write_text(new_html, encoding="utf-8")
            return "patched"
    return "skip-no-anchor"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = patch_one(fp, lang)
            stats[r] = stats.get(r, 0) + 1
    print("og:locale patch results:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
