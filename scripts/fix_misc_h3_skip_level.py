#!/usr/bin/env python3
"""z261o: promote miscellaneous <h3> patterns that cause h1→h3 skip-level.

Patterns covered (each is a known decorative / structural element that should be h2):
  P1. <div class="concept-card"><h3>...</h3>             — gen_batch_412_416.py pattern
  P2. <h3 class="app-cta-title">                         — inline CTA card
  P3. <h3 class="wc-card-warn-title">                    — warn / mistakes card
  P4. <h3>Contents</h3>  / <h3>目次</h3> / <h3>Conteúdo</h3>  — TOC heading
  P5. <h3 ...>📋 Official Ruleset Guides</h3>  (and JA/PT) — hub-link card title
  P6. <h3 ...>Common BJJ Problems & FAQ</h3>             — FAQ section title
  P7. <h3 ...>📬 BJJ Free Newsletter</h3>                — newsletter callout

All promotions preserve attributes. Idempotent.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ("en", "ja", "pt")


def _h3_to_h2(text_match: str) -> re.Pattern:
    """Build a regex that matches <h3 [attrs]>text</h3> with the inner text containing the marker."""
    return re.compile(
        rf'<h3([^>]*)>([^<]*{re.escape(text_match)}[^<]*)</h3>',
        re.IGNORECASE,
    )


# Pattern set: each is (label, regex, replacement_template)
PATTERNS: list[tuple[str, re.Pattern, str]] = [
    # P1. concept-card
    (
        "concept-card",
        re.compile(r'(<div class="concept-card">)<h3([^>]*)>([^<]+)</h3>', re.IGNORECASE),
        r'\1<h2\2>\3</h2>',
    ),
    # P2. app-cta-title (inline CTA)
    (
        "app-cta-title",
        re.compile(r'<h3(\s+[^>]*?class="app-cta-title"[^>]*)>([^<]+)</h3>', re.IGNORECASE),
        r'<h2\1>\2</h2>',
    ),
    # P3. wc-card-warn-title
    (
        "wc-card-warn-title",
        re.compile(r'<h3(\s+[^>]*?class="wc-card-warn-title"[^>]*)>([^<]+)</h3>', re.IGNORECASE),
        r'<h2\1>\2</h2>',
    ),
    # P4. TOC heading (EN/JA/PT). Match exact text only.
    (
        "toc-heading-en",
        re.compile(r'<h3([^>]*)>\s*Contents\s*</h3>', re.IGNORECASE),
        r'<h2\1>Contents</h2>',
    ),
    (
        "toc-heading-ja",
        re.compile(r'<h3([^>]*)>\s*目次\s*</h3>'),
        r'<h2\1>目次</h2>',
    ),
    (
        "toc-heading-pt",
        re.compile(r'<h3([^>]*)>\s*Conteúdo\s*</h3>'),
        r'<h2\1>Conteúdo</h2>',
    ),
    # P5. Hub link title 📋 (EN/JA/PT)
    (
        "hub-link-en",
        re.compile(r'<h3([^>]*)>(\s*📋\s*Official Ruleset Guides\s*)</h3>'),
        r'<h2\1>\2</h2>',
    ),
    (
        "hub-link-ja",
        re.compile(r'<h3([^>]*)>(\s*📋\s*公式ルールガイド[^<]*)</h3>'),
        r'<h2\1>\2</h2>',
    ),
    (
        "hub-link-pt",
        re.compile(r'<h3([^>]*)>(\s*📋\s*Guias[^<]*Regras[^<]*)</h3>'),
        r'<h2\1>\2</h2>',
    ),
    # P6. FAQ section common heading
    (
        "common-faq-en",
        re.compile(r'<h3([^>]*)>\s*Common BJJ Problems\s*&amp;?\s*FAQ\s*</h3>', re.IGNORECASE),
        r'<h2\1>Common BJJ Problems &amp; FAQ</h2>',
    ),
    # P7. Newsletter callout (EN/JA/PT)
    (
        "newsletter-en",
        re.compile(r'<h3([^>]*)>(\s*📬[^<]*Newsletter[^<]*)</h3>'),
        r'<h2\1>\2</h2>',
    ),
    (
        "newsletter-ja",
        re.compile(r'<h3([^>]*)>(\s*📬[^<]*ニュースレター[^<]*)</h3>'),
        r'<h2\1>\2</h2>',
    ),
    (
        "newsletter-pt",
        re.compile(r'<h3([^>]*)>(\s*📬[^<]*Newsletter[^<]*)</h3>'),
        r'<h2\1>\2</h2>',
    ),
    # P8. Table of Contents long form
    (
        "toc-longform-en",
        re.compile(r'<h3([^>]*)>\s*Table of Contents\s*</h3>', re.IGNORECASE),
        r'<h2\1>Table of Contents</h2>',
    ),
    # P9. Quick Tips callout
    (
        "quick-tips-en",
        re.compile(r'<h3([^>]*)>\s*💡\s*Quick Tips\s*</h3>'),
        r'<h2\1>💡 Quick Tips</h2>',
    ),
    (
        "quick-tips-ja",
        re.compile(r'<h3([^>]*)>(\s*💡[^<]*)</h3>'),
        r'<h2\1>\2</h2>',
    ),
    # P10. <div class="step"><h4> → <h3> (sibling to concept-card <h2>)
    (
        "step-h4-demote",
        re.compile(r'(<div class="step">)<h4([^>]*)>([^<]+)</h4>'),
        r'\1<h3\2>\3</h3>',
    ),
    # P11. <h3 style="margin:0;font-size:1rem...">  inline title in instructionals
    (
        "instructional-card-h3",
        re.compile(
            r'<h3(\s+style="[^"]*font-size:1rem[^"]*")>([^<]+)</h3>',
            re.IGNORECASE,
        ),
        r'<h2\1>\2</h2>',
    ),
]


def fix_file(fp: Path, apply: bool) -> dict[str, int]:
    html = fp.read_text(encoding="utf-8")
    orig = html
    counts: dict[str, int] = {}
    for label, rx, repl in PATTERNS:
        new_html, n = rx.subn(repl, html)
        if n > 0:
            counts[label] = counts.get(label, 0) + n
            html = new_html
    if apply and html != orig:
        fp.write_text(html, encoding="utf-8")
    return counts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    files_changed = 0
    grand: dict[str, int] = {}
    for loc in LOCALES:
        ld = ROOT / loc
        if not ld.exists():
            continue
        for fp in sorted(ld.glob("*.html")):
            if fp.name.startswith("_"):
                continue
            counts = fix_file(fp, args.apply)
            if counts:
                files_changed += 1
                for k, v in counts.items():
                    grand[k] = grand.get(k, 0) + v

    mode = "applied" if args.apply else "dry-run"
    print(f"[{mode}] files_changed={files_changed}")
    for k, v in sorted(grand.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print(f"  TOTAL_promotions: {sum(grand.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
