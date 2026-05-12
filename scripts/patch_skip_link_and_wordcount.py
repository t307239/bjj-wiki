#!/usr/bin/env python3
"""
patch_skip_link_and_wordcount.py — Wave WW Round 7: a11y + content depth signal

Audit found:
  - 4,452 pages missing skip-to-content link (WCAG 2.4.1 Bypass Blocks)
  - 3,246 pages missing Article.wordCount (Google content depth signal)

Fixes:
  1. Add `id="main"` to existing `<main>` tag
  2. Insert `<a class="skip-link" href="#main">Skip to content</a>` after `<body>`
     (visually hidden until focused via CSS in wiki-v2.css)
  3. Compute word count from text in `<main>` and inject into Article JSON-LD

Idempotent. Skip noindex.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
SKIP_TEXT = {"en": "Skip to content", "ja": "コンテンツへスキップ", "pt": "Pular para o conteúdo"}

# Match <main> without id attribute
MAIN_NO_ID_RE = re.compile(r'<main(?![^>]*\bid=)([^>]*)>', re.IGNORECASE)
# Body opening tag
BODY_OPEN_RE = re.compile(r'(<body[^>]*>)', re.IGNORECASE)
# Skip-link presence check
SKIP_LINK_RE = re.compile(r'class="skip-link"', re.IGNORECASE)
# Main content for word count (text only, between <main> and </main>)
MAIN_CONTENT_RE = re.compile(r'<main[^>]*>(.*?)</main>', re.DOTALL | re.IGNORECASE)
# Article schema
ARTICLE_LD_RE = re.compile(
    r'(<script[^>]+ld\+json[^>]*>)({[^<]*"@type":"Article"[^<]*})(</script>)',
    re.DOTALL,
)
SCRIPT_STRIP_RE = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
STYLE_STRIP_RE = re.compile(r"<style[^>]*>.*?</style>", re.IGNORECASE | re.DOTALL)


def count_words_in_main(html: str) -> int:
    """Return approx word count of <main> text content."""
    m = MAIN_CONTENT_RE.search(html)
    if not m:
        return 0
    inner = SCRIPT_STRIP_RE.sub("", STYLE_STRIP_RE.sub("", m.group(1)))
    text = re.sub(r"<[^>]+>", " ", inner)
    text = re.sub(r"&nbsp;|&[a-z]+;|&#\d+;", " ", text)
    # Use whitespace split for English/Latin scripts.
    # For JA/PT mixed content, this still gives a useful order-of-magnitude estimate.
    words = [w for w in re.split(r"\s+", text) if w.strip()]
    return len(words)


def patch_one(fp: Path, lang: str) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"

    changes = 0

    # Step 1: ensure <main> has id="main"
    new_html, n = MAIN_NO_ID_RE.subn(r'<main id="main"\1>', html, count=1)
    if n:
        changes += 1
        html = new_html

    # Step 2: insert skip-link after <body> if missing
    if not SKIP_LINK_RE.search(html):
        skip_link = f'<a class="skip-link" href="#main">{SKIP_TEXT[lang]}</a>'
        new_html, n = BODY_OPEN_RE.subn(rf'\1\n{skip_link}', html, count=1)
        if n:
            changes += 1
            html = new_html

    # Step 3: inject wordCount into Article JSON-LD if missing
    word_count = count_words_in_main(html)
    if word_count > 0:
        def add_wordcount(m: re.Match) -> str:
            ld_open = m.group(1)
            payload = m.group(2)
            ld_close = m.group(3)
            if '"wordCount"' in payload:
                return m.group(0)
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                return m.group(0)
            data["wordCount"] = word_count
            return f"{ld_open}{json.dumps(data, ensure_ascii=False)}{ld_close}"

        new_html = ARTICLE_LD_RE.sub(add_wordcount, html)
        if new_html != html:
            changes += 1
            html = new_html

    if changes == 0:
        return "already"
    fp.write_text(html, encoding="utf-8")
    return f"patched-{changes}"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = patch_one(fp, lang)
            stats[r] = stats.get(r, 0) + 1
    print("Skip link + wordCount patch:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
