#!/usr/bin/env python3
"""
fix_jsonld_url_drift.py — z255hhh: JSON-LD Article.url が canonical と不一致 fix

旧 silent SEO bug:
- 一部 page で JSON-LD `"@type": "Article", "url": "..."` が canonical と異なる
  例 1: jsonld='https://wiki.bjj-app.net/' (root) vs canonical='/ja/spider-guard.html'
  例 2: jsonld='/en/bjj-offensive-bjj-guide' (no .html) vs canonical='.../bjj-offensive-bjj-guide.html'
- 結果: Google が JSON-LD url を信頼するか canonical を信頼するか曖昧、
  rich snippet 帰属先がぶれる SEO 機会喪失

修正: JSON-LD Article 内の url を canonical と sync
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def patch_page(fp: Path) -> bool:
    html = fp.read_text(encoding="utf-8")
    if "noindex" in html[:1500]:
        return False
    canon_m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    if not canon_m:
        return False
    canon = canon_m.group(1)

    # Find Article json-ld blocks where url drifts from canonical
    changed = False

    def replace_article_url(m: re.Match) -> str:
        nonlocal changed
        block = m.group(0)
        # Only touch if url field differs
        url_m = re.search(r'("url":\s*")([^"]+)(")', block)
        if not url_m:
            return block
        if url_m.group(2).rstrip('/') == canon.rstrip('/'):
            return block
        new_block = block[:url_m.start(2)] + canon + block[url_m.end(2):]
        changed = True
        return new_block

    # Pattern: any block containing "@type": "Article" — match the entire JSON-LD script
    new_html = re.sub(
        r'<script type="application/ld\+json">(\{[^<]*?"@type"\s*:\s*"Article"[^<]*?\})</script>',
        replace_article_url,
        html
    )

    if not changed:
        return False
    fp.write_text(new_html, encoding="utf-8")
    return True


def main():
    print("🔧 fix_jsonld_url_drift.py — z255hhh")
    fixed = 0
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            if patch_page(fp):
                fixed += 1
    print(f"  ✅ {fixed} pages fixed")


if __name__ == "__main__":
    main()
