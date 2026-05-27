#!/usr/bin/env python3
"""
fix_pt_index_categories.py — Wave WW Round 15: PT homepage broken bug fix

CRITICAL bug: pt/index.html only has 1 of 11 cat-cards (Guarda only).
PT users land on the Brazilian homepage and see almost no content.
EN/JA both have 11 cat-cards with ~150 technique links each.

Fix:
  - Take en/index.html cat-card structure as source of truth
  - Translate category headings to PT
  - For each tech link, look up the PT page's h1 (or fallback to EN label)
  - Insert all 11 cards into pt/index.html

Idempotent: only patches if pt/index.html has < 5 cat-cards.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CAT_PT = {
    "Choke": "Estrangulamento",
    "Defense": "Defesa",
    "Escape": "Fuga",
    "Guard": "Guarda",
    "Joint Lock": "Chave de Articulação",
    "Leg Lock": "Chave de Perna",
    "Passing": "Passagem",
    "Position": "Posição",
    "Sweep": "Raspagem",
    "Takedown": "Queda",
    "Transition": "Transição",
}

# Common technique label PT translations (curated, verified terms)
TECH_PT = {
    "Rear Naked Choke": "Mata-Leão",
    "Triangle Choke": "Triângulo",
    "Guillotine Choke": "Guilhotina",
    "Bow and Arrow Choke": "Estrangulamento Arco e Flecha",
    "Ezekiel Choke": "Ezequiel",
    "D'Arce Choke": "D'Arce",
    "Anaconda Choke": "Anaconda",
    "Loop Choke": "Loop",
    "Arm Triangle Choke": "Estrangulamento de Braço",
    "North-South Choke": "Norte-Sul",
    "Baseball Choke": "Baseball",
    "Cross Collar Choke": "Estrangulamento de Gola Cruzada",
    "Clock Choke": "Relógio",
    "Lapel Choke": "Lapela",
    "Guard Retention": "Retenção de Guarda",
    "Hip Escape": "Fuga de Quadril",
    "Frame": "Frame",
    "Sprawl": "Sprawl",
    "Back Defense": "Defesa das Costas",
    "Shrimp Escape": "Camarão",
    "Bridge and Roll": "Ponte e Rolamento",
    "Elbow-Knee Escape": "Cotovelo-Joelho",
    "Closed Guard": "Guarda Fechada",
    "Open Guard": "Guarda Aberta",
    "Half Guard": "Meia Guarda",
    "Spider Guard": "Guarda Aranha",
    "De La Riva Guard": "Guarda De La Riva",
    "Berimbolo": "Berimbolo",
    "Butterfly Guard": "Guarda Borboleta",
    "Rubber Guard": "Guarda Borracha",
    "X-Guard": "Guarda X",
    "Worm Guard": "Worm Guard",
    "Reverse De La Riva": "De La Riva Invertida",
    "50/50 Guard": "Guarda 50/50",
    "Lasso Guard": "Guarda Lasso",
    "Deep Half Guard": "Meia Guarda Profunda",
    "Z-Guard": "Guarda Z",
    "Sitting Guard": "Guarda Sentada",
    "Armbar": "Chave de Braço",
    "Kimura": "Kimura",
    "Americana": "Americana",
    "Omoplata": "Omoplata",
    "Wrist Lock": "Chave de Punho",
    "Straight Armbar": "Chave de Braço Reta",
    "Monoplata": "Monoplata",
    "Heel Hook": "Heel Hook",
    "Inside Heel Hook": "Heel Hook Interno",
    "Outside Heel Hook": "Heel Hook Externo",
    "Knee Bar": "Chave de Joelho",
    "Toe Hold": "Toe Hold",
    "Calf Slicer": "Calf Slicer",
    "Ankle Lock": "Chave de Tornozelo",
    "Estima Lock": "Estima Lock",
    "Guard Pass": "Passagem de Guarda",
    "Torreando Pass": "Toreando",
    "Knee Slice Pass": "Knee Slice",
    "Leg Drag Pass": "Leg Drag",
    "Headquarters Pass": "Headquarters",
    "Stack Pass": "Stack Pass",
    "Double Under Pass": "Double Under",
    "Pressure Pass": "Pressão",
    "Smash Pass": "Smash",
    "X-Pass": "X-Pass",
    "Mount": "Montada",
    "Back Mount": "Costas",
    "Side Control": "100 Quilos",
    "North-South": "Norte-Sul",
    "Knee on Belly": "Joelho na Barriga",
    "S-Mount": "S-Mount",
    "Modified Mount": "Montada Modificada",
    "Body Triangle": "Triângulo de Corpo",
    "Turtle Position": "Tartaruga",
    "Seat Belt Control": "Cinto de Segurança",
    "Front Headlock": "Front Headlock",
    "Underhook": "Underhook",
    "Overhook": "Overhook",
    "Scissor Sweep": "Raspagem Tesoura",
    "Flower Sweep": "Raspagem Flor",
    "Hip Bump Sweep": "Bate de Quadril",
    "Pendulum Sweep": "Pêndulo",
    "Tripod Sweep": "Tripé",
    "Elevator Sweep": "Elevador",
    "Sickle Sweep": "Foice",
    "Overhead Sweep": "Raspagem por Cima",
    "Balloon Sweep": "Balão",
    "X-Guard Sweep": "Raspagem da Guarda X",
    "Double Leg Takedown": "Queda Dupla",
    "Single Leg Takedown": "Queda Simples",
    "Osoto Gari": "Osoto Gari",
    "Ankle Pick": "Pegada de Tornozelo",
    "Harai Goshi": "Harai Goshi",
    "Ippon Seoi Nage": "Ippon Seoi Nage",
    "Morote Seoi Nage": "Morote Seoi Nage",
    "Snap Down": "Snap Down",
    "Russian Tie": "Russian Tie",
    "Arm Drag": "Arm Drag",
    "Granby Roll": "Rolamento Granby",
    "Back Take": "Pegada das Costas",
    "Technical Stand-Up": "Levantada Técnica",
    "Stand In Base": "Em Base",
}


def patch_pt_index() -> str:
    en_path = REPO_ROOT / "en" / "index.html"
    pt_path = REPO_ROOT / "pt" / "index.html"
    en = en_path.read_text(encoding="utf-8")
    pt = pt_path.read_text(encoding="utf-8")

    # Idempotent guard
    pt_card_count = len(re.findall(r'class="cat-card"', pt))
    if pt_card_count >= 5:
        return f"already-{pt_card_count}-cards"

    # Extract all EN cat-cards (full markup)
    en_cards = re.findall(
        r'<div class="cat-card"><h2>([^<]+)</h2><div class="tech-links">(.*?)</div></div>',
        en, re.DOTALL,
    )
    if len(en_cards) < 5:
        return "skip-en-source-missing"

    # Build PT replacement
    pt_cards_html = ""
    for cat_en, links_html in en_cards:
        cat_pt = CAT_PT.get(cat_en, cat_en)
        # Translate each link label, keep href intact
        def translate_link(m: re.Match) -> str:
            href = m.group(1)
            label_en = m.group(2)
            label_pt = TECH_PT.get(label_en, label_en)
            return f'<a href="{href}">{label_pt}</a>'
        pt_links = re.sub(
            r'<a href="([^"]+)">([^<]+)</a>',
            translate_link,
            links_html,
        )
        pt_cards_html += (
            f'<div class="cat-card"><h2>{cat_pt}</h2>'
            f'<div class="tech-links">{pt_links}</div></div>'
        )

    # Replace the existing single cat-card with the full set
    new_pt, n = re.subn(
        r'<div class="cat-card">.*?</div></div>',
        pt_cards_html,
        pt, count=1, flags=re.DOTALL,
    )
    if n == 0:
        return "skip-no-cat-card-anchor"
    pt_path.write_text(new_pt, encoding="utf-8")
    return f"patched ({len(en_cards)} cards added)"


if __name__ == "__main__":
    result = patch_pt_index()
    print(f"PT index fix: {result}")
