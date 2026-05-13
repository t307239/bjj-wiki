#!/usr/bin/env python3
"""
fix_round_z260x_auto_toc_h2_id_clobber.py — z260x Round 2 (one-off fix)

Root cause: auto-toc JS in 3,856 pages does:
    headings.forEach(function(h,i){
      var id='section-'+i;
      h.id=id;                  // ← UNCONDITIONALLY overwrites h.id
      ...
      a.href='#'+id;
    });

When wiki-sidebar JS runs FIRST (line ~207) and assigns `h.id = 'hs'+i`,
the wiki-sidebar builds `<a href="#hs0..5">` links. Then the auto-toc JS
clobbers `h.id` to `section-N`, breaking the sidebar anchors (6 broken
anchors per affected gear/athlete/lp page).

Fix: change auto-toc to:
    headings.forEach(function(h,i){
      if(!h.id) h.id='section-'+i;
      var id = h.id;
      ...
      a.href='#'+id;
    });

This preserves any pre-existing IDs (incl. `hs0..N` from wiki-sidebar)
and the auto-toc list uses whatever id h2 actually has → both TOCs
consistent, zero broken anchors.

Also patches generator `generate_bjj_wiki.py` line ~1058-1066 to make
new pages clean.

Idempotent: only patches if the un-guarded `var id='section-'+i;\\n          h.id=id;`
pattern is present (replaces with guarded version).
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Match the entire bad block pattern (whitespace-flexible) and replace with guarded version.
# Bad pattern occurs in 2 forms with different indentations.
BAD_RE = re.compile(
    r"""(headings\.forEach\(function\(h,i\)\{[\s\n]*)
        var\s+id\s*=\s*'section-'\s*\+\s*i\s*;\s*\n
        \s*h\.id\s*=\s*id\s*;
        (\s*\n)""",
    re.VERBOSE,
)
GOOD = r"\1if(!h.id)h.id='section-'+i;\n        var id=h.id;\2"


def patch_file(fp: Path) -> bool:
    try:
        html = fp.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    new_html, n = BAD_RE.subn(GOOD, html)
    if n > 0 and new_html != html:
        fp.write_text(new_html, encoding="utf-8")
        return True
    return False


def main(dry_run: bool = False) -> int:
    fixed = 0
    skipped_already_clean = 0
    skipped_no_pattern = 0

    for lang in ("en", "ja", "pt"):
        d = ROOT / lang
        for fp in sorted(d.glob("*.html")):
            try:
                html = fp.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            has_bad = bool(BAD_RE.search(html))
            has_guard = "if(!h.id)h.id='section-'+i;" in html

            if has_bad:
                if dry_run:
                    fixed += 1  # would-fix count in dry-run
                elif patch_file(fp):
                    fixed += 1
                else:
                    skipped_no_pattern += 1
            elif has_guard:
                skipped_already_clean += 1
            else:
                skipped_no_pattern += 1

    # Also patch generator (z255jjjj-WW etc. preserved)
    gen_fp = ROOT / "scripts" / "generate_bjj_wiki.py"
    if gen_fp.exists() and not dry_run:
        gen_html = gen_fp.read_text(encoding="utf-8")
        new_gen = BAD_RE.sub(GOOD, gen_html)
        # generator uses double-brace escaping in f-strings; manual check
        if "var id='section-'+i;" in gen_html and new_gen != gen_html:
            gen_fp.write_text(new_gen, encoding="utf-8")
            print("FIX generator: scripts/generate_bjj_wiki.py")
        else:
            # Check if needs different escape pattern in f-string with {{ }}
            # Replace manually
            patched = re.sub(
                r"""(headings\.forEach\(function\(h,i\)\{\{[\s\n]*)
                    var\s+id\s*=\s*'section-'\s*\+\s*i\s*;\s*\n
                    \s*h\.id\s*=\s*id\s*;
                    (\s*\n)""",
                r"\1if(!h.id)h.id='section-'+i;\n          var id=h.id;\2",
                gen_html,
                flags=re.VERBOSE,
            )
            if patched != gen_html:
                gen_fp.write_text(patched, encoding="utf-8")
                print("FIX generator (escaped form): scripts/generate_bjj_wiki.py")
            else:
                print("OK  generator already clean or no match (manual review)")

    print(f"\nFiles fixed: {fixed}")
    print(f"Files already clean: {skipped_already_clean}")
    print(f"Files w/o pattern: {skipped_no_pattern}")
    return 0


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    sys.exit(main(dry_run))
