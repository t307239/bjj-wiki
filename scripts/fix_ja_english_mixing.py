#!/usr/bin/env python3
"""
fix_ja_english_mixing.py — z253: JA wiki 英語混入 fix (J-2)

scan_ja_english_mixing.py (J-1) で検出した 696 CRITICAL ja page の
<title> / <h1> / <meta description> を Gemini で日本語に翻訳。

設計原則:
  - input: ja_english_mixing_report.csv (J-1 出力)
  - 各 CRITICAL page で title / h1 / meta を Gemini 翻訳
  - 既存 body content には触らない (z248 depth section も保持)
  - BJJ 専門用語のカタカナ化を統一 (例: "Armbar" → "アームバー")
  - Idempotent: 一度 fix した page は再実行で skip (= 英語含まなくなれば skip)
  - Gemini fail は page skip、HTML 壊さない

cost / 時間:
  - 696 page × ~500 tokens input + ~200 tokens output = ~500K tokens
  - Gemini 2.5-flash-lite: ~$0.30
  - Rate limit 1 sec/page = 12 分

setup:
  - python3 scripts/scan_ja_english_mixing.py で先に csv 生成
  - GEMINI_API_KEY (env / .env / ~/.secrets)

Usage:
  python3 scripts/fix_ja_english_mixing.py --dry-run                # 1 page sample
  python3 scripts/fix_ja_english_mixing.py --apply --limit 10       # 10 件 test
  python3 scripts/fix_ja_english_mixing.py --apply                  # 全 CRITICAL fix
"""
from __future__ import annotations
import os
import sys
import re
import csv
import time
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
JA_DIR = REPO_ROOT / "ja"
REPORT_CSV = REPO_ROOT / "ja_english_mixing_report.csv"
RATE_LIMIT_SLEEP = 1.0


def import_gemini():
    try:
        import google.generativeai as genai
        return genai
    except ImportError:
        print("❌ google-generativeai 未 install")
        sys.exit(1)


def load_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key
    for p in [REPO_ROOT / ".env", Path.home() / ".secrets",
              Path.home() / "Claude" / "bjj-wiki" / ".env"]:
        if p.exists():
            for line in p.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def gemini_translate(genai, slug: str, title_en: str, h1_en: str, desc_en: str) -> dict | None:
    """3 field 一括翻訳して dict 返す"""
    api_key = load_api_key()
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        prompt = f"""You will receive a BJJ wiki page's English title/h1/meta description.
Translate them to natural Japanese. BJJ technical terms should use the established katakana form
(e.g., "Armbar" → "アームバー", "Guard" → "ガード", "Sweep" → "スイープ").

Page slug: {slug}

Input:
- title: {title_en}
- h1: {h1_en}
- description: {desc_en}

Output ONLY a JSON object in this exact format (no markdown, no commentary):
{{"title": "<JA title>", "h1": "<JA h1>", "description": "<JA description>"}}

Rules:
- title: under 60 chars, end with " | BJJ Wiki"
- h1: under 50 chars, no "| BJJ Wiki" suffix
- description: 100-150 chars, natural sentences
- Use established BJJ katakana
- Don't use emoji
"""
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        # Strip markdown code fence if present
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        import json
        result = json.loads(text)
        if not all(k in result for k in ("title", "h1", "description")):
            return None
        return result
    except Exception as e:
        print(f"     ⚠️  Gemini error: {e}")
        return None


def patch_html(html: str, new_title: str, new_h1: str, new_desc: str) -> str:
    """HTML の <title> / <h1> / <meta description> を replace"""
    # title
    html = re.sub(
        r"<title[^>]*>.*?</title>",
        f"<title>{new_title}</title>",
        html, count=1, flags=re.DOTALL
    )
    # meta description
    html = re.sub(
        r'(<meta[^>]+name=["\']description["\'][^>]+content=)["\'][^"\']*["\']',
        rf'\1"{new_desc}"',
        html, count=1
    )
    # h1
    html = re.sub(
        r"<h1[^>]*>.*?</h1>",
        f"<h1>{new_h1}</h1>",
        html, count=1, flags=re.DOTALL
    )
    return html


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=696)
    args = ap.parse_args()

    if not REPORT_CSV.exists():
        print(f"❌ {REPORT_CSV} not found — 先に scan_ja_english_mixing.py を run")
        return 1

    genai = import_gemini() if args.apply else None

    # CSV 読み込み、CRITICAL のみ
    targets = []
    with open(REPORT_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["severity"] == "CRITICAL":
                targets.append(row)

    print(f"📋 CRITICAL targets: {len(targets)} 件、limit={args.limit}")
    print()

    done = 0
    skip = 0
    fail = 0

    for i, row in enumerate(targets[:args.limit]):
        slug = row["slug"]
        fp = JA_DIR / f"{slug}.html"
        if not fp.exists():
            print(f"  [{i+1}] {slug}: ❌ file not found, skip")
            fail += 1
            continue

        html = fp.read_text(encoding="utf-8")
        # Idempotent: title が既に日本語含むなら skip
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if title_match and re.search(r"[぀-ゟ゠-ヿ一-鿿]", title_match.group(1)):
            print(f"  [{i+1}] {slug}: ⏭  既 fix 済 (title に JA 含む)")
            skip += 1
            continue

        if not args.apply:
            print(f"  [{i+1}] {slug}: 📝 (dry-run) would translate")
            done += 1
            continue

        result = gemini_translate(
            genai, slug,
            row["title"], row["h1"], row["desc"]
        )
        if not result:
            print(f"  [{i+1}] {slug}: ❌ Gemini fail")
            fail += 1
            continue

        new_html = patch_html(
            html,
            result["title"], result["h1"], result["description"]
        )
        if new_html == html:
            print(f"  [{i+1}] {slug}: ⚠️  patch 失敗 (no change)")
            fail += 1
            continue

        try:
            fp.write_text(new_html, encoding="utf-8")
            print(f"  [{i+1}] {slug}: ✅ {result['h1'][:40]}")
            done += 1
        except Exception as e:
            print(f"  [{i+1}] {slug}: ❌ write fail: {e}")
            fail += 1

        time.sleep(RATE_LIMIT_SLEEP)

    print()
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    mode = "APPLIED" if args.apply else "DRY-RUN"
    print(f"📊 [{mode}] done={done}, skip={skip}, fail={fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
