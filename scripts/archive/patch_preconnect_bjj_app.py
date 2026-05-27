#!/usr/bin/env python3
"""
patch_preconnect_bjj_app.py — Wave WW (D): inject preconnect for bjj-app.net

og:image / share-card / CTA target は全て bjj-app.net。preconnect すると
TTFB を ~30-100ms 削減 (HTTPS handshake を初期 navigate と並列化)。

Idempotent: 既に preconnect 済 page は skip。
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

NEW_LINK = '<link rel="preconnect" href="https://bjj-app.net">\n'
# Primary anchor: cdnjs preconnect (new template)
ANCHOR_RE = re.compile(
    r'(<link rel="preconnect" href="https://cdnjs\.cloudflare\.com"[^>]*>)\s*\n',
    re.IGNORECASE,
)
# Fallback anchor: wiki-v2.css link (universal across all pages)
FALLBACK_ANCHOR_RE = re.compile(
    r'(<link rel="stylesheet" href="/wiki-v2\.css"[^>]*>)\s*\n?',
    re.IGNORECASE,
)
ALREADY_RE = re.compile(r'<link rel="preconnect" href="https://bjj-app\.net"', re.IGNORECASE)


def patch_one(fp: Path) -> str:
    """Returns 'patched' / 'already' / 'skip-no-anchor' / 'skip-noindex'."""
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read-error"

    if ALREADY_RE.search(html):
        return "already"
    if 'name="robots" content="noindex' in html and "<head>" in html[:200]:
        # Redirect / noindex page — preconnect waste
        return "skip-noindex"
    m = ANCHOR_RE.search(html)
    if m:
        # Insert AFTER the cdnjs preconnect line
        new_html = html[:m.end()] + NEW_LINK + html[m.end():]
        fp.write_text(new_html, encoding="utf-8")
        return "patched"
    # Fallback: insert BEFORE the wiki-v2.css link
    m2 = FALLBACK_ANCHOR_RE.search(html)
    if not m2:
        return "skip-no-anchor"
    insert_at = m2.start()
    # Ensure newline boundary
    if insert_at > 0 and html[insert_at - 1] != "\n":
        text = "\n" + NEW_LINK
    else:
        text = NEW_LINK
    new_html = html[:insert_at] + text + html[insert_at:]
    fp.write_text(new_html, encoding="utf-8")
    return "patched-fallback"


def main() -> int:
    stats = {"patched": 0, "already": 0, "skip-no-anchor": 0,
             "skip-noindex": 0, "skip-read-error": 0}
    for lang in LANGS:
        lang_dir = REPO_ROOT / lang
        if not lang_dir.is_dir():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            r = patch_one(fp)
            stats[r] = stats.get(r, 0) + 1
    print("Preconnect patch results:")
    for k, v in stats.items():
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
