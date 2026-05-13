#!/usr/bin/env python3
"""
inject_videoobject_schema.py — z260o: 119 page で YT embed あるのに VideoObject schema 不在を fix

z255jjjj-WW Round5 で check_videoobject_when_yt_embed.py lint が追加されたが、
バッチ injection が一部 page (60 EN + 57 JA + 2 PT = 119 page) で漏れていた。

各 page の YT embed video id を抽出し、imanari-roll パターンの VideoObject schema を
`</head>` 直前に注入。
- name = "<H1 text> — Video Tutorial"  (locale 別 suffix)
- description = meta description (200 chars max)
- thumbnailUrl = https://i.ytimg.com/vi/<vid>/hqdefault.jpg
- uploadDate = 当日 ISO
- embedUrl = https://www.youtube.com/embed/<vid>
- inLanguage = lang

Idempotent: marker `<!-- z260o-videoobject -->` で再実行 skip。
"""
from __future__ import annotations
import re
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
YT_EMBED_RE = re.compile(
    r'src=["\']https?://(?:www\.)?youtube(?:-nocookie)?\.com/embed/([\w-]+)',
    re.IGNORECASE,
)
VIDEO_OBJECT_RE = re.compile(r'"@type"\s*:\s*"VideoObject"')
MARKER = "<!-- z260o-videoobject -->"
HEAD_END_RE = re.compile(r'</head>', re.IGNORECASE)
# z260o: YT iframe を width="560" height="315" 付きに改修 (CLS 防止 lint pwa-iframe-twitter)
YT_IFRAME_RE = re.compile(
    r'(<iframe\b)([^>]*?src=["\']https?://(?:www\.)?youtube(?:-nocookie)?\.com/embed/[^>]*?)(>)',
    re.IGNORECASE | re.DOTALL,
)
H1_RE = re.compile(r'<h1[^>]*>(.*?)</h1>', re.IGNORECASE | re.DOTALL)
META_DESC_RE = re.compile(
    r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
HTML_LANG_RE = re.compile(r'<html\s+lang=["\']([^"\']+)["\']', re.IGNORECASE)

SUFFIX_BY_LANG = {
    "en": " — Video Tutorial",
    "ja": " — ビデオチュートリアル",
    "pt": " — Tutorial em Vídeo",
}


def extract_text(html_fragment: str) -> str:
    """Strip tags from h1 content"""
    return re.sub(r'<[^>]+>', '', html_fragment).strip()


def build_video_object(vid: str, h1: str, desc: str, lang: str, upload_date: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": f"{h1}{SUFFIX_BY_LANG.get(lang, ' — Video Tutorial')}",
        "description": desc[:200] if desc else f"{h1} — BJJ technique guide",
        "thumbnailUrl": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
        "uploadDate": upload_date,
        "embedUrl": f"https://www.youtube.com/embed/{vid}",
        "inLanguage": lang,
    }


def inject(html: str, vobj: dict) -> str | None:
    """Inject VideoObject schema before </head>. Returns new html or None if no </head>."""
    if MARKER in html:
        return None  # already done
    json_str = json.dumps(vobj, ensure_ascii=False, separators=(", ", ": "))
    block = f'\n{MARKER}\n<script type="application/ld+json">{json_str}</script>\n'
    new_html, n = HEAD_END_RE.subn(block + '</head>', html, count=1)
    if n == 0:
        return None
    return new_html


def add_iframe_dims(html: str) -> tuple[str, int]:
    """Add width="560" height="315" to YT iframes lacking them. Idempotent."""
    fixed = 0
    def replace(m):
        nonlocal fixed
        full = m.group(0)
        attrs_part = m.group(2)
        if 'width=' in attrs_part.lower() and 'height=' in attrs_part.lower():
            return full
        # Insert dims after opening <iframe
        new_attrs = attrs_part
        if 'width=' not in new_attrs.lower():
            new_attrs = ' width="560"' + new_attrs
        if 'height=' not in new_attrs.lower():
            new_attrs = ' height="315"' + new_attrs
        fixed += 1
        return m.group(1) + new_attrs + m.group(3)
    new_html = YT_IFRAME_RE.sub(replace, html)
    return new_html, fixed


OG_VIDEO_PRESENT_RE = re.compile(r'property=["\']og:video["\']', re.IGNORECASE)
ARTICLE_PUB_PRESENT_RE = re.compile(r'property=["\']article:published_time["\']', re.IGNORECASE)
DATE_PUBLISHED_RE = re.compile(r'"datePublished"\s*:\s*"([^"]+)"', re.IGNORECASE)
OG_TYPE_ARTICLE_RE = re.compile(r'og:type["\'][^>]*content=["\']article["\']', re.IGNORECASE)


def add_og_video(html: str) -> tuple[str, bool]:
    """Add og:video meta for YT embedding pages. Idempotent."""
    if OG_VIDEO_PRESENT_RE.search(html):
        return html, False
    yt_match = YT_EMBED_RE.search(html)
    if not yt_match:
        return html, False
    vid = yt_match.group(1)
    block = (
        f'<meta property="og:video" content="https://www.youtube.com/embed/{vid}">\n'
        f'<meta property="og:video:type" content="text/html">\n'
        f'<meta property="og:video:width" content="560">\n'
        f'<meta property="og:video:height" content="315">\n'
    )
    new_html, n = HEAD_END_RE.subn(block + '</head>', html, count=1)
    return (new_html if n else html), bool(n)


def add_article_published_time(html: str) -> tuple[str, bool]:
    """Mirror JSON-LD datePublished into <meta article:published_time>. Idempotent."""
    if ARTICLE_PUB_PRESENT_RE.search(html):
        return html, False
    if not OG_TYPE_ARTICLE_RE.search(html):
        return html, False
    m = DATE_PUBLISHED_RE.search(html)
    if not m:
        return html, False
    block = f'<meta property="article:published_time" content="{m.group(1)}">\n'
    new_html, n = HEAD_END_RE.subn(block + '</head>', html, count=1)
    return (new_html if n else html), bool(n)


def process_file(fp: Path, lang: str, upload_date: str, also_iframe: bool = True) -> dict:
    """Returns dict of what was changed"""
    result = {"vo_added": False, "iframes_fixed": 0, "og_video_added": False, "article_pub_added": False, "reason": ""}
    html = fp.read_text(encoding="utf-8")
    if NOINDEX_RE.search(html[:600]):
        result["reason"] = "noindex"
        return result
    yt_match = YT_EMBED_RE.search(html)
    if not yt_match and not OG_TYPE_ARTICLE_RE.search(html):
        result["reason"] = "no_yt_no_article"
        return result
    new_html = html
    # 1) Add VideoObject schema
    if yt_match and not VIDEO_OBJECT_RE.search(html):
        vid = yt_match.group(1)
        h1_match = H1_RE.search(html)
        h1 = extract_text(h1_match.group(1)) if h1_match else fp.stem.replace("-", " ").title()
        desc_match = META_DESC_RE.search(html)
        desc = desc_match.group(1) if desc_match else ""
        vobj = build_video_object(vid, h1, desc, lang, upload_date)
        injected = inject(new_html, vobj)
        if injected is not None:
            new_html = injected
            result["vo_added"] = True
    # 2) Fix iframe dims
    if also_iframe and yt_match:
        new_html, ifix = add_iframe_dims(new_html)
        result["iframes_fixed"] = ifix
    # 3) Add og:video meta
    if yt_match:
        new_html, og_added = add_og_video(new_html)
        result["og_video_added"] = og_added
    # 4) Add article:published_time mirror
    new_html, art_added = add_article_published_time(new_html)
    result["article_pub_added"] = art_added
    if any([result["vo_added"], result["iframes_fixed"] > 0, result["og_video_added"], result["article_pub_added"]]):
        fp.write_text(new_html, encoding="utf-8")
    return result


def main() -> int:
    apply = "--apply" in sys.argv
    skip_iframe = "--no-iframe" in sys.argv
    # JST upload date
    jst = timezone(timedelta(hours=9))
    upload_date = datetime.now(jst).strftime("%Y-%m-%dT00:00:00+09:00")
    stats = {"vo_added": 0, "iframes_fixed": 0, "og_video_added": 0, "article_pub_added": 0, "skipped": 0}
    for lang in LANGS:
        for fp in sorted((REPO_ROOT / lang).glob("*.html")):
            if not apply:
                # Just count what would change
                html = fp.read_text(encoding="utf-8")
                if NOINDEX_RE.search(html[:600]): continue
                yt_match = YT_EMBED_RE.search(html)
                has_article = bool(OG_TYPE_ARTICLE_RE.search(html))
                if not yt_match and not has_article: continue
                if yt_match:
                    if not VIDEO_OBJECT_RE.search(html): stats["vo_added"] += 1
                    if not skip_iframe:
                        _, fx = add_iframe_dims(html)
                        stats["iframes_fixed"] += fx
                    if not OG_VIDEO_PRESENT_RE.search(html): stats["og_video_added"] += 1
                if has_article and DATE_PUBLISHED_RE.search(html) and not ARTICLE_PUB_PRESENT_RE.search(html):
                    stats["article_pub_added"] += 1
                continue
            res = process_file(fp, lang, upload_date, also_iframe=not skip_iframe)
            if res["vo_added"]: stats["vo_added"] += 1
            stats["iframes_fixed"] += res["iframes_fixed"]
            if res["og_video_added"]: stats["og_video_added"] += 1
            if res["article_pub_added"]: stats["article_pub_added"] += 1
    mode = "APPLY" if apply else "DRY-RUN"
    print(f"=== inject_videoobject_schema.py [{mode}] ===")
    print(f"stats: {stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
