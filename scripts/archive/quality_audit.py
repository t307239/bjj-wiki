#!/usr/bin/env python3
"""
quality_audit.py — BJJ Wiki コンテンツ品質監査 + ゴミ検出器

ローカルの HTML ファイルをスキャンし、WIKI_TEMPLATES.md 基準で 0〜100点スコアリング。
品質閾値（100点満点を目標とした5段階評価）:
  🏆 EXCELLENT (95+)  — 100点を目指すべきモデル記事
  ✅ GOOD     (90-94) — 十分な品質
  ⚠️  POOR     (80-89) — 改善が必要（目標ラインの 80 に届いていない）
  🔴 BAD      (60-79) — SEO負債リスク。早急に改善
  💀 GARBAGE  (<60)   — デプロイ不可レベル

使い方:
    python3 quality_audit.py                  # 全記事スキャン
    python3 quality_audit.py --lang en        # 英語のみ
    python3 quality_audit.py --garbage-only   # 80点未満のみ出力
    python3 quality_audit.py --fix-preview    # 修正提案を表示

出力:
    ~/Claude/bjj-wiki/quality_report.csv
    ~/Claude/bjj-wiki/garbage_slugs.txt   (80点未満 slug リスト)

依存: Python 3.8+ のみ（標準ライブラリ）
"""

import os
import re
import csv
import json
import argparse
from pathlib import Path
from html.parser import HTMLParser

# ─────────────────────────────────────────────────────
# 設定
# ─────────────────────────────────────────────────────

WIKI_ROOT = Path(__file__).parent.parent  # ~/Claude/bjj-wiki/
LANGUAGES = ["en", "ja", "pt"]

# ジャンル別スコアウェイト
SCORE_WEIGHTS = {
    # z245: 全項目 lenient (「無理に基準を満たそうとして破壊」 防止)
    # 段階加点 + 最低 30 pt base、「ベストな page を patch で破壊」 pressure 解消
    "word_count_gte_200": 10,   # 短い page も OK、200 語で加点
    "h2_count_gte_3":     15,   # H2 3 個 (緩和、ほとんど の page が達成)
    "h2_count_gte_6":      5,   # H2 6 個 で追加 bonus
    "has_list":           10,   # 必須じゃない、あれば加点
    "has_bold":           10,
    "has_video":          10,   # Technique/Drill 以外は自動加点維持
    "has_faq":            10,
    "has_internal_links": 10,   # 3 件以上で加点
    "internal_links_gte_5": 5,  # 5 件以上で追加 bonus
    "has_image":          10,   # 画像 1 枚以上
    "_base":              30,   # 全 page に base 30 pt (z245: 破壊耐性)
}
# 合計: 125、上限 100 で cap (= 半数程度の項目クリアで 100 達成可能)

# 動画ボーナスが適用されるジャンル
VIDEO_REQUIRED_TYPES = {"Technique", "Drill"}

# 判定閾値（100点を目標とした段階的な品質ゲート）
GARBAGE_THRESHOLD   = 60   # 💀 < 60  : デプロイ不可
BAD_THRESHOLD       = 80   # 🔴 60-79 : SEO負債リスク（目標ライン未達）
POOR_THRESHOLD      = 90   # ⚠️  80-89 : 改善余地あり
GOOD_THRESHOLD      = 95   # ✅ 90-94 : 良質
EXCELLENT_THRESHOLD = 95   # 🏆 95+   : モデル記事（100を目指す）

# ─────────────────────────────────────────────────────
# HTML 解析
# ─────────────────────────────────────────────────────

def parse_article(html: str) -> dict:
    """HTML から品質指標を抽出"""
    # H2 タイトル一覧
    h2_list = [
        re.sub(r"<[^>]+>", "", m).strip()
        for m in re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.IGNORECASE | re.DOTALL)
    ]

    # H3 タイトル一覧
    h3_list = [
        re.sub(r"<[^>]+>", "", m).strip()
        for m in re.findall(r"<h3[^>]*>(.*?)</h3>", html, re.IGNORECASE | re.DOTALL)
    ]

    # 語数（タグ除去後）
    plain = re.sub(r"<[^>]+>", " ", html)
    plain = re.sub(r"\s+", " ", plain).strip()
    word_count = len(plain.split())

    # リスト存在
    has_list = bool(re.search(r"<(ul|ol)\b", html, re.IGNORECASE))

    # Bold 存在
    has_bold = bool(re.search(r"<(strong|b)\b", html, re.IGNORECASE))

    # YouTube 動画
    has_video = bool(
        re.search(r"youtube\.com/embed|youtu\.be", html, re.IGNORECASE)
    )

    # 画像 (z245)
    has_image = bool(re.search(r"<img\b", html, re.IGNORECASE))

    # FAQ（H2 or H3 に "FAQ" or "Frequently Asked"）
    all_headings = h2_list + h3_list
    has_faq = any(
        "faq" in h.lower() or "frequently asked" in h.lower()
        for h in all_headings
    )

    # 内部リンク（/wiki/ または相対 .html への href）
    internal_links = re.findall(
        r'href=["\'](?:(?:https?://(?:wiki\.bjj-app\.net|bjj-app\.net/wiki))?/wiki/[^"\']+|[^"\'#]+\.html)["\']',
        html,
        re.IGNORECASE,
    )
    internal_link_count = len(internal_links)

    # content_type をメタタグ or class から推測
    content_type = _detect_content_type(html, h2_list)

    return {
        "word_count":          word_count,
        "h2_count":            len(h2_list),
        "h2_list":             h2_list,
        "has_list":            has_list,
        "has_bold":            has_bold,
        "has_video":           has_video,
        "has_faq":             has_faq,
        "has_image":           has_image,
        "internal_link_count": internal_link_count,
        "content_type":        content_type,
    }


def _detect_content_type(html: str, h2_list: list[str]) -> str:
    """コンテンツタイプを heuristic で推測（DB がない場合のフォールバック）"""
    html_lower = html.lower()

    # meta タグ content_type がある場合
    m = re.search(r'content_type["\s:=]+(["\'])(\w+)\1', html)
    if m:
        return m.group(2)

    # Heuristic ルール
    h2_lower = " ".join(h2_list).lower()
    if "athlete" in html_lower[:2000] or "biography" in h2_lower:
        return "Athlete_Bio"
    if any(k in h2_lower for k in ["drill", "solo drill", "partner drill"]):
        return "Drill"
    if any(k in h2_lower for k in ["step 1", "step-by-step", "how to execute", "execution"]):
        return "Technique"
    if any(k in h2_lower for k in ["scoring", "weight class", "submission legality", "prohibited"]):
        return "Rule"
    if any(k in h2_lower for k in ["conditioning", "nutrition", "diet", "workout", "program"]):
        return "Conditioning_Nutrition"
    if any(k in h2_lower for k in ["gear", "gi", "equipment", "review", "buy", "budget"]):
        return "Equipment_Gear"
    return "Concept_Strategy"


# ─────────────────────────────────────────────────────
# スコアリング
# ─────────────────────────────────────────────────────

def score_article(metrics: dict) -> tuple[int, dict[str, int]]:
    """100 点満点スコアを計算し、内訳も返す"""
    content_type = metrics["content_type"]
    breakdown = {}

    # z245: base 30 pt 全 page に (破壊耐性、無理に達成 pressure 解消)
    breakdown["_base"] = SCORE_WEIGHTS["_base"]

    # 語数
    breakdown["word_count_gte_200"] = (
        SCORE_WEIGHTS["word_count_gte_200"] if metrics["word_count"] >= 200 else 0
    )

    # H2 数 (z245: 段階加点に変更、3 で base 加点 + 6 で bonus)
    breakdown["h2_count_gte_3"] = (
        SCORE_WEIGHTS["h2_count_gte_3"] if metrics["h2_count"] >= 3 else 0
    )
    breakdown["h2_count_gte_6"] = (
        SCORE_WEIGHTS["h2_count_gte_6"] if metrics["h2_count"] >= 6 else 0
    )

    # リスト
    breakdown["has_list"] = SCORE_WEIGHTS["has_list"] if metrics["has_list"] else 0

    # Bold
    breakdown["has_bold"] = SCORE_WEIGHTS["has_bold"] if metrics["has_bold"] else 0

    # 動画（Technique/Drill のみ）
    if content_type in VIDEO_REQUIRED_TYPES:
        breakdown["has_video"] = SCORE_WEIGHTS["has_video"] if metrics["has_video"] else 0
    else:
        # 動画不要ジャンルは自動満点（ペナルティなし）→ 他項目で穴埋め
        breakdown["has_video"] = SCORE_WEIGHTS["has_video"]

    # FAQ
    breakdown["has_faq"] = SCORE_WEIGHTS["has_faq"] if metrics["has_faq"] else 0

    # 内部リンク（3 件以上 + 5 件で bonus）
    breakdown["has_internal_links"] = (
        SCORE_WEIGHTS["has_internal_links"]
        if metrics["internal_link_count"] >= 3
        else 0
    )
    breakdown["internal_links_gte_5"] = (
        SCORE_WEIGHTS["internal_links_gte_5"]
        if metrics["internal_link_count"] >= 5
        else 0
    )

    # 画像 (z245)
    breakdown["has_image"] = SCORE_WEIGHTS["has_image"] if metrics["has_image"] else 0

    total = sum(breakdown.values())
    return min(total, 100), breakdown


def grade(score: int) -> str:
    if score >= EXCELLENT_THRESHOLD: return "🏆 EXCELLENT"
    if score >= POOR_THRESHOLD:      return "✅ GOOD"
    if score >= BAD_THRESHOLD:       return "⚠️  POOR"
    if score >= GARBAGE_THRESHOLD:   return "🔴 BAD"
    return "💀 GARBAGE"


# ─────────────────────────────────────────────────────
# メイン処理
# ─────────────────────────────────────────────────────

def scan_language(lang: str, garbage_only: bool) -> list[dict]:
    lang_dir = WIKI_ROOT / lang
    if not lang_dir.exists():
        print(f"⚠️  {lang}/ ディレクトリが見つかりません")
        return []

    results = []
    html_files = sorted(lang_dir.glob("*.html"))
    print(f"\n📂 {lang}/ — {len(html_files)} ファイル")

    for path in html_files:
        slug = path.stem
        # リダイレクトファイルをスキップ
        html = path.read_text(encoding="utf-8", errors="replace")
        if 'http-equiv="refresh"' in html.lower():
            continue

        metrics = parse_article(html)
        score, breakdown = score_article(metrics)

        if garbage_only and score < BAD_THRESHOLD:
            continue

        results.append({
            "lang":               lang,
            "slug":               slug,
            "score":              score,
            "grade":              grade(score),
            "content_type":       metrics["content_type"],
            "word_count":         metrics["word_count"],
            "h2_count":           metrics["h2_count"],
            "h2_list":            " | ".join(metrics["h2_list"][:5]),
            "has_list":           int(metrics["has_list"]),
            "has_bold":           int(metrics["has_bold"]),
            "has_video":          int(metrics["has_video"]),
            "has_faq":            int(metrics["has_faq"]),
            "internal_links":     metrics["internal_link_count"],
            # スコア内訳
            **{f"pts_{k}": v for k, v in breakdown.items()},
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="BJJ Wiki Quality Auditor")
    parser.add_argument("--lang",         choices=LANGUAGES + ["all"], default="all")
    parser.add_argument("--garbage-only", action="store_true", help="80点未満（目標ライン未達）のみ出力")
    parser.add_argument("--fix-preview",  action="store_true", help="修正提案を表示")
    args = parser.parse_args()

    langs = LANGUAGES if args.lang == "all" else [args.lang]

    all_results = []
    for lang in langs:
        all_results.extend(scan_language(lang, args.garbage_only))

    # ソート（スコア昇順 = ゴミが先頭）
    all_results.sort(key=lambda x: x["score"])

    # CSV 出力
    csv_path = WIKI_ROOT / "quality_report.csv"
    if all_results:
        fieldnames = list(all_results[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\n✅ CSV出力完了: {csv_path}")

    # 80点未満 slug リスト（目標ラインに未達の記事）
    below_target = [r for r in all_results if r["score"] < BAD_THRESHOLD]
    if below_target:
        garbage_path = WIKI_ROOT / "garbage_slugs.txt"
        with open(garbage_path, "w", encoding="utf-8") as f:
            for r in below_target:
                f.write(f"{r['lang']}/{r['slug']}\n")
        print(f"🔴 目標ライン(80)未達: {len(below_target)} 件 → {garbage_path}")

    # サマリー表示
    print(f"\n{'─'*60}")
    print(f"総スキャン: {len(all_results)} 記事")
    bands = [
        ("🏆 EXCELLENT (95+)",  lambda s: s >= EXCELLENT_THRESHOLD),
        ("✅ GOOD     (90-94)", lambda s: POOR_THRESHOLD <= s < EXCELLENT_THRESHOLD),
        ("⚠️  POOR     (80-89)", lambda s: BAD_THRESHOLD <= s < POOR_THRESHOLD),
        ("🔴 BAD      (60-79)", lambda s: GARBAGE_THRESHOLD <= s < BAD_THRESHOLD),
        ("💀 GARBAGE  (<60)",   lambda s: s < GARBAGE_THRESHOLD),
    ]
    for label, cond in bands:
        count = sum(1 for r in all_results if cond(r["score"]))
        print(f"  {label}: {count} 件")

    if all_results:
        avg = sum(r["score"] for r in all_results) / len(all_results)
        print(f"  平均スコア: {avg:.1f}/100")

    # 修正プレビュー（dry-run）
    if args.fix_preview:
        print(f"\n{'─'*60}")
        print("🔧 修正提案（上位10件）:")
        for r in garbage[:10]:
            issues = []
            if r["word_count"] < 600:
                issues.append(f"語数不足({r['word_count']}語→600語必要)")
            if r["h2_count"] < 6:
                issues.append(f"H2不足({r['h2_count']}個→6個必要)")
            if not r["has_list"]:
                issues.append("リストなし")
            if not r["has_bold"]:
                issues.append("Bold強調なし")
            if not r["has_faq"]:
                issues.append("FAQなし")
            print(f"  [{r['score']:3d}] {r['lang']}/{r['slug']}: {', '.join(issues)}")


if __name__ == "__main__":
    main()
