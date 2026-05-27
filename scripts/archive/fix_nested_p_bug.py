#!/usr/bin/env python3
"""
fix_nested_p_bug.py — Wave WW Round 2: nested <p><p>...</p> HTML invalid

Audit found 204 pages with `<p><p style="...">content</p>` (no closing for
outer <p>). Invalid HTML. Generator bug from older script wrapped a paragraph
list in an outer empty <p>.

Fix: remove the outer empty `<p>` (the inner `<p style="...">` is the real
content). Use surgical string replacement.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

# Match the dangling outer <p> immediately followed by inner <p style=...>.
# Allow whitespace + optional newline between them.
NESTED_P_RE = re.compile(r'(<p[^>]*>)(\s*)(<p[^>]*style=)', re.DOTALL)


def fix_one(fp: Path) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    new_html, n = NESTED_P_RE.subn(r'\2\3', html)
    if n == 0:
        return "skip-clean"
    fp.write_text(new_html, encoding="utf-8")
    return f"patched-{n}"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = fix_one(fp)
            stats[r] = stats.get(r, 0) + 1
    print("Nested <p> fix results:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
