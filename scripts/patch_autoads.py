#!/usr/bin/env python3
"""
AdSense Auto Ads への移行パッチ
- 無効な data-ad-slot="auto" の <ins> ブロックを削除
- <head> の AdSense script タグは保持（Auto Ads として機能）
- Google のオートプレースメントで最適位置に自動配置される
"""
import os, re, glob

SITE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 削除対象: <ins class="adsbygoogle" ... data-ad-slot="auto"> ブロック全体 + push() script
AD_BLOCK_PATTERN = re.compile(
    r'<ins class="adsbygoogle"[^>]*data-ad-slot="auto"[^>]*>.*?</ins>\s*'
    r'<script>\(adsbygoogle = window\.adsbygoogle \|\| \[\]\)\.push\(\{\}\);</script>',
    re.DOTALL
)

def patch_file(path):
    with open(path, encoding="utf-8") as f:
        html = f.read()
    new_html, count = AD_BLOCK_PATTERN.subn("", html)
    if count > 0:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_html)
        return count
    return 0

def main():
    html_files = glob.glob(os.path.join(SITE_DIR, "**/*.html"), recursive=True)
    html_files += glob.glob(os.path.join(SITE_DIR, "*.html"))

    total_files = 0
    total_removed = 0
    skip = {"google9ef7b9e441cc36f8.html"}

    for path in html_files:
        fname = os.path.basename(path)
        if fname in skip:
            continue
        n = patch_file(path)
        if n > 0:
            total_files += 1
            total_removed += n

    print(f"✅ {total_files} files patched, {total_removed} invalid ad blocks removed")
    print("   AdSense Auto Ads now active (head script only)")

if __name__ == "__main__":
    main()
