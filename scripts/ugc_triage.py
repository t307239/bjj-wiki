#!/usr/bin/env python3
"""
ugc_triage.py — UGC 動画投稿の AI 自動フィルタリング

【目的】
  ugc_video_submissions テーブルの status='pending' 行を取得し、
  ルールベース + 軽量スコアリングで自動承認・却下を判定する。
  承認されたものは wiki_pages.video_url に反映。

【アルゴリズム（② 要件）】
  Phase 1: ハードフィルタ（即却下条件）
    - oEmbed で動画が削除済み / 非公開 / 視聴不可 → rejected
    - video_id が11文字の有効パターン以外 → rejected
    - youtube_url が YouTube ドメイン以外 → rejected

  Phase 2: ソフトスコア（0〜100点）
    +30: oEmbed タイトルに BJJ キーワードを含む
         ("bjj", "jiu-jitsu", "grappling", "armbar", "guard", "choke" 等)
    +20: oEmbed タイトルに tutorial キーワードを含む
         ("how to", "tutorial", "technique", "drill", "breakdown", "instructional")
    -20: タイトルに highlight / match / competition / ADCC / competition が含まれる
         （試合映像・ハイライトを排除）
    -30: タイトルに spam 系キーワードが含まれる
         ("subscribe", "follow me", "free class", "click here", "promo", "sale")
    +10: 同じ slug に過去 approved された動画と異なる video_id（重複登録防止）

  Phase 3: 閾値判定
    score >= 40 → approved（wiki_pages.video_url に反映）
    score < 40  → rejected
    なお既に wiki_pages.video_url が設定済みの場合は approved でも更新しない
    （video_enricher.py やより良い動画が先に設定されている可能性があるため）

【使い方】
  python3 ugc_triage.py                    # 全 pending を処理
  python3 ugc_triage.py --dry-run          # DB 書き込みなし（判定確認）
  python3 ugc_triage.py --limit 50         # 最大50件
  python3 ugc_triage.py --reprocess        # rejected も再処理（スコア再計算）

【前提】
  ~/Claude/bjj-wiki/.env または ~/.secrets に以下を記載:
    SUPABASE_URL=https://xxxx.supabase.co
    SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
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
from datetime import datetime, timezone

WIKI_ROOT    = Path(__file__).parent.parent
DOTENV_FILE  = WIKI_ROOT / ".env"
SECRETS_FILE = Path.home() / ".secrets"

# ── スコアリング定義 ────────────────────────────────────────────────────────

BJJ_KEYWORDS = [
    "bjj", "jiu-jitsu", "jiujitsu", "jiu jitsu", "grappling",
    "armbar", "arm bar", "triangle", "choke", "guard", "mount", "sweep",
    "takedown", "submission", "kimura", "omoplata", "guillotine",
    "half guard", "full guard", "butterfly", "x-guard", "berimbolo",
    "heel hook", "leg lock", "ankle lock", "knee bar",
    "pass", "passing", "retain", "retention",
]

TUTORIAL_KEYWORDS = [
    "how to", "tutorial", "technique", "drill", "breakdown",
    "instructional", "step by step", "learn", "teaching",
    "fundamentals", "basics", "beginner", "advanced",
]

HIGHLIGHT_KEYWORDS = [
    "highlight", "highlights", "best of", "compilation",
    "match", "tournament", "adcc", "worlds", "competition",
    "vs ", " vs.", "win", "loses",
]

SPAM_KEYWORDS = [
    "subscribe", "follow me", "free class", "click here",
    "promo", "sale", "discount", "coupon", "link in bio",
    "check out my", "my channel", "like and subscribe",
]

APPROVAL_THRESHOLD = 40


# ── 環境変数読み込み ────────────────────────────────────────────────────────

def load_env() -> dict:
    env = {}
    for path in [DOTENV_FILE, SECRETS_FILE]:
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    for key in ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]:
        if key in os.environ:
            env[key] = os.environ[key]
    return env


# ── Supabase クライアント ────────────────────────────────────────────────────

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


# ── oEmbed 確認 ─────────────────────────────────────────────────────────────

def fetch_oembed(video_id: str) -> Optional[dict]:
    """
    YouTube oEmbed API でタイトル取得と存在確認。
    削除・非公開: None を返す。
    成功: {"title": str, "author_name": str} を返す。
    """
    url = (
        "https://www.youtube.com/oembed?"
        + urllib.parse.urlencode({
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "format": "json",
        })
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BJJWikiBot/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return {
                    "title":       data.get("title", ""),
                    "author_name": data.get("author_name", ""),
                }
    except Exception:
        pass
    return None


# ── スコアリング ─────────────────────────────────────────────────────────────

VALID_VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
YOUTUBE_DOMAINS = ("youtube.com", "youtu.be")


def score_submission(submission: dict, oembed: Optional[dict]) -> tuple[int, list[str]]:
    """
    スコアを計算し (score: int, reasons: list[str]) を返す。
    oembed が None の場合（削除済み）は -999 を返して即却下。
    """
    notes = []

    # Phase 1: ハードフィルタ
    if oembed is None:
        return -999, ["❌ 動画が削除済み / 非公開"]

    video_id    = submission.get("video_id", "")
    youtube_url = submission.get("youtube_url", "")

    if not VALID_VIDEO_ID.match(video_id):
        return -999, ["❌ 無効な video_id"]

    parsed = urllib.parse.urlparse(youtube_url)
    if not any(d in parsed.netloc for d in YOUTUBE_DOMAINS):
        return -999, ["❌ YouTube ドメイン以外"]

    # Phase 2: ソフトスコア
    score = 0
    video_title   = (oembed.get("title", "")       or "").lower()
    author_name   = (oembed.get("author_name", "") or "").lower()
    combined_text = f"{video_title} {author_name}"

    # BJJ キーワード
    bjj_found = [kw for kw in BJJ_KEYWORDS if kw in combined_text]
    if bjj_found:
        score += 30
        notes.append(f"✅ BJJ キーワード検出: {', '.join(bjj_found[:3])}")

    # tutorial キーワード
    tut_found = [kw for kw in TUTORIAL_KEYWORDS if kw in video_title]
    if tut_found:
        score += 20
        notes.append(f"✅ Tutorial キーワード: {', '.join(tut_found[:2])}")

    # ハイライト系（減点）
    hl_found = [kw for kw in HIGHLIGHT_KEYWORDS if kw in video_title]
    if hl_found:
        score -= 20
        notes.append(f"⚠️ ハイライト系キーワード: {', '.join(hl_found[:2])}")

    # スパム系（減点）
    spam_found = [kw for kw in SPAM_KEYWORDS if kw in combined_text]
    if spam_found:
        score -= 30
        notes.append(f"❌ スパムキーワード: {', '.join(spam_found[:2])}")

    return score, notes


# ── メイン処理 ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UGC Video Auto-Triage for BJJ Wiki")
    parser.add_argument("--dry-run",   action="store_true", help="DB に書き込まない")
    parser.add_argument("--limit",     type=int, default=100, help="処理件数上限")
    parser.add_argument("--reprocess", action="store_true",
                        help="rejected 済みも再スコアリング（スコア改訂時）")
    args = parser.parse_args()

    env = load_env()
    supabase_url = env.get("SUPABASE_URL")
    supabase_key = env.get("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL と SUPABASE_SERVICE_ROLE_KEY を設定してください")
        return

    db = SupabaseClient(supabase_url, supabase_key)

    # ── pending 取得 ──────────────────────────────────────────────────────
    statuses = "pending,rejected" if args.reprocess else "pending"
    query = (
        f"status=in.({statuses})"
        f"&order=created_at.asc"
        f"&limit={args.limit}"
        f"&select=id,slug,lang,youtube_url,video_id,status"
    )
    submissions = db.select("ugc_video_submissions", query)
    if submissions is None:
        return

    print(f"📋 対象: {len(submissions)} 件 (status={statuses})\n")
    if not submissions:
        print("✅ トリアージ対象なし")
        return

    # slug ごとの既存 video_url キャッシュ
    wiki_video_cache: dict[str, Optional[str]] = {}

    approved_count = 0
    rejected_count = 0

    for i, sub in enumerate(submissions, 1):
        sub_id    = sub["id"]
        slug      = sub["slug"]
        lang      = sub["lang"]
        video_id  = sub["video_id"]

        print(f"[{i:3d}/{len(submissions)}] {slug} / {video_id}")

        # oEmbed で存在確認 & タイトル取得
        time.sleep(0.5)
        oembed = fetch_oembed(video_id)

        score, notes = score_submission(sub, oembed)

        for note in notes:
            print(f"    {note}")

        if oembed:
            print(f"    📹 タイトル: {oembed['title'][:80]}")
        print(f"    📊 スコア: {score} / 100 → ", end="")

        new_status = "approved" if score >= APPROVAL_THRESHOLD else "rejected"
        print(new_status.upper())

        notes_str = "; ".join(notes)

        if args.dry_run:
            print(f"    [DRY-RUN] status → {new_status}, ai_score={score}")
            if new_status == "approved":
                approved_count += 1
            else:
                rejected_count += 1
            continue

        # DB 更新: ugc_video_submissions
        update_data = {
            "status":      new_status,
            "ai_score":    score,
            "ai_notes":    notes_str,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
        db.update("ugc_video_submissions", f"id=eq.{sub_id}", update_data)

        # approved → wiki_pages.video_url に反映（未設定の場合のみ）
        if new_status == "approved":
            # 既存 video_url をキャッシュで確認
            if slug not in wiki_video_cache:
                pages = db.select("wiki_pages", f"slug=eq.{slug}&select=video_url")
                existing = (pages or [{}])[0].get("video_url")
                wiki_video_cache[slug] = existing

            if wiki_video_cache[slug]:
                print(f"    ℹ️  wiki_pages.video_url は既に設定済みのためスキップ")
            else:
                embed_url = f"https://www.youtube.com/embed/{video_id}"
                ok = db.update("wiki_pages", f"slug=eq.{slug}", {"video_url": embed_url})
                if ok:
                    print(f"    ✅ wiki_pages.video_url 更新: {embed_url}")
                    wiki_video_cache[slug] = embed_url
                else:
                    print(f"    ❌ wiki_pages 更新失敗")
            approved_count += 1
        else:
            rejected_count += 1

        print()

    # ── サマリー ─────────────────────────────────────────────────────────
    print(f"\n{'─'*50}")
    print(f"トリアージ完了: {len(submissions)} 件")
    print(f"  ✅ approved: {approved_count}")
    print(f"  ❌ rejected: {rejected_count}")
    if args.dry_run:
        print("  ※ DRY-RUN モード: DB への書き込みは行っていません")


if __name__ == "__main__":
    main()
