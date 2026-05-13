#!/usr/bin/env python3
"""
fix_pt_athlete_desc_concat_drift.py — z260u Phase B Round 2

PT athlete pages have description concat bug: two source descriptions were
glued without proper separator, resulting in patterns like:
  "...inovador.'Dede' é um competidor de..."  (truncated mid-sentence)

Pattern detected: `<sentence>.'<Nickname>' é um competidor de...`
The trailing fragment is broken English-derived translation drift.

Fix: keep only first sentence (everything before `<period>'<Nickname>'`).
Truncates to under 160 chars naturally by removing the broken second part.

idempotent: only patches if the broken concat pattern present.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Match: ends with `.'<text>` or `.'<text>...` — both forms of broken concat.
# The trailing fragment starts with `.'<some text>` which is non-Portuguese
# pattern (no space between period and quote = clearly a concat bug, not
# legitimate prose).
BROKEN_CONCAT_RE = re.compile(
    r"^(.+?\.)'([^']+?)(?:'\s*.*?)?(?:\.\.\.)?\s*$",
    re.DOTALL,
)


def patch_desc(html: str) -> tuple[str, list[str]]:
    log: list[str] = []
    new_html = html

    def replace_attr(match):
        opening = match.group(1)
        desc = match.group(2)
        closing = match.group(3)
        m = BROKEN_CONCAT_RE.match(desc)
        if m:
            cleaned = m.group(1).strip()
            log.append(f"truncated from {len(desc)} to {len(cleaned)} chars")
            return opening + cleaned + closing
        return match.group(0)

    new_html = re.sub(
        r'(<meta\s+name="description"\s+content=")([^"]*)("[^>]*>)',
        replace_attr,
        new_html,
        count=1,
        flags=re.IGNORECASE,
    )
    # Also fix og:description
    new_html = re.sub(
        r'(<meta\s+property="og:description"\s+content=")([^"]*)("[^>]*>)',
        replace_attr,
        new_html,
        count=1,
        flags=re.IGNORECASE,
    )
    return new_html, log


def main() -> int:
    fixed = 0
    for fp in sorted((ROOT / "pt").glob("athlete-*.html")):
        html = fp.read_text(encoding="utf-8")
        new_html, log = patch_desc(html)
        if new_html != html:
            fp.write_text(new_html, encoding="utf-8")
            fixed += 1
            print(f"  FIX {fp.relative_to(ROOT)}: {log[0]}")
    print(f"\nTotal fixed: {fixed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
