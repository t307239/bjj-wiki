#!/usr/bin/env python3
"""
fix_external_link_noreferrer.py — z255ddd: 4,371 page で external link に
rel="noreferrer" 追加 (privacy + security 強化)

旧 silent privacy bug:
- 外部 link (Twitter share / YouTube / Reddit share 等) で target="_blank" rel="noopener" のみ
- Referer header で「wiki.bjj-app.net/ja/anaconda-choke.html」が外部 site に漏出
- 結果: user の閲覧 page が Twitter / Google 等に tracking される privacy 問題
- noopener は tab nabbing 防止のみ、referrer leak は防がない

修正: rel="noopener" を含む external link に noreferrer を追加 (rel="noopener noreferrer")
- 同一 origin link は対象外 (referrer leak の問題なし)
- noopener が無い link は z255v fix で既に追加済み (z255v target-blank-security)
- idempotent: 既に noreferrer ある link は touch しない

(generator script の patch_target_blank_noopener.py と同期して恒久対応)
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def patch_html(html: str) -> tuple[str, int]:
    """Returns (new_html, count_replaced)."""
    count = 0

    def replace_link(m: re.Match) -> str:
        nonlocal count
        full_tag = m.group(0)
        # Skip if not target=_blank
        if 'target="_blank"' not in full_tag:
            return full_tag
        # Skip if not external (http://...)
        href_m = re.search(r'href="(http[^"]+)"', full_tag)
        if not href_m:
            return full_tag
        # Get current rel
        rel_m = re.search(r'\brel="([^"]+)"', full_tag)
        if not rel_m:
            return full_tag
        rel = rel_m.group(1)
        # Already has noreferrer? skip
        if 'noreferrer' in rel:
            return full_tag
        # Has noopener? add noreferrer
        if 'noopener' not in rel:
            return full_tag
        new_rel = rel + ' noreferrer'
        new_tag = full_tag.replace(f'rel="{rel}"', f'rel="{new_rel}"', 1)
        count += 1
        return new_tag

    new = re.sub(r'<a\b[^>]*>', replace_link, html)
    return new, count


def patch_page(fp: Path) -> int:
    html = fp.read_text(encoding="utf-8")
    if "noindex" in html[:1500]:
        return 0
    new, count = patch_html(html)
    if count > 0:
        fp.write_text(new, encoding="utf-8")
    return count


def main():
    print("🔧 fix_external_link_noreferrer.py — z255ddd")
    total_links = 0
    total_pages = 0
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            n = patch_page(fp)
            total_links += n
            if n > 0:
                total_pages += 1
    print(f"  ✅ {total_links} external links updated across {total_pages} pages")


if __name__ == "__main__":
    main()
