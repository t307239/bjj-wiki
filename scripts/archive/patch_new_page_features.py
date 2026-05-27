#!/usr/bin/env python3
# ⚠️ DEPRECATED — DO NOT RUN ⚠️
# このスクリプトはアフィリリンク(bjj06-22/bjjfanatics)を含む旧バッチスクリプトです。
# CLAUDE.md「アフィリリンク完全禁止」ルールにより使用禁止。
# 実行するとアフィリリンクが再注入され先祖返りします。
# 代わりに generate_bjj_wiki.py を使用してください。
"""
Add missing features to the 117 newly generated technique pages:
- Difficulty bar (belt level + stars + label)
- Athlete chips section
- Yoga crosslinks
- Gear crosslinks
- Pro Tip box
"""
import os, re

NEW_SLUGS = [
    'reverse-de-la-riva','z-guard','stack-pass','double-under-pass','pressure-pass',
    'smash-pass','x-pass','morote-seoi-nage','arm-triangle-choke','north-south-choke',
    'baseball-choke','cross-collar-choke','clock-choke','lapel-choke','straight-armbar',
    'monoplata','s-mount','modified-mount','body-triangle','tripod-sweep',
    'elevator-sweep','sickle-sweep','overhead-sweep','balloon-sweep','x-guard-sweep',
    'granby-roll','elbow-knee-escape','guard-retention','hip-escape','frame',
    'back-defense','technical-standup','stand-in-base','sitting-guard',
    'seat-belt-control','front-headlock','russian-tie','underhook','overhook',
    # Also cover any from earlier batches
    'ankle-lock','lasso-guard','50-50-guard','shrimp-escape','arm-drag',
    'bridge-and-roll','harai-goshi','ippon-seoi-nage','snap-down','estima-lock',
    'deep-half-guard','mount-escape',
]

# Difficulty config: (belt_color, belt_hex, stars, label)
DIFFICULTY = {
    'reverse-de-la-riva':   ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'z-guard':              ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'stack-pass':           ('#3b82f6', '🔵 Blue Belt', '★★☆☆☆', 'Intermediate'),
    'double-under-pass':    ('#8b5cf6', '🟣 Purple Belt', '★★★☆☆', 'Intermediate'),
    'pressure-pass':        ('#8b5cf6', '🟣 Purple Belt', '★★★★☆', 'Advanced'),
    'smash-pass':           ('#8b5cf6', '🟣 Purple Belt', '★★★★☆', 'Advanced'),
    'x-pass':               ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'morote-seoi-nage':     ('#8b5cf6', '🟣 Purple Belt', '★★★★☆', 'Advanced'),
    'arm-triangle-choke':   ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'north-south-choke':    ('#8b5cf6', '🟣 Purple Belt', '★★★★☆', 'Advanced'),
    'baseball-choke':       ('#92400e', '🟤 Brown Belt', '★★★★☆', 'Advanced'),
    'cross-collar-choke':   ('#6b7280', '⬜ White Belt', '★☆☆☆☆', 'Beginner'),
    'clock-choke':          ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'lapel-choke':          ('#8b5cf6', '🟣 Purple Belt', '★★★★☆', 'Advanced'),
    'straight-armbar':      ('#6b7280', '⬜ White Belt', '★☆☆☆☆', 'Beginner'),
    'monoplata':            ('#92400e', '🟤 Brown Belt', '★★★★☆', 'Advanced'),
    's-mount':              ('#8b5cf6', '🟣 Purple Belt', '★★★☆☆', 'Intermediate'),
    'modified-mount':       ('#3b82f6', '🔵 Blue Belt', '★★☆☆☆', 'Intermediate'),
    'body-triangle':        ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'tripod-sweep':         ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'elevator-sweep':       ('#3b82f6', '🔵 Blue Belt', '★★☆☆☆', 'Intermediate'),
    'sickle-sweep':         ('#8b5cf6', '🟣 Purple Belt', '★★★☆☆', 'Intermediate'),
    'overhead-sweep':       ('#8b5cf6', '🟣 Purple Belt', '★★★★☆', 'Advanced'),
    'balloon-sweep':        ('#92400e', '🟤 Brown Belt', '★★★★★', 'Expert'),
    'x-guard-sweep':        ('#8b5cf6', '🟣 Purple Belt', '★★★★☆', 'Advanced'),
    'granby-roll':          ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'elbow-knee-escape':    ('#6b7280', '⬜ White Belt', '★★☆☆☆', 'Beginner'),
    'guard-retention':      ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'hip-escape':           ('#6b7280', '⬜ White Belt', '★☆☆☆☆', 'Beginner'),
    'frame':                ('#6b7280', '⬜ White Belt', '★☆☆☆☆', 'Beginner'),
    'back-defense':         ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'technical-standup':    ('#6b7280', '⬜ White Belt', '★★☆☆☆', 'Beginner'),
    'stand-in-base':        ('#6b7280', '⬜ White Belt', '★☆☆☆☆', 'Beginner'),
    'sitting-guard':        ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'seat-belt-control':    ('#3b82f6', '🔵 Blue Belt', '★★☆☆☆', 'Intermediate'),
    'front-headlock':       ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'russian-tie':          ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'underhook':            ('#6b7280', '⬜ White Belt', '★★☆☆☆', 'Beginner'),
    'overhook':             ('#6b7280', '⬜ White Belt', '★★☆☆☆', 'Beginner'),
    'ankle-lock':           ('#6b7280', '⬜ White Belt', '★★☆☆☆', 'Beginner'),
    'lasso-guard':          ('#8b5cf6', '🟣 Purple Belt', '★★★★☆', 'Advanced'),
    '50-50-guard':          ('#8b5cf6', '🟣 Purple Belt', '★★★★☆', 'Advanced'),
    'shrimp-escape':        ('#6b7280', '⬜ White Belt', '★☆☆☆☆', 'Beginner'),
    'arm-drag':             ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'bridge-and-roll':      ('#6b7280', '⬜ White Belt', '★★☆☆☆', 'Beginner'),
    'harai-goshi':          ('#8b5cf6', '🟣 Purple Belt', '★★★★☆', 'Advanced'),
    'ippon-seoi-nage':      ('#8b5cf6', '🟣 Purple Belt', '★★★★☆', 'Advanced'),
    'snap-down':            ('#3b82f6', '🔵 Blue Belt', '★★★☆☆', 'Intermediate'),
    'estima-lock':          ('#92400e', '🟤 Brown Belt', '★★★★★', 'Expert'),
    'deep-half-guard':      ('#8b5cf6', '🟣 Purple Belt', '★★★★☆', 'Advanced'),
    'mount-escape':         ('#6b7280', '⬜ White Belt', '★★☆☆☆', 'Beginner'),
}

# Athlete assignments by category keywords
ATHLETES_BY_CAT = {
    'choke': [('Gordon Ryan', 'gordon-ryan', 'gordon+ryan'), ('Craig Jones', 'craig-jones', 'craig+jones')],
    'guard': [('Keenan Cornelius', 'keenan-cornelius', 'keenan+cornelius'), ('Bernardo Faria', 'bernardo-faria', 'bernardo+faria')],
    'pass': [('Buchecha', 'buchecha', 'buchecha'), ('Leandro Lo', 'leandro-lo', 'leandro+lo')],
    'takedown': [('Marcelo Garcia', 'marcelo-garcia', 'marcelo+garcia'), ('Leandro Lo', 'leandro-lo', 'leandro+lo')],
    'lock': [('Gordon Ryan', 'gordon-ryan', 'gordon+ryan'), ('Mikey Musumeci', 'mikey-musumeci', 'mikey+musumeci')],
    'sweep': [('Caio Terra', 'caio-terra', 'caio+terra'), ('Berimbolo', 'berimbolo-brothers', 'berimbolo')],
    'escape': [('Marcelo Garcia', 'marcelo-garcia', 'marcelo+garcia'), ('Roger Gracie', 'roger-gracie', 'roger+gracie')],
    'position': [('Andre Galvao', 'andre-galvao', 'andre+galvao'), ('Gordon Ryan', 'gordon-ryan', 'gordon+ryan')],
    'transition': [('Marcelo Garcia', 'marcelo-garcia', 'marcelo+garcia'), ('Gordon Ryan', 'gordon-ryan', 'gordon+ryan')],
    'defense': [('Marcelo Garcia', 'marcelo-garcia', 'marcelo+garcia'), ('Roger Gracie', 'roger-gracie', 'roger+gracie')],
    'default': [('Gordon Ryan', 'gordon-ryan', 'gordon+ryan'), ('Marcelo Garcia', 'marcelo-garcia', 'marcelo+garcia')],
}

YOGA_BY_CAT = {
    'choke': [('Pigeon Pose', 'pigeon-pose'), ('Shoulder Opener', 'thread-the-needle')],
    'guard': [('Happy Baby', 'happy-baby'), ('Butterfly Stretch', 'butterfly-stretch')],
    'pass': [('Warrior I', 'warrior-i'), ('Hip Flexor Stretch', 'low-lunge')],
    'takedown': [('Warrior II', 'warrior-ii'), ('Hip Opener', 'lizard-pose')],
    'lock': [('Wrist Stretch', 'wrist-flexion'), ('Shoulder Opener', 'thread-the-needle')],
    'sweep': [('Happy Baby', 'happy-baby'), ('Supine Twist', 'supine-twist')],
    'escape': [('Bridge Pose', 'bridge-pose'), ('Knee-to-Chest', 'knee-to-chest')],
    'position': [('Child\'s Pose', 'childs-pose'), ('Cat-Cow', 'cat-cow')],
    'transition': [('Sun Salutation', 'sun-salutation'), ('Downward Dog', 'downward-dog')],
    'defense': [('Bridge Pose', 'bridge-pose'), ('Happy Baby', 'happy-baby')],
    'default': [('Pigeon Pose', 'pigeon-pose'), ('Happy Baby', 'happy-baby')],
}

GEAR_BY_CAT = {
    'choke': [('Best BJJ Gi', 'best-bjj-gi-guide'), ('Best Rashguard', 'gear-rashguard-review')],
    'guard': [('Best BJJ Gi', 'best-bjj-gi-guide'), ('Best Kneepads', 'gear-kneepads-review')],
    'pass': [('Best BJJ Gi', 'best-bjj-gi-guide'), ('Best Kneepads', 'gear-kneepads-review')],
    'takedown': [('Best Rashguard', 'gear-rashguard-review'), ('Best BJJ Gi', 'best-bjj-gi-guide')],
    'lock': [('Best Rashguard', 'gear-rashguard-review'), ('Best Kneepads', 'gear-kneepads-review')],
    'sweep': [('Best BJJ Gi', 'best-bjj-gi-guide'), ('Best Rashguard', 'gear-rashguard-review')],
    'default': [('Best BJJ Gi', 'best-bjj-gi-guide'), ('Best Rashguard', 'gear-rashguard-review')],
}

PRO_TIPS = {
    'choke': 'Master the mechanics before adding speed — a technically perfect choke works with minimal strength.',
    'guard': 'Guard retention is half the battle. Focus on keeping your hips between you and your opponent.',
    'pass': 'Don\'t rush the pass. Slow, heavy pressure is more effective than fast, rushed attempts.',
    'takedown': 'Level changes and head movement are the secrets of high-level takedowns — not brute strength.',
    'lock': 'Never apply joint locks explosively in training. Use graduated pressure and release instantly on the tap.',
    'sweep': 'Timing beats strength every time for sweeps. Wait for your opponent to commit their weight.',
    'escape': 'Create space before trying to escape — trying to escape while flat and heavy pressure is applied rarely works.',
    'position': 'Dominant positions are won by anticipating escapes before they happen, not reacting after.',
    'transition': 'Transitions are where championships are won and lost. Practice them slowly until they become automatic.',
    'defense': 'Good defense starts with good posture before your opponent has established their attack.',
    'default': 'Focus on body mechanics over strength — a technique done correctly requires minimal effort.',
}

def get_cat_key(slug):
    for kw in ['choke','strangle','triangle','guillotine','darce','anaconda','lapel','collar','clock','north-south','baseball','rear-naked']:
        if kw in slug: return 'choke'
    for kw in ['armbar','arm-bar','kimura','americana','omoplata','monoplata','straight-armbar','lock','estima']:
        if kw in slug: return 'lock'
    for kw in ['guard','lasso','50-50','z-guard','x-guard','butterfly','half-guard','sitting-guard']:
        if kw in slug: return 'guard'
    for kw in ['pass','stack','smash','pressure','double-under','toreando','x-pass']:
        if kw in slug: return 'pass'
    for kw in ['sweep','tripod','elevator','sickle','overhead','balloon','x-guard-sweep']:
        if kw in slug: return 'sweep'
    for kw in ['takedown','throw','double-leg','single-leg','seoi','goshi','harai','osoto','russian-tie','snap-down']:
        if kw in slug: return 'takedown'
    for kw in ['escape','bridge-and-roll','shrimp','granby','mount-escape','hip-escape','elbow-knee']:
        if kw in slug: return 'escape'
    for kw in ['frame','defense','retention','back-defense','guard-retention']:
        if kw in slug: return 'defense'
    for kw in ['mount','position','seat-belt','body-triangle','underhook','overhook','front-headlock','arm-drag']:
        if kw in slug: return 'position'
    for kw in ['technical-standup','stand-in-base','transition']:
        if kw in slug: return 'transition'
    return 'default'

DIFF_BAR_CSS = '''
<style>
.difficulty-bar{display:flex;align-items:center;gap:10px;margin:8px 0 20px;flex-wrap:wrap}
.belt-tag{padding:4px 12px;border-radius:20px;font-size:.78rem;font-weight:700;border:1px solid rgba(255,255,255,.15)}
.stars{font-size:1rem;letter-spacing:2px}
.diff-label{font-size:.8rem;color:#90a4ae;font-weight:600}
.athletes-section{margin:28px 0}
.athletes-section h2{font-size:.9rem;font-weight:700;color:#a78bfa;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px}
.athlete-chips{display:flex;flex-wrap:wrap;gap:10px}
.athlete-chip{display:flex;align-items:center;gap:10px;background:#141926;border:1px solid #1f2840;border-radius:12px;padding:12px 16px;text-decoration:none;color:#e8e8ff;min-width:180px;transition:border-color .2s}
.athlete-chip:hover{border-color:#7c6af7}
.ac-name{font-weight:700;font-size:.9rem}
.ac-dvd{font-size:.78rem;color:#6b7aa8;margin-top:2px}
.ac-fanatics{display:inline-block;margin-top:6px;font-size:.75rem;color:#7c6af7;text-decoration:none;font-weight:600}
.yoga-box{background:linear-gradient(135deg,#0a1a10,#0f1a0a);border:1px solid #22c55e;border-radius:12px;padding:20px;margin:24px 0}
.yoga-box h3{font-size:.85rem;font-weight:700;color:#22c55e;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}
.yoga-box p{font-size:.85rem;color:#6b9e6b;margin-bottom:12px}
.yoga-chips{display:flex;flex-wrap:wrap;gap:8px}
.yoga-chip{background:#0d2010;border:1px solid #16a34a;border-radius:20px;padding:5px 12px;font-size:.8rem;color:#86efac;text-decoration:none}
.gear-box{background:linear-gradient(135deg,#1a0a0a,#1a0f0a);border:1px solid #dc2626;border-radius:12px;padding:20px;margin:24px 0}
.gear-box h3{font-size:.85rem;font-weight:700;color:#f87171;text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px}
.gear-links{display:flex;flex-wrap:wrap;gap:8px}
.gear-link{background:#1a0d0d;border:1px solid #7f1d1d;border-radius:20px;padding:5px 12px;font-size:.8rem;color:#fca5a5;text-decoration:none}
.pro-tip{background:linear-gradient(135deg,#0a1a0a,#0f200a);border:1px solid #16a34a;border-radius:12px;padding:16px 20px;margin:24px 0;position:relative}
.pro-tip::before{content:"💡 Pro Tip";font-size:.75rem;font-weight:700;color:#22c55e;text-transform:uppercase;letter-spacing:.08em;display:block;margin-bottom:6px}
.pro-tip p{margin:0;font-size:.9rem;color:#a7c9a7}
</style>
'''

def make_difficulty_bar(slug):
    if slug not in DIFFICULTY:
        return ''
    hex_color, belt_label, stars, label = DIFFICULTY[slug]
    return f'''<div class="difficulty-bar">
  <span class="belt-tag" style="background:#0f1e38;color:{hex_color};border-color:{hex_color}40">{belt_label}</span>
  <span class="stars" style="color:#f59e0b">{stars}</span>
  <span class="diff-label">{label}</span>
</div>
'''

def make_athlete_chips(slug):
    cat = get_cat_key(slug)
    athletes = ATHLETES_BY_CAT.get(cat, ATHLETES_BY_CAT['default'])
    chips = ''
    for name, profile_slug, fanatics_q in athletes:
        chips += f'''<a class="athlete-chip" href="athlete-{profile_slug}.html">
  <div>
    <div class="ac-name">🥋 {name}</div>
    <div class="ac-dvd">View profile & instructionals</div>
    <a class='ac-fanatics' href='https://bjjfanatics.com/collections/all?q={fanatics_q}' target='_blank' rel='noopener noreferrer nofollow' onclick='event.stopPropagation()'>BJJ Fanatics →</a>
  </div>
</a>'''
    return f'''<div class="athletes-section">
  <h2>Elite Athletes Who Use This Technique</h2>
  <div class="athlete-chips">{chips}</div>
</div>
'''

def make_yoga_box(slug, lang):
    cat = get_cat_key(slug)
    poses = YOGA_BY_CAT.get(cat, YOGA_BY_CAT['default'])
    chips = ''.join(
        f'<a class="yoga-chip" href="https://t307239.github.io/yoga-wiki/{lang}/{p_slug}.html" target="_blank" rel="noopener noreferrer">🧘 {p_name}</a>'
        for p_name, p_slug in poses
    )
    if lang == 'ja':
        h3 = '🧘 柔術のための柔軟性トレーニング'
        p = 'この技に必要な柔軟性を高めるヨガポーズ:'
    elif lang == 'pt':
        h3 = '🧘 Yoga para BJJ: Melhore sua Flexibilidade'
        p = 'Poses de yoga para aumentar a mobilidade necessária para esta técnica:'
    else:
        h3 = '🧘 Yoga for BJJ: Improve Your Flexibility'
        p = 'Build the mobility needed for this technique:'
    return f'''<div class="yoga-box">
  <h3>{h3}</h3>
  <p>{p}</p>
  <div class="yoga-chips">{chips}</div>
</div>
'''

def make_gear_box(slug, lang):
    cat = get_cat_key(slug)
    gears = GEAR_BY_CAT.get(cat, GEAR_BY_CAT['default'])
    links = ''.join(
        f'<a class="gear-link" href="{gear_slug}.html">🛒 {gear_name}</a>'
        for gear_name, gear_slug in gears
    )
    if lang == 'ja':
        h3 = '⚙️ おすすめギア'
    elif lang == 'pt':
        h3 = '⚙️ Equipamento Recomendado'
    else:
        h3 = '⚙️ Recommended Gear for Training'
    return f'''<div class="gear-box">
  <h3>{h3}</h3>
  <div class="gear-links">{links}</div>
</div>
'''

def make_pro_tip(slug, lang):
    cat = get_cat_key(slug)
    tip = PRO_TIPS.get(cat, PRO_TIPS['default'])
    return f'<div class="pro-tip"><p>{tip}</p></div>\n'

fixed = 0
for slug in NEW_SLUGS:
    for lang in ['en', 'ja', 'pt']:
        path = f'{lang}/{slug}.html'
        if not os.path.exists(path):
            continue
        with open(path) as f:
            content = f.read()

        changed = False

        # Add CSS if not present
        if 'difficulty-bar' not in content:
            content = content.replace('</style>', DIFF_BAR_CSS + '</style>', 1)
            changed = True

        # Add difficulty bar after h1 if not present
        if 'difficulty-bar' not in content:
            diff_html = make_difficulty_bar(slug)
            if diff_html:
                content = re.sub(r'(</h1>)', r'\1\n' + diff_html, content, count=1)
                changed = True
        elif '<div class="difficulty-bar">' not in content:
            diff_html = make_difficulty_bar(slug)
            if diff_html:
                content = re.sub(r'(</h1>)', r'\1\n' + diff_html, content, count=1)
                changed = True

        # Add Pro Tip before fanatics block
        if 'pro-tip' not in content and 'aff-box' in content:
            tip_html = make_pro_tip(slug, lang)
            content = content.replace('<div class="aff-box"', tip_html + '\n<div class="aff-box"', 1)
            changed = True

        # Add athlete section before yoga/gear or before beehiiv
        if 'athletes-section' not in content and 'athlete-chip' not in content:
            athlete_html = make_athlete_chips(slug)
            if 'beehiiv-box' in content:
                content = content.replace('<div class="beehiiv-box"', athlete_html + '\n<div class="beehiiv-box"', 1)
            else:
                content = content.replace('</article>', athlete_html + '\n</article>', 1)
            changed = True

        # Add yoga box
        if 'yoga-box' not in content and 'yoga' not in content.lower():
            yoga_html = make_yoga_box(slug, lang)
            if 'gear-box' in content:
                content = content.replace('<div class="gear-box"', yoga_html + '\n<div class="gear-box"', 1)
            elif 'athletes-section' in content:
                content = content.replace('</div>\n</main>', yoga_html + '\n</main>', 1)
            changed = True

        # Add gear box
        if 'gear-box' not in content:
            gear_html = make_gear_box(slug, lang)
            if '</main>' in content:
                content = content.replace('</main>', gear_html + '\n</main>', 1)
            changed = True

        if changed:
            with open(path, 'w') as f:
                f.write(content)
            fixed += 1

print(f"Enhanced {fixed} pages with new features")
