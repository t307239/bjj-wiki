#!/usr/bin/env python3
"""
scripts/score_quality.py

wiki_translations の content_html を採点して quality_score / quality_flags を更新する。
GitHub Actions の migrate ステップ後に実行される。

採点基準 (合計100点):
  - コンテンツ長     0-30点  (3k+ → 30, 2k+ → 20, 1k+ → 10, それ以下 → 0)
  - H2 セクション数  0-25点  (6個+ → 25, 4-5個 → 18, 2-3個 → 10, 1個 → 5, 0個 → 0)
  - FAQ セクション   0-20点  (3 Q&A → 20, 2 Q&A → 13, 1 Q&A → 7, なし → 0)
  - 動画リンク       0-15点  (YouTube リンクあり → 15)
  - 内部リンク数     0-10点  (3個+ → 10, 1-2個 → 5, なし → 0)

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


def score_content(content_html: str) -> tuple[int, dict]:
    """
    content_html を採点して (score: int, flags: dict) を返す。
    flags: 各軸の得点と不足項目を記録する辞書
    """
    if not content_html or len(content_html) < 50:
        return 0, {"error": "empty_content"}

    html = content_html

    # --- コンテンツ長 ---
    text_only = re.sub(r"<[^>]+>", "", html)
    char_len   = len(text_only.strip())
    if char_len >= 4000:
        len_score = 30
    elif char_len >= 3000:
        len_score = 25
    elif char_len >= 2000:
        len_score = 20
    elif char_len >= 1000:
        len_score = 10
    else:
        len_score = 0

    # --- H2 セクション数 ---
    h2_count = len(re.findall(r"<h2[\s>]", html, re.IGNORECASE))
    if h2_count >= 6:
        h2_score = 25
    elif h2_count >= 4:
        h2_score = 18
    elif h2_count >= 2:
        h2_score = 10
    elif h2_count == 1:
        h2_score = 5
    else:
        h2_score = 0

    # --- FAQ セクション ---
    # faq-q クラスまたは "Q:" パターンをカウント
    faq_count = len(re.findall(r'class=["\']faq-q["\']', html)) or len(re.findall(r">\s*Q:\s", html))
    if faq_count >= 3:
        faq_score = 20
    elif faq_count == 2:
        faq_score = 13
    elif faq_count == 1:
        faq_score = 7
    else:
        faq_score = 0

    # --- 動画リンク ---
    has_video = bool(re.search(r"youtube\.com|youtu\.be", html, re.IGNORECASE))
    vid_score = 15 if has_video else 0

    # --- 内部リンク ---
    # <a href="../en/slug.html"> または <a href="../slug.html"> パターン
    internal_links = re.findall(r'href=["\']\.\.\/[a-z]{2}\/[a-z][^"\']+\.html["\']', html)
    if len(internal_links) >= 3:
        link_score = 10
    elif len(internal_links) >= 1:
        link_score = 5
    else:
        link_score = 0

    total = len_score + h2_score + faq_score + vid_score + link_score

    flags = {
        "len_score":      len_score,
        "h2_score":       h2_score,
        "faq_score":      faq_score,
        "vid_score":      vid_score,
        "link_score":     link_score,
        "char_len":       char_len,
        "h2_count":       h2_count,
        "faq_count":      faq_count,
        "has_video":      has_video,
        "internal_links": len(internal_links),
        # G: セクション完全性チェック
        "missing_sections": _check_missing_sections(html),
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
            # ページネーション取得
            path = (f"wiki_translations?language_code=eq.{lang}"
                    f"&select=id,content_html"
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

                score, flags = score_content(content_html)
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
