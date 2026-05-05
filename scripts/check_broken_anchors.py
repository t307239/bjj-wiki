#!/usr/bin/env python3
"""
check_broken_anchors.py — z255z: ページ内アンカー fragment 検査 (23rd lint)

`<a href="#section-x">` が同一ページに `id="section-x"` を持つ要素を欠く場合、
TOC click でスクロールが起きず silent UX bug。Lighthouse SEO 監査でも減点。

検査対象:
  - en/, ja/, pt/ の HTML 内 <a href="#X">
  - <script>...</script> 内は除外 (動的 anchor 生成)
  - 空 fragment (`#`, `#top`, `#main`) は除外 (慣習的 placeholder)

--ci flag で hit > 0 → exit 1
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
ID_RE = re.compile(r'\bid\s*=\s*["\']([^"\']+)["\']')
ANCHOR_RE = re.compile(r'href=["\']#([^"\']+)["\']')
PLACEHOLDER_FRAGS = {"top", "main"}


def main() -> int:
    issues: list[tuple[str, str]] = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            cleaned = SCRIPT_RE.sub("", html)
            ids = set(ID_RE.findall(cleaned))
            for m in ANCHOR_RE.finditer(cleaned):
                frag = m.group(1)
                if not frag or frag in PLACEHOLDER_FRAGS:
                    continue
                if frag not in ids:
                    issues.append((f"{lang}/{fp.name}", frag))

    print(f"❌ Broken anchor fragments: {len(issues)}")
    from collections import Counter
    top = Counter(f for _, f in issues).most_common(8)
    for f, c in top:
        print(f"  {c:5d}x  #{f}")
    if not issues:
        print("\n✅ All in-page anchors resolve to existing ids.")

    if "--ci" in sys.argv:
        return 1 if issues else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
