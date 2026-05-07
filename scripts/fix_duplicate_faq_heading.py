#!/usr/bin/env python3
"""
fix_duplicate_faq_heading.py — z255ggg: 3,656 page で FAQ heading が重複
(同 page に <h2>Frequently Asked Questions</h2> が 2 回出現)

旧 silent UX/a11y bug:
- 旧 generator (faq class) + enrichment patch (faq-section class) が両方 FAQ を追加
- 同 heading の section が 2 つ並ぶと user は混乱、screen reader でも違和感
- HTML semantic 的にも duplicate heading は anti-pattern

修正:
- <section class="faq-section"> 内の <h2> を locale 別の「More Questions」相当に rename
  - en: "More Questions"
  - ja: "もっと質問"
  - pt: "Mais Perguntas"
- 元の <div class="faq"> 内の "Frequently Asked Questions" は維持
- idempotent: 既に rename 済 (More Questions 等) は touch しない
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

RENAME_MAP = {
    "en": ("Frequently Asked Questions", "More Questions"),
    "ja": ("よくある質問", "もっと質問"),
    "pt": ("Perguntas Frequentes", "Mais Perguntas"),
}


def patch_page(fp: Path) -> bool:
    html = fp.read_text(encoding="utf-8")
    if "noindex" in html[:1500]:
        return False
    lang = fp.parts[-2]
    if lang not in RENAME_MAP:
        return False
    old, new = RENAME_MAP[lang]

    # Strategy: replace the SECOND occurrence of "<h2...>old</h2>" on the page
    # (ignoring style/class attrs). The 1st occurrence remains unchanged.
    h2_pattern = re.compile(r'(<h2[^>]*>)' + re.escape(old) + r'(</h2>)')
    matches = list(h2_pattern.finditer(html))
    if len(matches) < 2:
        return False
    # Replace only the SECOND match
    second = matches[1]
    new_html = (
        html[:second.start()]
        + second.group(1) + new + second.group(2)
        + html[second.end():]
    )
    fp.write_text(new_html, encoding="utf-8")
    return True


def main():
    print("🔧 fix_duplicate_faq_heading.py — z255ggg")
    fixed = 0
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            if patch_page(fp):
                fixed += 1
    print(f"  ✅ {fixed} pages renamed")


if __name__ == "__main__":
    main()
