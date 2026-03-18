#!/usr/bin/env python3
"""
BJJ Wiki - Internal Link Checker
Checks for broken internal links within t307239.github.io/bjj-wiki/
"""

import os
import re
from pathlib import Path
from collections import defaultdict

WIKI_DIR = "/sessions/keen-sharp-davinci/mnt/bjj-wiki"
LANGS = ["en", "ja", "pt"]

def get_all_pages():
    """Build a set of all valid HTML pages"""
    valid_pages = set()

    for lang in LANGS:
        lang_dir = os.path.join(WIKI_DIR, lang)
        if os.path.isdir(lang_dir):
            for filename in os.listdir(lang_dir):
                if filename.endswith('.html'):
                    valid_pages.add(filename)

    return valid_pages

def extract_links(html_content: str) -> list:
    """Extract href links from HTML"""
    # Match href="..." and href='...'
    pattern = r'href=["\']([^"\']+)["\']'
    return re.findall(pattern, html_content)

def is_internal_link(link: str) -> bool:
    """Check if link is an internal BJJ wiki link"""
    # Ignore external links, anchors, and special protocols
    if link.startswith(('http://', 'https://', 'mailto:', 'tel:', 'javascript:')):
        return False
    if link.startswith('#'):
        return False
    if link == '' or link == '/':
        return False
    return True

def check_link_exists(link: str, valid_pages: set) -> bool:
    """Check if a link points to an existing page"""
    # Handle relative links like "page.html" or "./page.html" or "../en/page.html"
    link = link.lstrip('./')

    # Remove anchors
    if '#' in link:
        link = link.split('#')[0]

    # Check if file exists in any language directory
    return link in valid_pages

def main():
    valid_pages = get_all_pages()
    broken_links = defaultdict(list)
    total_links = 0
    broken_count = 0

    print("🔍 Scanning BJJ Wiki for broken links...\n")

    for lang in LANGS:
        lang_dir = os.path.join(WIKI_DIR, lang)
        if not os.path.isdir(lang_dir):
            continue

        for filename in os.listdir(lang_dir):
            if not filename.endswith('.html'):
                continue

            filepath = os.path.join(lang_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                links = extract_links(content)
                for link in links:
                    if not is_internal_link(link):
                        continue

                    total_links += 1
                    if not check_link_exists(link, valid_pages):
                        broken_links[f"{lang}/{filename}"].append(link)
                        broken_count += 1

            except Exception as e:
                print(f"⚠️  Error reading {lang}/{filename}: {e}")

    # Report results
    print(f"📊 Total internal links checked: {total_links}")
    print(f"❌ Broken links found: {broken_count}\n")

    if broken_count > 0:
        print("=" * 70)
        print("BROKEN LINKS BY FILE:")
        print("=" * 70)
        for filepath in sorted(broken_links.keys()):
            links = broken_links[filepath]
            print(f"\n📄 {filepath}")
            for link in sorted(set(links)):
                print(f"   → {link}")

    # Find most common broken links
    all_broken = []
    for links in broken_links.values():
        all_broken.extend(links)

    if all_broken:
        print("\n" + "=" * 70)
        print("MOST COMMON BROKEN LINKS:")
        print("=" * 70)
        from collections import Counter
        for link, count in Counter(all_broken).most_common(20):
            print(f"{count:3d}x  {link}")

    print("\n✅ Scan complete!")

if __name__ == '__main__':
    main()
