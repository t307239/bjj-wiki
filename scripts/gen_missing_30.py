#!/usr/bin/env python3
# ⚠️ DEPRECATED — DO NOT RUN ⚠️
# このスクリプトはアフィリリンク(bjj06-22/bjjfanatics)を含む旧バッチスクリプトです。
# CLAUDE.md「アフィリリンク完全禁止」ルールにより使用禁止。
# 実行するとアフィリリンクが再注入され先祖返りします。
# 代わりに generate_bjj_wiki.py を使用してください。
"""
Generate 39 missing technique pages × 3 languages using template engine.
No API calls — fully offline. Produces consistent, content-rich pages.
"""
import os, json, re
from datetime import date

TODAY = date.today().isoformat()
ADSENSE_ID = 'ca-pub-5529701443220352'
GA4_ID = 'G-7LM8L3TRZM'
BASE_URL = 'https://wiki.bjj-app.net'

TECHNIQUES = [
    ('reverse-de-la-riva', 'Reverse De La Riva', 'Guard'),
    ('z-guard', 'Z-Guard', 'Guard'),
    ('stack-pass', 'Stack Pass', 'Passing'),
    ('double-under-pass', 'Double Under Pass', 'Passing'),
    ('pressure-pass', 'Pressure Pass', 'Passing'),
    ('smash-pass', 'Smash Pass', 'Passing'),
    ('x-pass', 'X-Pass', 'Passing'),
    ('morote-seoi-nage', 'Morote Seoi Nage', 'Takedown'),
    ('arm-triangle-choke', 'Arm Triangle Choke', 'Choke'),
    ('north-south-choke', 'North-South Choke', 'Choke'),
    ('baseball-choke', 'Baseball Choke', 'Choke'),
    ('cross-collar-choke', 'Cross Collar Choke', 'Choke'),
    ('clock-choke', 'Clock Choke', 'Choke'),
    ('lapel-choke', 'Lapel Choke', 'Choke'),
    ('straight-armbar', 'Straight Armbar', 'Joint Lock'),
    ('monoplata', 'Monoplata', 'Joint Lock'),
    ('s-mount', 'S-Mount', 'Position'),
    ('modified-mount', 'Modified Mount', 'Position'),
    ('body-triangle', 'Body Triangle', 'Position'),
    ('tripod-sweep', 'Tripod Sweep', 'Sweep'),
    ('elevator-sweep', 'Elevator Sweep', 'Sweep'),
    ('sickle-sweep', 'Sickle Sweep', 'Sweep'),
    ('overhead-sweep', 'Overhead Sweep', 'Sweep'),
    ('balloon-sweep', 'Balloon Sweep', 'Sweep'),
    ('x-guard-sweep', 'X-Guard Sweep', 'Sweep'),
    ('granby-roll', 'Granby Roll', 'Transition'),
    ('elbow-knee-escape', 'Elbow-Knee Escape', 'Escape'),
    ('guard-retention', 'Guard Retention', 'Defense'),
    ('hip-escape', 'Hip Escape', 'Defense'),
    ('frame', 'Frame', 'Defense'),
    ('back-defense', 'Back Defense', 'Defense'),
    ('technical-standup', 'Technical Stand-Up', 'Transition'),
    ('stand-in-base', 'Stand In Base', 'Transition'),
    ('sitting-guard', 'Sitting Guard', 'Guard'),
    ('seat-belt-control', 'Seat Belt Control', 'Position'),
    ('front-headlock', 'Front Headlock', 'Position'),
    ('russian-tie', 'Russian Tie', 'Takedown'),
    ('underhook', 'Underhook', 'Position'),
    ('overhook', 'Overhook', 'Position'),
]

# Descriptions per category
CAT_INTROS = {
    'Guard': 'A guard variation that gives you control from the bottom position while setting up sweeps and submissions.',
    'Passing': 'A guard passing technique designed to get past your opponent\'s legs and establish a dominant top position.',
    'Takedown': 'A takedown used to bring the fight to the ground from a standing position.',
    'Choke': 'A choking technique that cuts off blood flow or air supply to force a submission.',
    'Joint Lock': 'A joint lock that hyperextends or rotates a joint past its natural range of motion to force a tap.',
    'Position': 'A control position that provides dominant leverage for attacks and control.',
    'Sweep': 'A sweep technique that reverses the top/bottom relationship from guard.',
    'Transition': 'A transition movement that changes position or creates openings.',
    'Escape': 'An escape technique to recover from a disadvantageous position.',
    'Defense': 'A defensive skill that protects against attacks and maintains positional integrity.',
}

STEP_TEMPLATES = {
    'Guard': [
        ('Establish the Guard', 'Control your opponent\'s posture and establish the guard position using your legs and grips.'),
        ('Disrupt Their Base', 'Use hip movement and grips to break their posture and create off-balance.'),
        ('Attack with Sweeps or Submissions', 'With their base disrupted, initiate your sweep or submission attack.'),
        ('Complete the Action', 'Finish the sweep to top position or complete the submission to force a tap.'),
    ],
    'Passing': [
        ('Control the Hips', 'Engage with grips and pressure to limit your opponent\'s hip mobility.'),
        ('Clear the Legs', 'Use the pass mechanics to get past their guard legs.'),
        ('Drive Through', 'Follow through with bodyweight and pressure to land in a dominant position.'),
        ('Settle and Hold', 'Stabilize in side control, mount, or north-south for 3 seconds to score.'),
    ],
    'Takedown': [
        ('Establish Grips', 'Control the collar, sleeve, or underhook to set up the throw.'),
        ('Break Posture', 'Pull or push to break their stance and create movement.'),
        ('Execute the Technique', 'Use hip drive, leg sweep, or shoulder throw to take them down.'),
        ('Land and Control', 'Land in a dominant ground position and establish control immediately.'),
    ],
    'Choke': [
        ('Establish Position', 'Get into a dominant position — back control, mount, or guard.'),
        ('Set the Grip', 'Place hands/arms in the correct position as described for this choke.'),
        ('Apply the Pressure', 'Use coordinated body mechanics to compress the carotid arteries or airway.'),
        ('Hold Until Tap', 'Maintain pressure and release immediately when your partner taps.'),
    ],
    'Joint Lock': [
        ('Isolate the Target Limb', 'Separate the arm or leg from your opponent\'s body.'),
        ('Align the Joint', 'Position the joint correctly in relation to your hip or arm for the lock.'),
        ('Apply Controlled Pressure', 'Use smooth, controlled pressure — not explosive force.'),
        ('Release on Tap', 'Release the moment your partner taps — joint locks can cause injury quickly.'),
    ],
    'Position': [
        ('Achieve the Entry', 'Enter the position through a sweep, pass, or submission defense.'),
        ('Establish Control', 'Set your grips and weight distribution to maximize control.'),
        ('Defend Against Escapes', 'Block their escape attempts by adjusting weight and hips.'),
        ('Attack From Position', 'Use the positional advantages to set up submissions or transitions.'),
    ],
    'Sweep': [
        ('Set Up From Guard', 'Start in guard and establish the specific grips for this sweep.'),
        ('Create the Imbalance', 'Use leg pressure and hand grips to break their base.'),
        ('Execute the Sweep', 'Apply the momentum or leverage to flip them to their back.'),
        ('Land in Top Position', 'Follow the sweep to land in side control or mount.'),
    ],
    'Transition': [
        ('Read the Opening', 'Identify the right moment to transition — usually when they overpressure or shift weight.'),
        ('Create the Space', 'Generate the space needed using frames or hip movement.'),
        ('Execute the Movement', 'Move quickly and decisively through the transition.'),
        ('Reestablish Control', 'Settle into the new position and re-establish grips.'),
    ],
    'Escape': [
        ('Frame Against Pressure', 'Use strong frames to prevent your opponent from applying more pressure.'),
        ('Create Space', 'Shrimp or bridge to create enough space to move your hips.'),
        ('Insert the Escape', 'Execute the specific escape — hip escape, roll, or guard recovery.'),
        ('Reestablish Guard or Stand', 'Return to guard or return to standing.'),
    ],
    'Defense': [
        ('Recognize the Threat', 'Identify what attack your opponent is setting up.'),
        ('Apply the Defense', 'Use the specific defensive movement or grip to counter.'),
        ('Create Counter Space', 'Use the defense to create space for your own attack or recovery.'),
        ('Maintain Composure', 'Stay calm and technical — panic leads to mistakes.'),
    ],
}

RELATED_BY_CAT = {
    'Guard': ['closed-guard','half-guard','de-la-riva-guard','x-guard','butterfly-guard'],
    'Passing': ['toreando-pass','knee-slice','leg-drag','double-leg-takedown'],
    'Takedown': ['double-leg-takedown','single-leg-takedown','hip-throw','osoto-gari'],
    'Choke': ['rear-naked-choke','triangle-choke','guillotine','darce-choke','arm-triangle'],
    'Joint Lock': ['armbar','kimura','americana','heel-hook','knee-bar'],
    'Position': ['mount','back-control','side-control','north-south'],
    'Sweep': ['scissor-sweep','hip-bump-sweep','flower-sweep','tripod-sweep'],
    'Transition': ['back-take','guard-recovery','shrimp-escape'],
    'Escape': ['bridge-and-roll','shrimp-escape','elbow-knee-escape'],
    'Defense': ['frame','guard-retention','hip-escape'],
}

def make_page(slug, name, category, lang):
    if lang == 'ja':
        title = f'{name}の技術解説 | BJJ Wiki'
        desc = f'{name}の正しい動き方・エントリー・よくあるミスを解説。ブラジリアン柔術の{category}技術。'
        h1 = f'{name} — BJJ技術解説'
    elif lang == 'pt':
        title = f'{name} | Guia Completo de Técnica de BJJ'
        desc = f'Aprenda {name} — mecânica, entradas, erros comuns e como usar em competição. Guia completo de BJJ.'
        h1 = f'{name} — Guia Completo'
    else:
        title = f'{name} | BJJ Technique Guide'
        desc = f'Complete guide to {name} in Brazilian Jiu-Jitsu — mechanics, entries, common mistakes, and how to use it in competition.'
        h1 = f'{name} — Complete BJJ Guide'

    intro = CAT_INTROS.get(category, 'A fundamental Brazilian Jiu-Jitsu technique used at all levels of competition.')
    steps = STEP_TEMPLATES.get(category, STEP_TEMPLATES['Guard'])
    related = RELATED_BY_CAT.get(category, ['closed-guard','armbar','triangle-choke'])

    # Build HowTo JSON-LD
    howto = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": f"How to perform {name}",
        "description": f"Step-by-step guide to {name} in Brazilian Jiu-Jitsu.",
        "step": [
            {"@type": "HowToStep", "position": i+1, "name": n, "text": t}
            for i, (n, t) in enumerate(steps)
        ]
    }

    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "datePublished": TODAY,
        "dateModified": TODAY,
        "author": {"@type": "Organization", "name": "BJJ Wiki"},
        "publisher": {"@type": "Organization", "name": "BJJ Wiki"}
    }

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "BJJ Wiki", "item": f"{BASE_URL}/{lang}/index.html"},
            {"@type": "ListItem", "position": 2, "name": name, "item": f"{BASE_URL}/{lang}/{slug}.html"}
        ]
    }

    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f"What is {name} in BJJ?",
                "acceptedAnswer": {"@type": "Answer", "text": f"{name} is a {category.lower()} technique in Brazilian Jiu-Jitsu. {intro}"}
            },
            {
                "@type": "Question",
                "name": f"When should I use {name}?",
                "acceptedAnswer": {"@type": "Answer", "text": f"{name} is most effective when your opponent gives you the right opening. Focus on correct mechanics and timing rather than strength."}
            }
        ]
    }

    related_links = ''.join(f'<a href="{r}.html">{r.replace("-"," ").title()}</a>' for r in related)

    hreflang = f'''    <link rel="alternate" hreflang="en" href="{BASE_URL}/en/{slug}.html">
    <link rel="alternate" hreflang="ja" href="{BASE_URL}/ja/{slug}.html">
    <link rel="alternate" hreflang="pt" href="{BASE_URL}/pt/{slug}.html">
    <link rel="alternate" hreflang="x-default" href="{BASE_URL}/en/{slug}.html">'''

    steps_html = ''
    for i, (step_name, step_text) in enumerate(steps, 1):
        steps_html += f'''<div style="background:#0d1520;border:1px solid #1a3a5c;border-radius:10px;padding:14px 18px;margin:8px 0">
  <div style="display:flex;align-items:center;gap:10px">
    <span style="background:#1565c0;color:#fff;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.8rem;font-weight:700;flex-shrink:0">{i}</span>
    <strong style="color:#90caf9">{step_name}</strong>
  </div>
  <p style="margin:8px 0 0 36px;color:#b0bec5;font-size:.9rem">{step_text}</p>
</div>\n'''

    fanatics_url = f'https://bjjfanatics.com/search?q={slug.replace("-","+")}+bjj&ref=BJJWIKI'

    if lang == 'ja':
        fanatics_text = f'{name}を極めるなら世界最高の教則DVDへ。'
        fanatics_btn = '🎬 DVDを見る (20% OFF: BJJWIKI)'
        beehiiv_head = '📬 BJJ Wikiニュースレター'
        beehiiv_sub = '週1回、新技解説・コンペ情報・トレーニングTipsをお届け。'
        beehiiv_btn = '無料購読する'
        steps_head = 'ステップバイステップ'
        related_head = '関連技'
    elif lang == 'pt':
        fanatics_text = f'Domine o {name} com os melhores instrutores no BJJ Fanatics.'
        fanatics_btn = '🎬 Ver Instrutionais (20% OFF: BJJWIKI)'
        beehiiv_head = '📬 BJJ Wiki Newsletter'
        beehiiv_sub = 'Dicas de treino, novas técnicas e análises de competição — toda semana, grátis.'
        beehiiv_btn = 'Assinar Grátis'
        steps_head = 'Passo a Passo'
        related_head = 'Técnicas Relacionadas'
    else:
        fanatics_text = f'Master {name} with world-class instructionals on BJJ Fanatics.'
        fanatics_btn = '🎬 Browse Instructionals (20% OFF: BJJWIKI)'
        beehiiv_head = '📬 BJJ Wiki Newsletter'
        beehiiv_sub = 'Training tips, new technique breakdowns, and competition insights — weekly, free.'
        beehiiv_btn = 'Subscribe Free'
        steps_head = 'Step-by-Step Guide'
        related_head = 'Related Techniques'

    skill_tree_href = f'../skill-tree.html' if False else 'skill-tree.html'

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
  <meta property="og:url" content="{BASE_URL}/{lang}/{slug}.html">
  <meta property="og:image" content="{BASE_URL}/og-image.svg">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
{hreflang}
  <link rel="preconnect" href="https://www.googletagmanager.com">
  <link rel="preconnect" href="https://pagead2.googlesyndication.com">
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>
  <script type="application/ld+json">
{json.dumps(howto, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(article, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(breadcrumb, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(faq, ensure_ascii=False, indent=2)}
  </script>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:#0a0a0a;color:#e0e0e0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.7}}
    header{{background:linear-gradient(135deg,#0d1f3c,#0a0a0a);padding:16px 20px;border-bottom:1px solid #1a2a3a}}
    nav a{{color:#64b5f6;text-decoration:none;margin-right:16px;font-size:.9rem}}
    main{{max-width:860px;margin:0 auto;padding:24px 20px 80px}}
    h1{{font-size:1.8rem;color:#e3f2fd;margin:0 0 8px;line-height:1.3}}
    h2{{font-size:1.15rem;color:#90caf9;margin:28px 0 12px;border-bottom:1px solid #1a2a3a;padding-bottom:6px}}
    p{{margin:0 0 14px;color:#cfd8dc}}
    .category-tag{{display:inline-block;background:#1565c0;color:#fff;font-size:.75rem;font-weight:700;padding:3px 10px;border-radius:20px;margin-bottom:14px;letter-spacing:.05em;text-transform:uppercase}}
    .related-links a{{display:inline-block;margin:4px 6px 4px 0;padding:4px 12px;background:#0d1f3c;border:1px solid #1565c0;border-radius:20px;color:#64b5f6;text-decoration:none;font-size:.85rem}}
    .breadcrumb{{font-size:.8rem;color:#546e7a;margin-bottom:20px}}
    .breadcrumb a{{color:#546e7a;text-decoration:none}}
    .share-bar{{display:flex;gap:8px;margin:24px 0;flex-wrap:wrap}}
    .share-bar a{{padding:8px 14px;border-radius:8px;text-decoration:none;font-size:.85rem;font-weight:600}}
    footer{{background:#0d1f3c;padding:20px;text-align:center;font-size:.8rem;color:#546e7a;margin-top:40px}}
    footer a{{color:#64b5f6;text-decoration:none;margin:0 8px}}
  </style>
</head>
<body>
<header>
  <nav>
    <a href="index.html">🥋 BJJ Wiki</a>
    <a href="skill-tree.html">🌳 Skill Tree</a>
    <a href="sparring-simulator.html">🎮 Simulator</a>
    <a href="news.html">📰 News</a>
  </nav>
</header>
<main>
  <div class="breadcrumb"><a href="index.html">BJJ Wiki</a> › <a href="index.html">{category}</a> › {name}</div>
  <div class="category-tag">🥋 {category}</div>
  <h1>{h1}</h1>
  <p style="color:#b0bec5;font-size:1rem;margin-bottom:20px">{intro}</p>

  <div class="share-bar">
    <a href="https://twitter.com/intent/tweet?text=Learn+{name.replace(' ','+')}+in+BJJ+🥋&url={BASE_URL}/{lang}/{slug}.html" target="_blank" style="background:#000;color:#fff">𝕏 Share</a>
    <a href="https://www.reddit.com/submit?url={BASE_URL}/{lang}/{slug}.html&title={name}+BJJ+Guide" target="_blank" style="background:#ff4500;color:#fff">Reddit</a>
    <a href="skill-tree.html" style="background:#1a3a1a;color:#a5d6a7;border:1px solid #2e7d32">📍 Track Progress → 🌳 Skill Tree</a>
  </div>

  <article>
    <h2>⚙️ {steps_head}</h2>
    {steps_html}

    <div class="aff-box" style="background:linear-gradient(135deg,#0a1428,#0d1f3c);border:1px solid #1565c0;border-radius:12px;padding:20px 24px;margin:32px 0;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;">
      <div>
        <div style="font-size:.8rem;color:#64b5f6;letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px">🎬 Instructional</div>
        <p style="margin:0;color:#e3f2fd;font-size:.95rem">{fanatics_text}</p>
      </div>
      <a href="{fanatics_url}" target="_blank" rel="noopener sponsored"
         style="background:#1565c0;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:700;white-space:nowrap;font-size:.9rem"
         onclick="gtag('event','fanatics_click',{{technique:'{slug}',lang:'{lang}'}})">
        {fanatics_btn}
      </a>
    </div>

    <div class="beehiiv-box" style="background:linear-gradient(135deg,#0a1a0a,#0d2010);border:1px solid #2e7d32;border-radius:12px;padding:20px 24px;margin:32px 0;text-align:center;">
      <div style="font-size:1.05rem;font-weight:700;color:#a5d6a7;margin-bottom:8px">{beehiiv_head}</div>
      <p style="margin:0 0 16px;color:#c8e6c9;font-size:.9rem">{beehiiv_sub}</p>
      <a href="https://bjjwiki.beehiiv.com/subscribe" target="_blank" rel="noopener"
         style="background:#2e7d32;color:#fff;padding:10px 24px;border-radius:8px;text-decoration:none;font-weight:700;font-size:.9rem"
         onclick="gtag('event','beehiiv_click',{{lang:'{lang}'}})">
        {beehiiv_btn}
      </a>
    </div>
  </article>

  <h2>{related_head}</h2>
  <div class="related-links">
    {related_links}
  </div>
</main>
<footer>
  <a href="../en/{slug}.html">EN</a> | <a href="../ja/{slug}.html">JA</a> | <a href="../pt/{slug}.html">PT</a><br><br>
  <a href="privacy.html">Privacy Policy</a> | <a href="about.html">About</a>
  <p style="margin-top:10px">© 2026 BJJ Wiki. All rights reserved.</p>
</footer>
</body>
</html>'''

# Generate pages
total = 0
for slug, name, category in TECHNIQUES:
    for lang in ['en', 'ja', 'pt']:
        path = f'{lang}/{slug}.html'
        if os.path.exists(path):
            continue  # Don't overwrite existing
        html = make_page(slug, name, category, lang)
        with open(path, 'w') as f:
            f.write(html)
        total += 1

print(f"Generated {total} new technique pages")
