#!/usr/bin/env python3
"""
fix_hreflang_drift.py — z255s: hreflang silent drift 修正

検出された 2 class:
  A. x-default hreflang が literal `{slug}` テンプレ未置換 (12 pages = 4 slug × 3 langs)
  B. EN page 3 件で ja hreflang 欠落 (best-bjj-leg-locks / best-bjj-techniques-beginners /
     best-no-gi-techniques)
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]


def fix_class_a():
    """Class A: literal `{slug}` を実際の slug に置換"""
    fixed = 0
    affected_slugs = [
        "bjj-flow-rolling",
        "bjj-private-lessons",
        "bjj-drilling-guide",
        "bjj-open-mat",
    ]
    for lang in LANGS:
        for slug in affected_slugs:
            fp = REPO_ROOT / lang / f"{slug}.html"
            if not fp.exists():
                continue
            html = fp.read_text(encoding="utf-8")
            new = html.replace(
                'hreflang="x-default" href="https://wiki.bjj-app.net/en/{slug}.html"',
                f'hreflang="x-default" href="https://wiki.bjj-app.net/en/{slug}.html"',
            )
            if new != html:
                fp.write_text(new, encoding="utf-8")
                fixed += 1
    return fixed


def fix_class_b():
    """Class B: ja hreflang 欠落 page に追加"""
    fixed = 0
    for slug in [
        "best-bjj-leg-locks",
        "best-bjj-techniques-beginners",
        "best-no-gi-techniques",
    ]:
        fp = REPO_ROOT / "en" / f"{slug}.html"
        if not fp.exists():
            continue
        html = fp.read_text(encoding="utf-8")
        # 既に ja hreflang があれば skip
        if re.search(r'<link\s+rel="alternate"\s+hreflang="ja"', html):
            continue
        # en hreflang line の直後に ja + pt を挿入
        en_pattern = re.compile(
            r'(<link\s+rel="alternate"\s+hreflang="en"\s+href="https://wiki\.bjj-app\.net/en/'
            + re.escape(slug) + r'\.html">)'
        )
        m = en_pattern.search(html)
        if not m:
            continue
        new_tags = (
            f'\n  <link rel="alternate" hreflang="ja" href="https://wiki.bjj-app.net/ja/{slug}.html">'
            f'\n  <link rel="alternate" hreflang="pt" href="https://wiki.bjj-app.net/pt/{slug}.html">'
        )
        # 既に pt hreflang があれば pt は省略
        if re.search(r'<link\s+rel="alternate"\s+hreflang="pt"', html):
            new_tags = (
                f'\n  <link rel="alternate" hreflang="ja" href="https://wiki.bjj-app.net/ja/{slug}.html">'
            )
        new = html[: m.end()] + new_tags + html[m.end():]
        fp.write_text(new, encoding="utf-8")
        fixed += 1
    return fixed


def main():
    print("🔧 fix_hreflang_drift.py — z255s")
    a = fix_class_a()
    print(f"  A. x-default {{slug}} substitution     : {a} files")
    b = fix_class_b()
    print(f"  B. EN page ja hreflang 追加            : {b} files")
    print(f"\n✅ Total fixed: {a + b} files")


if __name__ == "__main__":
    main()
