#!/usr/bin/env python3
"""
z260q: apple-touch-icon parity 補完

468 wiki page (en 153 / ja 152 / pt 163) で <link rel="apple-touch-icon"> が欠落。
他 page (ankle-lock 等) は標準で持っているため、iOS Safari "Add to Home Screen"
時の icon 一貫性が崩れる (favicon.svg → grey square fallback)。

修正方針:
  <link rel="icon"...favicon.svg...> 直後に
    <link rel="apple-touch-icon" sizes="180x180" href="https://wiki.bjj-app.net/apple-touch-icon.png">
  を idempotent に挿入。既に持つ page は skip。

対象: en/, ja/, pt/ 配下の全 .html、noindex page も含む (web-clip は noindex 関係なし)。
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

# anchor: existing icon link with favicon.svg
ICON_ANCHOR_RE = re.compile(
    r'(<link rel="icon"[^>]+favicon\.svg[^>]*>)',
    re.IGNORECASE,
)
APPLE_LINE = '<link rel="apple-touch-icon" sizes="180x180" href="https://wiki.bjj-app.net/apple-touch-icon.png">'


def process_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    if "apple-touch-icon" in html:
        return False
    m = ICON_ANCHOR_RE.search(html)
    if not m:
        return False
    insert_at = m.end()
    new_html = html[:insert_at] + "\n" + APPLE_LINE + html[insert_at:]
    path.write_text(new_html, encoding="utf-8")
    return True


def main() -> int:
    total = 0
    per_lang: dict[str, int] = {}
    for lang in LANGS:
        n = 0
        for fp in sorted((REPO_ROOT / lang).glob("*.html")):
            if process_file(fp):
                n += 1
        per_lang[lang] = n
        total += n

    print(f"✅ {total} pages patched")
    for lang, n in per_lang.items():
        print(f"  {lang}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
