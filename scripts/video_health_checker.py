#!/usr/bin/env python3
"""
video_health_checker.py — 月次デッドリンク検出 & 自己修復バッチ

【目的】
  wiki_pages.video_url に設定済みの YouTube embed URL を全件チェックし、
  削除・非公開・404 になった動画を検出して video_url を NULL に戻す。
  → UGC フォールバック CTA が自動的に表示される（自己修復）。

【動作フロー（② 要件 - self-healing）】
  1. wiki_pages テーブルから video_url IS NOT NULL の全行を取得
  2. 各 video_url から video_id を抽出
  3. YouTube oEmbed API で存在確認（API キー不要）
     - HTTP 200 → 存在する（ヘルシー）
     - HTTP 404 / 4xx / タイムアウト → 削除・非公開（デッドリンク）
  4. デッドリンクを検出 → wiki_pages.video_url = NULL に更新
  5. 変更レポートを dead_links_YYYYMMDD.json に保存

【実行方針】
  月1回 cron で実行。
  python3 video_health_checker.py --dry-run  # 変更なし・問題リストのみ出力
  python3 video_health_checker.py            # 実際に NULL 化
  python3 video_health_checker.py --slug armbar  # 特定スラグのみ確認

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
REPORTS_DIR  = WIKI_ROOT / "reports"
DOTENV_FILE  = WIKI_ROOT / ".env"
SECRETS_FILE = Path.home() / ".secrets"

# チェック間隔（oEmbed への負荷を抑える）
REQUEST_INTERVAL = 0.5  # 秒

# タイムアウト（秒）
OEMBED_TIMEOUT = 8

# リトライ回数（一時的なネットワーク障害を除外）
MAX_RETRIES = 2


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


# ── video_id 抽出 ─────────────────────────────────────────────────────────────

def extract_video_id(url: str) -> Optional[str]:
    """youtube.com/embed/VIDEO_ID から video_id を抽出"""
    patterns = [
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
        r"youtube\.com/watch\?(?:.*&)?v=([A-Za-z0-9_-]{11})",
        r"youtu\.be/([A-Za-z0-9_-]{11})",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


# ── oEmbed ヘルスチェック ─────────────────────────────────────────────────────

def check_video_health(video_id: str) -> tuple[bool, str]:
    """
    oEmbed API で動画の存在を確認。
    Returns: (is_alive: bool, reason: str)
    """
    oembed_url = (
        "https://www.youtube.com/oembed?"
        + urllib.parse.urlencode({
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "format": "json",
        })
    )

    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(
                oembed_url,
                headers={"User-Agent": "BJJWikiBot/1.0 (health-check)"}
            )
            with urllib.request.urlopen(req, timeout=OEMBED_TIMEOUT) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    title = data.get("title", "")
                    return True, f"OK: {title[:50]}"
                else:
                    return False, f"HTTP {resp.status}"
        except urllib.error.HTTPError as e:
            if e.code in (404, 401, 403):
                # 明確なエラーはリトライ不要
                reason_map = {
                    404: "削除済み / 動画ID無効",
                    401: "非公開 / 視聴制限",
                    403: "地域制限 / 著作権ブロック",
                }
                return False, f"HTTP {e.code}: {reason_map.get(e.code, '不明')}"
            if attempt < MAX_RETRIES - 1:
                time.sleep(1.0)
                continue
            return False, f"HTTP {e.code} (after {MAX_RETRIES} retries)"
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(1.0)
                continue
            return False, f"エラー: {str(e)[:60]}"

    return False, "タイムアウト / 接続失敗"


# ── レポート保存 ──────────────────────────────────────────────────────────────

def save_report(dead_links: list, healthy: int, skipped: int):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    report_path = REPORTS_DIR / f"dead_links_{date_str}.json"

    report = {
        "generated_at":    datetime.now(timezone.utc).isoformat(),
        "summary": {
            "healthy": healthy,
            "dead":    len(dead_links),
            "skipped": skipped,
        },
        "dead_links": dead_links,
    }
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n📄 レポート保存: {report_path}")
    return report_path


# ── メイン処理 ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Video Dead Link Detector & Self-Healer for BJJ Wiki"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="DB 書き込みなし（問題リストのみ出力）")
    parser.add_argument("--slug",    type=str, help="特定スラグのみチェック")
    parser.add_argument("--limit",   type=int, default=0,
                        help="チェック件数上限（0=全件）")
    args = parser.parse_args()

    env = load_env()
    supabase_url = env.get("SUPABASE_URL")
    supabase_key = env.get("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL と SUPABASE_SERVICE_ROLE_KEY を設定してください")
        return

    db = SupabaseClient(supabase_url, supabase_key)

    # ── video_url 設定済みの全ページを取得 ────────────────────────────────
    query_parts = ["video_url=not.is.null", "select=id,slug,video_url"]
    if args.slug:
        query_parts.append(f"slug=eq.{args.slug}")
    if args.limit > 0:
        query_parts.append(f"limit={args.limit}")

    pages = db.select("wiki_pages", "&".join(query_parts))
    if pages is None:
        return

    print(f"🔍 チェック対象: {len(pages)} 件\n")
    if not pages:
        print("✅ video_url 設定済みのページがありません")
        return

    healthy_count = 0
    skipped_count = 0
    dead_links    = []

    for i, page in enumerate(pages, 1):
        slug      = page["slug"]
        video_url = page.get("video_url", "")

        video_id = extract_video_id(video_url or "")
        if not video_id:
            print(f"[{i:3d}] {slug} — ⚠️  video_id 抽出失敗: {video_url[:60]}")
            skipped_count += 1
            continue

        time.sleep(REQUEST_INTERVAL)
        is_alive, reason = check_video_health(video_id)

        status_icon = "✅" if is_alive else "💀"
        print(f"[{i:3d}] {slug} ({video_id}) — {status_icon} {reason}")

        if is_alive:
            healthy_count += 1
        else:
            dead_links.append({
                "slug":      slug,
                "video_id":  video_id,
                "video_url": video_url,
                "reason":    reason,
            })

            if not args.dry_run:
                # wiki_pages.video_url を NULL に戻す（UGC CTA が自動表示される）
                ok = db.update("wiki_pages", f"slug=eq.{slug}", {"video_url": None})
                if ok:
                    print(f"       🔄 video_url を NULL にリセット → UGC CTA が表示されます")
                else:
                    print(f"       ❌ DB 更新失敗")

    # ── サマリー ─────────────────────────────────────────────────────────
    print(f"\n{'─'*55}")
    print(f"ヘルスチェック完了: {len(pages)} 件")
    print(f"  ✅ 正常: {healthy_count}")
    print(f"  💀 デッドリンク: {len(dead_links)}")
    print(f"  ⚠️  スキップ（video_id 不明）: {skipped_count}")

    if dead_links:
        print(f"\n💀 デッドリンク一覧:")
        for dl in dead_links:
            print(f"   - {dl['slug']}: {dl['reason']}")

    # レポート保存
    save_report(dead_links, healthy_count, skipped_count)

    if args.dry_run:
        print("\n⚠️  DRY-RUN モード: DB への書き込みは行っていません")
        print("   実際にリセットするには --dry-run を外して再実行してください")

    if len(dead_links) > 0 and not args.dry_run:
        print(f"\n✅ {len(dead_links)} 件の video_url を NULL にリセットしました")
        print("   UGC フォールバック CTA が自動的に表示されます")
        print("   新しい動画が必要な場合は video_fetcher.py を実行してください")


if __name__ == "__main__":
    main()
