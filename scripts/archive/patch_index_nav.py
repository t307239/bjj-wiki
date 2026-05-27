#!/usr/bin/env python3
"""
Add new pillar page cards to Featured Guides section in index.html for en/ja/pt.
"""
import os, re

NEW_CARDS = {
    'en': [
        ('belt-system', 'bjj-belt-system.html', '🥋 Belt System', 'White belt to black belt'),
        ('terminology', 'bjj-terminology.html', '📖 BJJ Glossary', '50+ essential terms'),
        ('rules', 'bjj-rules-for-beginners.html', '📋 Competition Rules', 'Points, fouls & scoring'),
        ('vs-wrestling', 'bjj-vs-wrestling.html', '🤼 BJJ vs Wrestling', 'Full comparison guide'),
        ('training-tips', 'bjj-training-tips.html', '⚡ Training Tips', '15 ways to improve faster'),
        ('gi-guide', 'best-bjj-gi-guide.html', '👘 Best Gi Guide', 'Find the right kimono'),
    ],
    'ja': [
        ('belt-system', 'bjj-belt-system.html', '🥋 帯制度ガイド', '白帯から黒帯まで'),
        ('terminology', 'bjj-terminology.html', '📖 BJJ用語集', '50以上の必須用語'),
        ('rules', 'bjj-rules-for-beginners.html', '📋 競技ルール', 'ポイント・反則・採点'),
        ('vs-wrestling', 'bjj-vs-wrestling.html', '🤼 BJJ vs レスリング', '完全比較ガイド'),
        ('training-tips', 'bjj-training-tips.html', '⚡ トレーニングのコツ', '15の上達法'),
        ('gi-guide', 'best-bjj-gi-guide.html', '👘 道衣ガイド', '自分に合った道衣を選ぶ'),
    ],
    'pt': [
        ('belt-system', 'bjj-belt-system.html', '🥋 Sistema de Faixas', 'Da branca à preta'),
        ('terminology', 'bjj-terminology.html', '📖 Terminologia BJJ', 'Mais de 50 termos'),
        ('rules', 'bjj-rules-for-beginners.html', '📋 Regras de Competição', 'Pontos e faltas'),
        ('vs-wrestling', 'bjj-vs-wrestling.html', '🤼 BJJ vs Wrestling', 'Guia de comparação'),
        ('training-tips', 'bjj-training-tips.html', '⚡ Dicas de Treino', '15 formas de evoluir'),
        ('gi-guide', 'best-bjj-gi-guide.html', '👘 Guia do Kimono', 'Escolha o gi certo'),
    ],
}

fixed = 0
for lang in ['en', 'ja', 'pt']:
    path = f'{lang}/index.html'
    if not os.path.exists(path):
        continue
    with open(path) as f:
        content = f.read()

    # Find the existing featured guides grid and append new cards
    pattern = r'(<!-- Featured Guides -->.*?<div[^>]*grid[^>]*>)(.*?)(</div>\s*</section>)'
    m = re.search(pattern, content, re.DOTALL)
    if not m:
        print(f"{lang}: Featured Guides pattern not found")
        continue

    # Build new cards HTML, skipping any already present
    new_cards_html = ''
    for _, href, label, sublabel in NEW_CARDS[lang]:
        if href not in content:
            new_cards_html += f'<a href="{href}" class="feat-card"><span>{label}</span><small>{sublabel}</small></a>'

    if not new_cards_html:
        print(f"{lang}: all cards already present")
        continue

    # Insert before closing </div></section>
    new_content = content[:m.start(3)] + new_cards_html + content[m.start(3):]
    with open(path, 'w') as f:
        f.write(new_content)
    print(f"{lang}: added new pillar cards")
    fixed += 1

print(f"Updated {fixed} index.html files")
