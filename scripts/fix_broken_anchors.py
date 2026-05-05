#!/usr/bin/env python3
"""
fix_broken_anchors.py — z255z: TOC `<a href="#tips">` etc. が anchor 不在で
スクロール失敗していた silent UX bug を修正.

検出された 2 class:
  A. #tips (20 件 = 7 slug × 3 langs - 1 既存): TOC link 存在するが
     `<div class="tips-box">` に id 属性無し
  B. #control (2 件): ja/crucifix.html, pt/crucifix.html で TOC link 存在するが
     対応 section が翻訳時に skip されていた

Class A 修正: <div class="tips-box"> → <div id="tips" class="tips-box">
Class B 修正: TOC li を削除 (該当 section の翻訳追加は scope 外)
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]


def fix_class_a():
    """Class A: tips-box に id="tips" を追加"""
    fixed = 0
    slugs = [
        "bicep-slicer", "cement-mixer", "crucifix", "imanari-roll",
        "paper-cutter-choke", "peruvian-necktie", "quarter-guard",
    ]
    for slug in slugs:
        for lang in LANGS:
            fp = REPO_ROOT / lang / f"{slug}.html"
            if not fp.exists():
                continue
            html = fp.read_text(encoding="utf-8")
            # 既に id="tips" あれば skip (idempotent)
            if 'id="tips"' in html:
                continue
            # `<div class="tips-box">` → `<div id="tips" class="tips-box">`
            new = re.sub(
                r'<div\s+class="tips-box">',
                '<div id="tips" class="tips-box">',
                html,
                count=1,
            )
            if new != html:
                fp.write_text(new, encoding="utf-8")
                fixed += 1
    return fixed


def fix_class_b():
    """Class B: ja/pt crucifix.html の dead #control TOC link を削除"""
    fixed = 0
    for lang in ("ja", "pt"):
        fp = REPO_ROOT / lang / "crucifix.html"
        if not fp.exists():
            continue
        html = fp.read_text(encoding="utf-8")
        # 既に id="control" あれば skip
        if 'id="control"' in html:
            continue
        # TOC li with #control (1 line) を削除
        new = re.sub(
            r'\s*<li><a\s+href="#control">[^<]+</a></li>\s*\n',
            "\n",
            html,
            count=1,
        )
        if new != html:
            fp.write_text(new, encoding="utf-8")
            fixed += 1
    return fixed


def main():
    print("🔧 fix_broken_anchors.py — z255z")
    a = fix_class_a()
    print(f"  A. tips-box id 追加        : {a} files")
    b = fix_class_b()
    print(f"  B. dead #control TOC 削除 : {b} files")
    print(f"\n✅ Total fixed: {a + b} files")


if __name__ == "__main__":
    main()
