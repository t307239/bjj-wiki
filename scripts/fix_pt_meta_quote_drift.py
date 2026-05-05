#!/usr/bin/env python3
"""
fix_pt_meta_quote_drift.py — z255aa: 52 PT page で <meta description> 内に
unescaped `"` があり HTML attribute parser が truncate していた silent SEO bug.

Pattern: `<meta name="description" content="Marcus "Buchecha" Almeida ...">`
                                                    ↑ ここで truncate
  → Google sees: "Marcus " のみ (実質空 description)
  → SERP snippet が空 / 不完全 / 間違った内容

修正方針:
  - <meta name="description" ...> tag 全体を取得 (broken 構造込み)
  - content="..." の最初の `"` から最後の `"` までを真の content として再構築
  - 内側の `"` を `'` (apostrophe) に置換
  - 長い場合は 160 chars に truncate (Google snippet 上限)

og:description にも同じ pattern があれば同期 fix。
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def find_broken_meta(html: str, prop_pattern: str) -> tuple[int, int, str] | None:
    """Find a <meta ... content="..."> tag where content has internal `"`.

    prop_pattern includes through `content="` so m_start.end() is the start of
    the description body content.
    Returns (start, end, full_content) or None.
    """
    m_start = re.search(prop_pattern, html, re.IGNORECASE)
    if not m_start:
        return None
    content_start = m_start.end()
    # Find the closing `">` of the meta tag (skip any internal `"`)
    end_re = re.compile(r'"\s*/?>')
    em = end_re.search(html, content_start)
    if not em:
        return None
    content = html[content_start:em.start()]
    return (m_start.start(), em.end(), content)


def has_internal_quote(content: str) -> bool:
    """True if content has any `"` (which would have broken HTML)."""
    return '"' in content


def patch_html(html: str) -> int:
    fixed = 0

    # name="description" — pattern includes `content="` to position cursor at content body
    found = find_broken_meta(html, r'<meta\s+name="description"\s+content="')
    if found and has_internal_quote(found[2]):
        start, end, content = found
        new_content = content.replace('"', "'")
        # Truncate if super long (likely concatenation bug)
        if len(new_content) > 200:
            new_content = new_content[:160].rstrip() + "..."
        new_tag = f'<meta name="description" content="{new_content}">'
        html = html[:start] + new_tag + html[end:]
        fixed += 1

    # property="og:description"
    found = find_broken_meta(html, r'<meta\s+property="og:description"\s+content="')
    if found and has_internal_quote(found[2]):
        start, end, content = found
        new_content = content.replace('"', "'")
        if len(new_content) > 200:
            new_content = new_content[:160].rstrip() + "..."
        new_tag = f'<meta property="og:description" content="{new_content}">'
        html = html[:start] + new_tag + html[end:]
        fixed += 1

    return fixed, html


def main():
    print("🔧 fix_pt_meta_quote_drift.py — z255aa")
    files_fixed = 0
    total_fixes = 0
    for lang in ("pt", "ja", "en"):
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            n, new_html = patch_html(html)
            if n > 0:
                fp.write_text(new_html, encoding="utf-8")
                files_fixed += 1
                total_fixes += n
    print(f"  Fixed {total_fixes} broken meta tags across {files_fixed} files")


if __name__ == "__main__":
    main()
