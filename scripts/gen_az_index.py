#!/usr/bin/env python3
"""
Generate A-Z Technique Index pages for en/ja/pt.
Comprehensive alphabetical directory → great for SEO and internal linking.
"""
import os, re, json
from datetime import date

TODAY = date.today().isoformat()
ADSENSE_ID = 'ca-pub-5529701443220352'
GA4_ID = 'G-7LM8L3TRZM'
BASE_URL = 'https://wiki.bjj-app.net'

SKIP = {'index.html','skill-tree.html','sparring-simulator.html','news.html',
        'about.html','privacy.html','404.html','athletes.html','feed.xml',
        'bjj-belt-system.html','bjj-terminology.html','bjj-rules-for-beginners.html',
        'bjj-vs-wrestling.html','bjj-training-tips.html','best-bjj-gi-guide.html'}

def get_techniques():
    techs = []
    for fname in sorted(os.listdir('en')):
        if not fname.endswith('.html'): continue
        if fname in SKIP: continue
        if fname.startswith('athlete-') or fname.startswith('gear-'): continue
        if fname.startswith('best-') or fname.startswith('bjj-') or fname.startswith('top-'): continue
        with open(f'en/{fname}') as f:
            content = f.read()
        m = re.search(r'<h1[^>]*>([^<]+)', content)
        title = m.group(1).strip() if m else fname.replace('.html','').replace('-',' ').title()
        title = title.split('—')[0].split('|')[0].strip()
        cat_m = re.search(r'class="category-tag"[^>]*>([^<]+)', content)
        cat = re.sub(r'[^\w\s/-]', '', cat_m.group(1).strip()) if cat_m else 'Technique'
        diff_m = re.search(r'class="diff-label">([^<]+)', content)
        diff = diff_m.group(1).strip() if diff_m else ''
        techs.append({'title': title, 'slug': fname.replace('.html',''), 'cat': cat.strip(), 'diff': diff})
    techs.sort(key=lambda x: x['title'].lower().lstrip('#0123456789 '))
    return techs

LETTERS = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + ['#']

def group_by_letter(techs):
    groups = {l: [] for l in LETTERS}
    for t in techs:
        first = t['title'][0].upper()
        if first.isdigit():
            groups['#'].append(t)
        elif first in groups:
            groups[first].append(t)
        else:
            groups['#'].append(t)
    return groups

CAT_COLORS = {
    'Choke': '#ef4444', 'Guard': '#3b82f6', 'Passing': '#f59e0b', 'Sweep': '#8b5cf6',
    'Takedown': '#10b981', 'Joint Lock': '#ec4899', 'Position': '#06b6d4',
    'Escape': '#84cc16', 'Defense': '#f97316', 'Transition': '#6366f1',
    'Technique': '#64748b',
}

def make_az_page(lang, techs):
    groups = group_by_letter(techs)

    if lang == 'ja':
        title_tag = 'BJJ技術辞典 A-Z | 全テクニック一覧'
        desc = 'ブラジリアン柔術の全テクニックをA-Z順で網羅。100以上の技をカテゴリ・難易度別に検索できる完全インデックス。'
        h1 = 'BJJ技術辞典 — 全テクニックA-Zインデックス'
        intro = '100以上のBJJテクニックをアルファベット順に掲載。カテゴリ・難易度でフィルタリング可能。'
        filter_all = 'すべて'
    elif lang == 'pt':
        title_tag = 'Índice A-Z de Técnicas de BJJ | Todas as Técnicas'
        desc = 'Índice completo de técnicas de BJJ em ordem alfabética — mais de 100 técnicas organizadas por categoria e nível de dificuldade.'
        h1 = 'Índice A-Z de Técnicas de BJJ'
        intro = 'Mais de 100 técnicas de BJJ listadas em ordem alfabética. Filtre por categoria ou dificuldade.'
        filter_all = 'Todos'
    else:
        title_tag = 'BJJ Techniques A-Z | Complete Index of 100+ Techniques'
        desc = 'Complete A-Z index of all BJJ techniques — 100+ moves organized alphabetically with categories and difficulty levels.'
        h1 = 'BJJ Techniques A-Z: Complete Index'
        intro = 'Browse all 100+ BJJ techniques in alphabetical order. Filter by category or difficulty level.'
        filter_all = 'All'

    # Build letter nav
    letter_nav = ''
    for letter in LETTERS:
        if groups[letter]:
            letter_nav += f'<a href="#letter-{letter}" style="color:#64b5f6;text-decoration:none;padding:4px 8px;border:1px solid #1a2a3a;border-radius:6px;font-size:.9rem;font-weight:700">{letter}</a>\n'
        else:
            letter_nav += f'<span style="color:#37474f;padding:4px 8px;font-size:.9rem">{letter}</span>\n'

    # Build technique cards per letter
    cards_html = ''
    total_count = 0
    for letter in LETTERS:
        if not groups[letter]:
            continue
        cards_html += f'<div id="letter-{letter}" style="margin:28px 0">\n'
        cards_html += f'<h2 style="font-size:1.4rem;color:#90caf9;margin-bottom:12px;border-bottom:2px solid #1a2a3a;padding-bottom:8px">{letter}</h2>\n'
        cards_html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px">\n'
        for t in groups[letter]:
            color = CAT_COLORS.get(t['cat'], '#64748b')
            diff_badge = f'<span style="font-size:.7rem;color:#78909c">{t["diff"]}</span>' if t['diff'] else ''
            cards_html += f'''<a href="{t['slug']}.html" style="display:block;background:#0d1520;border:1px solid #1a2a3a;border-radius:10px;padding:12px 14px;text-decoration:none;color:#e0e0e0;transition:border-color .2s" onmouseover="this.style.borderColor='{color}'" onmouseout="this.style.borderColor='#1a2a3a'">
  <div style="font-weight:700;font-size:.9rem;margin-bottom:4px">{t['title']}</div>
  <div style="display:flex;gap:8px;align-items:center">
    <span style="font-size:.72rem;color:{color};background:{color}20;padding:2px 8px;border-radius:10px">{t['cat']}</span>
    {diff_badge}
  </div>
</a>\n'''
            total_count += 1
        cards_html += '</div>\n</div>\n'

    # Schema
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": title_tag,
        "numberOfItems": total_count,
        "itemListElement": [
            {"@type": "ListItem", "position": i+1, "name": t['title'], "url": f"{BASE_URL}/{lang}/{t['slug']}.html"}
            for i, t in enumerate(techs)
        ]
    }, ensure_ascii=False)

    breadcrumb = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "BJJ Wiki", "item": f"{BASE_URL}/{lang}/index.html"},
            {"@type": "ListItem", "position": 2, "name": "A-Z Index", "item": f"{BASE_URL}/{lang}/techniques-az.html"}
        ]
    }, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <link rel="icon" href="https://wiki.bjj-app.net/favicon.svg" type="image/svg+xml">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title_tag}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{BASE_URL}/{lang}/techniques-az.html">
  <meta property="og:title" content="{title_tag}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="website">
    <meta property="og:site_name" content="BJJ Wiki">
  <meta property="og:url" content="{BASE_URL}/{lang}/techniques-az.html">
  <meta property="og:image" content="{BASE_URL}/og-image.svg">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="alternate" hreflang="en" href="{BASE_URL}/en/techniques-az.html">
  <link rel="alternate" hreflang="ja" href="{BASE_URL}/ja/techniques-az.html">
  <link rel="alternate" hreflang="pt" href="{BASE_URL}/pt/techniques-az.html">
  <link rel="alternate" hreflang="x-default" href="{BASE_URL}/en/techniques-az.html">
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>
  <script type="application/ld+json">{schema}</script>
  <script type="application/ld+json">{breadcrumb}</script>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:#0a0a0a;color:#e0e0e0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.6}}
    header{{background:linear-gradient(135deg,#0d1f3c,#0a0a0a);padding:16px 20px;border-bottom:1px solid #1a2a3a}}
    nav a{{color:#64b5f6;text-decoration:none;margin-right:16px;font-size:.9rem}}
    main{{max-width:1100px;margin:0 auto;padding:24px 20px 80px}}
    h1{{font-size:1.8rem;color:#e3f2fd;margin:0 0 8px}}
    h2{{font-size:1.1rem}}
    .letter-nav{{display:flex;flex-wrap:wrap;gap:6px;margin:20px 0 28px;padding:16px;background:#0d1520;border-radius:12px;border:1px solid #1a2a3a}}
    .search-box{{width:100%;padding:10px 16px;background:#0d1520;border:1px solid #1a2a3a;border-radius:10px;color:#e0e0e0;font-size:.95rem;margin-bottom:16px}}
    .search-box:focus{{outline:none;border-color:#3b82f6}}
    footer{{background:#0d1f3c;padding:20px;text-align:center;font-size:.8rem;color:#546e7a;margin-top:40px}}
    footer a{{color:#64b5f6;text-decoration:none;margin:0 8px}}
  </style>
</head>
<body>
<header>
  <nav>
    <a href="index.html">🥋 BJJ Wiki</a>
    <a href="techniques-az.html" style="color:#fff">📚 A-Z Index</a>
    <a href="skill-tree.html">🌳 Skill Tree</a>
    <a href="sparring-simulator.html">🎮 Simulator</a>
  </nav>
</header>
<main>
  <h1>{h1}</h1>
  <p style="color:#90a4ae;margin-bottom:20px">{intro} <strong style="color:#64b5f6">{total_count} techniques</strong> total.</p>

  <input type="text" class="search-box" placeholder="🔍 Search techniques..." oninput="filterTechs(this.value)">

  <div class="letter-nav">
    {letter_nav}
  </div>

  <div id="tech-grid">
  {cards_html}
  </div>

  <div style="margin-top:40px;padding:20px;background:#0d1520;border:1px solid #1a2a3a;border-radius:12px">
    <h2 style="color:#90caf9;margin-bottom:12px">📬 {"ニュースレター" if lang=="ja" else "Newsletter" if lang=="en" else "Newsletter"}</h2>
    <p style="color:#90a4ae;font-size:.9rem;margin-bottom:12px">{"週1回、新技解説をメールでお届け。無料。" if lang=="ja" else "New technique breakdowns delivered weekly. Free." if lang=="en" else "Novidades semanais sobre técnicas de BJJ. Grátis."}</p>
    <a href="https://bjjwiki.beehiiv.com/subscribe" target="_blank" style="background:#2e7d32;color:#fff;padding:10px 24px;border-radius:8px;text-decoration:none;font-weight:700">
      {"無料購読する" if lang=="ja" else "Subscribe Free" if lang=="en" else "Assinar Grátis"} →
    </a>
  </div>
</main>
<script>
function filterTechs(q) {{
  q = q.toLowerCase();
  document.querySelectorAll('#tech-grid a').forEach(function(card) {{
    var text = card.textContent.toLowerCase();
    card.style.display = (!q || text.includes(q)) ? '' : 'none';
  }});
  document.querySelectorAll('#tech-grid [id^="letter-"]').forEach(function(section) {{
    var visible = Array.from(section.querySelectorAll('a')).some(function(c) {{ return c.style.display !== 'none'; }});
    section.style.display = visible ? '' : 'none';
  }});
}}
</script>
<footer>
  <a href="../en/techniques-az.html">EN</a> | <a href="../ja/techniques-az.html">JA</a> | <a href="../pt/techniques-az.html">PT</a><br><br>
  <a href="privacy.html">Privacy</a> | <a href="about.html">About</a>
  <p style="margin-top:10px">© 2026 BJJ Wiki. All rights reserved.</p>
</footer>
</body>
</html>'''

techs = get_techniques()
for lang in ['en', 'ja', 'pt']:
    html = make_az_page(lang, techs)
    with open(f'{lang}/techniques-az.html', 'w') as f:
        f.write(html)
    print(f"Generated {lang}/techniques-az.html ({len(techs)} techniques)")
