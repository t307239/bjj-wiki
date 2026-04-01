#!/usr/bin/env python3
"""
BJJ Wiki — ドメイン一括更新スクリプト

旧URL: t307239.github.io/bjj-wiki
新URL: wiki.bjj-app.net

対象:
- 全HTMLファイル (hreflang, canonical, og:url, internal links)
- sitemap.xml
- feed.xml
- search.json
"""
import os
import re

WIKI_ROOT = os.path.join(os.path.dirname(__file__), "..")
OLD_DOMAIN = "t307239.github.io/bjj-wiki"
NEW_DOMAIN = "wiki.bjj-app.net"

# Also handle https://t307239.github.io/bjj-wiki/ → https://wiki.bjj-app.net/
OLD_BASE = f"https://{OLD_DOMAIN}"
NEW_BASE = f"https://{NEW_DOMAIN}"

count = 0
file_count = 0

def process_file(fpath):
    global count, file_count
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    if OLD_DOMAIN not in content and OLD_BASE not in content:
        return

    new_content = content.replace(OLD_BASE, NEW_BASE)
    new_content = new_content.replace(OLD_DOMAIN, NEW_DOMAIN)

    if new_content != content:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)
        replacements = content.count(OLD_DOMAIN) + content.count(OLD_BASE)
        count += replacements
        file_count += 1

# Process all HTML files in en/, ja/, pt/
for lang in ["en", "ja", "pt"]:
    langdir = os.path.join(WIKI_ROOT, lang)
    if not os.path.isdir(langdir):
        continue
    for fname in os.listdir(langdir):
        if fname.endswith(".html"):
            process_file(os.path.join(langdir, fname))

# Process root files
for fname in ["sitemap.xml", "feed.xml", "CNAME"]:
    fpath = os.path.join(WIKI_ROOT, fname)
    if os.path.exists(fpath):
        process_file(fpath)

# Process search.json files
for lang in ["en", "ja", "pt"]:
    sjpath = os.path.join(WIKI_ROOT, lang, "search.json")
    if os.path.exists(sjpath):
        process_file(sjpath)

# Create CNAME file for GitHub Pages custom domain
cname_path = os.path.join(WIKI_ROOT, "CNAME")
with open(cname_path, "w", encoding="utf-8") as f:
    f.write("wiki.bjj-app.net\n")
print(f"Created CNAME file: wiki.bjj-app.net")

print(f"\nDomain updated: {OLD_DOMAIN} → {NEW_DOMAIN}")
print(f"Files modified: {file_count}")
print(f"Total replacements: {count}")
