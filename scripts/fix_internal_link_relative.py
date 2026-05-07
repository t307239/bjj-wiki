#!/usr/bin/env python3
"""
fix_internal_link_relative.py — z255jjj: 33 page で body <a> link が同 locale 内
internal page に対して absolute URL を使用 → relative に変換

旧 silent UX/perf bug:
- <a href="https://wiki.bjj-app.net/en/closed-guard.html">Closed Guard</a>
  形式の absolute URL が body 内 <a> link で 33 page 残留
- 結果:
  - 同一 origin なのに browser が full URL parse してから resolve = 微 perf 低下
  - lang-switcher で /ja/ 等に switch しても link は /en/ のまま (UX 不整合)
  - canonical / hreflang は absolute 必須なのでそれは対象外、body 内 <a> のみ対象

修正:
- <a ... href="https://wiki.bjj-app.net/<same_lang>/<slug>.html" ...> を
  <a ... href="<slug>.html" ...> に変換 (同 page と同 locale)
- canonical / hreflang / OG image など <link> tag や <meta> は対象外
- twitter share / 外部 social は対象外 (URL params で encode 済)
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE = "https://wiki.bjj-app.net"


def patch_page(fp: Path) -> int:
    html = fp.read_text(encoding="utf-8")
    if "noindex" in html[:1500]:
        return 0
    lang = fp.parts[-2]
    count = 0

    def replace_a_link(m: re.Match) -> str:
        nonlocal count
        full_tag = m.group(0)
        # Skip if not <a> (e.g. <link>)
        if not full_tag.startswith('<a'): return full_tag
        # Extract href
        href_m = re.search(r'href="(' + re.escape(SITE) + r'/' + lang + r'/([^"]+\.html))"', full_tag)
        if not href_m: return full_tag
        # Skip share/twitter context (the URL is encoded in params, not a direct href)
        # Also skip if href contains "?" (query params)
        if '?' in href_m.group(1): return full_tag
        # Replace href with relative
        new_tag = full_tag.replace(href_m.group(1), href_m.group(2), 1)
        count += 1
        return new_tag

    new_html = re.sub(r'<a\b[^>]*>', replace_a_link, html)
    if count > 0:
        fp.write_text(new_html, encoding="utf-8")
    return count


def main():
    print("🔧 fix_internal_link_relative.py — z255jjj")
    total = 0; pages_fixed = 0
    for lang in ("en","ja","pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists(): continue
        for fp in sorted(lang_dir.glob("*.html")):
            n = patch_page(fp)
            total += n
            if n > 0: pages_fixed += 1
    print(f"  ✅ {total} links converted across {pages_fixed} pages")


if __name__ == "__main__":
    main()
