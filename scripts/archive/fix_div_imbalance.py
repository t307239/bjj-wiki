#!/usr/bin/env python3
"""
scripts/fix_div_imbalance.py

Wiki HTML の div 開閉タグ不整合を一括修正するスクリプト。

【原因】
  複数スクリプトが同じ CTA フラグメントを重複注入した結果、
  1. 孤立した </div> が余る (ja/pt: negative diff)
  2. container <div> が閉じてない (en: positive diff)
  3. </footer> 後に余分な </div> がある

【使い方】
  python scripts/fix_div_imbalance.py                # 全言語修正
  python scripts/fix_div_imbalance.py --dry-run      # 書き込みなし
  python scripts/fix_div_imbalance.py --lang ja       # 日本語のみ
"""

import re
import sys
from pathlib import Path

WIKI_DIR = Path(__file__).parent.parent

# ──────────────────────────────────────────
# CTA テキストパターン（各言語のorphan CTA検出用）
# ──────────────────────────────────────────
CTA_TEXTS = {
    "ja": "セッション・テクニック・ストリークを無料で管理",
    "pt": "Sessões, técnicas e sequências",
    "en": "Sessions, techniques & streaks",
}

# float-cta の別パターン（旧テンプレート由来）
CTA_ALT_TEXTS = {
    "ja": "セッション・テクニック・ストリーク",
    "pt": "Sessões, técnicas",
    "en": "Track your BJJ",
}


def count_divs(html: str) -> tuple[int, int]:
    opens = len(re.findall(r'<div[\s>]', html))
    closes = len(re.findall(r'</div>', html))
    return opens, closes


def remove_orphan_cta_fragments(html: str, lang: str) -> str:
    """重複注入された CTA フラグメントを除去する。

    パターン:
    1. 単行: <p class="wc-text-tip">...CTA text...</p><a href="...">...</a></div>
    2. 複数行: <p class="wc-text-tip">...CTA text...</p>\n  <a href="...">...</a>\n</div>
    3. 複数行 (onclick付き): <p class="wc-text-tip">...CTA text...</p>\n  <a href="..."\n     style="..."\n     onclick="...">...</a>\n</div>
    4. 壊れたscript: <script>(function(){var s=sessionStorage.getItem('floatShown');...
    """

    # パターン1: 単行 orphan CTA (</div> 付き)
    # <p class="wc-text-tip">...text...</p><a href="https://bjj-app.net/login" ...>...</a></div>
    html = re.sub(
        r'\n?<p class="wc-text-tip">[^<]+</p><a href="https://bjj-app\.net/login"[^>]*>[^<]*</a></div>\n?',
        '\n',
        html
    )

    # パターン2&3: 複数行 orphan CTA (</div> 付き)
    # <p class="wc-text-tip">...text...</p>\n  <a href="...">...</a>\n</div>
    # or with onclick spanning multiple lines
    html = re.sub(
        r'\n?\s*<p class="wc-text-tip">[^<]+</p>\s*\n\s*<a href="https://bjj-app\.net/login"[\s\S]*?</a>\s*\n\s*</div>\n?',
        '\n',
        html
    )

    # パターン: 孤立した <p class="wc-text-tip"> + <a> (</div> なし)
    html = re.sub(
        r'\n?\s*<p class="wc-text-tip">[^<]+</p>\s*\n\s*<a href="https://bjj-app\.net/login"[\s\S]*?</a>\s*\n',
        '\n',
        html
    )

    # パターン4: 壊れた float script
    html = re.sub(
        r'\n?<script>\(function\(\)\{var s=sessionStorage\.getItem\([\'"]floatShown[\'"]\).*?</script>\n?',
        '\n',
        html,
        flags=re.DOTALL
    )

    # pt 特有: orphan <p> + </div> fragments (newsletter text without wrapper)
    # e.g. <p style="...">Dicas de treino...</p>\n\n</div>
    html = re.sub(
        r'\n\s*<p style="[^"]*">[^<]*(?:treino|training|練習)[^<]*</p>\s*\n+\s*</div>\n',
        '\n',
        html
    )

    return html


def remove_orphan_float_cta_content(html: str, lang: str) -> str:
    """<div id="float-cta"> がないのに float-cta のコンテンツだけ
    残っているケースを除去"""

    # float-cta id がない場合のみ orphan コンテンツを除去
    if 'id="float-cta"' in html:
        return html

    # Orphan float-cta style の div (position:fixed;bottom:20px;right:20px)
    # 開閉が正しいものは除去しない（新テンプレートのfloat-cta）

    return html


def fix_missing_container_close(html: str) -> str:
    """container <div> が閉じてない場合、</footer> の前に </div> を追加"""
    opens, closes = count_divs(html)
    diff = opens - closes

    if diff <= 0:
        return html

    # footer の前に不足分の </div> を追加
    footer_match = re.search(r'<footer\b', html)
    if footer_match:
        insert_pos = footer_match.start()
        closing_divs = '</div>\n' * diff
        html = html[:insert_pos] + closing_divs + html[insert_pos:]

    return html


def fix_extra_closing_divs(html: str) -> str:
    """</footer> の直後にある orphan </div> を除去"""
    # </footer>\n</div> パターン
    html = re.sub(
        r'(</footer>)\s*\n(</div>)\s*\n',
        r'\1\n',
        html
    )
    return html


def fix_orphan_closing_divs(html: str) -> str:
    """全体のdiv差がまだ負の場合、depth tracking で
    orphan </div> を特定して除去"""
    opens, closes = count_divs(html)
    diff = opens - closes  # negative = extra closes

    if diff >= 0:
        return html

    # depth tracking で negative になる </div> を除去
    lines = html.split('\n')
    depth = 0
    removals_needed = abs(diff)
    removals_done = 0
    new_lines = []

    for i, line in enumerate(lines):
        o = len(re.findall(r'<div[\s>]', line))
        c = len(re.findall(r'</div>', line))
        new_depth = depth + o - c

        # depth が負になる行で、行が </div> のみ or </div></div> のみの場合
        if new_depth < 0 and removals_done < removals_needed:
            stripped = line.strip()
            if stripped == '</div>':
                # この行は orphan closing div — 除去
                removals_done += 1
                continue  # skip this line
            elif stripped == '</div></div>':
                # 2つの closing div — 必要な分だけ除去
                if removals_needed - removals_done >= 2:
                    removals_done += 2
                    continue
                else:
                    new_lines.append('</div>')
                    removals_done += 1
                    depth = new_depth + 1
                    continue

        depth = new_depth
        new_lines.append(line)

    return '\n'.join(new_lines)


def clean_excessive_blank_lines(html: str) -> str:
    """4行以上の連続空行を2行に圧縮"""
    return re.sub(r'\n{4,}', '\n\n\n', html)


def fix_file(path: Path, lang: str, dry_run: bool = False) -> bool:
    """1ファイルを修正。変更があれば True を返す"""
    html = path.read_text(encoding='utf-8')
    original = html

    # Step 1: orphan CTA fragments を除去
    html = remove_orphan_cta_fragments(html, lang)

    # Step 2: </footer> 後の orphan </div> を除去
    html = fix_extra_closing_divs(html)

    # Step 3: まだ negative diff なら orphan closing divs を除去
    html = fix_orphan_closing_divs(html)

    # Step 4: positive diff なら missing container close を追加
    html = fix_missing_container_close(html)

    # Step 5: 連続空行を圧縮
    html = clean_excessive_blank_lines(html)

    if html == original:
        return False

    if not dry_run:
        path.write_text(html, encoding='utf-8')

    return True


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", default="all")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    langs = ["en", "ja", "pt"] if args.lang == "all" else [args.lang]

    total_fixed = 0
    total_still_broken = 0

    for lang in langs:
        lang_dir = WIKI_DIR / lang
        if not lang_dir.is_dir():
            continue

        lang_fixed = 0
        lang_broken = 0

        for f in sorted(lang_dir.glob('*.html')):
            opens_before, closes_before = count_divs(
                f.read_text(encoding='utf-8')
            )
            diff_before = opens_before - closes_before

            changed = fix_file(f, lang, dry_run=args.dry_run)

            if changed:
                # 修正後のチェック
                if not args.dry_run:
                    html_after = f.read_text(encoding='utf-8')
                    opens_after, closes_after = count_divs(html_after)
                    diff_after = opens_after - closes_after

                    if diff_after != 0:
                        lang_broken += 1
                        if lang_broken <= 3:
                            print(f"  ⚠️  {lang}/{f.name}: {diff_before:+d} → {diff_after:+d} (still broken)")
                    else:
                        lang_fixed += 1
                else:
                    lang_fixed += 1

        marker = " (dry-run)" if args.dry_run else ""
        print(f"[{lang}] {lang_fixed} files fixed, {lang_broken} still broken{marker}")
        total_fixed += lang_fixed
        total_still_broken += lang_broken

    print(f"\n✅ Total: {total_fixed} files fixed, {total_still_broken} still broken")
    if total_still_broken > 0:
        print("  ⚠️  still_broken ファイルは追加パターン対応が必要")


if __name__ == "__main__":
    main()
