#!/usr/bin/env python3
"""
extract.py — HTML → JSON extractor for Technique pages (REF-2 W2-ext, z255qq)

Parses an existing Technique page HTML and extracts page data into the JSON
schema consumed by render.py. Goal: round-trip extract → render → diff = 0.

Used by:
  - W2 batch verification (run on 20+ existing pages, render, diff_check)
  - W4 cutover (run on all pages to validate template parity before deploy)

Limitations (W2 first cut):
  - Heuristic-based, not 100% precise on edge cases
  - Doesn't extract Gemini-generated section content perfectly
  - Skips JSON-LD bodies (re-rendered from canonical schema)

Usage:
    python3 scripts/template_engine/extract.py --page en/armbar.html --output /tmp/armbar.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag


def extract_jsonld(soup: BeautifulSoup, schema_type: str) -> str | None:
    """Extract a specific JSON-LD block by @type (e.g. 'Article', 'BreadcrumbList', 'FAQPage', 'HowTo')."""
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        text = script.string or ""
        if f'"@type":"{schema_type}"' in text or f'"@type": "{schema_type}"' in text:
            return text.strip()
    return None


def extract_intro_paragraphs(soup: BeautifulSoup) -> list[str]:
    """Extract intro paragraphs (the wrapped <p>...</p></p> block after h1)."""
    paragraphs = []
    h1 = soup.find("h1")
    if not h1:
        return []
    # Walk siblings until we hit difficulty-bar / h2 / toc
    for sibling in h1.find_next_siblings():
        if sibling.name == "h2":
            break
        if sibling.get("id") == "toc":
            break
        if isinstance(sibling, Tag) and sibling.name == "p":
            inner_ps = sibling.find_all("p", recursive=False)
            if inner_ps:
                for p in inner_ps:
                    # Inner content only (strip the <p style="..."> wrapper)
                    # so the template can rewrap consistently
                    paragraphs.append(p.decode_contents())
            else:
                # Skip text-only short <p> wrappers
                pass
        elif isinstance(sibling, Tag) and sibling.get("class") and "belt-guide-box" in sibling.get("class", []):
            continue
    return paragraphs


def extract_sections(soup: BeautifulSoup) -> list[dict]:
    """Extract content sections by walking h2 + sibling content.

    z255ggg (Wave O): content-preserving extraction.
    For each h2, captures all sibling elements until next h2 as raw inner_html.
    Falls back to structured (ol/ul) extraction for Technique-style cards
    to preserve template-driven rendering for those cases.

    Excludes well-known non-content sections (Related Video, FAQ, Athletes etc.)
    which are extracted separately.
    """
    sections = []
    excluded_headings = {
        # EN
        "Related Video",
        "Common BJJ Problems & FAQ",
        "Related Techniques",
        "Athletes",
        "Frequently Asked Questions",
        "Elite Athletes Who Use This",
        # JA
        "関連動画",
        "BJJのよくある悩み・FAQ",
        "関連テクニック",
        "この技を使うトップ選手",
        "🏆 この技を使うトップ選手",
        # PT
        "Vídeo Relacionado",
        "Problemas Comuns no BJJ & FAQ",
        "Técnicas Relacionadas",
        "Atletas de Elite Que Usam Esta Técnica",
    }
    # Excluded class markers (sections with their own extract function)
    excluded_class_markers = {"athletes-section", "faq-list", "yoga-box", "competition-box", "safety-box", "gear-box", "related-techs", "share-bar", "newsletter-box"}

    def is_excluded_heading(text: str) -> bool:
        if text in excluded_headings:
            return True
        if "Athletes" in text or "Atletas" in text or "選手" in text:
            return True
        if "FAQ" in text or "Q&A" in text or "よくある悩み" in text or "Comuns" in text:
            return True
        if text.lower() in {"related techniques", "技関連テクニック", "🥋 関連テクニック"}:
            return True
        return False

    h2_list = soup.find_all("h2")
    for i, h2 in enumerate(h2_list):
        heading_text = h2.get_text(strip=True)
        if is_excluded_heading(heading_text):
            continue

        # Collect all elements between this h2 and next h2 (or end)
        # Skip elements that belong to other extracted features (athlete chips etc.)
        next_h2 = h2_list[i + 1] if i + 1 < len(h2_list) else None
        section_elements = []
        for sib in h2.find_next_siblings():
            if sib is next_h2:
                break
            if isinstance(sib, Tag):
                cls = sib.get("class") or []
                if any(c in cls for c in excluded_class_markers):
                    continue
            section_elements.append(sib)

        # Try structured extraction first (for Technique-style card with ol/ul)
        # Fall back to preserved raw HTML for any other structure
        section: dict = {"heading": heading_text}
        h2_style = h2.get("style", "")
        if "fca5a5" in h2_style or "dc2626" in h2_style:
            section["style"] = "warning"

        # Look for a .card sibling
        card = None
        for el in section_elements:
            if isinstance(el, Tag) and el.name == "div" and "card" in (el.get("class") or []):
                card = el
                break

        if card and (card.find("ol", recursive=False) or card.find("ul", recursive=False)):
            # Technique-style structured (preserve original behavior)
            ol = card.find("ol", recursive=False)
            ul = card.find("ul", recursive=False)
            if ol:
                section["type"] = "ol"
                section["items"] = extract_list_items(ol)
            elif ul:
                section["type"] = "ul"
                section["items"] = extract_list_items(ul)
            else:
                section["type"] = "ul"
                section["items"] = []
        elif section_elements:
            # Content-preserving: capture entire section as raw inner_html
            section["type"] = "preserved"
            inner_parts = []
            for el in section_elements:
                inner_parts.append(str(el))
            section["inner_html"] = "".join(inner_parts).strip()
            # Skip empty sections
            if not section["inner_html"]:
                continue
        else:
            # No content
            continue

        sections.append(section)
    return sections


def extract_list_items(list_tag: Tag) -> list[dict]:
    """Extract items from <ol> or <ul>. Returns list of {bold?, text} dicts."""
    items = []
    for li in list_tag.find_all("li", recursive=False):
        bold_tag = li.find("strong")
        if bold_tag:
            bold_text = bold_tag.get_text(strip=True).rstrip(":")
            # Get text after the <strong> tag
            rest = "".join(
                str(s) for s in bold_tag.next_siblings
            ).strip()
            # Trim leading whitespace/colon
            rest = re.sub(r"^[\s:]+", "", rest)
            items.append({"bold": bold_text + ":", "text": rest})
        else:
            text = "".join(str(s) for s in li.children).strip()
            items.append({"text": text})
    return items


def extract_athletes(soup: BeautifulSoup) -> list[dict]:
    """Extract athlete chips from athletes-section."""
    section = soup.find("div", class_="athletes-section")
    if not section:
        return []
    chips = section.find_all("a", class_="athlete-chip")
    athletes = []
    for chip in chips:
        href = chip.get("href", "")
        slug_match = re.search(r"([^/]+)\.html$", href)
        slug = slug_match.group(1) if slug_match else ""
        flag_span = chip.find("span", recursive=False)
        flag = flag_span.get_text(strip=True) if flag_span else ""
        name_strong = chip.find("strong")
        name = name_strong.get_text(strip=True) if name_strong else ""
        athletes.append({"name": name, "flag": flag, "slug": slug})
    return athletes


def extract_yoga_poses(soup: BeautifulSoup) -> list[dict]:
    """Extract yoga pose chips from yoga-box."""
    box = soup.find("div", class_="yoga-box")
    if not box:
        return []
    poses = []
    for chip in box.find_all("a", class_="yoga-chip"):
        href = chip.get("href", "")
        slug_match = re.search(r"/([^/]+)\.html$", href)
        slug = slug_match.group(1) if slug_match else ""
        # Strip "🧘 " prefix from name
        name = chip.get_text(strip=True).replace("🧘", "").strip()
        poses.append({"name": name, "slug": slug})
    return poses


def extract_faq(soup: BeautifulSoup) -> list[dict]:
    """Extract FAQ Q&A pairs from .faq divs."""
    faq = []
    for div in soup.find_all("div", class_="faq"):
        q_div = div.find("div", class_="faq-q")
        if not q_div:
            continue
        question = q_div.get_text(strip=True)
        question = re.sub(r"^Q:\s*", "", question)
        # Answer is the next <p>
        ans_p = div.find("p")
        answer = "".join(str(c) for c in ans_p.children).strip() if ans_p else ""
        faq.append({"question": question, "answer": answer})
    return faq


def extract_related_techs(soup: BeautifulSoup) -> list[dict]:
    """Extract related techniques grid links."""
    # Find the div containing the Related Techniques heading
    heading_match = soup.find("h3", string=re.compile(r"Related Techniques|関連テクニック|Técnicas Relacionadas"))
    if not heading_match:
        return []
    grid = heading_match.find_parent("div")
    if not grid:
        return []
    techs = []
    for a in grid.find_all("a", href=True):
        href = a["href"]
        slug_match = re.search(r"([^/]+)\.html$", href)
        slug = slug_match.group(1) if slug_match else ""
        name = a.get_text(strip=True)
        techs.append({"name": name, "slug": slug})
    return techs


def extract_related_concepts(soup: BeautifulSoup) -> list[dict]:
    """Extract Dig Deeper semantic links."""
    heading_match = soup.find("h3", string=re.compile(r"Dig Deeper|深掘り|Aprofunde-se"))
    if not heading_match:
        return []
    container = heading_match.find_parent("div")
    if not container:
        return []
    concepts = []
    for a in container.find_all("a", href=True):
        href = a["href"]
        slug_match = re.search(r"([^/]+)\.html$", href)
        slug = slug_match.group(1) if slug_match else ""
        # Strip trailing "→" arrow
        name = a.get_text(strip=True).replace("→", "").strip()
        concepts.append({"name": name, "slug": slug})
    return concepts


def extract_video_embed_id(soup: BeautifulSoup) -> str | None:
    """Extract YouTube embed ID from the iframe."""
    iframe = soup.find("iframe", src=re.compile(r"youtube\.com/embed/"))
    if not iframe:
        return None
    src = iframe.get("src", "")
    m = re.search(r"/embed/([A-Za-z0-9_\-]+)", src)
    return m.group(1) if m else None


def extract_difficulty(soup: BeautifulSoup) -> dict | None:
    """Extract difficulty bar (belt color, stars, label).

    z255ccc: Normalize belt to canonical English. Existing pages may have
    translated belt text (e.g. "Branca", "白帯") which would break template
    lookups in belt_guide_box keyed on English.
    """
    bar = soup.find("div", class_="difficulty-bar")
    if not bar:
        return None
    diff_belt = bar.find("span", class_="diff-belt")
    diff_stars = bar.find("span", class_="diff-stars")
    diff_label = bar.find("span", class_="diff-label")
    if not (diff_belt and diff_stars and diff_label):
        return None
    # Normalize belt text to canonical English (lowercase)
    raw = diff_belt.get_text(strip=True).lower()
    locale_to_english = {
        "white": "white", "blue": "blue", "purple": "purple", "brown": "brown", "black": "black",
        # PT (long form + diff-belt UPPERCASE form)
        "branca": "white", "azul": "blue", "roxa": "purple", "marrom": "brown", "preta": "black",
        # JA (long form 白帯 + diff-belt short form 白 — both possible from re-rendered pages)
        "白帯": "white", "青帯": "blue", "紫帯": "purple", "茶帯": "brown", "黒帯": "black",
        "白": "white", "青": "blue", "紫": "purple", "茶": "brown", "黒": "black",
    }
    canonical = locale_to_english.get(raw, raw)
    return {
        "belt": canonical,
        "stars": diff_stars.get_text(strip=True),
        "label": diff_label.get_text(strip=True),
    }


def extract_guide_belt(soup: BeautifulSoup) -> str | None:
    """Extract guide_belt from belt-guide-box (Blue/Purple/etc.)."""
    box = soup.find("div", class_="belt-guide-box")
    if not box:
        return None
    badge = box.find("span")
    if not badge:
        return None
    text = badge.get_text(strip=True)
    # "Blue Belt Technique" → "blue"
    m = re.search(r"^(\w+)\s+Belt", text, re.IGNORECASE)
    if m:
        return m.group(1).lower()
    # JA: "青帯テクニック"
    if "白" in text:
        return "white"
    if "青" in text:
        return "blue"
    if "紫" in text:
        return "purple"
    if "茶" in text:
        return "brown"
    if "黒" in text:
        return "black"
    return None


def extract_page(html: str, slug: str) -> dict:
    """Extract a Technique page into the page data JSON schema."""
    soup = BeautifulSoup(html, "html.parser")

    # Basic metadata
    title_tag = soup.find("title")
    seo_title = title_tag.get_text(strip=True) if title_tag else ""

    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag.get("content", "") if desc_tag else ""

    keywords_tag = soup.find("meta", attrs={"name": "keywords"})
    keywords = keywords_tag.get("content", "") if keywords_tag else ""

    og_title_tag = soup.find("meta", attrs={"property": "og:title"})
    og_title = og_title_tag.get("content", "") if og_title_tag else seo_title

    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(strip=True) if h1_tag else ""
    # h1_simple = first part before colon (e.g. "Armbar: A White Belt's Guide" → "Armbar")
    h1_simple = h1.split(":", 1)[0].strip() if ":" in h1 else h1

    badge_tag = soup.find("span", class_="badge")
    category = badge_tag.get_text(strip=True) if badge_tag else ""

    # z255ccc: extract belt level from CLASS suffix (canonical English),
    # not text content (which may be translated like "Branca" / "白帯")
    belt_tag = soup.find("span", class_=re.compile(r"^belt\s+belt-"))
    belt_level = "White"
    if belt_tag:
        for cls in belt_tag.get("class", []):
            m = re.match(r"belt-([a-z]+)$", cls)
            if m:
                # Capitalize: "white" → "White", "brown" → "Brown"
                belt_level = m.group(1).capitalize()
                break

    # og_image_title: from og:image URL parameter "title=X"
    og_image_tag = soup.find("meta", attrs={"property": "og:image"})
    og_image_url = og_image_tag.get("content", "") if og_image_tag else ""
    og_image_title_match = re.search(r"[?&]title=([^&]+)", og_image_url)
    og_image_title = og_image_title_match.group(1) if og_image_title_match else h1_simple

    page: dict = {
        "slug": slug,
        "h1": h1,
        "h1_simple": h1_simple,
        "seo_title": seo_title,
        "og_title": og_title,
        "og_image_title": og_image_title,
        "description": description,
        "category": category,
        "belt_level": belt_level,
    }
    if keywords:
        page["keywords"] = keywords

    diff = extract_difficulty(soup)
    if diff:
        page["difficulty"] = diff

    guide_belt = extract_guide_belt(soup)
    if guide_belt:
        page["guide_belt"] = guide_belt

    page["intro_paragraphs"] = extract_intro_paragraphs(soup)
    page["sections"] = extract_sections(soup)
    page["athletes"] = extract_athletes(soup)
    page["yoga_poses"] = extract_yoga_poses(soup)
    page["faq"] = extract_faq(soup)
    page["related_techs"] = extract_related_techs(soup)
    page["related_concepts"] = extract_related_concepts(soup)

    video_id = extract_video_embed_id(soup)
    if video_id:
        page["video_embed_id"] = video_id

    # JSON-LD blocks (preserve as-is, the template will inject them safely)
    article_jsonld = extract_jsonld(soup, "Article")
    breadcrumb_jsonld = extract_jsonld(soup, "BreadcrumbList")
    faq_jsonld = extract_jsonld(soup, "FAQPage")
    howto_jsonld = extract_jsonld(soup, "HowTo")

    # z255eee: fix wrong @id (root URL) in existing JSON-LD
    # Some existing pages have mainEntityOfPage.@id = "https://wiki.bjj-app.net/"
    # (root) instead of the actual canonical URL. Repair while extracting.
    canonical_url_pattern = soup.find("link", attrs={"rel": "canonical"})
    canonical_url = canonical_url_pattern.get("href", "") if canonical_url_pattern else ""
    if canonical_url and article_jsonld:
        # Replace wrong @id with canonical URL
        article_jsonld = re.sub(
            r'"@id":"https://wiki\.bjj-app\.net/?"',
            f'"@id":"{canonical_url}"',
            article_jsonld,
        )
        # Also fix url field
        article_jsonld = re.sub(
            r'"url":"https://wiki\.bjj-app\.net/?"',
            f'"url":"{canonical_url}"',
            article_jsonld,
        )

    if article_jsonld:
        page["jsonld_article"] = article_jsonld
    if breadcrumb_jsonld:
        page["jsonld_breadcrumb"] = breadcrumb_jsonld
    if faq_jsonld:
        page["jsonld_faq"] = faq_jsonld
    if howto_jsonld:
        page["jsonld_howto"] = howto_jsonld
        page["howto_steps"] = True

    return page


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", required=True, type=Path, help="Path to existing HTML page")
    parser.add_argument("--output", type=Path, default=None, help="Output JSON file (default: stdout)")
    args = parser.parse_args()

    if not args.page.exists():
        print(f"❌ page not found: {args.page}", file=sys.stderr)
        return 1

    html = args.page.read_text(encoding="utf-8")
    # Slug from filename (without .html)
    slug = args.page.stem

    page_data = extract_page(html, slug)

    json_out = json.dumps(page_data, ensure_ascii=False, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json_out, encoding="utf-8")
        print(f"✅ Extracted: {args.output} ({len(json_out)} bytes)", file=sys.stderr)
    else:
        sys.stdout.write(json_out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
