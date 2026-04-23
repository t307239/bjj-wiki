#!/usr/bin/env python3
# ⚠️ DEPRECATED — DO NOT RUN ⚠️
# このスクリプトはアフィリリンク(bjj06-22/bjjfanatics)を含む旧バッチスクリプトです。
# CLAUDE.md「アフィリリンク完全禁止」ルールにより使用禁止。
# 実行するとアフィリリンクが再注入され先祖返りします。
# 代わりに generate_bjj_wiki.py を使用してください。
"""
Generate BJJ technique comparison pages — "X vs Y" format.
These target high-intent search queries like "armbar vs kimura bjj".
"""
import os, json
from datetime import date

TODAY = date.today().isoformat()
ADSENSE_ID = 'ca-pub-5529701443220352'
GA4_ID = 'G-7LM8L3TRZM'
BASE_URL = 'https://wiki.bjj-app.net'

COMPARISONS = [
    {
        'slug': 'armbar-vs-kimura',
        'a': {'name': 'Armbar', 'slug': 'armbar', 'emoji': '💪'},
        'b': {'name': 'Kimura', 'slug': 'kimura', 'emoji': '🔄'},
        'en': {
            'title': 'Armbar vs Kimura | Which BJJ Submission is Better?',
            'desc': 'Armbar vs Kimura — key differences, when to use each, setup chains, and which submission you should prioritize as a BJJ practitioner.',
            'h1': 'Armbar vs Kimura: Complete Comparison',
            'intro': 'The armbar and kimura are two of the most fundamental submissions in BJJ. Both attack the arm but work very differently. Here\'s everything you need to know about when and why to use each.',
            'rows': [
                ('Target', 'Elbow joint (hyperextension)', 'Shoulder joint (rotation)'),
                ('Position Setup', 'Mount, guard, back, side control', 'Guard, north-south, turtle, side control'),
                ('Grip Required', 'Hip clamp + arm isolation', 'Figure-4 grip (two-on-one)'),
                ('Difficulty', 'Intermediate (Blue Belt)', 'Intermediate (Blue Belt)'),
                ('Gi vs No-Gi', 'Excellent in both', 'More common in Gi, works No-Gi'),
                ('Escape Risk', 'Moderate — can pull arm out if early', 'Moderate — can roll/flip to escape'),
                ('Chain Attacks', '→ Omoplata, triangle, back take', '→ Guillotine, take-down, back control'),
                ('Best When', 'Opponent extends their arm', 'Opponent\'s arm is bent behind body'),
            ],
            'faq': [
                ('Which is easier to learn, armbar or kimura?', 'Most practitioners find the kimura grip easier to establish due to the intuitive two-on-one wrist control. The armbar requires more hip mobility and timing but has more attack angles.'),
                ('Can you chain armbar and kimura together?', 'Yes — this is a powerful combination. From guard or mount, an attempted armbar that your opponent defends can transition directly into a kimura as they bend their arm in defense.'),
            ],
            'verdict': 'Both are essential submissions to master. Learn the kimura first for its versatile setup positions, then add the armbar for its applications from mount and guard. Elite competitors use them as a linked system rather than choosing one.',
        },
        'ja': {
            'title': 'アームバー vs キムラ | どちらのサブミッションが効果的？',
            'desc': 'アームバーとキムラの違い、使い分け、セットアップの連鎖、どちらを優先すべきかを完全解説。',
            'h1': 'アームバー vs キムラ：完全比較',
            'intro': 'アームバーとキムラはBJJで最も基本的なサブミッションの2つ。どちらも腕を攻撃しますが、メカニズムは大きく異なります。',
        },
        'pt': {
            'title': 'Armbar vs Kimura | Qual Finalização é Melhor no BJJ?',
            'desc': 'Armbar vs Kimura — diferenças principais, quando usar cada um, encadeamentos e qual finalização priorizar no BJJ.',
            'h1': 'Armbar vs Kimura: Comparação Completa',
            'intro': 'O armbar e o kimura são duas das finalizações mais fundamentais do BJJ. Ambos atacam o braço mas funcionam de maneiras muito diferentes.',
        },
    },
    {
        'slug': 'triangle-vs-guillotine',
        'a': {'name': 'Triangle Choke', 'slug': 'triangle-choke', 'emoji': '🔺'},
        'b': {'name': 'Guillotine', 'slug': 'guillotine', 'emoji': '⚔️'},
        'en': {
            'title': 'Triangle vs Guillotine | BJJ Choke Comparison Guide',
            'desc': 'Triangle choke vs guillotine — setup positions, difficulty, best scenarios, and how they chain together in BJJ.',
            'h1': 'Triangle Choke vs Guillotine: Which to Use When',
            'intro': 'Two of the most popular chokes in BJJ — the triangle and guillotine each shine in different situations. Understanding when to use each can double your submission rate from the front.',
            'rows': [
                ('Type', 'Blood choke (carotid compression)', 'Primarily air choke (can be blood choke)'),
                ('Primary Position', 'Guard (closed, open)', 'Standing, front headlock, guard'),
                ('Works in Gi', 'Excellent', 'Excellent'),
                ('Works No-Gi', 'Excellent', 'Excellent (arm-in version is tighter)'),
                ('Difficulty', 'Intermediate — hip mobility needed', 'Beginner-friendly'),
                ('Setup Opportunity', 'Opponent postures up or arm crosses center', 'Opponent shoots or ducks their head'),
                ('Chain Attacks', '→ Armbar, omoplata, sweep', '→ Arm drag, back take, single leg'),
                ('Defense', 'Posture and stack', 'Frame and pull head out'),
            ],
            'faq': [
                ('Is the triangle choke or guillotine more effective?', 'Both are proven at the highest levels. The guillotine is generally easier to set up from standing positions, while the triangle has a higher finish rate from guard in competition.'),
                ('Can you combo triangle and guillotine?', 'Yes — a failed guillotine (when opponent tucks chin) often creates perfect hip angle for a triangle. This chain is used extensively by elite guard players.'),
            ],
            'verdict': 'Learn the guillotine first — it works from standing and can be set up quickly. Add the triangle from guard for a devastating combination. Together, any opponent who ducks their head or extends an arm is in danger.',
        },
        'ja': {
            'title': 'トライアングル vs ギロチン | BJJチョーク比較',
            'desc': 'トライアングルチョークとギロチンのセットアップ・難易度・最適場面を比較。どちらを使うべきかを解説。',
            'h1': 'トライアングル vs ギロチン：使い分けガイド',
            'intro': 'BJJで最も人気の2つのチョーク。トライアングルとギロチンはそれぞれ異なる状況で輝きます。',
        },
        'pt': {
            'title': 'Triangle vs Guilhotina | Comparação de Finalizações do BJJ',
            'desc': 'Triangle choke vs guilhotina — posições de setup, dificuldade, melhores cenários e como encadeá-los no BJJ.',
            'h1': 'Triangle vs Guilhotina: Quando Usar Cada Um',
            'intro': 'Dois dos estrangulamentos mais populares do BJJ — o triangle e a guilhotina brilham em situações diferentes.',
        },
    },
    {
        'slug': 'double-leg-vs-single-leg',
        'a': {'name': 'Double Leg Takedown', 'slug': 'double-leg-takedown', 'emoji': '🦵🦵'},
        'b': {'name': 'Single Leg Takedown', 'slug': 'single-leg-takedown', 'emoji': '🦵'},
        'en': {
            'title': 'Double Leg vs Single Leg Takedown | BJJ Takedown Guide',
            'desc': 'Double leg vs single leg takedown — when to shoot each, defensive considerations, and which to learn first for BJJ.',
            'h1': 'Double Leg vs Single Leg: Takedown Comparison',
            'intro': 'The double leg and single leg are the two most important wrestling takedowns in BJJ. Both start from a level change but end very differently. Here\'s how to choose and chain them.',
            'rows': [
                ('Target', 'Both legs simultaneously', 'One leg'),
                ('Entry Angle', 'Straight in, opponent square', 'Angle to outside'),
                ('Risk of Guillotine', 'Higher — head goes to center', 'Lower — head stays outside'),
                ('Finish Options', 'Drive through, lift, trip', 'Run the pipe, high crotch, trip'),
                ('Difficulty', 'Intermediate', 'Intermediate'),
                ('Best Setup', 'Collar tie + level change', 'Arm drag, snap down, level change'),
                ('Common Counters', 'Sprawl, guillotine, front headlock', 'Whizzer, sprawl, limp leg'),
                ('Use In Gi', 'Standard', 'Standard'),
            ],
            'faq': [
                ('Which takedown should a BJJ beginner learn first?', 'Most BJJ coaches recommend starting with the double leg for its directness, then adding the single leg as a countertakedown and when opponents post or sprawl on the double leg.'),
                ('How do you chain double and single leg?', 'A common chain: fake the double leg → opponent sprawls → shift to single leg on outside of their sprawled leg. This works at every level of competition.'),
            ],
            'verdict': 'Learn the double leg first for its directness, then the single leg as a chain and backup. The real power comes from threatening both simultaneously, forcing your opponent to defend against attacks on both legs.',
        },
        'ja': {
            'title': 'ダブルレッグ vs シングルレッグ | BJJテイクダウン比較',
            'desc': 'ダブルレッグとシングルレッグテイクダウンの違い・使い分け・どちらを先に習得すべきかを解説。',
            'h1': 'ダブルレッグ vs シングルレッグ：テイクダウン比較',
            'intro': 'ダブルレッグとシングルレッグはBJJで最も重要な2つのレスリングテイクダウン。',
        },
        'pt': {
            'title': 'Double Leg vs Single Leg | Comparação de Quedas no BJJ',
            'desc': 'Double leg vs single leg takedown — quando usar cada um, considerações defensivas e qual aprender primeiro para o BJJ.',
            'h1': 'Double Leg vs Single Leg: Comparação de Quedas',
            'intro': 'O double leg e o single leg são as duas quedas de wrestling mais importantes no BJJ.',
        },
    },
    {
        'slug': 'mount-vs-back-control',
        'a': {'name': 'Mount', 'slug': 'mount', 'emoji': '🏔️'},
        'b': {'name': 'Back Control', 'slug': 'back-control', 'emoji': '🎯'},
        'en': {
            'title': 'Mount vs Back Control | Which BJJ Position is More Dominant?',
            'desc': 'Mount vs back control in BJJ — points value, attack options, submission rate, and which position to chase in competition.',
            'h1': 'Mount vs Back Control: Which is More Dominant?',
            'intro': 'Mount and back control are the two highest-scoring positions in BJJ. Both score 4 points in IBJJF competition. But which is harder to escape, and which offers more submission options?',
            'rows': [
                ('IBJJF Points', '4 points', '4 points'),
                ('Escape Difficulty', 'Moderate — bridge/upa, elbow-knee', 'Hardest — opponent must remove hooks'),
                ('Submission Rate', 'High — armbar, chokes, americanas', 'Highest — rear naked choke is #1 sub'),
                ('Top Submission', 'Armbar, cross collar choke', 'Rear naked choke'),
                ('Gi Specific Subs', 'Cross collar, Ezekiel, bow-and-arrow', 'Bow-and-arrow choke'),
                ('Maintenance', 'Active weight management needed', 'Hip control + hooks = very stable'),
                ('Entry Difficulty', 'Moderate from guard pass', 'Harder — requires dedicated back take'),
                ('Common Escape', 'Bridge-and-roll, elbow-knee', 'Hands-to-hips, turn into opponent'),
            ],
            'faq': [
                ('Is back control better than mount in BJJ?', 'Back control generally has a higher submission rate (the rear naked choke is the most finished submission in MMA/BJJ), but mount is easier to achieve from a guard pass. Both score 4 IBJJF points.'),
                ('Which position should I focus on in competition?', 'Focus on the one that flows naturally from your passing style. Leg-drag passers often land in back control; pressure passers often land in mount. Train both but specialize in what your game produces.'),
            ],
            'verdict': 'Back control has a marginally higher submission rate, but mount is more accessible from common guard pass positions. The ideal competition game uses pressure passing to mount, then transitions to back when the opponent escapes to their side.',
        },
        'ja': {
            'title': 'マウント vs バックコントロール | どちらが上位ポジション？',
            'desc': 'マウントとバックコントロールの比較。ポイント・サブミッション率・逃げ方・どちらを狙うべきかを解説。',
            'h1': 'マウント vs バックコントロール：どちらが支配的？',
            'intro': 'マウントとバックコントロールはBJJで最も高スコアのポジション。両方とも4ポイント。どちらが脱出が難しく、どちらがより多くのサブミッションを生み出すか？',
        },
        'pt': {
            'title': 'Mount vs Back Control | Qual Posição é Mais Dominante no BJJ?',
            'desc': 'Mount vs back control no BJJ — pontos, opções de finalização, taxa de submissão e qual posição buscar na competição.',
            'h1': 'Mount vs Back Control: Qual é Mais Dominante?',
            'intro': 'Mount e back control são as duas posições com maior pontuação no BJJ. Ambas valem 4 pontos no IBJJF. Mas qual é mais difícil de escapar?',
        },
    },
    {
        'slug': 'closed-guard-vs-half-guard',
        'a': {'name': 'Closed Guard', 'slug': 'closed-guard', 'emoji': '🛡️'},
        'b': {'name': 'Half Guard', 'slug': 'half-guard', 'emoji': '🔒'},
        'en': {
            'title': 'Closed Guard vs Half Guard | BJJ Guard Comparison',
            'desc': 'Closed guard vs half guard — which guard should you master first? Differences in control, sweeps, submissions, and competition use.',
            'h1': 'Closed Guard vs Half Guard: Which to Master First?',
            'intro': 'Closed guard and half guard are both fundamental BJJ guard positions, but they work very differently. Closed guard offers powerful control, while half guard offers more transitions and modern passing resistance.',
            'rows': [
                ('Control Type', 'Full leg wrap — very tight control', 'One leg trapped — partial control'),
                ('Opponent Movement', 'Heavily restricted', 'Opponent can move more freely'),
                ('Submission Options', 'Armbar, triangle, guillotine, kimura', 'Kimura, D\'Arce, electric chair, leg lock'),
                ('Sweep Options', 'Hip bump, scissor, flower', 'Dog fight, deep half, roll under'),
                ('Guard Pass Risk', 'Lower — position is maintained well', 'Higher — opponent can pressure pass'),
                ('Transition Options', 'Limited — very controlled', 'High — deep half, lockdown, leg locks'),
                ('Best Against', 'Passive top players', 'Heavy pressure passers'),
                ('Recommended For', 'White/Blue belt beginners', 'Blue/Purple belt and above'),
            ],
            'faq': [
                ('Should I learn closed guard or half guard first?', 'Start with closed guard — it teaches fundamental guard mechanics, posture breaking, and submission setups with the most control. Half guard is an excellent second guard system once you understand the basics.'),
                ('Is closed guard or half guard better in no-gi?', 'Both work no-gi but closed guard is slightly harder to maintain without grips. Half guard, particularly the lockdown variation, can be very effective in no-gi despite grip limitations.'),
            ],
            'verdict': 'Start with closed guard to learn fundamental principles, then develop half guard as your second system. Many elite competitors use both — closed guard as their first response and half guard when the opponent breaks their closed guard posture.',
        },
        'ja': {
            'title': 'クローズドガード vs ハーフガード | どちらを先に習得すべき？',
            'desc': 'クローズドガードとハーフガードの違い、コントロール・スイープ・サブミッション・試合での使い方を比較。',
            'h1': 'クローズドガード vs ハーフガード：どちらを先に習得すべき？',
            'intro': 'クローズドガードとハーフガードはどちらもBJJの基本的なガードポジションですが、まったく異なる動き方をします。',
        },
        'pt': {
            'title': 'Closed Guard vs Meia Guarda | Comparação de Guardas do BJJ',
            'desc': 'Closed guard vs meia guarda — qual guarda dominar primeiro? Diferenças em controle, raspagens, finalizações e uso em competição.',
            'h1': 'Closed Guard vs Meia Guarda: Qual Dominar Primeiro?',
            'intro': 'Closed guard e meia guarda são posições fundamentais do BJJ, mas funcionam de maneiras muito diferentes.',
        },
    },
]

def make_comparison_page(comp, lang):
    data = comp[lang] if lang in comp else comp['en']
    a = comp['a']
    b = comp['b']
    slug = comp['slug']

    title = data['title']
    desc = data['desc']
    h1 = data['h1']
    intro = data['intro']
    rows = comp['en'].get('rows', [])
    faq_items = comp['en'].get('faq', [])
    verdict = comp['en'].get('verdict', '')

    if lang == 'ja':
        vs_head = '比較表'
        faq_head = 'よくある質問'
        verdict_head = '結論'
        table_headers = ['比較項目', a['name'], b['name']]
    elif lang == 'pt':
        vs_head = 'Comparação'
        faq_head = 'Perguntas Frequentes'
        verdict_head = 'Veredicto'
        table_headers = ['Aspecto', a['name'], b['name']]
    else:
        vs_head = 'Head-to-Head'
        faq_head = 'FAQ'
        verdict_head = 'Verdict'
        table_headers = ['Aspect', a['name'], b['name']]

    # Table rows HTML
    table_html = f'''<table style="width:100%;border-collapse:collapse;margin:16px 0">
  <thead>
    <tr>
      <th style="padding:10px 14px;background:#0d1f3c;text-align:left;color:#90caf9;font-size:.85rem;border-bottom:2px solid #1a2a3a">{table_headers[0]}</th>
      <th style="padding:10px 14px;background:#0d1f3c;text-align:left;color:#ef9a9a;font-size:.85rem;border-bottom:2px solid #1a2a3a">{a["emoji"]} {table_headers[1]}</th>
      <th style="padding:10px 14px;background:#0d1f3c;text-align:left;color:#a5d6a7;font-size:.85rem;border-bottom:2px solid #1a2a3a">{b["emoji"]} {table_headers[2]}</th>
    </tr>
  </thead>
  <tbody>'''
    for i, (aspect, a_val, b_val) in enumerate(rows):
        bg = '#0a1428' if i % 2 == 0 else '#0d1520'
        table_html += f'''
    <tr style="background:{bg}">
      <td style="padding:10px 14px;color:#78909c;font-size:.85rem;font-weight:600;border-bottom:1px solid #1a2a3a">{aspect}</td>
      <td style="padding:10px 14px;color:#cfd8dc;font-size:.85rem;border-bottom:1px solid #1a2a3a">{a_val}</td>
      <td style="padding:10px 14px;color:#cfd8dc;font-size:.85rem;border-bottom:1px solid #1a2a3a">{b_val}</td>
    </tr>'''
    table_html += '\n  </tbody>\n</table>'

    faq_html = ''
    faq_schema_items = []
    for q, ans in faq_items:
        faq_html += f'<details style="margin:8px 0;background:#0d1f0d;border:1px solid #2e7d32;border-radius:8px;padding:12px 16px"><summary style="font-weight:700;cursor:pointer;color:#a5d6a7">{q}</summary><p style="margin:10px 0 0;color:#b0bec5;font-size:.9rem">{ans}</p></details>\n'
        faq_schema_items.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}})

    faq_schema = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_schema_items}, ensure_ascii=False)
    article_schema = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "datePublished": TODAY, "dateModified": TODAY,
        "author": {"@type": "Organization", "name": "BJJ Wiki"},
        "publisher": {"@type": "Organization", "name": "BJJ Wiki"}
    }, ensure_ascii=False)
    breadcrumb = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "BJJ Wiki", "item": f"{BASE_URL}/{lang}/index.html"},
            {"@type": "ListItem", "position": 2, "name": h1, "item": f"{BASE_URL}/{lang}/{slug}.html"}
        ]
    }, ensure_ascii=False)

    verdict_html = f'''<div style="background:linear-gradient(135deg,#1a0a2e,#0d0a1a);border:2px solid #7c3aed;border-radius:14px;padding:20px 24px;margin:32px 0">
  <div style="font-size:.8rem;font-weight:700;color:#a78bfa;letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px">⚖️ {verdict_head}</div>
  <p style="color:#e2d9f3;font-size:.95rem;margin:0">{verdict}</p>
</div>''' if verdict else ''

    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{BASE_URL}/{lang}/{slug}.html">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="article">
  <meta property="og:image" content="{BASE_URL}/og-image.svg">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="alternate" hreflang="en" href="{BASE_URL}/en/{slug}.html">
  <link rel="alternate" hreflang="ja" href="{BASE_URL}/ja/{slug}.html">
  <link rel="alternate" hreflang="pt" href="{BASE_URL}/pt/{slug}.html">
  <link rel="alternate" hreflang="x-default" href="{BASE_URL}/en/{slug}.html">
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>
  <script type="application/ld+json">{faq_schema}</script>
  <script type="application/ld+json">{article_schema}</script>
  <script type="application/ld+json">{breadcrumb}</script>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:#0a0a0a;color:#e0e0e0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.7}}
    header{{background:linear-gradient(135deg,#0d1f3c,#0a0a0a);padding:16px 20px;border-bottom:1px solid #1a2a3a}}
    nav a{{color:#64b5f6;text-decoration:none;margin-right:16px;font-size:.9rem}}
    main{{max-width:900px;margin:0 auto;padding:24px 20px 80px}}
    h1{{font-size:1.8rem;color:#e3f2fd;margin:0 0 16px;line-height:1.3}}
    h2{{font-size:1.1rem;color:#90caf9;margin:28px 0 12px;border-bottom:1px solid #1a2a3a;padding-bottom:6px}}
    p{{margin:0 0 14px;color:#cfd8dc}}
    table{{overflow-x:auto;display:block}}
    .vs-banner{{display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center;margin:24px 0;padding:20px;background:#0d1520;border:1px solid #1a2a3a;border-radius:14px}}
    .vs-badge{{text-align:center;font-size:1.5rem;font-weight:900;color:#a78bfa}}
    .tech-card{{text-align:center;padding:16px;border-radius:10px;text-decoration:none;display:block}}
    .tech-card-a{{background:#1a0d0d;border:1px solid #7f1d1d}}
    .tech-card-b{{background:#0a1a0a;border:1px solid #14532d}}
    details summary{{list-style:none;cursor:pointer}}
    details summary::-webkit-details-marker{{display:none}}
    footer{{background:#0d1f3c;padding:20px;text-align:center;font-size:.8rem;color:#546e7a;margin-top:40px}}
    footer a{{color:#64b5f6;text-decoration:none;margin:0 8px}}
  </style>
</head>
<body>
<header>
  <nav>
    <a href="index.html">🥋 BJJ Wiki</a>
    <a href="techniques-az.html">📚 A-Z</a>
    <a href="skill-tree.html">🌳 Skill Tree</a>
  </nav>
</header>
<main>
  <h1>{h1}</h1>
  <p style="color:#90a4ae;margin-bottom:20px">{intro}</p>

  <div class="vs-banner">
    <a href="{a['slug']}.html" class="tech-card tech-card-a">
      <div style="font-size:2rem">{a['emoji']}</div>
      <div style="font-weight:700;color:#ef9a9a;margin-top:8px">{a['name']}</div>
    </a>
    <div class="vs-badge">VS</div>
    <a href="{b['slug']}.html" class="tech-card tech-card-b">
      <div style="font-size:2rem">{b['emoji']}</div>
      <div style="font-weight:700;color:#a5d6a7;margin-top:8px">{b['name']}</div>
    </a>
  </div>

  <h2>📊 {vs_head}</h2>
  {table_html}

  {verdict_html}

  <h2>❓ {faq_head}</h2>
  {faq_html}

  <div style="background:linear-gradient(135deg,#0a1428,#0d1f3c);border:1px solid #1565c0;border-radius:12px;padding:20px 24px;margin:32px 0;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;">
    <div>
      <div style="font-size:.8rem;color:#64b5f6;letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px">🎬 Go Deeper</div>
      <p style="margin:0;color:#e3f2fd;font-size:.95rem">Master both techniques with world-class instructionals on BJJ Fanatics.</p>
    </div>
    <a href="https://bjjfanatics.com/?ref=BJJWIKI" target="_blank" rel="noopener sponsored"
       style="background:#1565c0;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:700;white-space:nowrap;font-size:.9rem">
      🎬 Browse Instructionals (BJJWIKI 20% OFF)
    </a>
  </div>

  <div style="background:linear-gradient(135deg,#0a1a0a,#0d2010);border:1px solid #2e7d32;border-radius:12px;padding:20px 24px;margin:24px 0;text-align:center;">
    <div style="font-size:1.05rem;font-weight:700;color:#a5d6a7;margin-bottom:8px">📬 BJJ Wiki Newsletter</div>
    <p style="margin:0 0 16px;color:#c8e6c9;font-size:.9rem">Weekly technique breakdowns. Free.</p>
    <a href="https://bjjwiki.beehiiv.com/subscribe" target="_blank" rel="noopener"
       style="background:#2e7d32;color:#fff;padding:10px 24px;border-radius:8px;text-decoration:none;font-weight:700;font-size:.9rem">
      Subscribe Free →
    </a>
  </div>
</main>
<footer>
  <a href="../en/{slug}.html">EN</a> | <a href="../ja/{slug}.html">JA</a> | <a href="../pt/{slug}.html">PT</a><br><br>
  <a href="privacy.html">Privacy</a> | <a href="about.html">About</a>
  <p style="margin-top:10px">© 2026 BJJ Wiki. All rights reserved.</p>
</footer>
</body>
</html>'''

total = 0
for comp in COMPARISONS:
    for lang in ['en', 'ja', 'pt']:
        html = make_comparison_page(comp, lang)
        path = f'{lang}/{comp["slug"]}.html'
        with open(path, 'w') as f:
            f.write(html)
        total += 1

print(f"Generated {total} comparison pages ({len(COMPARISONS)} comparisons × 3 languages)")
