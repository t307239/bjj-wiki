#!/usr/bin/env python3
"""
fix_breadcrumb_locale_drift.py — z255xx: 987 page で <div class="breadcrumb"> が
EN のまま残留 → h1 (locale 翻訳済) に同期

旧 silent UX bug:
- 505 JA page で `BJJ Wiki › Kimura to Back Guide` 等 EN article title
- 482 PT page で `BJJ Wiki › Tie-Up Control in BJJ` 等 EN article title
- + PT で brand suffix `| BJJ Wiki B...` が breadcrumb に混入 + truncate
- 結果: locale 不整合 + UX 損失 (JA user に英語 breadcrumb)

修正:
- 各 page の h1 text を抽出
- <div class="breadcrumb"> の last crumb を h1 text で置換
- brand suffix `| BJJ Wiki...` は除去

idempotent: 既に h1 と breadcrumb が同期している page は touch しない。
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

BRAND_SUFFIX_RE = re.compile(r'\s*\|\s*BJJ\s*Wiki.*$', re.IGNORECASE)


def patch_page(fp: Path, lang: str) -> str:
    if lang == "en":
        return "skip-en"
    html = fp.read_text(encoding="utf-8")
    if "noindex" in html[:1500]:
        return "skip-noindex"

    # Extract h1
    h1_m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    if not h1_m:
        return "skip-no-h1"
    h1_text = h1_m.group(1).strip()
    # Strip brand suffix in case it leaked into h1 too
    h1_text = BRAND_SUFFIX_RE.sub('', h1_text).strip()

    # Find breadcrumb element
    bc_m = re.search(r'(<div class="breadcrumb">)(.*?)(</div>)', html, re.DOTALL)
    if not bc_m:
        return "skip-no-breadcrumb"

    crumb_inner = bc_m.group(2)
    # Replace last crumb (after final ›) with h1_text
    # Pattern: ...› LAST_CRUMB
    new_inner = re.sub(
        r'(.*›\s*)([^›]+?)(\s*)$',
        lambda m: m.group(1) + h1_text + m.group(3),
        crumb_inner,
        flags=re.DOTALL
    )
    # Also clean up any brand suffix leaked into breadcrumb
    new_inner = BRAND_SUFFIX_RE.sub('', new_inner)

    if new_inner == crumb_inner:
        return "skip-already-synced"

    new_html = html[:bc_m.start(2)] + new_inner + html[bc_m.end(2):]
    fp.write_text(new_html, encoding="utf-8")
    return "patched"


def main():
    print("🔧 fix_breadcrumb_locale_drift.py — z255xx")
    stats = {"patched": 0, "skip-already-synced": 0, "skip-en": 0,
             "skip-noindex": 0, "skip-no-h1": 0, "skip-no-breadcrumb": 0}
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            r = patch_page(fp, lang)
            stats[r] = stats.get(r, 0) + 1
    for k, v in stats.items():
        if v > 0:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
