#!/usr/bin/env python3
"""
fix_h1_brand_pollution.py — z255zz: 115 page で h1 に '| BJJ Wiki Brasil' suffix が
混入しているのを除去

旧 silent SEO bug:
- 115 PT page で <h1>Guia de Triângulo... | BJJ Wiki Brasil</h1>
- <h1> は article title のみであるべき。brand suffix は <title> tag に Next.js
  template (`%s | BJJ Wiki`) で auto 付与されるため、h1 に付ける必要なし
- 結果: SEO keyword stuffing、h1 char limit (~60) 圧迫、SERP 表示不整合

修正: h1 の `\\s*\\|\\s*BJJ\\s*Wiki(\\s+Brasil)?\\s*$` を strip
idempotent: 既に clean な h1 は touch しない
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

BRAND_SUFFIX_RE = re.compile(r'\s*\|\s*BJJ\s*Wiki(\s+Brasil)?\s*$', re.IGNORECASE)


def patch_page(fp: Path) -> bool:
    html = fp.read_text(encoding="utf-8")
    if "noindex" in html[:1500]:
        return False

    h1_m = re.search(r'(<h1[^>]*>)([^<]+)(</h1>)', html)
    if not h1_m:
        return False

    h1_text = h1_m.group(2)
    cleaned = BRAND_SUFFIX_RE.sub('', h1_text).strip()

    if cleaned == h1_text:
        return False  # already clean

    new_h1 = h1_m.group(1) + cleaned + h1_m.group(3)
    new_html = html.replace(h1_m.group(0), new_h1, 1)
    fp.write_text(new_html, encoding="utf-8")
    return True


def main():
    print("🔧 fix_h1_brand_pollution.py — z255zz")
    fixed = 0
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            if patch_page(fp):
                fixed += 1
    print(f"  ✅ {fixed} pages fixed")


if __name__ == "__main__":
    main()
