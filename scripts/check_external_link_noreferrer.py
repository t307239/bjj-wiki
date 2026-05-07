#!/usr/bin/env python3
"""
check_external_link_noreferrer.py — z255ddd: 24th bjj-wiki lint

External link (target="_blank" + http(s)://) で rel に noopener はあるが
noreferrer 不在を catch (privacy: referrer leak 防止)

旧 silent privacy bug: 14,073 件の external link で referrer header 漏出
(z255ddd fix_external_link_noreferrer.py で fix)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def check_page(fp: Path) -> int:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return 0
    if "noindex" in html[:1500]:
        return 0
    count = 0
    for m in re.finditer(r'<a\b[^>]*>', html):
        tag = m.group(0)
        if 'target="_blank"' not in tag:
            continue
        if not re.search(r'href="http', tag):
            continue
        rel_m = re.search(r'\brel="([^"]+)"', tag)
        if not rel_m:
            continue
        rel = rel_m.group(1)
        if 'noopener' in rel and 'noreferrer' not in rel:
            count += 1
    return count


def main():
    failed = []
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            count = check_page(fp)
            if count > 0:
                failed.append((str(fp.relative_to(REPO_ROOT)), count))

    print(f"❌ Pages with noopener-only external link (no noreferrer): {len(failed)}")
    for fp, count in failed[:10]:
        print(f"  {fp}: {count} links")

    if "--ci" in sys.argv:
        sys.exit(1 if failed else 0)
    if not failed:
        print("\n✅ All external links use rel='noopener noreferrer'.")


if __name__ == "__main__":
    main()
