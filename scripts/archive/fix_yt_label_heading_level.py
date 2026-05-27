#!/usr/bin/env python3
"""z261o: promote <h3 class="yt-label"> → <h2 class="yt-label"> for a11y heading order.

Root cause: scripts/patch_video_from_supabase.py and scripts/patch_youtube.py emitted <h3>
for the YouTube embed label, creating h1 → h3 skip on pages without a preceding <h2>.

Both source scripts already updated to emit <h2>. This script back-patches existing HTML.

Idempotent (no-op on already-fixed pages).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ("en", "ja", "pt")

# Match <h3 class="yt-label">...</h3>
YT_LABEL_RE = re.compile(
    r'<h3(\s+[^>]*?class="yt-label"[^>]*)>([^<]+)</h3>',
    re.IGNORECASE,
)


def fix_file(fp: Path) -> int:
    html = fp.read_text(encoding="utf-8")
    new_html, n = YT_LABEL_RE.subn(r'<h2\1>\2</h2>', html)
    if n > 0:
        fp.write_text(new_html, encoding="utf-8")
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    total_files = 0
    total_promotions = 0
    for loc in LOCALES:
        ld = ROOT / loc
        if not ld.exists():
            continue
        for fp in sorted(ld.glob("*.html")):
            if fp.name.startswith("_"):
                continue
            html = fp.read_text(encoding="utf-8")
            if not YT_LABEL_RE.search(html):
                continue
            if args.apply:
                n = fix_file(fp)
                if n > 0:
                    total_files += 1
                    total_promotions += n
            else:
                total_files += 1
                total_promotions += len(YT_LABEL_RE.findall(html))

    mode = "applied" if args.apply else "dry-run"
    print(f"[{mode}] files={total_files} promotions={total_promotions}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
