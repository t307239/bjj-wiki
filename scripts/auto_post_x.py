#!/usr/bin/env python3
"""
auto_post_x.py
==============
BJJ Wiki の新着ページを X (Twitter) に自動投稿するスクリプト。

必要な環境変数（GitHub Secrets に設定）:
  X_API_KEY             — Twitter API Key (Consumer Key)
  X_API_SECRET          — Twitter API Key Secret (Consumer Secret)
  X_ACCESS_TOKEN        — Access Token
  X_ACCESS_TOKEN_SECRET — Access Token Secret
  TELEGRAM_BOT_TOKEN    — Telegram 通知用（任意）
  TELEGRAM_CHAT_ID      — Telegram チャットID（任意）

Twitter Developer Portal での設定:
  1. https://developer.twitter.com/en/portal/dashboard でアプリ作成
  2. App permissions: Read and Write
  3. Generate Access Token and Secret（User認証済み）
  4. 上記4つの値を GitHub Secrets に設定

使い方:
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
from datetime import datetime, timezone


# ────────────────────────────────────────────
#  設定
# ────────────────────────────────────────────
SITE_BASE_URL = "https://wiki.bjj-app.net"
POSTED_LOG    = os.path.join(os.path.dirname(os.path.dirname(__file__)), "already_posted_x.txt")
MAX_TWEET_LEN = 280
DEFAULT_LIMIT = 1  # 1回の実行で最大投稿数（1日1回実行 × 1件 = 1件/日）

# ハッシュタグ（スペースを考慮してコンパクトに）
HASHTAGS = "#BJJ #BrazilianJiuJitsu #柔術"


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

    # パラメータを結合してソート
    all_params = {**params, **oauth_params}
    sorted_params = "&".join(
        f"{_percent_encode(k)}={_percent_encode(v)}"
        for k, v in sorted(all_params.items())
    )

    # 署名ベース文字列
    base_string = "&".join([
        method.upper(),
        _percent_encode(url),
        _percent_encode(sorted_params),
    ])

    # 署名キー
    signing_key = f"{_percent_encode(api_secret)}&{_percent_encode(access_token_secret)}"

    # HMAC-SHA1
    signature = base64.b64encode(
        hmac.new(
            signing_key.encode("utf-8"),
            base_string.encode("utf-8"),
            hashlib.sha1,
        ).digest()
    ).decode()
    oauth_params["oauth_signature"] = signature

    # Authorization ヘッダー
    header_parts = ", ".join(
        f'{_percent_encode(k)}="{_percent_encode(v)}"'
        for k, v in sorted(oauth_params.items())
    )
    return f"OAuth {header_parts}"


def post_tweet(text: str, dry_run: bool = False) -> dict | None:
    """X API v2 でツイートを投稿する。失敗時は例外を送出する。"""
    if dry_run:
        print(f"  [DRY RUN] Would tweet ({len(text)} chars):")
        print(f"  {text!r}")
        return {"id": "dry_run", "text": text}

    api_key             = os.environ.get("X_API_KEY", "")
    api_secret          = os.environ.get("X_API_SECRET", "")
    access_token        = os.environ.get("X_ACCESS_TOKEN", "")
    access_token_secret = os.environ.get("X_ACCESS_TOKEN_SECRET", "")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        raise RuntimeError("X API credentials not set (X_API_KEY / X_API_SECRET / X_ACCESS_TOKEN / X_ACCESS_TOKEN_SECRET)")

    url     = "https://api.twitter.com/2/tweets"
    payload = json.dumps({"text": text}).encode("utf-8")
    auth    = _build_oauth_header("POST", url, {}, api_key, api_secret, access_token, access_token_secret)

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", auth)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            return result.get("data", result)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"Twitter API error {e.code}: {body}")


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
    desc  = desc_m.group(1).strip()[:100] if desc_m else ""

    return {"title": title, "description": desc}


def build_tweet(title: str, description: str, url: str) -> str:
    """280文字以内のツイート文を生成"""
    # タイトルから余分な情報を削除
    clean_title = re.sub(r"\s*[-|].*$", "", title).strip()

    # ツイートを構築（タイトル + 短い説明 + URL + ハッシュタグ）
    url_len  = len(url) + 1           # URL + space
    tags_len = len(HASHTAGS) + 1      # hashtags + space
    max_text = MAX_TWEET_LEN - url_len - tags_len - 2  # 2 for newlines

    title_trunc = clean_title[:80] if len(clean_title) > 80 else clean_title
    desc_trunc  = description[:max(0, max_text - len(title_trunc) - 5)] if description else ""

    if desc_trunc:
        body = f"{title_trunc}\n{desc_trunc}..."
    else:
        body = title_trunc

    return f"{body}\n{url} {HASHTAGS}"


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

    mode = "DRY RUN" if dry_run else "実行"
    print(f"=== BJJ Wiki X(Twitter)自動投稿 ({mode}) ===")
    print(f"総ページ数: {total_pages}件")
    print(f"投稿済み:   {len(posted)}件 ({len(posted)*100//max(total_pages,1)}%)")
    print(f"未投稿:     {remaining}件")
    print(f"今回投稿上限: {limit}件")
    if remaining > 0:
        days_to_complete = (remaining + limit - 1) // limit  # 1回/日想定
        print(f"完了まで約: {days_to_complete}日（1日{limit}件ペース）")
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
        tweet    = build_tweet(meta["title"], meta["description"], page_url)

        print(f"  📝 {slug}")
        try:
            result = post_tweet(tweet, dry_run=dry_run)
        except RuntimeError as e:
            error_msg = str(e)
            print(f"  ❌ {error_msg}")
            if not dry_run:
                send_telegram(f"❌ BJJ Wiki X投稿失敗\n{error_msg}\n\n対処: Twitter Developer Portal でAccessTokenを再生成し、GitHub Secretsを更新してください")
            sys.exit(1)

        count += 1
        newly_posted.append(slug)
        posted.add(slug)
        print(f"  ✅ posted ({count}/{limit}): {tweet[:70]}...")
        if not dry_run:
            time.sleep(2)  # Rate limit対策

    if not dry_run:
        save_posted_log(posted)

    print()
    print(f"=== 完了: {count}件投稿 ===")
    if skipped_no_meta > 0:
        print(f"  (メタ情報なし {skipped_no_meta}件スキップ)")
    new_remaining = total_pages - len(posted)
    print(f"  残り未投稿: {new_remaining}件 / 全{total_pages}件")

    if count > 0 and not dry_run:
        progress_pct = len(posted) * 100 // max(total_pages, 1)
        send_telegram(
            f"🐦 BJJ Wiki → X に{count}件投稿\n"
            f"進捗: {len(posted)}/{total_pages}件 ({progress_pct}%)\n"
            + "\n".join(f"  • {s}" for s in newly_posted)
        )


if __name__ == "__main__":
    main()
