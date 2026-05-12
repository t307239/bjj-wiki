#!/usr/bin/env python3
"""
check_duplicate_related_techniques.py — z255jjjj-WW: dedup lint

Detects pages with 2+ "Related Techniques" h2 (visible duplicate sections).
Caused by injection scripts that don't check for pre-existing headings.

--ci flag → exit 1 if any page has duplicate.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

# Per-locale patterns. We treat each heading TEXT independently — having
# "Related Techniques" + "Related Guides" on the same page is fine (distinct
# sections). Only flag when the SAME heading text appears 2+ times.
PER_TEXT_PATTERNS = {
    "en": [
        re.compile(r'<h2[^>]*>\s*Related Techniques\s*</h2>', re.IGNORECASE),
        re.compile(r'<h2[^>]*>\s*Related Guides\s*</h2>', re.IGNORECASE),
        re.compile(r'<h2[^>]*>\s*Related Articles\s*</h2>', re.IGNORECASE),
    ],
    "ja": [
        re.compile(r'<h2[^>]*>\s*関連テクニック\s*</h2>'),
        re.compile(r'<h2[^>]*>\s*関連ガイド\s*</h2>'),
        re.compile(r'<h2[^>]*>\s*関連記事\s*</h2>'),
    ],
    "pt": [
        re.compile(r'<h2[^>]*>\s*Técnicas Relacionadas\s*</h2>', re.IGNORECASE),
        re.compile(r'<h2[^>]*>\s*Guias Relacionados\s*</h2>', re.IGNORECASE),
        re.compile(r'<h2[^>]*>\s*Artigos Relacionados\s*</h2>', re.IGNORECASE),
    ],
}


def main() -> int:
    hits: list[str] = []
    for lang in LANGS:
        patterns = PER_TEXT_PATTERNS[lang]
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for pat in patterns:
                count = len(pat.findall(html))
                if count >= 2:
                    hits.append(f"{lang}/{fp.name}: {count}× {pat.pattern[:60]}")
                    break

    print(f"❌ Pages with duplicate Related Techniques h2: {len(hits)}")
    for h in hits[:8]:
        print(f"   {h}")
    if not hits:
        print("\n✅ No duplicate Related Techniques h2 across any locale.")
    if "--ci" in sys.argv:
        return 1 if hits else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
