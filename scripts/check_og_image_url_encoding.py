#!/usr/bin/env python3
"""
check_og_image_url_encoding.py — z260j

og:image / twitter:image の URL に literal space (encoded されていない
URL parameter) が混入していないか検査。Twitter / Facebook crawler は
URL 内の literal space を不正な URI とみなし image fetch を諦める = SNS
share preview 死亡の silent bug。

Background:
- generate_bjj_wiki.py / patch_og_image_dynamic.py は urllib.parse.quote()
  で title parameter を URL encode している (正)
- しかし z260j 時点で 167 page が literal space 入りで存在していた
  (旧 generator の名残 / 別 path で生成された page)
- 一度 fix script で 167 page をクリーンアップ → 以後この lint で永久 block

Pattern A: og:image (or twitter:image) URL に literal " " が含まれる
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("en", "ja", "pt")

# og:image / twitter:image content value 抽出
META_IMG_RE = re.compile(
    r'<meta\s+(?:property|name)=["\'](?:og:image|twitter:image)["\']\s+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)


def scan() -> list[tuple[str, str]]:
    bad: list[tuple[str, str]] = []
    for lang in LANGS:
        for p in sorted((ROOT / lang).glob("*.html")):
            try:
                text = p.read_text(encoding="utf-8")
            except OSError:
                continue
            for m in META_IMG_RE.finditer(text):
                url = m.group(1)
                if " " in url:
                    bad.append((str(p.relative_to(ROOT)), url[:80]))
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ci", action="store_true", help="exit 1 if any drift found")
    args = ap.parse_args()
    bad = scan()
    print(f"❌ og:image / twitter:image with unencoded spaces: {len(bad)}")
    if bad:
        print()
        print("Sample:")
        for f, u in bad[:10]:
            print(f"  {f}: {u}")
        if args.ci:
            print()
            print("🔴 Fix with: python3 scripts/fix_og_image_url_encoding.py --apply")
            return 1
    else:
        print("✅ All og:image / twitter:image URLs are properly encoded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
