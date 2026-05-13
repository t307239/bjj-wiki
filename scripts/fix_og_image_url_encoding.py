#!/usr/bin/env python3
"""
fix_og_image_url_encoding.py — z260j

og:image / twitter:image の URL 内 `title=<...>` パラメータに literal space が
入っている page を URL-encode で修正。167 page 初回処理 (z260j Round 4 audit
で発見)。idempotent: literal space を持たない page は touch しない。

Twitter / Facebook crawler は URL の literal space を受理せず image fetch を
諦める = SNS share preview 死亡の silent bug を防止。

実行方法:
    cd ~/Claude/bjj-wiki
    python3 scripts/fix_og_image_url_encoding.py            # dry-run
    python3 scripts/fix_og_image_url_encoding.py --apply    # 実行
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("en", "ja", "pt")

# /api/og?... title=<value>(&suffix|" terminator)
IMG_URL_RE = re.compile(
    r'(content=["\'])(https://bjj-app\.net/api/og\?[^"\']*?title=)([^"\'&]+)((?:&[^"\']*)?["\'])',
    re.IGNORECASE,
)


def fix_html(text: str) -> tuple[str, int]:
    fixes = 0

    def replace(m: re.Match[str]) -> str:
        nonlocal fixes
        prefix, url_start, title_val, suffix = (
            m.group(1),
            m.group(2),
            m.group(3),
            m.group(4),
        )
        if " " not in title_val:
            return m.group(0)
        fixes += 1
        encoded = quote(title_val, safe="")
        return f"{prefix}{url_start}{encoded}{suffix}"

    out = IMG_URL_RE.sub(replace, text)
    return out, fixes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually write changes")
    args = ap.parse_args()
    total_files = 0
    fixed_files = 0
    total_fixes = 0
    for locale in LANGS:
        for p in sorted((ROOT / locale).glob("*.html")):
            total_files += 1
            text = p.read_text(encoding="utf-8")
            new_text, n = fix_html(text)
            if n > 0 and new_text != text:
                if args.apply:
                    p.write_text(new_text, encoding="utf-8")
                fixed_files += 1
                total_fixes += n
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] Scanned: {total_files} files")
    print(f"[{mode}] Fixed:   {fixed_files} files")
    print(f"[{mode}] Total replacements: {total_fixes}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
