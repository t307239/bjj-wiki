#!/usr/bin/env python3
"""
Add index.html Featured Guides cards for Batch 191-205 new pages
Anchor to last pages: Batch 191-205 terminal slugs
"""

import os
import re

BASE_DIR = "/sessions/keen-sharp-davinci/mnt/bjj-wiki"

# Batch 191-205 key pages to feature (milestone pages only)
FEATURES = {
    "en": [
        ("bjj-passing-closed-guard", "Passing Closed Guard", "Master guard passing fundamentals"),
        ("bjj-no-gi-clinch-guide", "No-Gi Clinch Mastery", "Clinch control for no-gi grappling"),
        ("bjj-mastery-concepts", "BJJ Mastery Framework", "Advanced conceptual understanding"),
        ("bjj-sensitivity-training", "Sensitivity Training", "Develop tactical feel and intuition"),
    ],
    "ja": [
        ("bjj-passing-closed-guard", "クローズドガードパス", "ガードパスの基本をマスター"),
        ("bjj-no-gi-clinch-guide", "ノーギクリンチマスタリー", "ノーギグラップリング用クリンチ"),
        ("bjj-mastery-concepts", "BJJマスタリーフレームワーク", "高度な概念理解"),
        ("bjj-sensitivity-training", "センシティビティトレーニング", "タクティカルな感覚を養う"),
    ],
    "pt": [
        ("bjj-passing-closed-guard", "Passagem de Guarda Fechada", "Domine os fundamentos de passagem"),
        ("bjj-no-gi-clinch-guide", "Domínio do Clinch No-Gi", "Controle de clinch para grappling"),
        ("bjj-mastery-concepts", "Framework de Maestría em BJJ", "Compreensão conceitual avançada"),
        ("bjj-sensitivity-training", "Treinamento de Sensibilidade", "Desenvolva sensação tática e intuição"),
    ],
}

def add_featured_guides(lang):
    """Add featured guides cards to index.html"""
    index_path = f"{BASE_DIR}/{lang}/index.html"

    if not os.path.exists(index_path):
        print(f"  ❌ {lang}/index.html not found")
        return

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if already has Featured Guides section
    if "Featured Guides" not in content and "特集ガイド" not in content and "Guias em Destaque" not in content:
        print(f"  ⚠️  {lang}/index.html has no Featured Guides section")
        return

    # Build cards HTML
    cards_html = ""
    for slug, title, desc in FEATURES[lang]:
        cards_html += f'''<div style="background:#111827;border:1px solid #1e2a3a;border-radius:10px;padding:16px;flex:1;min-width:200px">
  <h3 style="color:#e2b714;font-size:.95rem;margin-bottom:8px">{title}</h3>
  <p style="color:#9ca3af;font-size:.85rem;margin-bottom:12px">{desc}</p>
  <a href="{slug}.html" style="color:#e2b714;text-decoration:none;font-weight:700;font-size:.85rem">Learn More →</a>
</div>
'''

    # Try to insert before closing </div> of main container (but keep footer separate)
    pattern = r'(<div class="aff-box">\s*<p>📚.*?</a>\s*</div>)'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        insert_point = match.end()
        new_section = f'''
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin:40px 0">
  <h2 style="grid-column:1/-1;color:#e2b714;font-size:1.3rem;margin-bottom:0">New Batch 191-205 Guides</h2>
{cards_html}
</div>
'''
        content = content[:insert_point] + new_section + content[insert_point:]

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✅ {lang}/index.html updated with {len(FEATURES[lang])} feature cards")
    else:
        print(f"  ⚠️  {lang}/index.html structure unclear, skipping")

# Run
print("=" * 80)
print("Adding Featured Guides Cards (Batch 191-205)")
print("=" * 80)

for lang in ["en", "ja", "pt"]:
    add_featured_guides(lang)

print("\n✅ Index card updates complete")
