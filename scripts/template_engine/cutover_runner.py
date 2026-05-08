#!/usr/bin/env python3
"""
cutover_runner.py — Template-driven wiki generator (REF-2 cutover Phase 2, z255vv)

📖 これは何 (前置き、非技術者向け)

REF-2 refactor の cutover 用「shim」(つなぎ役) です。
旧 generator (`generate_bjj_wiki.py`) と同じ Gemini API call を使うが、
HTML 出力部分だけ新 template (`templates/archetypes/technique.html.j2`) に
置き換える。料理の例えで言うと:

  - 食材調達 (Gemini API call) は同じ料理人 (`call_gemini` 関数を流用)
  - 調理 (HTML 構築) を新人料理人 (= Jinja2 template) に変更
  - 配膳・盛り付け (CTA, FAQ marker, footer 等) は template が一括処理

これで `generate_bjj_wiki.py` の **1,969 行 monolith から 200 行 shim へ**
コード量を圧縮しつつ、output は byte-equivalent (or near) に保てる。

🔄 Switch logic (generate.yml で切替):

  USE_TEMPLATE_PIPELINE=false (default)  → 旧 generate_bjj_wiki.py が走る
  USE_TEMPLATE_PIPELINE=true             → 本 script が走る

Toshiki さんが GitHub Secrets / repo settings で 1 行 flip するだけで
本番切替可能。問題あれば true → false で 10 分 rollback。

📦 依存:
  - `scripts/generate_bjj_wiki.py` の関数を import で再利用:
    - call_gemini, build_article_prompt, add_internal_links, _validate_article_structure
    - TECHNIQUES, LANGUAGES, SITE_DIR, GEMINI_API_KEY
    - load_cache, save_cache, _fetch_low_quality_slugs, _sort_techniques_by_priority

  - `scripts/template_engine/render.py` の render_page 関数

使い方:
    python3 scripts/template_engine/cutover_runner.py --limit 5 --lang all
    python3 scripts/template_engine/cutover_runner.py --force --limit 200
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Reuse existing generate_bjj_wiki.py infrastructure (same Gemini calls,
# same technique list, same caching behavior)
from generate_bjj_wiki import (  # noqa: E402
    call_gemini,
    build_article_prompt,
    add_internal_links,
    TECHNIQUES,
    LANGUAGES,
    SITE_DIR,
    load_cache,
    save_cache,
    _fetch_low_quality_slugs,
    _sort_techniques_by_priority,
    _validate_article_structure,
)

# New template path
from render import render_page  # noqa: E402


# ─── Adapter: Gemini article dict → template page_data schema ──────────────

def _markdown_to_paragraphs(md_text: str) -> list[str]:
    """Lossy md → paragraph list. For intro_paragraphs etc."""
    if not md_text:
        return []
    # Split on double newlines or paragraph separators
    paras = re.split(r"\n\n+", md_text.strip())
    return [p.strip() for p in paras if p.strip()]


def _markdown_to_section_items(md_text: str) -> list[dict]:
    """Lossy md → section items (list of {bold?, text}).

    Handles common patterns:
      - Bullet list items '- **Bold:** text'
      - Numbered list '1. **Bold:** text'
      - Plain bullets '- text'
    """
    if not md_text:
        return []
    items: list[dict] = []
    for line in md_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Strip leading bullet/number markers
        m = re.match(r"^(?:[-*]|\d+\.)\s+(.*)$", line)
        if m:
            content = m.group(1).strip()
        else:
            content = line
        # Detect **Bold:** prefix
        bold_m = re.match(r"^\*\*([^*]+):\*\*\s*(.*)$", content)
        if bold_m:
            items.append({"bold": bold_m.group(1).strip() + ":", "text": bold_m.group(2).strip()})
        else:
            items.append({"text": content})
    return items


def _build_jsonld_article(tech: dict, lang_code: str, article: dict, base_url: str) -> str:
    """Reproduce the Article JSON-LD that article_to_html builds."""
    headline = article.get("title", tech["name"])
    desc = article.get("meta_description", "")
    url = f"{base_url}/{lang_code}/{tech['slug']}.html"
    payload = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headline,
        "description": desc,
        "url": url,
        "inLanguage": lang_code,
        "datePublished": "2026-03-13T00:00:00+09:00",
        "dateModified": "2026-05-08T00:00:00+09:00",
        "author": {"@type": "Organization", "name": "BJJ Wiki", "url": f"{base_url}/"},
        "publisher": {"@type": "Organization", "name": "BJJ Wiki", "url": f"{base_url}/"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def _build_jsonld_breadcrumb(tech: dict, lang_code: str, article: dict, base_url: str) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "BJJ Wiki", "item": f"{base_url}/{lang_code}/index.html"},
            {"@type": "ListItem", "position": 2, "name": article.get("title", tech["name"]),
             "item": f"{base_url}/{lang_code}/{tech['slug']}.html"},
        ],
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def _build_jsonld_faq(article: dict) -> str | None:
    """If at least 1 FAQ exists, build FAQPage JSON-LD."""
    faqs = []
    for i in (1, 2, 3):
        q = article.get(f"faq_q{i}")
        a = article.get(f"faq_a{i}")
        if q and a:
            faqs.append({
                "@type": "Question",
                "name": str(q),
                "acceptedAnswer": {"@type": "Answer", "text": str(a)},
            })
    if not faqs:
        return None
    payload = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faqs}
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def adapt_article_to_page_data(tech: dict, lang_code: str, article: dict, base_url: str = "https://wiki.bjj-app.net") -> dict:
    """Convert Gemini article dict to template page_data schema."""
    h1 = str(article.get("h1", tech["name"]))
    h1_simple = h1.split(":", 1)[0].strip() if ":" in h1 else h1

    seo_title = str(article.get("title", tech["name"]))
    desc = str(article.get("meta_description", ""))

    # Build sections from md fields (same field mapping as article_to_html)
    sections = []
    for section_heading, fields in [
        ("Grips & Mechanics", ["biomechanics_and_grips_md", "how_to"]),
        ("⚠️ White Belt Warnings", ["white_belt_warning_md", "key_details"]),
        ("Drill Progressions", ["drill_progressions_md", "variations"]),
        ("When to Use & Counters", ["counters_and_when_to_use_md", "when_to_use"]),
    ]:
        md_text = ""
        for f in fields:
            if article.get(f):
                md_text = str(article[f])
                break
        if not md_text:
            continue
        items = _markdown_to_section_items(md_text)
        if not items:
            continue
        section: dict = {
            "heading": section_heading,
            "type": "ol" if section_heading == "Grips & Mechanics" or section_heading == "Drill Progressions" else "ul",
            "items": items,
        }
        if "Warning" in section_heading or "⚠️" in section_heading:
            section["style"] = "warning"
        sections.append(section)

    # FAQ
    faq = []
    for i in (1, 2, 3):
        q = article.get(f"faq_q{i}")
        a = article.get(f"faq_a{i}")
        if q and a:
            faq.append({"question": str(q), "answer": str(a)})

    # Related techniques (same-category, exclude self)
    related = [t for t in TECHNIQUES if t["category"] == tech["category"] and t["slug"] != tech["slug"]][:5]
    related_techs = [{"name": t["name"], "slug": t["slug"]} for t in related]

    page_data = {
        "slug": tech["slug"],
        "h1": h1,
        "h1_simple": h1_simple,
        "seo_title": seo_title,
        "og_title": seo_title,
        "og_image_title": tech["name"][:60],
        "description": desc,
        "category": tech.get("category", ""),
        "belt_level": str(article.get("belt_level", "White")),
        "intro_paragraphs": _markdown_to_paragraphs(
            str(article.get("technique_overview_md", article.get("intro", "")))
        ),
        "sections": sections,
        "faq": faq,
        "related_techs": related_techs,
        "jsonld_article": _build_jsonld_article(tech, lang_code, article, base_url),
        "jsonld_breadcrumb": _build_jsonld_breadcrumb(tech, lang_code, article, base_url),
    }

    # Optional FAQ JSON-LD
    faq_jsonld = _build_jsonld_faq(article)
    if faq_jsonld:
        page_data["jsonld_faq"] = faq_jsonld

    # Optional keywords
    keywords = article.get("keywords")
    if keywords and isinstance(keywords, list):
        page_data["keywords"] = ", ".join(str(k) for k in keywords)

    # Optional semantic_links → related_concepts
    sem_links = article.get("semantic_links", [])
    if sem_links and isinstance(sem_links, list):
        related_concepts = []
        for slug in sem_links[:3]:
            slug_str = str(slug).strip()
            if slug_str:
                # Look up name in TECHNIQUES if possible
                t_match = next((t for t in TECHNIQUES if t["slug"] == slug_str), None)
                name = t_match["name"] if t_match else slug_str.replace("-", " ").title()
                related_concepts.append({"name": name, "slug": slug_str})
        if related_concepts:
            page_data["related_concepts"] = related_concepts

    return page_data


# ─── Main pipeline ──────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--lang", default="all")
    parser.add_argument("--dry-run", action="store_true",
                        help="render but don't write files (for testing)")
    args = parser.parse_args()

    os.makedirs(SITE_DIR, exist_ok=True)
    cache = {} if args.force else load_cache()
    langs = list(LANGUAGES.keys()) if args.lang == "all" else [args.lang]
    count = 0

    priority_slugs = _fetch_low_quality_slugs() if args.force else []
    techniques_ordered = _sort_techniques_by_priority(TECHNIQUES, priority_slugs)
    all_slugs = [t["slug"] for t in TECHNIQUES]

    print(f"[cutover_runner] template-driven pipeline starting (lang={args.lang}, limit={args.limit})", file=sys.stderr)

    for lang_code in langs:
        lang_dir = os.path.join(SITE_DIR, lang_code)
        os.makedirs(lang_dir, exist_ok=True)

        for tech in techniques_ordered:
            cache_key = f"{lang_code}/{tech['slug']}"
            out_path = os.path.join(lang_dir, f"{tech['slug']}.html")

            if cache_key in cache and os.path.exists(out_path) and not args.force:
                continue
            if count >= args.limit:
                print(f"[INFO] limit ({args.limit}) reached", file=sys.stderr)
                break

            print(f"[{lang_code}] {tech['name']} ...", file=sys.stderr)
            raw = call_gemini(build_article_prompt(tech, lang_code, all_slugs))
            if not raw:
                print(f"[WARNING] {tech['name']} Gemini call failed", file=sys.stderr)
                continue

            try:
                text = re.sub(r"^```[a-z]*\n?", "", raw.strip(), flags=re.MULTILINE)
                text = re.sub(r"\n?```$", "", text, flags=re.MULTILINE)
                article = json.loads(text.strip())
            except Exception as e:
                print(f"[WARNING] JSON parse: {e}", file=sys.stderr)
                continue

            # Lang-mismatch guard (z255ii) — skip if title/h1 has no native chars
            if lang_code in ("ja", "pt"):
                _t = article.get("title", "")
                _h = article.get("h1", "")
                _has_native = False
                if lang_code == "ja":
                    _has_native = bool(re.search(r"[぀-ゟ゠-ヿ一-鿿]", _t + _h))
                elif lang_code == "pt":
                    _has_native = bool(
                        re.search(r"[ãâáàçéêíóôõúÃÂÁÀÇÉÊÍÓÔÕÚ]", _t + _h)
                    ) or any(
                        w in (_t + _h).lower()
                        for w in ["sobre", "guarda", "guia", "para", "como", "no bjj", "do bjj"]
                    )
                if not _has_native:
                    print(f"[SKIP] {cache_key}: lang-mismatch (preserve existing file)", file=sys.stderr)
                    continue

            # Adapt + render via template
            page_data = adapt_article_to_page_data(tech, lang_code, article)
            html = render_page(
                archetype="technique",
                lang=lang_code,
                page_data=page_data,
                include_z243_cta=True,
            )

            # Same internal-link injection as old pipeline
            html = add_internal_links(html, tech["slug"], lang_code)

            # Validate (same guard as old pipeline)
            if not _validate_article_structure(html, tech["slug"], lang_code):
                print(f"[WARNING] {tech['name']}: structure validation failed, skip write", file=sys.stderr)
                continue

            if args.dry_run:
                print(f"[DRY] would write {out_path} ({len(html)} bytes)", file=sys.stderr)
            else:
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(html)
                cache[cache_key] = True
                print(f"[OK] {out_path} ({len(html)} bytes)", file=sys.stderr)

            count += 1

        if count >= args.limit:
            break

    if not args.dry_run:
        save_cache(cache)
    print(f"[cutover_runner] done. count={count}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
