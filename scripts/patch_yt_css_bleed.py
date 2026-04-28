#!/usr/bin/env python3
"""
patch_yt_css_bleed.py — z227 (F-26)
過去の patch_video_from_supabase.py が float-cta の <style> 内に
YouTube CSS を bleeding させた 17 EN + 17 JA + 2 PT ファイルを修復。

Before (drift state):
  <style>@keyframes slideUp{}}  /* YouTube embed */ .yt-wrap{...}</style>

After (clean):
  <style>@keyframes slideUp{}}</style>
  + 別の <style>...YouTube CSS...</style> を <head> 直前に inject

実行:
  cd ~/Claude/bjj-wiki
  python3 scripts/patch_yt_css_bleed.py            # dry-run
  python3 scripts/patch_yt_css_bleed.py --apply    # 実行
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("en", "ja", "pt")

# float-cta の <style> 内に bleeding した YouTube CSS を検出
# pattern: opacity:1}}  /* YouTube embed */\n  .yt-wrap{...} で始まり </style> で終わる
BLEED_RE = re.compile(
    r"(opacity:1\}\})"               # float-cta keyframes 末尾
    r"(\s*/\*\s*YouTube embed\s*\*/" # YouTube CSS マーカー
    r".*?)"                          # 内容 (lazy)
    r"(</style>)",                   # 閉じタグ
    re.DOTALL,
)

# 抽出した bleeding CSS を独立 <style> block にして <head> に挿入
HEAD_END_RE = re.compile(r"</head>", re.IGNORECASE)


def patch_file(fp: Path, apply: bool) -> tuple[bool, str]:
    try:
        src = fp.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"read error: {e}"

    m = BLEED_RE.search(src)
    if not m:
        return False, "no bleed"

    # 1. float-cta style から YT CSS 剥離
    keyframes_end = m.group(1)  # opacity:1}}
    yt_css = m.group(2).strip()  # /* YouTube embed */ .yt-wrap{...}
    style_close = m.group(3)  # </style>
    cleaned_block = keyframes_end + style_close
    new_src = src[:m.start()] + cleaned_block + src[m.end():]

    # 2. <head> に独立した <style> block を挿入 (yt-wrap が既に <head> に
    #    入ってないことを確認、二重定義防止)
    if "<style>\n  /* YouTube embed (z227 fixed) */" not in new_src:
        injected_block = f"<style>\n  /* YouTube embed (z227 fixed) */\n{yt_css}\n</style>\n"
        head_match = HEAD_END_RE.search(new_src)
        if head_match:
            new_src = new_src[:head_match.start()] + injected_block + new_src[head_match.start():]

    if new_src == src:
        return False, "no change after substitute"

    if apply:
        fp.write_text(new_src, encoding="utf-8")
    return True, "OK"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="実書込 (default: dry-run)")
    args = ap.parse_args()

    total = 0
    for lang in LANGS:
        d = ROOT / lang
        if not d.exists():
            print(f"⚠️  {lang}: dir not found")
            continue
        files = sorted(d.glob("*.html"))
        changed = 0
        for fp in files:
            ok, _ = patch_file(fp, args.apply)
            if ok:
                changed += 1
        print(f"📁 {lang}: {changed} / {len(files)} files patched")
        total += changed

    mode = "APPLIED" if args.apply else "DRY-RUN (use --apply)"
    print(f"\n📊 Total [{mode}]: {total} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
