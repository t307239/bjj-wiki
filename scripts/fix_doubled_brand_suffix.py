#!/usr/bin/env python3
"""
fix_doubled_brand_suffix.py — z255x: 65 page の <title> で "BJJ Wiki — BJJ Wiki | BJJ Wiki"
等の brand suffix 二重化を fix.

旧 generator が `<Title> — BJJ Wiki` を作っていたところに、後発の patch script が
`| BJJ Wiki` を append した結果、`Title — BJJ Wiki | BJJ Wiki` という二重 suffix が
65 page に残った。

SEO 損失:
  - Title 60 char limit を圧迫 → 技名 keyword が truncate される
  - SERP で見栄えが悪い (重複ブランド suffix)
  - 同じ brand 文字列が title で 2 回出現 → keyword stuffing 判定リスク

修正方針: `— BJJ Wiki | BJJ Wiki` → `| BJJ Wiki` (em-dash + space)
         `- BJJ Wiki | BJJ Wiki` → `| BJJ Wiki` (hyphen 版も)

og:title も同期修正。Idempotent。
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]


def collapse(text: str) -> str:
    # `... — BJJ Wiki | BJJ Wiki` → `... | BJJ Wiki`
    new = re.sub(
        r"\s*[—\-]\s*BJJ\s*Wiki\s*\|\s*BJJ\s*Wiki",
        " | BJJ Wiki",
        text,
        flags=re.IGNORECASE,
    )
    # `... | BJJ Wiki Brasil | BJJ Wiki` → `... | BJJ Wiki Brasil`
    # (PT 専用 brand を残し、後付けの一般 suffix を除去)
    new = re.sub(
        r"\|\s*BJJ\s*Wiki\s*Brasil\s*\|\s*BJJ\s*Wiki(?!\s*Brasil)",
        "| BJJ Wiki Brasil",
        new,
        flags=re.IGNORECASE,
    )
    # `... | BJJ Wiki | BJJ Wiki` → `... | BJJ Wiki` (defense in depth)
    new = re.sub(
        r"\|\s*BJJ\s*Wiki\s*\|\s*BJJ\s*Wiki",
        "| BJJ Wiki",
        new,
        flags=re.IGNORECASE,
    )
    return new


def patch_html(html: str) -> tuple[str, bool]:
    changed = False

    # <title>
    def title_repl(m):
        nonlocal changed
        inner = m.group(2)
        new_inner = collapse(inner)
        if new_inner != inner:
            changed = True
        return f"{m.group(1)}{new_inner}{m.group(3)}"

    new = re.sub(
        r"(<title[^>]*>)(.*?)(</title>)",
        title_repl,
        html,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # og:title
    def og_repl(m):
        nonlocal changed
        val = m.group(2)
        new_val = collapse(val)
        if new_val != val:
            changed = True
        return f"{m.group(1)}{new_val}{m.group(3)}"

    new = re.sub(
        r'(<meta\s+property=["\']og:title["\']\s+content=["\'])([^"\']+)(["\'])',
        og_repl,
        new,
        count=1,
        flags=re.IGNORECASE,
    )

    return new, changed


def main() -> int:
    print("🔧 fix_doubled_brand_suffix.py — z255x")
    fixed = 0
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            new, changed = patch_html(html)
            if changed:
                fp.write_text(new, encoding="utf-8")
                fixed += 1
    print(f"  Fixed {fixed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
