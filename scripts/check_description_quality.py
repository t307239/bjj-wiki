#!/usr/bin/env python3
"""
check_description_quality.py — z260w (consolidated from phase_b audit logic)

Lint replacement for one-off fix scripts (fix_locale_drift_descriptions.py /
fix_pt_athlete_desc_concat_drift.py / fix_long_descriptions.py /
fix_about_privacy_meta_drift.py).

Checks 4 classes of <meta name="description"> / <meta property="og:description">
drift that the above one-off scripts addressed:

  Class A — locale drift:
    JA description that is ASCII-dominant (≥50%) or ends with English-only residue.
    PT description with no PT marker but ≥2 English-only keywords.

  Class B — concat drift (PT athlete):
    PT athlete-*.html description that contains the broken concat pattern
    `<sentence>.'<Nickname>' é um competidor de...` (no space after period).

  Class C — length overflow:
    EN/PT description > 160 chars OR JA description > 130 chars.
    (Google SERP truncates at ~155-160 chars; JA chars are visually wider.)

  Class D — about/privacy meta drift (root + localized):
    Localized en/ja/pt/{about,privacy}.html: should be noindex,follow
    AND should NOT advertise hreflang alternates (noindex pages).
    Root /about.html and /privacy.html: should have robots index,follow
    AND should have canonical link to themselves.

`--ci` flag returns EXIT:1 if any finding, else EXIT:0.

Run: python3 scripts/check_description_quality.py [--ci] [--class A|B|C|D]
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

META_DESC_RE = re.compile(
    r'<meta\s+name="description"\s+content="([^"]*)"', re.IGNORECASE
)
OG_DESC_RE = re.compile(
    r'<meta\s+property="og:description"\s+content="([^"]*)"', re.IGNORECASE
)
ROBOTS_RE = re.compile(
    r'<meta\s+name="robots"\s+content="([^"]*)"', re.IGNORECASE
)
HREFLANG_RE = re.compile(
    r'<link\s+rel="alternate"\s+hreflang="[^"]*"\s+href="[^"]*"', re.IGNORECASE
)
CANONICAL_RE = re.compile(
    r'<link\s+rel="canonical"\s+href="([^"]*)"', re.IGNORECASE
)

# Class B: PT athlete description concat drift
# Pattern: <sentence>.'<Nickname>... (no space between period and quote)
PT_CONCAT_RE = re.compile(r"\.'[A-Za-z][^']*'")

# Class A heuristics
EN_RESIDUE_TRAILING_RE = re.compile(
    r"\b(positional|positioning|advantage|technique|submissions|control|guards?)\b\s*\w*\s*$",
    re.IGNORECASE,
)
PT_MARKER_RE = re.compile(
    r"(ção|ções|guarda|aprenda|conheça|técnica|posição|jiu-jitsu|raspagem|finalização|domine)",
    re.IGNORECASE,
)
PT_EN_ONLY_RE = re.compile(
    r"\b(the|with|from|your|that|this|here|these|those|positioning|technique|opponent|guard|control|learn|master)\b",
    re.IGNORECASE,
)


def has_cjk(s: str) -> bool:
    """Has hiragana / katakana / CJK ideograph."""
    return bool(re.search(r"[぀-ゟ゠-ヿ一-鿿]", s))


def looks_bad_ja(desc: str) -> bool:
    if not desc:
        return False
    en_letters = sum(1 for c in desc if c.isascii() and c.isalpha())
    total_letters = sum(1 for c in desc if c.isalpha())
    if total_letters == 0:
        return False
    en_ratio = en_letters / total_letters
    # If desc has CJK chars (hiragana / katakana / kanji), allow embedded
    # English brand / technique names. Only flag if entire desc is ASCII
    # (no CJK at all) OR has trailing EN residue pattern.
    has_jp = has_cjk(desc)
    if not has_jp and en_ratio > 0.5:
        # No JP chars at all and >50% English → fully English desc on JA page
        return True
    if has_jp and en_ratio > 0.75:
        # Some JP but ≥75% English letters → English-dominant
        return True
    if EN_RESIDUE_TRAILING_RE.search(desc):
        return True
    return False


def looks_bad_pt(desc: str) -> bool:
    if not desc:
        return False
    if not PT_MARKER_RE.search(desc) and len(PT_EN_ONLY_RE.findall(desc)) >= 2:
        return True
    return False


def class_a_locale_drift(html_files: list[Path]) -> list[tuple[str, str]]:
    """Return [(rel_path, reason)] for JA/PT description locale drift."""
    findings: list[tuple[str, str]] = []
    for fp in html_files:
        rel = fp.relative_to(ROOT).as_posix()
        if not (rel.startswith("ja/") or rel.startswith("pt/")):
            continue
        try:
            html = fp.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        m = META_DESC_RE.search(html)
        if not m:
            continue
        desc = m.group(1)
        if rel.startswith("ja/") and looks_bad_ja(desc):
            findings.append((rel, f"JA desc has EN-dominant or residue: {desc[:80]!r}"))
        elif rel.startswith("pt/") and looks_bad_pt(desc):
            findings.append((rel, f"PT desc lacks PT marker + has EN keywords: {desc[:80]!r}"))
    return findings


def class_b_pt_athlete_concat(html_files: list[Path]) -> list[tuple[str, str]]:
    """PT athlete description concat drift."""
    findings: list[tuple[str, str]] = []
    for fp in html_files:
        rel = fp.relative_to(ROOT).as_posix()
        if not (rel.startswith("pt/") and "athlete-" in rel):
            continue
        try:
            html = fp.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        m = META_DESC_RE.search(html)
        if not m:
            continue
        desc = m.group(1)
        if PT_CONCAT_RE.search(desc):
            findings.append((rel, f"PT concat drift `.'X'` detected: {desc[:120]!r}"))
    return findings


def class_c_length_overflow(html_files: list[Path]) -> list[tuple[str, str]]:
    """description length overflow."""
    findings: list[tuple[str, str]] = []
    for fp in html_files:
        rel = fp.relative_to(ROOT).as_posix()
        if not (rel.startswith("en/") or rel.startswith("ja/") or rel.startswith("pt/")):
            continue
        try:
            html = fp.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        m = META_DESC_RE.search(html)
        if not m:
            continue
        desc = m.group(1)
        is_ja = rel.startswith("ja/")
        limit = 130 if is_ja else 160
        if len(desc) > limit:
            findings.append((rel, f"description {len(desc)} > limit {limit}: {desc[:80]!r}"))
    return findings


def class_d_about_privacy(html_files_unused: list[Path]) -> list[tuple[str, str]]:
    """about/privacy meta drift — localized + root."""
    findings: list[tuple[str, str]] = []
    localized = [
        ("en", "about.html"), ("ja", "about.html"), ("pt", "about.html"),
        ("en", "privacy.html"), ("ja", "privacy.html"), ("pt", "privacy.html"),
    ]
    for lang, name in localized:
        fp = ROOT / lang / name
        if not fp.exists():
            continue
        try:
            html = fp.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = f"{lang}/{name}"
        m_robots = ROBOTS_RE.search(html)
        if not m_robots:
            findings.append((rel, "localized page missing <meta name=robots>"))
        else:
            content = m_robots.group(1).strip().lower()
            # must be noindex,follow (not nofollow)
            if "noindex" not in content:
                findings.append((rel, f"localized page robots not noindex: {content!r}"))
            elif "nofollow" in content:
                findings.append((rel, f"localized page robots should be 'noindex, follow' not 'noindex, nofollow': {content!r}"))
        # hreflang should NOT be present on noindex page (broken cluster)
        if HREFLANG_RE.search(html):
            findings.append((rel, "localized noindex page advertises hreflang (broken SEO cluster)"))

    for name in ("about.html", "privacy.html"):
        fp = ROOT / name
        if not fp.exists():
            continue
        try:
            html = fp.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        m_robots = ROBOTS_RE.search(html)
        if not m_robots:
            findings.append((name, "root page missing <meta name=robots index,follow>"))
        else:
            content = m_robots.group(1).strip().lower()
            if "noindex" in content:
                findings.append((name, f"root page robots is noindex: {content!r}"))
        if not CANONICAL_RE.search(html):
            findings.append((name, "root page missing canonical link"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true", help="EXIT:1 on findings")
    parser.add_argument("--class", dest="class_filter", choices=["A", "B", "C", "D", "all"], default="all")
    args = parser.parse_args()

    html_files = sorted(ROOT.glob("**/*.html"))
    # Filter out node_modules / archive / scripts
    html_files = [
        fp for fp in html_files
        if "node_modules" not in fp.parts
        and ".git" not in fp.parts
        and "archive" not in fp.parts
    ]

    runs = []
    if args.class_filter in ("A", "all"):
        runs.append(("Class A — locale drift (JA/PT)", class_a_locale_drift))
    if args.class_filter in ("B", "all"):
        runs.append(("Class B — PT athlete concat drift", class_b_pt_athlete_concat))
    if args.class_filter in ("C", "all"):
        runs.append(("Class C — description length overflow", class_c_length_overflow))
    if args.class_filter in ("D", "all"):
        runs.append(("Class D — about/privacy meta drift", class_d_about_privacy))

    total_findings = 0
    for label, fn in runs:
        findings = fn(html_files)
        total_findings += len(findings)
        print(f"\n=== {label}: {len(findings)} finding(s) ===")
        for rel, reason in findings[:30]:
            print(f"  {rel}: {reason}")
        if len(findings) > 30:
            print(f"  ... and {len(findings) - 30} more")

    print(f"\nTotal description-quality findings: {total_findings}")
    if args.ci and total_findings > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
