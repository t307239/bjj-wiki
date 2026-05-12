#!/usr/bin/env python3
"""
inject_itemlist_schema_hub.py — Wave WW Round 16: ItemList schema for hubs

15 hub pages (index / techniques-az / athletes / news / categories) lack
ItemList JSON-LD schema. Google rich results show "list" UI (carousel,
numbered items) when ItemList schema is present, boosting CTR.

Build ItemList from internal links inside each page's <main>:
  - Iterate through <a href="*.html"> in <main>
  - Top 25 unique items become ItemList entries (Google's recommended cap)

Idempotent. Marker: <!-- z255jjjj-itemlist -->
"""
from __future__ import annotations
import html as html_mod
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
MARKER = "<!-- z255jjjj-itemlist -->"
BASE = "https://wiki.bjj-app.net"

HUB_NAMES = [
    "index.html",
    "athletes.html", "athletes-az.html",
    "techniques-az.html",
    "concepts-az.html", "drills-az.html",
    "best-bjj-guards.html", "best-bjj-passes.html",
    "leg-locks.html", "guard-passing.html",
    "news.html",
]

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
ALREADY_RE = re.compile(re.escape(MARKER))
HEAD_END_RE = re.compile(r"</head>", re.IGNORECASE)
MAIN_RE = re.compile(r"<main[^>]*>(.*?)</main>", re.DOTALL | re.IGNORECASE)
# Tolerant LINK_RE: support nested HTML inside <a> (e.g. <a><div>Label</div></a>).
# Captures slug + first text-or-tag-content up to closing </a>.
LINK_RE = re.compile(
    r'<a[^>]+href="(?:\.\./)?(?:[a-z]{2}/)?([a-z0-9\-]+)\.html"[^>]*>(.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


def inject_one(fp: Path, lang: str) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"
    if ALREADY_RE.search(html):
        return "already"
    head_end = HEAD_END_RE.search(html)
    if not head_end:
        return "skip-no-head"
    main = MAIN_RE.search(html)
    if not main:
        return "skip-no-main"

    # Extract h1 for ItemList name
    h1 = H1_RE.search(html)
    h1_text = TAG_RE.sub("", h1.group(1)).strip() if h1 else fp.stem
    h1_text = html_mod.unescape(h1_text)

    # Collect unique internal-link items, top 25
    seen = set()
    items = []
    for m in LINK_RE.finditer(main.group(1)):
        slug = m.group(1)
        if slug in seen:
            continue
        seen.add(slug)
        # Extract clean label:
        # If <a> contains nested <div>s (card layout), take FIRST <div>'s text.
        # Otherwise strip all tags + collapse whitespace.
        inner = m.group(2)
        first_div = re.search(r"<div[^>]*>([^<]+)</div>", inner)
        if first_div:
            label = re.sub(r"\s+", " ", first_div.group(1)).strip()
        else:
            label = re.sub(r"\s+", " ", TAG_RE.sub(" ", inner)).strip()
        if len(label) < 2:
            continue
        if "←" in label or label.startswith("Back"):  # skip nav-back links
            continue
        items.append({
            "@type": "ListItem",
            "position": len(items) + 1,
            "name": label,
            "url": f"{BASE}/{lang}/{slug}.html",
        })
        if len(items) >= 25:
            break
    if len(items) < 5:
        return "skip-too-few-items"

    schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": h1_text,
        "url": f"{BASE}/{lang}/{fp.name}",
        "numberOfItems": len(items),
        "itemListElement": items,
    }
    block = (
        f"\n{MARKER}\n"
        f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>\n'
    )
    new_html = html[:head_end.start()] + block + html[head_end.start():]
    fp.write_text(new_html, encoding="utf-8")
    return f"patched-{len(items)}-items"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for hname in HUB_NAMES:
            fp = REPO_ROOT / lang / hname
            if not fp.exists():
                continue
            r = inject_one(fp, lang)
            stats[r] = stats.get(r, 0) + 1
        # Also catch *-az.html hubs not in HUB_NAMES list
        for fp in (REPO_ROOT / lang).glob("*-az.html"):
            if fp.name not in HUB_NAMES:
                r = inject_one(fp, lang)
                stats[r] = stats.get(r, 0) + 1
    print("ItemList schema injection results:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
