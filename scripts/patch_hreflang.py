#!/usr/bin/env python3
"""hreflang未設定ページにhreflangタグを追加するパッチ"""
import os, re, glob

BASE = os.path.dirname(__file__) + "/.."
SITE = "https://wiki.bjj-app.net"

def patch_file(path, lang):
    with open(path) as f:
        html = f.read()
    if 'hreflang' in html:
        return False
    if 'http-equiv="refresh"' in html:
        return False
    slug = os.path.basename(path)
    tags = f'''<link rel="alternate" hreflang="x-default" href="{SITE}/en/{slug}">
<link rel="alternate" hreflang="en" href="{SITE}/en/{slug}">
<link rel="alternate" hreflang="ja" href="{SITE}/ja/{slug}">
<link rel="alternate" hreflang="pt" href="{SITE}/pt/{slug}">
'''
    if '<link rel="canonical"' in html:
        html = html.replace('<link rel="canonical"', tags + '<link rel="canonical"', 1)
    elif '</head>' in html:
        html = html.replace('</head>', tags + '</head>', 1)
    else:
        return False
    with open(path,'w') as f: f.write(html)
    return True

def main():
    patched = skipped = 0
    skip_names = {"index.html","privacy.html","about.html","404.html"}
    for lang in ["en","ja","pt"]:
        for path in glob.glob(os.path.join(BASE, lang, "*.html")):
            if os.path.basename(path) in skip_names: continue
            if patch_file(path, lang): patched += 1
            else: skipped += 1
    print(f"hreflang added: {patched} pages, skipped: {skipped}")

if __name__ == "__main__":
    main()
