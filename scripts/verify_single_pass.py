#!/usr/bin/env python3
"""
verify_single_pass.py — z262+: 全 per-page lint を1ファイル1読みで実行

旧 verify_fast.py: 55 subprocess × parallel = 5-10s (各 script が独立に全 HTML を読む)
verify_single_pass.py: 1回ファイル walk で 44 per-page check を実行 + 9 cross-page subprocess を並列
  → I/O 削減 ~99% (4,500 HTML × 55 reads → 4,500 reads)
  → sandbox network mount でも 45s timeout 問題なし

split 方針:
  [inline per-page]  ファイルを1枚読めば完結する check (44 本)
  [subprocess]       複数ファイルの照合・sitemap・hreflang 等 cross-page check (9 本)

Usage:
    python3 scripts/verify_single_pass.py          # 全 lint 実行
    python3 scripts/verify_single_pass.py --ci     # exit 1 on any failure
"""
from __future__ import annotations
import json
import os
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
LANGS = ("en", "ja", "pt")
SITE = "https://wiki.bjj-app.net"

# ─── Shared ───────────────────────────────────────────────────────────────────
NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', re.IGNORECASE)
REDIRECT_MARKER = "<!-- z262-redirect -->"
REDIRECT_META_RE = re.compile(r'<meta[^>]+http-equiv=["\']refresh["\']', re.IGNORECASE)
SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
STYLE_RE = re.compile(r"<style[^>]*>.*?</style>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
A_TAG_RE = re.compile(r"<a\b[^>]*>", re.IGNORECASE)
H1_RE = re.compile(r"<h1[^>]*>([^<]+)</h1>")
CANONICAL_RE = re.compile(r'<link rel="canonical" href="([^"]+)"')
TITLE_RE = re.compile(r"<title>([\s\S]*?)</title>", re.IGNORECASE)
META_DESC_RE = re.compile(
    r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', re.IGNORECASE
)

# ─── check_jsonld_validity ────────────────────────────────────────────────────
JSONLD_BLOCK_RE = re.compile(
    r'<script type=["\']application/ld\+json["\']\s*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)
JSONLD_TEMPLATE_RE = re.compile(r"\{[A-Za-z_]+\}")

# ─── check_breadcrumb_locale_drift ───────────────────────────────────────────
BJJ_PROPER_NOUNS = {
    "Berimbolo", "Kimura", "Omoplata", "Americana", "Ezekiel",
    "Granby Roll", "Heel Hook", "Toe Hold", "Knee Bar", "Gogoplata", "Imanari Roll",
}
BREADCRUMB_DIV_RE = re.compile(r'<div class="breadcrumb">(.*?)</div>', re.DOTALL)
BREADCRUMB_LAST_RE = re.compile(r"›\s*([^›]+?)\s*$")
PT_MARKERS = (
    "ã","á","â","ç","é","ê","í","ó","ô","õ","ú",
    "ção","ões","guarda","jiu","técnica"," do "," da "," de ",
    " no "," os "," as "," um "," uma "," para "," em ",
    " na "," nas "," nos "," sua "," seu "," sem ",
    "qual "," vs.","entre","ando","endo","indo","iz ","ido ","ada ","ado ",
    "domine","aprenda","defenda","controle","defesa","finaliz",
    "treinar","lutar","comp","regras","completo","completa","guia","sistema","queda",
    "raspagem","passagem","estrang","chave","ataque","contra",
    "finalização","iniciante","avançado","fundamento",
    "pegada","lutas","energia","requisitos","faixa","azul",
    "roxa","marrom","preta","branca","kimono","costas",
    "cotovelo","joelho","sobrecarga","progressiva",
    "filosofia","categoria","arco","flecha","brabo",
    "entrada","escudo","gerenciando",
)

# ─── check_ui_label_locale_drift ─────────────────────────────────────────────
EN_CATEGORIES = {"Choke","Defense","Escape","Guard","Joint Lock",
                 "Leg Lock","Passing","Position","Sweep","Takedown","Transition"}
EN_BELTS = {"White","Blue","Purple","Brown","Black"}
EN_DIFFICULTIES = {"Beginner","Intermediate","Advanced"}
EN_BELT_FULL = {"White Belt","Blue Belt","Purple Belt","Brown Belt","Black Belt"}

# ─── check_cta_text_locale_drift ─────────────────────────────────────────────
EN_CTA_PATTERNS = [
    re.compile(r"\bStart Free\b"), re.compile(r"\bGet Started\b"),
    re.compile(r"\bSign Up\b"),    re.compile(r"\bJoin Free\b"),
    re.compile(r"\bTry Free\b"),   re.compile(r"\bJoin Now\b"),
]

# ─── check_analytics_id_drift ────────────────────────────────────────────────
EXPECTED_GA4 = "G-7LM8L3TRZM"
EXPECTED_GTM = "GTM-WC3DKRB"

# ─── check_brand_suffix_pollution ────────────────────────────────────────────
DOUBLE_BRAND_RE = re.compile(
    r"— BJJ Wiki\s*\|\s*BJJ Wiki|BJJ Wiki Brasil\s*\|\s*BJJ Wiki", re.IGNORECASE
)
OG_TITLE_RE = re.compile(
    r'<meta property=["\']og:title["\'][^>]*content=["\']([^"\']*)["\']', re.IGNORECASE
)

# ─── check_duplicate_bjj_prefix ──────────────────────────────────────────────
DUP_PREFIX_RE = re.compile(r"(【BJJ】\s*){2,}")

# ─── check_duplicate_faq_heading ─────────────────────────────────────────────
FAQ_H2_RE = re.compile(
    r"<h2[^>]*>\s*(?:Frequently Asked Questions|よくある質問|Perguntas Frequentes)\s*</h2>",
    re.IGNORECASE,
)

# ─── check_duplicate_related_techniques ──────────────────────────────────────
REL_TECH_PATTERNS: dict[str, list[re.Pattern]] = {
    "en": [
        re.compile(r"<h2[^>]*>\s*Related Techniques\s*</h2>", re.IGNORECASE),
        re.compile(r"<h2[^>]*>\s*Related Guides\s*</h2>", re.IGNORECASE),
        re.compile(r"<h2[^>]*>\s*Related Articles\s*</h2>", re.IGNORECASE),
    ],
    "ja": [
        re.compile(r"<h2[^>]*>\s*関連テクニック\s*</h2>"),
        re.compile(r"<h2[^>]*>\s*関連ガイド\s*</h2>"),
        re.compile(r"<h2[^>]*>\s*関連記事\s*</h2>"),
    ],
    "pt": [
        re.compile(r"<h2[^>]*>\s*Técnicas Relacionadas\s*</h2>", re.IGNORECASE),
        re.compile(r"<h2[^>]*>\s*Guias Relacionados\s*</h2>", re.IGNORECASE),
        re.compile(r"<h2[^>]*>\s*Artigos Relacionados\s*</h2>", re.IGNORECASE),
    ],
}

# ─── check_h1_brand_pollution ────────────────────────────────────────────────
H1_BRAND_RE = re.compile(r"\|\s*BJJ\s*Wiki", re.IGNORECASE)

# ─── check_h2_id_clobber ─────────────────────────────────────────────────────
AUTO_TOC_CLOBBER_RE = re.compile(r"h\.id\s*=\s*['\"]?section-")
AUTO_TOC_GUARD_RE = re.compile(r"if\s*\(!h\.id\)")

# ─── check_heading_hierarchy ─────────────────────────────────────────────────
HEADING_LEVEL_RE = re.compile(r"<h([1-6])\b([^>]*)>", re.IGNORECASE)
HIDDEN_ATTR_RE = re.compile(
    r'(?:\baria-hidden\s*=\s*["\']?true["\']?|\bhidden\b|\bstyle\s*=\s*["\'][^"\']*display\s*:\s*none)',
    re.IGNORECASE,
)

# ─── check_html_quality_minor ────────────────────────────────────────────────
EMPTY_HEADING_RE = re.compile(r"<(h[1-6])[^>]*>\s*</\1>", re.IGNORECASE)
BR_CHAIN_RE = re.compile(r"(<br\s*/?>[\s\n]*){3,}", re.IGNORECASE)

# ─── check_jsonld_url_drift ──────────────────────────────────────────────────
ARTICLE_JSONLD_RE = re.compile(
    r'<script type="application/ld\+json">\s*(\{[^<]*?"@type"\s*:\s*"Article"[^<]*?\})\s*</script>'
)
NESTED_OBJ_RE = re.compile(r'"\w+"\s*:\s*\{[^{}]*\}')
JSONLD_URL_FIELD_RE = re.compile(r'"(url|mainEntityOfPage)"\s*:\s*"([^"]+)"')

# ─── check_meta_attribute_quotes ─────────────────────────────────────────────
META_CONTENT_RE = re.compile(
    r'<meta\s+(?:name|property)=["\'][^"\']+["\']\s+content="([^"]*)"', re.IGNORECASE
)

# ─── check_misrouted_form_endpoints ──────────────────────────────────────────
FOREIGN_EMAILS = {"ai.fukugyo.ken@gmail.com"}
OWNER_EMAIL = "307239t777@gmail.com"
FORMSPREE_RAW_RE = re.compile(r"https://formspree\.io/f/([^\"'>\s]+)", re.IGNORECASE)
MAILTO_EMAIL_RE = re.compile(
    r'(?:mailto:|href=["\'])([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
    re.IGNORECASE,
)

# ─── check_mobile_a11y_meta ──────────────────────────────────────────────────
THEME_COLOR_RE = re.compile(r'<meta name=["\']theme-color["\']', re.IGNORECASE)
HTML_DIR_RE = re.compile(r"<html[^>]+\bdir=", re.IGNORECASE)
REFERRER_META_RE_2 = re.compile(r'<meta name=["\']referrer["\']', re.IGNORECASE)

# ─── check_naked_bjj_app_cta ─────────────────────────────────────────────────
NAKED_CTA_RE = re.compile(
    r'<a\s[^>]*href=["\']https://bjj-app\.net["\']', re.IGNORECASE | re.DOTALL
)

# ─── check_no_duplicate_html_id ──────────────────────────────────────────────
HTML_ID_RE = re.compile(r'\bid="([^"]+)"')

# ─── check_no_fake_subscriber_claim ──────────────────────────────────────────
SUSPICIOUS_SUBS = [
    re.compile(r'\b\d,?000\+\s*(?:BJJ\s*)?(?:Practitioners|subscribers|members|users)\b', re.IGNORECASE),
    re.compile(r'\d,?000\s*人以上(?:の|登録)'),
    re.compile(r'\b\d,?000\+\s*Praticantes\b', re.IGNORECASE),
]

# ─── check_no_generic_h1 ─────────────────────────────────────────────────────
GENERIC_H1S = {
    "Master this Technique", "Master this technique", "Master This Technique",
    "学ぶべきポイント", "Domine esta Técnica", "Untitled", "Tutorial", "Master Technique",
}

# ─── check_og_image_url_encoding ─────────────────────────────────────────────
META_IMG_RE = re.compile(
    r'<meta\s+(?:property|name)=["\'](?:og:image|twitter:image)["\']\s+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)

# ─── check_og_locale_completeness ────────────────────────────────────────────
OG_LOCALE_RE = re.compile(r'<meta property=["\']og:locale["\'](?!:alternate)', re.IGNORECASE)
OG_LOCALE_ALT_RE = re.compile(r'<meta property=["\']og:locale:alternate["\']', re.IGNORECASE)

# ─── check_pwa_iframe_twitter ────────────────────────────────────────────────
YT_IFRAME_RE = re.compile(r"<iframe[^>]*?>", re.DOTALL)

# ─── check_seo_meta_completeness ─────────────────────────────────────────────
ROBOTS_LARGE_RE = re.compile(
    r'name=["\']robots["\'][^>]*content=["\'][^"\']*max-image-preview:large', re.IGNORECASE
)
OG_IMAGE_RE = re.compile(r'property=["\']og:image["\']', re.IGNORECASE)
OG_IMAGE_ALT_RE = re.compile(r'property=["\']og:image:alt["\']', re.IGNORECASE)

# ─── check_target_blank_security ─────────────────────────────────────────────
TARGET_BLANK_RE = re.compile(r'\btarget\s*=\s*["\']_blank["\']', re.IGNORECASE)
REL_ATTR_RE = re.compile(r'\brel\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)

# ─── check_thin_content_indexable ────────────────────────────────────────────
THIN_ALLOWLIST = {"index.html", "sparring-simulator.html", "404.html", "newsletter.html"}
MAIN_TAG_RE = re.compile(r"<main[^>]*>(.*?)</main>", re.DOTALL | re.IGNORECASE)

# ─── check_title_html_tags ───────────────────────────────────────────────────
INNER_TAG_RE = re.compile(r"<[a-zA-Z]")

# ─── check_zindex_hardcode_in_html ───────────────────────────────────────────
ZINDEX_RE = re.compile(r"z-index\s*:\s*(\d+)", re.IGNORECASE)
# value → required marker substring (None = unconditionally allowed)
ZINDEX_ALLOWED: dict[int, str | None] = {999: "z243-float", 9999: None, 2: None}

# ─── check_videoobject_when_yt_embed ─────────────────────────────────────────
YT_EMBED_RE = re.compile(r"youtube(?:-nocookie)?\.com/embed/", re.IGNORECASE)
VIDEO_OBJECT_RE = re.compile(r'"@type"\s*:\s*"VideoObject"')

# ─── check_lang_switcher_consistency ─────────────────────────────────────────
ALLOWED_SPECIAL_PAGES = {"sparring-simulator"}

# ─── check_twitter_image_sync ────────────────────────────────────────────────
OG_IMG_CONTENT_RE = re.compile(r'<meta property="og:image" content="([^"]+)"')
TW_IMG_CONTENT_RE = re.compile(r'<meta name="twitter:image" content="([^"]+)"')

# ─── Cross-page subprocess specs ─────────────────────────────────────────────
# Why subprocess: these checks need to compare data across multiple files or
# scan non-HTML files (sitemap.xml, .github/workflows), making inline logic impractical.
CROSS_PAGE_SPECS: list[tuple[str, list[str], dict[str, str]]] = [
    ("check_locale_parity.py",       ["--ci"], {}),
    ("detect_gha_regression.py",     ["--ci"], {}),
    ("scan_ja_english_mixing.py",    ["--ci"], {}),
    ("scan_pt_english_mixing.py",    ["--ci"], {"CI_THRESHOLD": "50"}),
    ("check_broken_links.py",        ["--ci"], {}),
    ("check_sitemap_drift.py",       ["--ci"], {}),
    ("check_hreflang_validity.py",   ["--ci"], {}),
    ("check_index_locale_parity.py", ["--ci"], {}),
    ("check_description_quality.py", ["--ci"], {}),
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _is_zindex_allowed(value: int, line: str, context: str) -> bool:
    if value not in ZINDEX_ALLOWED:
        return False
    marker = ZINDEX_ALLOWED[value]
    return marker is None or marker in line or marker in context


def _extract_headings(html: str) -> list[tuple[int, int]]:
    """Return list of (level, line_no) for visible headings (not inside script/style)."""
    headings: list[tuple[int, int]] = []
    for m in HEADING_LEVEL_RE.finditer(html):
        attrs = m.group(2)
        if HIDDEN_ATTR_RE.search(attrs):
            continue
        # Rough check: is this heading inside a script/style block?
        prefix = html[max(0, m.start() - 4000):m.start()].lower()
        if prefix.rfind("<script") > prefix.rfind("</script>"):
            continue
        if prefix.rfind("<style") > prefix.rfind("</style>"):
            continue
        level = int(m.group(1))
        line_no = html.count("\n", 0, m.start()) + 1
        headings.append((level, line_no))
    return headings


def _new_accumulator() -> dict:
    return {
        # per-page findings — each entry is (src, extra) or just src
        "title_html_tags":              [],  # (src, snippet)
        "h2_id_clobber":               [],  # src
        "heading_hierarchy":           [],  # (src, issues_str)
        "jsonld_validity":             [],  # (src, class_str)
        "breadcrumb_jsonld":           [],  # src
        "jsonld_url_drift":            [],  # (src, detail)
        "analytics_id_drift":          [],  # (src, errs_str)
        "login_cta_tracking":          [],  # (src, count)
        "no_meta_keywords":            [],  # src
        "twitter_image_sync":          [],  # (src, detail)
        "h1_brand_pollution":          [],  # (src, detail)
        "duplicate_bjj_prefix":        [],  # (src, count)
        "duplicate_faq_heading":       [],  # (src, count)
        "duplicate_related_techniques":[],  # (src, detail)
        "no_nested_p":                 [],  # src
        "html_quality_empty_heading":  [],  # src
        "html_quality_br_chain":       [],  # src
        "no_duplicate_html_id":        [],  # (src, dup_list_str)
        "naked_bjj_app_cta":           [],  # src
        "no_fake_subscriber_claim":    [],  # (src, match)
        "lang_switcher":               [],  # (src, reason)
        "brand_suffix_pollution":      [],  # src
        "broken_anchors":              [],  # (src, broken_list)
        "meta_attribute_quotes":       [],  # src
        "misrouted_form_endpoints":    [],  # (src, detail)
        "duplicate_word_in_title":     [],  # (src, detail)
        "og_image_url_encoding":       [],  # (src, url)
        "external_link_noreferrer":    [],  # (src, count)
        "target_blank_security":       [],  # (src, tag_snippet)
        "og_locale_missing":           [],  # src
        "og_locale_alts_missing":      [],  # src
        "mobile_a11y_theme_color":     [],  # src
        "mobile_a11y_html_dir":        [],  # src
        "mobile_a11y_referrer":        [],  # src
        "main_tag_present":            [],  # src
        "skip_link":                   [],  # src
        "pwa_manifest":                [],  # src
        "pwa_iframe_dim":              [],  # src
        "pwa_tw_creator":              [],  # src
        "videoobject_when_yt":         [],  # src
        "og_video_when_yt":            [],  # src
        "og_article_author":           [],  # src
        "og_article_pub_time":         [],  # src
        "apple_touch_icon_missing":    [],  # src
        "apple_touch_icon_non_png":    [],  # src
        "seo_meta_robots":             [],  # src
        "seo_meta_og_alt":             [],  # src
        "no_generic_h1":               [],  # (src, h1_text)
        "thin_content":                [],  # (src, wc)
        "zindex_hardcode":             [],  # (src, value, excerpt)
        "internal_link_relative":      [],  # (src, count)
        "ui_label_locale_drift":       [],  # (src, drifts_list)
        "breadcrumb_locale_drift":     [],  # (src, reason)
        "ja_body_english_dominant":    [],  # src  (WARNING only)
        "cta_text_locale_drift":       [],  # (src, detail)
        # cross-page dedup (accumulated during walk, evaluated after)
        "titles":    {l: defaultdict(list) for l in LANGS},  # lang → title → [src]
        "meta_descs":{l: defaultdict(list) for l in LANGS},  # lang → desc  → [src]
        # counters
        "total_pages":    0,
        "indexable_pages":0,
    }


# ─── Per-page check ───────────────────────────────────────────────────────────

def check_file(html: str, fp: Path, lang: str, acc: dict) -> None:
    src = f"{lang}/{fp.name}"
    head_short = html[:1500]
    head = html[:8000]

    is_noindex     = bool(NOINDEX_RE.search(head_short))
    is_redirect_stub = REDIRECT_MARKER in html[:1000]
    has_redirect_meta = bool(REDIRECT_META_RE.search(head[:2000]))

    acc["total_pages"] += 1

    # ── check_title_html_tags (runs on ALL pages, incl. noindex) ─────────────
    m_title = TITLE_RE.search(html)
    if m_title and INNER_TAG_RE.search(m_title.group(1)):
        acc["title_html_tags"].append((src, m_title.group(1).strip()[:90]))

    # ── Accumulate titles/meta_descs for cross-page dedup ────────────────────
    if not is_noindex:
        if m_title:
            title_text = re.sub(r"<[^>]+>", "", m_title.group(1)).strip()
            if title_text:
                acc["titles"][lang][title_text].append(src)
        m_desc = META_DESC_RE.search(html)
        if m_desc:
            desc = m_desc.group(1).strip()
            if len(desc) >= 30:
                acc["meta_descs"][lang][desc].append(src)

    # Skip remaining checks for noindex pages
    if is_noindex:
        return

    acc["indexable_pages"] += 1

    # ── check_h2_id_clobber ───────────────────────────────────────────────────
    if AUTO_TOC_CLOBBER_RE.search(html) and not AUTO_TOC_GUARD_RE.search(html):
        acc["h2_id_clobber"].append(src)

    # ── check_heading_hierarchy ───────────────────────────────────────────────
    # Skip pages that are redirect stubs (have redirect meta) — they have no real content
    if not has_redirect_meta:
        headings = _extract_headings(html)
        issues: list[str] = []
        h1_lines = [ln for lvl, ln in headings if lvl == 1]
        if len(h1_lines) == 0:
            issues.append("no-h1")
        elif len(h1_lines) > 1:
            issues.append(f"multi-h1@lines={h1_lines}")
        prev_lvl: int | None = None
        for lvl, ln in headings:
            if prev_lvl is not None and lvl > prev_lvl + 1:
                issues.append(f"skip-level h{prev_lvl}→h{lvl}@L{ln}")
            prev_lvl = lvl
        if issues:
            acc["heading_hierarchy"].append((src, "; ".join(issues)))

    # ── check_jsonld_validity ─────────────────────────────────────────────────
    for m in JSONLD_BLOCK_RE.finditer(html):
        raw = m.group(1).strip()
        if JSONLD_TEMPLATE_RE.search(raw):
            acc["jsonld_validity"].append((src, "template-residue"))
            break
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            acc["jsonld_validity"].append((src, "parse-error"))
            break
        if "@context" not in data:
            acc["jsonld_validity"].append((src, "missing-@context"))
            break
        if "@type" not in data and "@graph" not in data:
            acc["jsonld_validity"].append((src, "missing-@type/@graph"))
            break

    # ── check_breadcrumb_jsonld ───────────────────────────────────────────────
    if H1_RE.search(html) and "BreadcrumbList" not in html:
        acc["breadcrumb_jsonld"].append(src)

    # ── check_jsonld_url_drift ────────────────────────────────────────────────
    canon_m = CANONICAL_RE.search(html)
    if canon_m:
        canon = canon_m.group(1)
        for m in ARTICLE_JSONLD_RE.finditer(html):
            stripped = NESTED_OBJ_RE.sub("", m.group(1))
            for um in JSONLD_URL_FIELD_RE.finditer(stripped):
                field, value = um.group(1), um.group(2)
                if value.rstrip("/").removesuffix(".html") != canon.rstrip("/").removesuffix(".html"):
                    acc["jsonld_url_drift"].append(
                        (src, f"jsonld.{field}={value[:50]} ≠ canon={canon[:50]}")
                    )

    # ── check_analytics_id_drift ─────────────────────────────────────────────
    errs: list[str] = []
    for m in re.finditer(r"G-([A-Z0-9]{8,})", html):
        if m.group(0) != EXPECTED_GA4:
            errs.append(f"GA4: {m.group(0)} ≠ {EXPECTED_GA4}")
            break
    for m in re.finditer(r"GTM-([A-Z0-9]+)", html):
        if m.group(0) != EXPECTED_GTM:
            errs.append(f"GTM: {m.group(0)} ≠ {EXPECTED_GTM}")
            break
    if errs:
        acc["analytics_id_drift"].append((src, ", ".join(errs)))

    # ── check_login_cta_tracking ─────────────────────────────────────────────
    n_missing = sum(
        1 for m in re.finditer(r'href="(https://bjj-app\.net/login[^"]*)"', html)
        if "?ref=" not in m.group(1) and "page=" not in m.group(1)
    )
    if n_missing:
        acc["login_cta_tracking"].append((src, n_missing))

    # ── check_no_meta_keywords ───────────────────────────────────────────────
    if re.search(r'<meta name="keywords"', html):
        acc["no_meta_keywords"].append(src)

    # ── check_twitter_image_sync ─────────────────────────────────────────────
    og_m = OG_IMG_CONTENT_RE.search(html)
    tw_m = TW_IMG_CONTENT_RE.search(html)
    if og_m and tw_m and og_m.group(1) != tw_m.group(1):
        acc["twitter_image_sync"].append(
            (src, f"og={og_m.group(1)[:40]} tw={tw_m.group(1)[:40]}")
        )

    # ── check_h1_brand_pollution ─────────────────────────────────────────────
    h1_m = H1_RE.search(html)
    if h1_m and H1_BRAND_RE.search(h1_m.group(1)):
        acc["h1_brand_pollution"].append((src, f"h1='{h1_m.group(1)[:60]}'"))

    # ── check_duplicate_bjj_prefix ───────────────────────────────────────────
    dup_count = len(DUP_PREFIX_RE.findall(html))
    if dup_count:
        acc["duplicate_bjj_prefix"].append((src, dup_count))

    # ── check_duplicate_faq_heading ──────────────────────────────────────────
    faq_cnt = len(FAQ_H2_RE.findall(html))
    if faq_cnt > 1:
        acc["duplicate_faq_heading"].append((src, faq_cnt))

    # ── check_duplicate_related_techniques ───────────────────────────────────
    for pat in REL_TECH_PATTERNS[lang]:
        if len(pat.findall(html)) >= 2:
            acc["duplicate_related_techniques"].append((src, f"{len(pat.findall(html))}×"))
            break

    # ── check_no_nested_p ────────────────────────────────────────────────────
    if re.search(r"<p[^>]*>\s*<p[^>]*>", html, re.DOTALL):
        acc["no_nested_p"].append(src)

    # ── check_html_quality_minor ─────────────────────────────────────────────
    if EMPTY_HEADING_RE.search(html):
        acc["html_quality_empty_heading"].append(src)
    if BR_CHAIN_RE.search(html):
        acc["html_quality_br_chain"].append(src)

    # ── check_no_duplicate_html_id ───────────────────────────────────────────
    ids = HTML_ID_RE.findall(html)
    dups = [i for i, n in Counter(ids).items() if n > 1 and i.strip()]
    if dups:
        acc["no_duplicate_html_id"].append((src, str(dups[:3])))

    # ── check_naked_bjj_app_cta ──────────────────────────────────────────────
    cleaned = SCRIPT_RE.sub("", html)
    if NAKED_CTA_RE.search(cleaned):
        acc["naked_bjj_app_cta"].append(src)

    # ── check_no_fake_subscriber_claim ───────────────────────────────────────
    for pat in SUSPICIOUS_SUBS:
        m = pat.search(html)
        if m:
            acc["no_fake_subscriber_claim"].append((src, m.group(0)))
            break

    # ── check_lang_switcher_consistency ──────────────────────────────────────
    if fp.stem not in ALLOWED_SPECIAL_PAGES:
        if not ("🇺🇸 EN" in html or "🇯🇵 JA" in html or "🇧🇷 PT" in html):
            if re.search(r">English</a>", html) and re.search(r">日本語</a>", html):
                acc["lang_switcher"].append((src, "Pattern B"))
            elif "🇺🇸 English" in html or "🇯🇵 日本語" in html:
                acc["lang_switcher"].append((src, "Pattern C"))
            elif (
                '<header class="site-header">' in html
                or "lang-nav" in html
                or "lang-switcher" in html
            ):
                acc["lang_switcher"].append((src, "missing standard lang-switcher"))

    # ── check_brand_suffix_pollution ─────────────────────────────────────────
    if m_title and DOUBLE_BRAND_RE.search(m_title.group(1)):
        acc["brand_suffix_pollution"].append(src)
    else:
        og_t = OG_TITLE_RE.search(html)
        if og_t and DOUBLE_BRAND_RE.search(og_t.group(1)):
            acc["brand_suffix_pollution"].append(src)

    # ── check_broken_anchors ─────────────────────────────────────────────────
    anchor_ids = set(HTML_ID_RE.findall(html))
    broken_frags = [
        f"#{frag}"
        for frag in re.findall(r'href="#([^"]+)"', html)
        if frag not in anchor_ids
    ]
    if broken_frags:
        acc["broken_anchors"].append((src, broken_frags[:3]))

    # ── check_meta_attribute_quotes ──────────────────────────────────────────
    for m in META_CONTENT_RE.finditer(html):
        if '"' in m.group(1):
            acc["meta_attribute_quotes"].append(src)
            break

    # ── check_misrouted_form_endpoints ───────────────────────────────────────
    stripped = SCRIPT_RE.sub("", STYLE_RE.sub("", html))
    for m in FORMSPREE_RAW_RE.finditer(stripped):
        ep = m.group(1)
        if any(fe in ep for fe in FOREIGN_EMAILS):
            acc["misrouted_form_endpoints"].append((src, f"Formspree raw email: {ep[:60]}"))
    for m in MAILTO_EMAIL_RE.finditer(stripped):
        email = m.group(1)
        if email in FOREIGN_EMAILS:
            acc["misrouted_form_endpoints"].append((src, f"foreign email: {email}"))

    # ── check_duplicate_word_in_title ────────────────────────────────────────
    if m_title:
        title_text = re.sub(r"<[^>]+>", "", m_title.group(1)).strip()
        words = title_text.split()
        seen_words: set[str] = set()
        for w in words:
            wl = w.lower().strip(".,!?;:'\"")
            if wl and len(wl) > 2 and wl in seen_words:
                acc["duplicate_word_in_title"].append((src, f"dup='{w}'"))
                break
            seen_words.add(wl)

    # ── check_og_image_url_encoding ──────────────────────────────────────────
    for m in META_IMG_RE.finditer(html):
        if " " in m.group(1):
            acc["og_image_url_encoding"].append((src, m.group(1)[:80]))
            break

    # ── check_external_link_noreferrer ───────────────────────────────────────
    ext_noref_cnt = 0
    for m in A_TAG_RE.finditer(html):
        tag = m.group(0)
        if 'target="_blank"' not in tag:
            continue
        if not re.search(r'href="http', tag):
            continue
        rel_m = re.search(r'\brel="([^"]+)"', tag)
        if rel_m and "noopener" in rel_m.group(1) and "noreferrer" not in rel_m.group(1):
            ext_noref_cnt += 1
    if ext_noref_cnt:
        acc["external_link_noreferrer"].append((src, ext_noref_cnt))

    # ── check_target_blank_security ──────────────────────────────────────────
    cleaned2 = SCRIPT_RE.sub("", html)
    for m in re.finditer(r"<a\s+([^>]*?)>", cleaned2, re.IGNORECASE):
        attrs = m.group(1)
        if not TARGET_BLANK_RE.search(attrs):
            continue
        rel_m = REL_ATTR_RE.search(attrs)
        if not rel_m:
            acc["target_blank_security"].append((src, m.group(0)[:100]))
            break
        tokens = rel_m.group(1).lower().split()
        if "noopener" not in tokens and "noreferrer" not in tokens:
            acc["target_blank_security"].append((src, m.group(0)[:100]))
            break

    # ── check_og_locale_completeness ─────────────────────────────────────────
    if not OG_LOCALE_RE.search(head):
        acc["og_locale_missing"].append(src)
    if len(OG_LOCALE_ALT_RE.findall(head)) < 2:
        acc["og_locale_alts_missing"].append(src)

    # ── check_mobile_a11y_meta ───────────────────────────────────────────────
    if not THEME_COLOR_RE.search(head):
        acc["mobile_a11y_theme_color"].append(src)
    if not HTML_DIR_RE.search(head):
        acc["mobile_a11y_html_dir"].append(src)
    if not REFERRER_META_RE_2.search(head):
        acc["mobile_a11y_referrer"].append(src)

    # ── check_main_tag_present ───────────────────────────────────────────────
    if "<main" not in html:
        acc["main_tag_present"].append(src)

    # ── check_skip_link ──────────────────────────────────────────────────────
    if not re.search(r'class="skip-link"', html, re.IGNORECASE):
        acc["skip_link"].append(src)

    # ── check_pwa_iframe_twitter ─────────────────────────────────────────────
    if 'rel="manifest"' not in html:
        acc["pwa_manifest"].append(src)
    for m in YT_IFRAME_RE.finditer(html):
        tag = m.group(0)
        if "youtube" in tag and ("width=" not in tag or "height=" not in tag):
            acc["pwa_iframe_dim"].append(src)
            break
    if '<meta name="twitter:site"' in html and '<meta name="twitter:creator"' not in html:
        acc["pwa_tw_creator"].append(src)

    # ── check_videoobject_when_yt_embed ──────────────────────────────────────
    if YT_EMBED_RE.search(html) and not VIDEO_OBJECT_RE.search(html):
        acc["videoobject_when_yt"].append(src)

    # ── check_og_video_when_yt ───────────────────────────────────────────────
    if "youtube.com/embed" in html and 'property="og:video"' not in html:
        acc["og_video_when_yt"].append(src)
    if 'og:type" content="article"' in html:
        if 'property="article:author"' not in html:
            acc["og_article_author"].append(src)
        if '"datePublished"' in html and 'property="article:published_time"' not in html:
            acc["og_article_pub_time"].append(src)

    # ── check_apple_touch_icon_png ───────────────────────────────────────────
    if not has_redirect_meta:
        m = re.search(r'<link rel="apple-touch-icon"[^>]+href="([^"]+)"', html, re.IGNORECASE)
        if not m:
            acc["apple_touch_icon_missing"].append(src)
        elif not m.group(1).lower().endswith(".png"):
            acc["apple_touch_icon_non_png"].append((src, m.group(1)[-40:]))

    # ── check_seo_meta_completeness ──────────────────────────────────────────
    if not is_redirect_stub:
        if not ROBOTS_LARGE_RE.search(head):
            acc["seo_meta_robots"].append(src)
        if OG_IMAGE_RE.search(head) and not OG_IMAGE_ALT_RE.search(head):
            acc["seo_meta_og_alt"].append(src)

    # ── check_no_generic_h1 ──────────────────────────────────────────────────
    if h1_m and h1_m.group(1).strip() in GENERIC_H1S:
        acc["no_generic_h1"].append((src, h1_m.group(1).strip()))

    # ── check_thin_content_indexable (EN+PT only) ────────────────────────────
    if lang in ("en", "pt") and fp.name not in THIN_ALLOWLIST:
        main_m = MAIN_TAG_RE.search(html)
        if main_m:
            body = SCRIPT_RE.sub("", STYLE_RE.sub("", main_m.group(1)))
            wc = len(re.sub(r"\s+", " ", TAG_RE.sub(" ", body)).strip().split())
            if wc < 100:
                acc["thin_content"].append((src, wc))

    # ── check_zindex_hardcode_in_html ────────────────────────────────────────
    for m in ZINDEX_RE.finditer(html):
        value = int(m.group(1))
        ls = html.rfind("\n", 0, m.start()) + 1
        le = html.find("\n", m.end())
        if le == -1:
            le = len(html)
        line = html[ls:le]
        ctx = html[max(0, m.start() - 200):min(len(html), m.end() + 200)]
        if not _is_zindex_allowed(value, line, ctx):
            acc["zindex_hardcode"].append((src, value, line.strip()[:100]))

    # ── check_internal_link_relative ─────────────────────────────────────────
    if not is_redirect_stub:
        pat = re.compile(
            r'href="(' + re.escape(SITE) + r'/' + lang + r'/[^"]+\.html)"'
        )
        cnt = sum(1 for m in pat.finditer(html) if "?" not in m.group(1))
        if cnt:
            acc["internal_link_relative"].append((src, cnt))

    # ─── JA/PT only ──────────────────────────────────────────────────────────

    # ── check_ui_label_locale_drift ──────────────────────────────────────────
    if lang in ("ja", "pt"):
        drifts: list[str] = []
        for m in re.finditer(r'<span class="badge">([^<]+)</span>', html):
            if m.group(1).strip() in EN_CATEGORIES:
                drifts.append(f"badge='{m.group(1)}'")
        for m in re.finditer(r'<span class="belt belt-[a-z]+">([^<]+)</span>', html):
            if m.group(1).strip() in EN_BELTS:
                drifts.append(f"belt='{m.group(1)}'")
        for m in re.finditer(r'<span class="diff-belt"[^>]*>([^<]+)</span>', html):
            if m.group(1).strip().title() in EN_BELTS:
                drifts.append(f"diff-belt='{m.group(1)}'")
        for m in re.finditer(r'<span class="diff-label">([^<]+)</span>', html):
            if m.group(1).strip() in EN_DIFFICULTIES:
                drifts.append(f"diff-label='{m.group(1)}'")
        for m in re.finditer(r'<span class="belt-tag"[^>]*>([^<]+)</span>', html):
            stripped = re.sub(r"^[^\w]+\s*", "", m.group(1).strip())
            if stripped in EN_BELT_FULL:
                drifts.append(f"belt-tag='{m.group(1).strip()}'")
        if drifts:
            acc["ui_label_locale_drift"].append((src, drifts))

    # ── check_breadcrumb_locale_drift ────────────────────────────────────────
    if lang in ("ja", "pt"):
        bc_m = BREADCRUMB_DIV_RE.search(html)
        if bc_m:
            crumb = bc_m.group(1)
            last_m = BREADCRUMB_LAST_RE.search(crumb.replace("\n", " "))
            if last_m:
                last_text = re.sub(r"<[^>]+>", "", last_m.group(1)).strip()
                if last_text and last_text not in BJJ_PROPER_NOUNS:
                    if re.search(r"\|\s*BJJ\s*Wiki", last_text, re.IGNORECASE):
                        acc["breadcrumb_locale_drift"].append(
                            (src, f"brand suffix leaked: '{last_text[:60]}'")
                        )
                    elif lang == "ja":
                        if re.search(r"[A-Za-z]", last_text) and not re.search(
                            r"[ぁ-んァ-ヶー一-龯]", last_text
                        ):
                            acc["breadcrumb_locale_drift"].append(
                                (src, f"EN-only crumb: '{last_text[:60]}'")
                            )
                    elif lang == "pt":
                        text_lower = last_text.lower()
                        if (
                            not any(mk in text_lower for mk in PT_MARKERS)
                            and len(last_text) > 20
                        ):
                            acc["breadcrumb_locale_drift"].append(
                                (src, f"likely EN-only crumb: '{last_text[:60]}'")
                            )

    # ── check_ja_body_english_dominant (WARNING only — --strict equiv) ────────
    if lang == "ja":
        body_text = re.sub(r"<[^>]+>", " ", SCRIPT_RE.sub("", STYLE_RE.sub("", html)))
        en_c = sum(1 for c in body_text if c.isascii() and c.isalpha())
        tot_c = sum(1 for c in body_text if c.isalpha())
        if tot_c > 0 and en_c / tot_c > 0.60:
            acc["ja_body_english_dominant"].append(src)

    # ── check_cta_text_locale_drift ──────────────────────────────────────────
    if lang in ("ja", "pt"):
        for cta_m in re.finditer(r"<(?:button|a)\b[^>]*>([^<]{3,40})</", html, re.IGNORECASE):
            text = cta_m.group(1).strip()
            for pat in EN_CTA_PATTERNS:
                if pat.search(text):
                    acc["cta_text_locale_drift"].append((src, f"EN CTA: '{text[:40]}'"))
                    break


# ─── Root-file scan (check_zindex_hardcode also covers root HTML) ─────────────

def scan_root_files(acc: dict) -> None:
    for fp in sorted(REPO_ROOT.glob("*.html")):
        try:
            html = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        src = fp.name
        for m in ZINDEX_RE.finditer(html):
            value = int(m.group(1))
            ls = html.rfind("\n", 0, m.start()) + 1
            le = html.find("\n", m.end())
            if le == -1:
                le = len(html)
            line = html[ls:le]
            ctx = html[max(0, m.start() - 200):min(len(html), m.end() + 200)]
            if not _is_zindex_allowed(value, line, ctx):
                acc["zindex_hardcode"].append((src, value, line.strip()[:100]))


# ─── Cross-page dedup report ──────────────────────────────────────────────────

def _report_dedup(acc: dict, ci_mode: bool) -> int:
    """Report duplicate titles and meta descriptions. Returns failure count."""
    failures = 0

    # Duplicate titles
    total_dup_groups = 0
    total_dup_pages = 0
    for lang in LANGS:
        dups = {t: p for t, p in acc["titles"][lang].items() if len(p) > 1}
        total_dup_groups += len(dups)
        total_dup_pages += sum(len(p) for p in dups.values())
        print(f"  {lang}: {len(dups)} duplicate title groups "
              f"({sum(len(p) for p in dups.values())} pages)")
        for t, paths in list(dups.items())[:3]:
            print(f"    « {t[:60]} »")
            for p in paths[:3]:
                print(f"       {p}")
    if total_dup_groups == 0:
        print("✅ No duplicate <title> within any locale.")
    else:
        print(f"🔴 check_duplicate_titles: {total_dup_groups} groups ({total_dup_pages} pages)")
        failures += 1

    print()

    # Duplicate meta descriptions
    total_desc_groups = 0
    total_desc_pages = 0
    for lang in LANGS:
        dups = {d: p for d, p in acc["meta_descs"][lang].items() if len(p) > 1}
        total_desc_groups += len(dups)
        total_desc_pages += sum(len(p) for p in dups.values())
        print(f"  {lang}: {len(dups)} duplicate meta-desc groups "
              f"({sum(len(p) for p in dups.values())} pages)")
        for d, paths in list(dups.items())[:3]:
            print(f"    « {d[:80]} »")
            for p in paths[:3]:
                print(f"       {p}")
    if total_desc_groups == 0:
        print("✅ No duplicate <meta description> within any locale.")
    else:
        print(f"🔴 check_duplicate_meta_desc: {total_desc_groups} groups ({total_desc_pages} pages)")
        failures += 1

    return failures


# ─── Per-page results report ──────────────────────────────────────────────────

def _report_per_page(acc: dict) -> int:
    """Print per-page results. Returns number of failed checks."""
    failures = 0

    def _section(key: str, label: str, items: list, ci_always: bool = True) -> None:
        nonlocal failures
        n = len(items)
        if n == 0:
            print(f"✅ {label}: 0")
        else:
            print(f"❌ {label}: {n}")
            for item in items[:6]:
                if isinstance(item, tuple):
                    print(f"   {item[0]}: {item[1]}")
                else:
                    print(f"   {item}")
            if n > 6:
                print(f"   ... and {n - 6} more")
            if ci_always:
                failures += 1

    print(f"\n📊 Total pages: {acc['total_pages']:,}  |  Indexable: {acc['indexable_pages']:,}")
    print()

    # ── Sorted sections (roughly matching original script order) ─────────────

    _section("title_html_tags",
             "<title> with embedded HTML tags", acc["title_html_tags"])

    _section("h2_id_clobber",
             "Pages with auto-toc h2 id clobber (no guard)", acc["h2_id_clobber"])

    _section("heading_hierarchy",
             "Pages with heading hierarchy issues (no-h1/multi-h1/skip-level)",
             acc["heading_hierarchy"])

    _section("jsonld_validity",
             "Pages with JSON-LD validity issues", acc["jsonld_validity"])

    _section("breadcrumb_jsonld",
             "Pages missing BreadcrumbList JSON-LD", acc["breadcrumb_jsonld"])

    _section("jsonld_url_drift",
             "Pages with JSON-LD url drift vs canonical", acc["jsonld_url_drift"])

    _section("ui_label_locale_drift",
             "JA/PT pages with EN UI label drift", acc["ui_label_locale_drift"])

    _section("lang_switcher",
             "Pages with lang-switcher format drift", acc["lang_switcher"])

    _section("breadcrumb_locale_drift",
             "Pages with EN-residue breadcrumb in JA/PT", acc["breadcrumb_locale_drift"])

    _section("h1_brand_pollution",
             "Pages with h1 brand pollution", acc["h1_brand_pollution"])

    _section("duplicate_bjj_prefix",
             "Pages with duplicate【BJJ】prefix", acc["duplicate_bjj_prefix"])

    _section("external_link_noreferrer",
             "Pages with noopener-only external link (no noreferrer)",
             acc["external_link_noreferrer"])

    _section("duplicate_faq_heading",
             "Pages with duplicate FAQ heading", acc["duplicate_faq_heading"])

    _section("analytics_id_drift",
             "Pages with analytics ID drift", acc["analytics_id_drift"])

    _section("login_cta_tracking",
             "Pages with /login CTA missing ?ref=wiki tracking",
             acc["login_cta_tracking"])

    _section("target_blank_security",
             "<a target=_blank> missing rel=noopener/noreferrer",
             acc["target_blank_security"])

    _section("brand_suffix_pollution",
             "Pages with double brand suffix in title", acc["brand_suffix_pollution"])

    _section("naked_bjj_app_cta",
             'Naked `href="https://bjj-app.net"` (no funnel tracking)',
             acc["naked_bjj_app_cta"])

    _section("broken_anchors",
             "Pages with broken #fragment anchors", acc["broken_anchors"])

    _section("meta_attribute_quotes",
             "Pages with unescaped \" in meta description",
             acc["meta_attribute_quotes"])

    _section("misrouted_form_endpoints",
             "Pages with misrouted form endpoints/emails",
             acc["misrouted_form_endpoints"])

    _section("duplicate_word_in_title",
             "Pages with duplicate words in title", acc["duplicate_word_in_title"])

    _section("no_meta_keywords",
             "Pages with obsolete <meta name='keywords'>", acc["no_meta_keywords"])

    _section("twitter_image_sync",
             "Pages with twitter:image ≠ og:image drift", acc["twitter_image_sync"])

    _section("og_image_url_encoding",
             "og:image / twitter:image with unencoded spaces",
             acc["og_image_url_encoding"])

    _section("duplicate_related_techniques",
             "Pages with duplicate Related Techniques h2",
             acc["duplicate_related_techniques"])

    _section("no_nested_p",
             "Pages with nested <p><p>", acc["no_nested_p"])

    _section("html_quality_empty_heading",
             "Pages with empty heading tags", acc["html_quality_empty_heading"])

    _section("html_quality_br_chain",
             "Pages with 3+ consecutive <br> chains", acc["html_quality_br_chain"])

    _section("og_locale_missing",
             "Pages missing og:locale", acc["og_locale_missing"])

    _section("og_locale_alts_missing",
             "Pages missing 2× og:locale:alternate", acc["og_locale_alts_missing"])

    _section("mobile_a11y_theme_color",
             "Pages missing theme-color meta", acc["mobile_a11y_theme_color"])

    _section("mobile_a11y_html_dir",
             "Pages missing <html dir=...>", acc["mobile_a11y_html_dir"])

    _section("mobile_a11y_referrer",
             "Pages missing referrer meta", acc["mobile_a11y_referrer"])

    _section("main_tag_present",
             "Pages missing <main> landmark", acc["main_tag_present"])

    _section("videoobject_when_yt",
             "Pages with YouTube embed but no VideoObject schema",
             acc["videoobject_when_yt"])

    _section("apple_touch_icon_missing",
             "Pages missing apple-touch-icon", acc["apple_touch_icon_missing"])

    non_png = acc["apple_touch_icon_non_png"]
    if isinstance(non_png[0], tuple) if non_png else False:
        _section("apple_touch_icon_non_png",
                 "Pages with non-PNG apple-touch-icon", non_png)
    else:
        _section("apple_touch_icon_non_png",
                 "Pages with non-PNG apple-touch-icon", non_png)

    _section("skip_link",
             "Pages missing skip-to-content link (WCAG 2.4.1)", acc["skip_link"])

    _section("pwa_manifest",
             "Pages missing <link rel=manifest>", acc["pwa_manifest"])

    _section("pwa_iframe_dim",
             "Pages with YouTube iframe missing width/height", acc["pwa_iframe_dim"])

    _section("pwa_tw_creator",
             "Pages missing twitter:creator", acc["pwa_tw_creator"])

    _section("no_fake_subscriber_claim",
             "Pages with unverified subscriber/user count claims",
             acc["no_fake_subscriber_claim"])

    _section("og_video_when_yt",
             "Pages with YouTube embed but missing og:video", acc["og_video_when_yt"])

    _section("og_article_author",
             "Pages with article type but missing article:author",
             acc["og_article_author"])

    _section("no_generic_h1",
             "Pages with generic placeholder <h1>", acc["no_generic_h1"])

    _section("thin_content",
             "Indexable EN+PT pages with <100 words of <main> content",
             acc["thin_content"])

    _section("no_duplicate_html_id",
             "Pages with duplicate HTML id attributes", acc["no_duplicate_html_id"])

    _section("zindex_hardcode",
             "Non-allowed z-index hardcodes in HTML", acc["zindex_hardcode"])

    _section("seo_meta_robots",
             "Indexable pages missing max-image-preview:large robots",
             acc["seo_meta_robots"])

    _section("seo_meta_og_alt",
             "Pages with og:image but missing og:image:alt", acc["seo_meta_og_alt"])

    _section("internal_link_relative",
             "Pages with absolute internal-link URL in <a>",
             acc["internal_link_relative"])

    _section("cta_text_locale_drift",
             "JA/PT pages with EN CTA text drift", acc["cta_text_locale_drift"])

    # WARNING only (not counted as failure)
    n_ja_en = len(acc["ja_body_english_dominant"])
    if n_ja_en:
        print(f"⚠️  check_ja_body_english_dominant (WARNING only): {n_ja_en} pages")
    else:
        print(f"✅ check_ja_body_english_dominant: 0")

    return failures


# ─── Cross-page subprocess runner ────────────────────────────────────────────

def _run_cross_page(ci_mode: bool) -> tuple[int, list[str]]:
    """Run cross-page checks in parallel. Returns (failure_count, failed_scripts)."""

    def run_one(spec: tuple) -> dict:
        script, args, extra_env = spec
        fp = SCRIPTS_DIR / script
        env = {**os.environ, **extra_env}
        result = subprocess.run(
            [sys.executable, str(fp)] + args,
            capture_output=True, text=True,
            cwd=str(REPO_ROOT), env=env,
        )
        return {
            "script": script,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    workers = min(len(CROSS_PAGE_SPECS), 9)
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(run_one, spec): spec[0] for spec in CROSS_PAGE_SPECS}
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda r: r["script"])

    failed: list[str] = []
    for r in results:
        if r["stdout"]:
            print(r["stdout"], end="")
        if r["stderr"]:
            print(r["stderr"], end="", file=sys.stderr)
        if r["returncode"] != 0:
            failed.append(r["script"])

    return len(failed), failed


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    ci_mode = "--ci" in sys.argv

    acc = _new_accumulator()

    # ── Single-pass file walk ─────────────────────────────────────────────────
    for lang in LANGS:
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            try:
                html = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            check_file(html, fp, lang, acc)

    # Also scan root HTML files for zindex check
    scan_root_files(acc)

    # ── Per-page results ──────────────────────────────────────────────────────
    print("=" * 70)
    print("PER-PAGE LINT RESULTS (single-pass)")
    print("=" * 70)
    per_page_failures = _report_per_page(acc)

    # ── Cross-page dedup (titles & meta descriptions) ─────────────────────────
    print()
    print("=" * 70)
    print("DUPLICATE TITLE / META DESCRIPTION")
    print("=" * 70)
    dedup_failures = _report_dedup(acc, ci_mode)

    # ── Cross-page subprocess checks ──────────────────────────────────────────
    print()
    print("=" * 70)
    print("CROSS-PAGE CHECKS (parallel subprocesses)")
    print("=" * 70)
    cross_page_failures, cross_page_failed = _run_cross_page(ci_mode)

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print("=" * 70)
    total_failures = per_page_failures + dedup_failures + cross_page_failures
    if total_failures == 0:
        print(f"✅ All lints passed.")
        print("   Safe to commit.")
    else:
        print(f"🔴 {total_failures} lint check(s) failed.")
        if cross_page_failed:
            print("   Failed cross-page scripts:")
            for s in cross_page_failed:
                print(f"     ✗ {s}")

    if ci_mode:
        return 1 if total_failures > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
