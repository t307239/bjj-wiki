#!/usr/bin/env python3
"""
youtube_enricher.py — YouTube Data API v3 による動画 URL 一括注入

Supabase の wiki_pages テーブルで video_url が NULL の Technique/Drill 記事を取得し、
YouTube Data API で最適動画を検索して video_url を更新する。

使い方:
    python3 youtube_enricher.py                        # 全対象記事を処理
    python3 youtube_enricher.py --limit 50             # 最大50件
    python3 youtube_enricher.py --dry-run              # DBへの書き込みなし（検索結果確認）
    python3 youtube_enricher.py --slug armbar          # 特定スラグのみ
    python3 youtube_enricher.py --reset-slug armbar    # 特定スラグのvideo_urlをNULLに戻す

前提:
    - ~/Claude/bjj-wiki/.env に以下を記載:
        SUPABASE_URL=https://xxxx.supabase.co
        SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
        YOUTUBE_API_KEY=AIzaSy...

    - または ~/.secrets に同キーを記載（既存スクリプトと互換）

依存: pip install supabase（supabase-py）
     pip install python-dotenv

アルゴリズム戦略:
    1. 検索クエリ: "{slug title} BJJ tutorial"
    2. 優先チャンネル: BJJFanatics, Bernardo Faria, Gordon Ryan, John Danaher
    3. フィルタ: videoDuration=medium(4〜20分)以上, viewCount > 10,000
    4. フォールバック: viewCount 降順で最上位を選択
    5. キャッシュ: youtube_video_cache.json で API 節約
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
CACHE_FILE   = WIKI_ROOT / "youtube_video_cache.json"
DOTENV_FILE  = WIKI_ROOT / ".env"
SECRETS_FILE = Path.home() / ".secrets"

# YouTube API
YT_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YT_VIDEO_URL  = "https://www.googleapis.com/youtube/v3/videos"

# 優先チャンネル ID（BJJFanatics 系の教則動画が多いチャンネル）
PRIORITY_CHANNELS = {
    "UCJ5v_MCU0cEBBCEQpnkHKJg": "BJJFanatics",         # BJJ Fanatics
    "UCYsRsqOzTxlPFZZRhkT-fPA": "Bernardo Faria BJJ",  # Bernardo Faria
    "UC4HqXzM3RYLKSO3dlyqBXFQ": "Gordon Ryan",          # Gordon Ryan
    "UCHmBrST_87T0IfQ_v3RRTPA": "FloGrappling",         # FloGrappling
    "UCzBqFwu_ZJVnlFYAuSFhQEQ": "John Danaher",         # Danaher
}

# 対象コンテンツタイプ
TARGET_CONTENT_TYPES = ["Technique", "Drill"]

# レート制限
REQUEST_INTERVAL   = 0.5   # API コール間隔（秒）
QUOTA_COST_SEARCH  = 100   # search: 100 quota units/call
QUOTA_COST_VIDEOS  = 1     # videos: 1 quota unit/call
DAILY_QUOTA        = 10000 # YouTube Data API v3 無料枠
MAX_CALLS_PER_RUN  = 80    # 1回のバッチで消費する search コール上限


# ─────────────────────────────────────────────────────
# 環境変数・シークレット読み込み
# ─────────────────────────────────────────────────────

def load_env() -> dict:
    env = {}

    # .env ファイル
    for path in [DOTENV_FILE, SECRETS_FILE]:
        if path.exists():
            for line in path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()

    # OS 環境変数が優先
    for key in ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "YOUTUBE_API_KEY"]:
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
# YouTube API
# ─────────────────────────────────────────────────────

def yt_request(url: str) -> Optional[dict]:
    """YouTube API に GET リクエスト、JSON を返す"""
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"    ⚠️  API エラー: {e}")
        return None


def get_video_stats(video_id: str, api_key: str) -> Optional[dict]:
    """動画の viewCount / duration を取得"""
    params = urllib.parse.urlencode({
        "part": "statistics,contentDetails",
        "id":   video_id,
        "key":  api_key,
    })
    data = yt_request(f"{YT_VIDEO_URL}?{params}")
    if not data or not data.get("items"):
        return None
    item = data["items"][0]
    return {
        "view_count": int(item["statistics"].get("viewCount", 0)),
        "duration":   item["contentDetails"].get("duration", ""),
    }


def iso8601_to_seconds(duration: str) -> int:
    """PT4M30S → 270 秒に変換"""
    m = re.search(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not m:
        return 0
    h = int(m.group(1) or 0)
    mins = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h * 3600 + mins * 60 + s


def search_best_video(title: str, content_type: str, api_key: str) -> Optional[str]:
    """
    タイトルから最適な YouTube 動画の embed URL を返す。
    キャッシュがある場合はそちらを使う。
    """
    cache = load_cache()
    cache_key = f"{content_type}:{title}"
    if cache_key in cache:
        print(f"    📦 キャッシュヒット: {cache[cache_key]}")
        return cache[cache_key]

    # 検索クエリを組み立て
    query = f"{title} BJJ tutorial technique"
    if content_type == "Drill":
        query = f"{title} BJJ drill practice"

    params = urllib.parse.urlencode({
        "part":             "snippet",
        "q":                query,
        "type":             "video",
        "maxResults":       10,
        "relevanceLanguage": "en",
        "safeSearch":       "none",
        "videoDuration":    "medium",  # 4〜20分
        "key":              api_key,
    })

    time.sleep(REQUEST_INTERVAL)
    data = yt_request(f"{YT_SEARCH_URL}?{params}")
    if not data or not data.get("items"):
        cache[cache_key] = None
        save_cache(cache)
        return None

    candidates = []
    for item in data["items"]:
        vid_id      = item["id"].get("videoId")
        channel_id  = item["snippet"].get("channelId", "")
        channel_name = item["snippet"].get("channelTitle", "")
        vid_title   = item["snippet"].get("title", "")

        if not vid_id:
            continue

        # 優先チャンネルかどうか
        is_priority = channel_id in PRIORITY_CHANNELS
        priority_score = 2 if is_priority else 0

        # 動画統計を取得
        time.sleep(REQUEST_INTERVAL)
        stats = get_video_stats(vid_id, api_key)
        view_count  = stats["view_count"] if stats else 0
        duration_s  = iso8601_to_seconds(stats["duration"]) if stats else 0

        # フィルタ: 3分未満 or 40分超はスキップ
        if duration_s < 180 or duration_s > 2400:
            continue

        candidates.append({
            "video_id":      vid_id,
            "title":         vid_title,
            "channel":       channel_name,
            "view_count":    view_count,
            "is_priority":   is_priority,
            "priority_score": priority_score,
        })

    if not candidates:
        cache[cache_key] = None
        save_cache(cache)
        return None

    # 優先チャンネル → viewCount 降順でソート
    best = sorted(
        candidates,
        key=lambda x: (x["priority_score"], x["view_count"]),
        reverse=True,
    )[0]

    embed_url = f"https://www.youtube.com/embed/{best['video_id']}"
    print(f"    🎬 選択: {best['title']} ({best['channel']}, {best['view_count']:,} views)")

    cache[cache_key] = embed_url
    save_cache(cache)
    return embed_url


# ─────────────────────────────────────────────────────
# Supabase クライアント（軽量実装）
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
    parser = argparse.ArgumentParser(description="YouTube Video Enricher for BJJ Wiki")
    parser.add_argument("--limit",       type=int, default=MAX_CALLS_PER_RUN)
    parser.add_argument("--dry-run",     action="store_true", help="DB に書き込まない")
    parser.add_argument("--slug",        type=str, help="特定スラグのみ処理")
    parser.add_argument("--reset-slug",  type=str, help="指定スラグの video_url を NULL に戻す")
    args = parser.parse_args()

    env = load_env()
    supabase_url = env.get("SUPABASE_URL")
    supabase_key = env.get("SUPABASE_SERVICE_ROLE_KEY")
    yt_api_key   = env.get("YOUTUBE_API_KEY")

    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL と SUPABASE_SERVICE_ROLE_KEY を設定してください")
        return
    if not yt_api_key:
        print("❌ YOUTUBE_API_KEY を設定してください")
        return

    db = SupabaseClient(supabase_url, supabase_key)

    # ── リセットモード ──────────────────────────────
    if args.reset_slug:
        print(f"🔄 video_url をリセット: {args.reset_slug}")
        ok = db.update("wiki_pages", f"slug=eq.{args.reset_slug}", {"video_url": None})
        print("✅ リセット完了" if ok else "❌ 失敗")
        return

    # ── 対象記事の取得 ──────────────────────────────
    print("🔍 Technique/Drill 記事で video_url が未設定のものを検索...\n")

    # wiki_pages (video_url IS NULL) を取得
    query_parts = ["video_url=is.null", "select=id,slug"]
    if args.slug:
        query_parts.append(f"slug=eq.{args.slug}")

    pages = db.select("wiki_pages", "&".join(query_parts))
    if pages is None:
        return

    print(f"  候補: {len(pages)} 件")

    # wiki_translations から content_type を取得（EN のみ）
    content_type_map = {}
    for page in pages:
        trans_query = (
            f"page_id=eq.{page['id']}"
            f"&language_code=eq.en"
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

    # フィルタ: Technique/Drill のみ
    targets = [
        v for v in content_type_map.values()
        if v["content_type"] in TARGET_CONTENT_TYPES
    ]
    targets = targets[: args.limit]

    print(f"  対象（Technique/Drill）: {len(targets)} 件\n")
    if not targets:
        print("✅ 全記事に video_url が設定済みです")
        return

    # ── 動画検索 & DB 更新 ──────────────────────────
    success = 0
    skipped = 0
    failed  = 0

    for i, item in enumerate(targets, 1):
        slug         = item["slug"]
        content_type = item["content_type"]
        title        = item["title"]

        print(f"[{i:3d}/{len(targets)}] {slug} ({content_type})")
        print(f"    タイトル: {title}")

        embed_url = search_best_video(title, content_type, yt_api_key)

        if not embed_url:
            print(f"    ⚠️  動画が見つかりませんでした")
            skipped += 1
            continue

        if args.dry_run:
            print(f"    [DRY-RUN] video_url: {embed_url}")
            success += 1
            continue

        # DB 更新
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
    print(f"次回バッチまで YouTube API クォータ残量を確認してください。")
    print(f"（1回の search = 100 quota units）")


if __name__ == "__main__":
    main()
