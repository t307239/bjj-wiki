#!/usr/bin/env python3
"""
Strengthen internal links to low-inlink technique pages.
Appends links in existing Related Techniques <div class="related-links"> sections.
"""
import os, re

TARGETS = {
    'lasso-guard':      ('Lasso Guard',         'ラッソーガード',       'Guarda Lasso',         ['spider-guard','de-la-riva-guard','x-guard','worm-guard']),
    '50-50-guard':      ('50/50 Guard',          '50/50ガード',         'Guarda 50/50',          ['heel-hook','outside-heel-hook','knee-bar','calf-slicer','inside-heel-hook']),
    'arm-drag':         ('Arm Drag',             'アームドラッグ',      'Arm Drag',              ['double-leg-takedown','single-leg-takedown','collar-drag','body-lock']),
    'bridge-and-roll':  ('Bridge and Roll',      'ブリッジ&ロール',    'Bridge e Roll',         ['mount','full-mount','americana','kimura']),
    'harai-goshi':      ('Harai Goshi',          '払腰',               'Harai Goshi',           ['hip-throw','osoto-gari','ko-uchi-gari','o-goshi']),
    'ippon-seoi-nage':  ('Ippon Seoi Nage',      '一本背負い投げ',     'Ippon Seoi Nage',       ['hip-throw','osoto-gari','seoi-nage','shoulder-throw']),
    'snap-down':        ('Snap Down',            'スナップダウン',     'Snap Down',             ['double-leg-takedown','single-leg-takedown','arm-drag','collar-drag']),
    'estima-lock':      ('Estima Lock',          'エスティマロック',   'Estima Lock',           ['toe-hold','ankle-lock','knee-bar','calf-slicer','outside-heel-hook']),
}

fixed = 0

for lang in ['en', 'ja', 'pt']:
    pages = {}
    for fname in sorted(os.listdir(lang)):
        if fname.endswith('.html'):
            with open(f'{lang}/{fname}') as f:
                pages[fname] = f.read()

    for target_slug, (name_en, name_ja, name_pt, donor_slugs) in TARGETS.items():
        target_fname = f'{target_slug}.html'
        if lang == 'ja':
            target_name = name_ja
        elif lang == 'pt':
            target_name = name_pt
        else:
            target_name = name_en

        added = 0
        for donor_slug in donor_slugs:
            if added >= 3:
                break
            donor_fname = f'{donor_slug}.html'
            if donor_fname not in pages:
                continue
            content = pages[donor_fname]
            if target_slug in content:
                continue  # already linked

            # Find the related-links div and append a link
            pattern = r'(<div class="related-links">)(.*?)(</div>)'
            m = re.search(pattern, content, re.DOTALL)
            if m:
                new_link = f'\n<a href="{target_slug}.html">{target_name}</a>'
                new_content = content[:m.start(3)] + new_link + content[m.start(3):]
                pages[donor_fname] = new_content
                with open(f'{lang}/{donor_fname}', 'w') as f:
                    f.write(new_content)
                fixed += 1
                added += 1

print(f"Added {fixed} internal links across all languages")
