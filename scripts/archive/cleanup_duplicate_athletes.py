#!/usr/bin/env python3
"""
cleanup_duplicate_athletes.py — z255b: athletes-section の重複除去

【発見経緯】
z255 の wiki MCP 検証で ja/armbar.html を確認した際、
「🏆この技を使うエリート選手」 section が連続 2 回表示される bug を発見。
58 pages (en=28, ja=28, pt=2) で同様の duplicate あり。

【原因】
3 scripts (patch_all_features.py / patch_new_page_features.py / generate_bjj_wiki.py) が
それぞれ <div class="athletes-section"> を inject。idempotency guard
("athletes-section" not in content) が後付け追加されたが、guard が無かった頃の
duplicate は残存している。

【修正方針】
- 各 page で 2 つ目以降の `<div class="athletes-section">...</div>` を削除
- 1 つ目は保持 (オリジナルとして)
- Idempotent: 1 つだけの page は無変更

Usage:
  python3 scripts/cleanup_duplicate_athletes.py --dry-run         # 確認
  python3 scripts/cleanup_duplicate_athletes.py --apply           # 全 lang
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANG_DIRS = ["en", "ja", "pt"]


def cleanup_html(html: str) -> tuple[str, int]:
    """Remove all but the first <div class="athletes-section">...</div>.
    Returns (modified_html, duplicates_removed)."""
    # Find all athletes-section blocks (non-greedy match to closing </div></div>)
    # Structure: <div class="athletes-section"><h2>...</h2><div class="athlete-chips">...</div></div>
    pattern = re.compile(
        r'<div class="athletes-section">.*?</div>\s*</div>',
        re.DOTALL,
    )
    matches = list(pattern.finditer(html))
    if len(matches) <= 1:
        return html, 0

    # Keep first, remove subsequent ones (in reverse order to preserve positions)
    duplicates_removed = 0
    new_html = html
    for m in reversed(matches[1:]):
        # Also strip trailing whitespace/newlines after the duplicate
        end = m.end()
        # Consume trailing \n and whitespace following the duplicate
        while end < len(new_html) and new_html[end] in (" ", "\n", "\t"):
            end += 1
        new_html = new_html[:m.start()] + new_html[end:]
        duplicates_removed += 1
    return new_html, duplicates_removed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Write changes (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--lang", choices=["en", "ja", "pt", "all"], default="all")
    args = parser.parse_args()

    do_write = args.apply
    langs = LANG_DIRS if args.lang == "all" else [args.lang]
    total_files = 0
    total_dups = 0

    for lang in langs:
        d = ROOT / lang
        if not d.exists():
            continue
        files_in_lang = 0
        dups_in_lang = 0
        for fp in sorted(d.glob("*.html")):
            if fp.name in ("index.html", "404.html"):
                continue
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            new_html, n = cleanup_html(html)
            if n > 0:
                files_in_lang += 1
                dups_in_lang += n
                if do_write:
                    fp.write_text(new_html, encoding="utf-8")
        action = "removed" if do_write else "would remove"
        print(f"  {lang}/: {files_in_lang} files ({dups_in_lang} duplicates {action})")
        total_files += files_in_lang
        total_dups += dups_in_lang

    print()
    mode = "APPLIED" if do_write else "DRY-RUN"
    print(f"📊 [{mode}] {total_files} files, {total_dups} duplicates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
