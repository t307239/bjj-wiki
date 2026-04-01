#!/usr/bin/env python3
"""
scripts/score_quality.py

wiki_translations の content_html を採点して quality_score / quality_flags を更新する。
GitHub Actions の migrate ステップ後に実行される。

採点基準 (合計100点) — 構造チェック重視 (文字数非依存):
  - H2 セクション数  0-30点  (6個+ → 30, 4-5個 → 22, 2-3個 → 15, 1個 → 5, 0個 → 0)
  - FAQ セクション   0-25点  (3 Q&A → 25, 2 Q&A → 17, 1 Q&A → 9, なし → 0)
  - 動画 iframe      0-25点  (<iframe ... youtube → 25, YouTube リンクのみ → 15, なし → 0)
  - 内部リンク数     0-20点  (3個+ → 20, 1-2個 → 10, なし → 0)

精度ペナルティ (最大 -20点) — デマ・品質問題を自動検出:
  - 重複セクション検出     -5点  (同じ h2 テキストが2回以上)
  - 安全警告の不整合       -5点  (脚部テクニックで腕の警告、等)
  - 制限技のベルト警告欠如 -5点  (ヒールフック/ニーバー等に白帯警告なし)
  - 希薄コンテンツ検出     -5点  (極端に短い or 繰り返しのみのコンテンツ)
  → total = max(0, base_score - accuracy_penalty)

使い方:
  python scripts/score_quality.py
  python scripts/score_quality.py --lang en  # 特定言語のみ
  python scripts/score_quality.py --dry-run  # スコア表示のみ、DB更新なし
"""

import os
import sys
import json
import re
import argparse
import urllib.request
import urllib.error
from html.parser import HTMLParser


# ─────────────────────────────────────────
# 設定
# ─────────────────────────────────────────

SUPABASE_URL      = os.environ.get("SUPABASE_URL", "")
SERVICE_ROLE_KEY  = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
LANGUAGES         = ["en", "ja", "pt"]
BATCH_SIZE        = 100  # Supabase REST API per-request limit


# ─────────────────────────────────────────
# Supabase REST ヘルパー
# ─────────────────────────────────────────

def _headers():
    return {
        "apikey":        SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=minimal",
    }


def supabase_get(path: str) -> list:
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def supabase_patch(table: str, row_id: int, payload: dict):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{row_id}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=_headers(), method="PATCH")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status


# ─────────────────────────────────────────
# 採点ロジック
# ─────────────────────────────────────────

class TagCounter(HTMLParser):
    """HTML 内の特定タグ・テキストを高速カウント"""
    def __init__(self):
        super().__init__()
        self.h2_count    = 0
        self.a_hrefs     = []
        self.faq_q_count = 0
        self.has_youtube = False

    def handle_starttag(self, tag, attrs):
        if tag == "h2":
            self.h2_count += 1
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.a_hrefs.append(v)
                    if "youtube.com" in v or "youtu.be" in v:
                        self.has_youtube = True

    def handle_data(self, data):
        if "faq-q" in data.lower() or re.search(r"^\s*Q:\s", data):
            pass  # handled via class check

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def score_content(content_html: str, slug: str = "") -> tuple[int, dict]:
    """
    content_html を採点して (score: int, flags: dict) を返す。
    flags: 各軸の得点と不足項目を記録する辞書
    文字数スコアを廃止し、構造チェック4軸で100点満点に。
    """
    if not content_html or len(content_html) < 50:
        return 0, {"error": "empty_content"}

    html = content_html

    # --- H2 セクション数 (0-30点) ---
    h2_count = len(re.findall(r"<h2[\s>]", html, re.IGNORECASE))
    if h2_count >= 6:
        h2_score = 30
    elif h2_count >= 4:
        h2_score = 22
    elif h2_count >= 2:
        h2_score = 15
    elif h2_count == 1:
        h2_score = 5
    else:
        h2_score = 0

    # --- FAQ セクション (0-25点) ---
    # faq-q クラスまたは "Q:" パターンをカウント
    faq_count = len(re.findall(r'class=["\']faq-q["\']', html)) or len(re.findall(r">\s*Q:\s", html))
    if faq_count >= 3:
        faq_score = 25
    elif faq_count == 2:
        faq_score = 17
    elif faq_count == 1:
        faq_score = 9
    else:
        faq_score = 0

    # --- 動画 iframe (0-25点) ---
    # <iframe src="...youtube..."> を優先検出。リンクのみの場合は部分点
    has_iframe = bool(re.search(r"<iframe[^>]+(?:youtube\.com|youtu\.be)", html, re.IGNORECASE))
    has_yt_link = bool(re.search(r"youtube\.com|youtu\.be", html, re.IGNORECASE))
    if has_iframe:
        vid_score = 25
    elif has_yt_link:
        vid_score = 15
    else:
        vid_score = 0
    has_video = has_yt_link  # 後方互換フラグ

    # --- 内部リンク数 (0-20点) ---
    # <a href="../en/slug.html"> または <a href="../slug.html"> パターン
    internal_links = re.findall(r'href=["\']\.\.\/[a-z]{2}\/[a-z][^"\']+\.html["\']', html)
    if len(internal_links) >= 3:
        link_score = 20
    elif len(internal_links) >= 1:
        link_score = 10
    else:
        link_score = 0

    base_score = h2_score + faq_score + vid_score + link_score

    # 精度ペナルティを適用
    accuracy_penalty, accuracy_flags = check_accuracy(html, slug=slug)
    total = max(0, base_score - accuracy_penalty)

    flags = {
        "h2_score":       h2_score,
        "faq_score":      faq_score,
        "vid_score":      vid_score,
        "link_score":     link_score,
        "h2_count":       h2_count,
        "faq_count":      faq_count,
        "has_video":      has_video,
        "has_iframe":     has_iframe,
        "internal_links": len(internal_links),
        # G: セクション完全性チェック
        "missing_sections": _check_missing_sections(html),
        # 精度チェック
        **accuracy_flags,
    }

    return total, flags


def _check_missing_sections(html: str) -> list:
    """G: 必須セクションが揃っているかチェックして不足リストを返す"""
    missing = []
    checks = [
        ("grips_mechanics",   r"grips?\s*&amp;\s*mechanics|グリップ|pegadas",   re.IGNORECASE),
        ("white_belt_warn",   r"white belt warnings?|白帯|faixa branca",         re.IGNORECASE),
        ("drill_progression", r"drill progression|ドリル段階|progressão",        re.IGNORECASE),
        ("counters",          r"counters?|when to use|カウンター|defesas",        re.IGNORECASE),
        ("faq",               r'class=["\']faq|common bjj problems|よくある質問|perguntas', re.IGNORECASE),
    ]
    for name, pattern, flags in checks:
        if not re.search(pattern, html, flags):
            missing.append(name)
    return missing


# ─────────────────────────────────────────
# 精度チェック (デマ・品質問題検出)
# ─────────────────────────────────────────

# 制限技キーワード → 白帯に不適切な技
_RESTRICTED_TECHNIQUES = [
    "heel hook", "heelhook", "inside heel hook", "outside heel hook",
    "kneebar", "knee bar", "toe hold", "toehold", "calf slicer",
    "can opener",  # cervical compression
]

# 技タイプ → 正しい安全警告の体の部位マッピング
_BODY_PART_SAFETY_MAP = {
    # 手首系
    "wrist lock": ["wrist", "手首", "pulso"],
    "kimura": ["shoulder", "肩", "ombro"],
    "americana": ["shoulder", "肩", "ombro"],
    # 肘系
    "armbar": ["elbow", "肘", "cotovelo"],
    "arm bar": ["elbow", "肘", "cotovelo"],
    "bicep slicer": ["elbow", "bicep", "肘", "cotovelo"],
    # 足系
    "heel hook": ["knee", "joelho", "膝"],
    "kneebar": ["knee", "joelho", "膝"],
    "toe hold": ["knee", "ankle", "joelho", "tornozelo", "膝", "足首"],
    "ankle lock": ["ankle", "tornozelo", "足首"],
    # 頸椎系
    "can opener": ["spine", "neck", "cervical", "頸椎", "首", "coluna"],
    "twister": ["spine", "neck", "cervical", "頸椎", "首", "coluna"],
}

# 誤った体部位の警告 (e.g. "heel hook" に "shoulder" 警告 → 誤り)
_WRONG_BODY_PART_COMBOS = [
    # (tech_keyword, wrong_body_part) — 技名に対して*誤った*体部位が安全警告に使われている場合
    ("heel hook",    r"especially to the shoulder|especially to the wrist|especially to the elbow\b"),
    ("kneebar",      r"especially to the shoulder|especially to the wrist"),
    ("armbar",       r"especially to the knee|especially to the ankle"),
    ("arm bar",      r"especially to the knee|especially to the ankle"),
    ("wrist lock",   r"especially to the knee|especially to the ankle|especially to the elbow\b"),
    ("kimura",       r"especially to the knee|especially to the ankle|especially to the elbow\b"),
    ("ankle lock",   r"especially to the shoulder|especially to the wrist|especially to the elbow\b"),
    ("bicep slicer", r"especially to the knee|especially to the ankle|especially to the wrist"),
    ("can opener",   r"especially to the shoulder|especially to the wrist|especially to the elbow\b|especially to the knee|especially to the ankle"),
]


def check_accuracy(html: str, slug: str = "") -> tuple[int, dict]:
    """
    精度チェックを実行してペナルティと詳細フラグを返す。

    Returns:
        (penalty: int, accuracy_flags: dict)
        penalty は 0〜20 の整数 (最大 -20点)
    """
    flags = {}
    penalty = 0
    html_lower = html.lower()

    # ① 重複セクション検出 (-5点)
    h2_texts = re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.IGNORECASE | re.DOTALL)
    # HTMLタグを除去してテキスト化
    def strip_tags(s): return re.sub(r"<[^>]+>", "", s).strip().lower()
    h2_clean = [strip_tags(t) for t in h2_texts if strip_tags(t)]
    duplicates = [t for t in set(h2_clean) if h2_clean.count(t) >= 2]
    if duplicates:
        penalty += 5
        flags["duplicate_sections"] = duplicates
    else:
        flags["duplicate_sections"] = []

    # ② 安全警告の不整合 (-5点) — 技と体部位のミスマッチ
    # slug が渡されている場合はそのページの主技のみチェック (false positive 防止)
    # slug がない場合は技名が本文中に3回以上登場する場合のみチェック
    wrong_combos = []
    slug_lower = slug.lower().replace("-", " ").replace("_", " ")
    for tech, wrong_pattern in _WRONG_BODY_PART_COMBOS:
        # スラッグに技名が含まれる OR 本文中に3回以上登場する場合のみ対象
        tech_in_slug = tech in slug_lower
        tech_count = html_lower.count(tech)
        if tech_in_slug or tech_count >= 3:
            if re.search(wrong_pattern, html, re.IGNORECASE):
                wrong_combos.append({"technique": tech, "wrong_warning": wrong_pattern})
    if wrong_combos:
        penalty += 5
        flags["safety_warning_mismatch"] = wrong_combos
    else:
        flags["safety_warning_mismatch"] = []

    # ③ 制限技のベルト警告欠如 (-5点)
    # ヒールフック/ニーバー等が含まれるのに白帯警告がない場合
    has_restricted = any(tech in html_lower for tech in _RESTRICTED_TECHNIQUES)
    has_belt_warn = bool(re.search(
        r"white belt|blue belt|not recommended for beginner|初心者|白帯|blue/white|intermediate|advanced only|"
        r"faixa branca|faixa azul|não recomendado|beginner caution",
        html, re.IGNORECASE
    ))
    missing_belt_warn = has_restricted and not has_belt_warn
    if missing_belt_warn:
        penalty += 5
        flags["missing_belt_warning"] = True
    else:
        flags["missing_belt_warning"] = False

    # ④ 希薄コンテンツ検出 (-5点)
    # 本文テキストが極端に短い、または同一文が3回以上繰り返されている
    text_only = re.sub(r"<[^>]+>", " ", html)
    text_only = re.sub(r"\s+", " ", text_only).strip()
    word_count = len(text_only.split())

    # 繰り返しチェック: 連続する50文字以上のフレーズが複数回現れる
    sentences = re.findall(r"[A-Za-z\u3040-\u30ffぁ-ん][^.!?。！？]{40,}[.!?。！？]", text_only)
    repeated = [s for s in set(sentences) if sentences.count(s) >= 3]

    thin_content = word_count < 80 or len(repeated) > 0
    if thin_content:
        penalty += 5
        flags["thin_content"] = {
            "word_count": word_count,
            "repeated_phrases": len(repeated),
        }
    else:
        flags["thin_content"] = None

    flags["accuracy_penalty"] = penalty
    return penalty, flags


# ─────────────────────────────────────────
# メイン処理
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", default="all", help="採点する言語 (en/ja/pt/all)")
    parser.add_argument("--dry-run", action="store_true", help="DB更新なし、スコア表示のみ")
    parser.add_argument("--limit", type=int, default=0, help="処理件数上限 (0=全件)")
    args = parser.parse_args()

    if not SUPABASE_URL or not SERVICE_ROLE_KEY:
        print("❌ SUPABASE_URL と SUPABASE_SERVICE_ROLE_KEY を設定してください")
        sys.exit(1)

    langs = LANGUAGES if args.lang == "all" else [args.lang]

    total_updated = 0
    score_distribution = {range(0, 20): 0, range(20, 40): 0, range(40, 60): 0,
                          range(60, 80): 0, range(80, 101): 0}

    for lang in langs:
        print(f"\n📊 [{lang}] 採点開始...")
        offset = 0
        lang_updated = 0
        lang_scores  = []

        while True:
            # ページネーション取得 (slug を精度チェックに使用)
            path = (f"wiki_translations?language_code=eq.{lang}"
                    f"&select=id,content_html,slug"
                    f"&offset={offset}&limit={BATCH_SIZE}")
            try:
                rows = supabase_get(path)
            except Exception as e:
                print(f"  ❌ 取得失敗: {e}")
                break

            if not rows:
                break

            for row in rows:
                row_id       = row["id"]
                content_html = row.get("content_html", "") or ""
                slug         = row.get("slug", "") or ""

                score, flags = score_content(content_html, slug=slug)
                lang_scores.append(score)

                if not args.dry_run:
                    try:
                        supabase_patch("wiki_translations", row_id, {
                            "quality_score": score,
                            "quality_flags": flags,
                        })
                        lang_updated += 1
                    except Exception as e:
                        print(f"  ⚠️  id={row_id} 更新失敗: {e}")

                if args.limit and lang_updated >= args.limit:
                    break

            offset += BATCH_SIZE
            print(f"  ... {offset} 件処理済み")

            if len(rows) < BATCH_SIZE:
                break
            if args.limit and lang_updated >= args.limit:
                break

        total_updated += lang_updated
        if lang_scores:
            avg = sum(lang_scores) / len(lang_scores)
            low = sum(1 for s in lang_scores if s < 40)
            print(f"  ✅ [{lang}] {lang_updated}件更新 | 平均: {avg:.1f}点 | 低品質(<40): {low}件")

    print(f"\n✅ 採点完了: 合計 {total_updated} 件更新")


if __name__ == "__main__":
    main()
