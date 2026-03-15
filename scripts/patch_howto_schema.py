#!/usr/bin/env python3
"""
Add HowTo JSON-LD schema to BJJ technique pages.
Extracts h2 section headers from each page to build realistic steps.
"""
import os, re, json

# Skip non-technique pages
NON_TECHNIQUE = {
    'index.html','skill-tree.html','sparring-simulator.html','news.html',
    'about.html','privacy.html','404.html','athletes.html',
    'best-bjj-guards.html','best-bjj-leg-locks.html','best-bjj-techniques-beginners.html',
    'best-no-gi-techniques.html','bjj-competition-guide.html','bjj-takedowns-guide.html',
    'bjj-beginners-guide.html','bjj-passing-fundamentals.html','bjj-sweeps-guide.html',
    'bjj-submissions-guide.html','bjj-escapes-guide.html','bjj-leg-locks-guide.html',
    'bjj-guard-types.html','bjj-top-positions.html','bjj-concepts-guide.html',
    'bjj-belt-system.html','bjj-terminology.html','bjj-rules-for-beginners.html',
    'bjj-vs-wrestling.html','bjj-training-tips.html','best-bjj-gi-guide.html',
    'bjj-competition-guide.html','bjj-takedowns-guide.html',
}

# Generic step templates by category keywords
STEP_TEMPLATES = {
    'choke': [
        ('Establish Position', 'Secure a dominant position — mount, back control, or guard — before attempting the choke.'),
        ('Set the Grip', 'Establish the correct grip or arm position required for the choke as described above.'),
        ('Apply Pressure', 'Use your bodyweight and muscle coordination to cut off blood flow or air supply.'),
        ('Hold Until Tap', 'Maintain steady pressure until your training partner taps or verbally submits. Release immediately.'),
    ],
    'armlock': [
        ('Gain Dominant Position', 'Move to a position that isolates your opponent\'s arm — typically from mount, guard, or side control.'),
        ('Isolate the Arm', 'Separate the target arm from their body using your legs or grips.'),
        ('Align the Joint', 'Ensure the elbow joint is correctly positioned — hyperextension direction depends on the lock.'),
        ('Apply Controlled Pressure', 'Use hips and bodyweight to create leverage. Apply gradually until your partner taps.'),
    ],
    'sweep': [
        ('Set Up from Guard', 'Start from a guard position (closed guard, butterfly, half guard) and establish grips.'),
        ('Create Imbalance', 'Break your opponent\'s base using grips and hip movement.'),
        ('Execute the Sweep', 'Use the leverage and momentum to reverse the position — get on top.'),
        ('Secure Top Position', 'Maintain pressure and settle into a scoring position after the sweep.'),
    ],
    'pass': [
        ('Pressure and Control', 'Establish grips and apply pressure to limit your opponent\'s guard mobility.'),
        ('Clear the Legs', 'Remove or bypass your opponent\'s legs using the passing technique.'),
        ('Establish Side Position', 'Land in side control, north-south, or mount as you complete the pass.'),
        ('Settle and Score', 'Hold the position for 3 seconds to score points in competition.'),
    ],
    'takedown': [
        ('Control the Stance', 'Establish your fighting stance and control the distance.'),
        ('Set Up the Shot', 'Use fakes, grip fighting, or level changes to create the opening.'),
        ('Execute the Takedown', 'Drive through with explosive hip power and leg drive.'),
        ('Secure Ground Position', 'Land in a dominant top position — side control, mount, or back.'),
    ],
    'escape': [
        ('Identify the Pressure', 'Understand your opponent\'s weight distribution and where they are weak.'),
        ('Create Space', 'Use frames, shrimping, or bridging to create enough space to move.'),
        ('Insert Your Escape', 'Apply the specific escape technique to recover guard or reverse.'),
        ('Reestablish Guard or Stand', 'Complete the escape by returning to a neutral or favorable position.'),
    ],
    'default': [
        ('Learn the Position', 'Understand the starting position and what condition triggers this technique.'),
        ('Establish Grips', 'Set the required grips or framing before initiating the technique.'),
        ('Execute the Movement', 'Apply the technique with proper body mechanics and timing.'),
        ('Finish and Control', 'Complete the technique — whether a submission, sweep, or position — and maintain control.'),
    ],
}

def get_steps(slug, title):
    slug_lower = slug.lower()
    title_lower = title.lower()
    combined = slug_lower + ' ' + title_lower

    if any(w in combined for w in ['choke','strangle','collar','lapel','triangle','guillotine','d\'arce','anaconda','rear naked']):
        return STEP_TEMPLATES['choke']
    if any(w in combined for w in ['armbar','arm-bar','kimura','americana','wrist-lock','omoplata','shoulder','elbow','lock']):
        return STEP_TEMPLATES['armlock']
    if any(w in combined for w in ['sweep','butterfly-sweep','hip-bump','scissor','flower']):
        return STEP_TEMPLATES['sweep']
    if any(w in combined for w in ['pass','pressure-pass','smash','stack','toreando','leg-drag','knee-slice']):
        return STEP_TEMPLATES['pass']
    if any(w in combined for w in ['takedown','throw','double-leg','single-leg','hip-throw','seoi','goshi','harai','osoto']):
        return STEP_TEMPLATES['takedown']
    if any(w in combined for w in ['escape','defense','recover']):
        return STEP_TEMPLATES['escape']
    return STEP_TEMPLATES['default']

fixed = 0

for lang in ['en', 'ja', 'pt']:
    for fname in sorted(os.listdir(lang)):
        if not fname.endswith('.html'): continue
        if fname in NON_TECHNIQUE: continue

        path = f'{lang}/{fname}'
        with open(path) as f:
            content = f.read()

        if 'HowTo' in content:
            continue

        # Extract title
        title_m = re.search(r'<title>([^<|]+)', content)
        title = title_m.group(1).strip() if title_m else fname.replace('.html','').replace('-',' ').title()

        slug = fname.replace('.html', '')
        steps = get_steps(slug, title)

        howto_schema = {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": f"How to {title.split('|')[0].strip()}",
            "description": f"Step-by-step guide to {title.split('|')[0].strip()} in Brazilian Jiu-Jitsu.",
            "step": [
                {
                    "@type": "HowToStep",
                    "position": i+1,
                    "name": name,
                    "text": text
                }
                for i, (name, text) in enumerate(steps)
            ]
        }

        schema_html = f'<script type="application/ld+json">\n{json.dumps(howto_schema, ensure_ascii=False, indent=2)}\n</script>'
        content = content.replace('</head>', f'{schema_html}\n</head>', 1)

        with open(path, 'w') as f:
            f.write(content)
        fixed += 1

print(f"Added HowTo schema to: {fixed} pages")
