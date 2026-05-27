#!/usr/bin/env python3
"""
BJJ Wiki — Full Layout Unification Script

Forces ALL content pages (non-redirect) to have:
1. Type C header: 🥋 BJJ Wiki logo + lang-nav (EN/JA/PT)
2. Consistent <body> structure: progress-bar → container → header → content
3. Removes old nav bars, duplicate headers, stale EN|JA|PT links

Does NOT change:
- Page content (<h1>, <h2>, <p>, sections etc.)
- <head> section (meta tags, CSS)
- Redirect pages (meta http-equiv=refresh)
"""
import os
import re

WIKI_ROOT = os.path.join(os.path.dirname(__file__), "..")
LANGS = ["en", "ja", "pt"]
LANG_FLAGS = {"en": "🇺🇸 EN", "ja": "🇯🇵 JA", "pt": "🇧🇷 PT"}

def build_header(lang, filename):
    """Build Type C header HTML"""
    links = []
    for l in ["en", "ja", "pt"]:
        active = ' class="active"' if l == lang else ''
        links.append(f'    <a href="../{l}/{filename}"{active}>{LANG_FLAGS[l]}</a>')
    return f'''<header>
  <a href="../{lang}/index.html" class="logo">🥋 BJJ Wiki</a>
  <nav class="lang-nav">
{chr(10).join(links)}
  </nav>
</header>'''

def has_type_c_header(content):
    """Check if page already has proper Type C header"""
    return 'class="logo"' in content and 'BJJ Wiki</a>' in content

def is_redirect(content):
    return 'http-equiv="refresh"' in content

def fix_page(content, lang, filename):
    """Fix a content page to have Type C layout"""

    # Skip redirects
    if is_redirect(content):
        return content

    # Already has Type C header
    if has_type_c_header(content):
        return content

    new_header = build_header(lang, filename)

    # Strategy: Find <body> tag and inject header right after it
    # Then remove any old headers/navs

    # 1. Remove old nav bars (various patterns)
    # Old nav with Home/A-Z links
    content = re.sub(
        r'<header>\s*<nav>.*?</nav>\s*</header>',
        '',
        content,
        flags=re.DOTALL
    )
    # Old <nav> blocks
    content = re.sub(
        r'<nav>\s*<a[^>]*>🥋[^<]*</a>.*?</nav>',
        '',
        content,
        flags=re.DOTALL
    )
    # Bare EN|JA|PT links
    content = re.sub(
        r'<div class="lang-nav">.*?</div>\s*',
        '',
        content,
        flags=re.DOTALL
    )
    content = re.sub(
        r'\s*<a href="[^"]*">EN</a>\s*\|\s*<a href="[^"]*">JA</a>\s*\|\s*<a href="[^"]*">PT</a>\s*',
        '',
        content
    )
    # Old standalone header with h1 (but keep the h1 content)
    old_h = re.search(r'<header>\s*<h1>(.*?)</h1>(.*?)</header>', content, re.DOTALL)
    if old_h:
        # Keep the h1 and desc, remove header tags
        h1_content = old_h.group(1)
        desc_content = old_h.group(2).strip()
        replacement = f'\n<h1>{h1_content}</h1>\n{desc_content}\n' if desc_content else f'\n<h1>{h1_content}</h1>\n'
        content = content[:old_h.start()] + replacement + content[old_h.end():]

    # 2. Inject Type C header after <body> or after progress-bar
    # Find injection point
    body_match = re.search(r'<body[^>]*>', content)
    if not body_match:
        return content

    inject_pos = body_match.end()

    # Skip past GTM noscript if present
    gtm_match = re.search(r'<!-- Google Tag Manager \(noscript\) -->.*?<!-- End Google Tag Manager \(noscript\) -->', content[inject_pos:], re.DOTALL)
    if gtm_match:
        inject_pos += gtm_match.end()

    # Skip past progress-bar div if present
    progress_match = re.match(r'\s*<div[^>]*(?:id="read-progress"|class="progress-bar")[^>]*></div>', content[inject_pos:])
    if progress_match:
        inject_pos += progress_match.end()

    # Check if container div follows
    container_match = re.match(r'\s*<div class="container">', content[inject_pos:])
    if container_match:
        # Insert header inside container, right after opening tag
        inject_pos += container_match.end()
        content = content[:inject_pos] + '\n' + new_header + '\n' + content[inject_pos:]
    else:
        # No container — wrap content in container and add header
        # Find closing </body>
        content = content[:inject_pos] + '\n<div class="container">\n' + new_header + '\n' + content[inject_pos:]

    return content

# Process all pages
count = 0
for lang in LANGS:
    langdir = os.path.join(WIKI_ROOT, lang)
    if not os.path.isdir(langdir):
        continue
    for fname in os.listdir(langdir):
        if not fname.endswith(".html") or fname == "index.html":
            continue
        fpath = os.path.join(langdir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        if is_redirect(content):
            continue

        if has_type_c_header(content):
            continue

        new_content = fix_page(content, lang, fname)
        if new_content != content:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            count += 1

print(f"Pages fixed with Type C header: {count}")
