#!/usr/bin/env python3
"""
check_duplicate_word_in_title.py — z255ll: title/h1 内の同 case 単語連続検査
(26th lint).

旧 generator が slug 末尾 "-guide" 等を context として認識せず固定 "Guide" suffix
を append → "X Guide" + "Guide" = "X Guide Guide" の連続単語重複が発生していた
silent SEO bug。SERP 見栄え悪化 + keyword stuffing 判定 risk。

検査 pattern:
  - <title> / <h1> / og:title で `\b(\w+)\s+\1\b` が同 case で連続
  - PT の `de De La Riva` / `no No-Gi` 等 lowercase preposition + capitalized
    proper noun の sequence は case-sensitive 判定で除外
  - ALLOWED list (BJJ/Jiu/Wiki) は legitimate repeat として除外

--ci flag で hit > 0 → exit 1
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
ALLOWED = {"bjj", "jiu", "wiki"}

DUP_RE = re.compile(r"\b(\w+)\s+\1\b")  # case-sensitive on purpose


def main() -> int:
    issues: list[tuple[str, str, str]] = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            if "noindex" in html[:1500]:
                continue
            for tag, pat in [
                ("title", r"<title[^>]*>([^<]+)</title>"),
                ("h1", r"<h1[^>]*>([^<]+)</h1>"),
                ("og:title", r'<meta\s+property="og:title"\s+content="([^"]+)"'),
            ]:
                m = re.search(pat, html)
                if not m:
                    continue
                text = m.group(1)
                for dm in DUP_RE.finditer(text):
                    word = dm.group(1)
                    if word.lower() in ALLOWED:
                        continue
                    issues.append((f"{lang}/{fp.name}", tag, text[:80]))
                    break

    print(f"❌ Duplicate same-case word in title/h1/og:title: {len(issues)}")
    for src, tag, text in issues[:10]:
        print(f"   {src} [{tag}]: {text}")
    if not issues:
        print("\n✅ No duplicate consecutive same-case word in title/h1/og:title.")

    if "--ci" in sys.argv:
        return 1 if issues else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
