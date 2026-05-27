#!/usr/bin/env python3
"""Add batch 377-381 article cards to index.html files."""

import os
import re

SITE_DIR = "/sessions/keen-sharp-davinci/mnt/Claude/bjj-wiki"

# 5 new articles with titles and descriptions per language
ARTICLES = {
    "en": [
        ("bjj-attacking-from-turtle.html", "🐢 Attacking from Turtle", "Master top & bottom turtle attacks and granby roll systems"),
        ("bjj-conditioning-science.html", "⚡ Conditioning Science", "Energy systems, VO2 max, HRV & periodization strategies"),
        ("bjj-guard-setups-masterclass.html", "🎓 Guard Setups Masterclass", "Entry systems for closed, half, butterfly, DLR & spider guard"),
        ("bjj-back-control-finishing.html", "🔚 Back Control Finishing", "RNC, bow-and-arrow & body triangle mastery"),
        ("bjj-sweeps-to-submissions.html", "⛓️ Sweeps to Submissions", "Chain sweeps into immediate submission attacks"),
    ],
    "ja": [
        ("bjj-attacking-from-turtle.html", "🐢 タートルポジション攻撃", "トップ・ボトムタートル攻撃とグランビーロール"),
        ("bjj-conditioning-science.html", "⚡ コンディショニング科学", "エネルギーシステム・VO2max・HRV・ピリオダイゼーション"),
        ("bjj-guard-setups-masterclass.html", "🎓 ガードセットアップ", "クローズド・ハーフ・バタフライ・DLR・スパイダー"),
        ("bjj-back-control-finishing.html", "🔚 バックコントロール・フィニッシング", "RNC・ボウアンドアロー・ボディトライアングル"),
        ("bjj-sweeps-to-submissions.html", "⛓️ スウィープからサブミッション", "掃き技から即座のサブミッション攻撃"),
    ],
    "pt": [
        ("bjj-attacking-from-turtle.html", "🐢 Ataque da Tartaruga", "Ataques de tartaruga no topo, fundo e granby roll"),
        ("bjj-conditioning-science.html", "⚡ Ciência do Condicionamento", "Sistemas de energia, VO2 máximo, HRV e periodização"),
        ("bjj-guard-setups-masterclass.html", "🎓 Setups de Guard", "Entradas para guard fechado, meio, butterfly, DLR e aranha"),
        ("bjj-back-control-finishing.html", "🔚 Acabamento de Costas", "RNC, arco-e-flecha e triângulo de corpo"),
        ("bjj-sweeps-to-submissions.html", "⛓️ Sweeps para Submissões", "Encadeie sweeps em submissões imediatas"),
    ]
}

def add_cards_to_index(lang_code):
    """Add new cards to the 📚 New Guides section in index.html."""
    index_path = os.path.join(SITE_DIR, lang_code, "index.html")

    if not os.path.exists(index_path):
        print(f"⚠️  {lang_code}/index.html not found")
        return

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Create new card entries in the format used in the "New Guides" section
    new_cards_html = ""
    for href, title, desc in ARTICLES[lang_code]:
        card = f'<a href="{href}" style="display:block;background:#111827;border:1px solid #1e2a3a;border-radius:10px;padding:16px;text-decoration:none;transition:border-color .2s" onmouseover="this.style.borderColor=\'#e2b714\'" onmouseout="this.style.borderColor=\'#1e2a3a\'"><strong style="color:#e2b714">{title}</strong><p style="color:#aaa;font-size:.85rem;margin-top:4px">{desc}</p></a>'
        new_cards_html += card

    # Find the position to insert: after the opening <div style="display:grid;..."> in the "New Guides" section
    # Different language versions use different headers
    headers = {
        "en": r'<h2 style="color:#e2b714;margin-bottom:16px">📚 New Guides</h2>',
        "ja": r'<h2 style="color:#e2b714;margin-bottom:16px">📚 新着ガイド</h2>',
        "pt": r'<h2 style="color:#e2b714;margin-bottom:16px">📚 New Guides</h2>',
    }

    header_pattern = headers.get(lang_code, r'<h2[^>]*>📚[^<]*</h2>')

    match = re.search(header_pattern + r'\s*<div style="display:grid;[^"]*">', content, re.DOTALL)

    if match:
        insertion_point = match.end()
        # Insert new cards right after the opening div
        content = content[:insertion_point] + new_cards_html + content[insertion_point:]

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ {lang_code}: Added 5 cards to 📚 section")
    else:
        print(f"⚠️  {lang_code}: Could not find section header in index.html")

def main():
    """Add cards to all language index files."""
    for lang in ["en", "ja", "pt"]:
        add_cards_to_index(lang)

if __name__ == "__main__":
    main()
