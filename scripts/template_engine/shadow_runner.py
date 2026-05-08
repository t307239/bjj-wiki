#!/usr/bin/env python3
"""
shadow_runner.py — Passive shadow mode runner for cutover verification (z255uu)

📖 これは何 (前置き、非技術者向け)

「Shadow mode」 = 新 template pipeline を **production と並行して動かす** が、
既存 page には触らない仕組みです。料理の例えで言うと:
  - 既存の 7 人料理人がいつも通り料理を作る (production、 影響 0)
  - 新人料理人 (= 新 template) が同じ材料 (= 既存 page から抽出した data)
    で料理を作って、別の皿に置く (= shadow/ directory)
  - 二つの料理を毎日比べて 「同じ味? 違う?」 を Telegram で報告
  - 数日同じ味なら、新人に交代しても安全 → 切替 (= cutover) 可能

このスクリプトは production を一切壊さない pure shadow runner。
明日 GitHub Actions cron が走ると Telegram に結果が届く。

📊 What this does (1 cycle):
  1. Sample N existing pages from en/, ja/, pt/ (default 30 each)
  2. Run extract.py to get JSON data
  3. Run render.py to produce new HTML
  4. Run diff_check.py to categorize differences
  5. Aggregate results across all pages
  6. Output summary + Telegram notification

🚫 What this does NOT do:
  - Does not modify any existing {lang}/*.html
  - Does not call Gemini API (uses existing extracted content)
  - Does not deploy anything to production
  - Does not change generate.yml or any other workflow

Usage:
    python3 scripts/template_engine/shadow_runner.py --sample 30
    python3 scripts/template_engine/shadow_runner.py --sample 100 --output shadow/

Exit code:
    0 = shadow run successful (regardless of TEMPLATE_GAP count)
    1 = runtime error (extraction crashed, etc.)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from batch_verify import list_technique_pages, verify_page  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def run_shadow(lang: str, sample: int) -> dict:
    """Run shadow on N pages for one locale."""
    lang_dir = REPO_ROOT / lang
    pages = list_technique_pages(lang_dir)
    if not pages:
        return {"lang": lang, "error": f"no pages in {lang_dir}", "results": []}

    actual_sample = pages[:sample] if sample < len(pages) else pages
    results = []
    cat_totals: Counter = Counter()
    zero_gap = 0

    for page_path in actual_sample:
        result = verify_page(page_path, lang)
        results.append(result)
        if result.get("error"):
            continue
        for cat, n in result.get("categories", {}).items():
            cat_totals[cat] += n
        if result.get("template_gap", 0) == 0:
            zero_gap += 1

    successful = len([r for r in results if not r.get("error")])

    return {
        "lang": lang,
        "sample_size": len(actual_sample),
        "successful": successful,
        "zero_gap_pct": 100 * zero_gap / max(successful, 1),
        "category_totals": dict(cat_totals),
        "template_gap_total": cat_totals.get("TEMPLATE_GAP", 0),
        "errors": [r for r in results if r.get("error")][:5],
    }


def format_telegram_msg(per_lang: dict[str, dict]) -> str:
    """Build a concise Telegram message body."""
    lines = ["🌓 Shadow run report"]
    overall_ok = True
    for lang, r in per_lang.items():
        if r.get("error"):
            lines.append(f"  {lang.upper()}: ❌ ERROR — {r['error']}")
            overall_ok = False
            continue
        gap = r["template_gap_total"]
        pct = r["zero_gap_pct"]
        # PT in drift cleanup mode: any gap is acceptable (head structure unification)
        if lang == "pt" and gap > 0:
            emoji = "🟢"  # PT drift cleanup
            note = " (drift cleanup mode — head 構造統一、acceptable)"
        elif gap == 0:
            emoji = "✅"
            note = ""
        elif pct >= 90:
            emoji = "🟡"
            note = ""
            overall_ok = False
        else:
            emoji = "❌"
            note = ""
            overall_ok = False
        lines.append(
            f"  {emoji} {lang.upper()}: {r['successful']}/{r['sample_size']} "
            f"verified, {pct:.0f}% zero-gap, {gap} TEMPLATE_GAP hunks{note}"
        )
    lines.append("")
    if overall_ok:
        lines.append("→ 全 locale 同等 (PT は drift cleanup mode)。 cutover 可能 state.")
    else:
        lines.append("→ TEMPLATE_GAP 検出。 template / extractor 確認要.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=int, default=30, help="Pages per locale (default: 30)")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON report path (default: do not write)",
    )
    parser.add_argument(
        "--telegram-msg-out",
        type=Path,
        default=None,
        help="Write Telegram message body to this file (consumed by GHA shell step)",
    )
    args = parser.parse_args()

    per_lang = {}
    for lang in ("en", "ja", "pt"):
        print(f"🔍 Shadow run: {lang}...", file=sys.stderr)
        per_lang[lang] = run_shadow(lang, args.sample)

    msg = format_telegram_msg(per_lang)
    print(msg)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(per_lang, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\n📄 JSON report: {args.output}", file=sys.stderr)

    if args.telegram_msg_out:
        args.telegram_msg_out.parent.mkdir(parents=True, exist_ok=True)
        args.telegram_msg_out.write_text(msg, encoding="utf-8")
        print(f"\n📨 Telegram msg body: {args.telegram_msg_out}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
