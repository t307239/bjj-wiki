#!/usr/bin/env python3
"""
fix_index_chip_labels_z255fff.py — WIKI-9: ja/index.html and pt/index.html chip labels translation

Strategy:
  - Category headings (h2): use templates/messages/<lang>.yml category_label
  - Technique chip text: extract from each ja/<tech>.html or pt/<tech>.html h1, strip suffix
  - No Gemini API call needed (faster + uses existing authentic translations)
"""
import re
import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Suffix patterns to strip from h1/title to get clean tech name
SUFFIX_PATTERNS = [
    r"[:：]\s*BJJ.*$",
    r"[:：]\s*白帯.*$",
    r"[:：]\s*初心者.*$",
    r"[:：]\s*完全ガイド.*$",
    r"[:：]\s*Guia.*$",
    r"[:：]\s*Faixa.*$",
    r"\s+BJJ$",
    r"\s+no\s+BJJ.*$",
    r"\s+no\s+Jiu-Jitsu.*$",
    r"\s*\|\s*BJJ.*$",
    r"^🔁\s*",
    r"^🥋\s*",
    r"\s*\(.*\)$",
]


def get_h1(html_path: Path) -> str | None:
    if not html_path.exists():
        return None
    try:
        html = html_path.read_text(encoding="utf-8")
    except Exception:
        return None
    m = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
    return m.group(1).strip() if m else None


def clean_chip_label(text: str) -> str:
    text = text.strip()
    for pat in SUFFIX_PATTERNS:
        text = re.sub(pat, "", text)
    return text.strip()


def load_category_labels(lang: str) -> dict:
    fp = REPO_ROOT / "templates" / "messages" / f"{lang}.yml"
    with fp.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("category_label", {})


def fix_index(lang: str, dry_run: bool = False) -> int:
    """Fix chip labels in <lang>/index.html"""
    index_path = REPO_ROOT / lang / "index.html"
    if not index_path.exists():
        print(f"❌ {index_path} not found")
        return 0

    html = index_path.read_text(encoding="utf-8")
    original_html = html

    # Step 1: Translate category headings (h2)
    cat_labels = load_category_labels(lang)
    cat_replacements = 0
    for en_cat, lang_cat in cat_labels.items():
        # Match `<h2>Choke</h2>` style
        old = f"<h2>{en_cat}</h2>"
        new = f"<h2>{lang_cat}</h2>"
        if old in html and old != new:
            html = html.replace(old, new)
            cat_replacements += 1

    # Step 2: Translate technique chip labels
    chip_replacements = 0
    chip_skipped = 0
    chip_pattern = re.compile(r'(<a href="([^"]+\.html)">)([^<]+)(</a>)')

    def replace_chip(m):
        nonlocal chip_replacements, chip_skipped
        prefix, target_html, en_label, suffix = m.groups()
        target_path = REPO_ROOT / lang / target_html
        translated_h1 = get_h1(target_path)
        if translated_h1:
            clean = clean_chip_label(translated_h1)
            if clean and clean != en_label.strip():
                chip_replacements += 1
                return f"{prefix}{clean}{suffix}"
        chip_skipped += 1
        return m.group(0)

    html = chip_pattern.sub(replace_chip, html)

    if html == original_html:
        print(f"⏭️  {lang}/index.html: no changes needed")
        return 0

    if not dry_run:
        index_path.write_text(html, encoding="utf-8")
    print(f"✅ {lang}/index.html: cat={cat_replacements} chip={chip_replacements} skipped={chip_skipped}")
    return chip_replacements + cat_replacements


def main(dry_run: bool = False) -> int:
    total = 0
    for lang in ["ja", "pt"]:
        total += fix_index(lang, dry_run=dry_run)
    print(f"\nTotal replacements: {total}")
    return 0


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("=== DRY RUN ===")
    sys.exit(main(dry_run=dry_run))
