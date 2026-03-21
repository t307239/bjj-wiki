#!/usr/bin/env python3
"""
BJJ Wiki — YouTube ボタン削除 + Gear 404リンク修正

1. YouTube: 赤いピル型ボタンを完全削除（検索結果一覧表示のみならボタン不要）
2. YouTube: CSSスタイル定義も削除
3. Gear: ../../gear/*.html の404リンクを削除（実在しないページ）
"""
import os
import re

WIKI_ROOT = os.path.join(os.path.dirname(__file__), "..")
LANGS = ["en", "ja", "pt"]

yt_removed = 0
gear_removed = 0
css_removed = 0

for lang in LANGS:
    langdir = os.path.join(WIKI_ROOT, lang)
    if not os.path.isdir(langdir):
        continue
    for fname in os.listdir(langdir):
        if not fname.endswith(".html"):
            continue
        fpath = os.path.join(langdir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        original = content
        had_yt = "yt-search-btn" in content
        had_gear = "../../gear/" in content

        # 1. Remove YouTube anchor (various wrappers)
        # With div wrapper
        content = re.sub(
            r'<div[^>]*>\s*<a\s[^>]*class="yt-search-btn"[^>]*>.*?</a>\s*</div>\s*',
            '',
            content,
            flags=re.DOTALL
        )
        # Bare anchor (no div wrapper) — on its own line
        content = re.sub(
            r'\s*<a\s[^>]*class="yt-search-btn"[^>]*>.*?</a>\s*',
            '\n',
            content,
            flags=re.DOTALL
        )

        # 2. Remove YouTube CSS styles
        content = re.sub(
            r'\s*\.yt-search-btn\s*\{[^}]*\}\s*',
            '\n',
            content
        )
        content = re.sub(
            r'\s*\.yt-search-btn:hover\s*\{[^}]*\}\s*',
            '\n',
            content
        )
        content = re.sub(
            r'\s*\.yt-search-btn\s+svg\s*\{[^}]*\}\s*',
            '\n',
            content
        )

        # 3. Remove gear 404 links (keep surrounding text)
        content = re.sub(
            r'<a\s+href="\.\./\.\./gear/[^"]*\.html"[^>]*>(.*?)</a>',
            r'\1',
            content,
            flags=re.DOTALL
        )

        if content != original:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            if had_yt and "yt-search-btn" not in content:
                yt_removed += 1
            if had_gear and "../../gear/" not in content:
                gear_removed += 1

print(f"YouTube buttons+CSS removed: {yt_removed} pages")
print(f"Gear 404 links removed: {gear_removed} pages")
