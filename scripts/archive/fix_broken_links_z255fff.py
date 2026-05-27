#!/usr/bin/env python3
"""
fix_broken_links_z255fff.py — 22 broken internal links を実在 page に redirect

z255fff (2026-05-09): Wave A of Wiki 最新化 plan.

22 broken links 内訳:
  - typo / 旧名: 5 件 (bjj white belt, scissors-sweep, scissr-sweep, torreano-pass)
  - 抽象 category page (存在しない): 12 件 (joint-lock / leg-lock / choke / guard / sweep)
  - concept link (存在しない): 5 件 (collar-grip / grip-fighting / posture-control / seatbelt-grip / takedown-defense)

Strategy: 各 link を最も意味的に近い existing page に redirect。
generate_bjj_wiki.py source は触らない (これらは Gemini 生成本文中の inline link で source patch 不要)
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# (source_file, broken_target, replacement_target)
FIXES = [
    # EN — typo / 旧名
    ("en/cross-collar-choke.html", "en/bjj white belt.html", "en/white-belt-bjj-guide.html"),
    ("en/guard-pass.html", "en/torreano-pass.html", "en/bjj-torreando-pass-variations.html"),
    # EN — category placeholders (link to closest guide)
    ("en/rear-naked-choke.html", "en/choke.html", "en/bjj-nogi-chokes-guide.html"),
    ("en/loop-choke.html", "en/choke.html", "en/bjj-gi-chokes-guide.html"),
    ("en/closed-guard.html", "en/guard.html", "en/best-bjj-guards.html"),
    ("en/x-guard-sweep.html", "en/sweep.html", "en/bjj-scissor-sweep-guide.html"),
    ("en/straight-armbar.html", "en/joint-lock.html", "en/bjj-joint-lock-mechanics.html"),
    ("en/americana.html", "en/joint-lock.html", "en/bjj-joint-lock-mechanics.html"),
    ("en/armbar.html", "en/joint-lock.html", "en/bjj-joint-lock-mechanics.html"),
    ("en/outside-heel-hook.html", "en/leg-lock.html", "en/best-bjj-leg-locks.html"),
    ("en/inside-heel-hook.html", "en/leg-lock.html", "en/best-bjj-leg-locks.html"),
    # EN — concept links
    ("en/snap-down.html", "en/collar-grip.html", "en/bjj-collar-grip-fighting.html"),
    ("en/baseball-choke.html", "en/grip-fighting.html", "en/bjj-gi-grip-fighting.html"),
    ("en/snap-down.html", "en/posture-control.html", "en/bjj-defensive-posture-guide.html"),
    ("en/backtake.html", "en/seatbelt-grip.html", "en/bjj-back-escape-seat-belt-guide.html"),
    ("en/sprawl.html", "en/takedown-defense.html", "en/bjj-takedown-defense.html"),
    # JA — typo / 旧名
    ("ja/overhead-sweep.html", "ja/scissors-sweep.html", "ja/scissor-sweep.html"),
    ("ja/pendulum-sweep.html", "ja/scissr-sweep.html", "ja/scissor-sweep.html"),
    # JA — category placeholders
    ("ja/rear-naked-choke.html", "ja/choke.html", "ja/bjj-nogi-chokes-guide.html"),
    ("ja/north-south-choke.html", "ja/collar-choke.html", "ja/bjj-collar-choke-details.html"),
    ("ja/loop-choke.html", "ja/collar-lapel-chokes.html", "ja/bjj-gi-chokes-guide.html"),
    ("ja/calf-slicer.html", "ja/leg-lock.html", "ja/best-bjj-leg-locks.html"),
]


def find_existing_target(target: str) -> str | None:
    """Return target if exists, else find closest match."""
    if (REPO_ROOT / target).exists():
        return target
    # Fallback search
    lang = target.split("/")[0]
    name = target.split("/")[1].replace(".html", "")
    candidates = list((REPO_ROOT / lang).glob(f"*{name}*.html"))
    if candidates:
        return f"{lang}/{candidates[0].name}"
    return None


def main(dry_run: bool = False) -> int:
    fixed = 0
    skipped = 0
    not_found = 0

    for source, broken_target, replacement in FIXES:
        source_path = REPO_ROOT / source
        if not source_path.exists():
            print(f"⚠️  source not found: {source}")
            skipped += 1
            continue

        # Validate replacement exists
        replacement_path = REPO_ROOT / replacement
        if not replacement_path.exists():
            # Try fallback search
            actual = find_existing_target(replacement)
            if actual:
                replacement = actual
                replacement_path = REPO_ROOT / actual
            else:
                print(f"❌ replacement target not found: {replacement} (broken={broken_target})")
                not_found += 1
                continue

        html = source_path.read_text(encoding="utf-8")
        broken_filename = broken_target.split("/")[1]
        replacement_filename = replacement.split("/")[1]

        old_pattern = f'href="../{broken_target}"'
        new_pattern = f'href="../{replacement}"'

        if old_pattern not in html:
            print(f"⏭️  no match in {source}: {old_pattern}")
            skipped += 1
            continue

        new_html = html.replace(old_pattern, new_pattern)
        n_replaced = html.count(old_pattern)

        if not dry_run:
            source_path.write_text(new_html, encoding="utf-8")
        print(f"✅ {source}: {broken_filename} → {replacement_filename} ({n_replaced} occurrences)")
        fixed += n_replaced

    print()
    print(f"Summary: fixed={fixed}, skipped={skipped}, not_found={not_found}")
    return 0 if not_found == 0 else 1


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("=== DRY RUN ===")
    sys.exit(main(dry_run=dry_run))
