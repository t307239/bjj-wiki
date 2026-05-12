#!/usr/bin/env python3
"""
check_no_nested_p.py — z255jjjj-WW Round2: nested <p> regression detector

Catches the `<p><p style="...">...` invalid HTML pattern that sneaks in via
older generator scripts.

--ci flag → exit 1 if any page has the pattern.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
NESTED_P_RE = re.compile(r'<p[^>]*>\s*<p[^>]*>', re.DOTALL)


def main() -> int:
    hits: list[str] = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if NESTED_P_RE.search(html):
                hits.append(f"{lang}/{fp.name}")
    print(f"❌ Pages with nested <p><p>: {len(hits)}")
    for h in hits[:6]:
        print(f"   {h}")
    if not hits:
        print("\n✅ No nested <p> tags across any locale.")
    if "--ci" in sys.argv:
        return 1 if hits else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
