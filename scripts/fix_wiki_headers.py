#!/usr/bin/env python3
"""
BJJ Wiki — ヘッダー構造統一スクリプト

Type A (1276ページ): <header><h1>Title</h1><p>desc</p></header><nav>Home/A-Z...</nav>
Type B (71ページ): <div class="lang-nav">EN|JA|PT</div><article><header>...<h1>
→ Type C style: <header><a class="logo">🥋 BJJ Wiki</a><nav class="lang-nav">...</nav></header>

Type C のヘッダー構造（テンプレート）:
<header>
  <a href="index.html" class="logo">🥋 BJJ Wiki</a>
  <nav class="lang-nav">
    <a href="../{lang}/filename" class="active">🇺🇸 EN</a>
    <a href="../{lang}/filename">🇯🇵 JA</a>
    <a href="../{lang}/filename">🇧🇷 PT</a>
  </nav>
</header>
"""
import os
import re

WIKI_ROOT = os.path.join(os.path.dirname(__file__), "..")
LANGS = ["en", "ja", "pt"]

LANG_FLAGS = {"en": "🇺🇸 EN", "ja": "🇯🇵 JA", "pt": "🇧🇷 PT"}

def build_type_c_header(lang, filename):
    """Build a Type C style header"""
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

def fix_type_a(content, lang, filename):
    """Fix Type A: replace old <header><h1>...</h1></header><nav>...</nav> with Type C header"""
    # Remove old nav block (Home/A-Z/Skill Tree...)
    # Remove various nav patterns
    content = re.sub(
        r'<nav>\s*<a[^>]*>🏠\s*(?:Home|ホーム|Início).*?</nav>',
        '',
        content,
        flags=re.DOTALL
    )
    # Also remove inline nav with style attributes
    content = re.sub(
        r'<div[^>]*>\s*<a[^>]*>🏠\s*(?:Home|ホーム|Início).*?</div>',
        '',
        content,
        flags=re.DOTALL
    )

    # Replace old header with Type C header
    # Old: <header><h1>Title</h1><p>desc</p></header>
    old_header = re.search(r'<header>.*?</header>', content, re.DOTALL)
    if old_header:
        # Extract title and desc from old header
        title_match = re.search(r'<h1>(.*?)</h1>', old_header.group(), re.DOTALL)
        desc_match = re.search(r'<p>(.*?)</p>', old_header.group(), re.DOTALL)

        new_header = build_type_c_header(lang, filename)

        # Keep title and desc but move them outside header
        title_html = f'\n<h1>{title_match.group(1)}</h1>' if title_match else ''
        desc_html = f'\n<p class="intro" style="color:var(--muted);text-align:center;margin-bottom:24px">{desc_match.group(1)}</p>' if desc_match else ''

        content = content[:old_header.start()] + new_header + title_html + desc_html + content[old_header.end():]

    return content

def fix_type_b(content, lang, filename):
    """Fix Type B: replace EN|JA|PT div + article header with Type C header"""
    # Remove old lang-nav (various patterns)
    content = re.sub(
        r'<div class="lang-nav">.*?</div>\s*',
        '',
        content,
        flags=re.DOTALL
    )
    # Also remove bare inline EN|JA|PT links
    content = re.sub(
        r'\s*<a href="[^"]*">EN</a>\s*\|\s*<a href="[^"]*">JA</a>\s*\|\s*<a href="[^"]*">PT</a>\s*',
        '',
        content,
        flags=re.DOTALL
    )

    # Find and replace the article>header structure
    old_header = re.search(r'<article>\s*<header>(.*?)</header>', content, re.DOTALL)
    if old_header:
        inner = old_header.group(1)
        title_match = re.search(r'<h1>(.*?)</h1>', inner, re.DOTALL)
        intro_match = re.search(r'<p class="intro">(.*?)</p>', inner, re.DOTALL)
        diff_match = re.search(r'<span class="diff-badge[^"]*">(.*?)</span>', inner, re.DOTALL)

        new_header = build_type_c_header(lang, filename)

        parts = [new_header]
        if diff_match:
            parts.append(f'\n<div style="text-align:center;margin-bottom:8px"><span class="badge badge-diff">{diff_match.group(1)}</span></div>')
        if title_match:
            parts.append(f'\n<h1 style="text-align:center">{title_match.group(1)}</h1>')
        if intro_match:
            parts.append(f'\n<p class="intro">{intro_match.group(1)}</p>')

        replacement = '\n'.join(parts) + '\n<article>'
        content = content[:old_header.start()] + replacement + content[old_header.end():]

    return content

count_a = 0
count_b = 0

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

        original = content

        # Detect Type A (has old nav with Home/A-Z)
        if re.search(r'<nav>\s*<a href="[^"]*">🏠', content):
            content = fix_type_a(content, lang, fname)
            if content != original:
                count_a += 1

        # Detect Type B (has EN|JA|PT div at top)
        elif '<div class="lang-nav"><a href=' in content and '>EN</a> |' in content:
            content = fix_type_b(content, lang, fname)
            if content != original:
                count_b += 1

        if content != original:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)

print(f"Type A headers fixed: {count_a} pages")
print(f"Type B headers fixed: {count_b} pages")
print(f"Total: {count_a + count_b} pages")
