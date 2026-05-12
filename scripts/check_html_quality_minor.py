#!/usr/bin/env python3
"""
check_html_quality_minor.py — z255jjjj-WW Round18: HTML quality lints

Detect:
  1. Empty <h2></h2> headings
  2. 3+ consecutive <br> tags (anti-pattern, should use <p>)

Both are HTML invalid signals + bad markup hygiene.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
EMPTY_H_RE = re.compile(r"<h[2-6][^>]*>\s*</h[2-6]>")
BR_CHAIN_RE = re.compile(r"(?:<br\s*/?>\s*){3,}")


def main() -> int:
    issues: dict[str, list[str]] = {"empty-heading": [], "br-chain": []}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if NOINDEX_RE.search(html[:600]):
                continue
            src = f"{lang}/{fp.name}"
            if EMPTY_H_RE.search(html):
                issues["empty-heading"].append(src)
            if BR_CHAIN_RE.search(html):
                issues["br-chain"].append(src)

    total = sum(len(v) for v in issues.values())
    for k, v in issues.items():
        print(f"❌ {k}: {len(v)}")
        for s in v[:3]:
            print(f"   {s}")
    if total == 0:
        print("\n✅ No empty headings or excessive br chains.")
    if "--ci" in sys.argv:
        return 1 if total > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
