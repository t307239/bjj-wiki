#!/usr/bin/env python3
"""
patch_og_image_dynamic.py — z223
既存 4,698 Wiki ページの og:image / twitter:image を
technique-specific dynamic image (bjj-app.net /api/og?mode=technique)
に一括置換。

before: <meta property="og:image" content="https://wiki.bjj-app.net/og-image.svg">
after:  <meta property="og:image" content="https://bjj-app.net/api/og?mode=technique&category=technique&title=Triangle%20Choke&lang=en">

実行方法:
    cd ~/Claude/bjj-wiki
    python3 scripts/patch_og_image_dynamic.py            # dry-run
    python3 scripts/patch_og_image_dynamic.py --apply    # 実行
"""
from __future__ import annotations
import argparse
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("en", "ja", "pt")
APP_OG_BASE = "https://bjj-app.net/api/og"
# 旧 OG 2 パターン全て対象:
#   1. wiki.bjj-app.net/og-image.svg (generic)
#   2. wiki.bjj-app.net/og/<lang>-<slug>.svg (per-page SVG)
# どちらも SVG = Twitter/X で render されない real bug (PNG/JPG/WEBP のみ対応)
OLD_OG_PATTERN = re.compile(
    r'(<meta\s+(?:property|name)="(?:og:image|twitter:image)"\s+content=")'
    r'https://wiki\.bjj-app\.net/og(?:-image|/[\w\-]+)\.svg'
    r'("\s*/?>)',
    re.IGNORECASE,
)
TITLE_PATTERN = re.compile(r"<title>([^<|]+?)\s*\|\s*BJJ Wiki</title>", re.IGNORECASE)


def slug_to_title(slug: str) -> str:
    """triangle-choke → Triangle Choke (fallback when <title> 取得失敗時)"""
    return " ".join(w.capitalize() for w in slug.split("-"))


def build_og_url(title: str, lang: str) -> str:
    q = urllib.parse.quote(title[:60], safe="")
    return f"{APP_OG_BASE}?mode=technique&category=technique&title={q}&lang={lang}"


def patch_file(fp: Path, lang: str, apply: bool) -> tuple[bool, str]:
    """1 file 修正 → (changed, message)"""
    try:
        src = fp.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"read error: {e}"

    # 旧 pattern (どちらかでも) が無ければ already migrated か対象外
    if "wiki.bjj-app.net/og-image.svg" not in src and "wiki.bjj-app.net/og/" not in src:
        return False, "already migrated or no OG meta"

    # title 抽出 (失敗時は slug fallback)
    m = TITLE_PATTERN.search(src)
    if m:
        title = m.group(1).strip()
    else:
        title = slug_to_title(fp.stem)

    new_url = build_og_url(title, lang)

    # og:image / twitter:image だけを置換 (apple-touch-icon は変えない)
    new_src = OLD_OG_PATTERN.sub(rf'\1{new_url}\2', src)

    if new_src == src:
        return False, "regex did not match"

    if apply:
        fp.write_text(new_src, encoding="utf-8")
    return True, f"OK ({title[:40]})"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="actually write (default: dry-run)")
    ap.add_argument("--limit", type=int, default=0,
                    help="process only first N files per locale (0 = all)")
    args = ap.parse_args()

    total_changed = 0
    total_skipped = 0
    total_errors = 0
    for lang in LANGS:
        lang_dir = ROOT / lang
        if not lang_dir.exists():
            print(f"⚠️  {lang}: directory not found, skipping")
            continue
        files = sorted(lang_dir.glob("*.html"))
        if args.limit > 0:
            files = files[: args.limit]
        print(f"📁 {lang}: {len(files)} files")
        changed = 0
        skipped = 0
        errors = 0
        for fp in files:
            ok, msg = patch_file(fp, lang, args.apply)
            if ok:
                changed += 1
            elif msg.startswith("read error"):
                errors += 1
                print(f"  ❌ {fp.name}: {msg}")
            else:
                skipped += 1
        print(f"  → changed={changed}, skipped={skipped}, errors={errors}")
        total_changed += changed
        total_skipped += skipped
        total_errors += errors

    print()
    mode = "APPLIED" if args.apply else "DRY-RUN (use --apply to write)"
    print(f"📊 Total [{mode}]: changed={total_changed}, skipped={total_skipped}, errors={total_errors}")
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
