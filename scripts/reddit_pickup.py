#!/usr/bin/env python3
"""
reddit_pickup.py — z239: r/bjj community 質問 daily pickup

毎朝 cron で r/bjj の新規 thread から「Toshiki が答えやすそう & 反応得やすそう」
な技術質問を pickup → Telegram に suggested wiki page + Gemini 答え下書き付きで送る。

目的:
  Reddit r/bjj に「ただの promo 屋じゃない」と認識されるための community 貢献
  自動化。Toshiki は Telegram で 5 分/日 select + 手 reply するだけ。
  1-2 週間 karma 蓄積 → 後の launch (mod DM / cold post) の地ならし。

必要な環境変数 (GitHub Secrets):
  REDDIT_CLIENT_ID       : reddit.com/prefs/apps で「script」 type 作成して取得
  REDDIT_CLIENT_SECRET   : 同上
  REDDIT_USER_AGENT      : 例: "bjj-wiki-pickup/0.1 by t307239"
  GEMINI_API_KEY         : 既存 (FAQ 生成で使用中)
  TELEGRAM_BOT_TOKEN     : 既存
  TELEGRAM_CHAT_ID       : 既存

setup (初回のみ、Toshiki):
  1. https://www.reddit.com/prefs/apps/ → are you a developer? create an app
  2. type: 「script」、name: 「bjj-wiki-pickup」、redirect uri: http://localhost
  3. client ID (16 字) と secret (27 字) を取得
  4. GitHub repo Settings → Secrets and variables → Actions に追加
  5. python3 -m pip install --upgrade praw google-generativeai requests

Usage:
  python3 scripts/reddit_pickup.py [--dry-run] [--limit N]
"""
from __future__ import annotations
import os
import sys
import re
import glob
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SUBREDDIT = "bjj"
LOOKBACK_HOURS = 24

# pickup フィルタ閾値
MIN_COMMENTS = 0           # 0 でも pickup (最初に reply で目立てる)
MAX_COMMENTS = 15          # 多すぎると埋もれる
MIN_SCORE = 1              # negative skip
MAX_SCORE = 100            # 人気すぎは competitive
MIN_AGE_MIN = 30           # 投稿直後は待つ (mod による削除可能性)
MAX_AGE_HOURS = LOOKBACK_HOURS

DEFAULT_LIMIT = 10         # daily pickup 件数上限

# 質問判定 keyword
QUESTION_KEYWORDS_EN = [
    "how to", "how do", "how can", "how should",
    "what is", "what are", "what's", "what do",
    "why does", "why is", "why do",
    "when should", "should i", "can i", "is it",
    "advice", "help", "tips", "recommend",
    "anyone else", "does anyone", "have you",
]


def import_libs():
    try:
        import praw
        import google.generativeai as genai
        import requests
        return praw, genai, requests
    except ImportError as e:
        print(f"❌ library 不足: {e}")
        print()
        print("install:")
        print("  python3 -m pip install --upgrade praw google-generativeai requests")
        sys.exit(1)


def is_question(title: str, body: str) -> bool:
    """title が ? で終わる、または質問 keyword を含むか判定。"""
    if title.rstrip().endswith("?"):
        return True
    text = (title + " " + body).lower()
    return any(kw in text for kw in QUESTION_KEYWORDS_EN)


def load_wiki_slugs() -> list[tuple[str, set[str]]]:
    """
    bjj-wiki/en/*.html の slug 一覧 + 各 slug の keyword set を作る。
    return: [(slug, {keyword, ...}), ...]
    """
    slugs = []
    for html_path in sorted(glob.glob(str(REPO_ROOT / "en" / "*.html"))):
        slug = Path(html_path).stem
        if slug in ("index", "404", "about", "contact"):
            continue
        # slug を keyword 化 (kebab-case → words)
        keywords = set(re.split(r"[-_/]", slug.lower()))
        keywords.discard("")
        slugs.append((slug, keywords))
    return slugs


def match_wiki_pages(post_text: str, wiki_slugs: list[tuple[str, set[str]]], top_n: int = 3) -> list[str]:
    """post text と wiki slug の keyword 重複度で top N suggest。"""
    text_words = set(re.findall(r"[a-z]+", post_text.lower()))
    scored = []
    for slug, kws in wiki_slugs:
        overlap = len(text_words & kws)
        if overlap > 0:
            scored.append((overlap, slug))
    scored.sort(reverse=True)
    return [slug for _, slug in scored[:top_n]]


def gemini_draft_answer(genai, post_title: str, post_body: str, wiki_pages: list[str]) -> str:
    """Gemini Flash で答え下書きを生成。"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "(GEMINI_API_KEY not set, skipping draft)"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        wiki_links = ", ".join(f"https://wiki.bjj-app.net/en/{s}" for s in wiki_pages[:2])
        prompt = (
            "You are a helpful BJJ practitioner answering on Reddit r/bjj.\n"
            "Write a concise, friendly answer to the post below.\n"
            "- 2-4 sentences max\n"
            "- Practical, no fluff\n"
            "- Naturally mention 1 BJJ Wiki link if directly relevant (no hard sell)\n"
            "- Don't use emoji\n"
            "- Avoid Reddit-specific slang you're not sure about\n"
            f"Available wiki pages (use only if directly related):\n{wiki_links}\n"
            f"\n--- POST ---\nTitle: {post_title}\nBody: {post_body[:1500]}\n"
            "\n--- ANSWER ---"
        )
        resp = model.generate_content(prompt)
        return resp.text.strip()[:1000]
    except Exception as e:
        return f"(Gemini error: {e})"


def send_telegram(requests, message: str) -> bool:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("⚠️  Telegram credentials not set, printing only:")
        print(message)
        return False
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        r = requests.post(url, data={
            "chat_id": chat_id, "text": message,
            "parse_mode": "HTML", "disable_web_page_preview": "false",
        }, timeout=15)
        return r.ok
    except Exception as e:
        print(f"❌ Telegram send fail: {e}")
        return False


def format_telegram_message(picks: list[dict]) -> str:
    if not picks:
        return f"📭 r/{SUBREDDIT} pickup ({datetime.now(timezone.utc).date()})\n\n本日 pickup 該当なし"
    lines = [f"🦝 <b>r/{SUBREDDIT} 質問 pickup</b> ({len(picks)} 件)"]
    lines.append(f"<i>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</i>")
    lines.append("")
    for i, p in enumerate(picks, 1):
        lines.append(f"<b>#{i} {p['title'][:80]}</b>")
        lines.append(f"💬 {p['num_comments']}  |  ⬆ {p['score']}  |  🕐 {p['age_min']}分前")
        lines.append(f"🔗 {p['url']}")
        if p["wiki_pages"]:
            lines.append(f"📚 関連: {', '.join(p['wiki_pages'][:2])}")
        if p.get("draft"):
            lines.append(f"✏️ <i>下書き:</i>\n<pre>{p['draft'][:500]}</pre>")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    limit = DEFAULT_LIMIT
    for i, arg in enumerate(sys.argv):
        if arg == "--limit" and i + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 1])
            except ValueError:
                pass
    no_draft = "--no-draft" in sys.argv

    praw, genai, requests = import_libs()

    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "bjj-wiki-pickup/0.1")

    if not client_id or not client_secret:
        print("❌ REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET が未設定")
        print("   https://www.reddit.com/prefs/apps/ で「script」 type の app を作成")
        sys.exit(1)

    print(f"=== r/{SUBREDDIT} 質問 pickup ({datetime.now(timezone.utc)}) ===")
    print(f"フィルタ: comments {MIN_COMMENTS}-{MAX_COMMENTS}, score {MIN_SCORE}-{MAX_SCORE}, "
          f"age {MIN_AGE_MIN}m-{MAX_AGE_HOURS}h")

    reddit = praw.Reddit(
        client_id=client_id, client_secret=client_secret, user_agent=user_agent,
    )
    reddit.read_only = True

    wiki_slugs = load_wiki_slugs()
    print(f"📚 wiki slugs loaded: {len(wiki_slugs)}")

    now = datetime.now(timezone.utc)
    cutoff_old = now - timedelta(hours=MAX_AGE_HOURS)
    cutoff_new = now - timedelta(minutes=MIN_AGE_MIN)

    picks = []
    seen = 0
    for submission in reddit.subreddit(SUBREDDIT).new(limit=200):
        seen += 1
        post_time = datetime.fromtimestamp(submission.created_utc, timezone.utc)
        if post_time < cutoff_old or post_time > cutoff_new:
            continue
        if not is_question(submission.title, submission.selftext or ""):
            continue
        if submission.num_comments < MIN_COMMENTS or submission.num_comments > MAX_COMMENTS:
            continue
        if submission.score < MIN_SCORE or submission.score > MAX_SCORE:
            continue
        if submission.stickied or submission.over_18:
            continue

        wiki_matches = match_wiki_pages(
            submission.title + " " + (submission.selftext or ""), wiki_slugs
        )
        age_min = int((now - post_time).total_seconds() / 60)

        pick = {
            "title": submission.title,
            "url": f"https://reddit.com{submission.permalink}",
            "score": submission.score,
            "num_comments": submission.num_comments,
            "age_min": age_min,
            "wiki_pages": wiki_matches,
            "body_preview": (submission.selftext or "")[:500],
        }

        if not no_draft and wiki_matches:
            pick["draft"] = gemini_draft_answer(
                genai, submission.title, submission.selftext or "", wiki_matches
            )

        picks.append(pick)
        if len(picks) >= limit:
            break

    print(f"📊 scanned {seen} posts → {len(picks)} picks")
    for i, p in enumerate(picks, 1):
        print(f"  #{i} [{p['num_comments']}c {p['score']}↑ {p['age_min']}m] {p['title'][:60]}")

    msg = format_telegram_message(picks)
    if dry_run:
        print()
        print("=== DRY-RUN: Telegram 送信スキップ ===")
        print(msg)
    else:
        ok = send_telegram(requests, msg)
        if ok:
            print(f"✅ Telegram 送信完了 ({len(picks)} picks)")
        else:
            print(f"⚠️  Telegram 送信失敗")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
