#!/usr/bin/env python3
"""
check_hreflang_validity.py — z255s: hreflang 整合性検査 (16th lint)

検出する drift class:
  A. literal `{slug}` / `{lang}` テンプレ未置換 (生成スクリプトのバグで残ったもの)
  B. hreflang が指す URL が disk に無い (404 → Google index 汚染)
  C. self hreflang と current page の URL 不一致 (e.g., ja page で hreflang="ja"
     が pt のパスを指す等)
  D. public page (noindex でない) で en/ja/pt 全 locale alternate のいずれか欠落

--ci flag で drift > 0 → exit 1
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
SITE_PREFIX = "https://wiki.bjj-app.net/"

ROOT_PAGES_OK = {
    "en/index.html",
    "ja/index.html",
    "pt/index.html",
    "about.html",
    "privacy.html",
}


def main() -> int:
    valid = set()
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            valid.add(f"{lang}/{fp.name}")

    a_template = []   # Class A
    b_404 = []        # Class B
    c_self_mismatch = []  # Class C
    d_missing = []    # Class D

    template_re = re.compile(r"\{[a-z_]+\}")

    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")[:5000]  # head のみで十分
            except Exception:
                continue
            src = f"{lang}/{fp.name}"
            alts = re.findall(
                r'<link\s+rel=["\']alternate["\']\s+hreflang=["\']([a-z\-]+)["\']\s+href=["\']([^"\']+)["\']',
                html, re.IGNORECASE,
            )
            seen = set()
            for hl, href in alts:
                # Class A: テンプレ未置換
                if template_re.search(href):
                    a_template.append((src, hl, href))
                    continue
                if not href.startswith(SITE_PREFIX):
                    continue
                target = href[len(SITE_PREFIX):]
                # Class B: 404 (root pages はそのまま許容)
                if target not in valid and target not in ROOT_PAGES_OK:
                    b_404.append((src, hl, target))
                # Class C: self mismatch
                if hl == lang:
                    expected = f"{lang}/{fp.name}"
                    if target != expected:
                        c_self_mismatch.append((src, target, expected))
                seen.add(hl)

            # Class D: noindex 除外 + 全 3 locale alternate 必須
            if "noindex" in html:
                continue
            if alts and not all(l in seen for l in LANGS):
                missing = [l for l in LANGS if l not in seen]
                d_missing.append((src, missing))

    print(f"❌ A. literal {{template}} in hreflang: {len(a_template)}")
    for src, hl, href in a_template[:8]:
        print(f"   {src} [{hl}] → {href}")
    print(f"❌ B. hreflang → 404 page:             {len(b_404)}")
    for src, hl, t in b_404[:8]:
        print(f"   {src} [{hl}] → {t}")
    print(f"❌ C. self hreflang mismatch:          {len(c_self_mismatch)}")
    for src, cur, exp in c_self_mismatch[:8]:
        print(f"   {src}: cur={cur} exp={exp}")
    print(f"❌ D. missing locale alternate:        {len(d_missing)}")
    for src, miss in d_missing[:8]:
        print(f"   {src} missing {miss}")

    total = len(a_template) + len(b_404) + len(c_self_mismatch) + len(d_missing)
    if total == 0:
        print("\n✅ hreflang fully consistent.")
    else:
        print(f"\n🔴 Total drift: {total}")

    if "--ci" in sys.argv:
        return 1 if total > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
