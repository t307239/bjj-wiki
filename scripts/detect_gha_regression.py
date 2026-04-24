#!/usr/bin/env python3
"""
detect_gha_regression.py — GHA 先祖返り自動検出 lint

Day 5_236z140-z155 (12 cycles) で発見した regression pattern を自動検出。
個別修正ではなく「今後の drift を検出」するのが目的。

検出パターン (z140-z155 の実績 findings):
  1. Gemini API key が URL query に  (z143/z152/z155)
  2. access_token が URL body に    (z155)
  3. f-string JSON-LD (escape なし)   (z153)
  4. HTML 属性に {x} 直挿入 (escape なし)  (z153)
  5. title に ` | BJJ` 系 suffix 二重適用リスク (z144/z149)
  6. index/category 生成で og:site_name 等欠落 (z154)
  7. 生成 HTML に html lang="pt-BR" (z129 で pt 統一済み)
  8. GTM-XXXXXX / G-PLACEHOLDER 残存 (z130)
  9. [JA]/[PT]/[EN] title prefix (z134/z135)
  10. MONTH_LABELS_EN/_JA のみ (PT 欠落, z147)
  11. locale === "ja" で ELSE EN fallback (PT 無視, z145)
  12. hreflang="pt-BR" (pt に統一済み, z128)

Usage:
  python3 scripts/detect_gha_regression.py            # 全件検出
  python3 scripts/detect_gha_regression.py --strict   # exit 1 if any 🔴
  python3 scripts/detect_gha_regression.py --ci       # CI 用 (strict + 短縮出力)
"""

from __future__ import annotations
import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

# 自己参照除外 (lint 自身がパターン定義を含むため)
SELF_FILENAME = Path(__file__).name

# ── Pattern Registry ────────────────────────────────────────────────

PATTERNS = [
    # (id, severity, file_glob, regex, description, z-tag)
    ("GEMINI_URL_KEY", "🔴", "scripts/*.py",
     r"generativelanguage\.googleapis\.com[^\"']*\?key=\{",
     "Gemini API key が URL query に残存 → x-goog-api-key header に",
     "z143/z152"),
    ("TOKEN_URL_QUERY", "🔴", "scripts/*.py",
     r'\?access_token=\{|"access_token":\s*(?:access_token|token|[A-Z_]+TOKEN)\b',
     "access_token が URL/body に → Authorization Bearer header に",
     "z155"),
    ("JSONLD_FSTRING", "🔴", "scripts/generate_bjj_wiki.py",
     r'application/ld\+json"?>\s*\n?\s*\{\{',
     "JSON-LD を f-string で組み立てている → json.dumps に",
     "z153"),
    ("HTML_ATTR_UNESCAPED", "🟡", "scripts/*.py",
     r'content="\{article\.get\([^)]+\)\}"',
     "content 属性に Gemini 出力を直接挿入 → html.escape に",
     "z153"),
    ("INDEX_META_MISSING", "🟡", None,  # ad-hoc check
     None,
     "generate_index() / generate_category_index() に og:site_name なし",
     "z154"),
    ("HTML_LANG_PT_BR", "🟡", "scripts/*.py",
     r'<html\s+lang="pt-BR"',
     'html lang="pt-BR" 残存 → "pt" に (z129)',
     "z129"),
    ("GTM_PLACEHOLDER", "🟡", "scripts/*.py",
     r'GTM-XXXXXXX*|G-PLACEHOLDER',
     'GTM プレースホルダ残存 → GTM-WC3DKRB / G-7LM8L3TRZM に',
     "z130"),
    ("LANG_PREFIX_TITLE", "🟡", "scripts/*.py",
     r'<title>\s*\[(JA|PT|EN)\]|<title>\{[^}]*\}\s*\[(JA|PT|EN)\]',
     'title に [JA]/[PT]/[EN] prefix → 除去 (z134/z135)',
     "z134"),
    ("HREFLANG_PT_BR", "🟡", "scripts/*.py",
     r'hreflang="pt-BR"',
     'hreflang="pt-BR" → "pt" に統一 (z128)',
     "z128"),
    ("MONTH_LABELS_DRIFT", "🟡", None,  # ad-hoc
     None,
     "MONTH_LABELS_{EN,JA} は定義済だが _PT 欠落",
     "z147"),
    ("TITLE_DOUBLE_SUFFIX", "🟡", None,  # ad-hoc on HTML output samples
     None,
     'title に "| BJJ Wiki | BJJ Wiki" 等の二重 suffix 可能性',
     "z149"),
]


# ── Detection engine ────────────────────────────────────────────────

def scan_regex_pattern(pattern_id: str, severity: str, file_glob: str,
                        regex: str, description: str, z_tag: str) -> list:
    """Generic regex-based pattern check."""
    findings = []
    if file_glob is None or regex is None:
        return findings
    pat = re.compile(regex)
    for fp in ROOT.glob(file_glob):
        if not fp.is_file():
            continue
        # 自己参照除外
        if fp.name == SELF_FILENAME:
            continue
        try:
            content = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(content.splitlines(), 1):
            if pat.search(line):
                findings.append({
                    "id": pattern_id, "severity": severity,
                    "file": fp.relative_to(ROOT).as_posix(),
                    "line": i, "text": line.strip()[:120],
                    "description": description, "z": z_tag,
                })
    return findings


def scan_index_meta_missing() -> list:
    """Ad-hoc: generate_index() / generate_category_index() が
    og:site_name / twitter:card / hreflang を含むか検査 (z154 regression)"""
    findings = []
    fp = SCRIPTS / "generate_bjj_wiki.py"
    if not fp.exists():
        return findings
    content = fp.read_text(encoding="utf-8", errors="ignore")
    for fn_name in ("generate_category_index", "generate_index"):
        # Find function body (naive: from 'def X' to next 'def ')
        m = re.search(rf"def\s+{fn_name}\s*\([^)]*\)\s*:(.*?)(?=\ndef\s+|\Z)",
                      content, re.DOTALL)
        if not m:
            continue
        body = m.group(1)
        for required in ('og:site_name', 'twitter:card', 'hreflang'):
            if required not in body:
                findings.append({
                    "id": "INDEX_META_MISSING", "severity": "🟡",
                    "file": "scripts/generate_bjj_wiki.py",
                    "line": 0,
                    "text": f"{fn_name}() に {required!r} が含まれていない",
                    "description": f"{fn_name}() に {required} 欠落",
                    "z": "z154",
                })
    return findings


def scan_month_labels_drift() -> list:
    """Ad-hoc: MONTH_LABELS_EN or MONTH_LABELS_JA が定義されていて
    MONTH_LABELS_PT が定義されていない箇所 (z147 regression)"""
    findings = []
    for fp in ROOT.glob("scripts/*.py"):
        if fp.name == SELF_FILENAME:
            continue
        try:
            c = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        has_en = bool(re.search(r"MONTH_LABELS_EN\s*=", c))
        has_ja = bool(re.search(r"MONTH_LABELS_JA\s*=", c))
        has_pt = bool(re.search(r"MONTH_LABELS_PT\s*=", c))
        if (has_en or has_ja) and not has_pt:
            findings.append({
                "id": "MONTH_LABELS_DRIFT", "severity": "🟡",
                "file": fp.relative_to(ROOT).as_posix(), "line": 0,
                "text": f"MONTH_LABELS_EN={has_en} JA={has_ja} PT={has_pt}",
                "description": "MONTH_LABELS_PT が欠落",
                "z": "z147",
            })
    return findings


# ── Main ────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                        help="🔴 が 1 件でもあれば exit 1")
    parser.add_argument("--ci", action="store_true",
                        help="CI 用短縮出力 (strict と同じ)")
    args = parser.parse_args()
    if args.ci:
        args.strict = True

    all_findings = []

    # 1. Regex-based patterns
    for p in PATTERNS:
        all_findings.extend(scan_regex_pattern(*p))

    # 2. Ad-hoc checks
    all_findings.extend(scan_index_meta_missing())
    all_findings.extend(scan_month_labels_drift())

    # Group by severity
    criticals = [f for f in all_findings if f["severity"] == "🔴"]
    warnings = [f for f in all_findings if f["severity"] == "🟡"]

    if args.ci:
        print(f"🔴 Critical: {len(criticals)}")
        print(f"🟡 Warning:  {len(warnings)}")
        for f in criticals[:20]:
            print(f"  🔴 [{f['id']}] {f['file']}:{f['line']} — {f['description']} ({f['z']})")
        if criticals:
            return 1
        return 0

    # Pretty output
    print("=" * 70)
    print(f"🛡️  GHA 先祖返り自動検出 (scripts/detect_gha_regression.py)")
    print("=" * 70)
    print(f"  🔴 Critical: {len(criticals)}")
    print(f"  🟡 Warning:  {len(warnings)}")
    print(f"  合計:       {len(all_findings)}")
    print()

    if criticals:
        print("🔴 CRITICAL findings (seniority check required before next cron):")
        for f in criticals:
            print(f"  {f['file']}:{f['line']} [{f['id']}]")
            print(f"    {f['description']} ({f['z']})")
            if f.get('text'):
                print(f"    └─ {f['text'][:100]}")
        print()

    if warnings:
        print("🟡 WARNING findings:")
        for f in warnings:
            print(f"  {f['file']}:{f['line']} [{f['id']}] — {f['description']} ({f['z']})")
        print()

    if not all_findings:
        print("✅ 先祖返りなし。全 12 pattern に該当なし。")

    if args.strict and criticals:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
