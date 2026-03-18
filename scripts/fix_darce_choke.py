#!/usr/bin/env python3
"""
Fix D'アルセ → ダースチョーク replacement and add cross-links
"""

import os
import re

JA_DIR = "/sessions/keen-sharp-davinci/mnt/bjj-wiki/ja"

# Target files and cross-link pairs
CROSS_LINKS = {
    "bjj-d-arce-choke-details.html": {
        "link_to": ["bjj-anaconda-choke.html", "bjj-turtle-top-attacks.html"],
        "section_title_ja": "関連する技"
    },
    "bjj-turtle-top-attacks.html": {
        "link_to": ["bjj-d-arce-choke-details.html", "bjj-clock-choke.html"],
        "section_title_ja": "関連する技"
    },
    "bjj-anaconda-choke.html": {
        "link_to": ["bjj-d-arce-choke-details.html"],
        "section_title_ja": "関連する技"
    },
    "bjj-clock-choke.html": {
        "link_to": ["bjj-turtle-top-attacks.html", "bjj-d-arce-choke-details.html"],
        "section_title_ja": "関連する技"
    },
}

def replace_darce_text(html: str) -> str:
    """Replace D'アルセ with ダースチョーク"""
    return html.replace("D'アルセ", "ダースチョーク")

def add_cross_link_section(html: str, file_key: str, slug: str) -> str:
    """Add related techniques section if it doesn't exist"""
    if file_key not in CROSS_LINKS:
        return html

    config = CROSS_LINKS[file_key]
    link_files = config["link_to"]
    section_title = config["section_title_ja"]

    # Check if section already exists
    if "関連する技" in html or "Related Techniques" in html:
        return html

    # Build related links HTML
    related_html = f'<h3>{section_title}</h3>\n<ul>'
    for link_file in link_files:
        # Convert file name to display name
        name = link_file.replace("bjj-", "").replace(".html", "").replace("-", " ").title()
        related_html += f'\n<li><a href="{link_file}">{name}</a></li>'
    related_html += '\n</ul>'

    # Insert before closing body or before footer if it exists
    if '</main>' in html:
        html = html.replace('</main>', f'{related_html}\n</main>', 1)
    elif '</article>' in html:
        html = html.replace('</article>', f'{related_html}\n</article>', 1)
    else:
        # Fallback: insert before closing body
        html = html.replace('</body>', f'{related_html}\n</body>', 1)

    return html

# Process Japanese files
def main():
    processed = 0
    replaced = 0

    for filename in os.listdir(JA_DIR):
        if not filename.endswith('.html'):
            continue

        filepath = os.path.join(JA_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # Replace D'アルセ with ダースチョーク
        if "D'アルセ" in content:
            content = replace_darce_text(content)
            replaced += 1

        # Add cross-links
        content = add_cross_link_section(content, filename, filename.replace('.html', ''))

        # Write back if changed
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            processed += 1

    print(f"✅ Processed {processed} files")
    print(f"✅ Replaced D'アルセ in {replaced} files")

if __name__ == '__main__':
    main()
