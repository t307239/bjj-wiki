#!/usr/bin/env python3
"""
auto_post_threads.py — BJJ Wiki → Threads 自動投稿

Threads API (Meta Graph API) を使用。
テキスト投稿（500文字以内）+ リンク付き。

必要な環境変数（GitHub Secrets）:
  THREADS_ACCESS_TOKEN   — Long-lived User Access Token
  THREADS_USER_ID        — Threads User ID
  TELEGRAM_BOT_TOKEN     — Telegram通知用（任意）
  TELEGRAM_CHAT_ID       — Telegram チャットID（任意）

Threads Developer Portal での設定:
  1. https://developers.facebook.com/ でアプリ作成
  2. Threads API → threads_basic, threads_content_publish のパーミッション取得
  3. User Access Token を取得（60日有効、refresh可能）
  4. User ID: GET https://graph.threads.net/v1.0/me?access_token=TOKEN

Usage:
  python3 scripts/auto_post_threads.py [--dry-run] [--limit N]
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
APP_URL = "https://bjj-app.net"
POSTED_LOG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "already_posted_threads.txt")
MAX_POST_LEN = 500
DEFAULT_LIMIT = 1

THREADS_API_BASE = "https://graph.threads.net/v1.0"


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
        "{title}\n\n{short_desc}\n\nFull guide: {url}\n\nTrack your training free at bjj-app.net\n\n{tags}",
        "Technique spotlight: {title}\n\n{short_desc}\n\nLearn more: {url}\n\n{tags}",
        "Want to improve your {title_lower}?\n\nRead the full breakdown: {url}\n\nLog your rolls at bjj-app.net\n\n{tags}",
    ],
    "athlete": [
        "{title}\n\n{short_desc}\n\nFull profile: {url}\n\n{tags}",
        "BJJ Legend: {title}\n\n{short_desc}\n\nRead more: {url}\n\n{tags}",
    ],
    "training": [
        "{title}\n\n{short_desc}\n\nFull guide: {url}\n\nFree training tracker: bjj-app.net\n\n{tags}",
        "Training tip: {title}\n\n{url}\n\nTrack your progress: bjj-app.net\n\n{tags}",
    ],
    "general": [
        "{title}\n\n{short_desc}\n\nRead more: {url}\n\n{tags}",
        "New on BJJ Wiki: {title}\n\n{url}\n\n{tags}",
    ],
}

HASHTAG_POOLS = {
    "technique": ["#BJJ", "#BrazilianJiuJitsu", "#JiuJitsu", "#Grappling", "#BJJTechnique"],
    "athlete": ["#BJJ", "#BrazilianJiuJitsu", "#JiuJitsu", "#BJJLegend", "#MartialArts"],
    "training": ["#BJJ", "#BrazilianJiuJitsu", "#BJJTraining", "#Grappling", "#JiuJitsuLife"],
    "general": ["#BJJ", "#BrazilianJiuJitsu", "#JiuJitsu", "#Grappling"],
}


# ────────────────────────────────────────────
#  Threads API
# ────────────────────────────────────────────
def create_threads_post(text: str, user_id: str, access_token: str, dry_run: bool = False) -> dict | None:
    """Threads API でテキスト投稿を作成する（2ステップ: create → publish）"""
    if dry_run:
        print(f"  [DRY RUN] ({len(text)} chars):")
        print(f"  {text[:200]}...")
        return {"id": "dry_run"}

    # Step 1: Create media container
    create_url = f"{THREADS_API_BASE}/{user_id}/threads"
    params = {
        "media_type": "TEXT",
        "text": text,
        "access_token": access_token,
    }
    encoded = urllib.parse.urlencode(params).encode()

    try:
        req = urllib.request.Request(create_url, data=encoded, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            container_id = result.get("id")
            if not container_id:
                print(f"  [ERROR] No container ID: {result}")
                return None
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  [ERROR] Create failed {e.code}: {body[:300]}")
        if e.code == 401:
            raise RuntimeError(f"Threads auth failed: {body}")
        return None

    # Step 2: Publish
    time.sleep(2)  # Wait for container to be ready
    publish_url = f"{THREADS_API_BASE}/{user_id}/threads_publish"
    publish_params = {
        "creation_id": container_id,
        "access_token": access_token,
    }
    encoded = urllib.parse.urlencode(publish_params).encode()

    try:
        req = urllib.request.Request(publish_url, data=encoded, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            post_id = result.get("id")
            print(f"  [OK] Thread {post_id}")
            return result
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  [ERROR] Publish failed {e.code}: {body[:300]}")
        return None


import urllib.parse


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


def build_threads_post(slug: str, title: str, description: str, url: str) -> str:
    """テンプレートベースの投稿文生成（500文字以内）"""
    clean_title = re.sub(r"\s*[-|–—].*$", "", title).strip()
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

    access_token = os.environ.get("THREADS_ACCESS_TOKEN", "")
    user_id = os.environ.get("THREADS_USER_ID", "")

    if not access_token or not user_id:
        print("[WARN] THREADS_ACCESS_TOKEN or THREADS_USER_ID not set — skipping")
        print("Setup: https://developers.facebook.com/ → Threads API")
        sys.exit(0)  # Exit 0 so GHA doesn't fail

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    en_dir = os.path.join(base, "en")
    html_files = sorted(glob.glob(os.path.join(en_dir, "*.html")), key=os.path.getmtime, reverse=True)
    posted = load_posted_log()
    total_pages = len(html_files)
    remaining = total_pages - len(posted)

    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"=== BJJ Wiki Threads Auto Post ({mode}) ===")
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
        post_text = build_threads_post(slug, meta["title"], meta["description"], page_url)

        print(f"  [{category}] {slug}")
        try:
            result = create_threads_post(post_text, user_id, access_token, dry_run=dry_run)
        except RuntimeError as e:
            print(f"  FAIL: {e}")
            if not dry_run:
                send_telegram(f"Threads auth failed: {e}")
            sys.exit(1)

        if result:
            count += 1
            newly_posted.append(slug)
            posted.add(slug)
            if not dry_run:
                time.sleep(3)  # Rate limit
        else:
            print(f"  [SKIP] Failed to post {slug}")

    if not dry_run:
        save_posted_log(posted)

    print(f"\n=== Done: {count} threads ===")
    print(f"  Remaining: {total_pages - len(posted)}/{total_pages}")

    if count > 0 and not dry_run:
        send_telegram(
            f"Threads: {count} posts\n"
            + "\n".join(f"  {s}" for s in newly_posted)
        )


if __name__ == "__main__":
    main()
