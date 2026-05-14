#!/usr/bin/env python3
"""z261o: fix h1 → h3 skip-level by promoting legacy <h3>🥋 Related/関連/Técnicas</h3>
to <h2> inside <div class="related-section">.

Root cause:
  scripts/fix_crosslinks.py emits <h3> for related-section heading.
  Pages without a sibling <h2> between h1 and that <h3> get a skip-level
  WCAG 2.4.6 violation (screen readers can lose context).

Strategy:
  Only promote when the heading is inside <div class="related-section">.
  Bump corresponding inline style (related-section h3 → h2 styled compactly).
  Marker: <!-- z261o-h-promoted -->

Idempotent: re-run-safe (regex anchored to <div class="related-section">).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ("en", "ja", "pt")

# Match <div class="related-section"> with <h3>...</h3> within first ~200 chars
LEGACY_RELATED_BLOCK_RE = re.compile(
    r'(<div\s+class="related-section"[^>]*>\s*)<h3([^>]*)>([^<]+)</h3>',
    re.IGNORECASE,
)

# Idempotency marker — if present, skip
MARKER = "<!-- z261o-h-promoted -->"


def fix_file(fp: Path) -> tuple[bool, int]:
    html = fp.read_text(encoding="utf-8")
    if MARKER in html:
        return False, 0
    # Only act if a legacy related-section <h3> exists
    if not LEGACY_RELATED_BLOCK_RE.search(html):
        return False, 0

    # Promote <h3> → <h2> with compact inline style matching the older visual weight
    def _promote(m: re.Match) -> str:
        opening = m.group(1)
        attrs = m.group(2).strip()
        heading_text = m.group(3)
        # Add modest inline style if no class/style already present (preserve attrs)
        style_inject = ""
        if "style=" not in attrs and "class=" not in attrs:
            style_inject = ' style="font-size:1.1rem;color:var(--accent,#7c3aed);margin-bottom:12px"'
        return f"{opening}<h2{(' ' + attrs) if attrs else ''}{style_inject}>{heading_text}</h2>"

    new_html, n = LEGACY_RELATED_BLOCK_RE.subn(_promote, html)
    if n == 0:
        return False, 0

    # Insert marker just after <head> if not already
    if MARKER not in new_html:
        new_html = new_html.replace("</head>", f"{MARKER}\n</head>", 1)
    fp.write_text(new_html, encoding="utf-8")
    return True, n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write changes")
    ap.add_argument(
        "--dry-run", action="store_true", help="Print without writing (default)"
    )
    args = ap.parse_args()

    total_files_changed = 0
    total_promotions = 0
    for loc in LOCALES:
        ld = ROOT / loc
        if not ld.exists():
            continue
        for fp in sorted(ld.glob("*.html")):
            if fp.name.startswith("_"):
                continue
            html = fp.read_text(encoding="utf-8")
            if MARKER in html:
                continue
            if not LEGACY_RELATED_BLOCK_RE.search(html):
                continue
            if args.apply:
                changed, n = fix_file(fp)
                if changed:
                    total_files_changed += 1
                    total_promotions += n
            else:
                total_files_changed += 1
                total_promotions += len(LEGACY_RELATED_BLOCK_RE.findall(html))

    mode = "applied" if args.apply else "dry-run"
    print(f"[{mode}] files_changed={total_files_changed} promotions={total_promotions}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
