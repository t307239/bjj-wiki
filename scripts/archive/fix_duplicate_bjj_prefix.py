#!/usr/bin/env python3
"""
fix_duplicate_bjj_prefix.py — z255aaa: 74 JA page で【BJJ】【BJJ】重複 prefix 修正

旧 silent UX bug:
- 74 JA page で h1 / breadcrumb / body 内に【BJJ】【BJJ】等の重複 prefix
- 例: 【BJJ】【BJJ】フォールディングパスガイド (本来「【BJJ】フォールディングパスガイド」)
- 原因: 旧 generator が【BJJ】prefix を自動付与、後続の翻訳 batch も再付与で double-stamp
- 結果: SEO keyword stuffing、見栄え悪化、user 不信感

修正:
- 連続する【BJJ】prefix を 1 個に圧縮 (regex: (【BJJ】){2,} → 【BJJ】)
- h1 / breadcrumb / og:title / title / meta description / body 内全部 sweep
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DUP_PREFIX_RE = re.compile(r'(【BJJ】\s*){2,}')


def patch_page(fp: Path) -> bool:
    html = fp.read_text(encoding="utf-8")
    if "noindex" in html[:1500]:
        return False
    new = DUP_PREFIX_RE.sub('【BJJ】', html)
    if new == html:
        return False
    fp.write_text(new, encoding="utf-8")
    return True


def main():
    print("🔧 fix_duplicate_bjj_prefix.py — z255aaa")
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
