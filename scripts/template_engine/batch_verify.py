#!/usr/bin/env python3
"""
batch_verify.py — Run extract → render → diff_check on N existing Technique
                  pages and aggregate gap statistics (REF-2 W2-ext, z255qq)

Workflow per page:
  1. extract.py existing.html  → /tmp/extracted.json
  2. render.py extracted.json  → /tmp/rendered.html
  3. diff_check.py rendered.html vs existing.html

Aggregates: % pages with 0 TEMPLATE_GAP, top failing pages, gap category
distribution. Designed for unattended execution on 20-200 pages.

Usage:
    python3 scripts/template_engine/batch_verify.py --sample 20 --lang en
    python3 scripts/template_engine/batch_verify.py --sample 100 --lang en --out /tmp/batch_report.json
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import tempfile
from collections import Counter
from difflib import unified_diff
from pathlib import Path

# Add the template_engine dir to path so we can import sibling modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract import extract_page  # noqa: E402
from render import render_page  # noqa: E402
from diff_check import parse_unified_diff  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Heuristic to identify Technique archetype pages
# (since we don't have an authoritative archetype map yet)
TECHNIQUE_CATEGORIES = {
    "Joint Lock", "Submission", "Sweep", "Pass", "Escape", "Guard",
    "Takedown", "Choke", "Mount", "Position", "Transition",
    # JA equivalents
    "関節技", "サブミッション", "スイープ", "パス", "エスケープ",
    "テイクダウン", "チョーク", "ポジション",
    # PT equivalents
    "Chave", "Finalização", "Raspagem", "Passagem", "Posição",
}


def is_technique_page(html: str) -> bool:
    """Quick heuristic: pages with `<span class="badge">{category}</span>` matching Technique archetype."""
    m = re.search(r'<span class="badge">([^<]+)</span>', html)
    if not m:
        return False
    return m.group(1).strip() in TECHNIQUE_CATEGORIES


def list_technique_pages(lang_dir: Path) -> list[Path]:
    """Walk lang_dir and return Technique archetype pages."""
    pages = []
    for fp in lang_dir.glob("*.html"):
        # Skip index, glossary, root pages
        if fp.stem in {"index", "techniques-az", "athletes", "athletes-az", "compare"}:
            continue
        try:
            html = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if is_technique_page(html):
            pages.append(fp)
    return pages


def verify_page(page_path: Path, lang: str) -> dict:
    """Run extract → render → diff and return {gap_categories: dict, error: str|None}."""
    try:
        html = page_path.read_text(encoding="utf-8")
        slug = page_path.stem

        # Extract
        page_data = extract_page(html, slug)

        # Render
        rendered = render_page(
            archetype="technique",
            lang=lang,
            page_data=page_data,
            include_z243_cta=True,
        )

        # Diff
        existing_lines = html.splitlines(keepends=True)
        rendered_lines = rendered.splitlines(keepends=True)
        diff = list(
            unified_diff(
                existing_lines,
                rendered_lines,
                fromfile=str(page_path),
                tofile="rendered",
                n=0,
            )
        )

        hunks = parse_unified_diff(diff)
        cats = Counter(cat for cat, _, _ in hunks)

        return {
            "slug": slug,
            "lang": lang,
            "existing_lines": len(existing_lines),
            "rendered_lines": len(rendered_lines),
            "total_hunks": len(hunks),
            "categories": dict(cats),
            "template_gap": cats.get("TEMPLATE_GAP", 0),
            "error": None,
        }
    except Exception as e:
        return {
            "slug": page_path.stem,
            "lang": lang,
            "error": f"{type(e).__name__}: {e}",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", default="en", choices=["en", "ja", "pt"])
    parser.add_argument("--sample", type=int, default=20, help="Random sample size")
    parser.add_argument("--seed", type=int, default=42, help="Sampling seed")
    parser.add_argument("--out", type=Path, default=None, help="Output JSON report")
    args = parser.parse_args()

    lang_dir = REPO_ROOT / args.lang
    if not lang_dir.is_dir():
        print(f"❌ lang dir not found: {lang_dir}", file=sys.stderr)
        return 1

    print(f"🔍 Scanning {lang_dir} for Technique pages...", file=sys.stderr)
    technique_pages = list_technique_pages(lang_dir)
    print(f"   found {len(technique_pages)} Technique pages", file=sys.stderr)

    random.seed(args.seed)
    if args.sample < len(technique_pages):
        sample = random.sample(technique_pages, args.sample)
    else:
        sample = technique_pages

    print(f"📊 Verifying {len(sample)} pages...", file=sys.stderr)

    results = []
    for i, page_path in enumerate(sample, 1):
        result = verify_page(page_path, args.lang)
        results.append(result)
        gap = result.get("template_gap", "ERR")
        err = result.get("error")
        marker = "❌" if err else ("⚠️" if gap and gap > 0 else "✅")
        print(f"  [{i:3d}/{len(sample)}] {marker} {page_path.stem}  (gap={gap})", file=sys.stderr)

    # Aggregate
    successful = [r for r in results if r.get("error") is None]
    errors = [r for r in results if r.get("error") is not None]
    zero_gap = [r for r in successful if r["template_gap"] == 0]

    print()
    print("=" * 70)
    print(f"📈 Batch verify summary ({args.lang}, n={len(sample)})")
    print("=" * 70)
    print(f"  Successful extracts:        {len(successful)} / {len(sample)}")
    print(f"  Extraction errors:          {len(errors)}")
    print(f"  Zero TEMPLATE_GAP pages:    {len(zero_gap)} / {len(successful)} ({100*len(zero_gap)/max(len(successful),1):.1f}%)")
    print()

    # Category aggregation
    cat_totals: Counter = Counter()
    for r in successful:
        for cat, n in r.get("categories", {}).items():
            cat_totals[cat] += n
    print(f"  Category totals (across all pages):")
    for cat, n in cat_totals.most_common():
        emoji = "🔴" if cat == "TEMPLATE_GAP" else "🟢"
        print(f"    {emoji} {cat:18s}: {n}")

    # Top failing pages (highest TEMPLATE_GAP)
    if successful:
        worst = sorted(successful, key=lambda r: -r["template_gap"])[:5]
        print()
        print("  Top 5 by TEMPLATE_GAP count:")
        for r in worst:
            print(f"    {r['template_gap']:3d} gaps — {r['slug']}")

    # Errors
    if errors:
        print()
        print(f"  Extraction errors ({len(errors)}):")
        for r in errors[:5]:
            print(f"    {r['slug']}: {r['error']}")

    # Output JSON
    if args.out:
        report = {
            "lang": args.lang,
            "sample_size": len(sample),
            "successful": len(successful),
            "zero_gap_pct": 100 * len(zero_gap) / max(len(successful), 1),
            "category_totals": dict(cat_totals),
            "results": results,
        }
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n📄 JSON report: {args.out}")

    # Exit code
    template_gap_total = cat_totals.get("TEMPLATE_GAP", 0)
    if template_gap_total > 0:
        print(f"\n❌ {template_gap_total} TEMPLATE_GAP hunks across {len(sample)} pages")
        return 1
    print("\n✅ No real template bugs detected across batch")
    return 0


if __name__ == "__main__":
    sys.exit(main())
