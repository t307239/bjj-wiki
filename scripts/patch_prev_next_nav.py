#!/usr/bin/env python3
"""
Add prev/next technique navigation to all technique pages.
Keeps users on site longer → better engagement signals for Google.
"""
import os, re

SKIP = {
    'index.html','skill-tree.html','sparring-simulator.html','news.html',
    'about.html','privacy.html','404.html','athletes.html','feed.xml',
    'techniques-az.html',
    'bjj-belt-system.html','bjj-terminology.html','bjj-rules-for-beginners.html',
    'bjj-vs-wrestling.html','bjj-training-tips.html','best-bjj-gi-guide.html',
    # comparison pages
    'armbar-vs-kimura.html','triangle-vs-guillotine.html',
    'double-leg-vs-single-leg.html','mount-vs-back-control.html',
    'closed-guard-vs-half-guard.html',
}

def get_technique_slugs(lang):
    slugs = []
    for fname in sorted(os.listdir(lang)):
        if not fname.endswith('.html'): continue
        if fname in SKIP: continue
        if fname.startswith('athlete-') or fname.startswith('gear-'): continue
        if fname.startswith('best-') or fname.startswith('bjj-') or fname.startswith('top-'): continue
        slugs.append(fname.replace('.html',''))
    slugs.sort()
    return slugs

def make_nav_html(prev_slug, prev_title, next_slug, next_title, lang):
    if lang == 'ja':
        prev_label = '← 前の技'
        next_label = '次の技 →'
        all_label = '📚 全技術一覧'
    elif lang == 'pt':
        prev_label = '← Anterior'
        next_label = 'Próxima →'
        all_label = '📚 Índice A-Z'
    else:
        prev_label = '← Previous'
        next_label = 'Next →'
        all_label = '📚 A-Z Index'

    prev_html = f'<a href="{prev_slug}.html" style="flex:1;text-align:left;padding:12px 16px;background:#0d1520;border:1px solid #1a2a3a;border-radius:10px;text-decoration:none;color:#64b5f6;font-size:.85rem;min-width:0"><div style="color:#546e7a;font-size:.75rem;margin-bottom:4px">{prev_label}</div><div style="font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{prev_title[:30]}</div></a>' if prev_slug else '<div style="flex:1"></div>'

    next_html = f'<a href="{next_slug}.html" style="flex:1;text-align:right;padding:12px 16px;background:#0d1520;border:1px solid #1a2a3a;border-radius:10px;text-decoration:none;color:#64b5f6;font-size:.85rem;min-width:0"><div style="color:#546e7a;font-size:.75rem;margin-bottom:4px">{next_label}</div><div style="font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{next_title[:30]}</div></a>' if next_slug else '<div style="flex:1"></div>'

    return f'''
<nav style="display:flex;gap:10px;align-items:stretch;margin:32px 0" aria-label="Technique navigation">
  {prev_html}
  <a href="techniques-az.html" style="padding:12px 16px;background:#0d1520;border:1px solid #1a2a3a;border-radius:10px;text-decoration:none;color:#90a4ae;font-size:.8rem;white-space:nowrap;display:flex;align-items:center">{all_label}</a>
  {next_html}
</nav>
'''

fixed = 0
for lang in ['en', 'ja', 'pt']:
    slugs = get_technique_slugs(lang)

    # Get titles for each slug
    titles = {}
    for slug in slugs:
        path = f'{lang}/{slug}.html'
        if not os.path.exists(path):
            continue
        with open(path) as f:
            content = f.read()
        m = re.search(r'<h1[^>]*>([^<]+)', content)
        if m:
            title = m.group(1).strip().split('—')[0].split('|')[0].strip()
        else:
            title = slug.replace('-',' ').title()
        titles[slug] = title

    for i, slug in enumerate(slugs):
        path = f'{lang}/{slug}.html'
        if not os.path.exists(path):
            continue
        with open(path) as f:
            content = f.read()

        if 'Technique navigation' in content:
            continue

        prev_slug = slugs[i-1] if i > 0 else None
        next_slug = slugs[i+1] if i < len(slugs)-1 else None
        prev_title = titles.get(prev_slug, '') if prev_slug else ''
        next_title = titles.get(next_slug, '') if next_slug else ''

        nav_html = make_nav_html(prev_slug, prev_title, next_slug, next_title, lang)

        # Insert before </main>
        if '</main>' in content:
            content = content.replace('</main>', nav_html + '\n</main>', 1)
        elif '</body>' in content:
            content = content.replace('</body>', nav_html + '\n</body>', 1)

        with open(path, 'w') as f:
            f.write(content)
        fixed += 1

print(f"Added prev/next navigation to: {fixed} pages")
