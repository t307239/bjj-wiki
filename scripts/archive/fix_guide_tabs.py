#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add horizontal guide tab navigation to bjj-wiki en/ja/pt index.html

Replaces the 4 stacked guide sections (Featured / Gear / Training / New Guides)
with a pill-tab UI. Sections 2-4 are hidden by default; clicking a tab pill
shows the selected section. The contact form is moved to after the New Guides
section so it doesn't float between hidden tab panels.
"""

import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WIKI_DIR = os.path.dirname(SCRIPT_DIR)

LANG_TABS = {
    'en': [
        ('guide-featured', '📌 Featured'),
        ('guide-gear',     '🛒 Gear'),
        ('guide-training', '🏋️ Training'),
        ('guide-new',      '📚 New Guides'),
    ],
    'ja': [
        ('guide-featured', '📌 特集'),
        ('guide-gear',     '🛒 ギア'),
        ('guide-training', '🏋️ トレーニング'),
        ('guide-new',      '📚 新着'),
    ],
    'pt': [
        ('guide-featured', '📌 Destaque'),
        ('guide-gear',     '🛒 Gear'),
        ('guide-training', '🏋️ Treino'),
        ('guide-new',      '📚 Novos'),
    ],
}

TAB_CSS = """\
<style>
.guide-tabs{display:flex;gap:8px;overflow-x:auto;padding:0 0 12px;margin:32px 0 0;scrollbar-width:thin;-webkit-overflow-scrolling:touch}
.guide-tabs::-webkit-scrollbar{height:4px}
.guide-tabs::-webkit-scrollbar-thumb{background:#2d2d4e;border-radius:2px}
.guide-tab{flex-shrink:0;padding:8px 18px;border-radius:20px;border:1px solid #1e2a3a;background:#111827;color:#9aa8bb;cursor:pointer;font-size:.9rem;font-family:inherit;transition:all .2s;white-space:nowrap;outline:none}
.guide-tab.active{background:#7c3aed;border-color:#7c3aed;color:#fff;font-weight:700}
.guide-tab:hover:not(.active){border-color:#7c3aed;color:#e2e2ee}
</style>"""

TAB_JS = """\
<script>
function showGuideTab(id,btn){
  ['guide-featured','guide-gear','guide-training','guide-new'].forEach(function(g){
    var el=document.getElementById(g);
    if(el)el.style.display=(g===id)?'':'none';
  });
  document.querySelectorAll('.guide-tab').forEach(function(b){b.classList.remove('active')});
  btn.classList.add('active');
}
</script>"""


def make_tab_bar(tabs):
    btns = ''
    for i, (tid, label) in enumerate(tabs):
        active = ' active' if i == 0 else ''
        btns += (
            f'  <button class="guide-tab{active}" '
            f'onclick="showGuideTab(\'{tid}\', this)">{label}</button>\n'
        )
    return f'<div class="guide-tabs">\n{btns}</div>'


def process_file(lang, filepath):
    with open(filepath, encoding='utf-8') as f:
        html = f.read()

    # Idempotency check
    if 'class="guide-tabs"' in html:
        print(f'  {lang}/index.html: already processed, skipping')
        return False

    # ------------------------------------------------------------------
    # Step 1: Extract and remove the contact form section
    # ------------------------------------------------------------------
    contact_re = re.compile(
        r'(<section class="contact-section"[^>]*>.*?</section>)'
        r'(\s*(?:<!--\s*/Formspree\s*-->)?)',
        re.DOTALL
    )
    contact_match = contact_re.search(html)
    contact_html = ''
    if contact_match:
        contact_html = contact_match.group(1)
        html = html[:contact_match.start()] + html[contact_match.end():]
        print(f'    contact form extracted')
    else:
        print(f'    WARNING: contact form not found in {filepath}')

    # ------------------------------------------------------------------
    # Step 2: Add id="guide-featured" to Featured section
    # ------------------------------------------------------------------
    featured_marker = '<!-- Featured Guides -->\n<section style="margin:32px 0">'
    if featured_marker in html:
        html = html.replace(
            featured_marker,
            '<!-- Featured Guides -->\n<section id="guide-featured" style="margin:32px 0">',
            1
        )
        print(f'    guide-featured id added')
    else:
        print(f'    WARNING: Featured section marker not found in {filepath}')

    # ------------------------------------------------------------------
    # Step 3: Add id="guide-gear" + display:none  (marker: 🛒 emoji in h2)
    # ------------------------------------------------------------------
    # Pattern: <section style="margin:32px 0">\n<h2 ...>🛒
    gear_old = re.search(
        r'<section style="margin:32px 0">\n(<h2[^>]*>🛒)',
        html
    )
    if gear_old:
        html = re.sub(
            r'<section style="margin:32px 0">\n(<h2[^>]*>🛒)',
            r'<section id="guide-gear" style="margin:32px 0;display:none">\n\1',
            html, count=1
        )
        print(f'    guide-gear id added')
    else:
        print(f'    WARNING: Gear section not found in {filepath}')

    # ------------------------------------------------------------------
    # Step 4: Add id="guide-training" + display:none  (marker: 🏋 emoji)
    # ------------------------------------------------------------------
    training_old = re.search(
        r'<section style="margin:32px 0">\n(<h2[^>]*>🏋)',
        html
    )
    if training_old:
        html = re.sub(
            r'<section style="margin:32px 0">\n(<h2[^>]*>🏋)',
            r'<section id="guide-training" style="margin:32px 0;display:none">\n\1',
            html, count=1
        )
        print(f'    guide-training id added')
    else:
        print(f'    WARNING: Training section not found in {filepath}')

    # ------------------------------------------------------------------
    # Step 5: Add id="guide-new" + display:none  (marker: 📚 emoji in h2)
    # ------------------------------------------------------------------
    new_old = re.search(
        r'<section style="margin:32px 0">\n(<h2[^>]*>📚)',
        html
    )
    if new_old:
        html = re.sub(
            r'<section style="margin:32px 0">\n(<h2[^>]*>📚)',
            r'<section id="guide-new" style="margin:32px 0;display:none">\n\1',
            html, count=1
        )
        print(f'    guide-new id added')
    else:
        print(f'    WARNING: New Guides section not found in {filepath}')

    # ------------------------------------------------------------------
    # Step 6: Insert tab CSS + bar before <!-- Featured Guides -->
    # ------------------------------------------------------------------
    tab_bar = make_tab_bar(LANG_TABS[lang])
    insert_before = '<!-- Featured Guides -->'
    if insert_before in html:
        html = html.replace(
            insert_before,
            TAB_CSS + '\n' + tab_bar + '\n' + insert_before,
            1
        )
        print(f'    tab bar inserted')
    else:
        print(f'    WARNING: could not find insertion point for tab bar')

    # ------------------------------------------------------------------
    # Step 7: Insert JS + contact form after guide-new closing </section>
    # ------------------------------------------------------------------
    guide_new_pos = html.find('id="guide-new"')
    if guide_new_pos == -1:
        print(f'  ERROR: guide-new not found after processing {filepath}')
        return False

    # Find the closing </section> of guide-new
    # The guide-new section contains only <div> and <a> tags inside, so
    # the first </section> after id="guide-new" is its own closing tag.
    section_close_pos = html.find('</section>', guide_new_pos)
    if section_close_pos == -1:
        print(f'  ERROR: no closing </section> after guide-new in {filepath}')
        return False

    insert_point = section_close_pos + len('</section>')
    suffix = '\n' + TAB_JS
    if contact_html:
        suffix += '\n' + contact_html + '\n<!-- /Formspree -->'
    html = html[:insert_point] + suffix + html[insert_point:]
    print(f'    JS + contact form inserted after guide-new')

    # ------------------------------------------------------------------
    # Write result
    # ------------------------------------------------------------------
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'  ✅ {lang}/index.html done')
    return True


if __name__ == '__main__':
    total_ok = 0
    for lang in ['en', 'ja', 'pt']:
        filepath = os.path.join(WIKI_DIR, lang, 'index.html')
        print(f'\nProcessing {lang}/index.html ...')
        if os.path.exists(filepath):
            if process_file(lang, filepath):
                total_ok += 1
        else:
            print(f'  WARNING: {filepath} not found')
    print(f'\nDone. {total_ok}/3 files processed.')
