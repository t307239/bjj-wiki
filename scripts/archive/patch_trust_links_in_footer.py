#!/usr/bin/env python3
"""
patch_trust_links_in_footer.py — Wave WW Round 11: trust signal completion

411 pages have a <footer> but no privacy/about/terms link inside.
Trust links in footer are a basic UX + Google trust signal.

Insert into footer (locale-aware text), per existing /privacy.html etc.
Idempotent. Skip noindex.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
HAS_TRUST_RE = re.compile(r'<a[^>]+href="[^"]*(?:privacy|about|terms)', re.IGNORECASE)
FOOTER_END_RE = re.compile(r'</footer>', re.IGNORECASE)
FOOTER_OPEN_RE = re.compile(r'<footer[^>]*>', re.IGNORECASE)

LINKS = {
    "en": (
        '<p style="margin-top:12px;font-size:.85rem">'
        '<a href="../privacy.html" style="color:var(--muted);margin:0 8px">Privacy Policy</a> · '
        '<a href="../about.html" style="color:var(--muted);margin:0 8px">About</a>'
        '</p>'
    ),
    "ja": (
        '<p style="margin-top:12px;font-size:.85rem">'
        '<a href="../privacy.html" style="color:var(--muted);margin:0 8px">プライバシーポリシー</a> · '
        '<a href="../about.html" style="color:var(--muted);margin:0 8px">サイトについて</a>'
        '</p>'
    ),
    "pt": (
        '<p style="margin-top:12px;font-size:.85rem">'
        '<a href="../privacy.html" style="color:var(--muted);margin:0 8px">Política de Privacidade</a> · '
        '<a href="../about.html" style="color:var(--muted);margin:0 8px">Sobre</a>'
        '</p>'
    ),
}


def patch_one(fp: Path, lang: str) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"
    if HAS_TRUST_RE.search(html):
        return "already"
    m_end = FOOTER_END_RE.search(html)
    if not m_end:
        return "skip-no-footer"
    block = LINKS[lang]
    new_html = html[:m_end.start()] + block + html[m_end.start():]
    fp.write_text(new_html, encoding="utf-8")
    return "patched"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = patch_one(fp, lang)
            stats[r] = stats.get(r, 0) + 1
    print("Trust links patch results:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
