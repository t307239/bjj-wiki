#!/usr/bin/env python3
"""
check_duplicate_bjj_prefix.py — z255aaa: 23rd bjj-wiki lint

【BJJ】【BJJ】等 brand prefix の重複混入を catch。
旧 silent UX bug: 188 page で重複 prefix → SEO + 見栄え低下
(z255aaa fix_duplicate_bjj_prefix.py で fix)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DUP_PREFIX_RE = re.compile(r'(【BJJ】\s*){2,}')


def check_page(fp: Path) -> int:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return 0
    if "noindex" in html[:1500]:
        return 0
    return len(DUP_PREFIX_RE.findall(html))


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

    print(f"❌ Pages with duplicate【BJJ】prefix: {len(failed)}")
    for fp, count in failed[:10]:
        print(f"  {fp}: {count} occurrences")

    if "--ci" in sys.argv:
        sys.exit(1 if failed else 0)
    if not failed:
        print("\n✅ No duplicate【BJJ】prefix detected.")


if __name__ == "__main__":
    main()
