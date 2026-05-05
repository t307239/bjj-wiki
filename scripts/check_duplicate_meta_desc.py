#!/usr/bin/env python3
"""
check_duplicate_meta_desc.py — z255w: 同 locale 内の meta description 衝突検査
(20th lint)

Google は同 locale 内の同一 meta description 複数 page を duplicate content
判定し、両方の SEO 評価を下げる。z255u (duplicate title) の sibling lint。

検査対象:
  - en/, ja/, pt/ の各 page で <meta name="description"> を抽出
  - noindex page は除外
  - 同 locale 内で同 description 複数 page → CRITICAL

allow-list (一定数 page で同じ description が現れるのは仕様):
  - 短い description (< 30 chars) は除外 (空状態 fallback の可能性)
  - "BJJ Wiki — ..." 等の generic stub は除外

--ci flag で duplicate group > 0 → exit 1
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]


def main() -> int:
    per_lang: dict[str, dict[str, list[str]]] = {l: defaultdict(list) for l in LANGS}

    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            if "noindex" in html[:1500]:
                continue
            m = re.search(
                r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']',
                html,
                re.IGNORECASE,
            )
            if not m:
                continue
            desc = m.group(1).strip()
            if len(desc) < 30:
                continue
            per_lang[lang][desc].append(f"{lang}/{fp.name}")

    total_groups = 0
    total_pages = 0
    for lang in LANGS:
        dups = {d: p for d, p in per_lang[lang].items() if len(p) > 1}
        groups = len(dups)
        pages = sum(len(p) for p in dups.values())
        total_groups += groups
        total_pages += pages
        print(f"  {lang}: {groups} duplicate-meta groups ({pages} pages)")
        for d, paths in list(dups.items())[:5]:
            print(f"    « {d[:80]} »")
            for p in paths[:4]:
                print(f"       {p}")

    print()
    if total_groups == 0:
        print("✅ No duplicate <meta description> within any locale.")
    else:
        print(f"🔴 Total duplicate groups: {total_groups} ({total_pages} pages)")

    if "--ci" in sys.argv:
        return 1 if total_groups > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
