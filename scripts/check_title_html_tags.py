#!/usr/bin/env python3
"""
check_title_html_tags.py — z255kk: <title> 内 HTML tag 混入検査 (26th lint)

HTML 仕様で `<title>` element の content は CDATA-like で**子要素禁止**。
内部に `<strong>`, `<span>`, `<em>` 等の inline HTML element を入れると:
  - 一部 SEO scraper / SNS unfurl parser が最初の `<` で truncate
  - Google SERP の title 表示が「Guia de Posição Saddle: Sistema Supremo de」のように切れる
  - browser title bar には element が strip された text が出るため、
    content と SEO scraper の見え方が divergent になる silent bug

Round 25 で `pt/bjj-saddle-position-guide.html` の `<title>` に
`<strong>Heel Hook</strong>` が埋め込まれていた事象を契機に追加。
24 PT page に同 pattern が drift していた (旧 SEO emphasis script の遺物)。

--ci flag で hit > 0 → exit 1
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

# <title> ... </title> を greedy 走査 (改行を跨いで closing tag まで)
TITLE_RE = re.compile(r"<title>([\s\S]*?)</title>", re.IGNORECASE)
# 内部に inline HTML element があるか (任意の `<a-z` 開始タグを検出)
INNER_TAG_RE = re.compile(r"<[a-zA-Z]")


def main() -> int:
    issues: list[tuple[str, str]] = []
    for lang in LANGS:
        lang_dir = REPO_ROOT / lang
        if not lang_dir.is_dir():
            continue
        for fp in lang_dir.glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            m = TITLE_RE.search(html)
            if not m:
                continue
            inner = m.group(1)
            if INNER_TAG_RE.search(inner):
                issues.append((f"{lang}/{fp.name}", inner.strip()[:90]))

    print(f"❌ <title> with embedded HTML tags (SEO scraper truncation risk): {len(issues)}")
    for src, snippet in issues[:10]:
        print(f"   {src}: {snippet}")
    if len(issues) > 10:
        print(f"   ... and {len(issues) - 10} more")
    if not issues:
        print("\n✅ All <title> elements are tag-free CDATA.")

    if "--ci" in sys.argv:
        return 1 if issues else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
