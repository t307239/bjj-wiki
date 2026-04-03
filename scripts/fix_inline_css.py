#!/usr/bin/env python3
"""
fix_inline_css.py — インラインCSS→クラス参照に置換

処理内容:
  1. 頻出インラインstyle属性を対応するCSSクラスに置換
  2. wiki-components.css の <link> を <head> に追加
  3. ページサイズ削減とキャッシュ効率化

使い方:
    python3 scripts/fix_inline_css.py --dry-run     # プレビュー
    python3 scripts/fix_inline_css.py               # 実行
    python3 scripts/fix_inline_css.py --lang en      # ENのみ

依存: Python 3.8+ 標準ライブラリのみ
"""

import re
import argparse
from pathlib import Path

WIKI_ROOT = Path(__file__).parent.parent
LANGUAGES = ["en", "ja"]

# ─────────────────────────────────────────────────────
# インラインstyle → class マッピング
# ─────────────────────────────────────────────────────
# key: 正規化したstyle文字列（末尾セミコロンなし、スペース除去）
# value: 置換先クラス名

STYLE_TO_CLASS = {
    # タグ
    "display:inline-block;margin:4px;padding:6px 14px;background:#141926;border:1px solid #1e293b;border-radius:20px;color:#90caf9;font-size:.8rem;text-decoration:none;transition:all .2s": "wc-tag",

    # PRO バッジ
    "display:inline-block;font-size:.6rem;font-weight:700;background:#7c3aed;color:#fff;border-radius:4px;padding:2px 6px;margin-left:6px;vertical-align:middle": "wc-pro-badge",

    # フッター
    "margin:40px 0 0;padding:20px 16px;border-top:1px solid #1a2a3a;text-align:center": "wc-footer",
    "color:#546e7a;font-size:.72rem;line-height:1.6;max-width:600px;margin:0 auto": "wc-footer-text",

    # カード — Tip (green)
    "margin-bottom:16px;padding:14px 16px;background:#0a1a0a;border-left:3px solid #16a34a;border-radius:8px": "wc-card-tip",
    "color:#86efac;font-size:0.95rem;font-weight:700;margin-bottom:6px": "wc-card-tip-title",

    # カード — Warning (red)
    "margin-bottom:16px;padding:14px 16px;background:#1a0a0a;border-left:3px solid #dc2626;border-radius:8px": "wc-card-warn",
    "color:#fca5a5;font-size:0.95rem;font-weight:700;margin-bottom:6px": "wc-card-warn-title",

    # カード — Info (blue/neutral)
    "margin-bottom:16px;padding:14px 16px;background:#0d1b2a;border:1px solid #1e2a3a;border-radius:8px": "wc-card-info",
    "color:#e2e8f0;font-size:0.95rem;font-weight:700;margin-bottom:6px": "wc-card-info-title",

    # セクション
    "margin:32px 0": "wc-section-divider",
    "margin:32px 0 16px;padding:20px;background:#0c1220;border:1px solid #1e293b;border-radius:16px": "wc-section-box",
    "color:#a5b4fc;font-size:1rem;margin:0 0 12px;font-weight:700": "wc-section-box-title",
    "display:flex;flex-wrap:wrap;gap:0": "wc-section-box-grid",

    # テキスト
    "color:#9ca3af;font-size:0.9rem;margin:0": "wc-muted",
    "color:#9ca3af;font-size:0.9rem;margin-bottom:8px;padding-left:4px": "wc-muted-mb8",
    "color:#9ca3af;font-size:0.9rem;margin-bottom:12px": "wc-muted-mb12",
    "color:#9ca3af;font-size:.9rem;margin-bottom:16px": "wc-muted-mb16",
    "color:#9ca3af;text-decoration:none": "wc-link-muted",
    "color:#64b5f6;text-decoration:none;font-size:.85rem": "wc-link-blue",
    "font-size:.8rem;color:#c8e6c9;margin:0 0 12px": "wc-text-tip",
    "margin-bottom:16px": "wc-mb16",

    # ヘディング
    "color:#e2e8f0;font-size:1.2rem;font-weight:800;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid #1a2a3a": "wc-heading-section",

    # CTA
    "display:block;background:#10B981;color:#fff;padding:8px 16px;border-radius:8px;text-decoration:none;font-weight:600;font-size:.85rem;text-align:center;transition:background .2s": "wc-cta-primary",

    # ピラーページ
    "font-size:.75rem;font-weight:700;color:#546e7a;letter-spacing:.1em;text-transform:uppercase;margin-bottom:10px": "wc-pillar-subtitle",
    "display:flex;flex-direction:column;gap:6px": "wc-pillar-list",
}


def normalize_style(style: str) -> str:
    """スタイル文字列を正規化（比較用）"""
    # 末尾セミコロン除去、余計なスペース除去
    s = style.strip().rstrip(';').strip()
    # プロパティ間のスペースを統一
    s = re.sub(r'\s*;\s*', ';', s)
    s = re.sub(r'\s*:\s*', ':', s)
    return s


def build_lookup():
    """正規化済みのルックアップテーブルを構築"""
    lookup = {}
    for style, cls in STYLE_TO_CLASS.items():
        normalized = normalize_style(style)
        lookup[normalized] = cls
    return lookup


CSS_LINK_TAG = '<link rel="stylesheet" href="/wiki-components.css">'


def process_file(filepath: Path, lookup: dict, dry_run: bool = False) -> dict:
    """1ファイル処理"""
    html = filepath.read_text(encoding='utf-8')
    original_len = len(html)
    replacements = 0

    # style="..." を見つけて置換
    def replace_style(match):
        nonlocal replacements
        full_match = match.group(0)  # style="..."
        style_value = match.group(1)  # ... の中身
        normalized = normalize_style(style_value)

        if normalized in lookup:
            cls = lookup[normalized]
            replacements += 1
            # 既存のclass属性があるか確認
            # タグ全体を取得するのは複雑なので、style属性をclass属性に差し替え
            return f'class="{cls}"'
        return full_match

    new_html = re.sub(r'style="([^"]*)"', replace_style, html)

    # wiki-components.css の link タグを追加（まだない場合）
    if replacements > 0 and 'wiki-components.css' not in new_html:
        # <style> タグの直前または </head> の前に挿入
        style_pos = new_html.find('<style>')
        if style_pos > 0:
            new_html = new_html[:style_pos] + CSS_LINK_TAG + '\n' + new_html[style_pos:]
        else:
            head_end = new_html.find('</head>')
            if head_end > 0:
                new_html = new_html[:head_end] + CSS_LINK_TAG + '\n' + new_html[head_end:]

    if not dry_run and replacements > 0:
        filepath.write_text(new_html, encoding='utf-8')

    return {
        "file": filepath.name,
        "replacements": replacements,
        "saved_bytes": original_len - len(new_html) if replacements > 0 else 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Fix Wiki Inline CSS")
    parser.add_argument("--dry-run", action="store_true", help="変更を加えずにプレビューのみ")
    parser.add_argument("--lang", choices=["en", "ja", "pt"], help="特定言語のみ処理")
    args = parser.parse_args()

    langs = [args.lang] if args.lang else LANGUAGES
    lookup = build_lookup()

    print(f"\n{'='*60}")
    print(f"🎨 Inline CSS Fix — {'DRY RUN' if args.dry_run else 'APPLYING'}")
    print(f"{'='*60}")
    print(f"  マッピングルール: {len(lookup)} パターン")

    total_replacements = 0
    total_saved = 0
    files_modified = 0

    for lang in langs:
        lang_dir = WIKI_ROOT / lang
        if not lang_dir.exists():
            continue

        lang_replacements = 0
        lang_saved = 0
        lang_files = 0

        for fpath in sorted(lang_dir.glob('*.html')):
            result = process_file(fpath, lookup, args.dry_run)
            if result["replacements"] > 0:
                lang_replacements += result["replacements"]
                lang_saved += result["saved_bytes"]
                lang_files += 1

        total_replacements += lang_replacements
        total_saved += lang_saved
        files_modified += lang_files
        print(f"  [{lang.upper()}] {lang_files} ファイル修正、{lang_replacements} style→class置換、{lang_saved//1024}KB削減")

    print(f"\n  合計: {files_modified} ファイル、{total_replacements} 置換、{total_saved//1024}KB削減")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
