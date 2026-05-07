#!/usr/bin/env python3
"""
check_cta_text_locale_drift.py — z255ll: JA/PT page で CTA / nav の英語残留検査
(27th lint)

Round 26 (200 page random pickup) で発見した 70 page (JA 55 + PT 15) の
CTA 英語残留 root cause を恒久 catch:

検出パターン:
  - JA: nav `<a href=".../login...">App</a>` (50 page で発見)
  - JA: cta-button `>Start Tracking Free →</a>` (5 page)
  - PT: cta-button `>Start Free →</a>` (15 page)
  - JA: cta-button `>Start Free →</a>` (subset of above pattern, JA でも誤適用)

JA は「アプリ」「無料で始める」「無料で記録を始める」が標準、PT は
「Começar Grátis」が標準 (patch_locale_full.py / fix_wiki4.py の既存 mapping)。

これら英語残留は generator script (fix_wiki4.py / patch 系) の locale branch
ロジックが旧版で書かれていた時の遺物。Round 26 で全部 fix 済 (z255ll)、
本 lint で先祖返りを永久 block。

--ci flag で hit > 0 → exit 1
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# JA-only patterns: English text inside CTA / nav with /login href
JA_PATTERNS = [
    (re.compile(r'<a\s+href="[^"]*\/login[^"]*"[^>]*>App</a>'), 'nav: >App</a>'),
    (re.compile(r'>Start Tracking Free →<'), 'cta: >Start Tracking Free →<'),
    (re.compile(r'>\s*Start Free →\s*<'), 'cta: >Start Free →<'),
]

# PT-only patterns
PT_PATTERNS = [
    (re.compile(r'>\s*Start Free →\s*<'), 'cta: >Start Free →<'),
    (re.compile(r'>Start Tracking Free →<'), 'cta: >Start Tracking Free →<'),
]


def scan(lang: str, patterns) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    lang_dir = REPO_ROOT / lang
    if not lang_dir.is_dir():
        return issues
    for fp in lang_dir.glob("*.html"):
        try:
            html = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        for p, label in patterns:
            if p.search(html):
                issues.append((f"{lang}/{fp.name}", label))
    return issues


def main() -> int:
    ja_issues = scan("ja", JA_PATTERNS)
    pt_issues = scan("pt", PT_PATTERNS)
    total = len(ja_issues) + len(pt_issues)

    print(f"❌ JA pages with English CTA / nav residue: {len(ja_issues)}")
    for src, label in ja_issues[:6]:
        print(f"   {src}  ({label})")
    print(f"❌ PT pages with English CTA residue: {len(pt_issues)}")
    for src, label in pt_issues[:6]:
        print(f"   {src}  ({label})")
    if total == 0:
        print("\n✅ No CTA / nav English residue in JA / PT pages.")

    if "--ci" in sys.argv:
        return 1 if total > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
