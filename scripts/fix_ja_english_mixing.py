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
Translate them to natural Japanese. ALL BJJ technical terms must use established katakana form.

CRITICAL: ALL English BJJ terms must be converted to katakana, NOT left in English.

Required katakana conversions:
- Armbar → アームバー / Triangle Choke → トライアングルチョーク / Kimura → キムラ
- Guard → ガード / Sweep → スイープ / Pass → パス
- Mount → マウント / Side Control → サイドコントロール / Back Control → バック
- Rear Naked Choke → リアネイキッドチョーク / Heel Hook → ヒールフック
- Half Guard → ハーフガード / Closed Guard → クローズドガード / Open Guard → オープンガード
- Sub / Submission → サブミッション / Take Down → テイクダウン

ONLY proper nouns (人名 like "Andre Galvao", "Marcelo Garcia") may remain in English.

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
- Don't use emoji
- VERIFY: no English BJJ terms remain, only proper nouns
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
    ap.add_argument("--interactive", action="store_true",
                    help="1 page ごとに diff 表示 + Y/N/Q 確認")
    ap.add_argument("--slug", help="特定 slug のみ test")
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

    if args.slug:
        targets = [r for r in targets if r["slug"] == args.slug]
        if not targets:
            print(f"⚠️  slug '{args.slug}' は CRITICAL に含まれない")
            return 0

    print(f"📋 CRITICAL targets: {len(targets)} 件、limit={args.limit}")
    if args.interactive:
        print("🔍 INTERACTIVE: 各 page で y(適用) / n(skip) / q(終了) 入力")
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
        # Idempotent (z254c 改善): title/h1 に「5 文字以上の英単語」 残ってたら re-fix 対象
        # 旧 logic「JA 含むなら skip」 では半端 fix 状態が残ったため
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
        title_text = re.sub(r"<[^>]+>", "", title_match.group(1)) if title_match else ""
        h1_text = re.sub(r"<[^>]+>", "", h1_match.group(1)) if h1_match else ""
        # 許容語: BJJ, Wiki, 人名 (ASCII 大文字始まり 1 単語) は skip 判定で除外
        ALLOWED = {"BJJ", "Wiki", "Jiu", "Jitsu", "MMA", "ADCC", "IBJJF", "EBI"}
        title_eng = [w for w in re.findall(r"\b[A-Za-z]{5,}\b", title_text) if w.lower() not in {a.lower() for a in ALLOWED}]
        h1_eng = [w for w in re.findall(r"\b[A-Za-z]{5,}\b", h1_text) if w.lower() not in {a.lower() for a in ALLOWED}]
        # h1 が 「人名のみ」 (Andre Galvao 等、3 単語以下、JA なし) なら h1 残し OK と判定
        h1_words = h1_text.strip().split()
        h1_is_proper_noun_only = (
            len(h1_words) <= 3
            and not re.search(r"[぀-ゟ゠-ヿ一-鿿]", h1_text)
            and all(w[0].isupper() if w else True for w in h1_words)
        )
        # title に 英語残ってたら re-fix。h1 も 単独人名以外で英語あれば re-fix
        if not title_eng and (h1_is_proper_noun_only or not h1_eng):
            print(f"  [{i+1}] {slug}: ⏭  fix 済 (英語残なし)")
            skip += 1
            continue

        if not args.apply and not args.interactive:
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

        # Interactive mode: diff 表示 + Y/N/Q
        if args.interactive:
            print()
            print(f"━━━ [{i+1}/{len(targets[:args.limit])}] {slug} ━━━")
            print(f"  title BEFORE : {row['title'][:80]}")
            print(f"  title AFTER  : {result['title'][:80]}")
            print(f"  h1    BEFORE : {row['h1'][:80]}")
            print(f"  h1    AFTER  : {result['h1'][:80]}")
            print(f"  desc  BEFORE : {row['desc'][:100]}")
            print(f"  desc  AFTER  : {result['description'][:100]}")
            print()
            choice = input("  apply? [y]es / [n]o / [q]uit: ").strip().lower()
            if choice == "q":
                print(f"  🛑 quit")
                break
            if choice != "y":
                print(f"  ⏭  skip")
                skip += 1
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
            if not args.interactive:
                print(f"  [{i+1}] {slug}: ✅ {result['h1'][:40]}")
            else:
                print(f"  ✅ applied")
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
