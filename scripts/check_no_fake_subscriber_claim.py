#!/usr/bin/env python3
"""
check_no_fake_subscriber_claim.py — z255jjjj-WW Round9: 嘘より沈黙 lint

CLAUDE.md ZERO TOLERANCE rule -3 (嘘より沈黙) + existing 「Honest pricing
fake stats 完全撲滅 (z201)」 enforcement.

Detect any unverified subscriber/user/practitioner count claim:
  - "Join 2,000+ BJJ Practitioners"
  - "2,000人以上の柔術家"
  - "Junte-se a 2,000+ Praticantes"
  - "10,000+ users" (any large round number with people-noun)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

# Match any claim of N,000+ practitioners/subscribers/users (the "+ rounded" pattern is the lying signature)
SUSPICIOUS = [
    re.compile(r'\b\d,?000\+\s*(?:BJJ\s*)?(?:Practitioners|subscribers|members|users)\b', re.IGNORECASE),
    re.compile(r'\d,?000\s*人以上(?:の|登録)'),
    re.compile(r'\b\d,?000\+\s*Praticantes\b', re.IGNORECASE),
]


def main() -> int:
    hits: list[str] = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for pat in SUSPICIOUS:
                m = pat.search(html)
                if m:
                    hits.append(f"{lang}/{fp.name}: {m.group(0)}")
                    break
    print(f"❌ Pages with unverified subscriber/user count claim: {len(hits)}")
    for h in hits[:6]:
        print(f"   {h}")
    if not hits:
        print("\n✅ No fake subscriber/user count claims found.")
    if "--ci" in sys.argv:
        return 1 if hits else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
