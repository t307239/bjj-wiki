#!/usr/bin/env python3
"""
fix_round_z260w_desc_drift.py — z260w Round 1 (one-off fix)

Found by `check_description_quality.py` (new lint, z260w):
  - 8 PT pages with fully English meta description (locale drift)
  - 1 EN page with description > 160 chars (length overflow)

Idempotent: only writes if bad pattern still present.

After this runs successfully, archive to scripts/archive/.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

META_DESC_RE = re.compile(
    r'(<meta\s+name="description"\s+content=")([^"]*)("[^>]*>)', re.IGNORECASE
)
OG_DESC_RE = re.compile(
    r'(<meta\s+property="og:description"\s+content=")([^"]*)("[^>]*>)', re.IGNORECASE
)

# 8 PT translations — keep BJJ terms in PT, stay under 160 chars
PT_REPLACEMENTS: dict[str, str] = {
    "pt/bjj-connection-principles.html":
        "Domine os princípios de conexão e movimento de quadril no Jiu-Jitsu Brasileiro. Aprenda a controlar distância e manter dominância em todas as posições.",
    "pt/bjj-overtime-strategy-bjj.html":
        "Aprenda estratégias de overtime e morte súbita no BJJ. Domine regras EBI e lutas submission-only com técnicas de finalização eficazes.",
    "pt/bjj-pin-escape-fundamentals.html":
        "Domine os princípios fundamentais de escape de pin no Jiu-Jitsu. Aprenda ponte, frames e escapes explosivos de posições dominadas.",
    "pt/bjj-points-strategy-guide.html":
        "Aprenda estratégia de pontuação em competição de Jiu-Jitsu. Domine técnicas de pontuação e vantagens posicionais segundo as regras IBJJF.",
    "pt/bjj-pressure-fundamentals.html":
        "Aprenda fundamentos de pressão e controle no BJJ. Domine distribuição de peso e mecânica corporal para passagem de guarda eficaz.",
    "pt/bjj-stalling-rules-bjj.html":
        "Aprenda as regras de stalling em competição IBJJF. Domine técnicas legais vs ilegais de stalling no Jiu-Jitsu Brasileiro.",
    "pt/bjj-strangle-from-back.html":
        "Domine variações de estrangulamento da posição de costas (back control). Aprenda mata-leão (RNC), gola e estrangulamentos com lapela.",
    "pt/bjj-weight-distribution-guide.html":
        "Aprenda distribuição de peso no Jiu-Jitsu para controle máximo. Domine aplicação de pressão e manutenção de equilíbrio em posições de cima.",
}

# 1 EN compression — preserve meaning, fit under 160 chars
EN_REPLACEMENTS: dict[str, str] = {
    "en/bjj-counter-attack-system.html":
        "Master the BJJ counter attack system. Capitalize on opponent mistakes, turn defense into offense, and counter common attacks effectively.",
}


def patch_file(rel: str, new_desc: str) -> bool:
    fp = ROOT / rel
    if not fp.exists():
        print(f"  SKIP missing: {rel}")
        return False
    html = fp.read_text(encoding="utf-8")
    orig = html

    m = META_DESC_RE.search(html)
    if not m:
        print(f"  SKIP no description: {rel}")
        return False
    cur_desc = m.group(2)

    # Idempotent: skip if already at target
    if cur_desc == new_desc:
        print(f"  OK  {rel} (already at target)")
        return False

    # Replace meta description
    html = html[: m.start(2)] + new_desc + html[m.end(2):]

    # Sync og:description if it matched the bad one
    og = OG_DESC_RE.search(html)
    if og and og.group(2) == cur_desc:
        html = html[: og.start(2)] + new_desc + html[og.end(2):]

    if html != orig:
        fp.write_text(html, encoding="utf-8")
        print(f"  FIX {rel} ({len(cur_desc)} → {len(new_desc)}): {new_desc[:80]}")
        return True
    return False


def main() -> int:
    print("=== z260w PT description locale-drift fix ===")
    fixed_pt = 0
    for rel, new_desc in PT_REPLACEMENTS.items():
        if patch_file(rel, new_desc):
            fixed_pt += 1

    print("\n=== z260w EN description length fix ===")
    fixed_en = 0
    for rel, new_desc in EN_REPLACEMENTS.items():
        if patch_file(rel, new_desc):
            fixed_en += 1

    print(f"\nTotal: PT={fixed_pt}, EN={fixed_en}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
