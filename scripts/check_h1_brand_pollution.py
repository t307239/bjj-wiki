#!/usr/bin/env python3
"""
check_h1_brand_pollution.py — z255zz: 22nd bjj-wiki lint

<h1> に '| BJJ Wiki' / '| BJJ Wiki Brasil' 等 brand suffix が混入していないか catch。

旧 silent SEO bug: 115 PT page で h1 に suffix 混入 → keyword stuffing + char overflow
(z255zz fix_h1_brand_pollution.py で fix)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BRAND_SUFFIX_RE = re.compile(r'\|\s*BJJ\s*Wiki', re.IGNORECASE)


def check_page(fp: Path) -> str | None:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return None
    if "noindex" in html[:1500]:
        return None

    h1_m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    if not h1_m:
        return None

    if BRAND_SUFFIX_RE.search(h1_m.group(1)):
        return f"h1='{h1_m.group(1)[:60]}'"
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

    print(f"❌ Pages with h1 brand pollution: {len(failed)}")
    for fp, err in failed[:20]:
        print(f"  {fp}: {err}")

    if "--ci" in sys.argv:
        sys.exit(1 if failed else 0)
    if not failed:
        print("\n✅ All h1 elements clean of brand suffix.")


if __name__ == "__main__":
    main()
