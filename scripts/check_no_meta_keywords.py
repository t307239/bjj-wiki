#!/usr/bin/env python3
"""
check_no_meta_keywords.py — z255nnn: 29th bjj-wiki lint

<meta name="keywords"> 残留 catch (Google 2009 から ignore、bloat のみ)

旧 silent SEO bug: 2,813 page で残留 (z255nnn fix で削除)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def check_page(fp: Path) -> bool:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return False
    if "noindex" in html[:1500]:
        return False
    return bool(re.search(r'<meta name="keywords"', html))


def main():
    failed = []
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            if check_page(fp):
                failed.append(str(fp.relative_to(REPO_ROOT)))

    print(f"❌ Pages with obsolete <meta name='keywords'>: {len(failed)}")
    for fp in failed[:10]:
        print(f"  {fp}")

    if "--ci" in sys.argv:
        sys.exit(1 if failed else 0)
    if not failed:
        print("\n✅ No obsolete meta keywords (Google ignores since 2009).")


if __name__ == "__main__":
    main()
