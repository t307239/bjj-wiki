#!/usr/bin/env python3
"""
inject_related_techniques.py — Wave WW (F): Internal linking strengthening

Audit found 2,014 orphan pages (0 inbound links) across 3 locales:
  - EN: 558 (37.6%)
  - JA: 406 (27.4%)
  - PT: 1,050 (70.8%)

Strategy: inject a "Related Techniques" section into pages that have no
"related-techniques" marker yet, linking to 5-8 thematically-related slugs
(by slug-token overlap). Each link = 1 inbound link for that target page.

Idempotent: marker `<!-- z255jjjj-related-tech -->` skips re-runs.

Anchor: insert AFTER the last <footer> (or before </body> if no footer).
This places the section at the page bottom (above the footer in new
template, or at the very end in legacy pages).
"""
from __future__ import annotations
import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
MARKER = "<!-- z255jjjj-related-tech -->"

# Tokenize: split slug by `-`, drop common BJJ noise words and stop tokens
NOISE = {
    "bjj", "guide", "guides", "the", "and", "a", "to", "in", "of", "for", "with",
    "best", "vs", "is", "or", "an", "from", "by", "on",
    "athlete", "tournament", "competition",  # too generic
}
SHORT_OK = {"gi", "no", "ko", "wt"}  # short tokens worth keeping


def tokenize(slug: str) -> set[str]:
    parts = slug.split("-")
    return {p for p in parts if (len(p) > 2 or p in SHORT_OK) and p not in NOISE}


# Build inbound link counter to find orphans
LINK_RE = re.compile(
    r'<a[^>]+href=["\'](?:\.\./)?(?:[a-z]{2}/)?([a-z0-9\-]+)\.html["\']',
    re.IGNORECASE,
)
SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
NOINDEX_RE = re.compile(r'name="robots"\s+content="noindex')

# Anchor: prefer to insert before z243-bottom-cta marker; fallback to <footer>; final fallback to </body>
INSERT_ANCHORS = [
    re.compile(r"<!--\s*z243-bottom-cta\s*-->", re.IGNORECASE),
    re.compile(r"<footer[\s>]", re.IGNORECASE),
    re.compile(r"</body>", re.IGNORECASE),
]

# Heading translation per locale
HEADINGS = {
    "en": "Related Techniques",
    "ja": "関連テクニック",
    "pt": "Técnicas Relacionadas",
}


def find_indexable_pages() -> dict[str, dict[str, Path]]:
    """Return {lang: {slug: Path}} for all indexable pages per locale."""
    result: dict[str, dict[str, Path]] = {l: {} for l in LANGS}
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                head = fp.read_text(encoding="utf-8", errors="ignore")[:600]
            except Exception:
                continue
            if NOINDEX_RE.search(head):
                continue
            # Skip generic index/list pages from "related" candidates
            if fp.stem in {
                "index", "techniques-az", "athletes", "athletes-az",
                "concepts-az", "drills-az", "rules-az", "equipment-az",
                "skill-tree", "news", "privacy", "about", "newsletter",
                "404", "sparring-simulator", "competition-events",
                "competition-prep", "competition-results",
                "yoga-for-bjj", "yoga-poses-az",
            }:
                continue
            result[lang][fp.stem] = fp
    return result


def find_related_for_slug(slug: str, all_slugs: list[str], k: int = 6) -> list[str]:
    """Return top-k related slugs by token-overlap Jaccard similarity.

    Special-case fallbacks:
    - athlete-* slug → if no token match, peer with other athlete-* slugs
    - bjj-X-* slug → if no token match, peer with other bjj-X-* siblings
    """
    own = tokenize(slug)
    scored: list[tuple[float, str]] = []
    if own:
        for other in all_slugs:
            if other == slug:
                continue
            ot = tokenize(other)
            if not ot:
                continue
            intersection = own & ot
            if not intersection:
                continue
            jaccard = len(intersection) / len(own | ot)
            prefix_match = sum(1 for o in own if o in ot)
            scored.append((jaccard + prefix_match * 0.05, other))
    scored.sort(reverse=True)
    result = [s for _, s in scored[:k]]

    if len(result) >= 3:
        return result

    # Fallback 1: peer with same-prefix athlete slugs
    if slug.startswith("athlete-"):
        peers = [s for s in all_slugs if s.startswith("athlete-") and s != slug]
        # Deterministic but spread: pick by hash position
        import hashlib
        peers.sort(key=lambda s: hashlib.md5((slug + s).encode()).hexdigest())
        return (result + [p for p in peers if p not in result])[:k]

    # Fallback 2: peer with siblings sharing 2-token prefix (e.g., bjj-arm-*)
    parts = slug.split("-")
    if len(parts) >= 3:
        prefix2 = "-".join(parts[:2]) + "-"
        peers = [s for s in all_slugs if s.startswith(prefix2) and s != slug and s not in result]
        result = (result + peers)[:k]

    # Fallback 3: alphabetical neighbors (still better than nothing for SEO)
    if len(result) < 3:
        sorted_slugs = sorted(all_slugs)
        try:
            idx = sorted_slugs.index(slug)
        except ValueError:
            idx = 0
        # Pick slugs at index ±1, ±2, ±3, ±4
        neighbors: list[str] = []
        for offset in [-1, 1, -2, 2, -3, 3, -4, 4]:
            if 0 <= idx + offset < len(sorted_slugs):
                cand = sorted_slugs[idx + offset]
                if cand != slug and cand not in result and cand not in neighbors:
                    neighbors.append(cand)
        result = (result + neighbors)[:k]

    return result


def already_has_marker(html: str) -> bool:
    return MARKER in html


def find_insert_position(html: str) -> int | None:
    for rx in INSERT_ANCHORS:
        m = rx.search(html)
        if m:
            return m.start()
    return None


def build_section(related: list[str], lang: str) -> str:
    heading = HEADINGS[lang]
    # Title-case slug for visible label, e.g. "bjj-armbar-setup" → "BJJ Armbar Setup"
    def label(slug: str) -> str:
        words = []
        for w in slug.split("-"):
            if w == "bjj":
                words.append("BJJ")
            elif w == "no":
                words.append("No")
            elif w == "gi":
                words.append("Gi")
            else:
                words.append(w.capitalize())
        return " ".join(words)

    items = "".join(
        f'<a href="{slug}.html" style="background:#1e1e2e;color:#c8e6c9;'
        f'text-decoration:none;padding:6px 14px;border-radius:6px;font-size:.9rem;'
        f'border:1px solid rgba(255,255,255,0.10);transition:border-color .15s">'
        f'{label(slug)}</a>'
        for slug in related
    )
    return (
        f"\n{MARKER}\n"
        f'<section style="background:var(--card,#18181b);border:1px solid var(--border,rgba(255,255,255,0.10));'
        f'border-radius:12px;padding:24px;margin:32px 0">\n'
        f'  <h2 style="font-size:1.1rem;color:var(--accent,#7c3aed);margin-bottom:16px">{heading}</h2>\n'
        f'  <div style="display:flex;flex-wrap:wrap;gap:8px">{items}</div>\n'
        f"</section>\n"
    )


def inject_one(fp: Path, lang: str, all_slugs: list[str], dry: bool) -> str:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return "skip-read"
    if NOINDEX_RE.search(html[:600]):
        return "skip-noindex"
    if already_has_marker(html):
        return "already"
    related = find_related_for_slug(fp.stem, all_slugs, k=6)
    if len(related) < 3:
        return "skip-no-related"
    pos = find_insert_position(html)
    if pos is None:
        return "skip-no-anchor"
    section = build_section(related, lang)
    new_html = html[:pos] + section + html[pos:]
    if dry:
        return f"dry-{len(related)}"
    fp.write_text(new_html, encoding="utf-8")
    return f"patched-{len(related)}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--lang", choices=LANGS)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    if not args.apply and not args.dry_run:
        print("❌ --apply or --dry-run required", file=sys.stderr)
        return 1

    pages = find_indexable_pages()
    langs = [args.lang] if args.lang else LANGS

    for lang in langs:
        all_slugs = sorted(pages[lang].keys())
        targets = sorted(pages[lang].items())
        if args.limit:
            targets = targets[: args.limit]
        stats: dict[str, int] = defaultdict(int)
        for slug, fp in targets:
            r = inject_one(fp, lang, all_slugs, dry=args.dry_run)
            stats[r] += 1
        print(f"\n=== {lang} ===")
        for k in sorted(stats.keys()):
            print(f"  {k}: {stats[k]:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
