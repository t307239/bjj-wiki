#!/usr/bin/env python3
"""
inject_person_schema.py — Wave WW SEO 2: Person JSON-LD for athlete pages

Athlete pages lack `Person` schema, which Google uses for Knowledge Panel
+ rich SERP cards. We have 75 athlete pages (25 per locale × 3 locales).

Per "嘘より沈黙" rule: only include verified facts. Don't guess nationality,
achievements, etc. Use only:
  - name (from <h1>)
  - description (from <meta description>)
  - url (canonical)
  - jobTitle (locale-aware "Brazilian Jiu-Jitsu Athlete")
  - knowsAbout: ["Brazilian Jiu-Jitsu", "Grappling"]
  - sameAs: only if we know them (skip for now — don't guess social URLs)

Idempotent: marker `<!-- z255jjjj-person-schema -->` skips re-runs.
"""
from __future__ import annotations
import html as html_mod
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
MARKER = "<!-- z255jjjj-person-schema -->"

H1_RE = re.compile(r"<h1[^>]*>([^<]+)</h1>")
DESC_RE = re.compile(r'<meta name="description" content="([^"]+)"')
CANONICAL_RE = re.compile(r'<link rel="canonical" href="([^"]+)"')
HEAD_END_RE = re.compile(r"</head>", re.IGNORECASE)
ALREADY_RE = re.compile(re.escape(MARKER))

JOB_TITLE = {
    "en": "Brazilian Jiu-Jitsu Athlete",
    "ja": "ブラジリアン柔術選手",
    "pt": "Atleta de Jiu-Jitsu Brasileiro",
}
KNOWS_ABOUT = {
    "en": ["Brazilian Jiu-Jitsu", "Grappling", "Submission Grappling"],
    "ja": ["ブラジリアン柔術", "グラップリング", "サブミッショングラップリング"],
    "pt": ["Jiu-Jitsu Brasileiro", "Grappling", "Submission Grappling"],
}


def patch_one(fp: Path, lang: str) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if ALREADY_RE.search(html):
        return "already"

    h1 = H1_RE.search(html)
    desc = DESC_RE.search(html)
    canonical = CANONICAL_RE.search(html)
    head_end = HEAD_END_RE.search(html)

    if not (h1 and desc and canonical and head_end):
        return "skip-missing-fields"

    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": html_mod.unescape(h1.group(1).strip()),
        "description": html_mod.unescape(desc.group(1).strip()),
        "url": canonical.group(1).strip(),
        "jobTitle": JOB_TITLE[lang],
        "knowsAbout": KNOWS_ABOUT[lang],
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": canonical.group(1).strip(),
        },
    }
    block = (
        f"\n{MARKER}\n"
        f'<script type="application/ld+json">{json.dumps(person, ensure_ascii=False)}</script>\n'
    )
    new_html = html[:head_end.start()] + block + html[head_end.start():]
    fp.write_text(new_html, encoding="utf-8")
    return "patched"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("athlete-*.html"):
            r = patch_one(fp, lang)
            stats[r] = stats.get(r, 0) + 1
    print("Person schema patch results:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
