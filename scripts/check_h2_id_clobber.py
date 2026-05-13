#!/usr/bin/env python3
"""
check_h2_id_clobber.py — z260x lint

Catches the regression pattern where auto-toc JS unconditionally overwrites
`h.id` (clobbering IDs set by other generators like wiki-sidebar). This
caused 3,856+ pages to have broken sidebar anchors (#hs0..5).

Bad pattern:
    headings.forEach(function(h,i){
      var id='section-'+i;
      h.id=id;          // ← UNCONDITIONAL: breaks pre-existing hs0..5 IDs
      ...

Good pattern (z260x):
    headings.forEach(function(h,i){
      if(!h.id)h.id='section-'+i;
      var id=h.id;
      ...

`--ci` flag returns EXIT:1 if any finding, else EXIT:0.

Run: python3 scripts/check_h2_id_clobber.py [--ci]
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Bad pattern: unconditional h.id overwrite right after `var id='section-'+i;`
BAD_RE = re.compile(
    r"""headings\.forEach\(function\(h,i\)\{[\s\n]*
        var\s+id\s*=\s*'section-'\s*\+\s*i\s*;\s*\n
        \s*h\.id\s*=\s*id\s*;""",
    re.VERBOSE,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true", help="EXIT:1 on findings")
    args = parser.parse_args()

    findings = []
    for lang in ("en", "ja", "pt"):
        d = ROOT / lang
        if not d.exists():
            continue
        for fp in sorted(d.glob("*.html")):
            try:
                html = fp.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if BAD_RE.search(html):
                findings.append(str(fp.relative_to(ROOT)))

    print(f"❌ Pages with unconditional h2 id clobber (auto-toc breaks wiki-sidebar anchors): {len(findings)}")
    for f in findings[:20]:
        print(f"  {f}")
    if len(findings) > 20:
        print(f"  ... and {len(findings) - 20} more")

    if args.ci and findings:
        return 1
    print("\n✅ No h2 id clobber pattern found." if not findings else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
