#!/usr/bin/env python3
"""
fix_ui_labels_extended_z255fff.py — Extended UI label patch (WIKI-10 second pass)

z255fff (2026-05-09): The original fix_ui_labels_locale.py handled only the
canonical patterns (`<span class="belt belt-white">White</span>`).
Athlete pages and equipment/drill pages introduced 4 additional patterns
that escape the original regex:

  1. emoji-prefixed belt: `<span class="belt belt-white">🥋 White</span>`
     (~1,100 occurrences, top driver of the 70% drift)
  2. capitalized belt class: `<span class="belt belt-Purple">🥋 Purple</span>`
     (~25 occurrences, athletes with case-sensitive class)
  3. badge with emoji + full belt name: `<span class="badge">🥋 Black Belt</span>`
     (~25 athlete pages)
  4. badge category with emoji prefix: `<span class="badge">🥋 Defense</span>`
     (~3 occurrences)

Idempotent: regex preserves emoji prefix, only replaces the EN word.
EN page is skipped (EN labels are correct).
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Reuse same translation maps as fix_ui_labels_locale.py
BELT_SHORT = {
    "ja": {
        "White": "白", "Blue": "青", "Purple": "紫",
        "Brown": "茶", "Black": "黒",
    },
    "pt": {
        "White": "Branca", "Blue": "Azul", "Purple": "Roxa",
        "Brown": "Marrom", "Black": "Preta",
    },
}

BELT_FULL = {
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

CATEGORY = {
    "ja": {
        "Choke": "絞め技", "Defense": "ディフェンス", "Escape": "エスケープ",
        "Guard": "ガード", "Joint Lock": "関節技", "Leg Lock": "足関節技",
        "Passing": "ガードパス", "Position": "ポジション", "Sweep": "スイープ",
        "Takedown": "テイクダウン", "Transition": "トランジション",
    },
    "pt": {
        "Choke": "Estrangulamento", "Defense": "Defesa", "Escape": "Fuga",
        "Guard": "Guarda", "Joint Lock": "Chave de Articulação",
        "Leg Lock": "Chave de Perna", "Passing": "Passagem de Guarda",
        "Position": "Posição", "Sweep": "Raspagem", "Takedown": "Queda",
        "Transition": "Transição",
    },
}

DIFFICULTY = {
    "ja": {"Beginner": "初級", "Intermediate": "中級", "Advanced": "上級"},
    "pt": {"Beginner": "Iniciante", "Intermediate": "Intermediário", "Advanced": "Avançado"},
}


def patch_page(fp: Path, lang: str) -> int:
    if lang == "en":
        return 0
    html = fp.read_text(encoding="utf-8")
    orig = html
    count = 0

    # Pattern 1: emoji-prefixed belt in `belt belt-X` (lowercase or capitalized class)
    belt_short = BELT_SHORT.get(lang, {})
    for en_belt, native in belt_short.items():
        # `<span class="belt belt-white">🥋 White</span>` (case-insensitive class)
        pattern = rf'(<span class="belt belt-[A-Za-z]+">)((?:[^\w<]+\s*)?){re.escape(en_belt)}(\s*</span>)'
        def make_repl(native_text):
            return lambda m: f'{m.group(1)}{m.group(2)}{native_text}{m.group(3)}'
        html, n = re.subn(pattern, make_repl(native), html)
        count += n

    # Pattern 2: badge with optional emoji + full belt name (athlete pages, with or without emoji)
    belt_full = BELT_FULL.get(lang, {})
    for en_full, native in belt_full.items():
        # Matches: `<span class="badge">Blue Belt</span>` (no emoji)
        #          `<span class="badge">🥋 Blue Belt</span>` (with emoji)
        #          `<span class="badge">🥋 Black <strong>Belt</strong></span>` (strong tag)
        prefix = re.escape(en_full.replace(" Belt", ""))
        pattern = rf'(<span class="badge">)((?:[^\w<]*\s*)?){prefix}\s*(?:<strong>)?Belt(?:</strong>)?(\s*</span>)'
        def make_repl(native_text):
            return lambda m: f'{m.group(1)}{m.group(2)}{native_text}{m.group(3)}'
        html, n = re.subn(pattern, make_repl(native), html)
        count += n

    # Pattern 3: badge category with emoji prefix
    cat_dict = CATEGORY.get(lang, {})
    for en_cat, native in cat_dict.items():
        # `<span class="badge">🥋 Defense</span>` (with emoji)
        pattern = rf'(<span class="badge">)((?:[^\w<]+\s*)){re.escape(en_cat)}(\s*</span>)'
        def make_repl(native_text):
            return lambda m: f'{m.group(1)}{m.group(2)}{native_text}{m.group(3)}'
        html, n = re.subn(pattern, make_repl(native), html)
        count += n

    # Pattern 4: difficulty in <span class="badge"> (uncovered by original)
    diff_dict = DIFFICULTY.get(lang, {})
    for en_diff, native in diff_dict.items():
        # `<span class="badge">Intermediate</span>` (no emoji)
        pattern = rf'(<span class="badge">){re.escape(en_diff)}(</span>)'
        def make_repl(native_text):
            return lambda m: f'{m.group(1)}{native_text}{m.group(2)}'
        html, n = re.subn(pattern, make_repl(native), html)
        count += n

    if html != orig:
        fp.write_text(html, encoding="utf-8")
    return count


def main(dry_run: bool = False) -> int:
    print("🔧 fix_ui_labels_extended_z255fff.py — WIKI-10 extended (4 new patterns)")
    if dry_run:
        print("=== DRY RUN ===")
    total = {"ja": 0, "pt": 0}
    pages = {"ja": 0, "pt": 0}
    for lang in ("ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            if dry_run:
                # In dry-run, restore after counting
                orig = fp.read_text(encoding="utf-8")
                n = patch_page(fp, lang)
                fp.write_text(orig, encoding="utf-8")
            else:
                n = patch_page(fp, lang)
            total[lang] += n
            if n > 0:
                pages[lang] += 1
    for lang in ("ja", "pt"):
        print(f"  {lang}: {total[lang]} replacements across {pages[lang]} pages")
    return 0


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    sys.exit(main(dry_run=dry_run))
