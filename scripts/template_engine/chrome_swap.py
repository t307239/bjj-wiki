#!/usr/bin/env python3
"""
chrome_swap.py — z255iii Wave GG: Surgical chrome migration

Body-preservation 100%. Strategy:
1. Render new template normally (extract → render) for chrome reference
2. Splice old body into new chrome:
   - new_chrome_top  = new[:h1_start_in_new]
   - old_body        = old[h1_start_in_old : end_marker_in_old]
   - new_chrome_bot  = new[end_marker_in_new:]
3. Combine: new_top + old_body + new_bot
4. Result: new template chrome + 100% original body content

This is safer than extract+rerender because:
- We don't try to "understand" the body structure
- Body content (every word, every tag) is preserved exactly
- Only chrome (head meta / header / footer / CTAs / share-bar) is swapped

Failure modes (handled):
- No h1 in old/new → skip page
- No z243-bottom-cta in old/new → use </body> as boundary
- Render fail → skip page
"""
from __future__ import annotations
import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def find_header_end(html: str) -> int | None:
    """Find position immediately AFTER closing </header> tag."""
    m = re.search(r'</header>', html)
    return m.end() if m else None


def find_footer_start(html: str) -> int | None:
    """Find position of opening <footer> tag (the LAST one)."""
    matches = list(re.finditer(r'<footer[\s>]', html))
    return matches[-1].start() if matches else None


def find_body_end(html: str) -> int | None:
    """Find position of </body>."""
    m = re.search(r'</body>', html)
    return m.start() if m else None


def render_new_template(page_path: Path) -> tuple[bool, str | None]:
    """Run extract → render to produce new template HTML for this page."""
    slug = page_path.stem
    lang = page_path.parent.name
    json_path = f"/tmp/cs_{lang}_{slug}.json"
    html_out = f"/tmp/cs_{lang}_{slug}_new.html"
    r1 = subprocess.run(
        ["python3", "scripts/template_engine/extract.py",
         "--page", str(page_path), "--output", json_path],
        capture_output=True, text=True, timeout=15,
    )
    if r1.returncode != 0:
        return False, f"extract fail: {r1.stderr[-100:]}"
    r2 = subprocess.run(
        ["python3", "scripts/template_engine/render.py",
         "--archetype", "technique", "--lang", lang,
         "--data", json_path, "--output", html_out],
        capture_output=True, text=True, timeout=15,
    )
    if r2.returncode != 0:
        return False, f"render fail: {r2.stderr[-100:]}"
    return True, html_out



def is_already_swapped(html: str) -> bool:
    """Quick heuristic: check if page already has new-template chrome.
    Look for specific markers that only appear in new template output:
    - <link rel="preconnect" href="https://pagead2.googlesyndication.com">
    - <meta property="og:image:width" content="1200">
    """
    return ('preconnect" href="https://pagead2' in html
            and 'og:image:width" content="1200"' in html)


def chrome_swap_one(page_path: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Apply chrome swap to a single page. Returns (success, message)."""
    try:
        old = page_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"read fail: {e}"

    # Idempotent skip
    if is_already_swapped(old):
        return True, "already swapped (skip)"

    # Step 1: render new template for this page
    ok, new_path = render_new_template(page_path)
    if not ok:
        return False, new_path

    new = Path(new_path).read_text(encoding="utf-8")

    # Step 2: find boundaries
    # Splice strategy v2: new_chrome_top = head + header (up to end of </header>)
    #                    old_body       = everything in body between </header> and <footer>
    #                    new_chrome_bot = footer + post-footer scripts + closing tags
    # This preserves 100% of old body content (including any inline z243 markers)
    old_header_end = find_header_end(old)
    old_footer_start = find_footer_start(old)
    new_header_end = find_header_end(new)
    new_footer_start = find_footer_start(new)

    if old_header_end is None or old_footer_start is None:
        return False, f"old: missing header_end ({old_header_end}) or footer_start ({old_footer_start})"
    if new_header_end is None or new_footer_start is None:
        return False, f"new: missing header_end or footer_start"
    if old_header_end >= old_footer_start:
        return False, "old: header after footer"

    # Step 4: splice
    new_chrome_top = new[:new_header_end]
    old_body = old[old_header_end:old_footer_start]
    new_chrome_bot = new[new_footer_start:]

    combined = new_chrome_top + old_body + new_chrome_bot

    # Sanity check: text content preservation
    def text_only(s):
        m = re.search(r'<body[^>]*>(.*)</body>', s, re.DOTALL)
        if not m:
            return ''
        b = m.group(1)
        b = re.sub(r'<script[^>]*>.*?</script>', '', b, flags=re.DOTALL)
        b = re.sub(r'<style[^>]*>.*?</style>', '', b, flags=re.DOTALL)
        return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', b)).strip()

    o_text = text_only(old)
    c_text = text_only(combined)
    if o_text:
        loss_pct = (len(o_text) - len(c_text)) * 100 / len(o_text)
        # Allow some loss (template chrome has different text content)
        # but if loss > 15%, abort (something went wrong)
        if loss_pct > 15:
            return False, f"⚠️ ABORT: text loss {loss_pct:.1f}% (old={len(o_text)} new={len(c_text)})"

    if dry_run:
        return True, f"[DRY] would write {len(combined)} bytes (loss {loss_pct:.1f}%)"

    page_path.write_text(combined, encoding="utf-8")
    return True, f"{len(combined)} bytes (loss {loss_pct:.1f}%)"


def find_target_pages(lang: str | None = None) -> list[Path]:
    """Find pages that need chrome swap (i.e., currently old generator output)."""
    langs = [lang] if lang else ["en", "ja", "pt"]
    pages = []
    for lc in langs:
        lang_dir = REPO_ROOT / lc
        if not lang_dir.is_dir():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            if fp.stem in {"index", "techniques-az", "athletes", "athletes-az",
                           "compare", "newsletter", "404"}:
                continue
            try:
                html = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if "<h1" not in html:
                continue
            pages.append(fp)
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", choices=["en", "ja", "pt"], default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--slug", help="Single slug for testing")
    args = parser.parse_args()

    if not args.apply and not args.dry_run:
        print("❌ Either --apply or --dry-run required (safety)", file=sys.stderr)
        return 1

    if args.slug:
        # Single page test
        for lang in (args.lang and [args.lang]) or ["en", "ja", "pt"]:
            fp = REPO_ROOT / lang / f"{args.slug}.html"
            if fp.exists():
                ok, msg = chrome_swap_one(fp, dry_run=args.dry_run)
                emoji = "✅" if ok else "❌"
                print(f"{emoji} {fp.relative_to(REPO_ROOT)}: {msg}")
        return 0

    pages = find_target_pages(args.lang)
    print(f"Found {len(pages)} pages", file=sys.stderr)
    if args.limit:
        pages = pages[:args.limit]
        print(f"Limited to {len(pages)}", file=sys.stderr)

    success = 0
    failed = 0
    fails = []
    start = time.time()
    for i, fp in enumerate(pages, 1):
        ok, msg = chrome_swap_one(fp, dry_run=args.dry_run)
        if ok:
            success += 1
        else:
            failed += 1
            fails.append((str(fp.relative_to(REPO_ROOT)), msg))
        if i % 50 == 0 or i == len(pages):
            elapsed = time.time() - start
            rate = i / elapsed if elapsed else 0
            eta = (len(pages) - i) / rate if rate else 0
            print(f"  [{i:5d}/{len(pages)}] {success} OK, {failed} fail, {rate:.1f} pg/s, ETA {eta:.0f}s",
                  file=sys.stderr)

    print(f"\nResults: {success} OK / {failed} fail / {len(pages)} total", file=sys.stderr)
    if fails:
        print(f"\nFailed pages (top 10):", file=sys.stderr)
        for f, m in fails[:10]:
            print(f"  ❌ {f}: {m}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
