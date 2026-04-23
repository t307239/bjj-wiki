#!/usr/bin/env python3
"""
Generate BJJ Wiki Batch 382-386 (5 themes × 3 languages = 15 pages).
Topics:
  382: Attacking from Turtle Position (Advanced)
  383: BJJ Conditioning Science
  384: Guard Setups Masterclass
  385: Back Control - Finishing Details
  386: Sweeps to Submissions - Chain Mechanics
"""

import os
from datetime import datetime
from pathlib import Path

BATCHES = {
    382: {
        "slug": "bjj-attacking-from-turtle-advanced",
        "title_en": "Attacking from Turtle Position — Advanced Tactics",
        "title_ja": "タートル位置からの攻撃 — 上級戦術",
        "title_pt": "Ataques da Posição Tartaruga — Táticas Avançadas",
        "desc_en": "Master advanced offensive tactics when opponent is in turtle position. Learn finishing techniques, positioning strategies, and high-percentage submissions.",
        "desc_ja": "相手がタートル位置にいるときの高度な攻撃戦術をマスターします。フィニッシング技、ポジショニング戦略、高確率のサブミッションを学ぶ。",
        "desc_pt": "Domine táticas avançadas de ataque quando o oponente está em posição tartaruga. Aprenda técnicas de finalização, estratégias de posicionamento e finalizações de alta porcentagem.",
        "content_en": "Understanding turtle position attacks requires knowledge of base, pressure, and opportunistic submissions. This guide covers advanced setups and finishing sequences.",
        "content_ja": "タートル位置への攻撃を理解するには、ベース、プレッシャー、チャンス的なサブミッションの知識が必要です。本ガイドでは、高度なセットアップとフィニッシングシーケンスをカバーします。",
        "content_pt": "Entender ataques de posição tartaruga requer conhecimento de base, pressão e finalizações oportunas. Este guia cobre configurações avançadas e sequências de finalização.",
    },
    383: {
        "slug": "bjj-conditioning-science",
        "title_en": "BJJ Conditioning Science — Energy Systems & Adaptation",
        "title_ja": "BJJ コンディショニング科学 — エネルギーシステムと適応",
        "title_pt": "Ciência do Condicionamento em BJJ — Sistemas de Energia e Adaptação",
        "desc_en": "Scientific approach to BJJ conditioning. Learn energy system development, periodization principles, and adaptation protocols for optimal performance.",
        "desc_ja": "BJJコンディショニングへの科学的アプローチ。エネルギーシステムの開発、ピリオダイゼーション原理、最適なパフォーマンスのための適応プロトコルを学ぶ。",
        "desc_pt": "Abordagem científica do condicionamento em BJJ. Aprenda desenvolvimento de sistemas de energia, princípios de periodização e protocolos de adaptação para desempenho ideal.",
        "content_en": "Energy systems in BJJ include phosphocreatine, anaerobic glycolytic, and aerobic systems. Understanding which dominates different match phases enables targeted training.",
        "content_ja": "BJJのエネルギーシステムには、ホスファゲン、無酸素解糖、有酸素システムが含まれます。異なるマッチフェーズでどのシステムが支配的かを理解することで、ターゲット化されたトレーニングが可能になります。",
        "content_pt": "Os sistemas de energia em BJJ incluem fosfocreatina, glicolítico anaeróbico e sistemas aeróbicos. Entender qual domina diferentes fases da luta permite treinamento direcionado.",
    },
    384: {
        "slug": "bjj-guard-setups-masterclass",
        "title_en": "Guard Setups Masterclass — Entry & Base Control",
        "title_ja": "ガードセットアップマスタークラス — エントリーとベースコントロール",
        "title_pt": "Aula Mestre de Configurações de Guarda — Entrada e Controle de Base",
        "desc_en": "Advanced guard setup techniques for various positions. Learn efficient entries from standing, ground, and transitional positions with proper base and frame control.",
        "desc_ja": "様々なポジションでの高度なガードセットアップ技。立位、グラウンド、遷移ポジションからの効率的なエントリーを学び、適切なベースとフレームコントロールを習得します。",
        "desc_pt": "Técnicas avançadas de configuração de guarda para várias posições. Aprenda entradas eficientes de posições em pé, no chão e de transição com controle adequado de base e frame.",
        "content_en": "Effective guard setup begins with proper foot placement, hip positioning, and connection. Master fundamental concepts before progressing to advanced variations.",
        "content_ja": "効果的なガードセットアップは、足の配置、腰のポジショニング、コネクションから始まります。高度なバリエーションに進む前に基本的なコンセプトをマスターします。",
        "content_pt": "Uma configuração eficiente de guarda começa com posicionamento adequado dos pés, posicionamento de quadril e conexão. Domine conceitos fundamentais antes de progredir para variações avançadas.",
    },
    385: {
        "slug": "bjj-back-control-finishing-details",
        "title_en": "Back Control — Finishing Details for High-Percentage Submissions",
        "title_ja": "バックコントロール — 高確率のサブミッション用フィニッシング詳細",
        "title_pt": "Controle de Costas — Detalhes de Finalização para Finalizações de Alta Porcentagem",
        "desc_en": "Master finishing sequences from back control position. Learn hooks placement, body positioning, and submission setup for maximum efficiency and safety.",
        "desc_ja": "バックコントロール位置からのフィニッシングシーケンスをマスターします。フック配置、ボディポジショニング、最大効率と安全性のためのサブミッションセットアップを学ぶ。",
        "desc_pt": "Domine sequências de finalização da posição de controle de costas. Aprenda posicionamento de ganchos, posicionamento de corpo e configuração de finalização para máxima eficiência e segurança.",
        "content_en": "Rear naked choke finish requires proper hook control, posture management, and chin control. This guide details each component for reliable execution.",
        "content_ja": "背後からの絞め首フィニッシュは、適切なフックコントロール、姿勢管理、あご制御が必要です。本ガイドでは、信頼できる実行のための各コンポーネントを詳しく説明しています。",
        "content_pt": "O término do mata-leão de trás requer controle adequado de ganchos, gerenciamento de postura e controle do queixo. Este guia detalha cada componente para execução confiável.",
    },
    386: {
        "slug": "bjj-sweeps-to-submissions-chain-mechanics",
        "title_en": "Sweeps to Submissions — Chain Mechanics & Timing",
        "title_ja": "スウィープからサブミッションへ — チェーンメカニクスとタイミング",
        "title_pt": "Varreduras para Finalizações — Mecânica de Cadeia e Timing",
        "desc_en": "Advanced chain attack mechanics from sweep to submission. Learn seamless transitions, opponent reactions, and how to capitalize on positioning shifts.",
        "desc_ja": "スウィープからサブミッションへの高度なチェーン攻撃メカニクス。シームレスな遷移、相手の反応、ポジショニング変化を活用する方法を学ぶ。",
        "desc_pt": "Mecânica avançada de ataque em cadeia de varredura para finalização. Aprenda transições contínuas, reações do oponente e como capitalizar mudanças de posicionamento.",
        "content_en": "Chain attacks exploit momentum and positioning shifts. Understanding opponent weight distribution and balance enables effective progression from sweep to submission.",
        "content_ja": "チェーン攻撃は運動量とポジショニング変化を利用します。相手の体重分布とバランスを理解することで、スウィープからサブミッションへの効果的な進行が可能になります。",
        "content_pt": "Ataques em cadeia exploram mudanças de momentum e posicionamento. Entender distribuição de peso e equilíbrio do oponente permite progressão eficaz de varredura para finalização.",
    },
}

def build_html(slug, data, lang):
    """Build complete HTML page for a BJJ Wiki article."""
    key = f"title_{lang}"
    desc_key = f"desc_{lang}"
    content_key = f"content_{lang}"

    title = data[key]
    desc = data[desc_key]
    content = data[content_key]

    hreflang_links = {
        "en": f'<link rel="alternate" hreflang="en" href="https://wiki.bjj-app.net/en/{slug}.html">',
        "ja": f'<link rel="alternate" hreflang="ja" href="https://wiki.bjj-app.net/ja/{slug}.html">',
        "pt": f'<link rel="alternate" hreflang="pt" href="https://wiki.bjj-app.net/pt/{slug}.html">',
    }

    lang_attr = {"en": "en", "ja": "ja", "pt": "pt"}

    html = f"""<!DOCTYPE html>
<html lang="{lang_attr[lang]}">
<head>
<meta charset="UTF-8">
  <link rel="icon" href="https://wiki.bjj-app.net/favicon.svg" type="image/svg+xml">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — BJJ Wiki</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://wiki.bjj-app.net/{lang}/{slug}.html">
<link rel="canonical" href="https://wiki.bjj-app.net/{lang}/{slug}.html">
{hreflang_links['en']}
{hreflang_links['ja']}
{hreflang_links['pt']}
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }}
  h1 {{ color: #d32f2f; margin-bottom: 10px; }}
  .meta {{ color: #999; margin-bottom: 30px; }}
  .content {{ margin: 30px 0; }}
  a {{ color: #1976d2; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
</style>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-XXX');
</script>
</head>
<body>
<h1>{title}</h1>
<div class="meta">
  <p>BJJ Wiki — {datetime.now().strftime('%Y-%m-%d')}</p>
</div>

<article>
<div class="content">
<p>{content}</p>

<h2>Key Concepts</h2>
<ul>
<li>Advanced technique mastery</li>
<li>Positional dominance</li>
<li>Submission efficiency</li>
<li>Training methodology</li>
</ul>

<h2>Related Resources</h2>
<p>Explore related articles to deepen your understanding of BJJ techniques and training principles.</p>
</div>
</article>

<footer>
<hr>
<p><small>BJJ Wiki — Community-driven Brazilian Jiu-Jitsu Encyclopedia | <a href="/en/index.html">Back to Index</a></small></p>
</footer>
</body>
</html>
"""
    return html

def main():
    """Generate Batch 382-386 pages."""
    base_dir = Path('/sessions/keen-sharp-davinci/mnt/bjj-wiki')
    languages = ['en', 'ja', 'pt']

    total_created = 0

    for batch_num, batch_data in BATCHES.items():
        slug = batch_data['slug']
        print(f'Batch {batch_num}: {slug}')

        for lang in languages:
            lang_dir = base_dir / lang
            output_file = lang_dir / f'{slug}.html'

            if output_file.exists():
                print(f'  ⊘ {lang}: Already exists')
                continue

            html = build_html(slug, batch_data, lang)
            output_file.write_text(html, encoding='utf-8')
            total_created += 1
            print(f'  ✓ {lang}: Created')

    print(f'\n📊 Summary:')
    print(f'  Total pages created: {total_created} / 15')
    print(f'  Batch 382-386 complete')

if __name__ == '__main__':
    main()
