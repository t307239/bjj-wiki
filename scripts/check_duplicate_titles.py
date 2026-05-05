#!/usr/bin/env python3
"""
check_duplicate_titles.py — z255u: 同一 locale 内の <title> 衝突検査 (18th lint)

Google は同 locale 内で同一 title 複数 page を duplicate content と判定し、
両方 (or どちらか) の SEO 評価を下げる。

検査対象:
  - en/, ja/, pt/ の各 page で <title> を抽出
  - noindex page は除外 (consolidation redirect)
  - 同一 locale 内で同 title 複数 page を CRITICAL 扱い

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
            m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            if not m:
                continue
            title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            if title:
                per_lang[lang][title].append(f"{lang}/{fp.name}")

    total_groups = 0
    total_pages = 0
    for lang in LANGS:
        dups = {t: p for t, p in per_lang[lang].items() if len(p) > 1}
        groups = len(dups)
        pages = sum(len(p) for p in dups.values())
        total_groups += groups
        total_pages += pages
        print(f"  {lang}: {groups} duplicate groups ({pages} pages)")
        for t, paths in list(dups.items())[:6]:
            print(f"    « {t[:60]} »")
            for p in paths[:4]:
                print(f"       {p}")

    print()
    if total_groups == 0:
        print("✅ No duplicate <title> within any locale.")
    else:
        print(f"🔴 Total duplicate groups: {total_groups} ({total_pages} pages)")

    if "--ci" in sys.argv:
        return 1 if total_groups > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
