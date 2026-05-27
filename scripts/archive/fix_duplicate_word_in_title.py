#!/usr/bin/env python3
"""
fix_duplicate_word_in_title.py — z255ll: 17 EN page で title/h1 に
"Guide Guide" / "System System" 等 content word の重複が発生していた bug を fix.

Root cause: 旧 generator が slug 末尾の "-guide" 等を context として認識せず、
固定 "Guide" suffix を append → "X Guide" + "Guide" = "X Guide Guide" が
17 page で発生。

修正方針:
  - <title> / <h1> / og:title の "Word Word" → "Word" 圧縮
  - Allowed: BJJ/Jiu/Wiki (legitimate repeats)
  - PT は大文字始まりの後の (de/no/em/da/do) 等 preposition 重複に注意
    → 大小文字区別あり (lowercase + uppercase = OK), 同 case 重複のみ fix

Idempotent: 何度実行しても二重圧縮にならない (regex は同 case 連続のみ match)
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

ALLOWED = {"bjj", "jiu", "wiki"}

# 同 case の単語連続 (case-sensitive で判定、PT preposition の de + De La Riva 等を除外)
DUP_RE = re.compile(r"\b(\w+)\s+\1\b")  # case-sensitive (no re.IGNORECASE)


def collapse_in(text: str) -> tuple[str, int]:
    """Replace consecutive same-case duplicates. Returns (new_text, n_changes)."""
    n = 0

    def repl(m):
        nonlocal n
        word = m.group(1)
        if word.lower() in ALLOWED:
            return m.group(0)
        n += 1
        return word

    new = DUP_RE.sub(repl, text)
    return new, n


def patch_html(html: str) -> tuple[str, int]:
    total = 0
    # <title>...</title>
    def title_repl(m):
        nonlocal total
        inner = m.group(2)
        new_inner, n = collapse_in(inner)
        total += n
        return f"{m.group(1)}{new_inner}{m.group(3)}"

    new = re.sub(
        r"(<title[^>]*>)([^<]+)(</title>)", title_repl, html, count=1
    )

    # <h1>...</h1>
    def h1_repl(m):
        nonlocal total
        inner = m.group(2)
        new_inner, n = collapse_in(inner)
        total += n
        return f"{m.group(1)}{new_inner}{m.group(3)}"

    new = re.sub(
        r"(<h1[^>]*>)([^<]+)(</h1>)", h1_repl, new, count=1
    )

    # <meta property="og:title" content="...">
    def og_repl(m):
        nonlocal total
        val = m.group(2)
        new_val, n = collapse_in(val)
        total += n
        return f"{m.group(1)}{new_val}{m.group(3)}"

    new = re.sub(
        r'(<meta\s+property="og:title"\s+content=")([^"]+)(")',
        og_repl,
        new,
        count=1,
    )

    return new, total


def main():
    print("🔧 fix_duplicate_word_in_title.py — z255ll")
    files_fixed = 0
    total_changes = 0
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            new, n = patch_html(html)
            if n > 0:
                fp.write_text(new, encoding="utf-8")
                files_fixed += 1
                total_changes += n
    print(f"  Fixed {total_changes} duplicate words across {files_fixed} files")


if __name__ == "__main__":
    main()
