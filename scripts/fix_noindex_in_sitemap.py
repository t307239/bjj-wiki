#!/usr/bin/env python3
"""
fix_noindex_in_sitemap.py — z255hh: sitemap.xml から noindex page entries を除去.

240 page が `<meta name="robots" content="noindex">` 持ちながら sitemap に
残っており、Google が conflict として wasted crawl + sitemap quality 低下扱い。

修正:
  1. 現 sitemap.xml をパースして各 entry を分析
  2. on-disk page が noindex なら entry を skip
  3. 新 sitemap.xml を書き戻し

Idempotent.
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITEMAP = REPO_ROOT / "sitemap.xml"
SITE_PREFIX = "https://wiki.bjj-app.net/"


def is_noindex(rel: str) -> bool:
    fp = REPO_ROOT / rel
    if not fp.exists():
        return False
    try:
        head = fp.read_text(encoding="utf-8")[:1500]
    except Exception:
        return False
    return "noindex" in head


def main():
    print("🔧 fix_noindex_in_sitemap.py — z255hh")
    sm = SITEMAP.read_text(encoding="utf-8")

    # Match each <url>...</url> block
    block_re = re.compile(r"\s*<url>(.*?)</url>", re.DOTALL)
    blocks = block_re.findall(sm)
    keep_blocks = []
    removed = 0
    for inner in blocks:
        loc_m = re.search(r"<loc>([^<]+)</loc>", inner)
        if not loc_m:
            keep_blocks.append(inner)
            continue
        url = loc_m.group(1)
        if not url.startswith(SITE_PREFIX):
            keep_blocks.append(inner)
            continue
        rel = url[len(SITE_PREFIX):]
        if is_noindex(rel):
            removed += 1
            continue
        keep_blocks.append(inner)

    # Reconstruct sitemap with kept blocks
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    lines.append('        xmlns:xhtml="http://www.w3.org/1999/xhtml">')
    for b in keep_blocks:
        lines.append(f"  <url>{b.strip()}</url>")
    lines.append("</urlset>")
    SITEMAP.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Removed {removed} noindex entries from sitemap")
    print(f"  Kept {len(keep_blocks)} entries")


if __name__ == "__main__":
    main()
