#!/usr/bin/env python3
"""
auto_post_x.py — BJJ Wiki → X (Twitter) 自動投稿（v2: テンプレバリエーション+CTA）

改善点 (v2):
  - 5パターンのツイートテンプレート（単調さ解消）
  - CTA付き（BJJ Appへの誘導）
  - ページカテゴリ自動判定（テクニック/選手/歴史/ルール等）
  - ハッシュタグのバリエーション

必要な環境変数（GitHub Secrets）:
  X_API_KEY / X_API_SECRET / X_ACCESS_TOKEN / X_ACCESS_TOKEN_SECRET
  TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID（任意）

Usage:
  python3 scripts/auto_post_x.py [--dry-run] [--limit N]
"""

import os
import sys
import json
import time
import glob
import re
import hmac
import hashlib
import base64
import urllib.parse
import urllib.request
import random
from datetime import datetime, timezone


# ────────────────────────────────────────────
#  設定
# ────────────────────────────────────────────
SITE_BASE_URL = "https://wiki.bjj-app.net"
APP_URL = "https://bjj-app.net"
POSTED_LOG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "already_posted_x.txt")
MAX_TWEET_LEN = 280
DEFAULT_LIMIT = 1

# ────────────────────────────────────────────
#  テンプレートシステム
# ────────────────────────────────────────────

# カテゴリ判定キーワード
CATEGORY_KEYWORDS = {
    "technique": [
        "choke", "sweep", "guard", "pass", "mount", "escape", "submission",
        "armbar", "triangle", "kimura", "americana", "omoplata", "guillotine",
        "takedown", "throw", "lock", "hold", "control", "transition",
        "hook", "grip", "berimbolo", "half-guard", "open-guard", "closed-guard",
        "side-control", "back-take", "knee-on-belly", "north-south",
    ],
    "athlete": [
        "gracie", "miyao", "musumeci", "meregali", "galvao", "buchecha",
        "leandro", "marcelo", "roger", "gordon", "ryan", "craig", "jones",
        "keenan", "cornelius", "lachlan", "nicky", "mikey", "tainan",
        "athlete", "champion", "competitor", "fighter", "legend",
    ],
    "history": [
        "history", "origin", "evolution", "tradition", "lineage", "founding",
        "ancient", "century", "era", "development",
    ],
    "rules": [
        "rule", "scoring", "point", "advantage", "penalty", "ibjjf",
        "adcc", "competition", "tournament", "weight-class", "belt-system",
    ],
    "training": [
        "drill", "training", "workout", "conditioning", "warm-up",
        "beginner", "fundamental", "concept", "principle", "mindset",
        "strategy", "game-plan",
    ],
}

# テンプレート（{title}, {desc}, {url}, {cta}, {tags} をプレースホルダ）
TWEET_TEMPLATES = {
    "technique": [
        "{title}\n\n{short_desc}\n\n{url}\n{cta}\n{tags}",
        "Do you know {title_lower}?\n\n{short_desc}\n\nFull guide:\n{url}\n{cta}\n{tags}",
        "Level up your game with {title_lower}\n\n{url}\n{cta}\n{tags}",
        "Technique breakdown: {title}\n\n{short_desc}\n\n{url}\n{tags}",
        "Add this to your arsenal:\n{title}\n\n{url}\n{cta}\n{tags}",
    ],
    "athlete": [
        "{title}\n\n{short_desc}\n\n{url}\n{tags}",
        "Learn about {title_lower}\n\n{short_desc}\n\nFull profile:\n{url}\n{tags}",
        "BJJ Legend: {title}\n\n{url}\n{tags}",
    ],
    "history": [
        "{title}\n\n{short_desc}\n\n{url}\n{tags}",
        "Did you know?\n\n{short_desc}\n\nRead more:\n{url}\n{tags}",
    ],
    "rules": [
        "{title}\n\n{short_desc}\n\n{url}\n{tags}",
        "Know the rules:\n{title}\n\n{url}\n{tags}",
    ],
    "training": [
        "{title}\n\n{short_desc}\n\n{url}\n{cta}\n{tags}",
        "Training tip: {title_lower}\n\n{url}\n{cta}\n{tags}",
    ],
    "default": [
        "{title}\n\n{short_desc}\n\n{url}\n{tags}",
        "New on BJJ Wiki:\n{title}\n\n{url}\n{tags}",
        "{title}\n\n{url}\n{cta}\n{tags}",
    ],
}

# CTA（ランダム選択）
CTA_LINES = [
    "Track your training: bjj-app.net",
    "Log your rolls at bjj-app.net",
    "Free BJJ training log: bjj-app.net",
]

# ハッシュタグのプール（カテゴリ別）
HASHTAG_POOLS = {
    "technique": ["#BJJ", "#BrazilianJiuJitsu", "#柔術", "#Grappling", "#JiuJitsuTechnique", "#NoGi", "#SubmissionGrappling"],
    "athlete": ["#BJJ", "#BrazilianJiuJitsu", "#柔術", "#JiuJitsuLegend", "#Grappling", "#MartialArts"],
    "history": ["#BJJ", "#BrazilianJiuJitsu", "#柔術", "#MartialArtsHistory", "#JiuJitsuHistory"],
    "rules": ["#BJJ", "#BrazilianJiuJitsu", "#柔術", "#IBJJF", "#Competition", "#Tournament"],
    "training": ["#BJJ", "#BrazilianJiuJitsu", "#柔術", "#BJJTraining", "#Grappling", "#JiuJitsuLife"],
    "default": ["#BJJ", "#BrazilianJiuJitsu", "#柔術", "#Grappling", "#MartialArts"],
}


def detect_category(slug: str, title: str) -> str:
    """ページのカテゴリを自動判定"""
    text = f"{slug} {title}".lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for kw in keywords if kw in text)
    if not scores:
        return "default"
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "default"


def select_hashtags(category: str, max_tags: int = 4) -> str:
    """カテゴリに基づいてハッシュタグを選択"""
    pool = HASHTAG_POOLS.get(category, HASHTAG_POOLS["default"])
    # 最初の2つ（#BJJ, #BrazilianJiuJitsu）は固定、残りをランダム
    fixed = pool[:2]
    variable = pool[2:]
    random.shuffle(variable)
    selected = fixed + variable[:max(0, max_tags - len(fixed))]
    return " ".join(selected)


# ────────────────────────────────────────────
#  OAuth 1.0a 署名生成（tweepyなしで動作）
# ────────────────────────────────────────────
def _nonce() -> str:
    return base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("=")


def _timestamp() -> str:
    return str(int(time.time()))


def _percent_encode(s: str) -> str:
    return urllib.parse.quote(s, safe="")


def _build_oauth_header(
    method: str,
    url: str,
    params: dict,
    api_key: str,
    api_secret: str,
    access_token: str,
    access_token_secret: str,
) -> str:
    oauth_params = {
        "oauth_consumer_key":     api_key,
        "oauth_nonce":            _nonce(),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp":        _timestamp(),
        "oauth_token":            access_token,
        "oauth_version":          "1.0",
    }

    all_params = {**params, **oauth_params}
    sorted_params = "&".join(
        f"{_percent_encode(k)}={_percent_encode(v)}"
        for k, v in sorted(all_params.items())
    )

    base_string = "&".join([
        method.upper(),
        _percent_encode(url),
        _percent_encode(sorted_params),
    ])

    signing_key = f"{_percent_encode(api_secret)}&{_percent_encode(access_token_secret)}"

    signature = base64.b64encode(
        hmac.new(
            signing_key.encode("utf-8"),
            base_string.encode("utf-8"),
            hashlib.sha1,
        ).digest()
    ).decode()
    oauth_params["oauth_signature"] = signature

    header_parts = ", ".join(
        f'{_percent_encode(k)}="{_percent_encode(v)}"'
        for k, v in sorted(oauth_params.items())
    )
    return f"OAuth {header_parts}"


def post_tweet(text: str, dry_run: bool = False) -> dict | None:
    """X API v2 でツイートを投稿する"""
    if dry_run:
        print(f"  [DRY RUN] Would tweet ({len(text)} chars):")
        print(f"  {text}")
        print()
        return {"id": "dry_run", "text": text}

    api_key             = os.environ.get("X_API_KEY", "")
    api_secret          = os.environ.get("X_API_SECRET", "")
    access_token        = os.environ.get("X_ACCESS_TOKEN", "")
    access_token_secret = os.environ.get("X_ACCESS_TOKEN_SECRET", "")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        raise RuntimeError("X API credentials not set")

    url     = "https://api.twitter.com/2/tweets"
    payload = json.dumps({"text": text}).encode("utf-8")
    auth    = _build_oauth_header("POST", url, {}, api_key, api_secret, access_token, access_token_secret)

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", auth)
    req.add_header("Content-Type", "application/json")

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                return result.get("data", result)
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if e.code == 403 and "just a moment" in body.lower() and attempt < 2:
                wait = 30 * (attempt + 1)
                print(f"  [RETRY] Cloudflare 403 → {wait}s wait ({attempt+1}/3)")
                time.sleep(wait)
                continue
            raise RuntimeError(f"Twitter API error {e.code}: {body[:500]}")


def send_telegram(msg: str) -> None:
    token   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return
    url     = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": msg}).encode()
    req     = urllib.request.Request(url, data=payload)
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


# ────────────────────────────────────────────
#  ページスキャン・ツイート文生成
# ────────────────────────────────────────────
def extract_page_meta(filepath: str) -> dict | None:
    """HTML ファイルからタイトルと description を抽出"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None

    title_m = re.search(r"<title>([^<]+)</title>", content, re.IGNORECASE)
    desc_m  = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>', content, re.IGNORECASE | re.DOTALL)

    if not title_m:
        return None

    title = title_m.group(1).strip()
    desc  = desc_m.group(1).strip()[:150] if desc_m else ""

    return {"title": title, "description": desc}


def build_tweet(slug: str, title: str, description: str, url: str) -> str:
    """テンプレベースのツイート文を生成（280文字以内）"""
    # タイトルをクリーンアップ
    clean_title = re.sub(r"\s*[-|–—].*$", "", title).strip()
    if not clean_title:
        clean_title = title

    # カテゴリ判定
    category = detect_category(slug, clean_title)

    # テンプレート選択（slug のハッシュで決定的 + バリエーション）
    templates = TWEET_TEMPLATES.get(category, TWEET_TEMPLATES["default"])
    template_idx = hash(slug) % len(templates)
    template = templates[template_idx]

    # ハッシュタグ選択
    random.seed(slug)  # 同じslugなら同じ結果（冪等性）
    tags = select_hashtags(category, max_tags=4)

    # CTA選択
    cta_idx = hash(slug + "cta") % len(CTA_LINES)
    cta = CTA_LINES[cta_idx]

    # 短い説明文（1文目のみ）
    short_desc = description.split(".")[0].strip()
    if short_desc and not short_desc.endswith("."):
        short_desc += "."
    if len(short_desc) > 100:
        short_desc = short_desc[:97] + "..."

    # テンプレ展開
    tweet = template.format(
        title=clean_title,
        title_lower=clean_title.lower() if clean_title[0].isupper() else clean_title,
        short_desc=short_desc,
        url=url,
        cta=cta,
        tags=tags,
    )

    # 280文字に収める（URLは23文字固定でカウントされる）
    # 実際のURL長を考慮してトリミング
    if len(tweet) > MAX_TWEET_LEN:
        # CTAを削除して再試行
        tweet = template.replace("\n{cta}", "").format(
            title=clean_title,
            title_lower=clean_title.lower() if clean_title[0].isupper() else clean_title,
            short_desc=short_desc,
            url=url,
            cta="",
            tags=tags,
        )

    if len(tweet) > MAX_TWEET_LEN:
        # 説明文を短縮
        tweet = f"{clean_title}\n\n{url}\n{tags}"

    return tweet.strip()


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
    limit   = DEFAULT_LIMIT
    for i, arg in enumerate(sys.argv):
        if arg == "--limit" and i + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 1])
            except ValueError:
                pass

    base        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    en_dir      = os.path.join(base, "en")
    html_files  = sorted(glob.glob(os.path.join(en_dir, "*.html")), key=os.path.getmtime, reverse=True)
    posted      = load_posted_log()
    total_pages = len(html_files)
    remaining   = total_pages - len(posted)

    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"=== BJJ Wiki X Auto Post v2 ({mode}) ===")
    print(f"Total: {total_pages} | Posted: {len(posted)} ({len(posted)*100//max(total_pages,1)}%) | Remaining: {remaining}")
    if remaining > 0:
        days_to_complete = (remaining + limit - 1) // limit
        print(f"Completion ETA: ~{days_to_complete} days ({limit}/run)")
    print()

    count = 0
    newly_posted = []
    skipped_no_meta = 0

    for filepath in html_files:
        if count >= limit:
            break

        slug = os.path.basename(filepath).replace(".html", "")
        if slug in posted:
            continue

        meta = extract_page_meta(filepath)
        if not meta:
            skipped_no_meta += 1
            continue

        page_url = f"{SITE_BASE_URL}/en/{slug}.html"
        category = detect_category(slug, meta["title"])
        tweet    = build_tweet(slug, meta["title"], meta["description"], page_url)

        print(f"  [{category}] {slug}")
        try:
            result = post_tweet(tweet, dry_run=dry_run)
        except RuntimeError as e:
            error_msg = str(e)
            print(f"  FAIL: {error_msg}")
            if not dry_run:
                send_telegram(f"X post failed: {error_msg}")
            sys.exit(1)

        count += 1
        newly_posted.append(slug)
        posted.add(slug)
        print(f"  OK ({count}/{limit}): {tweet[:80]}...")
        if not dry_run:
            time.sleep(2)

    if not dry_run:
        save_posted_log(posted)

    print(f"\n=== Done: {count} tweets ===")
    if skipped_no_meta > 0:
        print(f"  (Skipped {skipped_no_meta} pages with no meta)")
    new_remaining = total_pages - len(posted)
    print(f"  Remaining: {new_remaining}/{total_pages}")

    if count > 0 and not dry_run:
        progress_pct = len(posted) * 100 // max(total_pages, 1)
        send_telegram(
            f"X: {count} tweets posted\n"
            f"Progress: {len(posted)}/{total_pages} ({progress_pct}%)\n"
            + "\n".join(f"  {s}" for s in newly_posted)
        )


if __name__ == "__main__":
    main()
