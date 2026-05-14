#!/usr/bin/env python3
"""
check_zindex_hardcode_in_html.py — z261f lint (48th wiki lint)

Catches hardcoded `z-index: NN` values in HTML files (live wiki: en/ja/pt + root)
that are NOT on the allowlist. New surface introducing arbitrary z-index values
breaks the layered stacking design and competes with the float-cta / lang-switcher
overlays.

Allowed values (legitimate stacking):
  - 999  : z243 float-cta (4,695 page across 3 locale) — must be wrapped in
           `<!-- z243-float-cta -->` marker or `<div id="z243-float"`
  - 9999 : reserved for modal/lightbox (only legitimate inside docs/ examples)

Any other z-index value (e.g., 100, 500, 9998, 10000, etc.) on a live wiki page
is flagged as WARN; CI mode (`--ci`) returns EXIT:1.

Run: python3 scripts/check_zindex_hardcode_in_html.py [--ci]
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# z-index: NN  (any integer, with optional whitespace)
ZINDEX_RE = re.compile(r"z-index\s*:\s*(\d+)", re.IGNORECASE)

# Allowed z-index values per context. Map: value → required marker substring.
# If marker is None, value is unconditionally allowed.
ALLOWED = {
    999: "z243-float",   # z243-float-cta marker required on same / nearby element
    9999: None,           # legacy modal/lightbox (rare, mostly in docs/)
    2: None,              # tooltip-style minor overlays
}

# Scan these directories (live wiki + root)
SCAN_DIRS = ["en", "ja", "pt"]
SCAN_ROOT_FILES = True  # root *.html (404, about, privacy, etc.)


def is_allowed(value: int, line: str, context: str) -> bool:
    """Return True if this z-index is on the allowlist for the given context."""
    if value not in ALLOWED:
        return False
    marker = ALLOWED[value]
    if marker is None:
        return True
    # Marker must appear in the line OR within 200 chars surrounding context
    return marker in line or marker in context


def scan_file(fp: Path) -> list[tuple[int, int, str]]:
    """Return list of (line_no, value, line_excerpt) for non-allowed hits."""
    try:
        text = fp.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    findings = []
    for m in ZINDEX_RE.finditer(text):
        value = int(m.group(1))
        # Get line number + line content
        line_start = text.rfind("\n", 0, m.start()) + 1
        line_end = text.find("\n", m.end())
        if line_end == -1:
            line_end = len(text)
        line = text[line_start:line_end]
        ln = text[:m.start()].count("\n") + 1
        # Context: ±200 chars
        ctx_start = max(0, m.start() - 200)
        ctx_end = min(len(text), m.end() + 200)
        context = text[ctx_start:ctx_end]
        if not is_allowed(value, line, context):
            excerpt = line.strip()[:160]
            findings.append((ln, value, excerpt))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true", help="EXIT:1 on findings")
    args = parser.parse_args()

    total_findings: list[tuple[str, int, int, str]] = []

    # Locale dirs
    for lang in SCAN_DIRS:
        d = ROOT / lang
        if not d.exists():
            continue
        for fp in sorted(d.glob("*.html")):
            hits = scan_file(fp)
            for ln, val, excerpt in hits:
                total_findings.append((str(fp.relative_to(ROOT)), ln, val, excerpt))

    # Root *.html (404, about, privacy, etc.)
    if SCAN_ROOT_FILES:
        for fp in sorted(ROOT.glob("*.html")):
            hits = scan_file(fp)
            for ln, val, excerpt in hits:
                total_findings.append((str(fp.relative_to(ROOT)), ln, val, excerpt))

    print(f"→ scanning for z-index: NN hardcodes outside allowlist {sorted(ALLOWED.keys())}...")
    print(f"❌ Non-allowed z-index hardcodes: {len(total_findings)}")

    # Group by value for summary
    from collections import Counter
    by_value = Counter(v for _, _, v, _ in total_findings)
    if by_value:
        print("  By value:")
        for v, n in sorted(by_value.items()):
            print(f"    z-index: {v} → {n} hits")

    # Sample first 20
    for fp, ln, val, ex in total_findings[:20]:
        print(f"  {fp}:{ln}  z-index:{val}  {ex[:100]}")
    if len(total_findings) > 20:
        print(f"  ... and {len(total_findings) - 20} more")

    if args.ci and total_findings:
        return 1
    if not total_findings:
        print(f"\n✅ All z-index values are on allowlist {sorted(ALLOWED.keys())}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
