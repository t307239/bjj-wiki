#!/usr/bin/env python3
"""Add index cards for Batch 206-220 to all language index.html files."""

import os
import re

BASE_DIR = '/sessions/keen-sharp-davinci/mnt/bjj-wiki'

# Sample of new pages for visibility on index (pick 15 most relevant)
CARDS = {
    'en': [
        ('bjj-ashi-garami-setup.html', 'Ashi Garami Setups', 'Master ashi garami position attacks'),
        ('bjj-guard-to-top-transition.html', 'Guard to Top Transition', 'Smooth position transitions'),
        ('bjj-posture-in-closed-guard.html', 'Posture Defense', 'Prevent submissions with posture'),
        ('bjj-folding-pass-guide.html', 'Folding Pass Guide', 'Master the smash pass'),
        ('bjj-flexibility-training.html', 'Flexibility Training', 'Improve BJJ mobility'),
        ('bjj-safe-training-guide.html', 'Safe Training Guide', 'Injury prevention fundamentals'),
        ('bjj-first-competition-guide.html', 'First Competition Guide', 'Complete competition prep'),
        ('bjj-rear-naked-choke-detail.html', 'RNC Deep Dive', 'Master finishing position'),
        ('bjj-guard-engagement-bjj.html', 'Guard Engagement', 'Proper guard control'),
        ('bjj-explosive-bjj-game.html', 'Explosive Game', 'Develop explosive power'),
        ('bjj-confidence-bjj.html', 'Build Confidence', 'Mental strength in BJJ'),
        ('bjj-teaching-bjj.html', 'Teaching BJJ', 'Share knowledge with others'),
        ('bjj-curriculum-bjj.html', 'Curriculum Design', 'Structure BJJ classes'),
        ('bjj-belt-promotion-criteria.html', 'Belt Promotion Criteria', 'Standards for advancement'),
        ('bjj-legacy-in-bjj.html', 'Legacy Building', 'Your BJJ journey impact'),
    ],
    'ja': [
        ('bjj-ashi-garami-setup.html', 'アシガラミセットアップ', 'アシガラミ技術をマスター'),
        ('bjj-guard-to-top-transition.html', 'ガード→トップ移行', 'ポジション移行のコツ'),
        ('bjj-posture-in-closed-guard.html', 'クローズドガード体勢', 'サブミッション防御'),
        ('bjj-folding-pass-guide.html', 'フォールディングパス', 'クローズドガード崩し'),
        ('bjj-flexibility-training.html', '柔軟性トレーニング', 'BJJの可動域改善'),
        ('bjj-safe-training-guide.html', '安全なトレーニング', '怪我予防の原則'),
        ('bjj-first-competition-guide.html', '初試合ガイド', '試合完全準備'),
        ('bjj-rear-naked-choke-detail.html', 'RNC深掘り', 'フィニッシュの極意'),
        ('bjj-guard-engagement-bjj.html', 'ガード抱え込み', 'ガードコントロール'),
        ('bjj-explosive-bjj-game.html', '爆発的なゲーム', '爆発力を開発'),
        ('bjj-confidence-bjj.html', '自信構築', 'BJJのメンタル'),
        ('bjj-teaching-bjj.html', 'BJJを教える', '知識を共有'),
        ('bjj-curriculum-bjj.html', 'カリキュラム設計', 'クラス構成'),
        ('bjj-belt-promotion-criteria.html', '帯昇格基準', '昇格の基準'),
        ('bjj-legacy-in-bjj.html', 'レガシー構築', 'BJJでの貢献'),
    ],
    'pt': [
        ('bjj-ashi-garami-setup.html', 'Setups de Ashi Garami', 'Domine a posição'),
        ('bjj-guard-to-top-transition.html', 'Transição Guarda-Cima', 'Transições suaves'),
        ('bjj-posture-in-closed-guard.html', 'Postura de Defesa', 'Previna submissões'),
        ('bjj-folding-pass-guide.html', 'Folding Pass', 'Domine o smash pass'),
        ('bjj-flexibility-training.html', 'Flexibilidade para BJJ', 'Melhore mobilidade'),
        ('bjj-safe-training-guide.html', 'Treinamento Seguro', 'Prevenção de lesões'),
        ('bjj-first-competition-guide.html', 'Primeira Competição', 'Preparação completa'),
        ('bjj-rear-naked-choke-detail.html', 'RNC Detalhado', 'Finalize com maestria'),
        ('bjj-guard-engagement-bjj.html', 'Guard Engagement', 'Controle de guarda'),
        ('bjj-explosive-bjj-game.html', 'Jogo Explosivo', 'Desenvolva explosividade'),
        ('bjj-confidence-bjj.html', 'Confiança em BJJ', 'Força mental'),
        ('bjj-teaching-bjj.html', 'Ensinando BJJ', 'Compartilhe conhecimento'),
        ('bjj-curriculum-bjj.html', 'Design de Currículo', 'Estruture as aulas'),
        ('bjj-belt-promotion-criteria.html', 'Critérios de Promoção', 'Padrões de avanço'),
        ('bjj-legacy-in-bjj.html', 'Construir Legado', 'Impacto na comunidade'),
    ],
}

def add_index_cards(lang, cards_list):
    """Add cards to New Guides section in index.html."""
    path = os.path.join(BASE_DIR, lang, 'index.html')
    if not os.path.exists(path):
        print(f"[{lang}] ❌ index.html not found")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the New Guides section div
    pattern = r'(<h2 style="color:#e2b714;margin-bottom:16px">📚 New Guides</h2>\s*<div style="display:grid;grid-template-columns:repeat\(auto-fill,minmax\(240px,1fr\)\);gap:12px">)'
    match = re.search(pattern, content)
    if not match:
        print(f"[{lang}] ❌ New Guides section not found")
        return

    # Find the position after the opening div
    insert_pos = match.end()

    # Build the new card HTML lines to insert
    cards_html = ''
    for slug, title, desc in cards_list:
        # Build card with proper styling
        cards_html += f'<a href="{slug}" style="display:block;background:#111827;border:1px solid #1e2a3a;border-radius:10px;padding:16px;text-decoration:none;transition:border-color .2s" onmouseover="this.style.borderColor=\'#e2b714\'" onmouseout="this.style.borderColor=\'#1e2a3a\'"><strong style="color:#e2b714">{title}</strong><p style="color:#aaa;font-size:.85rem;margin-top:4px">{desc}</p></a>'

    # Insert the new cards
    new_content = content[:insert_pos] + cards_html + content[insert_pos:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"[{lang}] ✅ Added {len(cards_list)} index cards")

def main():
    """Add cards to all language index files."""
    for lang in ['en', 'ja', 'pt']:
        if lang in CARDS:
            add_index_cards(lang, CARDS[lang])

    print(f"\n✅ All index cards added (Batches 206-220)")

if __name__ == '__main__':
    main()
