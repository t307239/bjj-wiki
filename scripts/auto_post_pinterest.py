#!/usr/bin/env python3
"""
auto_post_pinterest.py — BJJ Wiki → Pinterest 自動投稿（v2: 個別画像+ハッシュタグ+CTA）

改善点 (v2):
  - ページ別OG画像（og-png/en-{slug}.png）を使用（なければ共通画像にフォールバック）
  - ハッシュタグ付き description（Pinterest SEO向上）
  - CTA付き（BJJ Appへの誘導）
  - カテゴリ自動判定でdescription最適化

認証: OAuth Refresh Token方式（365日有効）
  1. pinterest_oauth_setup.py で初回セットアップ
  2. GitHub Secrets: PINTEREST_APP_ID / PINTEREST_APP_SECRET / PINTEREST_REFRESH_TOKEN
"""
import os
import json
import re
import sys
import urllib.request
import urllib.error
import base64
import random
from datetime import datetime
from pathlib import Path

SITE_URL = "https://wiki.bjj-app.net"
APP_URL = "https://bjj-app.net"


# ── カテゴリ判定 ──
CATEGORY_KEYWORDS = {
    "technique": [
        "choke", "sweep", "guard", "pass", "mount", "escape", "submission",
        "armbar", "triangle", "kimura", "americana", "omoplata", "guillotine",
        "takedown", "throw", "lock", "hold", "control", "transition",
        "hook", "grip", "berimbolo", "half-guard", "open-guard", "closed-guard",
    ],
    "athlete": [
        "gracie", "miyao", "musumeci", "meregali", "galvao", "buchecha",
        "leandro", "marcelo", "roger", "gordon", "ryan", "craig",
        "athlete", "champion", "competitor", "legend",
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


# ── ハッシュタグ ──
HASHTAG_POOLS = {
    "technique": ["#BJJ", "#BrazilianJiuJitsu", "#JiuJitsu", "#Grappling", "#BJJTechnique", "#SubmissionGrappling", "#NoGi", "#MartialArts", "#BJJLifestyle"],
    "athlete": ["#BJJ", "#BrazilianJiuJitsu", "#JiuJitsu", "#Grappling", "#BJJLegend", "#MartialArts", "#JiuJitsuLife", "#BJJCommunity"],
    "training": ["#BJJ", "#BrazilianJiuJitsu", "#JiuJitsu", "#BJJTraining", "#Grappling", "#BJJLife", "#TrainBJJ", "#JiuJitsuLifestyle"],
    "general": ["#BJJ", "#BrazilianJiuJitsu", "#JiuJitsu", "#Grappling", "#MartialArts", "#BJJCommunity"],
}


def build_hashtags(category: str, max_tags: int = 8) -> str:
    """Pinterest用ハッシュタグ（descriptionに含める、多めでOK）"""
    pool = HASHTAG_POOLS.get(category, HASHTAG_POOLS["general"])
    return " ".join(pool[:max_tags])


# ── CTA ──
CTA_LINES = [
    "Track your BJJ progress free at bjj-app.net",
    "Log your training sessions: bjj-app.net",
    "Free BJJ training tracker: bjj-app.net",
    "Start tracking your BJJ journey: bjj-app.net",
]


# ── Telegram通知 ──
def send_telegram(msg):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        payload = json.dumps({"chat_id": chat_id, "text": msg}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload, headers={"Content-Type": "application/json"}, method="POST"
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


class AuthFailure(Exception):
    pass


# ── OAuth Token Refresh ──
def refresh_access_token(app_id, app_secret, refresh_token):
    credentials = base64.b64encode(f"{app_id}:{app_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = f"grant_type=refresh_token&refresh_token={refresh_token}".encode()
    try:
        req = urllib.request.Request(
            "https://api.pinterest.com/v5/oauth/token",
            data=body, headers=headers, method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode())
            new_token = data.get("access_token", "")
            expires_in = data.get("expires_in", 0)
            print(f"[AUTH] Token refreshed (expires_in: {expires_in}s)")
            return new_token
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        print(f"[AUTH ERROR] Refresh failed: HTTP {e.code}: {body_text}")
        if e.code == 401:
            raise AuthFailure(f"Refresh token expired: {body_text}")
        return ""
    except Exception as e:
        print(f"[AUTH ERROR] {e}")
        return ""


def get_access_token():
    refresh_token = os.environ.get("PINTEREST_REFRESH_TOKEN", "")
    app_id = os.environ.get("PINTEREST_APP_ID", "")
    app_secret = os.environ.get("PINTEREST_APP_SECRET", "")
    if refresh_token and app_id and app_secret:
        print("[AUTH] OAuth refresh token flow")
        token = refresh_access_token(app_id, app_secret, refresh_token)
        if token:
            return token
    legacy = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
    if legacy:
        print("[AUTH] Legacy token")
        return legacy
    return ""


# ── Pinterest API v5 ──
def get_image_url(slug: str) -> str:
    """ページ別PNG画像のURL（存在すればper-page、なければ共通画像）"""
    # og-png/ にPNGがあるかチェック（ローカル or URL）
    wiki_root = Path(__file__).parent.parent
    png_path = wiki_root / "og-png" / f"en-{slug}.png"
    if png_path.exists():
        return f"{SITE_URL}/og-png/en-{slug}.png"
    # フォールバック: 共通OG画像
    return f"{SITE_URL}/og-image.png"


def post_to_pinterest(title, description, link, image_url, board_id, access_token):
    if not access_token:
        print("[WARN] No access token")
        return False

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "board_id": board_id,
        "title": title[:100],
        "description": description[:500],
        "link": link,
        "media_source": {
            "source_type": "image_url",
            "url": image_url,
        },
        "alt_text": f"{title} - BJJ technique guide from BJJ Wiki",
    }
    try:
        req = urllib.request.Request(
            "https://api.pinterest.com/v5/pins",
            data=json.dumps(payload).encode(), headers=headers, method="POST"
        )
        result = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
        print(f"  [OK] Pin {result.get('id')}: {title[:50]}")
        return True
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        print(f"  [ERROR] Pinterest {e.code}: {body_text[:200]}")
        if e.code == 401:
            raise AuthFailure(f"Pinterest 401: {body_text}")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


# ── HTML解析 ──
def extract_meta(html_content: str) -> tuple[str, str]:
    t = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL)
    title = t.group(1).replace(" | BJJ Wiki", "").strip() if t else "Untitled"
    d = re.search(r'<meta name="description" content="([^"]*)"', html_content)
    desc = d.group(1) if d else ""
    if not desc:
        p = re.search(r'<p>(.*?)</p>', html_content, re.DOTALL)
        if p:
            desc = re.sub(r'<[^>]+>', '', p.group(1)).strip()[:200]
    return title, desc


def build_pin_description(title: str, desc: str, slug: str) -> str:
    """Pinterest用の最適化されたdescription（ハッシュタグ+CTA付き）"""
    category = detect_category(slug, title)
    tags = build_hashtags(category)

    random.seed(slug)
    cta = CTA_LINES[hash(slug) % len(CTA_LINES)]

    # 説明文を構築（500文字以内）
    parts = []
    if desc:
        parts.append(desc[:200])
    parts.append(cta)
    parts.append(tags)

    result = "\n\n".join(parts)
    return result[:500]


# ── 投稿ログ管理 ──
def load_posted_slugs():
    f = Path(__file__).parent / "already_posted_pinterest.txt"
    if f.exists():
        return set(line.strip() for line in f.read_text(encoding="utf-8").splitlines() if line.strip())
    return set()


def save_posted_slug(slug):
    f = Path(__file__).parent / "already_posted_pinterest.txt"
    with open(f, "a", encoding="utf-8") as fp:
        fp.write(slug + "\n")


# ── メイン ──
def main():
    dry_run = "--dry-run" in sys.argv
    print(f"=== BJJ Wiki Pinterest Auto Post v2 {'(DRY RUN)' if dry_run else ''} === {datetime.now()}")

    access_token = get_access_token()
    board_id = os.environ.get("PINTEREST_BOARD_ID", "")

    if not access_token:
        msg = "Pinterest: token取得失敗"
        print(f"[FATAL] {msg}")
        send_telegram(f"Pinterest: {msg}")
        sys.exit(1)

    if not board_id:
        print("[FATAL] PINTEREST_BOARD_ID not set")
        sys.exit(1)

    en_dir = Path(__file__).parent.parent / "en"
    if not en_dir.exists():
        print(f"[ERROR] {en_dir} not found")
        return

    html_files = sorted(en_dir.glob("*.html"), key=lambda f: f.stat().st_mtime, reverse=True)
    posted_slugs = load_posted_slugs()
    skip_slugs = {"index", "about", "contact", "404"}
    candidates = [f for f in html_files if f.stem not in posted_slugs and f.stem not in skip_slugs]
    remaining = len(candidates)
    print(f"Total: {len(html_files)} | Posted: {len(posted_slugs)} | Remaining: {remaining}")

    posted_count = 0
    error_count = 0
    limit = 5

    for html_file in html_files:
        if posted_count >= limit:
            break
        slug = html_file.stem
        if slug in skip_slugs or slug in posted_slugs:
            continue

        try:
            html_content = html_file.read_text(encoding="utf-8")
        except Exception:
            continue

        title, desc = extract_meta(html_content)
        if not title or not desc:
            continue

        url = f"{SITE_URL}/en/{slug}.html"
        image_url = get_image_url(slug)
        pin_desc = build_pin_description(title, desc, slug)
        category = detect_category(slug, title)

        print(f"  [{category}] {slug}")
        print(f"    image: {image_url}")

        if dry_run:
            print(f"    [DRY RUN] title={title[:60]}")
            print(f"    desc={pin_desc[:100]}...")
            posted_count += 1
            continue

        try:
            if post_to_pinterest(title, pin_desc, url, image_url, board_id, access_token):
                save_posted_slug(slug)
                posted_count += 1
                error_count = 0
            else:
                error_count += 1
        except AuthFailure as e:
            print(f"[FATAL] Auth: {e}")
            send_telegram(f"Pinterest auth failed. Re-run pinterest_oauth_setup.py")
            sys.exit(1)

        if error_count >= 3:
            print("[WARN] 3 consecutive errors — stopping")
            send_telegram(f"Pinterest: 3 consecutive errors")
            break

    actual_remaining = remaining - posted_count
    print(f"\nDone: {posted_count} pins | Remaining: {actual_remaining}")
    if posted_count > 0 and not dry_run:
        send_telegram(f"Pinterest: {posted_count} pins (remaining: {actual_remaining})")


if __name__ == "__main__":
    main()
