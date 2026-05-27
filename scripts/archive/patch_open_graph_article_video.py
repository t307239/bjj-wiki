#!/usr/bin/env python3
"""
patch_open_graph_article_video.py — Wave WW Round 10:
3 Open Graph completeness fixes for richer social sharing + E-A-T.

Audit found:
  - 3,330 pages with YouTube embed but no og:video → Facebook video share
    can't auto-play. Adding og:video + og:video:type lets Facebook display
    the video player inline.
  - 4,452 pages (100% indexable) missing article:author → E-A-T signal gap
  - 4,452 pages missing article:published_time → article freshness signal

Per CLAUDE.md rule -3 (嘘より沈黙): use only verified info.
  - article:author = "BJJ App Inc." (organization, true)
  - article:published_time = page's datePublished from existing Article schema
    (already in JSON-LD, just promote to meta)
  - og:video = the existing YouTube iframe URL

Idempotent. Skip noindex.
Per CLAUDE.md rule -4: template was updated first; this patch covers existing.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
HAS_OG_VIDEO_RE = re.compile(r'<meta property=["\']og:video["\']', re.IGNORECASE)
HAS_AR_AUTHOR_RE = re.compile(r'<meta property=["\']article:author["\']', re.IGNORECASE)
HAS_AR_PUBTIME_RE = re.compile(r'<meta property=["\']article:published_time["\']', re.IGNORECASE)

YT_EMBED_RE = re.compile(
    r'<iframe[^>]*?src="(https://www\.youtube(?:-nocookie)?\.com/embed/[^"]+)"',
    re.IGNORECASE | re.DOTALL,
)
# Fallback: find any first youtube.com/embed/<ID> reference (for JS-injected players)
YT_FALLBACK_RE = re.compile(
    r'youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_-]{11})',
    re.IGNORECASE,
)
DATE_PUBLISHED_RE = re.compile(r'"datePublished"\s*:\s*"([^"]+)"')
OG_TYPE_ARTICLE_RE = re.compile(r'<meta property="og:type" content="article"\s*/?>', re.IGNORECASE)
OG_HEIGHT_RE = re.compile(r'(<meta property=["\']og:image:height["\'][^>]*>)\s*\n?', re.IGNORECASE)
OG_TYPE_RE = re.compile(r'(<meta property=["\']og:type["\'][^>]*>)\s*\n?', re.IGNORECASE)


def patch_one(fp: Path, lang: str) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"

    changes = 0
    metas_to_add: list[str] = []

    # 1. og:video + og:video:type for YouTube embed (try iframe first, then fallback)
    if not HAS_OG_VIDEO_RE.search(html):
        embed_url: str | None = None
        yt = YT_EMBED_RE.search(html)
        if yt:
            embed_url = yt.group(1).split("?")[0]
        else:
            # Fallback: any youtube.com/embed/<ID> reference (e.g., JS-injected)
            yt_fb = YT_FALLBACK_RE.search(html)
            if yt_fb:
                embed_url = f"https://www.youtube.com/embed/{yt_fb.group(1)}"
        if embed_url:
            metas_to_add.append(f'<meta property="og:video" content="{embed_url}">')
            metas_to_add.append('<meta property="og:video:type" content="text/html">')
            metas_to_add.append('<meta property="og:video:width" content="560">')
            metas_to_add.append('<meta property="og:video:height" content="315">')

    # 2 + 3. article:author + article:published_time (only on og:type=article pages)
    is_article = bool(OG_TYPE_ARTICLE_RE.search(html))
    if is_article:
        if not HAS_AR_AUTHOR_RE.search(html):
            metas_to_add.append('<meta property="article:author" content="BJJ App Inc.">')

        if not HAS_AR_PUBTIME_RE.search(html):
            m_dp = DATE_PUBLISHED_RE.search(html)
            if m_dp:
                metas_to_add.append(
                    f'<meta property="article:published_time" content="{m_dp.group(1)}">'
                )

    if not metas_to_add:
        return "already"

    # Insert after og:image:height (richer Open Graph block) or fallback after og:type
    block = "\n".join(metas_to_add) + "\n"
    m = OG_HEIGHT_RE.search(html)
    if m:
        new_html = html[:m.end()] + block + html[m.end():]
    else:
        m = OG_TYPE_RE.search(html)
        if m:
            new_html = html[:m.end()] + block + html[m.end():]
        else:
            return "skip-no-anchor"

    fp.write_text(new_html, encoding="utf-8")
    return f"patched-{len(metas_to_add)}"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = patch_one(fp, lang)
            stats[r] = stats.get(r, 0) + 1
    print("OG video + article:author + published_time patch:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
