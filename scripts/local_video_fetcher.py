#!/usr/bin/env python3
"""
local_video_fetcher.py — ローカル実行・YouTube 動画自動取得（API キー不要）

【設計思想】
  Adapter Pattern により「検索バックエンド」と「処理ロジック」を完全分離。
  バックエンドを差し替えても DB 更新・エラーハンドリング・冪等性チェックの
  コードは一切変更不要。

  ┌─────────────────────────────────────────────────────────────────┐
  │  VideoFetcherEngine（処理ロジック）                              │
  │    ├── 冪等性: video_url が既に設定済みの slug はスキップ        │
  │    ├── 日次レート制限: MAX_DAILY_CALLS = 80                      │
  │    ├── キュー: 上限超過分は fetch_queue.json に積んで翌日処理    │
  │    └── DB 更新 / エラーハンドリング                              │
  │                               │                                  │
  │  VideoSearcher（ABC）                                            │
  │    ├── LocalYouTubeSearcher  ← requests + ytInitialData 解析    │
  │    └── OfficialAPISearcher   ← YouTube Data API v3（将来用）    │
  └─────────────────────────────────────────────────────────────────┘

【Mac ターミナルでの使い方】
  cd ~/Claude/bjj-wiki

  # 通常実行（--limit 50 推奨・最初は dry-run で確認）
  python3 scripts/local_video_fetcher.py --dry-run --limit 10
  python3 scripts/local_video_fetcher.py --limit 50

  # キューに積まれた翌日分を処理
  python3 scripts/local_video_fetcher.py --from-queue

  # 特定スラグだけ強制再取得（video_url がある場合も上書き）
  python3 scripts/local_video_fetcher.py --slug armbar --force

  # バックエンドを YouTube Data API に切り替え（API key 必要）
  python3 scripts/local_video_fetcher.py --backend api --limit 50

【前提環境】
  pip install requests
  ~/Claude/bjj-wiki/.env または ~/.secrets に:
    SUPABASE_URL=https://xxxx.supabase.co
    SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
    YOUTUBE_API_KEY=AIza...  # --backend api 時のみ必要

【冪等性ルール】
  - wiki_pages.video_url が NULL の slug のみ処理対象
  - 途中で中断 → 再実行しても重複・上書きなし
  - --force フラグで既存 video_url を強制上書き（単体スラグ向け）

【日次レート制限】
  MAX_DAILY_CALLS = 80  (YouTube への HTTP リクエスト数)
  - 使用量を rate_limit_state.json に記録（UTC 日付でリセット）
  - 80 件超過した slug はキュー（fetch_queue.json）に積む
  - 翌日 --from-queue で消化
"""

from __future__ import annotations

import abc
import json
import os
import re
import time
import argparse
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── パス定義 ─────────────────────────────────────────────────────────────────

WIKI_ROOT        = Path(__file__).parent.parent
DOTENV_FILE      = WIKI_ROOT / ".env"
SECRETS_FILE     = Path.home() / ".secrets"
CACHE_DIR        = WIKI_ROOT / "cache"
QUEUE_FILE       = CACHE_DIR / "fetch_queue.json"
RATE_STATE_FILE  = CACHE_DIR / "rate_limit_state.json"
REPORTS_DIR      = WIKI_ROOT / "reports"

# ── ローカル HTML からタイトルを取得するヘルパー ──────────────────────────────

def get_title_from_html(wiki_root: Path, slug: str, lang: str) -> str:
    """
    ローカル HTML ファイルからページタイトルを取得する。
    wiki_pages テーブルには title カラムがないため、HTML ファイルを参照。
    """
    html_path = wiki_root / lang / f"{slug}.html"
    if not html_path.exists():
        return slug.replace("-", " ").title()
    try:
        with open(html_path, encoding="utf-8") as f:
            content = f.read(4096)  # 先頭4KB で充分
        # <h1>タグ（最も正確なタイトル）
        m = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.IGNORECASE | re.DOTALL)
        if m:
            return re.sub(r"<[^>]+>", "", m.group(1)).strip()
        # <title>タグ（フォールバック）
        m = re.search(r"<title[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
        if m:
            title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            return title.split("|")[0].strip()
    except Exception:
        pass
    return slug.replace("-", " ").title()


# ── 定数 ──────────────────────────────────────────────────────────────────────

MAX_DAILY_CALLS  = 80           # YouTube への検索リクエスト上限（安全マージン込み）
REQUEST_INTERVAL = 1.5          # リクエスト間隔（秒）

# 優先チャンネル: スコア加点対象
PRIORITY_CHANNELS = {
    "bjj fanatics", "bernardo faria bjj fanatics",
    "gordon ryan", "danaher", "flo grappling",
    "chewjitsu", "stephan kesting", "john danaher",
    "the grappling academy", "bjj mental models",
}

# 必須キーワード: タイトルに含まれるか確認
BJJ_KEYWORDS = [
    "bjj", "jiu-jitsu", "jiu jitsu", "grappling", "submission",
    "guard", "armbar", "triangle", "choke", "sweep", "takedown",
    "kimura", "omoplata", "guillotine", "half guard",
]

TUTORIAL_KEYWORDS = [
    "how to", "tutorial", "technique", "drill", "breakdown",
    "instructional", "step by step", "learn", "teaching",
    "fundamentals", "basics",
]

ANTI_KEYWORDS = [
    "highlight", "compilation", "best of", "match", "tournament",
    "adcc", "worlds", " vs ", "subscribe", "promo", "free class",
]

# アスリートページでは「highlight」「compilation」「best of」は適切なコンテンツ
# 試合・トーナメント系のみペナルティ適用
ATHLETE_ANTI_KEYWORDS = [
    "match", "tournament", "adcc", "worlds", " vs ",
    "subscribe", "promo", "free class",
]


# ── クエリ生成ヘルパー ────────────────────────────────────────────────────────

def _slug_to_search_term(slug: str) -> str:
    """
    スラグを YouTube 検索キーワードに変換。
    例:
      "armbar"              → "armbar"
      "50-50-guard"         → "50/50 guard"
      "athlete-ffion-davies"→ "Ffion Davies"
      "arm-triangle-choke"  → "arm triangle choke"
    """
    term = slug.replace("athlete-", "")        # アスリートプレフィックス除去
    term = term.replace("-", " ")              # ハイフン→スペース
    term = re.sub(r"\b50 50\b", "50/50", term) # 50/50 ガード特殊処理
    return term.strip()


def _build_search_query(slug: str, search_term: str, *, use_quotes: bool = True) -> str:
    """
    スラグの種別に応じたクエリを構築。
    - アスリートページ: アスリート名 + "BJJ"（tutorial不要・名前でヒット優先）
    - 通常ページ: キーワード + "BJJ tutorial"
    - use_quotes=False: 短い一般語の引用符なしフォールバック用
    """
    if slug.startswith("athlete-"):
        return f'"{search_term}" BJJ'
    if use_quotes:
        return f'"{search_term}" BJJ tutorial'
    # フォールバック: 引用符なし（短い一般語でヒット率向上）
    return f'{search_term} BJJ tutorial technique'


# ── 環境変数 ──────────────────────────────────────────────────────────────────

def load_env() -> dict:
    env: dict = {}
    for path in [DOTENV_FILE, SECRETS_FILE]:
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    for key in ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "YOUTUBE_API_KEY"]:
        if key in os.environ:
            env[key] = os.environ[key]
    return env


# ── Supabase クライアント ─────────────────────────────────────────────────────

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


# ── VideoResult データクラス ──────────────────────────────────────────────────

class VideoResult:
    """検索バックエンドが返す動画情報の統一フォーマット"""
    def __init__(
        self,
        video_id: str,
        title: str,
        channel: str,
        duration: str = "",
        view_count: int = 0,
        score: int = 0,
    ):
        self.video_id   = video_id
        self.title      = title
        self.channel    = channel
        self.duration   = duration
        self.view_count = view_count
        self.score      = score

    @property
    def embed_url(self) -> str:
        return f"https://www.youtube.com/embed/{self.video_id}"

    def __repr__(self) -> str:
        return (
            f"VideoResult(id={self.video_id!r}, "
            f"title={self.title[:40]!r}, "
            f"channel={self.channel!r}, score={self.score})"
        )


# ── Adapter Pattern: VideoSearcher ABC ───────────────────────────────────────

class VideoSearcher(abc.ABC):
    """
    検索バックエンドの抽象基底クラス。
    サブクラスは search() を実装するだけでよい。
    スコアリング・フィルタリングは共通ロジックに委譲。
    """

    @abc.abstractmethod
    def search(self, query: str, max_results: int = 10) -> list[VideoResult]:
        """
        クエリを検索して VideoResult のリストを返す。
        結果は未ランク付け（スコアは 0 のまま）でよい。
        """
        ...

    def find_best_video(self, title: str, slug: str) -> tuple[Optional[VideoResult], int]:
        """
        スラグ・タイトルから最適な動画を1件選ぶ共通ロジック。
        バックエンドに依存しない。

        Returns: (best_video_or_None, search_call_count)
          search_call_count はレート制限のカウント用（フォールバックで2回になりうる）

        【クエリ設計】
        ページタイトル全文を引用符で囲むと YouTube でヒット0になりやすい
        （"Mastering the BJJ Armbar: A Comprehensive Guide" など）。
        スラグを短いキーワードに変換して使う。
        - 通常ページ: "armbar" BJJ tutorial
        - アスリート: "Ffion Davies" BJJ（tutorial不要）

        引用符付きで結果なし or スコア不足の場合、引用符なしで再検索（フォールバック）。
        """
        search_term = _slug_to_search_term(slug)
        calls = 0

        # 1回目: 引用符付き検索（精度優先）
        query = _build_search_query(slug, search_term, use_quotes=True)
        best = self._search_and_score(query, title, slug)
        calls += 1
        if best and best.score >= 10:
            return best, calls

        # 2回目: 引用符なしフォールバック（リコール優先）
        if not slug.startswith("athlete-"):
            query_fallback = _build_search_query(slug, search_term, use_quotes=False)
            if query_fallback != query:
                print(f"         🔄 フォールバック検索: {query_fallback}")
                time.sleep(REQUEST_INTERVAL)  # フォールバック前にも間隔を空ける
                best_fb = self._search_and_score(query_fallback, title, slug)
                calls += 1
                if best_fb and best_fb.score >= 10:
                    return best_fb, calls

        return None, calls

    def _search_and_score(self, query: str, title: str, slug: str) -> Optional[VideoResult]:
        """検索→スコアリング→ベスト候補を返す内部ヘルパー"""
        candidates = self.search(query, max_results=10)
        if not candidates:
            return None
        scored = [self._score(v, title, slug) for v in candidates]
        scored.sort(key=lambda v: v.score, reverse=True)
        return scored[0]

    @staticmethod
    def _score(video: VideoResult, page_title: str, slug: str = "") -> VideoResult:
        """タイトル・チャンネル・キーワードからスコアを計算して付与"""
        title_lower   = video.title.lower()
        channel_lower = video.channel.lower()
        page_lower    = page_title.lower()
        score = 0

        # ページタイトルのキーワードが動画タイトルに含まれるか
        page_words = re.findall(r"\b\w+\b", page_lower)
        matched_words = sum(1 for w in page_words if w in title_lower and len(w) > 3)
        score += matched_words * 10

        # BJJ キーワード
        if any(kw in title_lower or kw in channel_lower for kw in BJJ_KEYWORDS):
            score += 20

        # Tutorial キーワード
        if any(kw in title_lower for kw in TUTORIAL_KEYWORDS):
            score += 20

        # 優先チャンネル
        if any(ch in channel_lower for ch in PRIORITY_CHANNELS):
            score += 15

        # アンチキーワード（試合・ハイライト等）
        # アスリートページでは highlight/compilation/best of を許可
        anti_list = ATHLETE_ANTI_KEYWORDS if slug.startswith("athlete-") else ANTI_KEYWORDS
        if any(kw in title_lower for kw in anti_list):
            score -= 30

        # アスリートページ: 選手名が動画タイトル・チャンネルに含まれなければ大幅減点
        # （関係ない一般チュートリアルを弾く）
        if slug.startswith("athlete-"):
            athlete_parts = [
                w for w in slug.replace("athlete-", "").split("-") if len(w) > 2
            ]
            name_matched = any(p in title_lower or p in channel_lower for p in athlete_parts)
            if not name_matched:
                score -= 40

        # 極端に短い動画（shorts 等）は減点
        if video.duration:
            parts = video.duration.split(":")
            try:
                if len(parts) == 2:
                    minutes = int(parts[0])
                    if minutes < 3:
                        score -= 15
            except ValueError:
                pass

        video.score = score
        return video


# ── Adapter 実装 1: LocalYouTubeSearcher ─────────────────────────────────────

class LocalYouTubeSearcher(VideoSearcher):
    """
    requests + YouTube 検索ページの ytInitialData を解析する。
    API キー不要。Mac のターミナルから直接実行できる。

    YouTube が返す HTML の中に埋め込まれた JSON（window.ytInitialData）を
    正規表現で抽出してパースする手法。
    ブラウザと同じ User-Agent を使うことで通常の検索と同等の結果を取得。

    注意: YouTube の HTML 構造変更に影響を受ける可能性あり。
    取得失敗時は空リストを返す（エラー終了しない）。
    """

    _YT_INITIAL_DATA_RE = re.compile(
        r"var ytInitialData\s*=\s*(\{.+?\});\s*(?:var|</script>)",
        re.DOTALL,
    )
    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self):
        try:
            import requests as _requests
            self._requests = _requests
        except ImportError:
            raise RuntimeError(
                "LocalYouTubeSearcher には requests が必要です。\n"
                "  pip install requests"
            )

    def search(self, query: str, max_results: int = 10) -> list[VideoResult]:
        search_url = (
            "https://www.youtube.com/results?"
            + urllib.parse.urlencode({"search_query": query, "sp": "EgIQAQ%3D%3D"})
            # sp=EgIQAQ== は「動画のみ」フィルター
        )
        try:
            resp = self._requests.get(
                search_url, headers=self._HEADERS, timeout=12
            )
            resp.raise_for_status()
        except Exception as e:
            print(f"    ⚠️  YouTube 取得エラー: {e}")
            return []

        return self._parse_yt_initial_data(resp.text, max_results)

    def _parse_yt_initial_data(self, html: str, max_results: int) -> list[VideoResult]:
        """ytInitialData JSON から動画リストを抽出"""
        # JSON 末尾が不完全な場合に備えて複数の区切りを試す
        match = None
        for pattern in [
            r"var ytInitialData\s*=\s*(\{.+?\});\s*</script>",
            r"var ytInitialData\s*=\s*(\{.+?\});\s*var ",
            r"var ytInitialData\s*=\s*(\{.+?\});",
        ]:
            m = re.search(pattern, html, re.DOTALL)
            if m:
                match = m
                break

        if not match:
            print("    ⚠️  ytInitialData が見つかりません（YouTube HTML 構造変更の可能性）")
            return []

        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            # JSON が不完全な場合は末尾を削って再試行
            raw = match.group(1)
            for trim in range(1, 5):
                try:
                    data = json.loads(raw[: raw.rfind("}") - trim + 1] + "}")
                    break
                except json.JSONDecodeError:
                    continue
            else:
                print("    ⚠️  ytInitialData の JSON パース失敗")
                return []

        # contents を掘り下げる
        try:
            contents = (
                data["contents"]["twoColumnSearchResultsRenderer"]
                    ["primaryContents"]["sectionListRenderer"]
                    ["contents"][0]["itemSectionRenderer"]["contents"]
            )
        except (KeyError, IndexError, TypeError):
            print("    ⚠️  ytInitialData の構造が予期しない形式です")
            return []

        results: list[VideoResult] = []
        for item in contents:
            vr = item.get("videoRenderer")
            if not vr:
                continue

            video_id = vr.get("videoId", "")
            if not video_id or len(video_id) != 11:
                continue

            title = ""
            title_obj = vr.get("title", {})
            if "runs" in title_obj:
                title = "".join(run.get("text", "") for run in title_obj["runs"])
            elif "simpleText" in title_obj:
                title = title_obj["simpleText"]

            channel = ""
            owner = vr.get("ownerText", {})
            if "runs" in owner:
                channel = owner["runs"][0].get("text", "")

            duration = ""
            length_obj = vr.get("lengthText", {})
            if "simpleText" in length_obj:
                duration = length_obj["simpleText"]

            # 再生数（可能な場合のみ）
            view_count = 0
            view_obj = vr.get("viewCountText", {})
            view_str = view_obj.get("simpleText", "") or "".join(
                r.get("text", "") for r in view_obj.get("runs", [])
            )
            view_match = re.search(r"([\d,]+)", view_str.replace(",", ""))
            if view_match:
                try:
                    view_count = int(view_match.group(1).replace(",", ""))
                except ValueError:
                    pass

            results.append(VideoResult(
                video_id=video_id,
                title=title,
                channel=channel,
                duration=duration,
                view_count=view_count,
            ))

            if len(results) >= max_results:
                break

        return results


# ── Adapter 実装 2: OfficialAPISearcher ──────────────────────────────────────

class OfficialAPISearcher(VideoSearcher):
    """
    YouTube Data API v3 を使った検索。
    無料枠: 100 units/day（search.list = 100 units/クエリ → 実質 100 クエリ/day）
    API キー必要: ~/.secrets の YOUTUBE_API_KEY

    LocalYouTubeSearcher が壊れたとき or より安定した実行が必要なときの代替。
    使い方: python3 local_video_fetcher.py --backend api --limit 50
    """

    API_BASE = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OfficialAPISearcher には YOUTUBE_API_KEY が必要です")
        self.api_key = api_key

    def search(self, query: str, max_results: int = 10) -> list[VideoResult]:
        params = urllib.parse.urlencode({
            "key":         self.api_key,
            "q":           query,
            "part":        "snippet",
            "type":        "video",
            "maxResults":  min(max_results, 50),
            "videoDuration": "medium",  # 4〜20分（shorts 除外）
            "relevanceLanguage": "en",
        })
        url = f"{self.API_BASE}/search?{params}"
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "BJJWikiBot/2.0"}
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"    ⚠️  YouTube Data API エラー: {e}")
            return []

        results: list[VideoResult] = []
        for item in data.get("items", []):
            snippet  = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId", "")
            if not video_id:
                continue
            results.append(VideoResult(
                video_id=video_id,
                title=snippet.get("title", ""),
                channel=snippet.get("channelTitle", ""),
            ))
        return results


# ── 日次レート制限 ─────────────────────────────────────────────────────────────

class RateLimitState:
    """
    fetch_date（UTC 日付）と呼び出し回数を rate_limit_state.json で管理。
    日付が変わると自動リセット。
    """

    def __init__(self, path: Path = RATE_STATE_FILE):
        self.path = path
        self._state = self._load()

    def _load(self) -> dict:
        today = self._today()
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if data.get("fetch_date") == today:
                    return data
            except Exception:
                pass
        return {"fetch_date": today, "calls": 0}

    @staticmethod
    def _today() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def remaining(self) -> int:
        return max(0, MAX_DAILY_CALLS - self._state["calls"])

    def increment(self, n: int = 1):
        self._state["calls"] += n
        self._save()

    def _save(self):
        self.path.write_text(
            json.dumps(self._state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def __repr__(self) -> str:
        return (
            f"RateLimitState(date={self._state['fetch_date']}, "
            f"calls={self._state['calls']}/{MAX_DAILY_CALLS})"
        )


# ── キュー管理 ────────────────────────────────────────────────────────────────

class FetchQueue:
    """
    日次上限を超えた slug を fetch_queue.json に積む FIFO キュー。
    --from-queue で翌日処理。
    """

    def __init__(self, path: Path = QUEUE_FILE):
        self.path = path
        self._items: list[dict] = self._load()

    def _load(self) -> list[dict]:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return []

    def push(self, slug: str, lang: str, title: str):
        # 重複防止
        if not any(i["slug"] == slug and i["lang"] == lang for i in self._items):
            self._items.append({
                "slug":       slug,
                "lang":       lang,
                "title":      title,
                "queued_at":  datetime.now(timezone.utc).isoformat(),
            })
            self._save()

    def pop_all(self) -> list[dict]:
        items = list(self._items)
        self._items.clear()
        self._save()
        return items

    def __len__(self) -> int:
        return len(self._items)

    def _save(self):
        self.path.write_text(
            json.dumps(self._items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


# ── VideoFetcherEngine（処理ロジック共通層）──────────────────────────────────

class VideoFetcherEngine:
    """
    バックエンド（VideoSearcher）に依存しない処理コア。
    - 冪等性チェック（video_url 設定済みスキップ）
    - 日次レート制限 + キューイング
    - DB 更新・エラーハンドリング・ドライラン対応
    """

    def __init__(
        self,
        searcher: VideoSearcher,
        db: SupabaseClient,
        dry_run: bool = False,
        force: bool = False,
    ):
        self.searcher  = searcher
        self.db        = db
        self.dry_run   = dry_run
        self.force     = force
        self.rate      = RateLimitState()
        self.queue     = FetchQueue()

    def run(self, slugs: list[dict]):
        """
        slugs: [{"slug": str, "lang": str, "title": str}, ...]
        """
        print(f"\n🔍 処理対象: {len(slugs)} 件")
        print(f"📊 {self.rate}  残り: {self.rate.remaining()} calls\n")

        stats = {"processed": 0, "updated": 0, "skipped": 0, "queued": 0, "no_match": 0, "failed": 0}

        for i, item in enumerate(slugs, 1):
            slug  = item["slug"]
            lang  = item["lang"]
            title = item["title"]

            print(f"[{i:4d}/{len(slugs)}] {slug} ({lang}) — {title[:40]}")

            # ── 冪等性チェック ──────────────────────────────────────────────
            if not self.force:
                pages = self.db.select(
                    "wiki_pages",
                    f"slug=eq.{slug}&select=video_url",
                )
                if pages is None:
                    # DB接続エラー時: スキップせず続行（video_url未設定と仮定）
                    print("         ⚠️  DB 冪等性チェック失敗 → 続行（仮定: 未設定）")
                elif pages and pages[0].get("video_url"):
                    print("         ✅ 既に video_url 設定済み → スキップ（冪等）")
                    stats["skipped"] += 1
                    continue

            # ── 日次レート制限チェック ──────────────────────────────────────
            if self.rate.remaining() <= 0:
                self.queue.push(slug, lang, title)
                print(f"         ⏳ 日次上限到達 → キューに追加（残: {len(self.queue)} 件）")
                stats["queued"] += 1
                continue

            # ── 検索実行 ────────────────────────────────────────────────────
            time.sleep(REQUEST_INTERVAL)
            try:
                best, search_calls = self.searcher.find_best_video(title, slug)
            except Exception as e:
                print(f"         ❌ 検索エラー: {e}")
                stats["failed"] += 1
                self.rate.increment()
                continue

            self.rate.increment(search_calls)
            stats["processed"] += 1

            if best is None:
                print("         ⚠️  適切な動画が見つかりませんでした")
                stats["no_match"] += 1
                continue

            print(f"         🎯 [{best.score:+3d}pt] {best.title[:55]}")
            print(f"              ch: {best.channel}  dur: {best.duration}")
            print(f"              id: {best.video_id}  → {best.embed_url}")

            # ── DB 更新 ─────────────────────────────────────────────────────
            if self.dry_run:
                print("         [DRY-RUN] DB 書き込みをスキップ")
                stats["updated"] += 1
            else:
                ok = self.db.update(
                    "wiki_pages",
                    f"slug=eq.{slug}",
                    {"video_url": best.embed_url},
                )
                if ok:
                    print("         ✅ wiki_pages.video_url 更新完了")
                    stats["updated"] += 1
                else:
                    print("         ❌ DB 更新失敗")
                    stats["failed"] += 1

        # ── サマリー ─────────────────────────────────────────────────────────
        print(f"\n{'─' * 60}")
        print(f"完了: {stats['processed']} 件処理")
        print(f"  ✅ 更新: {stats['updated']}")
        print(f"  ⏭️  スキップ（設定済み）: {stats['skipped']}")
        print(f"  ⏳ キュー追加（明日処理）: {stats['queued']}")
        print(f"  ⚠️  動画なし（マッチなし）: {stats['no_match']}")
        print(f"  ❌ DB更新失敗 / 検索エラー: {stats['failed']}")
        print(f"  📊 本日の API 呼び出し数: {MAX_DAILY_CALLS - self.rate.remaining()}/{MAX_DAILY_CALLS}")

        if self.queue:
            print(f"\n⏳ キュー残件数: {len(self.queue)} 件")
            print("   翌日 --from-queue で処理します")

        if self.dry_run:
            print("\n⚠️  DRY-RUN モード: DB への書き込みは行っていません")


# ── メイン ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Local YouTube Video Fetcher for BJJ Wiki (API-keyless)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run",    action="store_true",
                        help="DB 書き込みなし（確認用）")
    parser.add_argument("--limit",      type=int, default=50,
                        help="処理件数上限 (default: 50)")
    parser.add_argument("--lang",       type=str, default="en",
                        choices=["en", "ja", "pt"],
                        help="対象言語 (default: en)")
    parser.add_argument("--slug",       type=str,
                        help="特定スラグのみ処理")
    parser.add_argument("--force",      action="store_true",
                        help="video_url が設定済みでも強制上書き（--slug と組み合わせて使用）")
    parser.add_argument("--from-queue", action="store_true",
                        help="キューに積まれた翌日分を処理")
    parser.add_argument("--backend",    type=str, default="local",
                        choices=["local", "api"],
                        help="検索バックエンド (default: local = requests+ytInitialData)")
    parser.add_argument("--show-queue", action="store_true",
                        help="キューの内容を表示して終了")
    args = parser.parse_args()

    # ── キュー確認モード ──────────────────────────────────────────────────────
    if args.show_queue:
        q = FetchQueue()
        if not q:
            print("📭 キューは空です")
        else:
            print(f"📬 キュー: {len(q)} 件")
            for item in q._items:
                print(f"  - {item['slug']} ({item['lang']}) queued: {item['queued_at'][:10]}")
        return

    # ── 環境変数 ─────────────────────────────────────────────────────────────
    env = load_env()
    supabase_url = env.get("SUPABASE_URL")
    supabase_key = env.get("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL と SUPABASE_SERVICE_ROLE_KEY を設定してください")
        return

    db = SupabaseClient(supabase_url, supabase_key)

    # ── バックエンド選択 ──────────────────────────────────────────────────────
    if args.backend == "api":
        api_key = env.get("YOUTUBE_API_KEY")
        if not api_key:
            print("❌ --backend api には YOUTUBE_API_KEY が必要です")
            return
        searcher: VideoSearcher = OfficialAPISearcher(api_key)
        print("🔌 バックエンド: YouTube Data API v3")
    else:
        try:
            searcher = LocalYouTubeSearcher()
            print("🔌 バックエンド: LocalYouTubeSearcher (requests + ytInitialData)")
        except RuntimeError as e:
            print(f"❌ {e}")
            return

    engine = VideoFetcherEngine(searcher, db, dry_run=args.dry_run, force=args.force)

    # ── キューモード ──────────────────────────────────────────────────────────
    if args.from_queue:
        queue = FetchQueue()
        items = queue.pop_all()
        if not items:
            print("📭 キューは空です")
            return
        print(f"📬 キューから {len(items)} 件を処理します")
        slugs = [
            {"slug": i["slug"], "lang": i["lang"], "title": i["title"]}
            for i in items
        ]
        engine.run(slugs)
        return

    # ── 通常モード: DB から未設定 slug を取得 ─────────────────────────────────
    # ※ wiki_pages には slug と video_url のみ（lang/title カラムなし）
    # タイトルはローカル HTML ファイルから取得する
    if args.slug:
        # 単体スラグ
        pages = db.select(
            "wiki_pages",
            f"slug=eq.{args.slug}&select=slug",
        )
        if not pages:
            # DBにない場合でもローカルHTMLが存在すれば処理する
            html_path = WIKI_ROOT / args.lang / f"{args.slug}.html"
            if not html_path.exists():
                print(f"❌ slug={args.slug} が見つかりません（DB + ローカルHTML両方）")
                return
            pages = [{"slug": args.slug}]
        slugs = [{"slug": p["slug"], "lang": args.lang,
                  "title": get_title_from_html(WIKI_ROOT, p["slug"], args.lang)}
                 for p in pages]
    else:
        # video_url が NULL の全スラグを取得（冪等性のセカンドライン）
        # wiki_pages テーブルに slug が登録されていない場合は HTML ファイルでフォールバック
        query_parts = [
            "video_url=is.null",
            "select=slug",
            "order=slug.asc",
        ]
        if args.limit > 0:
            query_parts.append(f"limit={args.limit}")

        pages = db.select("wiki_pages", "&".join(query_parts))
        if pages is None:
            # DB 接続失敗時: ローカル HTML ファイルから直接スキャン
            print("⚠️  DB 接続失敗 → ローカル HTML ファイルからフォールバック")
            lang_dir = WIKI_ROOT / args.lang
            html_files = sorted(lang_dir.glob("*.html")) if lang_dir.exists() else []
            limit = args.limit if args.limit > 0 else len(html_files)
            pages = [{"slug": f.stem} for f in html_files[:limit]]
        if not pages:
            print(f"✅ video_url が未設定のページはありません")
            return
        slugs = [{"slug": p["slug"], "lang": args.lang,
                  "title": get_title_from_html(WIKI_ROOT, p["slug"], args.lang)}
                 for p in pages
                 # ローカルHTMLが存在する lang のみ対象
                 if (WIKI_ROOT / args.lang / f"{p['slug']}.html").exists()]

    engine.run(slugs)


if __name__ == "__main__":
    main()
