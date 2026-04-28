"""
_launch_announce.py — z226: shared launch announcement helper

各 auto_post_*.py が main() 冒頭で check_and_consume(platform) を呼ぶ。
sentinel file (launch_announcement_<platform>.txt) が repo root にあれば
その内容を返し、ファイルを削除する。次回 cron からは normal Wiki post 再開。

使い方 (Toshiki が「launch する」と決めた時):
  cd ~/Claude/bjj-wiki
  echo "I built a free BJJ tracker..." > launch_announcement_x.txt
  echo "Different text..." > launch_announcement_threads.txt
  ...
  → 翌日の cron で各 platform に 1 回だけ launch text 投稿、その後通常運転

各 sentinel file は最初に main() が走った platform でのみ消費される。
4 platform 別ファイルにすることで、複数 platform へ並列に launch announcement
を仕込める (各 cron 時刻が異なるため、最初に走った 1 つだけが消費される問題を回避)。

文字数制限 (post 失敗回避):
  - X (Twitter):  280 chars
  - Threads:      500 chars
  - Bluesky:      300 chars (graphemes、URL は短縮されない)
  - Mastodon:     500 chars (instance により設定可、bjj.social が標準 500)
"""
from __future__ import annotations
import os
from pathlib import Path

# repo root = scripts/ の親
REPO_ROOT = Path(__file__).resolve().parent.parent


def check_and_consume(platform: str) -> str | None:
    """
    sentinel file 存在チェック + 内容読込 + 削除 (one-shot 保証)。

    platform: "x" | "threads" | "bluesky" | "mastodon"
    returns: launch text (success) or None (sentinel 不在)
    """
    if platform not in ("x", "threads", "bluesky", "mastodon"):
        return None
    sentinel = REPO_ROOT / f"launch_announcement_{platform}.txt"
    if not sentinel.exists():
        return None
    try:
        text = sentinel.read_text(encoding="utf-8").strip()
    except Exception as e:
        print(f"  [LAUNCH] Failed to read {sentinel.name}: {e}")
        return None
    if not text:
        # 空ファイル → 削除して None
        try:
            sentinel.unlink()
        except Exception:
            pass
        return None
    # 削除を try / Telegram 通知後でも consume 確定させる
    try:
        sentinel.unlink()
        print(f"  [LAUNCH] Consumed {sentinel.name} ({len(text)} chars)")
    except Exception as e:
        print(f"  [LAUNCH] WARN: read OK but unlink failed for {sentinel.name}: {e}")
        # 削除失敗時でも text は返す。再 cron で重複投稿の risk あるため
        # GH Actions 側で workspace の write 権限ある前提
    return text
