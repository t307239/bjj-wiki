#!/usr/bin/env python3
"""
enrich_sitemap_hreflang.py — Wave WW Round 6: international SEO

sitemap.xml has 4,456 URLs but 0 xhtml:link hreflang annotations. Google
recommends sitemap-level hreflang as the canonical source for locale
variants (more reliable than crawling each page's <link rel="alternate">).

For each URL like /en/<slug>.html, add:
  <xhtml:link rel="alternate" hreflang="en" href=".../en/<slug>.html"/>
  <xhtml:link rel="alternate" hreflang="ja" href=".../ja/<slug>.html"/>
  <xhtml:link rel="alternate" hreflang="pt" href=".../pt/<slug>.html"/>
  <xhtml:link rel="alternate" hreflang="x-default" href=".../en/<slug>.html"/>

Skip:
  - Root pages (/privacy, /about, /athletes) — not locale-grouped
  - URLs whose alternates don't actually exist on disk

Idempotent: skip URLs that already have xhtml:link.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITEMAP = REPO_ROOT / "sitemap.xml"
BASE = "https://wiki.bjj-app.net"
LANGS = ["en", "ja", "pt"]

URL_PATH_RE = re.compile(rf'<loc>{re.escape(BASE)}/([a-z]{{2}})/([^<]+)</loc>')
URL_BLOCK_RE = re.compile(r'<url>(.*?)</url>', re.DOTALL)


def build_alternates(slug_path: str) -> str:
    """Return the xhtml:link block (4 lines) for a page, only if all locales exist."""
    available = []
    for lang in LANGS:
        if (REPO_ROOT / lang / slug_path).exists():
            available.append(lang)
    if len(available) < 2:
        return ""  # No need for hreflang if only 1 locale exists

    lines = []
    for lang in available:
        lines.append(
            f'<xhtml:link rel="alternate" hreflang="{lang}" '
            f'href="{BASE}/{lang}/{slug_path}"/>'
        )
    # x-default → English fallback
    if "en" in available:
        lines.append(
            f'<xhtml:link rel="alternate" hreflang="x-default" '
            f'href="{BASE}/en/{slug_path}"/>'
        )
    return "".join(lines)


def enrich_url_block(block_content: str) -> tuple[str, bool]:
    """Return (new_block_content, was_modified)."""
    if "xhtml:link" in block_content:
        return block_content, False
    m = URL_PATH_RE.search(block_content)
    if not m:
        return block_content, False
    lang, slug_path = m.group(1), m.group(2)
    alternates = build_alternates(slug_path)
    if not alternates:
        return block_content, False
    return block_content + alternates, True


def main() -> int:
    if not SITEMAP.exists():
        print("❌ sitemap.xml not found", file=sys.stderr)
        return 1
    xml = SITEMAP.read_text(encoding="utf-8")

    enriched_count = 0
    skipped_count = 0

    def replace_block(m: re.Match) -> str:
        nonlocal enriched_count, skipped_count
        block = m.group(1)
        new_block, modified = enrich_url_block(block)
        if modified:
            enriched_count += 1
        else:
            skipped_count += 1
        return f"<url>{new_block}</url>"

    new_xml = URL_BLOCK_RE.sub(replace_block, xml)
    SITEMAP.write_text(new_xml, encoding="utf-8")
    print(f"Sitemap hreflang enrichment:")
    print(f"  enriched: {enriched_count:,}")
    print(f"  skipped:  {skipped_count:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
