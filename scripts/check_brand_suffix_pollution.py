#!/usr/bin/env python3
"""
check_brand_suffix_pollution.py — z255x: title 内の brand suffix 重複検査 (21st lint)

`<Title> — BJJ Wiki | BJJ Wiki` のように brand suffix が 2 回出現する状態を
検出。複数 generator が独立に suffix を付加した結果生じる silent SEO bug。

検出 pattern:
  A. "— BJJ Wiki | BJJ Wiki" / "- BJJ Wiki | BJJ Wiki" (em-dash + pipe 二重)
  B. "| BJJ Wiki | BJJ Wiki" (pipe 二重)
  C. "| BJJ Wiki Brasil | BJJ Wiki" (PT 用 localized brand + global brand 二重)

SEO 影響:
  - Title 60 char limit を圧迫し技名 keyword が truncate
  - SERP で brand 文字列が冗長に見える
  - 同 brand 文字列を 2 回含むため keyword stuffing 判定リスク

--ci flag で hit > 0 → exit 1
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

PATTERNS = [
    re.compile(r"[—\-]\s*BJJ\s*Wiki\s*\|\s*BJJ\s*Wiki", re.IGNORECASE),
    re.compile(r"\|\s*BJJ\s*Wiki\s*\|\s*BJJ\s*Wiki", re.IGNORECASE),
    re.compile(r"\|\s*BJJ\s*Wiki\s*Brasil\s*\|\s*BJJ\s*Wiki(?!\s*Brasil)", re.IGNORECASE),
]


def main() -> int:
    hits: list[tuple[str, str, str]] = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            if "noindex" in html[:1500]:
                continue
            # title
            m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
            if m:
                t = m.group(1)
                for p in PATTERNS:
                    if p.search(t):
                        hits.append((f"{lang}/{fp.name}", "title", t[:80]))
                        break
            # og:title
            om = re.search(
                r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)',
                html, re.IGNORECASE,
            )
            if om:
                t = om.group(1)
                for p in PATTERNS:
                    if p.search(t):
                        hits.append((f"{lang}/{fp.name}", "og:title", t[:80]))
                        break

    print(f"❌ Brand suffix pollution: {len(hits)}")
    for src, where, t in hits[:8]:
        print(f"   {src} [{where}]: {t}")
    if not hits:
        print("\n✅ No brand suffix pollution.")

    if "--ci" in sys.argv:
        return 1 if hits else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
