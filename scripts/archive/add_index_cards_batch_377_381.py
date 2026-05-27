#!/usr/bin/env python3
"""Add batch 377-381 article cards to index.html files."""

import os
import re

SITE_DIR = "/sessions/keen-sharp-davinci/mnt/Claude/bjj-wiki"

# 5 new articles with titles per language
ARTICLES = {
    "en": {
        "bjj-attacking-from-turtle": "Attacking from Turtle Position",
        "bjj-conditioning-science": "BJJ Conditioning Science",
        "bjj-guard-setups-masterclass": "Guard Setups Masterclass",
        "bjj-back-control-finishing": "Back Control Finishing Details",
        "bjj-sweeps-to-submissions": "Sweeps to Submissions",
    },
    "ja": {
        "bjj-attacking-from-turtle": "タートルポジション攻撃",
        "bjj-conditioning-science": "BJJコンディショニング科学",
        "bjj-guard-setups-masterclass": "ガードセットアップマスタークラス",
        "bjj-back-control-finishing": "バックコントロール・フィニッシング",
        "bjj-sweeps-to-submissions": "スウィープからサブミッション",
    },
    "pt": {
        "bjj-attacking-from-turtle": "Ataque da Posição de Tartaruga",
        "bjj-conditioning-science": "Ciência do Condicionamento do BJJ",
        "bjj-guard-setups-masterclass": "Masterclass de Setups de Guard",
        "bjj-back-control-finishing": "Detalhes de Acabamento de Controle de Costas",
        "bjj-sweeps-to-submissions": "Sweeps para Submissões",
    }
}

def add_cards_to_index(lang_code):
    """Add new cards to index.html for specified language."""
    index_path = os.path.join(SITE_DIR, lang_code, "index.html")

    if not os.path.exists(index_path):
        print(f"⚠️  {lang_code}/index.html not found")
        return

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Create new card entries
    new_cards = []
    for article_key, title in ARTICLES[lang_code].items():
        card = f'<a class="tech-card" href="{article_key}.html"><span class="tech-name">{title}</span><span class="arrow">→</span></a>\n'
        new_cards.append(card)

    new_cards_html = "".join(new_cards)

    # Find the closing tech-grid div or last tech-card and insert before the closing div
    # Strategy: find last tech-card in index content and add after it

    # More robust: find last </a> before closing </div> in any cat-section
    # Insert before </div> that closes the last cat-section

    # Find all </div> tags and their contexts
    lines = content.split("\n")

    # Find the insertion point: look for closing </div> tags from cat-sections
    # Insert new cards in a "Featured" or "Latest" section or before final closing divs

    # Alternative: find the last tech-grid and insert cards there
    match = re.search(r'(<div class="cat-section"[^>]*>.*?</div>\s*)+(?=\s*<div class="aff-box")', content, re.DOTALL)

    if match:
        # Insert new cards right before the aff-box
        insertion_point = match.end()

        # Create a new section for batch 377-381
        new_section = f'''<div class="cat-section" data-cat="advanced">
  <div class="cat-header">
    <h2>Latest (Batch 377-381)</h2><span class="cat-count">5</span>
  </div>
  <div class="tech-grid">
{new_cards_html}  </div>
</div>
'''
        content = content[:insertion_point] + new_section + content[insertion_point:]

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ {lang_code}: Added 5 cards to index.html")
    else:
        print(f"⚠️  {lang_code}: Could not find insertion point in index.html")

def main():
    """Add cards to all language index files."""
    for lang in ["en", "ja", "pt"]:
        add_cards_to_index(lang)

if __name__ == "__main__":
    main()
