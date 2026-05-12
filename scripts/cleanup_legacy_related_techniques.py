#!/usr/bin/env python3
"""
cleanup_legacy_related_techniques.py — Wave WW SEO 2: dedup pre-existing legacy

39 pages have 2 "Related Techniques"-equivalent h2 sections, both pre-existing
(not from my injection). The pattern is:
  - Match #1: bare `<h2>関連テクニック</h2>` + generic `<ul>` (4 links to hub pages)
  - Match #2: `<h2 class="wc-section-box-title">関連テクニック</h2>` + richer
              wc-section-box-grid with per-page-specific links

Match #2 (the richer one) should be kept. Match #1 (bare/generic) should be
removed along with its following `<ul>` and the "Training Recommendations" /
"トレーニング推奨" / "Recomendações de Treino" h2+ul that often follows it
as a paired template.

Idempotent: only removes if BOTH headings exist.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

HEADINGS = {
    "en": "Related Techniques",
    "ja": "関連テクニック",
    "pt": "Técnicas Relacionadas",
}
TRAINING_HEADING = {
    "en": "Training Recommendations",
    "ja": "トレーニング推奨",
    "pt": "Recomendações de Treino",
}


def find_richer_related(html: str, heading: str) -> bool:
    """Check if the wc-section-box-title variant exists."""
    pat = re.compile(
        r'<h2[^>]*class="[^"]*wc-section-box-title[^"]*"[^>]*>\s*'
        + re.escape(heading) + r'\s*</h2>',
        re.IGNORECASE,
    )
    return bool(pat.search(html))


def find_legacy_block(html: str, heading: str, training: str) -> tuple[int, int] | None:
    """Find the bare-h2 legacy block. Returns (start, end) of region to remove."""
    bare_pat = re.compile(r'<h2>\s*' + re.escape(heading) + r'\s*</h2>')
    m = bare_pat.search(html)
    if not m:
        return None
    start = m.start()
    # Try to extend through the following <ul>...</ul>
    ul_pat = re.compile(r'\s*<ul>.*?</ul>\s*', re.DOTALL)
    after = ul_pat.match(html, m.end())
    if not after:
        return (start, m.end())
    end = after.end()
    # Optionally extend through the paired "Training Recommendations" h2+ul
    training_pat = re.compile(
        r'\s*<h2>\s*' + re.escape(training) + r'\s*</h2>\s*<ul>.*?</ul>\s*',
        re.DOTALL,
    )
    extra = training_pat.match(html, end)
    if extra:
        end = extra.end()
    return (start, end)


def cleanup_one(fp: Path, lang: str) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    heading = HEADINGS[lang]
    training = TRAINING_HEADING[lang]
    if not find_richer_related(html, heading):
        return "skip-no-richer"
    region = find_legacy_block(html, heading, training)
    if not region:
        return "skip-no-legacy"
    start, end = region
    new_html = html[:start] + html[end:]
    fp.write_text(new_html, encoding="utf-8")
    return "removed-legacy"


def main() -> int:
    stats: dict[str, int] = {}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = cleanup_one(fp, lang)
            stats[r] = stats.get(r, 0) + 1
    print("Legacy cleanup results:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
