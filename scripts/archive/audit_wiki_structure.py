#!/usr/bin/env python3
"""
Wiki構成ムラ検出スクリプト (audit_wiki_structure.py)

全ページを新テンプレート基準でスコアリングし、構造的に欠落している要素を報告する。
スコア17点満点（= 新テンプレート article_to_html の全要素を持つ状態）。

Usage:
  python3 scripts/audit_wiki_structure.py                # 全ページレポート
  python3 scripts/audit_wiki_structure.py --lang ja       # 言語指定
  python3 scripts/audit_wiki_structure.py --below 6       # スコアN未満のみ
  python3 scripts/audit_wiki_structure.py --csv            # CSV出力
  python3 scripts/audit_wiki_structure.py --summary        # サマリーのみ
"""

import re
import os
import sys
import glob
import argparse
from collections import Counter
from pathlib import Path

WIKI_ROOT = Path(__file__).resolve().parent.parent

# ── 17-point structural checklist ──
CHECKS = [
    ("h2_3plus",       "3+ h2 sections",        lambda c: len(re.findall(r'<h2', c)) >= 3),
    ("card_blocks",    "Card UI blocks",         lambda c: bool(re.search(r'class="card"', c))),
    ("toc",            "Table of contents",      lambda c: bool(re.search(r'class="toc', c))),
    ("progress_bar",   "Reading progress bar",   lambda c: bool(re.search(r'read-progress|progress-bar', c))),
    ("back_to_top",    "Back-to-top button",     lambda c: bool(re.search(r'back-to-top', c))),
    ("cta_banner",     "CTA banner/box",         lambda c: bool(re.search(r'cta-banner|cta-box', c))),
    ("share_bar",      "Share bar/buttons",      lambda c: bool(re.search(r'share-bar|share-btn', c))),
    ("beehiiv",        "Beehiiv newsletter CTA", lambda c: bool(re.search(r'beehiiv', c))),
    ("faq_section",    "FAQ section",            lambda c: bool(re.search(r'faq-item|faq-q', c))),
    ("mermaid_map",    "Mermaid technique map",  lambda c: bool(re.search(r'mermaid|Technique Map', c))),
    ("video_section",  "Video/YT section",       lambda c: bool(re.search(r'ts-wrap|yt-search-btn', c))),
    ("jsonld_4plus",   "4+ JSON-LD schemas",     lambda c: len(re.findall(r'application/ld\+json', c)) >= 4),
    ("related_grid",   "Related techniques",     lambda c: bool(re.search(r'related-section|related-grid', c))),
    ("difficulty_bar", "Difficulty bar",          lambda c: bool(re.search(r'difficulty-bar|diff-belt', c))),
    ("athlete_chips",  "Athlete chips",           lambda c: bool(re.search(r'athlete-chip', c))),
    ("breadcrumb",     "Breadcrumb nav",          lambda c: bool(re.search(r'breadcrumb', c))),
    ("body_2000plus",  "Body text > 6KB",         lambda c: len(re.sub(r'<[^>]+>', '', c)) > 6000),
]

MAX_SCORE = len(CHECKS)

SKIP_FILES = {"index.html", "about.html", "athletes.html", "privacy.html", "terms.html"}


def is_technique_page(basename: str) -> bool:
    if basename in SKIP_FILES:
        return False
    if basename.startswith("athlete-"):
        return False
    return basename.endswith(".html")


def score_page(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    basename = os.path.basename(filepath)
    result = {
        "file": basename,
        "path": filepath,
        "score": 0,
        "missing": [],
        "present": [],
    }

    for name, label, check_fn in CHECKS:
        if check_fn(content):
            result["score"] += 1
            result["present"].append(name)
        else:
            result["missing"].append(name)

    result["pct"] = result["score"] / MAX_SCORE * 100
    return result


def main():
    parser = argparse.ArgumentParser(description="Wiki structure audit")
    parser.add_argument("--lang", default="ja", help="Language directory (default: ja)")
    parser.add_argument("--below", type=int, default=None, help="Only show pages below this score")
    parser.add_argument("--csv", action="store_true", help="CSV output")
    parser.add_argument("--summary", action="store_true", help="Summary only")
    args = parser.parse_args()

    lang_dir = WIKI_ROOT / args.lang
    if not lang_dir.is_dir():
        print(f"Error: {lang_dir} not found")
        sys.exit(1)

    all_files = sorted(lang_dir.glob("*.html"))
    tech_files = [f for f in all_files if is_technique_page(f.name)]
    results = [score_page(str(f)) for f in tech_files]

    if args.below is not None:
        results = [r for r in results if r["score"] < args.below]

    if args.csv:
        print("file,score,pct,missing")
        for r in results:
            print(f"{r['file']},{r['score']},{r['pct']:.0f},{';'.join(r['missing'])}")
        return

    # ── Score Distribution ──
    dist = Counter(r["score"] for r in results)
    print(f"\n{'='*60}")
    print(f"  Wiki Structure Audit — {args.lang}/ ({len(results)} technique pages)")
    print(f"{'='*60}")
    print(f"\n  Score Distribution (out of {MAX_SCORE}):")
    for s in sorted(dist.keys()):
        bar = "█" * min(dist[s] // 5, 60)
        print(f"    {s:2d}: {dist[s]:4d}  {bar}")

    avg = sum(r["pct"] for r in results) / len(results) if results else 0
    print(f"\n  Average completeness: {avg:.1f}%")

    # ── Most Commonly Missing Features ──
    missing_counter = Counter()
    for r in results:
        for m in r["missing"]:
            missing_counter[m] += 1
    print(f"\n  Most commonly missing:")
    for feat, count in missing_counter.most_common():
        label = next((l for n, l, _ in CHECKS if n == feat), feat)
        pct = count / len(results) * 100
        print(f"    {label:<25} {count:4d}/{len(results)} ({pct:.0f}%)")

    if args.summary:
        return

    # ── Generation tiers ──
    tier_new = [r for r in results if r["score"] >= 10]
    tier_mid = [r for r in results if 4 <= r["score"] < 10]
    tier_old = [r for r in results if r["score"] < 4]

    print(f"\n  Generation Tiers:")
    print(f"    🟢 New template (10+):  {len(tier_new):4d} pages")
    print(f"    🟡 Mid generation (4-9): {len(tier_mid):4d} pages")
    print(f"    🔴 Old/minimal (0-3):   {len(tier_old):4d} pages")

    # ── Bottom 20 ──
    print(f"\n  Bottom 20 (lowest scores):")
    bottom = sorted(results, key=lambda r: r["score"])[:20]
    for r in bottom:
        missing_str = ", ".join(r["missing"][:4])
        if len(r["missing"]) > 4:
            missing_str += f" +{len(r['missing'])-4}"
        print(f"    {r['score']:2d}/{MAX_SCORE} {r['file']:<40} missing: {missing_str}")

    print()


if __name__ == "__main__":
    main()
