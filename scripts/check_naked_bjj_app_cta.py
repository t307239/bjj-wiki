#!/usr/bin/env python3
"""
check_naked_bjj_app_cta.py — z255y: naked `https://bjj-app.net` href 検査 (22nd lint)

Wiki → App funnel CTA は必ず `/login?ref=wiki&page=<slug>` 形式であるべき。
naked `https://bjj-app.net` のままだと:
  - 旧 referrer 情報が落ちて funnel attribution 不能
  - root page (CVR 低い) に着地し /login (CVR 高い) を経由しない
  - per-page funnel tracking 不能

検査: <script> 外で `href="https://bjj-app.net"` (no path) → CRITICAL

--ci flag で hit > 0 → exit 1
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
NAKED_RE = re.compile(r'href=["\']https://bjj-app\.net["\']', re.IGNORECASE)


def main() -> int:
    hits: list[str] = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            cleaned = SCRIPT_RE.sub("", html)
            if NAKED_RE.search(cleaned):
                hits.append(f"{lang}/{fp.name}")

    print(f'❌ Naked `href="https://bjj-app.net"` (no funnel tracking): {len(hits)}')
    for h in hits[:10]:
        print(f"   {h}")
    if not hits:
        print("\n✅ All bjj-app.net CTAs use /login?ref=wiki funnel tracking.")

    if "--ci" in sys.argv:
        return 1 if hits else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
