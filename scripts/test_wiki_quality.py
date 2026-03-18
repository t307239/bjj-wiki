#!/usr/bin/env python3
"""
BJJ Wiki Quality Test Suite
Usage: python3 scripts/test_wiki_quality.py
       python3 -m pytest scripts/test_wiki_quality.py -v  (pytest optional)

Tests validate the generated HTML files without external dependencies.
"""

import os
import re
import glob
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
BASE_URL = "https://t307239.github.io/bjj-wiki"
AFFILIATE_TAG = "bjj06-22"
APP_URL = "bjj-app-one.vercel.app"

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
                self.assertIn(AFFILIATE_TAG, content,
                    f"{lang}/{slug}.html にアフィリエイトタグ {AFFILIATE_TAG} なし")


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


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    exit(0 if result.wasSuccessful() else 1)
