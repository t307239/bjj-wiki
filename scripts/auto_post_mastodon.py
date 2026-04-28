#!/usr/bin/env python3
"""
auto_post_mastodon.py — BJJ Wiki → Mastodon 自動投稿

Mastodon API を使用。テキスト投稿（500文字以内）。
完全無料・分散型SNS。フィットネス/格闘技コミュニティに到達可能。

必要な環境変数（GitHub Secrets）:
  MASTODON_INSTANCE     — インスタンスURL（例: https://mastodon.social）
  MASTODON_ACCESS_TOKEN — アクセストークン
  TELEGRAM_BOT_TOKEN    — Telegram通知用（任意）
  TELEGRAM_CHAT_ID      — Telegram チャットID（任意）

セットアップ:
  1. Mastodonインスタンスでアカウント作成（mastodon.social 推奨）
  2. Settings → Development → New Application
     - Application name: BJJ Wiki Bot
     - Scopes: write:statuses
  3. 生成された Access Token を GitHub Secrets に設定

Usage:
  python3 scripts/auto_post_mastodon.py [--dry-run] [--limit N]
"""

import os
import sys
import json
import re
import time
import glob
import random
import urllib.request
import urllib.error
from datetime import datetime

SITE_BASE_URL = "https://wiki.bjj-app.net"
POSTED_LOG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "already_posted_mastodon.txt")
MAX_POST_LEN = 500
DEFAULT_LIMIT = 1


# ────────────────────────────────────────────
#  カテゴリ・テンプレート
# ────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "technique": [
        "choke", "sweep", "guard", "pass", "mount", "escape", "submission",
        "armbar", "triangle", "kimura", "americana", "omoplata", "guillotine",
        "takedown", "throw", "lock", "hold", "control", "transition",
    ],
    "athlete": [
        "gracie", "miyao", "musumeci", "meregali", "galvao", "buchecha",
        "marcelo", "roger", "gordon", "ryan", "legend", "champion",
    ],
    "training": [
        "drill", "training", "workout", "beginner", "fundamental",
        "concept", "principle", "strategy",
    ],
}


def detect_category(slug: str, title: str) -> str:
    text = f"{slug} {title}".lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in kws):
            return cat
    return "general"


POST_TEMPLATES = {
    "technique": [
        "{title}\n\n{short_desc}\n\nFull guide: {url}\n\nTrack your BJJ training free at bjj-app.net\n\n{tags}",
        "Technique breakdown: {title}\n\n{short_desc}\n\n{url}\n\n{tags}",
        "Want to improve your {title_lower}?\n\nRead the full guide: {url}\n\n{tags}",
    ],
    "athlete": [
        "{title}\n\n{short_desc}\n\nFull profile: {url}\n\n{tags}",
        "BJJ Legend: {title}\n\n{url}\n\n{tags}",
    ],
    "training": [
        "{title}\n\n{short_desc}\n\n{url}\n\nFree training log: bjj-app.net\n\n{tags}",
    ],
    "general": [
        "{title}\n\n{short_desc}\n\n{url}\n\n{tags}",
        "New on BJJ Wiki: {title}\n\n{url}\n\n{tags}",
    ],
}

HASHTAG_POOLS = {
    "technique": ["#BJJ", "#BrazilianJiuJitsu", "#JiuJitsu", "#Grappling", "#MartialArts"],
    "athlete": ["#BJJ", "#BrazilianJiuJitsu", "#MartialArts", "#JiuJitsu"],
    "training": ["#BJJ", "#BrazilianJiuJitsu", "#Grappling", "#Training"],
    "general": ["#BJJ", "#BrazilianJiuJitsu", "#JiuJitsu", "#Grappling"],
}


# ────────────────────────────────────────────
#  Mastodon API
# ────────────────────────────────────────────
def mastodon_post(text: str, instance: str, access_token: str, dry_run: bool = False) -> dict | None:
    """Mastodon API でステータスを投稿"""
    if dry_run:
        print(f"  [DRY RUN] ({len(text)} chars):")
        print(f"  {text[:200]}...")
        return {"id": "dry_run"}

    url = f"{instance.rstrip('/')}/api/v1/statuses"
    payload = json.dumps({
        "status": text,
        "visibility": "public",
        "language": "en",
    }).encode()

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            print(f"  [OK] Toot: {result.get('id', '')}")
            return result
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  [ERROR] Mastodon {e.code}: {body[:300]}")
        if e.code == 401 or e.code == 403:
            raise RuntimeError(f"Mastodon auth failed: {body}")
        return None


def send_telegram(msg: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": msg}).encode()
    req = urllib.request.Request(url, data=payload)
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


# ────────────────────────────────────────────
#  ページスキャン・投稿文生成
# ────────────────────────────────────────────
def extract_page_meta(filepath: str) -> dict | None:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None

    title_m = re.search(r"<title>([^<]+)</title>", content, re.IGNORECASE)
    desc_m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>', content, re.IGNORECASE | re.DOTALL)

    if not title_m:
        return None

    title = title_m.group(1).strip()
    desc = desc_m.group(1).strip()[:200] if desc_m else ""
    return {"title": title, "description": desc}


def build_post(slug: str, title: str, description: str, url: str) -> str:
    """テンプレートベースの投稿文生成（500文字以内）"""
    clean_title = re.sub(r"\s+[|–—]\s+.*$", "", title).strip()
    clean_title = re.sub(r"\s+-\s+BJJ Wiki.*$", "", clean_title).strip()
    if not clean_title:
        clean_title = title

    category = detect_category(slug, clean_title)
    templates = POST_TEMPLATES.get(category, POST_TEMPLATES["general"])

    random.seed(slug)
    template = templates[hash(slug) % len(templates)]
    tags = " ".join(HASHTAG_POOLS.get(category, HASHTAG_POOLS["general"])[:4])

    short_desc = description.split(".")[0].strip()
    if short_desc and not short_desc.endswith("."):
        short_desc += "."
    if len(short_desc) > 120:
        short_desc = short_desc[:117] + "..."

    post = template.format(
        title=clean_title,
        title_lower=clean_title.lower() if clean_title[0].isupper() else clean_title,
        short_desc=short_desc,
        url=url,
        tags=tags,
    )

    if len(post) > MAX_POST_LEN:
        post = f"{clean_title}\n\n{url}\n\n{tags}"

    return post.strip()[:MAX_POST_LEN]


def load_posted_log() -> set:
    if not os.path.exists(POSTED_LOG):
        return set()
    with open(POSTED_LOG, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_posted_log(posted: set) -> None:
    with open(POSTED_LOG, "w", encoding="utf-8") as f:
        for slug in sorted(posted):
            f.write(slug + "\n")


def main():
    dry_run = "--dry-run" in sys.argv
    limit = DEFAULT_LIMIT
    for i, arg in enumerate(sys.argv):
        if arg == "--limit" and i + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 1])
            except ValueError:
                pass

    instance = os.environ.get("MASTODON_INSTANCE", "")
    access_token = os.environ.get("MASTODON_ACCESS_TOKEN", "")

    if not instance or not access_token:
        print("[WARN] MASTODON_INSTANCE or MASTODON_ACCESS_TOKEN not set — skipping")
        print("Setup: mastodon.social → Settings → Development → New Application")
        sys.exit(0)

    # ── z226: launch announcement one-shot ──
    from _launch_announce import check_and_consume
    launch_text = check_and_consume("mastodon")
    if launch_text:
        print(f"=== LAUNCH ANNOUNCEMENT (Mastodon) === ({len(launch_text)} chars)")
        try:
            result = mastodon_post(launch_text, instance, access_token, dry_run=dry_run)
            if not dry_run and result:
                send_telegram(f"Mastodon launch announcement posted ✅")
                print(f"  POSTED: {result}")
            return
        except Exception as e:
            print(f"  FAIL: {e}")
            if not dry_run:
                send_telegram(f"Mastodon launch announcement FAILED: {e}")
            sys.exit(1)

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    en_dir = os.path.join(base, "en")
    html_files = sorted(glob.glob(os.path.join(en_dir, "*.html")), key=os.path.getmtime, reverse=True)
    posted = load_posted_log()
    total_pages = len(html_files)
    remaining = total_pages - len(posted)

    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"=== BJJ Wiki Mastodon Auto Post ({mode}) ===")
    print(f"Total: {total_pages} | Posted: {len(posted)} | Remaining: {remaining}")
    print()

    count = 0
    newly_posted = []

    for filepath in html_files:
        if count >= limit:
            break

        slug = os.path.basename(filepath).replace(".html", "")
        if slug in posted or slug in {"index", "about", "contact", "404"}:
            continue

        meta = extract_page_meta(filepath)
        if not meta:
            continue

        page_url = f"{SITE_BASE_URL}/en/{slug}.html"
        category = detect_category(slug, meta["title"])
        post_text = build_post(slug, meta["title"], meta["description"], page_url)

        print(f"  [{category}] {slug}")
        try:
            result = mastodon_post(post_text, instance, access_token, dry_run=dry_run)
        except RuntimeError as e:
            print(f"  FAIL: {e}")
            if not dry_run:
                send_telegram(f"Mastodon auth failed: {e}")
            sys.exit(1)

        if result:
            count += 1
            newly_posted.append(slug)
            posted.add(slug)
            if not dry_run:
                time.sleep(3)

    if not dry_run:
        save_posted_log(posted)

    print(f"\n=== Done: {count} toots ===")
    print(f"  Remaining: {total_pages - len(posted)}/{total_pages}")

    if count > 0 and not dry_run:
        send_telegram(
            f"Mastodon: {count} posts\n"
            + "\n".join(f"  {s}" for s in newly_posted)
        )


if __name__ == "__main__":
    main()
