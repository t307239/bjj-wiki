#!/usr/bin/env python3
"""
fix_duplicate_titles.py — z255u: 同一 locale 内で title 衝突する 18 page を fix

EN では distinct title だが翻訳時に細部が落ち、JA/PT で title 衝突した 9 pair
(18 page)。Google が duplicate content と判定する SEO 損失。

修正方針: slug の意味を踏まえて 2 つ目の page の title を distinct に書き直す。
canonical はそのまま (両 page を独立 page として indexable に保つ)。
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# (lang, slug, new_title, new_h1) — 既存 title を残したい slug は無変更
TITLE_FIXES = [
    # ─── ja ─────────────────────────────────────────────────────
    # bjj-front-headlock-bjj は legacy "in BJJ" 系、bjj-front-headlock-system が new
    ("ja", "bjj-front-headlock-bjj",
     "フロントヘッドロック攻防 | BJJ Wiki",
     "BJJ におけるフロントヘッドロック攻防"),
    # bjj-bjj-academy-guide は "Choosing"、bjj-academies-guide は "Evaluation"
    ("ja", "bjj-academies-guide",
     "BJJジムの評価ガイド | BJJ Wiki",
     "BJJジムを評価する指標"),
    # ─── pt ─────────────────────────────────────────────────────
    # bjj-cutting-weight-bjj は general、bjj-competition-weight-cutting は competition specific
    ("pt", "bjj-competition-weight-cutting",
     "Corte de Peso para Competição de BJJ | Métodos e Timing | BJJ Wiki",
     "Corte de Peso para Competição: Métodos Seguros e Timing"),
    # long-game-development = 10-year blueprint、long-game-bjj = generic
    ("pt", "bjj-long-game-development",
     "Desenvolvimento de Longo Prazo no BJJ: Plano de 10 Anos | BJJ Wiki",
     "Desenvolvimento de Longo Prazo no BJJ: Plano de Maestria de 10 Anos"),
    # submission-defense (broad) vs choke-defense (specific)
    ("pt", "bjj-choke-defense-guide",
     "Guia de Defesa de Estrangulamentos no BJJ | BJJ Wiki",
     "Guia de Defesa de Estrangulamentos"),
    # kimura-system vs kimura-trap-system — 後者を完成版扱いに
    ("pt", "bjj-kimura-trap-system",
     "Sistema Kimura Trap Completo: Guia BJJ | BJJ Wiki",
     "Sistema Kimura Trap: Guia Completo"),
    # closed-guard-fundamentals vs guard-fundamentals-closed — 後者は重複生成、独自 framing 化
    ("pt", "bjj-guard-fundamentals-closed",
     "Guarda Fechada: Fundamentos do Jogo de Guarda no BJJ | BJJ Wiki",
     "Guarda Fechada: Fundamentos do Jogo de Guarda"),
    # bjj-no-gi-guard-guide vs bjj-no-gi-guard-game — 前者は legacy stub
    ("pt", "bjj-no-gi-guard-guide",
     "Guia da Guarda Sem Kimono no BJJ | BJJ Wiki",
     "Guia da Guarda Sem Kimono no BJJ"),
    # bjj-top-half-guard-guide vs bjj-passing-half-guard — 前者は legacy stub
    ("pt", "bjj-top-half-guard-guide",
     "Guia da Passagem de Meia Guarda Superior | BJJ Wiki",
     "Passagem de Meia Guarda Superior: Guia"),
    # ─── en (z255x で brand suffix collapse 後に露出) ─────────────
    # bjj-no-gi-guard-guide vs bjj-no-gi-guard-game — 前者は legacy stub
    ("en", "bjj-no-gi-guard-guide",
     "No-Gi Guard Guide | BJJ Wiki",
     "No-Gi Guard Guide"),
]


def patch(lang: str, slug: str, new_title: str, new_h1: str) -> bool:
    fp = REPO_ROOT / lang / f"{slug}.html"
    if not fp.exists():
        return False
    html = fp.read_text(encoding="utf-8")

    # title
    new = re.sub(
        r"(<title[^>]*>)(.*?)(</title>)",
        lambda m: f"{m.group(1)}{new_title}{m.group(3)}",
        html,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    # og:title (合わせる)
    new = re.sub(
        r'(<meta\s+property=["\']og:title["\']\s+content=["\'])([^"\']+)(["\'])',
        lambda m: f"{m.group(1)}{new_title}{m.group(3)}",
        new,
        count=1,
        flags=re.IGNORECASE,
    )
    # h1
    new = re.sub(
        r"(<h1[^>]*>)(.*?)(</h1>)",
        lambda m: f"{m.group(1)}{new_h1}{m.group(3)}",
        new,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if new == html:
        return False
    fp.write_text(new, encoding="utf-8")
    return True


def main():
    print("🔧 fix_duplicate_titles.py — z255u")
    fixed = 0
    for lang, slug, t, h1 in TITLE_FIXES:
        if patch(lang, slug, t, h1):
            fixed += 1
            print(f"  ✅ {lang}/{slug}.html")
        else:
            print(f"  ⚠️  {lang}/{slug}.html (skipped)")
    print(f"\n✅ Total fixed: {fixed} files")


if __name__ == "__main__":
    main()
