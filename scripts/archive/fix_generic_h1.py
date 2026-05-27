#!/usr/bin/env python3
"""
fix_generic_h1.py — Wave WW Round 12: real content quality fix

27 pages have generic "Master this Technique" h1 instead of a topic-specific
heading. This kills SEO (Google can't tell what the page is about from h1)
and confuses readers landing from social shares.

Replace with slug-derived title-cased h1:
  bjj-overtime-strategy-bjj → "BJJ Overtime Strategy"
  bjj-strangle-from-back    → "BJJ Strangle from Back"
  bjj-tripod-sweep-guide    → "BJJ Tripod Sweep Guide"

Idempotent. Skip noindex.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex')
H1_RE = re.compile(r'(<h1[^>]*>)([^<]+)(</h1>)')
GENERIC_H1_TEXTS = {
    "Master this Technique",
    "Master this technique",
    "Master This Technique",
    "学ぶべきポイント",
    "Domine esta Técnica",
}

# Words to keep uppercase
UPPER = {"BJJ", "MMA", "ADCC", "IBJJF", "RNC"}
# Lowercase connectors
LOWER = {"from", "to", "for", "the", "a", "of", "in", "and", "with", "vs"}


def slug_to_title(slug: str) -> str:
    """Convert slug to a title-cased h1, e.g., 'bjj-strangle-from-back' → 'BJJ Strangle From Back'."""
    # Strip common suffixes (only at end)
    for suffix in ["-guide", "-system", "-bjj"]:
        if slug.endswith(suffix):
            slug = slug[: -len(suffix)]
    parts = slug.split("-")
    out: list[str] = []
    for i, p in enumerate(parts):
        u = p.upper()
        if u in UPPER:
            out.append(u)
        elif p in LOWER and i > 0:
            out.append(p)
        else:
            out.append(p.capitalize())
    return " ".join(out)


def patch_one(fp: Path, lang: str) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"
    m = H1_RE.search(html)
    if not m:
        return "skip-no-h1"
    h1_text = m.group(2).strip()
    if h1_text not in GENERIC_H1_TEXTS:
        return "skip-not-generic"
    new_h1 = slug_to_title(fp.stem)
    new_html = html[:m.start()] + m.group(1) + new_h1 + m.group(3) + html[m.end():]
    fp.write_text(new_html, encoding="utf-8")
    return f"patched ({h1_text} → {new_h1})"


def main() -> int:
    stats: dict[str, int] = {}
    examples: list[str] = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            r = patch_one(fp, lang)
            key = r if not r.startswith("patched") else "patched"
            stats[key] = stats.get(key, 0) + 1
            if r.startswith("patched") and len(examples) < 8:
                examples.append(f"  {fp.name}: {r[len('patched '):]}")
    print("Generic h1 fix results:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v:,}")
    if examples:
        print("\nExamples:")
        for e in examples:
            print(e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
