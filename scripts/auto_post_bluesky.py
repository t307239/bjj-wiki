#!/usr/bin/env python3
"""
auto_post_bluesky.py — BJJ Wiki → Bluesky 自動投稿

AT Protocol (atproto) を使用。テキスト投稿 + リンクカード。
Blueskyは完全無料API。海外BJJコミュニティに強い。

必要な環境変数（GitHub Secrets）:
  BLUESKY_HANDLE     — Blueskyハンドル（例: bjjwiki.bsky.social）
  BLUESKY_APP_PASSWORD — App Password（Settings → App Passwords で生成）
  TELEGRAM_BOT_TOKEN  — Telegram通知用（任意）
  TELEGRAM_CHAT_ID    — Telegram チャットID（任意）

セットアップ:
  1. https://bsky.app/ でアカウント作成
  2. Settings → App Passwords → Generate App Password
  3. GitHub Secrets に BLUESKY_HANDLE / BLUESKY_APP_PASSWORD を設定

Usage:
  python3 scripts/auto_post_bluesky.py [--dry-run] [--limit N]
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
from datetime import datetime, timezone

SITE_BASE_URL = "https://wiki.bjj-app.net"
POSTED_LOG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "already_posted_bluesky.txt")
MAX_POST_LEN = 300  # Bluesky 300 char limit
DEFAULT_LIMIT = 1

BSKY_API = "https://bsky.social/xrpc"


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
        "{title}\n\n{short_desc}\n\nFull guide: {url}",
        "Technique spotlight: {title}\n\n{url}",
        "Level up your game: {title}\n\n{short_desc}\n\n{url}",
    ],
    "athlete": [
        "{title}\n\n{short_desc}\n\n{url}",
        "BJJ Legend: {title}\n\nFull profile: {url}",
    ],
    "training": [
        "{title}\n\n{short_desc}\n\n{url}",
        "Training tip: {title}\n\n{url}",
    ],
    "general": [
        "{title}\n\n{short_desc}\n\n{url}",
        "New on BJJ Wiki: {title}\n\n{url}",
    ],
}


# ────────────────────────────────────────────
#  Bluesky AT Protocol API
# ────────────────────────────────────────────
def bsky_login(handle: str, app_password: str) -> tuple[str, str]:
    """ログインしてaccess JWT + DID を取得"""
    url = f"{BSKY_API}/com.atproto.server.createSession"
    payload = json.dumps({"identifier": handle, "password": app_password}).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        return data["accessJwt"], data["did"]


def bsky_create_post(text: str, link_url: str, link_title: str, link_desc: str,
                     access_jwt: str, did: str, dry_run: bool = False) -> dict | None:
    """Bluesky投稿を作成（リンクカード facet 付き）"""
    if dry_run:
        print(f"  [DRY RUN] ({len(text)} chars):")
        print(f"  {text[:200]}...")
        return {"uri": "dry_run"}

    # リンクのバイト位置を検出（facet用）
    text_bytes = text.encode("utf-8")
    url_bytes = link_url.encode("utf-8")
    url_start = text_bytes.find(url_bytes)

    facets = []
    if url_start >= 0:
        facets.append({
            "index": {
                "byteStart": url_start,
                "byteEnd": url_start + len(url_bytes),
            },
            "features": [{
                "$type": "app.bsky.richtext.facet#link",
                "uri": link_url,
            }]
        })

    # 外部リンクカード（embed）
    embed = {
        "$type": "app.bsky.embed.external",
        "external": {
            "uri": link_url,
            "title": link_title[:300],
            "description": link_desc[:300] if link_desc else "",
        }
    }

    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "langs": ["en"],
    }
    if facets:
        record["facets"] = facets
    record["embed"] = embed

    url = f"{BSKY_API}/com.atproto.repo.createRecord"
    payload = json.dumps({
        "repo": did,
        "collection": "app.bsky.feed.post",
        "record": record,
    }).encode()

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {access_jwt}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            print(f"  [OK] Post: {result.get('uri', '')[:60]}")
            return result
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  [ERROR] Bluesky {e.code}: {body[:300]}")
        if e.code == 401:
            raise RuntimeError(f"Bluesky auth failed: {body}")
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
    """テンプレートベースの投稿文生成（300文字以内）"""
    # " | BJJ Wiki" 等のサフィックス除去（ハイフン入り語は保持）
    clean_title = re.sub(r"\s+[|–—]\s+.*$", "", title).strip()
    clean_title = re.sub(r"\s+-\s+BJJ Wiki.*$", "", clean_title).strip()
    if not clean_title:
        clean_title = title

    category = detect_category(slug, clean_title)
    templates = POST_TEMPLATES.get(category, POST_TEMPLATES["general"])

    random.seed(slug)
    template = templates[hash(slug) % len(templates)]

    short_desc = description.split(".")[0].strip()
    if short_desc and not short_desc.endswith("."):
        short_desc += "."
    if len(short_desc) > 100:
        short_desc = short_desc[:97] + "..."

    post = template.format(
        title=clean_title,
        title_lower=clean_title.lower() if clean_title[0].isupper() else clean_title,
        short_desc=short_desc,
        url=url,
    )

    if len(post) > MAX_POST_LEN:
        post = f"{clean_title}\n\n{url}"

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

    handle = os.environ.get("BLUESKY_HANDLE", "")
    app_password = os.environ.get("BLUESKY_APP_PASSWORD", "")

    if not handle or not app_password:
        print("[WARN] BLUESKY_HANDLE or BLUESKY_APP_PASSWORD not set — skipping")
        print("Setup: bsky.app → Settings → App Passwords")
        sys.exit(0)

    # ログイン
    access_jwt = ""
    did = ""
    if not dry_run:
        try:
            access_jwt, did = bsky_login(handle, app_password)
            print(f"[AUTH] Logged in as {handle} (DID: {did[:20]}...)")
        except Exception as e:
            print(f"[FATAL] Bluesky login failed: {e}")
            send_telegram(f"Bluesky login failed: {e}")
            sys.exit(1)

    # ── z226: launch announcement one-shot ──
    from _launch_announce import check_and_consume
    launch_text = check_and_consume("bluesky")
    if launch_text:
        print(f"=== LAUNCH ANNOUNCEMENT (Bluesky) === ({len(launch_text)} chars)")
        try:
            # link card 不要、text のみ post
            result = bsky_create_post(
                launch_text,
                link_url="",
                link_title="",
                link_desc="",
                access_jwt=access_jwt,
                did=did,
                dry_run=dry_run,
            )
            if not dry_run and result:
                send_telegram(f"Bluesky launch announcement posted ✅")
                print(f"  POSTED: {result}")
            return
        except Exception as e:
            print(f"  FAIL: {e}")
            if not dry_run:
                send_telegram(f"Bluesky launch announcement FAILED: {e}")
            sys.exit(1)

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    en_dir = os.path.join(base, "en")
    html_files = sorted(glob.glob(os.path.join(en_dir, "*.html")), key=os.path.getmtime, reverse=True)
    posted = load_posted_log()
    total_pages = len(html_files)
    remaining = total_pages - len(posted)

    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"=== BJJ Wiki Bluesky Auto Post ({mode}) ===")
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

        # タイトルをクリーンアップ（embed用）
        clean_title = re.sub(r"\s+[|–—]\s+.*$", "", meta["title"]).strip()
        clean_title = re.sub(r"\s+-\s+BJJ Wiki.*$", "", clean_title).strip()

        print(f"  [{category}] {slug}")
        try:
            result = bsky_create_post(
                post_text, page_url, clean_title, meta["description"],
                access_jwt, did, dry_run=dry_run
            )
        except RuntimeError as e:
            print(f"  FAIL: {e}")
            if not dry_run:
                send_telegram(f"Bluesky auth failed: {e}")
            sys.exit(1)

        if result:
            count += 1
            newly_posted.append(slug)
            posted.add(slug)
            if not dry_run:
                time.sleep(2)

    if not dry_run:
        save_posted_log(posted)

    print(f"\n=== Done: {count} posts ===")
    print(f"  Remaining: {total_pages - len(posted)}/{total_pages}")

    if count > 0 and not dry_run:
        send_telegram(
            f"Bluesky: {count} posts\n"
            + "\n".join(f"  {s}" for s in newly_posted)
        )


if __name__ == "__main__":
    main()
