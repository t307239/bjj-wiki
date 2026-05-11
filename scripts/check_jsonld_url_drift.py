#!/usr/bin/env python3
"""
check_jsonld_url_drift.py — z255hhh: 26th bjj-wiki lint

JSON-LD Article.url ≠ <link rel="canonical"> を catch
旧 silent SEO bug: 883 page で url drift (z255hhh fix)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def check_page(fp: Path) -> str | None:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return None
    if "noindex" in html[:1500]:
        return None
    canon_m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    if not canon_m:
        return None
    canon = canon_m.group(1)
    for m in re.finditer(r'<script type="application/ld\+json">\s*(\{[^<]*?"@type"\s*:\s*"Article"[^<]*?\})\s*</script>', html):
        block = m.group(1)
        # z255hhh-fix: skip nested objects (publisher.url, author.url etc.) — strip them first
        stripped = re.sub(r'"\w+"\s*:\s*\{[^{}]*\}', '', block)
        # Look for top-level url-like fields
        for url_m in re.finditer(r'"(url|mainEntityOfPage)"\s*:\s*"([^"]+)"', stripped):
            field, value = url_m.group(1), url_m.group(2)
            # Normalize trailing .html for comparison
            v_norm = value.rstrip('/').removesuffix('.html')
            c_norm = canon.rstrip('/').removesuffix('.html')
            if v_norm != c_norm:
                return f"jsonld.{field}={value[:50]} ≠ canon={canon[:50]}"
    return None


def main():
    failed = []
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            err = check_page(fp)
            if err:
                failed.append((str(fp.relative_to(REPO_ROOT)), err))
    print(f"❌ Pages with JSON-LD url drift: {len(failed)}")
    for fp, err in failed[:10]:
        print(f"  {fp}: {err}")
    if "--ci" in sys.argv:
        sys.exit(1 if failed else 0)
    if not failed:
        print("\n✅ All JSON-LD Article.url match canonical.")


if __name__ == "__main__":
    main()
