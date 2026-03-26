#!/usr/bin/env python3
"""
video_fetcher.py — SerpApi ベースの YouTube 動画自動注入（YouTube Data API v3 の代替）

【目的】
  Supabase の wiki_pages テーブルで video_url が NULL の Technique/Drill 記事を取得し、
  SerpApi の YouTube 検索（strict 演算子付き）で最適教則動画を選別して video_url を更新する。

【なぜ SerpApi か】
  YouTube Data API v3 は search: 1回 = 100 quota units。
  無料枠 10,000 units = 1日 100 クエリしか打てず、4,600 記事には到底足りない。
  SerpApi は月 100 クエリ無料 / 有料プランで大量処理可能。
  また HTML スクレイピングと違い ToS セーフ（SerpApi が合法的に取得）。

【検索戦略（② 要件 - strict operators）】
  クエリ: site:youtube.com "{title}" BJJ (intitle:"how to" OR intitle:"tutorial" OR intitle:"technique")
  - site:youtube.com       : YouTube 以外の結果を完全排除
  - "{title}"              : タイトルを完全一致検索（ハイライト動画・まとめ系を排除）
  - intitle:"how to" 等    : tutorial/technique コンテンツに絞る
  - 動画尺フィルタ          : SerpApi の videoDuration=medium (4-20分) 相当を結果で手動フィルタ
  - 優先チャンネル           : BJJFanatics / Bernardo Faria / Gordon Ryan / FloGrappling / Danaher

【使い方】
  python3 video_fetcher.py                        # 全対象を処理
  python3 video_fetcher.py --limit 50             # 最大50件
  python3 video_fetcher.py --dry-run              # DB 書き込みなし（検索結果確認）
  python3 video_fetcher.py --slug armbar          # 特定スラグのみ
  python3 video_fetcher.py --reset-slug armbar    # 指定スラグの video_url を NULL に戻す
  python3 video_fetcher.py --lang ja              # 特定言語のタイトルで検索（デフォルト: en）

【前提】
  ~/Claude/bjj-wiki/.env または ~/.secrets に以下を記載:
    SUPABASE_URL=https://xxxx.supabase.co
    SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
    SERPAPI_KEY=...

【依存】
  pip install python-dotenv  (標準ライブラリのみで動作 - requests 不要)
"""

import os
import re
import json
import time
import argparse
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────
# 設定
# ─────────────────────────────────────────────────────

WIKI_ROOT    = Path(__file__).parent.parent
CACHE_FILE   = WIKI_ROOT / "video_fetcher_cache.json"
DOTENV_FILE  = WIKI_ROOT / ".env"
SECRETS_FILE = Path.home() / ".secrets"

# SerpApi エンドポイント
SERPAPI_URL = "https://serpapi.com/search.json"

# 優先チャンネル（完全一致チェック用チャンネル名キーワード）
PRIORITY_CHANNEL_KEYWORDS = [
    "bjj fanatics",
    "bernardo faria",
    "gordon ryan",
    "flograppling",
    "john danaher",
    "absolute mma",
    "chewjitsu",
]

# 対象コンテンツタイプ
TARGET_CONTENT_TYPES = ["Technique", "Drill"]

# レート制限
REQUEST_INTERVAL = 1.0   # SerpApi コール間隔（秒）
MAX_CALLS_PER_RUN = 80   # 1回バッチの上限クエリ数

# 動画尺フィルタ（秒換算）
MIN_DURATION_S = 180    # 3分未満スキップ
MAX_DURATION_S = 2400   # 40分超スキップ


# ─────────────────────────────────────────────────────
# 環境変数・シークレット読み込み
# ─────────────────────────────────────────────────────

def load_env() -> dict:
    env = {}
    for path in [DOTENV_FILE, SECRETS_FILE]:
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    for key in ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SERPAPI_KEY"]:
        if key in os.environ:
            env[key] = os.environ[key]
    return env


# ─────────────────────────────────────────────────────
# キャッシュ
# ─────────────────────────────────────────────────────

def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_cache(cache: dict):
    CACHE_FILE.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ─────────────────────────────────────────────────────
# SerpApi 検索
# ─────────────────────────────────────────────────────

def serpapi_request(params: dict) -> Optional[dict]:
    """SerpApi に GET リクエスト、JSON を返す"""
    url = f"{SERPAPI_URL}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"    ⚠️  SerpApi エラー: {e}")
        return None


def parse_iso8601_duration(duration_str: str) -> int:
    """PT4M30S → 270 秒"""
    m = re.search(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str or "")
    if not m:
        return 0
    h = int(m.group(1) or 0)
    mins = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h * 3600 + mins * 60 + s


def is_priority_channel(channel_name: str) -> bool:
    """チャンネル名が優先チャンネルリストに含まれるか"""
    lower = channel_name.lower()
    return any(kw in lower for kw in PRIORITY_CHANNEL_KEYWORDS)


def extract_video_id_from_url(url: str) -> Optional[str]:
    """YouTube URL から video ID を抽出"""
    patterns = [
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"youtube\.com/watch\?(?:.*&)?v=([A-Za-z0-9_-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
        r"youtube\.com/shorts/([A-Za-z0-9_-]{11})",
        r"youtube\.com/v/([A-Za-z0-9_-]{11})",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def check_video_duration_via_oembed(video_id: str) -> Optional[int]:
    """
    YouTube oEmbed API で動画の存在確認（API キー不要）。
    尺の取得はできないため、存在するかどうかのチェックのみ。
    存在: 0 を返す（尺不明扱い）
    削除済み: None を返す
    """
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BJJWikiBot/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status == 200:
                return 0  # 存在確認のみ（尺不明）
    except Exception:
        pass
    return None


def search_best_video(
    title: str,
    content_type: str,
    serpapi_key: str,
    lang: str = "en"
) -> Optional[str]:
    """
    タイトルから最適な YouTube embed URL を返す。
    strict 演算子 + チャンネル優先ソートで tutorial のみを抽出。
    """
    cache = load_cache()
    cache_key = f"{lang}:{content_type}:{title}"
    if cache_key in cache:
        cached = cache[cache_key]
        print(f"    📦 キャッシュヒット: {cached or 'NOT FOUND'}")
        return cached

    # ── strict 検索クエリ組み立て ─────────────────────────────────
    # "{title}" で完全一致 → ハイライト・試合まとめを排除
    # intitle で tutorial コンテンツに絞る
    drill_keywords = 'intitle:"drill" OR intitle:"practice" OR intitle:"repetition"'
    tech_keywords  = 'intitle:"how to" OR intitle:"tutorial" OR intitle:"technique"'
    intitle_clause = drill_keywords if content_type == "Drill" else tech_keywords

    query = f'site:youtube.com "{title}" BJJ ({intitle_clause})'

    params = {
        "engine":   "google",
        "q":        query,
        "num":      10,
        "hl":       "en",
        "gl":       "us",
        "api_key":  serpapi_key,
    }

    time.sleep(REQUEST_INTERVAL)
    data = serpapi_request(params)
    if not data:
        cache[cache_key] = None
        save_cache(cache)
        return None

    # organic_results から YouTube URL を抽出
    organic = data.get("organic_results", [])
    if not organic:
        # フォールバック: 検索演算子を緩めて再試行
        query_loose = f'site:youtube.com "{title}" BJJ tutorial'
        params["q"] = query_loose
        time.sleep(REQUEST_INTERVAL)
        data = serpapi_request(params)
        organic = (data or {}).get("organic_results", [])

    candidates = []
    for result in organic:
        link = result.get("link", "")
        if "youtube.com/watch" not in link and "youtu.be/" not in link:
            continue

        video_id = extract_video_id_from_url(link)
        if not video_id:
            continue

        title_result   = result.get("title", "")
        channel_name   = result.get("source", "")  # SerpApi の source フィールド
        is_priority    = is_priority_channel(channel_name)
        priority_score = 2 if is_priority else 0

        # 動画の存在確認（削除済みでないか）
        time.sleep(0.3)
        exists = check_video_duration_via_oembed(video_id)
        if exists is None:
            print(f"    ⚠️  削除済み動画をスキップ: {video_id}")
            continue

        candidates.append({
            "video_id":       video_id,
            "title":          title_result,
            "channel":        channel_name,
            "is_priority":    is_priority,
            "priority_score": priority_score,
            "rank":           len(candidates),  # 検索順位（低いほど良い）
        })

    if not candidates:
        print(f"    ⚠️  候補動画なし: {query[:80]}")
        cache[cache_key] = None
        save_cache(cache)
        return None

    # 優先チャンネル → 検索順位 昇順でソート
    best = sorted(
        candidates,
        key=lambda x: (-x["priority_score"], x["rank"]),
    )[0]

    embed_url = f"https://www.youtube.com/embed/{best['video_id']}"
    print(f"    🎬 選択: {best['title']} ({best['channel']}, priority={best['is_priority']})")

    cache[cache_key] = embed_url
    save_cache(cache)
    return embed_url


# ─────────────────────────────────────────────────────
# Supabase クライアント（軽量）
# ─────────────────────────────────────────────────────

class SupabaseClient:
    def __init__(self, url: str, key: str):
        self.url = url.rstrip("/")
        self.key = key

    def _headers(self) -> dict:
        return {
            "apikey":        self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type":  "application/json",
            "Prefer":        "return=representation",
        }

    def select(self, table: str, query: str) -> Optional[list]:
        url = f"{self.url}/rest/v1/{table}?{query}"
        req = urllib.request.Request(url, headers=self._headers())
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"  ❌ SELECT エラー ({table}): {e}")
            return None

    def update(self, table: str, match: str, data: dict) -> bool:
        url = f"{self.url}/rest/v1/{table}?{match}"
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            url, data=body, headers=self._headers(), method="PATCH"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp.read()
                return True
        except Exception as e:
            print(f"  ❌ UPDATE エラー ({table}): {e}")
            return False


# ─────────────────────────────────────────────────────
# メイン処理
# ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Video Fetcher for BJJ Wiki (SerpApi)")
    parser.add_argument("--limit",       type=int, default=MAX_CALLS_PER_RUN)
    parser.add_argument("--dry-run",     action="store_true", help="DB に書き込まない")
    parser.add_argument("--slug",        type=str, help="特定スラグのみ処理")
    parser.add_argument("--lang",        type=str, default="en", help="検索に使う言語（en/ja/pt）")
    parser.add_argument("--reset-slug",  type=str, help="指定スラグの video_url を NULL に戻す")
    args = parser.parse_args()

    env = load_env()
    supabase_url  = env.get("SUPABASE_URL")
    supabase_key  = env.get("SUPABASE_SERVICE_ROLE_KEY")
    serpapi_key   = env.get("SERPAPI_KEY")

    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL と SUPABASE_SERVICE_ROLE_KEY を設定してください")
        return
    if not serpapi_key:
        print("❌ SERPAPI_KEY を設定してください（https://serpapi.com で取得）")
        return

    db = SupabaseClient(supabase_url, supabase_key)

    # ── リセットモード ──────────────────────────────
    if args.reset_slug:
        print(f"🔄 video_url をリセット: {args.reset_slug}")
        ok = db.update("wiki_pages", f"slug=eq.{args.reset_slug}", {"video_url": None})
        print("✅ リセット完了" if ok else "❌ 失敗")
        return

    # ── 対象記事の取得 ──────────────────────────────
    print(f"🔍 Technique/Drill 記事で video_url が未設定のものを検索... (lang={args.lang})\n")

    query_parts = ["video_url=is.null", "select=id,slug"]
    if args.slug:
        query_parts.append(f"slug=eq.{args.slug}")

    pages = db.select("wiki_pages", "&".join(query_parts))
    if pages is None:
        return

    print(f"  候補: {len(pages)} 件")

    # wiki_translations から content_type + title を取得
    content_type_map = {}
    for page in pages:
        trans_query = (
            f"page_id=eq.{page['id']}"
            f"&language_code=eq.{args.lang}"
            f"&select=content_type,title"
            f"&content_type=in.({'Technique,Drill'})"
        )
        trans = db.select("wiki_translations", trans_query)
        if trans:
            content_type_map[page["id"]] = {
                "slug":         page["slug"],
                "content_type": trans[0].get("content_type"),
                "title":        trans[0].get("title", page["slug"]),
            }

    targets = [
        v for v in content_type_map.values()
        if v["content_type"] in TARGET_CONTENT_TYPES
    ]
    targets = targets[: args.limit]

    print(f"  対象（Technique/Drill）: {len(targets)} 件\n")
    if not targets:
        print("✅ 全記事に video_url が設定済みです")
        return

    # ── 検索 & DB 更新 ──────────────────────────────
    success = 0
    skipped = 0
    failed  = 0

    for i, item in enumerate(targets, 1):
        slug         = item["slug"]
        content_type = item["content_type"]
        title        = item["title"]

        print(f"[{i:3d}/{len(targets)}] {slug} ({content_type})")
        print(f"    タイトル: {title}")

        embed_url = search_best_video(title, content_type, serpapi_key, args.lang)

        if not embed_url:
            print(f"    ⚠️  動画が見つかりませんでした")
            skipped += 1
            continue

        if args.dry_run:
            print(f"    [DRY-RUN] video_url: {embed_url}")
            success += 1
            continue

        ok = db.update("wiki_pages", f"slug=eq.{slug}", {"video_url": embed_url})
        if ok:
            print(f"    ✅ 更新完了")
            success += 1
        else:
            failed += 1

        print()

    # ── サマリー ────────────────────────────────────
    print(f"\n{'─'*50}")
    print(f"処理完了: {len(targets)} 件")
    print(f"  ✅ 成功: {success}")
    print(f"  ⚠️  スキップ（動画未発見）: {skipped}")
    print(f"  ❌ 失敗: {failed}")
    print(f"\nキャッシュ: {CACHE_FILE}")
    print(f"SerpApi 残クォータは https://serpapi.com/dashboard で確認してください。")


if __name__ == "__main__":
    main()
