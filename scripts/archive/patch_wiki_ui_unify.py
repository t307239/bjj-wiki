#!/usr/bin/env python3
"""
patch_wiki_ui_unify.py — BJJ Wiki UI統一パッチ (Phase 2)

対象:
  1. CSSカスタムプロパティ未使用ページ → :root デザイントークン注入
  2. 旧 lang-switcher ナビ → 現行 lang-nav スタイルに統一
  3. 旧ダブルヘッダー構造 → 外側の重複ヘッダーを除去
  4. フッターテキストの統一

実行: python3 scripts/patch_wiki_ui_unify.py
"""

import os
import re
import glob

WIKI_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LANGS = ["en", "ja", "pt"]

# ── 新デザインシステム CSS :root ────────────────────────────────────────────
DESIGN_TOKENS = """:root{--bg:#0f172a;--card:#18181b;--card-hover:#1c1c22;--border:rgba(255,255,255,0.10);--border-hover:rgba(124,58,237,0.5);--text:#e2e8f0;--muted:#64748b;--accent:#7c3aed;--accent2:#e94560}"""

# ── 旧ハードコードカラー → CSS変数置換マップ ────────────────────────────────
HARDCODE_REPLACEMENTS = [
    (r'background:\s*#0f172a\b', 'background:var(--bg)'),
    (r'background:\s*#18181b\b', 'background:var(--card)'),
    (r'background:\s*#1c1c22\b', 'background:var(--card-hover)'),
    (r'color:\s*#e2e8f0\b',      'color:var(--text)'),
    (r'color:\s*#64748b\b',      'color:var(--muted)'),
    (r'color:\s*#7c3aed\b',      'color:var(--accent)'),
    (r'color:\s*#7c6af7\b',      'color:var(--accent)'),
    (r'color:\s*#e94560\b',      'color:var(--accent2)'),
    (r'border-color:\s*rgba\(255,255,255,0\.1[0]?\)', 'border-color:var(--border)'),
]

# ── 旧 lang-switcher → lang-nav 変換 ────────────────────────────────────────
def replace_lang_switcher(content: str, lang: str, slug: str) -> str:
    """
    旧パターン:
      <div class="lang-switcher"><a href="../ja/slug.html">日本語</a> | <a href="../pt/slug.html">Português</a></div>
    新パターン (lang-nav スタイルに統一):
      <nav class="lang-nav">...</nav>
    """
    # lang-switcher が既にない場合はスキップ
    if 'class="lang-switcher"' not in content:
        return content

    # 言語ラベルのマッピング
    lang_labels = {
        "en": ("🇺🇸 EN", "🇯🇵 JA", "🇧🇷 PT"),
        "ja": ("🇺🇸 EN", "🇯🇵 JA", "🇧🇷 PT"),
        "pt": ("🇺🇸 EN", "🇯🇵 JA", "🇧🇷 PT"),
    }
    en_lbl, ja_lbl, pt_lbl = lang_labels[lang]

    en_active = 'class="active"' if lang == "en" else ""
    ja_active = 'class="active"' if lang == "ja" else ""
    pt_active = 'class="active"' if lang == "pt" else ""

    new_nav = (
        f'<nav class="lang-nav">'
        f'<a href="../en/{slug}.html" {en_active}>{en_lbl}</a>'
        f'<a href="../ja/{slug}.html" {ja_active}>{ja_lbl}</a>'
        f'<a href="../pt/{slug}.html" {pt_active}>{pt_lbl}</a>'
        f'</nav>'
    )

    # 旧 lang-switcher div を新 lang-nav に置換
    content = re.sub(
        r'<div class="lang-switcher">.*?</div>',
        new_nav,
        content,
        flags=re.DOTALL
    )
    return content


def remove_double_header(content: str) -> str:
    """
    旧ページにある内側の重複 <header> ブロック（旧ロゴ + 旧ナビ）を除去。
    外側の <header> (新構造) は保持する。
    パターン:
      <header>
        <a href="../en/index.html" class="logo">🥋 BJJ Wiki</a>
        <nav class="lang-nav">...</nav>
      </header>
      <header>  ← この内側の古いヘッダーを除去
        <a href="../index.html" class="logo">BJJ<span>Wiki</span></a>
        <nav>...</nav>
      </header>
    """
    # 内側の古いヘッダーパターン: BJJ<span>Wiki</span> を含む <header> ブロック
    content = re.sub(
        r'<header>\s*<a href=["\'][^"\']*index\.html["\'] class="logo">BJJ<span>Wiki</span></a>.*?</header>',
        '',
        content,
        flags=re.DOTALL
    )
    return content


def ensure_design_tokens(content: str) -> str:
    """
    CSS :root ブロックが未定義のページにデザイントークンを注入。
    """
    if 'var(--bg)' in content:
        return content  # 既にCSS変数使用済み

    # <style> タグの先頭に :root を注入
    if '<style>' in content:
        content = content.replace('<style>', f'<style>\n  {DESIGN_TOKENS}\n', 1)
    elif '<style ' in content:
        # <style type="text/css"> 等のケース
        content = re.sub(r'<style([^>]*)>', f'<style\\1>\\n  {DESIGN_TOKENS}\\n', content, count=1)

    return content


def patch_hardcoded_colors(content: str) -> str:
    """ハードコードされた色をCSS変数に置換（CSS内のみ）。"""
    # <style>...</style> ブロック内だけを対象にする
    def patch_style_block(match):
        block = match.group(0)
        for pattern, replacement in HARDCODE_REPLACEMENTS:
            block = re.sub(pattern, replacement, block)
        return block

    content = re.sub(r'<style[^>]*>.*?</style>', patch_style_block, content, flags=re.DOTALL)
    return content


def patch_file(path: str, lang: str) -> tuple[bool, str]:
    """
    1ファイルをパッチ。
    Returns: (modified: bool, reason: str)
    """
    with open(path, encoding='utf-8') as f:
        original = f.read()

    slug = os.path.splitext(os.path.basename(path))[0]
    content = original

    # 1. CSS変数注入
    content = ensure_design_tokens(content)

    # 2. ハードコードカラー → CSS変数
    content = patch_hardcoded_colors(content)

    # 3. lang-switcher → lang-nav
    content = replace_lang_switcher(content, lang, slug)

    # 4. ダブルヘッダー除去
    content = remove_double_header(content)

    if content == original:
        return False, "no change"

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True, "patched"


def main():
    total_patched = 0
    total_skipped = 0

    for lang in LANGS:
        lang_dir = os.path.join(WIKI_ROOT, lang)
        if not os.path.isdir(lang_dir):
            print(f"[SKIP] {lang_dir} not found")
            continue

        html_files = sorted(glob.glob(os.path.join(lang_dir, "*.html")))
        content_files = [f for f in html_files if os.path.basename(f) != "index.html"]

        patched = 0
        skipped = 0

        for path in content_files:
            modified, reason = patch_file(path, lang)
            if modified:
                patched += 1
            else:
                skipped += 1

        print(f"[{lang.upper()}] patched={patched}, skipped(no change)={skipped}, total={len(content_files)}")
        total_patched += patched
        total_skipped += skipped

    print(f"\n✅ Done — Total patched: {total_patched}, skipped: {total_skipped}")


if __name__ == "__main__":
    main()
