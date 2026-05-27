#!/usr/bin/env python3
"""
fix_athletes_internal_links.py — Wave WW Round 17: athletes.html link gap

athletes.html lists 6 elite athletes by name in <h2> headings but doesn't
link to their dedicated athlete-*.html pages. This kills:
  - User can't click to read more about athlete
  - Google can't crawl from hub to detail
  - Internal link graph weakens (athletes pages become less authoritative)

Fix: wrap each `<h2>NAME</h2>` with `<a href="athlete-<slug>.html">`.

Idempotent: skip if already linked.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]


# JA/PT name → athlete slug mapping (since transliteration can't be regex-derived)
NAME_TO_SLUG_OVERRIDE = {
    "ゴードン・ライアン": "athlete-gordon-ryan",
    "ミッキー・ムスメシ": "athlete-mikey-musumeci",
    "クレイグ・ジョーンズ": "athlete-craig-jones",
    "ベルナルド・ファリア": "athlete-bernardo-faria",
    "ジョン・ダナハー": "athlete-john-danaher",
    "ラクラン・ジャイルズ": "athlete-lachlan-giles",
    # PT mostly matches EN romanization, fall through to default
}


def name_to_slug(name: str) -> str:
    """Gordon Ryan → athlete-gordon-ryan; ゴードン・ライアン → athlete-gordon-ryan."""
    name = name.strip()
    # Override for non-Latin names
    if name in NAME_TO_SLUG_OVERRIDE:
        return NAME_TO_SLUG_OVERRIDE[name]
    s = name.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return f"athlete-{s}"


def patch_one(fp: Path) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"

    # Find each <h2 ...>NAME</h2> in athletes.html where the parent <a> doesn't exist
    # Anchor: only patch h2s that are NOT already inside <a>
    # Pattern: capture <h2 attrs>name</h2>
    H2_RE = re.compile(r'(<h2(?:\s[^>]*)?>)([^<]+)(</h2>)')

    changes = 0
    new_html = html

    def maybe_link(m: re.Match) -> str:
        nonlocal changes
        h2_open = m.group(1)
        name = m.group(2).strip()
        h2_close = m.group(3)

        # Idempotency: check 200 chars before for `<a href="athlete-`
        # (covers wrap + style attributes + nested elements)
        start = m.start()
        before = new_html[max(0, start - 200):start]
        if 'href="athlete-' in before and before.rstrip().endswith('>'):
            return m.group(0)  # already wrapped

        slug = name_to_slug(name)
        # Verify the destination exists
        if not (REPO_ROOT / fp.parent.name / f"{slug}.html").exists():
            return m.group(0)

        changes += 1
        # Wrap the h2 in <a>
        return f'<a href="{slug}.html" style="text-decoration:none;color:inherit">{h2_open}{name}{h2_close}</a>'

    new_html = H2_RE.sub(maybe_link, new_html)
    if changes == 0:
        return "skip-no-changes"
    fp.write_text(new_html, encoding="utf-8")
    return f"patched-{changes}"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        fp = REPO_ROOT / lang / "athletes.html"
        if not fp.exists():
            continue
        r = patch_one(fp)
        stats[r] = stats.get(r, 0) + 1
        print(f"{lang}/athletes.html: {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
