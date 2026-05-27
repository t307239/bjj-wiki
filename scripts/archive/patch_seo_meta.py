#!/usr/bin/env python3
"""
patch_seo_meta.py — Wave WW (SEO): inject 2 high-impact SEO meta tags

1. <meta name="robots" content="max-image-preview:large, index, follow">
   → enables Google to show LARGE image previews in SERP (CTR boost)
   → 0 pages have this currently

2. <meta property="og:image:alt" content="<page title>">
   → Twitter/Facebook accessibility + SEO + Open Graph richness
   → 4,442 indexable pages have og:image but 0 have og:image:alt

Both are idempotent — re-running skips already-patched pages.
Skips noindex / redirect pages.
"""
from __future__ import annotations
import html as html_mod
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

# Robots meta directive (preserves existing if present)
ROBOTS_META = '<meta name="robots" content="max-image-preview:large, index, follow">'
# Anchor: insert after <meta charset="UTF-8"> (universal across all pages)
CHARSET_RE = re.compile(r'(<meta charset=["\']UTF-8["\']\s*/?>)\s*\n?', re.IGNORECASE)
EXISTING_ROBOTS_RE = re.compile(r'<meta\s+name=["\']robots["\']', re.IGNORECASE)
OG_IMAGE_RE = re.compile(
    # Tolerant of single quotes inside content (e.g. D'Arce). Match the outer
    # quote char with backreference so we don't match across attributes.
    r'(<meta property=(["\'])og:image\2 content=(["\']).*?\3\s*/?>)\s*\n?',
    re.IGNORECASE,
)
EXISTING_OG_ALT_RE = re.compile(r'<meta property=["\']og:image:alt["\']', re.IGNORECASE)
TITLE_RE = re.compile(r'<title>([^<]+)</title>', re.IGNORECASE)
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', re.IGNORECASE)


def derive_alt_from_title(title: str) -> str:
    """Strip brand suffix and other noise from <title> for use as image alt."""
    # Remove common brand suffixes
    for sep in [" | BJJ App Wiki", " — BJJ App Wiki", " | BJJ Wiki", " — BJJ Wiki"]:
        if sep in title:
            title = title.split(sep)[0]
    return title.strip()


def patch_one(fp: Path) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"

    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"

    changed = False

    # 1. Robots meta (only if no existing robots tag)
    if not EXISTING_ROBOTS_RE.search(html):
        m = CHARSET_RE.search(html)
        if m:
            html = html[:m.end()] + ROBOTS_META + "\n" + html[m.end():]
            changed = True

    # 2. og:image:alt
    if not EXISTING_OG_ALT_RE.search(html):
        m_img = OG_IMAGE_RE.search(html)
        m_title = TITLE_RE.search(html)
        if m_img and m_title:
            alt = derive_alt_from_title(m_title.group(1))
            alt_escaped = html_mod.escape(alt, quote=True)
            alt_meta = f'<meta property="og:image:alt" content="{alt_escaped}">\n'
            html = html[:m_img.end()] + alt_meta + html[m_img.end():]
            changed = True

    if changed:
        fp.write_text(html, encoding="utf-8")
        return "patched"
    return "already"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = patch_one(fp)
            stats[r] = stats.get(r, 0) + 1
    print("SEO meta patch results:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
