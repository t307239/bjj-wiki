#!/usr/bin/env python3
"""
rebuild_pt_index.py — z255ss-fix: pt/index.html の content drift 修正

旧: pt/index.html は chip が 1 件のみ (Guarda Fechada)、en/ja は 104 件 = catastrophic drift
修正: en/index.html を base に PT meta + PT category heading + PT chip 翻訳で
     完全再生成 (header / language switcher / footer は構造そのまま)

Idempotent: 既に rebuild 済 (chip 数 ≥ 100) なら skip。
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# fix_index_chip_labels.py と同期 (DRY: import して使う)
import sys
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from fix_index_chip_labels import TRANSLATIONS  # type: ignore

# fix_index_design_drift.py の category 翻訳 (PT 抜粋)
CATEGORY_PT = {
    "Choke": "Estrangulamentos",
    "Defense": "Defesa",
    "Escape": "Fugas",
    "Guard": "Guarda",
    "Joint Lock": "Chave de Articulação",
    "Leg Lock": "Chave de Perna",
    "Passing": "Passagem de Guarda",
    "Position": "Posições",
    "Sweep": "Raspagens",
    "Takedown": "Quedas",
    "Transition": "Transições",
}

# PT meta strings
PT_TITLE = "Todas as Técnicas de BJJ | BJJ Wiki"
PT_OG_TITLE = "Todas as Técnicas de BJJ"
PT_DESC = "Enciclopédia completa de técnicas de Jiu-Jitsu Brasileiro. Aprenda guardas, passagens, finalizações e muito mais."
PT_H1 = "Todas as Técnicas de BJJ"


def main():
    en_fp = REPO_ROOT / "en" / "index.html"
    pt_fp = REPO_ROOT / "pt" / "index.html"

    en_html = en_fp.read_text(encoding="utf-8")
    pt_old = pt_fp.read_text(encoding="utf-8")
    chip_count_old = en_html.count('<a href="') - 4  # exclude header anchors

    # idempotency guard
    pt_chip_old = len(re.findall(r'<a href="[^"]+\.html">', pt_old))
    if pt_chip_old >= 100:
        print(f"  ✅ pt/index.html already rebuilt ({pt_chip_old} chips), skipping")
        return

    # Step 1: copy en/index.html structure
    pt_new = en_html

    # Step 2: change html lang
    pt_new = pt_new.replace('<html lang="en">', '<html lang="pt">')

    # Step 3: meta strings (title / og:title / twitter:title / og:url / canonical)
    pt_new = pt_new.replace("All BJJ Techniques | BJJ Wiki", PT_TITLE)
    pt_new = pt_new.replace(
        '<meta property="og:url" content="https://wiki.bjj-app.net/en/index.html">',
        '<meta property="og:url" content="https://wiki.bjj-app.net/pt/index.html">',
    )
    pt_new = pt_new.replace(
        '<meta property="og:title" content="All BJJ Techniques">',
        f'<meta property="og:title" content="{PT_OG_TITLE}">',
    )
    pt_new = pt_new.replace(
        '<meta property="og:description" content="Complete encyclopedia of Brazilian Jiu-Jitsu techniques. Learn guards, passes, submissions, sweeps and more.">',
        f'<meta property="og:description" content="{PT_DESC}">',
    )
    pt_new = pt_new.replace(
        '<meta name="twitter:title" content="All BJJ Techniques">',
        f'<meta name="twitter:title" content="{PT_OG_TITLE}">',
    )
    pt_new = pt_new.replace(
        '<meta name="twitter:description" content="Complete encyclopedia of Brazilian Jiu-Jitsu techniques. Learn guards, passes, submissions, sweeps and more.">',
        f'<meta name="twitter:description" content="{PT_DESC}">',
    )
    pt_new = pt_new.replace(
        '<meta name="description" content="Complete encyclopedia of Brazilian Jiu-Jitsu techniques. Learn guards, passes, submissions, sweeps and more.">',
        f'<meta name="description" content="{PT_DESC}">',
    )
    pt_new = pt_new.replace(
        '<link rel="canonical" href="https://wiki.bjj-app.net/en/index.html">',
        '<link rel="canonical" href="https://wiki.bjj-app.net/pt/index.html">',
    )

    # Step 4: BreadcrumbList JSON-LD
    pt_new = pt_new.replace(
        '"name":"All BJJ Techniques","item":"https://wiki.bjj-app.net/en/index.html"',
        f'"name":"{PT_OG_TITLE}","item":"https://wiki.bjj-app.net/pt/index.html"',
    )

    # Step 5: language switcher (active class swap)
    pt_new = pt_new.replace(
        '<a href="../en/index.html" class="active">🇺🇸 EN</a><a href="../ja/index.html">🇯🇵 JA</a><a href="../pt/index.html">🇧🇷 PT</a>',
        '<a href="../en/index.html">🇺🇸 EN</a><a href="../ja/index.html">🇯🇵 JA</a><a href="../pt/index.html" class="active">🇧🇷 PT</a>',
    )

    # Step 6: h1 + subtitle
    pt_new = pt_new.replace(
        "<h1>All BJJ Techniques</h1>",
        f"<h1>{PT_H1}</h1>",
    )
    pt_new = pt_new.replace(
        '<p class="subtitle">Complete encyclopedia of Brazilian Jiu-Jitsu techniques. Learn guards, passes, submissions, sweeps and more.</p>',
        f'<p class="subtitle">{PT_DESC}</p>',
    )

    # Step 7: category headings
    for en_cat, pt_cat in CATEGORY_PT.items():
        pt_new = pt_new.replace(f"<h2>{en_cat}</h2>", f"<h2>{pt_cat}</h2>")

    # Step 8: chip labels (sorted by length desc to avoid substring conflicts)
    for en_name in sorted(TRANSLATIONS.keys(), key=lambda s: -len(s)):
        target = TRANSLATIONS[en_name].get("pt")
        if not target:
            continue
        # callable replacement (avoid \1 + digit interpretation bug)
        pattern = (
            r'(<a href="[^"]+\.html">)'
            + re.escape(en_name)
            + r"(</a>)"
        )
        def make_replacer(t: str):
            return lambda m: m.group(1) + t + m.group(2)
        pt_new = re.sub(pattern, make_replacer(target), pt_new)

    pt_fp.write_text(pt_new, encoding="utf-8")
    pt_chip_new = len(re.findall(r'<a href="[^"]+\.html">', pt_new))
    print(f"  ✅ pt/index.html rebuilt: {pt_chip_old} → {pt_chip_new} chips")


if __name__ == "__main__":
    main()
