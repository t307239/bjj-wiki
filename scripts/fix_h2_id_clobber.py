#!/usr/bin/env python3
"""
fix_h2_id_clobber.py — z261g: 200 page auto-toc h2 id clobber regression

200 HTML pages still have the bad pattern:
    headings.forEach(function(h,i){
      var id='section-'+i;
      h.id=id;            // ← clobbers wiki-sidebar anchor IDs (hs0..5)
      ...

Fix to z260x's idempotent pattern:
    headings.forEach(function(h,i){
      var id='section-'+i;
      if(!h.id)h.id=id;   // preserve pre-existing IDs
      ...

Source generators (`fix_ux_improvements.py`, `structural_upgrade.py`) still
emit the bad pattern; this patcher fixes the existing corpus.
Per CLAUDE.md rule -4: source generators should be fixed in a follow-up
to prevent future regenerations; this batch covers current files.

Idempotent: skip pages already using `if(!h.id)`.

Usage:
    python3 scripts/fix_h2_id_clobber.py            # apply
    python3 scripts/fix_h2_id_clobber.py --dry-run  # preview only
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("en", "ja", "pt")

# Match the exact bad pattern. Two capture groups: indent + comment after
BAD_RE = re.compile(
    r"(headings\.forEach\(function\(h,i\)\{\s*\n"
    r"\s*var\s+id\s*=\s*'section-'\s*\+\s*i\s*;\s*\n"
    r"(\s*))h\.id\s*=\s*id\s*;",
)

NEW_PATTERN = r"\1if(!h.id)h.id=id;"


def patch_one(fp: Path) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "skip-read"
    if not BAD_RE.search(html):
        return "already"
    new_html = BAD_RE.sub(NEW_PATTERN, html)
    if new_html == html:
        return "noop"
    fp.write_text(new_html, encoding="utf-8")
    return "patched"


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    stats: dict[str, int] = {}
    for lang in LANGS:
        d = ROOT / lang
        if not d.exists():
            continue
        for fp in sorted(d.glob("*.html")):
            if dry_run:
                # mock: check only
                try:
                    html = fp.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    r = "skip-read"
                else:
                    r = "would-patch" if BAD_RE.search(html) else "already"
            else:
                r = patch_one(fp)
            stats[r] = stats.get(r, 0) + 1
    print(f"h2-id-clobber fix [{'DRY-RUN' if dry_run else 'APPLY'}]:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
