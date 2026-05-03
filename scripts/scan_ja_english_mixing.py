#!/usr/bin/env python3
"""
scan_ja_english_mixing.py — z252: JA wiki 英語混入 検出 (J-1)

z248 で発覚した「ja/armbar.html の <title>/<h1>/<meta description> が英語」
bug の規模調査。1,566 ja page を scan、英語混入してる page を list 化。

検出ルール:
  - <title> に 連続 5 文字以上の ASCII alphabet (例: "Armbar", "Technique")
  - <h1> に 連続 5 文字以上の ASCII alphabet
  - <meta name="description"> に 連続 5 文字以上の ASCII alphabet
  - 日本語文字 (ひらがな/カタカナ/漢字) が title/h1/meta に存在する場合も check
    (BJJ 専門用語のカタカナは除外、e.g., 「アームバー」 は OK)

出力:
  - bjj-wiki/ja_english_mixing_report.csv
  - 統計 summary を stdout に

Usage:
  python3 scripts/scan_ja_english_mixing.py
"""
from __future__ import annotations
import os
import re
import csv
import sys
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parent.parent
JA_DIR = REPO_ROOT / "ja"
OUT_CSV = REPO_ROOT / "ja_english_mixing_report.csv"

# 連続 5 文字以上の ASCII alphabet → 英語と判定
ENGLISH_RE = re.compile(r"\b[A-Za-z]{5,}\b")
# 日本語文字 (ひらがな + カタカナ + CJK Unified Ideographs)
JA_RE = re.compile(r"[぀-ゟ゠-ヿ一-鿿]")

# BJJ 専門用語の英語名 (これらは混入とカウントしない、許容語彙)
ALLOWED_ENGLISH = {
    "BJJ", "Jiu", "Jitsu", "MMA", "ADCC", "IBJJF", "EBI", "Polaris",
    "Brazilian", "Gracie",
}


def extract_field(html: str, pattern: str) -> str:
    m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m.lastindex else m.group(0)


def detect_english(text: str) -> list[str]:
    """text 内で 5+ 文字英単語を検出 (allowed 除外)"""
    if not text:
        return []
    matches = ENGLISH_RE.findall(text)
    return [m for m in matches if m.lower() not in {a.lower() for a in ALLOWED_ENGLISH}]


def has_japanese(text: str) -> bool:
    return bool(JA_RE.search(text))


def main() -> int:
    if not JA_DIR.exists():
        print(f"❌ {JA_DIR} not found")
        return 1

    files = sorted(JA_DIR.glob("*.html"))
    print(f"📂 ja/ — {len(files)} ファイル scan 開始")

    issues = []
    severity_counter = Counter()

    for fp in files:
        try:
            html = fp.read_text(encoding="utf-8")
        except Exception as e:
            print(f"⚠️  read fail: {fp.name}: {e}")
            continue

        title = extract_field(html, r"<title[^>]*>(.*?)</title>")
        h1 = extract_field(html, r"<h1[^>]*>(.*?)</h1>")
        desc_m = re.search(
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE,
        )
        desc = desc_m.group(1) if desc_m else ""

        title_eng = detect_english(title)
        h1_eng = detect_english(h1)
        desc_eng = detect_english(desc)
        title_ja = has_japanese(title)
        h1_ja = has_japanese(h1)
        desc_ja = has_japanese(desc)

        # 重大度:
        #   CRITICAL: title or h1 が「英語のみ」 (日本語ゼロ) — 元 bug pattern
        #   WARNING: title or h1 に英語混入だが日本語あり
        #   INFO: meta だけ英語混入
        sev = ""
        if (title_eng and not title_ja) or (h1_eng and not h1_ja):
            sev = "CRITICAL"
        elif title_eng or h1_eng:
            sev = "WARNING"
        elif desc_eng and not desc_ja:
            sev = "INFO"

        if sev:
            severity_counter[sev] += 1
            issues.append({
                "slug": fp.stem,
                "severity": sev,
                "title": title[:80],
                "title_english": ",".join(title_eng[:5]),
                "h1": h1[:80],
                "h1_english": ",".join(h1_eng[:5]),
                "desc": desc[:120],
                "desc_english": ",".join(desc_eng[:5]),
            })

    # CSV 出力
    if issues:
        with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(issues[0].keys()))
            writer.writeheader()
            writer.writerows(issues)
        print(f"✅ 出力: {OUT_CSV}")

    print()
    print("─" * 60)
    print(f"📊 結果 (1,566 ja page 中):")
    print(f"  🔴 CRITICAL (title/h1 が英語のみ): {severity_counter['CRITICAL']} 件")
    print(f"  🟡 WARNING (title/h1 に英語混入): {severity_counter['WARNING']} 件")
    print(f"  🟢 INFO (meta だけ英語): {severity_counter['INFO']} 件")
    print(f"  ✅ 健全: {len(files) - sum(severity_counter.values())} 件")

    if issues:
        print()
        print("CRITICAL sample (top 5):")
        critical = [i for i in issues if i["severity"] == "CRITICAL"][:5]
        for i in critical:
            print(f"  - ja/{i['slug']}: title='{i['title'][:50]}' / h1='{i['h1'][:50]}'")

    return 0


if __name__ == "__main__":
    sys.exit(main())
