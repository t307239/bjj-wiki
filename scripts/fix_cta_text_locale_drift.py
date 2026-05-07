#!/usr/bin/env python3
"""
fix_cta_text_locale_drift.py — z255ll: CTA / nav 英語残留 fix

Round 26 (200 page random pickup) で発見した 3 系統 70 page の
locale drift を root-cause で修正。

Pattern A (JA): nav link `<a href="...login...">App</a>` (50 page)
  → `<a href="...login...">アプリ</a>`
  「アプリ」が JA Wiki の標準 nav 文言。

Pattern B (JA): cta-button `>Start Tracking Free →</a>` (5 page)
  → `>無料で始める →</a>`
  patch_locale_full.py の既存 mapping「Start Free → → 無料で始める →」と整合。

Pattern C (PT): cta-button `>Start Free →</a>` (15 page)
  → `>Começar Grátis →</a>`
  fix_wiki4.py の `Começar Gratuitamente →` よりも短く indie-friendly な
  PT 慣用句 (Stripe / Notion BR の標準採用)。

Idempotent: 既に localized なら no-op。
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Pattern A: JA nav link `>App</a>`
# Anchor on href containing /login to avoid accidental match elsewhere
PATTERN_A_RE = re.compile(
    r'(<a\s+href="[^"]*\/login[^"]*"[^>]*>)App(</a>)'
)
# Pattern B: JA `>Start Tracking Free →</a>`
PATTERN_B_RE = re.compile(r'>Start Tracking Free →<')
# Pattern C: PT `>Start Free →</a>` (allow leading whitespace + newline)
PATTERN_C_RE = re.compile(r'>\s*Start Free →\s*<')


def fix_ja(html: str) -> tuple[str, int]:
    n = 0
    new, c = PATTERN_A_RE.subn(r'\1アプリ\2', html)
    n += c
    new, c = PATTERN_B_RE.subn(">無料で始める →<", new)
    n += c
    return new, n


def fix_pt(html: str) -> tuple[str, int]:
    n = 0
    new, c = PATTERN_C_RE.subn(">Começar Grátis →<", html)
    n += c
    # PT も Start Tracking Free が混入していたケース (Round 26 で 5 件発見)
    new, c = re.subn(r">Start Tracking Free →<", ">Comece a Registrar Grátis →<", new)
    n += c
    return new, n


def main() -> int:
    apply = "--apply" in sys.argv
    by_locale = {"ja": 0, "pt": 0}
    files_changed = 0

    for lang, fixer in (("ja", fix_ja), ("pt", fix_pt)):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.is_dir():
            continue
        for fp in lang_dir.glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            new_html, n = fixer(html)
            if n == 0 or new_html == html:
                continue
            by_locale[lang] += n
            files_changed += 1
            if apply:
                fp.write_text(new_html, encoding="utf-8")

    print(f"📋 candidates by locale: {by_locale}, files affected: {files_changed}")
    if not apply and files_changed > 0:
        print("   (run with --apply to write changes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
