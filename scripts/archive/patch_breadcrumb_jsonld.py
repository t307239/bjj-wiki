#!/usr/bin/env python3
"""
patch_breadcrumb_jsonld.py — z255tt: 3,859 indexable page に BreadcrumbList 追加

旧: technique article page には BreadcrumbList JSON-LD が無く、Google SERP に
    breadcrumb navigation が表示されない (richer SERP CTR 機会喪失)。
    index.html / 4 root page だけが BreadcrumbList を持つ状況。

修正: 各 indexable page に 3-level BreadcrumbList を追加
    1. BJJ Wiki (https://wiki.bjj-app.net/)
    2. Locale index (e.g. https://wiki.bjj-app.net/ja/index.html)
    3. Current article (h1 から取得)

idempotent:
- 既に BreadcrumbList が存在すれば skip
- noindex page は skip (sitemap 除外と整合)
- h1 が無い page は skip (redirect / consolidated)
"""
from __future__ import annotations
import re
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://wiki.bjj-app.net"

LOCALE_INDEX_NAME = {
    "en": "All BJJ Techniques",
    "ja": "全BJJ技一覧",
    "pt": "Todas as Técnicas de BJJ",
}


def extract_h1(html: str) -> str | None:
    m = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
    if not m:
        return None
    return m.group(1).strip()


def make_breadcrumb_jsonld(lang: str, slug: str, article_name: str) -> str:
    locale_name = LOCALE_INDEX_NAME[lang]
    article_url = f"{SITE_URL}/{lang}/{slug}.html"
    locale_index_url = f"{SITE_URL}/{lang}/index.html"
    obj = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "BJJ Wiki", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": locale_name, "item": locale_index_url},
            {"@type": "ListItem", "position": 3, "name": article_name, "item": article_url},
        ],
    }
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False, separators=(",", ":"))}</script>'


def patch_page(fp: Path) -> str:
    """Returns: 'patched' / 'skip-noindex' / 'skip-already' / 'skip-no-h1' / 'skip-not-indexable'"""
    html = fp.read_text(encoding="utf-8")

    # idempotent guard: already has BreadcrumbList?
    if "BreadcrumbList" in html:
        return "skip-already"

    # noindex skip
    head_part = html[:2000]
    if "noindex" in head_part:
        return "skip-noindex"

    # h1 extraction
    h1 = extract_h1(html)
    if not h1:
        return "skip-no-h1"

    # determine lang/slug from path
    parts = fp.parts
    if len(parts) < 2 or parts[-2] not in LOCALE_INDEX_NAME:
        return "skip-not-indexable"
    lang = parts[-2]
    slug = fp.stem  # filename without .html

    # generate JSON-LD
    breadcrumb = make_breadcrumb_jsonld(lang, slug, h1)

    # inject before </head> (preserves existing JSON-LD blocks)
    new = html.replace("</head>", breadcrumb + "</head>", 1)
    if new == html:
        return "skip-no-head"

    fp.write_text(new, encoding="utf-8")
    return "patched"


def main():
    print("🔧 patch_breadcrumb_jsonld.py — z255tt")
    stats = {
        "patched": 0, "skip-already": 0, "skip-noindex": 0,
        "skip-no-h1": 0, "skip-not-indexable": 0, "skip-no-head": 0,
    }
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            result = patch_page(fp)
            stats[result] = stats.get(result, 0) + 1

    print(f"  ✅ Patched: {stats['patched']}")
    for k, v in sorted(stats.items()):
        if k != "patched" and v > 0:
            print(f"  ⏭  {k}: {v}")


if __name__ == "__main__":
    main()
