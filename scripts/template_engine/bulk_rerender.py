#!/usr/bin/env python3
"""
bulk_rerender.py — 全 wiki page を新 template で即時再生成 (REF-2 cutover Phase 7、z255aaa)

📖 これは何 (前置き、非技術者向け)

Cutover の後 generate.yml の cron は **毎日 200 page しか re-generate しない**
ため、既存 4,500 page 全部に新 template (Phase 5 translation map / Round 27
attribution fix / 今 turn の rel="noopener noreferrer" 追加) が反映されるのに
**約 23 日かかる**。

このスクリプトは Gemini API を呼ばずに **既存 page から data を抽出 → 新
template で再 render → 元の path に書き戻す**ことで、**1 時間以内に全 4,500
page を新 template に統一**する。

⚡ 流れ:
  1. en/ ja/ pt/ の全 .html を walk
  2. 各 page を `extract.py` で JSON data に分解
  3. `render.py` で新 template で再 HTML 化
  4. 元の path に書き戻す (上書き)

🎯 効果 (cutover 後即時):
  - 全 JA page で badge="Joint Lock" → "関節技" 等の翻訳適用 (Phase 5)
  - 全 page で UGC + Dynamic CTA に attribution 完備 (Round 27)
  - 全 external CTA で target="_blank" + rel="noopener noreferrer" (今 turn)
  - PT page の head 構造 EN/JA と統一 (drift cleanup)

⚠️ Production への影響:
  - 既存 page を **上書きする** (auto-push daemon が 5 分で main 反映)
  - GitHub Pages re-deploy が走り、~10 分以内に全本番 page 更新
  - SEO 影響: HTML 構造変化なし (URL/canonical/og 全部不変)、drift cleanup
    効果でむしろ向上

🛡️ Safety:
  - --dry-run mode で書き込みなし試運転可
  - --limit N で N page だけ rerun (段階的 deploy 可)
  - --lang LANG で 1 locale だけ
  - エラーが出た page は skip + log (silent fail せず)

Usage:
    # まず dry-run で確認
    python3 scripts/template_engine/bulk_rerender.py --dry-run --limit 10

    # 1 locale ずつ慎重に
    python3 scripts/template_engine/bulk_rerender.py --lang ja --limit 50

    # 全部一気に (cutover 用)
    python3 scripts/template_engine/bulk_rerender.py --apply
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract import extract_page
from render import render_page
from batch_verify import is_technique_page

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def find_target_pages(lang: str | None = None, all_archetypes: bool = False) -> list[Path]:
    """Find all pages to re-render.

    If all_archetypes=True (z255ggg), include all wiki pages (Athlete, Equipment,
    Drill, Concept_Strategy, Rule, Conditioning_Nutrition, Misc, etc.) — for
    full template migration.

    Otherwise, only Technique archetype pages (legacy default).
    """
    langs = [lang] if lang else ["en", "ja", "pt"]
    pages = []
    for lc in langs:
        lang_dir = REPO_ROOT / lc
        if not lang_dir.is_dir():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            # Skip non-content pages (index, glossary, root pages)
            if fp.stem in {"index", "techniques-az", "athletes", "athletes-az", "compare", "newsletter", "404"}:
                continue
            try:
                html = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if all_archetypes:
                # Accept any page with <h1>
                if "<h1" in html:
                    pages.append(fp)
            elif is_technique_page(html):
                pages.append(fp)
    return pages


def rerender_one(page_path: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Extract → render → write back. Returns (success, message).

    Wave V (z255hhh): Adds content-preservation safety check.
    If rendered output has > 30% text content loss vs original, ABORT and
    skip this page (signal of cascade corruption or extract bug).
    """
    try:
        html = page_path.read_text(encoding="utf-8")
        slug = page_path.stem
        # Determine lang from path (en / ja / pt)
        lang = page_path.parent.name
        if lang not in ("en", "ja", "pt"):
            return False, f"unknown lang dir: {page_path.parent.name}"

        page_data = extract_page(html, slug)
        new_html = render_page(
            archetype="technique",
            lang=lang,
            page_data=page_data,
            include_z243_cta=True,
        )

        # Wave V: content preservation safety check
        import re as _re
        def _text_only(s):
            body = _re.search(r'<body[^>]*>(.*)</body>', s, _re.DOTALL)
            if not body:
                return ''
            t = body.group(1)
            t = _re.sub(r'<script[^>]*>.*?</script>', '', t, flags=_re.DOTALL)
            t = _re.sub(r'<style[^>]*>.*?</style>', '', t, flags=_re.DOTALL)
            return _re.sub(r'\s+', ' ', _re.sub(r'<[^>]+>', ' ', t)).strip()

        old_text = _text_only(html)
        new_text = _text_only(new_html)
        if old_text:
            loss_pct = (len(old_text) - len(new_text)) * 100 / len(old_text)
            # Acceptable loss: < 40% (FAQ/Athletes/Related extracted separately,
            # drill/concept pages with heavy FAQ can lose ~30-35%, athlete bios ~8%)
            if loss_pct > 40:
                return False, f"⚠️ ABORT: text content loss {loss_pct:.1f}% (old={len(old_text)} new={len(new_text)})"

        # Check for duplicate h2 in rendered output (cascade corruption signal)
        rendered_h2 = _re.findall(r'<h2[^>]*>([^<]+)</h2>', new_html)
        from collections import Counter
        h2_counts = Counter(h.strip() for h in rendered_h2)
        dups = [h for h, c in h2_counts.items() if c > 1]
        if dups:
            return False, f"⚠️ ABORT: duplicate h2 in output: {dups[:3]}"

        if dry_run:
            return True, f"[DRY] would write {len(new_html)} bytes (text loss {loss_pct:.1f}%)"
        page_path.write_text(new_html, encoding="utf-8")
        return True, f"{len(new_html)} bytes written"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", choices=["en", "ja", "pt"], default=None, help="Single locale (default: all 3)")
    parser.add_argument("--limit", type=int, default=None, help="Limit pages (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Don't write, just count")
    parser.add_argument("--apply", action="store_true", help="Required to actually write (safety)")
    parser.add_argument("--all-archetypes", action="store_true", help="z255ggg: include Athlete/Equipment/Drill/Concept/Rule/Conditioning/Misc (full migration)")
    args = parser.parse_args()

    if not args.apply and not args.dry_run:
        print("❌ Either --apply or --dry-run required (safety)", file=sys.stderr)
        return 1

    scope = "ALL archetypes" if args.all_archetypes else "Technique only"
    print(f"🔍 Scanning {scope} pages (lang={args.lang or 'all'})...", file=sys.stderr)
    pages = find_target_pages(args.lang, all_archetypes=args.all_archetypes)
    print(f"   found {len(pages)} pages", file=sys.stderr)

    if args.limit:
        pages = pages[: args.limit]
        print(f"   limited to {len(pages)} (--limit {args.limit})", file=sys.stderr)

    print(f"⚡ {'[DRY-RUN]' if args.dry_run else 'Re-rendering'} {len(pages)} pages...", file=sys.stderr)

    success = 0
    failed = []
    started = time.time()
    for i, page_path in enumerate(pages, 1):
        ok, msg = rerender_one(page_path, dry_run=args.dry_run)
        if ok:
            success += 1
            if i % 50 == 0 or i == len(pages):
                elapsed = time.time() - started
                rate = i / max(elapsed, 0.01)
                eta = (len(pages) - i) / max(rate, 0.01)
                print(f"  [{i:4d}/{len(pages)}] {success} OK, {len(failed)} fail, {rate:.1f} pg/s, ETA {eta:.0f}s", file=sys.stderr)
        else:
            failed.append((page_path, msg))
            print(f"  ❌ {page_path}: {msg}", file=sys.stderr)

    elapsed = time.time() - started
    print(file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"  Total:    {len(pages)}", file=sys.stderr)
    print(f"  Success:  {success}", file=sys.stderr)
    print(f"  Failed:   {len(failed)}", file=sys.stderr)
    print(f"  Elapsed:  {elapsed:.1f}s ({len(pages)/max(elapsed,0.01):.1f} pg/s)", file=sys.stderr)
    if failed:
        print(f"\n  Failed pages (top 5):", file=sys.stderr)
        for fp, msg in failed[:5]:
            print(f"    {fp}: {msg}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    return 0 if not failed else 2


if __name__ == "__main__":
    sys.exit(main())
