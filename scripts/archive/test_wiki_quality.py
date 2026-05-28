#!/usr/bin/env python3
"""
BJJ Wiki Quality Test Suite
Usage: python3 scripts/test_wiki_quality.py
       python3 -m pytest scripts/test_wiki_quality.py -v  (pytest optional)

Tests validate the generated HTML files without external dependencies.

Test classes
────────────
  TestSitemapConsistency    – sitemap.xml URL count and EN/JA/PT file parity
  TestHreflangTags          – hreflang attribute completeness
  TestHtmlLangAttribute     – html[lang] prefix matches directory
  TestMetaTags              – <title> and meta description present
  TestNoMojibake            – no Latin-1 garble in UTF-8 pages
  TestAmazonAffiliateLinks  – affiliate tag and no unencoded spaces
  TestCtaBanner             – BJJ App CTA banner in newer pages
  TestNoHttpLinks           – all external links use HTTPS
  TestDuplicateTitles       – JA titles differ from EN
  TestYouTubeButton         – .yt-search-btn anchor present in content pages
  TestSearchJsonConsistency – search.json valid, slugs cover ≥95% of EN pages
  TestIndexHtmlClean        – index.html has no orphaned Batch/tech-card blocks
"""

import os
import re
import glob
import json
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

# ── Paths ──────────────────────────────────────────────────────────────────────
WIKI_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EN_DIR  = os.path.join(WIKI_ROOT, "en")
JA_DIR  = os.path.join(WIKI_ROOT, "ja")
PT_DIR  = os.path.join(WIKI_ROOT, "pt")
SITEMAP = os.path.join(WIKI_ROOT, "sitemap.xml")

LANGS = {"en": EN_DIR, "ja": JA_DIR, "pt": PT_DIR}
BASE_URL = "https://wiki.bjj-app.net"
# AFFILIATE_TAG removed — CLAUDE.md: アフィリリンク完全禁止
AFFILIATE_TAG = "bjj06-22"  # kept for assertNotIn test below
APP_URL = "bjj-app.net"

# How many pages to sample per test (keep fast; full scan optional)
SAMPLE_SIZE = 50


# ── Helpers ────────────────────────────────────────────────────────────────────

def all_html_files(lang_dir: str) -> list[str]:
    return sorted(glob.glob(os.path.join(lang_dir, "*.html")))


def sampled(files: list[str], n: int = SAMPLE_SIZE) -> list[str]:
    """Deterministic sample: every N-th file."""
    if len(files) <= n:
        return files
    step = max(1, len(files) // n)
    return files[::step][:n]


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


class MetaTagParser(HTMLParser):
    """Minimal HTML parser that collects meta[name=description] and title."""
    def __init__(self):
        super().__init__()
        self.title = ""
        self._in_title = False
        self.description = ""
        self.lang = ""
        self.hreflang = set()

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "html":
            self.lang = d.get("lang", "")
        if tag == "title":
            self._in_title = True
        if tag == "meta" and d.get("name", "").lower() == "description":
            self.description = d.get("content", "")
        if tag == "link" and d.get("rel") == "alternate":
            hl = d.get("hreflang", "")
            if hl:
                self.hreflang.add(hl)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def parse_meta(path: str) -> MetaTagParser:
    p = MetaTagParser()
    p.feed(read(path))
    return p


# ── Test Classes ───────────────────────────────────────────────────────────────

class TestSitemapConsistency(unittest.TestCase):
    """Sitemap URL count should be close to actual file count."""

    def _count_sitemap_urls(self) -> int:
        tree = ET.parse(SITEMAP)
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        return len(root.findall("sm:url", ns))

    def test_sitemap_file_exists(self):
        self.assertTrue(os.path.exists(SITEMAP), "sitemap.xml が存在しない")

    def test_sitemap_has_urls(self):
        count = self._count_sitemap_urls()
        self.assertGreater(count, 1000, f"sitemap URLが少なすぎる: {count}")

    def test_sitemap_en_pages_covered(self):
        en_files = all_html_files(EN_DIR)
        sitemap_text = read(SITEMAP)
        # At least 90% of EN files should be in the sitemap
        covered = sum(1 for f in en_files
                      if os.path.basename(f) in sitemap_text)
        coverage = covered / len(en_files) if en_files else 0
        self.assertGreater(coverage, 0.9,
            f"EN sitemap カバレッジ低: {covered}/{len(en_files)} = {coverage:.1%}")

    def test_three_langs_equal_file_count(self):
        counts = {lang: len(all_html_files(d)) for lang, d in LANGS.items()}
        self.assertEqual(counts["en"], counts["ja"],
            f"EN/JA ファイル数不一致: {counts}")
        self.assertEqual(counts["en"], counts["pt"],
            f"EN/PT ファイル数不一致: {counts}")


class TestHreflangTags(unittest.TestCase):
    """Pages that have hreflang must include all 3 languages (no partial sets)."""

    REQUIRED_HREFLANG = {"en", "ja", "pt", "x-default"}

    def _check_lang(self, lang: str, lang_dir: str):
        files = sampled(all_html_files(lang_dir))
        failures = []
        for path in files:
            m = parse_meta(path)
            # Skip pages with NO hreflang at all (older format pages)
            if not m.hreflang:
                continue
            # Pages that have SOME hreflang must have ALL required ones
            missing = self.REQUIRED_HREFLANG - m.hreflang
            if missing:
                failures.append(f"{os.path.basename(path)}: hreflang 不足 {missing}")
        if failures:
            self.fail(f"[{lang}] 不完全なhreflang ({len(failures)}/{len(files)}):\n" +
                      "\n".join(failures[:5]))

    def _coverage_check(self, lang: str, lang_dir: str):
        """At least 70% of pages should have hreflang (trend tracking)."""
        files = all_html_files(lang_dir)
        with_hreflang = sum(1 for f in files if parse_meta(f).hreflang)
        coverage = with_hreflang / len(files) if files else 0
        self.assertGreater(coverage, 0.70,
            f"[{lang}] hreflang カバレッジ低: {with_hreflang}/{len(files)} = {coverage:.1%}")

    def test_en_hreflang(self): self._check_lang("en", EN_DIR)
    def test_ja_hreflang(self): self._check_lang("ja", JA_DIR)
    def test_pt_hreflang(self): self._check_lang("pt", PT_DIR)
    def test_en_hreflang_coverage(self): self._coverage_check("en", EN_DIR)
    def test_ja_hreflang_coverage(self): self._coverage_check("ja", JA_DIR)
    def test_pt_hreflang_coverage(self): self._coverage_check("pt", PT_DIR)


class TestHtmlLangAttribute(unittest.TestCase):
    """html[lang] must start with the directory language prefix."""

    EXPECTED_PREFIX = {"en": "en", "ja": "ja", "pt": "pt"}

    def _check_lang(self, lang: str, lang_dir: str):
        prefix = self.EXPECTED_PREFIX[lang]
        files = sampled(all_html_files(lang_dir))
        failures = []
        for path in files:
            m = parse_meta(path)
            if not m.lang.startswith(prefix):
                failures.append(
                    f"{os.path.basename(path)}: lang='{m.lang}' (期待プレフィックス: '{prefix}')")
        if failures:
            self.fail(f"[{lang}] html[lang] 不正 ({len(failures)}/{len(files)}):\n" +
                      "\n".join(failures[:5]))

    def test_en_lang_attr(self): self._check_lang("en", EN_DIR)
    def test_ja_lang_attr(self): self._check_lang("ja", JA_DIR)
    def test_pt_lang_attr(self): self._check_lang("pt", PT_DIR)


class TestMetaTags(unittest.TestCase):
    """Every page should have a non-empty <title> and meta description."""

    def _check_lang(self, lang: str, lang_dir: str):
        files = sampled(all_html_files(lang_dir))
        missing_title = []
        missing_desc = []
        for path in files:
            m = parse_meta(path)
            name = os.path.basename(path)
            if not m.title.strip():
                missing_title.append(name)
            if not m.description.strip():
                missing_desc.append(name)
        if missing_title:
            self.fail(f"[{lang}] title 欠落: {missing_title[:5]}")
        if missing_desc:
            self.fail(f"[{lang}] meta description 欠落: {missing_desc[:5]}")

    def test_en_meta(self): self._check_lang("en", EN_DIR)
    def test_ja_meta(self): self._check_lang("ja", JA_DIR)
    def test_pt_meta(self): self._check_lang("pt", PT_DIR)


class TestNoMojibake(unittest.TestCase):
    """Check for common UTF-8 → Latin-1 mojibake patterns."""

    # Specific garbled byte sequences (no character ranges)
    PATTERNS = [
        "Ã©",   # é
        "Ã¨",   # è
        "Ã£",   # ã
        "â€™",  # right single quotation mark
        "â€œ",  # left double quotation mark
        "â€",   # generic double-byte start
        "Â ",   # non-breaking space garbled
        "Ã\xaf",  # ï garbled
    ]

    def _check_lang(self, lang: str, lang_dir: str):
        files = sampled(all_html_files(lang_dir))
        hits = []
        for path in files:
            content = read(path)
            if any(p in content for p in self.PATTERNS):
                matched = [p for p in self.PATTERNS if p in content]
                hits.append(f"{os.path.basename(path)}: {matched[:2]}")
        if hits:
            self.fail(f"[{lang}] mojibake 検出 ({len(hits)}/{len(files)}): {hits[:5]}")

    def test_en_mojibake(self): self._check_lang("en", EN_DIR)
    def test_ja_mojibake(self): self._check_lang("ja", JA_DIR)
    def test_pt_mojibake(self): self._check_lang("pt", PT_DIR)


class TestAmazonAffiliateLinks(unittest.TestCase):
    """Amazon links must use affiliate tag and have no unencoded spaces."""

    def test_no_unencoded_spaces_in_amazon_urls(self):
        """amazon.com/s?k=... must not contain literal spaces"""
        pattern = re.compile(r'amazon\.[a-z.]+/s\?k=[^"]*? [^"]*?"')
        failures = []
        for lang, lang_dir in LANGS.items():
            for path in all_html_files(lang_dir):
                content = read(path)
                if pattern.search(content):
                    failures.append(f"{lang}/{os.path.basename(path)}")
        if failures:
            self.fail(f"Amazon URLにスペース混入: {failures[:10]}")

    def test_gear_pages_have_affiliate_tag(self):
        """Gear pages (rash guard / knee pads / ear guards) must have affiliate tag."""
        gear_slugs = ["best-bjj-rash-guard", "best-bjj-knee-pads", "best-bjj-ear-guards"]
        for lang, lang_dir in LANGS.items():
            for slug in gear_slugs:
                path = os.path.join(lang_dir, f"{slug}.html")
                if not os.path.exists(path):
                    continue  # page may not exist in all langs
                content = read(path)
                # CLAUDE.md: アフィリリンク完全禁止 — 存在しないことを検証
                self.assertNotIn(AFFILIATE_TAG, content,
                    f"{lang}/{slug}.html にアフィリエイトタグ {AFFILIATE_TAG} が残存")


class TestCtaBanner(unittest.TestCase):
    """Pages generated by current template should include BJJ App CTA."""

    # Only newer batch pages have the CTA; check a known set
    KNOWN_CTA_PAGES = [
        "en/bjj-guard-sweeps-masterclass.html",
        "en/bjj-submission-chain-attacks.html",
        "ja/bjj-guard-sweeps-masterclass.html",
        "pt/bjj-guard-sweeps-masterclass.html",
    ]

    def test_known_pages_have_cta(self):
        for rel_path in self.KNOWN_CTA_PAGES:
            path = os.path.join(WIKI_ROOT, rel_path)
            if not os.path.exists(path):
                continue
            content = read(path)
            self.assertIn(APP_URL, content,
                f"{rel_path} に BJJ App CTA バナーなし")


class TestNoHttpLinks(unittest.TestCase):
    """All links should use HTTPS, not HTTP."""

    def test_no_http_external_links(self):
        """Links to external sites should not use plain http://"""
        # Allow localhost and specific known-safe http patterns
        pattern = re.compile(r'href="http://(?!localhost)[^"]{10,}"')
        files = sampled(all_html_files(EN_DIR))
        hits = []
        for path in files:
            content = read(path)
            if pattern.search(content):
                hits.append(os.path.basename(path))
        if hits:
            self.fail(
                f"HTTP(非HTTPS)リンク検出 ({len(hits)}/{len(files)}): {hits[:5]}")


class TestDuplicateTitles(unittest.TestCase):
    """Pages in different languages should NOT have identical <title> values."""

    def test_ja_titles_differ_from_en(self):
        en_titles = {}
        for path in sampled(all_html_files(EN_DIR)):
            en_titles[os.path.basename(path)] = parse_meta(path).title.strip()

        duplicates = []
        for path in sampled(all_html_files(JA_DIR)):
            name = os.path.basename(path)
            ja_title = parse_meta(path).title.strip()
            en_title = en_titles.get(name, "")
            if en_title and ja_title == en_title:
                duplicates.append(name)

        if duplicates:
            self.fail(
                f"JA ページのタイトルが EN と同一 ({len(duplicates)}件): "
                f"{duplicates[:5]}")


class TestNoYouTubeButton(unittest.TestCase):
    """
    YouTube buttons were intentionally removed (Day 4fn).
    Verify no yt-search-btn anchors remain in content pages.
    """

    YT_ANCHOR_RE = re.compile(r'<a[^>]+yt-search-btn')

    def _content_files(self, lang_dir: str) -> list[str]:
        return sorted(
            f for f in all_html_files(lang_dir)
            if os.path.basename(f) != "index.html"
        )

    def _check_no_buttons(self, lang: str, lang_dir: str):
        files = sampled(self._content_files(lang_dir))
        has_button = [f for f in files if self.YT_ANCHOR_RE.search(read(f))]
        self.assertEqual(
            len(has_button), 0,
            f"[{lang}] {len(has_button)} pages still have yt-search-btn anchors"
        )

    def test_en_no_youtube_buttons(self):
        self._check_no_buttons("en", EN_DIR)

    def test_ja_no_youtube_buttons(self):
        self._check_no_buttons("ja", JA_DIR)

    def test_pt_no_youtube_buttons(self):
        self._check_no_buttons("pt", PT_DIR)


class TestSearchJsonConsistency(unittest.TestCase):
    """
    Each language directory contains a search.json that powers the client-side
    search widget.  We verify:

      1. The file exists and is valid JSON.
      2. Every entry has the required fields: s (slug), t (title), d (description).
      3. The slug set covers ≥ 95% of content HTML files in the same directory.
      4. No duplicate slugs.
      5. All slugs are non-empty strings (no null / empty entries).
    """

    COVERAGE_THRESHOLD = 0.95
    REQUIRED_FIELDS = {"s", "t", "d"}

    def _load(self, lang: str, lang_dir: str) -> list[dict]:
        path = os.path.join(lang_dir, "search.json")
        self.assertTrue(
            os.path.exists(path),
            f"[{lang}] search.json が見つからない: {path}"
        )
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, list,
            f"[{lang}] search.json はリスト形式でなければならない")
        return data

    def _check_lang(self, lang: str, lang_dir: str):
        data = self._load(lang, lang_dir)

        # ── required fields ──────────────────────────────────────────────────
        missing_fields = []
        for i, entry in enumerate(data):
            absent = self.REQUIRED_FIELDS - set(entry.keys())
            if absent:
                missing_fields.append(f"entry[{i}] slug={entry.get('s','?')}: {absent}")
        if missing_fields:
            self.fail(
                f"[{lang}] search.json エントリにフィールド不足 "
                f"({len(missing_fields)}件):\n" + "\n".join(missing_fields[:5])
            )

        # ── non-empty slugs ───────────────────────────────────────────────────
        empty_slugs = [i for i, e in enumerate(data) if not e.get("s", "").strip()]
        if empty_slugs:
            self.fail(f"[{lang}] search.json に空スラグが {len(empty_slugs)} 件")

        # ── duplicate slugs ───────────────────────────────────────────────────
        slugs = [e["s"] for e in data]
        seen, dups = set(), []
        for s in slugs:
            if s in seen:
                dups.append(s)
            seen.add(s)
        if dups:
            self.fail(
                f"[{lang}] search.json に重複スラグ ({len(dups)}件): {dups[:5]}"
            )

        # ── coverage against actual HTML files ───────────────────────────────
        slug_set = set(slugs)
        content_files = [
            f for f in all_html_files(lang_dir)
            if os.path.basename(f) != "index.html"
        ]
        matched = sum(
            1 for f in content_files
            if os.path.splitext(os.path.basename(f))[0] in slug_set
        )
        coverage = matched / len(content_files) if content_files else 0
        self.assertGreaterEqual(
            coverage, self.COVERAGE_THRESHOLD,
            f"[{lang}] search.json カバレッジ低: "
            f"{matched}/{len(content_files)} = {coverage:.1%} "
            f"(閾値 {self.COVERAGE_THRESHOLD:.0%})"
        )

    def test_en_search_json(self):
        self._check_lang("en", EN_DIR)

    def test_ja_search_json(self):
        self._check_lang("ja", JA_DIR)

    def test_pt_search_json(self):
        self._check_lang("pt", PT_DIR)

    def test_search_json_min_entries(self):
        """All three search.json files must have a substantial number of entries."""
        for lang, lang_dir in LANGS.items():
            path = os.path.join(lang_dir, "search.json")
            if not os.path.exists(path):
                self.fail(f"[{lang}] search.json が存在しない")
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self.assertGreater(
                len(data), 1000,
                f"[{lang}] search.json のエントリ数が少なすぎる: {len(data)}"
            )


class TestIndexHtmlClean(unittest.TestCase):
    """
    After the Day 4fl_27 cleanup pass, index.html must NOT contain:

      - Inline batch comment blocks  (<!-- Batch NNN --> ... <!-- END BATCH CARDS -->)
      - Orphaned .tech-card elements that were injected outside the proper structure

    The canonical page catalogue is now search.json; index.html only contains
    the accordion category sections.
    """

    # Pattern that matches the injected Batch comment markers
    BATCH_COMMENT_RE = re.compile(r"<!--\s*Batch\s+\d+", re.IGNORECASE)

    # Pattern for a standalone .tech-card <div> (the old card format injected
    # in bulk – these should no longer appear in index.html)
    TECH_CARD_RE = re.compile(r'class=["\']tech-card["\']', re.IGNORECASE)

    def _get_index(self, lang: str, lang_dir: str) -> str:
        path = os.path.join(lang_dir, "index.html")
        self.assertTrue(
            os.path.exists(path),
            f"[{lang}] index.html が見つからない"
        )
        return read(path)

    def test_en_no_batch_comments(self):
        content = self._get_index("en", EN_DIR)
        m = self.BATCH_COMMENT_RE.search(content)
        self.assertIsNone(
            m,
            f"[en] index.html に Batch コメントブロックが残存: "
            f"...{content[max(0, m.start()-20):m.end()+40]}..."
            if m else ""
        )

    def test_ja_no_batch_comments(self):
        content = self._get_index("ja", JA_DIR)
        m = self.BATCH_COMMENT_RE.search(content)
        self.assertIsNone(
            m,
            f"[ja] index.html に Batch コメントブロックが残存"
            if m else ""
        )

    def test_pt_no_batch_comments(self):
        content = self._get_index("pt", PT_DIR)
        m = self.BATCH_COMMENT_RE.search(content)
        self.assertIsNone(
            m,
            f"[pt] index.html に Batch コメントブロックが残存"
            if m else ""
        )

    def test_en_no_orphaned_tech_cards(self):
        content = self._get_index("en", EN_DIR)
        matches = self.TECH_CARD_RE.findall(content)
        self.assertEqual(
            len(matches), 0,
            f"[en] index.html に孤立した .tech-card が {len(matches)} 件残存"
        )

    def test_ja_no_orphaned_tech_cards(self):
        content = self._get_index("ja", JA_DIR)
        matches = self.TECH_CARD_RE.findall(content)
        self.assertEqual(
            len(matches), 0,
            f"[ja] index.html に孤立した .tech-card が {len(matches)} 件残存"
        )

    def test_pt_no_orphaned_tech_cards(self):
        content = self._get_index("pt", PT_DIR)
        matches = self.TECH_CARD_RE.findall(content)
        self.assertEqual(
            len(matches), 0,
            f"[pt] index.html に孤立した .tech-card が {len(matches)} 件残存"
        )

    def test_index_has_search_json_script(self):
        """index.html should reference search.json for the client-side search."""
        for lang, lang_dir in LANGS.items():
            content = self._get_index(lang, lang_dir)
            self.assertIn(
                "search.json", content,
                f"[{lang}] index.html に search.json への参照がない"
            )


class TestHreflangUrlConsistency(unittest.TestCase):
    """
    hreflang URL consistency check (added Day 4fo).

    For each page that HAS hreflang tags, verify:
      1. The URL for hreflang="en"   contains /en/   in its path.
      2. The URL for hreflang="ja"   contains /ja/   in its path.
      3. The URL for hreflang="pt*"  contains /pt/   in its path.
      4. The slug in every hreflang URL matches the page's own filename (sans ext).
      5. x-default (when present) points to the /en/ variant.
    """

    HREFLANG_RE = re.compile(
        r'<link[^>]+rel=["\']alternate["\'][^>]+hreflang=["\']([^"\']+)["\'][^>]+href=["\']([^"\']+)["\']',
        re.IGNORECASE,
    )
    BASE = "https://wiki.bjj-app.net"

    def _extract_hreflang_map(self, content: str) -> dict[str, str]:
        """Return {hreflang_value: href_url} for all alternate link tags."""
        return {hl: url for hl, url in self.HREFLANG_RE.findall(content)}

    def _check_lang(self, lang: str, lang_dir: str):
        files = sampled(all_html_files(lang_dir))
        failures = []
        for path in files:
            content = read(path)
            hmap = self._extract_hreflang_map(content)
            if not hmap:
                continue  # older pages without hreflang – skip

            slug = os.path.splitext(os.path.basename(path))[0]

            # Check each lang URL contains the correct directory prefix
            lang_dir_checks = {
                "en":   "/en/",
                "ja":   "/ja/",
            }
            for hl_key, expected_dir in lang_dir_checks.items():
                url = hmap.get(hl_key, "")
                if url and expected_dir not in url:
                    failures.append(
                        f"{os.path.basename(path)}: hreflang={hl_key} URL に "
                        f"'{expected_dir}' が含まれない: {url}"
                    )

            # pt or pt-BR
            pt_url = hmap.get("pt") or hmap.get("pt-BR", "")
            if pt_url and "/pt/" not in pt_url:
                failures.append(
                    f"{os.path.basename(path)}: hreflang=pt* URL に '/pt/' が含まれない: {pt_url}"
                )

            # Slug consistency: every URL must end with /{slug}.html
            for hl_key, url in hmap.items():
                if not url:
                    continue
                expected_suffix = f"/{slug}.html"
                if not url.endswith(expected_suffix):
                    failures.append(
                        f"{os.path.basename(path)}: hreflang={hl_key} URL の slug が "
                        f"ページ名と不一致 (期待: ...{expected_suffix}, 実際: {url})"
                    )

            # x-default must point to /en/ when present
            xdefault = hmap.get("x-default", "")
            if xdefault and "/en/" not in xdefault:
                failures.append(
                    f"{os.path.basename(path)}: x-default が /en/ を指していない: {xdefault}"
                )

        if failures:
            self.fail(
                f"[{lang}] hreflang URL 整合性エラー ({len(failures)}件):\n"
                + "\n".join(failures[:5])
            )

    def test_en_hreflang_url_consistency(self):
        self._check_lang("en", EN_DIR)

    def test_ja_hreflang_url_consistency(self):
        self._check_lang("ja", JA_DIR)

    def test_pt_hreflang_url_consistency(self):
        self._check_lang("pt", PT_DIR)


class TestTranslationCompleteness(unittest.TestCase):
    """
    JA/PT pages must use translated UI text in nav and footer (added Day 4fo).

    - JA pages: breadcrumb/footer home link text must be 'ホーム', not 'Home'
    - PT pages: breadcrumb/footer home link text must be 'Início', not 'Home'

    Method: look for >Home< anchor text pattern in nav/footer context.
    False-positive guard: only flag files where the translated term is absent
    AND the English term is present.
    """

    # Matches literal >Home< as anchor text (case-sensitive, not e.g. 'Homepage')
    EN_HOME_RE = re.compile(r'>Home<')

    JA_HOME_TERM  = "ホーム"
    PT_HOME_TERMS = ("Início", "Inicio")   # accent variant for robustness

    def test_ja_home_translated(self):
        files = sampled(all_html_files(JA_DIR))
        failures = []
        for path in files:
            content = read(path)
            has_en_home  = bool(self.EN_HOME_RE.search(content))
            has_ja_home  = self.JA_HOME_TERM in content
            # Only flag when English "Home" is present AND Japanese translation is absent
            if has_en_home and not has_ja_home:
                failures.append(os.path.basename(path))
        if failures:
            self.fail(
                f"[ja] ナビ/フッターに英語 'Home' が残存 ('{self.JA_HOME_TERM}' なし) "
                f"({len(failures)}/{len(files)}):\n" + "\n".join(failures[:5])
            )

    def test_pt_home_translated(self):
        files = sampled(all_html_files(PT_DIR))
        failures = []
        for path in files:
            content = read(path)
            has_en_home  = bool(self.EN_HOME_RE.search(content))
            has_pt_home  = any(t in content for t in self.PT_HOME_TERMS)
            if has_en_home and not has_pt_home:
                failures.append(os.path.basename(path))
        if failures:
            self.fail(
                f"[pt] ナビ/フッターに英語 'Home' が残存 ('Início' なし) "
                f"({len(failures)}/{len(files)}):\n" + "\n".join(failures[:5])
            )

    def test_ja_last_updated_translated(self):
        """'Last updated' should appear as '最終更新' in JA pages."""
        EN_TERM = "Last updated"
        JA_TERM = "最終更新"
        files = sampled(all_html_files(JA_DIR))
        failures = []
        for path in files:
            content = read(path)
            if EN_TERM in content and JA_TERM not in content:
                failures.append(os.path.basename(path))
        if failures:
            self.fail(
                f"[ja] 'Last updated' が '{JA_TERM}' に翻訳されていないページ "
                f"({len(failures)}/{len(files)}):\n" + "\n".join(failures[:5])
            )


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    exit(0 if result.wasSuccessful() else 1)
