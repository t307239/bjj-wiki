#!/usr/bin/env python3
"""
Generate cross-links between related BJJ Wiki pages.
Maps 50 key pages to their related topics for SEO and navigation benefits.
"""

import os
import re
from pathlib import Path

# Define key page relationships (slug -> list of related slugs)
CROSS_LINKS = {
    # Guard Fundamentals
    "bjj-guard-fundamentals": [
        "bjj-guard-passing-fundamentals",
        "bjj-open-guard-fundamentals",
        "bjj-closed-guard-systems",
    ],
    "bjj-closed-guard-systems": [
        "bjj-guard-fundamentals",
        "bjj-guard-sweep-systems",
        "bjj-armbar-setup-guide",
    ],
    "bjj-open-guard-fundamentals": [
        "bjj-guard-fundamentals",
        "bjj-spider-guard-system",
        "bjj-collar-sleeve-guard",
        "bjj-de-la-riva-attacks",
    ],

    # Guard Passing
    "bjj-guard-passing-fundamentals": [
        "bjj-guard-fundamentals",
        "bjj-pressure-fundamentals",
        "bjj-knee-on-belly-escape-system",
    ],
    "bjj-pressure-passing-guide": [
        "bjj-guard-passing-fundamentals",
        "bjj-smash-pass-guide",
        "bjj-stack-pass-guide",
    ],

    # Sweeps
    "bjj-sweep-fundamentals": [
        "bjj-guard-fundamentals",
        "bjj-flower-sweep-guide",
        "bjj-scissor-sweep-guide",
        "bjj-hip-bump-sweep-guide",
    ],
    "bjj-flower-sweep-guide": [
        "bjj-sweep-fundamentals",
        "bjj-hip-bump-sweep-guide",
        "bjj-back-take-from-guard-system",
    ],

    # Submissions
    "bjj-armbar-setup-guide": [
        "bjj-closed-guard-systems",
        "bjj-mount-system",
        "bjj-back-control-system",
    ],
    "bjj-triangle-setup-guide": [
        "bjj-guard-fundamentals",
        "bjj-closed-guard-systems",
        "bjj-submission-chain-attacks",
    ],
    "bjj-submission-chain-attacks": [
        "bjj-armbar-setup-guide",
        "bjj-triangle-setup-guide",
        "bjj-collar-choke-system",
    ],

    # Positions
    "bjj-mount-system": [
        "bjj-mount-attack-system",
        "bjj-mount-escape-system",
        "bjj-pressure-fundamentals",
    ],
    "bjj-back-control-system": [
        "bjj-back-escape-guide",
        "bjj-hook-management-guide",
        "bjj-body-lock-escapes",
    ],

    # Escapes
    "bjj-mount-escape-system": [
        "bjj-mount-system",
        "bjj-hip-escape-system",
        "bjj-technical-standup-guide",
    ],
    "bjj-back-escape-guide": [
        "bjj-back-control-system",
        "bjj-turtle-defense-guide",
        "bjj-seat-belt-control-guide",
    ],

    # Leg Lock Systems
    "bjj-leg-lock-system": [
        "bjj-kneebar-guide",
        "bjj-calf-slicer-guide",
        "bjj-heel-hook-guide",
    ],
    "bjj-heel-hook-guide": [
        "bjj-leg-lock-system",
        "bjj-leg-lock-defense-system",
        "bjj-ashi-garami-guide",
    ],

    # Takedowns
    "bjj-takedown-entry-systems": [
        "bjj-clinch-work-guide",
        "bjj-wrestling-integration",
        "bjj-foot-sweep-guide",
    ],
    "bjj-clinch-work-guide": [
        "bjj-takedown-entry-systems",
        "bjj-collar-tie-system",
        "bjj-body-lock-takedown",
    ],

    # No-Gi
    "bjj-nogi-guard-guide": [
        "bjj-guard-fundamentals",
        "bjj-nogi-passing-guide",
        "bjj-nogi-chokes-guide",
    ],
    "bjj-nogi-chokes-guide": [
        "bjj-nogi-guard-guide",
        "bjj-guillotine-from-sprawl",
        "bjj-front-headlock-guide",
    ],

    # Conditioning & Training
    "bjj-periodization-guide": [
        "bjj-strength-programming-guide",
        "bjj-cardio-systems-guide",
        "bjj-recovery-optimization-guide",
    ],
    "bjj-strength-training-guide": [
        "bjj-grip-strength-training",
        "bjj-core-training-guide",
        "bjj-explosive-power-bjj",
    ],

    # Competition
    "bjj-tournament-bracket-guide": [
        "bjj-match-strategy-guide",
        "bjj-points-scoring-guide",
        "bjj-competition-prep-advanced",
    ],
    "bjj-match-strategy-guide": [
        "bjj-tournament-bracket-guide",
        "bjj-game-plan-development",
        "bjj-guard-pull-strategy",
    ],

    # Fundamentals
    "bjj-posture-in-guard": [
        "bjj-base-in-bjj",
        "bjj-pressure-fundamentals",
        "bjj-connection-points-guide",
    ],
    "bjj-base-in-bjj": [
        "bjj-posture-in-guard",
        "bjj-technical-standup-guide",
        "bjj-inside-position-guide",
    ],

    # Concepts
    "bjj-kuzushi-bjj": [
        "bjj-pressure-fundamentals",
        "bjj-balance-in-bjj",
        "bjj-inside-position-guide",
    ],
    "bjj-inside-position-guide": [
        "bjj-kuzushi-bjj",
        "bjj-base-in-bjj",
        "bjj-leverage-system-guide",
    ],
}

def get_html_files(base_dir, lang='en'):
    """Get all HTML files in a language directory."""
    lang_dir = Path(base_dir) / lang
    if not lang_dir.exists():
        return []
    return sorted(lang_dir.glob('bjj-*.html'))

def extract_slug(html_file):
    """Extract slug from filename."""
    return html_file.stem

def add_cross_links_to_file(html_file, related_slugs, lang='en'):
    """Add cross-links to a BJJ Wiki HTML file."""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Don't modify if cross-links already exist
    if '<!-- CROSS-LINKS SECTION -->' in content:
        return False

    # Build cross-link HTML
    cross_link_html = '\n<!-- CROSS-LINKS SECTION -->\n<section class="cross-links">\n<h3>Related Articles</h3>\n<ul>\n'

    for slug in related_slugs:
        title = slug.replace('bjj-', '').replace('-', ' ').title()
        cross_link_html += f'<li><a href="{slug}.html">{title}</a></li>\n'

    cross_link_html += '</ul>\n</section>\n<!-- END CROSS-LINKS SECTION -->\n'

    # Insert before footer or at end of article section
    if '</article>' in content:
        content = content.replace('</article>', f'</article>\n{cross_link_html}')
    elif '</main>' in content:
        content = content.replace('</main>', f'{cross_link_html}</main>')
    else:
        content = content.replace('</body>', f'{cross_link_html}\n</body>')

    # Write back
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

def main():
    """Generate cross-links for all key pages."""
    base_dir = '/sessions/keen-sharp-davinci/mnt/bjj-wiki'
    languages = ['en', 'ja', 'pt']

    modified_count = 0
    skipped_count = 0

    for slug, related_slugs in CROSS_LINKS.items():
        for lang in languages:
            html_file = Path(base_dir) / lang / f'{slug}.html'

            if not html_file.exists():
                skipped_count += 1
                print(f'⊘ Skip: {slug} ({lang}) — file not found')
                continue

            if add_cross_links_to_file(html_file, related_slugs, lang):
                modified_count += 1
                print(f'✓ Cross-linked: {slug} ({lang}) → {len(related_slugs)} related')
            else:
                print(f'⊘ Already linked: {slug} ({lang})')

    print(f'\n📊 Summary:')
    print(f'  Modified: {modified_count} files')
    print(f'  Skipped: {skipped_count} files')
    print(f'  Total pages targeted: {len(CROSS_LINKS)} × 3 languages = {len(CROSS_LINKS) * 3}')

if __name__ == '__main__':
    main()
