#!/usr/bin/env python3
"""
fix_naked_bjj_app_cta.py — z255y: 711 件の naked `href="https://bjj-app.net"` を
funnel-tracked URL に upgrade.

正しい形式: https://bjj-app.net/login?ref=wiki&page=<slug>
  - /login = アプリ登録ページ (CVR 最大)
  - ref=wiki = wiki funnel と判別 (analytics で source 分離)
  - page=<slug> = どの記事から流入したか per-page 追跡

z176 の patch_funnel_cta.py は ?page=bottom / ?page=float の placement 区別だが、
古い in-content CTA は naked URL のまま 711 件残っていた。

Idempotent: 既に /login? を含む URL は skip。
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]


def patch_html(html: str, slug: str) -> tuple[str, int]:
    new_url = f"https://bjj-app.net/login?ref=wiki&page={slug}"
    fixed = 0

    def repl(m):
        nonlocal fixed
        fixed += 1
        return f'href="{new_url}"'

    # Match exact naked URL (no path / no query)
    new = re.sub(r'href=["\']https://bjj-app\.net["\']', repl, html)
    return new, fixed


def main():
    print("🔧 fix_naked_bjj_app_cta.py — z255y")
    files_fixed = 0
    total_fixed = 0
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            slug = fp.stem  # filename without extension
            new, n = patch_html(html, slug)
            if n > 0:
                fp.write_text(new, encoding="utf-8")
                files_fixed += 1
                total_fixed += n
    print(f"  Upgraded {total_fixed} naked CTAs across {files_fixed} files")


if __name__ == "__main__":
    main()
