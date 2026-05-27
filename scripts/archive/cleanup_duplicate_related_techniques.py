#!/usr/bin/env python3
"""
cleanup_duplicate_related_techniques.py — Wave WW: dedup my injection

Audit found 2,384 page (out of 4,452) with duplicate "Related Techniques" h2:
the pre-existing one (class="wc-section-box-title" with full-title links) +
my newer injection (`<!-- z255jjjj-related-tech -->`) which has slug-derived
links.

The pre-existing version is richer (full page titles, contextual). My
injection is generic. Strategy: when pre-existing h2 exists, REMOVE my
injection. When NOT, keep my injection.

Idempotent.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
MARKER = "<!-- z255jjjj-related-tech -->"

# Detect "pre-existing" Related Techniques heading (i.e., NOT my injection).
# The pre-existing ones use class="wc-section-box-title" or "wc-related-techniques".
# Mine uses inline style="font-size:1.1rem;color:var(--accent,#7c3aed)".
# Match any pre-existing "Related Techniques"-like h2 EXCEPT my own injection.
# My h2 has the inline style starting with `font-size:1.1rem;color:var(--accent`.
# Anything else is considered pre-existing.
def is_my_h2(h2_open: str) -> bool:
    return "font-size:1.1rem;color:var(--accent,#7c3aed)" in h2_open

PREEXISTING_PATTERNS = {
    "en": re.compile(r'(<h2[^>]*>)\s*(?:Related Techniques|Related Guides|Related Articles)\s*</h2>', re.IGNORECASE),
    "ja": re.compile(r'(<h2[^>]*>)\s*(?:関連テクニック|関連ガイド|関連記事)\s*</h2>'),
    "pt": re.compile(r'(<h2[^>]*>)\s*(?:Técnicas Relacionadas|Guias Relacionados|Artigos Relacionados)\s*</h2>', re.IGNORECASE),
}


def has_preexisting(html: str, lang: str) -> bool:
    """Return True if any 'Related Techniques' h2 exists that is NOT my injection."""
    pat = PREEXISTING_PATTERNS.get(lang)
    if not pat:
        return False
    for m in pat.finditer(html):
        if not is_my_h2(m.group(1)):
            return True
    return False

# Match my injected section to remove cleanly.
# Pattern: starts with marker, ends with </section>\n
MY_SECTION_RE = re.compile(
    r'\n?' + re.escape(MARKER) + r'\n<section[^>]*>.*?</section>\n?',
    re.DOTALL,
)


def cleanup_one(fp: Path, lang: str) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if MARKER not in html:
        return "skip-no-marker"

    if not has_preexisting(html, lang):
        return "keep-no-preexisting"

    # Pre-existing exists → remove my injection
    new_html, n = MY_SECTION_RE.subn("", html, count=1)
    if n == 0:
        return "skip-section-not-found"
    fp.write_text(new_html, encoding="utf-8")
    return "removed"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = cleanup_one(fp, lang)
            stats[r] = stats.get(r, 0) + 1
    print("Cleanup results:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
