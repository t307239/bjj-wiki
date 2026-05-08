#!/usr/bin/env python3
"""
gen_llms_txt.py — Generate llms.txt for AI citation optimization (REF-2 W5, BACKLOG F-28)

📖 これは何 (非技術者向け)

`llms.txt` は AI (ChatGPT / Perplexity / Google AI Overviews 等) が site の
全体構造を理解するための「サイトマップの AI 版」です。
通常の sitemap.xml は検索エンジン用に URL 一覧を提供しますが、
llms.txt は AI が **どの page に何が書いてあるかを 1 ファイルで一覧** できる
形にしたもの。

これがあると AI が回答を作るときに wiki.bjj-app.net を citation として
引用しやすくなる → AI からの流入が増える可能性。

format spec: https://llmstxt.org/

📂 出力ファイル
- /llms.txt              (root level、英語ベース、Google AI Overviews が読む)

📋 何を含めるか:
- Site の概要 (1 paragraph)
- 主要 section の link (Wiki の主要技 / 帯ガイド / ルールガイド等)
- 各 link に短い説明 (AI が引用元として理解しやすいよう)

📊 効果 (期待):
- AI overviews / Perplexity / ChatGPT search からの citation 流入 +5-15%
- ChatGPT が「BJJ について」と聞かれた時に bjj-wiki.net を出典として挙げる確率 ↑

Usage:
    python3 scripts/template_engine/gen_llms_txt.py
    python3 scripts/template_engine/gen_llms_txt.py --output llms.txt
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# Curated section structure for llms.txt
# Each (heading, [(slug, description)]) becomes:
#   ## {heading}
#   - [{title}](URL): {description}
SITE_HEADER = """\
# BJJ Wiki — Free Brazilian Jiu-Jitsu Technique Encyclopedia

> Free, open BJJ technique reference covering 1,500+ pages of techniques,
> positions, escapes, sweeps, submissions, drills, and competition rules.
> Available in English, Japanese, and Portuguese.
> Built by an indie blue belt practitioner. No ads, no paywall on the wiki.

Companion training tracker app: https://bjj-app.net (free, optional)
"""


def list_pages_in_lang(lang: str) -> list[Path]:
    """Return all .html pages in a lang directory, excluding indices."""
    lang_dir = REPO_ROOT / lang
    if not lang_dir.is_dir():
        return []
    excluded_stems = {
        "index", "techniques-az", "athletes", "athletes-az", "compare",
        "newsletter", "404",
    }
    return [
        fp for fp in sorted(lang_dir.glob("*.html"))
        if fp.stem not in excluded_stems
    ]


def extract_title_and_h1(html: str) -> tuple[str, str]:
    """Extract <title> and <h1> from page (simple regex, fast)."""
    title_m = re.search(r"<title>([^<]*)</title>", html)
    title = title_m.group(1).strip() if title_m else ""
    # Strip "| BJJ Wiki" suffix variants
    title = re.sub(r"\s*\|\s*BJJ Wiki(\s*Brasil)?\s*$", "", title)
    title = re.sub(r"\s*\|\s*BJJ Wiki\s*\|\s*BJJ Wiki\s*$", "", title)

    h1_m = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", html)
    h1 = h1_m.group(1) if h1_m else ""
    h1 = re.sub(r"<[^>]+>", "", h1).strip()

    return title, h1


def extract_description(html: str) -> str:
    """Extract meta description."""
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
    return m.group(1).strip() if m else ""


def extract_category(html: str) -> str:
    """Extract <span class='badge'>{category}</span>."""
    m = re.search(r'<span class="badge">([^<]*)</span>', html)
    return m.group(1).strip() if m else ""


def categorize_pages(pages: list[Path]) -> dict[str, list[tuple[Path, str, str, str]]]:
    """Group pages by category. Returns {category: [(path, title, h1, desc), ...]}.

    Each tuple has: path, page-title (cleaned), h1 (display), short description.
    """
    by_cat: dict[str, list] = {}
    for fp in pages:
        try:
            html = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        title, h1 = extract_title_and_h1(html)
        if not title:
            continue
        desc = extract_description(html)
        # Truncate description to ~80 chars for llms.txt (it's a list, not full text)
        if len(desc) > 100:
            desc = desc[:97].rstrip() + "..."
        cat = extract_category(html) or "Other"
        by_cat.setdefault(cat, []).append((fp, title, h1, desc))
    return by_cat


def build_llms_txt(pages_by_cat: dict, base_url: str = "https://wiki.bjj-app.net") -> str:
    """Build llms.txt content."""
    out = [SITE_HEADER, ""]

    # Belt Guide section first (high-traffic / authoritative)
    belt_guides = [
        ("white-belt-bjj-guide", "White Belt BJJ Guide"),
        ("blue-belt-bjj-guide", "Blue Belt BJJ Guide"),
        ("purple-belt-bjj-guide", "Purple Belt BJJ Guide"),
        ("brown-belt-bjj-guide", "Brown Belt BJJ Guide"),
        ("black-belt-bjj-guide", "Black Belt BJJ Guide"),
    ]
    out.append("## Belt Guides")
    out.append("")
    for slug, title in belt_guides:
        path = REPO_ROOT / "en" / f"{slug}.html"
        if path.exists():
            out.append(f"- [{title}]({base_url}/en/{slug}.html): Comprehensive overview of techniques and milestones for this belt level.")
    out.append("")

    # Per-category sections (sorted by category name for stable output)
    for cat in sorted(pages_by_cat.keys()):
        if cat == "Other":
            continue
        pages = pages_by_cat[cat]
        if len(pages) < 2:
            continue
        out.append(f"## {cat}")
        out.append("")
        for fp, title, h1, desc in pages[:30]:  # cap at 30 per category to keep llms.txt manageable
            slug = fp.stem
            url = f"{base_url}/en/{slug}.html"
            display_desc = desc if desc else h1
            out.append(f"- [{title}]({url}): {display_desc}")
        if len(pages) > 30:
            out.append(f"- ...and {len(pages) - 30} more {cat} pages.")
        out.append("")

    # Other sections
    if "Other" in pages_by_cat:
        out.append("## Other")
        out.append("")
        for fp, title, h1, desc in pages_by_cat["Other"][:15]:
            slug = fp.stem
            url = f"{base_url}/en/{slug}.html"
            out.append(f"- [{title}]({url}): {desc or h1}")
        if len(pages_by_cat["Other"]) > 15:
            out.append(f"- ...and {len(pages_by_cat['Other']) - 15} more pages.")
        out.append("")

    out.append("---")
    out.append("")
    out.append("## About this file")
    out.append("")
    out.append("This llms.txt follows https://llmstxt.org/ format. It helps AI tools")
    out.append("(ChatGPT, Perplexity, Google AI Overviews, etc.) understand site")
    out.append("structure for citation. Last generated by gen_llms_txt.py.")

    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "llms.txt",
        help="Output path (default: llms.txt at repo root)",
    )
    parser.add_argument(
        "--lang",
        default="en",
        choices=["en", "ja", "pt"],
        help="Language for content (default: en, since llms.txt is global)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print to stdout instead of writing file",
    )
    args = parser.parse_args()

    pages = list_pages_in_lang(args.lang)
    if not pages:
        print(f"❌ No pages found in {args.lang}/", file=sys.stderr)
        return 1

    print(f"📂 Scanning {len(pages)} pages in {args.lang}/...", file=sys.stderr)
    by_cat = categorize_pages(pages)

    cat_summary = ", ".join(f"{cat}={len(p)}" for cat, p in sorted(by_cat.items()))
    print(f"📊 Categories: {cat_summary}", file=sys.stderr)

    content = build_llms_txt(by_cat)

    if args.dry_run:
        sys.stdout.write(content)
    else:
        args.output.write_text(content, encoding="utf-8")
        print(f"✅ Wrote {args.output} ({len(content)} bytes, {content.count(chr(10))} lines)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
