#!/usr/bin/env python3
"""
fix_h2_toc_locale_z255fff.py — Wave H: TOC heading 翻訳

JA: 100 page で「Grips & Mechanics」「⚠️ White Belt Warnings」
    「Drill Progressions」「When to Use & Counters」が EN 残留
PT: ~250 occurrences の EN h2 (Training Recommendations / Training Tips /
    Introduction / Core Concepts 等)

戦略: explicit 翻訳辞書で in-place patch (Gemini 不要、確実)
- h2 tag 本文のみ replace (TOC link 内 anchor text は別途処理)
- entity escape 対応 (`&amp;` → `&`)
- idempotent: 既に native 翻訳されてる場合は触らない
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# JA translations
JA_TRANSLATIONS = {
    "Grips & Mechanics": "グリップとメカニクス",
    "Grips &amp; Mechanics": "グリップとメカニクス",
    "⚠️ White Belt Warnings": "⚠️ 白帯への警告",
    "Drill Progressions": "ドリルの進め方",
    "When to Use & Counters": "使うタイミングとカウンター",
    "When to Use &amp; Counters": "使うタイミングとカウンター",
    "▶ Video Tutorials": "▶ ビデオチュートリアル",
    "Key Concepts": "重要なコンセプト",
    "Related Resources": "関連リソース",
}

# PT translations
PT_TRANSLATIONS = {
    "Training Recommendations": "Recomendações de Treino",
    "Training Tips": "Dicas de Treinamento",
    "Introduction": "Introdução",
    "Core Concepts": "Conceitos Principais",
    "Variations": "Variações",
    "How to Execute": "Como Executar",
    "Counters e Defesa": "Contra-ataques e Defesa",
    "Defesa e Counters": "Defesa e Contra-ataques",
    "Drill Progressions": "Progressão dos Drills",
    "When to Use & Counters": "Quando Usar e Contra-ataques",
    "When to Use &amp; Counters": "Quando Usar e Contra-ataques",
    "Defesas e Counters": "Defesas e Contra-ataques",
    "Key Concepts": "Conceitos-Chave",
    "⚡ Universal Training Tips": "⚡ Dicas Universais de Treinamento",
    "Counters ao Duck Under": "Contra-ataques ao Duck Under",
}


def patch_page(fp: Path, translations: dict) -> int:
    """Replace EN h2 with native version (also updates anchor text in TOC)."""
    html = fp.read_text(encoding="utf-8")
    orig = html
    count = 0

    for en_text, native in translations.items():
        if en_text not in html:
            continue
        # Replace inside <h2 ...>EN</h2>
        h2_pattern = rf'(<h2[^>]*>){re.escape(en_text)}(</h2>)'
        html, n1 = re.subn(h2_pattern, lambda m: m.group(1) + native + m.group(2), html)
        # Replace inside TOC link: <a href="#X">EN</a>
        toc_pattern = rf'(<a href="#[^"]+">){re.escape(en_text)}(</a>)'
        html, n2 = re.subn(toc_pattern, lambda m: m.group(1) + native + m.group(2), html)
        count += n1 + n2

    if html != orig:
        fp.write_text(html, encoding="utf-8")
    return count


def main(dry_run: bool = False) -> int:
    print("🔧 fix_h2_toc_locale_z255fff.py — Wave H (TOC heading translation)")
    if dry_run:
        print("=== DRY RUN (no writes) ===")

    total = {"ja": 0, "pt": 0}
    pages = {"ja": 0, "pt": 0}

    for lang, translations in [("ja", JA_TRANSLATIONS), ("pt", PT_TRANSLATIONS)]:
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            if dry_run:
                orig = fp.read_text(encoding="utf-8")
                n = patch_page(fp, translations)
                fp.write_text(orig, encoding="utf-8")
            else:
                n = patch_page(fp, translations)
            total[lang] += n
            if n > 0:
                pages[lang] += 1

    for lang in ("ja", "pt"):
        print(f"  {lang}: {total[lang]} replacements across {pages[lang]} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main(dry_run="--dry-run" in sys.argv))
