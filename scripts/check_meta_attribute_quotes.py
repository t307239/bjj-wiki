#!/usr/bin/env python3
"""
check_meta_attribute_quotes.py — z255aa: <meta description> 内 unescaped `"` 検査
(24th lint)

`<meta name="description" content="...">` の content 値に escape されていない `"`
が含まれると、HTML attribute parser が最初の内側 `"` で truncate してしまう
silent SEO bug。Google が読む description は最初の `"` までで切れる → SERP snippet
が空 / 不完全。

og:description でも同じ pattern を検査。

検出方針:
  - <meta name="description" content="`...`> の `...` 部分に `"` 含むか
  - <meta property="og:description" content="..." > の `...` 部分に `"` 含むか

--ci flag で hit > 0 → exit 1
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

PATTERNS = [
    ('description', re.compile(r'<meta\s+name="description"\s+content="', re.IGNORECASE)),
    ('og:description', re.compile(r'<meta\s+property="og:description"\s+content="', re.IGNORECASE)),
]
END_RE = re.compile(r'"\s*/?>')


def main() -> int:
    issues: list[tuple[str, str, str]] = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            for label, p in PATTERNS:
                m = p.search(html)
                if not m:
                    continue
                em = END_RE.search(html, m.end())
                if not em:
                    continue
                content = html[m.end():em.start()]
                if '"' in content:
                    issues.append((f"{lang}/{fp.name}", label, content[:80]))

    print(f'❌ <meta> with unescaped `"` in content (HTML truncation): {len(issues)}')
    for src, label, snippet in issues[:8]:
        print(f"   {src} [{label}]: ...{snippet}...")
    if not issues:
        print("\n✅ All <meta> description/og:description content properly escaped.")

    if "--ci" in sys.argv:
        return 1 if issues else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
