#!/usr/bin/env python3
"""
fix_ui_labels_locale.py — z255uu (WIKI-10): JA/PT page の category/belt/difficulty
UI label を locale 翻訳

旧: 1,185 JA + 1,305 PT page で UI label が EN 残留
  - <span class="badge">Joint Lock</span> → 関節技
  - <span class="belt belt-white">White</span> → 白帯
  - <span class="diff-belt">BLUE</span> → 青
  - <span class="diff-label">Intermediate</span> → 中級

idempotent: class 名で marker、replacement も unicode-aware regex で精密 match。
EN page は対象外 (EN label が正解)。
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Category translations (CLAUDE.md Layer 1: BJJ 専門用語、コミュニティ標準カタカナ採用)
CATEGORY = {
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
        "Choke": "Estrangulamento",
        "Defense": "Defesa",
        "Escape": "Fuga",
        "Guard": "Guarda",
        "Joint Lock": "Chave de Articulação",
        "Leg Lock": "Chave de Perna",
        "Passing": "Passagem de Guarda",
        "Position": "Posição",
        "Sweep": "Raspagem",
        "Takedown": "Queda",
        "Transition": "Transição",
    },
}

# Belt translations
BELT = {
    "ja": {
        "White": "白帯", "Blue": "青帯", "Purple": "紫帯",
        "Brown": "茶帯", "Black": "黒帯",
        "WHITE": "白", "BLUE": "青", "PURPLE": "紫", "BROWN": "茶", "BLACK": "黒",
    },
    "pt": {
        "White": "Faixa Branca", "Blue": "Faixa Azul", "Purple": "Faixa Roxa",
        "Brown": "Faixa Marrom", "Black": "Faixa Preta",
        "WHITE": "BRANCA", "BLUE": "AZUL", "PURPLE": "ROXA", "BROWN": "MARROM", "BLACK": "PRETA",
    },
}

# Difficulty translations
DIFFICULTY = {
    "ja": {
        "Beginner": "初級", "Intermediate": "中級", "Advanced": "上級",
    },
    "pt": {
        "Beginner": "Iniciante", "Intermediate": "Intermediário", "Advanced": "Avançado",
    },
}


def patch_page(fp: Path, lang: str) -> int:
    """Returns count of replacements made."""
    if lang == "en":
        return 0
    html = fp.read_text(encoding="utf-8")
    orig = html
    count = 0

    # 1. <span class="badge">CATEGORY</span>
    cat_dict = CATEGORY.get(lang, {})
    for en_cat, native in cat_dict.items():
        pattern = rf'(<span class="badge">){re.escape(en_cat)}(</span>)'
        def make_replacer(t: str):
            return lambda m: m.group(1) + t + m.group(2)
        html, n = re.subn(pattern, make_replacer(native), html)
        count += n

    # 2. <span class="belt belt-X">BELT</span>
    belt_dict = BELT.get(lang, {})
    for en_belt, native in belt_dict.items():
        # Title case (White) — used in <span class="belt belt-white">White</span>
        pattern = rf'(<span class="belt belt-[a-z]+">){re.escape(en_belt)}(</span>)'
        def make_replacer(t: str):
            return lambda m: m.group(1) + t + m.group(2)
        html, n = re.subn(pattern, make_replacer(native), html)
        count += n

    # 3. <span class="diff-belt" style="...">BELT_UPPER</span>
    for en_belt, native in belt_dict.items():
        # Upper case (BLUE) — used in difficulty bar
        pattern = rf'(<span class="diff-belt"[^>]*>){re.escape(en_belt)}(</span>)'
        def make_replacer(t: str):
            return lambda m: m.group(1) + t + m.group(2)
        html, n = re.subn(pattern, make_replacer(native), html)
        count += n

    # 4. <span class="diff-label">DIFFICULTY</span>
    diff_dict = DIFFICULTY.get(lang, {})
    for en_diff, native in diff_dict.items():
        pattern = rf'(<span class="diff-label">){re.escape(en_diff)}(</span>)'
        def make_replacer(t: str):
            return lambda m: m.group(1) + t + m.group(2)
        html, n = re.subn(pattern, make_replacer(native), html)
        count += n

    # 5. <span class="belt-tag" ...>🥋 Blue Belt</span> — separate pattern with emoji prefix
    BELT_FULL_NAMES = {
        "ja": {
            "White Belt": "白帯", "Blue Belt": "青帯", "Purple Belt": "紫帯",
            "Brown Belt": "茶帯", "Black Belt": "黒帯",
        },
        "pt": {
            "White Belt": "Faixa Branca", "Blue Belt": "Faixa Azul",
            "Purple Belt": "Faixa Roxa", "Brown Belt": "Faixa Marrom",
            "Black Belt": "Faixa Preta",
        },
    }
    belt_full = BELT_FULL_NAMES.get(lang, {})
    for en_full, native in belt_full.items():
        # Allow optional emoji prefix (e.g. "🥋 Blue Belt", "🟣 Purple Belt")
        pattern = rf'(<span class="belt-tag"[^>]*>(?:[^\w<]*\s*)?){re.escape(en_full)}(</span>)'
        def make_replacer(t: str):
            return lambda m: m.group(1) + t + m.group(2)
        html, n = re.subn(pattern, make_replacer(native), html)
        count += n

    if html != orig:
        fp.write_text(html, encoding="utf-8")
    return count


def main():
    print("🔧 fix_ui_labels_locale.py — z255uu (WIKI-10)")
    total = {"ja": 0, "pt": 0}
    pages = {"ja": 0, "pt": 0}
    for lang in ("ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            n = patch_page(fp, lang)
            total[lang] += n
            if n > 0:
                pages[lang] += 1
    for lang in ("ja", "pt"):
        print(f"  {lang}: {total[lang]} replacements across {pages[lang]} pages")


if __name__ == "__main__":
    main()
