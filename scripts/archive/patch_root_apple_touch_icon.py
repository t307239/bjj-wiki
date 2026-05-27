#!/usr/bin/env python3
"""
z260q-b: root page (athletes.html / about.html / privacy.html) にも
apple-touch-icon を補完。news.html / index.html は既に持っている。
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGETS = ["athletes.html", "about.html", "privacy.html"]
APPLE_LINE = '<link rel="apple-touch-icon" sizes="180x180" href="https://wiki.bjj-app.net/apple-touch-icon.png">'

# anchor patterns (try in order)
ANCHOR_PATTERNS = [
    re.compile(r'(<link rel="icon"[^>]+favicon\.svg[^>]*>)', re.IGNORECASE),
    re.compile(r'(<meta charset="UTF-8">)', re.IGNORECASE),
]


def process_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    if "apple-touch-icon" in html:
        return False
    for ap in ANCHOR_PATTERNS:
        m = ap.search(html)
        if m:
            new_html = html[:m.end()] + "\n" + APPLE_LINE + html[m.end():]
            path.write_text(new_html, encoding="utf-8")
            return True
    return False


def main() -> int:
    n = 0
    for fname in TARGETS:
        fp = REPO_ROOT / fname
        if fp.exists() and process_file(fp):
            n += 1
            print(f"  patched {fname}")
    print(f"✅ {n} root pages patched")
    return 0


if __name__ == "__main__":
    main()
