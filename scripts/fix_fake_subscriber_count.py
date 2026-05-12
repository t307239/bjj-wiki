#!/usr/bin/env python3
"""
fix_fake_subscriber_count.py — Wave WW Round 9: 嘘より沈黙 enforcement

CLAUDE.md ZERO TOLERANCE rule -3「嘘より沈黙」+ existing 「Honest pricing
fake stats 完全撲滅 (z201)」 violation: 2,972 indexable pages claim
"Join 2,000+ BJJ Practitioners" in the Beehiiv newsletter signup —
actual subscriber count is far lower (per CLAUDE.md z219, real users ≈ 1).

Replace with honest copy that emphasizes value rather than fake social proof:
  EN: "📬 Free BJJ Newsletter"
       p: "Get the free BJJ White Belt Guide + weekly technique breakdowns
           and training tips. No spam. Unsubscribe anytime."
  JA: "📬 BJJ 無料ニュースレター"
       p: "無料の白帯ガイド＋毎週の技術解説・練習のコツをお届け。
           スパムなし。いつでも配信停止可能。"
  PT: "📬 Newsletter BJJ Grátis"
       p: "Receba o Guia Gratuito do Faixa Branca + análises de técnicas
           semanais, dicas de treino. Sem spam. Desinscrever a qualquer
           momento."

Idempotent. Skip noindex.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')

# Per-locale heading + paragraph replacements
REPLACEMENTS = {
    "en": [
        (
            re.compile(r'<h3>📬\s*Join\s*2,?000\+\s*BJJ\s*Practitioners\s*</h3>', re.IGNORECASE),
            '<h3>📬 Free BJJ Newsletter</h3>',
        ),
    ],
    "ja": [
        (
            re.compile(r'<h3>📬\s*2,?000\s*人以上の柔術家に参加\s*</h3>'),
            '<h3>📬 BJJ 無料ニュースレター</h3>',
        ),
    ],
    "pt": [
        (
            re.compile(r'<h3>📬\s*Junte-se a 2,?000\+\s*Praticantes de BJJ\s*</h3>', re.IGNORECASE),
            '<h3>📬 Newsletter BJJ Grátis</h3>',
        ),
    ],
}


def patch_one(fp: Path, lang: str) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"
    changes = 0
    for pat, repl in REPLACEMENTS.get(lang, []):
        new_html, n = pat.subn(repl, html)
        if n:
            changes += n
            html = new_html
    if changes == 0:
        return "already"
    fp.write_text(html, encoding="utf-8")
    return f"patched-{changes}"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = patch_one(fp, lang)
            stats[r] = stats.get(r, 0) + 1
    print("Fake subscriber count fix:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
