#!/usr/bin/env python3
"""z261o: heading hierarchy validator for bjj-wiki HTML pages.

検出する 3 class:
  A. multi-h1   — 1 page に <h1> が複数 (a11y / SEO 違反)
  B. no-h1      — <h1> 不在 (a11y screen reader が page topic を把握不能)
  C. skip-level — h1 → h3 等の skip (例: <h1> の直後に <h3>。<h2> が無い)

CI mode: `--ci` で exit 1 if findings > 0.

NOTE:
  - <h1>..<h6> の出現順を line 順で抽出 (HTML 構造を厳密 parse しないが十分な精度)
  - aria-hidden や hidden attribute 付き heading は除外
  - 5 件超を bulk fix する場合は別 script 化 (rule -4.5)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ("en", "ja", "pt")

# <h1>..<h6> tag with optional attributes. case-insensitive.
HEADING_RE = re.compile(
    r"<h([1-6])\b([^>]*)>", re.IGNORECASE
)

# Skip hidden headings (a11y not exposed)
HIDDEN_ATTR_RE = re.compile(
    r'(?:\baria-hidden\s*=\s*["\']?true["\']?|\bhidden\b|\bstyle\s*=\s*["\'][^"\']*display\s*:\s*none)',
    re.IGNORECASE,
)


def extract_headings(html: str) -> list[tuple[int, int, str]]:
    """Return [(level, line_no, raw_tag)] excluding hidden headings."""
    headings: list[tuple[int, int, str]] = []
    for m in HEADING_RE.finditer(html):
        attrs = m.group(2)
        if HIDDEN_ATTR_RE.search(attrs):
            continue
        # Skip <h\d> in <script> / <style> blocks — approximate by looking back
        # 200 chars for </script> or </style> after a matching <script>/<style>.
        start = m.start()
        prefix = html[max(0, start - 4000) : start].lower()
        last_script_open = prefix.rfind("<script")
        last_script_close = prefix.rfind("</script>")
        last_style_open = prefix.rfind("<style")
        last_style_close = prefix.rfind("</style>")
        if last_script_open > last_script_close or last_style_open > last_style_close:
            continue
        level = int(m.group(1))
        # line number
        line_no = html.count("\n", 0, m.start()) + 1
        headings.append((level, line_no, m.group(0)))
    return headings


def classify(headings: list[tuple[int, int, str]]) -> dict[str, list]:
    out: dict[str, list] = {"multi_h1": [], "no_h1": [], "skip_level": []}
    if not headings:
        # no heading at all → no_h1
        out["no_h1"].append(None)
        return out

    h1_lines = [h[1] for h in headings if h[0] == 1]
    if len(h1_lines) == 0:
        out["no_h1"].append(None)
    elif len(h1_lines) > 1:
        out["multi_h1"].extend(h1_lines)

    # skip-level: any consecutive pair (lvl_a, lvl_b) where lvl_b > lvl_a + 1
    # OR the first heading is h3+ when there is no preceding h1/h2 already counted
    prev_lvl = None
    for lvl, line_no, _ in headings:
        if prev_lvl is not None and lvl > prev_lvl + 1:
            out["skip_level"].append((prev_lvl, lvl, line_no))
        prev_lvl = lvl
    return out


REDIRECT_RE = re.compile(
    r'http-equiv\s*=\s*["\']refresh["\']', re.IGNORECASE
)
NOINDEX_RE = re.compile(
    r'<meta\s+name\s*=\s*["\']robots["\']\s+content\s*=\s*["\'][^"\']*noindex',
    re.IGNORECASE,
)


def is_wiki_page(p: Path) -> bool:
    if not p.is_file() or p.suffix != ".html":
        return False
    name = p.name
    # exclude obvious non-content / template files
    if name.startswith("_"):
        return False
    return True


def is_noindex_redirect_stub(html: str) -> bool:
    """Pages that are noindex redirect stubs don't need h1 (legacy ../<page>.html stubs)."""
    head_section = html[:4000]
    return bool(NOINDEX_RE.search(head_section)) and bool(REDIRECT_RE.search(head_section))


def scan_locale(locale: str, sample_n: int | None = None) -> list[dict]:
    """Return [{path, multi_h1, no_h1, skip_level}] for findings."""
    locale_dir = ROOT / locale
    if not locale_dir.exists():
        return []
    files = sorted(p for p in locale_dir.iterdir() if is_wiki_page(p))
    if sample_n is not None:
        # uniform sample (every N-th file)
        step = max(1, len(files) // sample_n)
        files = files[::step][:sample_n]

    findings: list[dict] = []
    for fp in files:
        try:
            html = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        # Skip noindex redirect stubs (legacy ../<page>.html shims)
        if is_noindex_redirect_stub(html):
            continue
        headings = extract_headings(html)
        bucket = classify(headings)
        if any(bucket.values()):
            findings.append(
                {
                    "path": str(fp.relative_to(ROOT)),
                    **bucket,
                }
            )
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ci", action="store_true", help="Exit 1 if findings > 0")
    ap.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Sample N pages per locale (default: all)",
    )
    ap.add_argument(
        "--limit-print",
        type=int,
        default=20,
        help="Max findings to print per class per locale",
    )
    args = ap.parse_args()

    total_multi_h1 = 0
    total_no_h1 = 0
    total_skip_level = 0
    total_pages_with_issue = 0

    for loc in LOCALES:
        findings = scan_locale(loc, sample_n=args.sample)
        if not findings:
            print(f"[{loc}] ✅ 0 finding")
            continue
        m1 = [f for f in findings if f["multi_h1"]]
        nh = [f for f in findings if f["no_h1"]]
        sl = [f for f in findings if f["skip_level"]]
        total_multi_h1 += len(m1)
        total_no_h1 += len(nh)
        total_skip_level += len(sl)
        total_pages_with_issue += len(findings)
        print(f"\n[{loc}] {len(findings)} page(s) with heading issue")
        print(f"  multi-h1   : {len(m1)}")
        print(f"  no-h1      : {len(nh)}")
        print(f"  skip-level : {len(sl)}")
        # print samples
        for f in (m1 + nh + sl)[: args.limit_print]:
            tags = []
            if f["multi_h1"]:
                tags.append(f"multi-h1@lines={f['multi_h1']}")
            if f["no_h1"]:
                tags.append("no-h1")
            if f["skip_level"]:
                tags.append(
                    "skip-level=" + ",".join(f"h{a}→h{b}@L{ln}" for a, b, ln in f["skip_level"][:3])
                )
            print(f"  - {f['path']}  | {'; '.join(tags)}")

    print("\n============================================================")
    print(f"TOTAL: pages_with_issue={total_pages_with_issue}")
    print(f"  multi-h1   : {total_multi_h1}")
    print(f"  no-h1      : {total_no_h1}")
    print(f"  skip-level : {total_skip_level}")
    print("============================================================")

    if args.ci and total_pages_with_issue > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
