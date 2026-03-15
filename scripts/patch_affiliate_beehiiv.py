#!/usr/bin/env python3
"""
Patch Fanatics affiliate links + Beehiiv CTA to pages missing them.
"""
import os, re

# --- Fanatics affiliate block (inserted before </article> or before </main> or before </body>) ---
def make_fanatics_block(slug, name, lang):
    if lang == 'ja':
        cta = f'{name}を深めるなら教則DVDが最速。BJJ Fanaticsで今すぐチェック。'
        btn = '🎬 DVDを見る (20% OFF: BJJWIKI)'
    elif lang == 'pt':
        cta = f'Aprenda {name} com os melhores instrutores do mundo no BJJ Fanatics.'
        btn = '🎬 Ver Instrutionais (20% OFF: BJJWIKI)'
    else:
        cta = f'Level up your {name} with world-class instructionals on BJJ Fanatics.'
        btn = '🎬 Browse Instructionals (20% OFF: BJJWIKI)'

    search_query = slug.replace('-', '+')
    url = f'https://bjjfanatics.com/search?q={search_query}&ref=BJJWIKI'

    return f'''
<div class="aff-box" style="background:linear-gradient(135deg,#0a1428,#0d1f3c);border:1px solid #1565c0;border-radius:12px;padding:20px 24px;margin:32px 0;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;">
  <div>
    <div style="font-size:.8rem;color:#64b5f6;letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px">🎬 Instructional</div>
    <p style="margin:0;color:#e3f2fd;font-size:.95rem">{cta}</p>
  </div>
  <a href="{url}" target="_blank" rel="noopener sponsored"
     style="background:#1565c0;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:700;white-space:nowrap;font-size:.9rem"
     onclick="gtag('event','fanatics_click',{{technique:'{slug}',lang:'{lang}'}})">
    {btn}
  </a>
</div>
'''

# --- Beehiiv CTA block ---
def make_beehiiv_block(lang):
    if lang == 'ja':
        headline = '📬 BJJ Wikiニュースレター'
        sub = '週1回、新技解説・コンペ情報・トレーニングTipsをお届け。'
        btn = '無料購読する'
    elif lang == 'pt':
        headline = '📬 BJJ Wiki Newsletter'
        sub = 'Dicas de treino, novas técnicas e análises de competição — toda semana, grátis.'
        btn = 'Assinar Grátis'
    else:
        headline = '📬 BJJ Wiki Newsletter'
        sub = 'Training tips, new technique breakdowns, and competition insights — weekly, free.'
        btn = 'Subscribe Free'

    return f'''
<div class="beehiiv-box" style="background:linear-gradient(135deg,#0a1a0a,#0d2010);border:1px solid #2e7d32;border-radius:12px;padding:20px 24px;margin:32px 0;text-align:center;">
  <div style="font-size:1.05rem;font-weight:700;color:#a5d6a7;margin-bottom:8px">{headline}</div>
  <p style="margin:0 0 16px;color:#c8e6c9;font-size:.9rem">{sub}</p>
  <a href="https://bjjwiki.beehiiv.com/subscribe" target="_blank" rel="noopener"
     style="background:#2e7d32;color:#fff;padding:10px 24px;border-radius:8px;text-decoration:none;font-weight:700;font-size:.9rem"
     onclick="gtag('event','beehiiv_click',{{lang:'{lang}'}})">
    {btn}
  </a>
</div>
'''

fixed_fanatics = 0
fixed_beehiiv = 0

for lang in ['en', 'ja', 'pt']:
    for fname in sorted(os.listdir(lang)):
        if not fname.endswith('.html'):
            continue
        path = f'{lang}/{fname}'
        with open(path) as f:
            content = f.read()

        changed = False
        slug = fname.replace('.html', '')

        # Extract name from title
        title_match = re.search(r'<title>([^<|]+)', content)
        name = title_match.group(1).strip() if title_match else slug.replace('-', ' ').title()

        # Add Fanatics block if missing
        if 'fanatics' not in content.lower() and 'fanatic' not in content.lower():
            block = make_fanatics_block(slug, name, lang)
            # Try to insert before </article>, then </main>, then </body>
            if '</article>' in content:
                content = content.replace('</article>', f'{block}\n</article>', 1)
            elif '</main>' in content:
                content = content.replace('</main>', f'{block}\n</main>', 1)
            else:
                content = content.replace('</body>', f'{block}\n</body>', 1)
            fixed_fanatics += 1
            changed = True

        # Add Beehiiv CTA if missing
        if 'beehiiv' not in content.lower():
            block = make_beehiiv_block(lang)
            if '</article>' in content:
                content = content.replace('</article>', f'{block}\n</article>', 1)
            elif '</main>' in content:
                content = content.replace('</main>', f'{block}\n</main>', 1)
            else:
                content = content.replace('</body>', f'{block}\n</body>', 1)
            fixed_beehiiv += 1
            changed = True

        if changed:
            with open(path, 'w') as f:
                f.write(content)

print(f"Added Fanatics block to: {fixed_fanatics} pages")
print(f"Added Beehiiv CTA to:   {fixed_beehiiv} pages")
