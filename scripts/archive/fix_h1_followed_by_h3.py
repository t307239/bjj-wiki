#!/usr/bin/env python3
"""z261o: promote bare <h3> that appears as the next heading after <h1> (with no
intervening <h2>) to <h2> for a11y heading order.

Conservative strategy:
  - Walk headings in order.
  - For each <h1>, look at subsequent headings until the next <h1> or EOF.
  - If the first subsequent heading is <h3> (or <h4>+) with no <h2> between, promote
    consecutive same-level headings up to the first <h2> (or until level decreases below).
  - Only promote when the <h3> has no class (avoids touching styled cards like
    wc-card-warn-title, app-cta-title, etc. which are already handled by P*-rules above).

Idempotent.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ("en", "ja", "pt")

# Match either <h3> or <h3 attrs> capturing position + level + text + attrs
HEADING_RE = re.compile(
    r"<h([1-6])([^>]*)>(.*?)</h\1>", re.IGNORECASE | re.DOTALL
)


def fix_html(html: str) -> tuple[str, int]:
    matches = list(HEADING_RE.finditer(html))
    if not matches:
        return html, 0

    # Find positions to promote: indices of <h3> with no class/style id markers,
    # immediately after <h1> with no <h2> in between.
    to_promote: list[int] = []  # indices into matches list
    n_headings = len(matches)
    for i, m in enumerate(matches):
        lvl = int(m.group(1))
        if lvl != 1:
            continue
        # Look ahead until next h1 or h2
        j = i + 1
        while j < n_headings:
            mj = matches[j]
            lvl_j = int(mj.group(1))
            if lvl_j <= 2:
                break  # found h2 or h1, stop
            if lvl_j == 3:
                attrs = mj.group(2)
                # Skip if h3 has class or special id (likely already handled by P-rules)
                if "class=" in attrs.lower() or "id=" in attrs.lower():
                    j += 1
                    continue
                to_promote.append(j)
            j += 1

    if not to_promote:
        return html, 0

    # Build output by splicing
    out: list[str] = []
    cursor = 0
    n_replacements = 0
    for j in range(n_headings):
        m = matches[j]
        if j not in to_promote:
            continue
        # append text from cursor to m.start()
        out.append(html[cursor:m.start()])
        attrs = m.group(2)
        inner = m.group(3)
        out.append(f"<h2{attrs}>{inner}</h2>")
        cursor = m.end()
        n_replacements += 1
    out.append(html[cursor:])
    return "".join(out), n_replacements


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    files_changed = 0
    total_replacements = 0
    for loc in LOCALES:
        ld = ROOT / loc
        if not ld.exists():
            continue
        for fp in sorted(ld.glob("*.html")):
            if fp.name.startswith("_"):
                continue
            html = fp.read_text(encoding="utf-8")
            new_html, n = fix_html(html)
            if n > 0:
                if args.apply:
                    fp.write_text(new_html, encoding="utf-8")
                files_changed += 1
                total_replacements += n

    mode = "applied" if args.apply else "dry-run"
    print(f"[{mode}] files_changed={files_changed} replacements={total_replacements}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
