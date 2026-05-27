#!/usr/bin/env python3
"""
fix_index_design_drift.py — z255rr: en/ja/pt/index.html を技術 page と同 design に
統一 (言語スイッチャー追加 + カテゴリ heading 翻訳).

旧: index.html だけ logo のみで language switcher / breadcrumb 不在 →
    技 page (e.g. armbar.html) には EN/JA/PT switcher あるのに index は
    取り残されて UI 不整合。

修正:
  1. <header> に <div class="lang-switcher"> 追加 (active locale 強調)
  2. <h2>Choke</h2> 等の category heading を locale 別 翻訳
     (chip labels = 技名 EN は WIKI-9 candidate で defer、index は heading のみ)
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Category JA/PT translations (英語 heading そのまま EN は維持)
CATEGORY_TRANSLATIONS = {
    "ja": {
        "Choke": "絞め技",
        "Defense": "ディフェンス",
        "Escape": "エスケープ",
        "Guard": "ガード",
        "Joint Lock": "関節技",
        "Leg Lock": "足関節技",
        "Passing": "ガードパス",
        "Position": "ポジション",
        "Sweep": "スイープ",
        "Takedown": "テイクダウン",
        "Transition": "トランジション",
    },
    "pt": {
        "Choke": "Estrangulamentos",
        "Defense": "Defesa",
        "Escape": "Fugas",
        "Guard": "Guarda",
        "Joint Lock": "Chave de Articulação",
        "Leg Lock": "Chave de Perna",
        "Passing": "Passagem de Guarda",
        "Position": "Posições",
        "Sweep": "Raspagens",
        "Takedown": "Quedas",
        "Transition": "Transições",
    },
}


def build_lang_switcher(active: str) -> str:
    """Use existing .lang-nav class (defined in wiki-v2.css line 50-52)
    matching individual technique pages' language switcher style."""
    items = []
    for code, label in [("en", "🇺🇸 EN"), ("ja", "🇯🇵 JA"), ("pt", "🇧🇷 PT")]:
        active_class = ' class="active"' if code == active else ""
        items.append(f'<a href="../{code}/index.html"{active_class}>{label}</a>')
    return (
        '<nav class="lang-nav" aria-label="Language">'
        + "".join(items)
        + "</nav>"
    )


def patch_index(lang: str):
    fp = REPO_ROOT / lang / "index.html"
    if not fp.exists():
        print(f"  ⚠️  {lang}/index.html not found")
        return False
    html = fp.read_text(encoding="utf-8")

    # 1. Add language switcher to header (idempotent)
    if 'class="lang-nav"' not in html:
        switcher = build_lang_switcher(lang)
        # Insert before </header>
        new = re.sub(
            r'(<header><a href="\.\./index\.html" class="logo">BJJ<span>Wiki</span></a>)(</header>)',
            rf'\1{switcher}\2',
            html,
            count=1,
        )
        if new != html:
            html = new
        else:
            print(f"  ⚠️  {lang}: header pattern not matched")

    # 2. Translate category headings (only for ja/pt)
    if lang in CATEGORY_TRANSLATIONS:
        trans = CATEGORY_TRANSLATIONS[lang]
        for en, native in trans.items():
            # <h2>Choke</h2> → <h2>絞め技</h2>
            html = html.replace(f"<h2>{en}</h2>", f"<h2>{native}</h2>")

    fp.write_text(html, encoding="utf-8")
    return True


def main():
    print("🔧 fix_index_design_drift.py — z255rr")
    fixed = 0
    for lang in ["en", "ja", "pt"]:
        if patch_index(lang):
            print(f"  ✅ {lang}/index.html")
            fixed += 1
    print(f"\n✅ Fixed {fixed} index pages")


if __name__ == "__main__":
    main()
