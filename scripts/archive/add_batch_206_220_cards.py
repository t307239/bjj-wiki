#!/usr/bin/env python3
"""Add Batch 206-220 index cards to all language index.html files."""

import os

BASE_DIR = '/sessions/keen-sharp-davinci/mnt/bjj-wiki'

CARDS = {
    'en': [
        ('bjj-ashi-garami-setup.html', 'Ashi Garami Setups', 'Learn proper ashi garami position setups.'),
        ('bjj-collar-tie-takedowns.html', 'Collar Tie Takedowns', 'Clinch takedown chains and control.'),
        ('bjj-guard-to-top-transition.html', 'Guard to Top Transitions', 'Smooth position transitions.'),
        ('bjj-posture-in-closed-guard.html', 'Posture to Prevent Subs', 'Defend submissions with posture.'),
        ('bjj-folding-pass-guide.html', 'Folding Pass (Smash)', 'Master the folding guard pass.'),
        ('bjj-flexibility-training.html', 'Flexibility for BJJ', 'Improve range of motion.'),
        ('bjj-safe-training-guide.html', 'Safe Training Guide', 'Injury prevention essentials.'),
        ('bjj-lumberjack-sweep.html', 'Lumberjack Sweep', 'Escape bottom with sweeps.'),
        ('bjj-first-competition-guide.html', 'First Competition Guide', 'Complete competition prep.'),
        ('bjj-rear-naked-choke-detail.html', 'RNC Details', 'Master the finishing position.'),
        ('bjj-guard-engagement-bjj.html', 'Guard Engagement', 'Proper guard engagement.'),
        ('bjj-leg-pummeling-bjj.html', 'Leg Pummeling', 'Guard transition techniques.'),
        ('bjj-explosive-bjj-game.html', 'Explosive BJJ Game', 'Develop explosive techniques.'),
        ('bjj-confidence-bjj.html', 'Building Confidence', 'Mental game fundamentals.'),
        ('bjj-teaching-bjj.html', 'Teaching BJJ', 'Share your knowledge.'),
    ],
    'ja': [
        ('bjj-ashi-garami-setup.html', '【BJJ】アシガラミセットアップ', 'アシガラミの基本的なセットアップ。'),
        ('bjj-collar-tie-takedowns.html', '【BJJ】カラータイテイクダウン', 'クリンチテイクダウンのチェーン。'),
        ('bjj-guard-to-top-transition.html', '【BJJ】ガードからトップへの移行', 'スムーズなポジション移行。'),
        ('bjj-posture-in-closed-guard.html', '【BJJ】クローズドガードの体勢', 'サブミッション防御の体勢。'),
        ('bjj-folding-pass-guide.html', '【BJJ】フォールディングパス', 'ガード潰しパスをマスター。'),
        ('bjj-flexibility-training.html', '【BJJ】柔軟性トレーニング', '可動域を改善。'),
        ('bjj-safe-training-guide.html', '【BJJ】安全なトレーニング', '怪我予防の基本。'),
        ('bjj-lumberjack-sweep.html', '【BJJ】ランバージャックスイープ', 'ボトムからのエスケープ。'),
        ('bjj-first-competition-guide.html', '【BJJ】初試合ガイド', '試合完全準備。'),
        ('bjj-rear-naked-choke-detail.html', '【BJJ】リアネイキッドチョーク', 'フィニッシュの極意。'),
        ('bjj-guard-engagement-bjj.html', '【BJJ】ガードエンゲージメント', 'ガード抱え込み技術。'),
        ('bjj-leg-pummeling-bjj.html', '【BJJ】レッグパンメリング', 'ガード移行技術。'),
        ('bjj-explosive-bjj-game.html', '【BJJ】爆発的なBJJゲーム', '爆発力を開発。'),
        ('bjj-confidence-bjj.html', '【BJJ】自信構築', 'メンタルの基本。'),
        ('bjj-teaching-bjj.html', '【BJJ】BJJを教える', '知識を共有。'),
    ],
    'pt': [
        ('bjj-ashi-garami-setup.html', 'Setups de Ashi Garami', 'Aprenda os setups fundamentais.'),
        ('bjj-collar-tie-takedowns.html', 'Projeções de Collar Tie', 'Cadeias de projeções clinch.'),
        ('bjj-guard-to-top-transition.html', 'Transições Guarda para Cima', 'Transições de posição suave.'),
        ('bjj-posture-in-closed-guard.html', 'Postura em Guarda Fechada', 'Defenda submissões.'),
        ('bjj-folding-pass-guide.html', 'Folding Pass', 'Domine o folding pass.'),
        ('bjj-flexibility-training.html', 'Flexibilidade para BJJ', 'Melhore amplitude.'),
        ('bjj-safe-training-guide.html', 'Guia de Treinamento Seguro', 'Prevenção de lesões.'),
        ('bjj-lumberjack-sweep.html', 'Lumberjack Sweep', 'Escape de baixo.'),
        ('bjj-first-competition-guide.html', 'Guia Primeira Competição', 'Preparação completa.'),
        ('bjj-rear-naked-choke-detail.html', 'Detalhes do RNC', 'Finalize com maestria.'),
        ('bjj-guard-engagement-bjj.html', 'Guard Engagement', 'Apropriação de guarda.'),
        ('bjj-leg-pummeling-bjj.html', 'Leg Pummeling', 'Técnicas de transição.'),
        ('bjj-explosive-bjj-game.html', 'Jogo Explosivo', 'Desenvolva explosividade.'),
        ('bjj-confidence-bjj.html', 'Construir Confiança', 'Fundamentos mentais.'),
        ('bjj-teaching-bjj.html', 'Ensinando BJJ', 'Compartilhe conhecimento.'),
    ],
}

def add_cards(lang, cards_list, anchor_slug):
    """Add cards after anchor slug in index.html."""
    path = os.path.join(BASE_DIR, lang, 'index.html')
    if not os.path.exists(path):
        print(f"[{lang}] ❌ index.html not found")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find anchor
    anchor_pattern = f'href="{anchor_slug}"'
    idx = content.find(anchor_pattern)
    if idx == -1:
        print(f"[{lang}] ❌ Anchor {anchor_slug} not found")
        return

    # Find closing </a> tag
    close_a = content.find('</a>', idx)
    insert_pos = close_a + len('</a>')

    # Build cards HTML
    cards_html = '\n'
    for slug, title, desc in cards_list:
        cards_html += f'''      <a href="{slug}" style="background:#111827;border:1px solid #1e2a3a;border-radius:10px;padding:16px;text-decoration:none;display:block;margin-bottom:10px">
        <div style="color:#e2b714;font-weight:700;margin-bottom:4px">{title}</div>
        <div style="color:#9ca3af;font-size:.88rem">{desc}</div>
      </a>\n'''

    # Insert
    new_content = content[:insert_pos] + cards_html + content[insert_pos:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"[{lang}] ✅ Added {len(cards_list)} cards after {anchor_slug}")

def main():
    """Add all batch cards to all language indices."""
    # Determine anchor slug (last page of batch 205)
    anchor = 'bjj-legacy-in-bjj.html'  # Last page from batch 220

    for lang in ['en', 'ja', 'pt']:
        if lang in CARDS:
            add_cards(lang, CARDS[lang], anchor)

    print(f"\n✅ Index cards added for all languages")

if __name__ == '__main__':
    main()
