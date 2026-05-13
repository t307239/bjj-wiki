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


def process_file(fp: Path, lang: str, upload_date: str, also_iframe: bool = True) -> tuple[bool, str, int]:
    """Returns (vo_added, reason, iframes_fixed)"""
    html = fp.read_text(encoding="utf-8")
    if NOINDEX_RE.search(html[:600]):
        return (False, "noindex", 0)
    yt_match = YT_EMBED_RE.search(html)
    if not yt_match:
        return (False, "no_yt_embed", 0)
    new_html = html
    vo_added = False
    if not VIDEO_OBJECT_RE.search(html):
        vid = yt_match.group(1)
        h1_match = H1_RE.search(html)
        h1 = extract_text(h1_match.group(1)) if h1_match else fp.stem.replace("-", " ").title()
        desc_match = META_DESC_RE.search(html)
        desc = desc_match.group(1) if desc_match else ""
        vobj = build_video_object(vid, h1, desc, lang, upload_date)
        injected = inject(new_html, vobj)
        if injected is not None:
            new_html = injected
            vo_added = True
    iframes_fixed = 0
    if also_iframe:
        new_html, iframes_fixed = add_iframe_dims(new_html)
    if vo_added or iframes_fixed > 0:
        fp.write_text(new_html, encoding="utf-8")
    if vo_added:
        return (True, "fixed", iframes_fixed)
    if iframes_fixed > 0:
        return (False, "iframe_only", iframes_fixed)
    return (False, "already_has_video_object", 0)


def main() -> int:
    apply = "--apply" in sys.argv
    skip_iframe = "--no-iframe" in sys.argv
    # JST upload date
    jst = timezone(timedelta(hours=9))
    upload_date = datetime.now(jst).strftime("%Y-%m-%dT00:00:00+09:00")
    stats = {"vo_added": 0, "iframe_only_pages": 0, "iframes_fixed_total": 0, "no_yt": 0, "noindex": 0, "skipped": 0}
    by_lang = {}
    for lang in LANGS:
        by_lang.setdefault(lang, 0)
        for fp in sorted((REPO_ROOT / lang).glob("*.html")):
            if not apply:
                html = fp.read_text(encoding="utf-8")
                if NOINDEX_RE.search(html[:600]): continue
                if not YT_EMBED_RE.search(html): continue
                if VIDEO_OBJECT_RE.search(html):
                    # Still might need iframe dim fix
                    _, fixed = add_iframe_dims(html) if not skip_iframe else (html, 0)
                    if fixed > 0:
                        stats["iframes_fixed_total"] += fixed
                        stats["iframe_only_pages"] += 1
                    continue
                by_lang[lang] += 1
                stats["vo_added"] += 1
                continue
            vo_added, reason, iframes_fixed = process_file(fp, lang, upload_date, also_iframe=not skip_iframe)
            if vo_added:
                stats["vo_added"] += 1
                by_lang[lang] += 1
            elif reason == "iframe_only":
                stats["iframe_only_pages"] += 1
            elif reason == "no_yt_embed":
                stats["no_yt"] += 1
            elif reason == "noindex":
                stats["noindex"] += 1
            else:
                stats["skipped"] += 1
            stats["iframes_fixed_total"] += iframes_fixed
    mode = "APPLY" if apply else "DRY-RUN"
    print(f"=== inject_videoobject_schema.py [{mode}] ===")
    print(f"stats: {stats}")
    print(f"by lang (vo_added): {by_lang}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
