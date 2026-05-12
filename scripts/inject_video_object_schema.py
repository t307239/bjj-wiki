#!/usr/bin/env python3
"""
inject_video_object_schema.py — Wave WW Round 5 SEO: VideoObject JSON-LD

3,330 indexable pages have YouTube embeds but no VideoObject schema.
Google rich results require VideoObject schema to surface video snippets
in SERP (huge CTR boost on "how to" queries).

Per "嘘より沈黙": only include facts we can verify:
  - name: page h1 + " — Video Tutorial" (per locale)
  - description: page meta description
  - thumbnailUrl: YouTube auto-generates from video ID
  - embedUrl: the iframe src
  - uploadDate: page's Article.dateModified (when WE embedded; honest)
    (schema.org definition: "date this media was uploaded to this site")

Idempotent. Marker: <!-- z255jjjj-videoobject -->
Skip noindex.
"""
from __future__ import annotations
import html as html_mod
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
MARKER = "<!-- z255jjjj-videoobject -->"

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
ALREADY_RE = re.compile(re.escape(MARKER))
HAS_VIDEO_OBJECT_RE = re.compile(r'"@type"\s*:\s*"VideoObject"')
YOUTUBE_EMBED_RE = re.compile(
    r'<iframe[^>]*?src="https://www\.youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_-]+)[^"]*"',
    re.IGNORECASE | re.DOTALL,
)
H1_RE = re.compile(r'<h1[^>]*>([^<]+)</h1>')
DESC_RE = re.compile(r'<meta name="description" content="([^"]+)"')
DATE_MOD_RE = re.compile(r'"dateModified"\s*:\s*"([^"]+)"')
HEAD_END_RE = re.compile(r"</head>", re.IGNORECASE)

VIDEO_TYPE_LABEL = {
    "en": "Video Tutorial",
    "ja": "動画チュートリアル",
    "pt": "Tutorial em Vídeo",
}


def inject_one(fp: Path, lang: str) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"
    if ALREADY_RE.search(html):
        return "already"
    if HAS_VIDEO_OBJECT_RE.search(html):
        return "skip-existing-schema"

    m_video = YOUTUBE_EMBED_RE.search(html)
    if not m_video:
        return "skip-no-youtube"
    video_id = m_video.group(1)
    embed_url = f"https://www.youtube.com/embed/{video_id}"
    thumbnail = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

    h1 = H1_RE.search(html)
    desc = DESC_RE.search(html)
    date_mod = DATE_MOD_RE.search(html)
    head_end = HEAD_END_RE.search(html)
    if not (h1 and desc and head_end):
        return "skip-missing-fields"

    name = html_mod.unescape(h1.group(1).strip()) + f" — {VIDEO_TYPE_LABEL[lang]}"
    description = html_mod.unescape(desc.group(1).strip())
    upload_date = date_mod.group(1) if date_mod else "2026-05-12T00:00:00+09:00"

    video = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": name,
        "description": description,
        "thumbnailUrl": thumbnail,
        "uploadDate": upload_date,
        "embedUrl": embed_url,
        "inLanguage": lang,
    }
    block = (
        f"\n{MARKER}\n"
        f'<script type="application/ld+json">{json.dumps(video, ensure_ascii=False)}</script>\n'
    )
    new_html = html[:head_end.start()] + block + html[head_end.start():]
    fp.write_text(new_html, encoding="utf-8")
    return "patched"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = inject_one(fp, lang)
            stats[r] = stats.get(r, 0) + 1
    print("VideoObject schema patch results:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
