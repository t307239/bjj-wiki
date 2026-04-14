#!/usr/bin/env python3
"""
BJJ Wiki -> Pinterest Auto Post Script (OAuth Refresh Token方式)

【認証フロー】
  1. 初回のみ: pinterest_oauth_setup.py を実行して refresh_token を取得
  2. GitHub Secrets に PINTEREST_APP_ID / PINTEREST_APP_SECRET / PINTEREST_REFRESH_TOKEN を設定
  3. 毎回実行時に refresh_token → 新 access_token を自動取得（30日有効、毎回更新）
  4. refresh_token は365日有効。期限切れ時は pinterest_oauth_setup.py を再実行

【フォールバック】
  PINTEREST_REFRESH_TOKEN 未設定時は従来の PINTEREST_ACCESS_TOKEN を使用（後方互換）
"""
import os, json, re, sys, urllib.request, urllib.error, base64
from datetime import datetime
from pathlib import Path

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
    """Pinterest認証失敗 — トークン期限切れの可能性"""
    pass

# ── OAuth Token Refresh ──
def refresh_access_token(app_id, app_secret, refresh_token):
    """
    Pinterest API v5: refresh_token → 新 access_token を取得
    POST https://api.pinterest.com/v5/oauth/token
    Authorization: Basic base64(app_id:app_secret)
    Body: grant_type=refresh_token&refresh_token=XXX
    """
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
            new_access_token = data.get("access_token", "")
            token_type = data.get("token_type", "bearer")
            expires_in = data.get("expires_in", 0)
            print(f"[AUTH] Token refreshed successfully (expires_in: {expires_in}s, type: {token_type})")
            return new_access_token
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        print(f"[AUTH ERROR] Pinterest token refresh failed: HTTP {e.code}: {body_text}")
        if e.code == 401:
            raise AuthFailure(f"Refresh token expired or invalid: {body_text}")
        return ""
    except Exception as e:
        print(f"[AUTH ERROR] Token refresh failed: {e}")
        return ""

def get_access_token():
    """
    アクセストークン取得の優先順位:
    1. PINTEREST_REFRESH_TOKEN + APP_ID + APP_SECRET → OAuth refresh で新トークン取得
    2. PINTEREST_ACCESS_TOKEN → 従来方式（後方互換、24h限定）
    """
    refresh_token = os.environ.get("PINTEREST_REFRESH_TOKEN", "")
    app_id = os.environ.get("PINTEREST_APP_ID", "")
    app_secret = os.environ.get("PINTEREST_APP_SECRET", "")

    if refresh_token and app_id and app_secret:
        print("[AUTH] Using OAuth refresh token flow")
        token = refresh_access_token(app_id, app_secret, refresh_token)
        if token:
            return token
        print("[AUTH] Refresh failed, checking fallback...")

    # フォールバック: 従来方式
    legacy_token = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
    if legacy_token:
        print("[AUTH] Using legacy PINTEREST_ACCESS_TOKEN (24h限定)")
        return legacy_token

    return ""

# ── Pinterest API ──
def post_to_pinterest(title, description, link, board_id, access_token):
    if not access_token:
        print("[WARN] No access token available.")
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
            "url": "https://wiki.bjj-app.net/og-image.png",
        },
        "alt_text": title + " - BJJ technique guide",
    }
    try:
        req = urllib.request.Request(
            "https://api.pinterest.com/v5/pins",
            data=json.dumps(payload).encode(), headers=headers, method="POST"
        )
        result = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
        print(f"[OK] Pin: {result.get('id')} - {title[:50]}")
        return True
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        print(f"[ERROR] Pinterest {e.code}: {body_text}")
        if e.code == 401:
            raise AuthFailure(f"Pinterest 401: {body_text}")
        return False
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

# ── HTML解析 ──
def extract_title_and_desc(html):
    t = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    title = t.group(1).replace(" | BJJ Wiki", "").strip() if t else "Untitled"
    d = re.search(r'<meta name="description" content="([^"]*)"', html)
    desc = d.group(1) if d else ""
    if not desc:
        p = re.search(r'<p>(.*?)</p>', html, re.DOTALL)
        if p:
            desc = re.sub(r'<[^>]+>', '', p.group(1)).strip()[:200]
    return title, desc

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
    print(f"=== BJJ Wiki Pinterest Auto Poster (OAuth) === {datetime.now()}")

    # トークン取得（OAuth refresh → レガシーフォールバック）
    access_token = get_access_token()
    board_id = os.environ.get("PINTEREST_BOARD_ID", "")

    if not access_token:
        msg = "Pinterest: アクセストークン取得失敗。PINTEREST_REFRESH_TOKEN + APP_ID + APP_SECRET を確認してください"
        print(f"[FATAL] {msg}")
        send_telegram(f"🚨 {msg}")
        sys.exit(1)

    if not board_id:
        print("[FATAL] PINTEREST_BOARD_ID not set.")
        sys.exit(1)

    en_dir = Path(__file__).parent.parent / "en"
    if not en_dir.exists():
        print(f"[ERROR] {en_dir} not found")
        return

    html_files = sorted(en_dir.glob("*.html"), key=lambda f: f.stat().st_mtime, reverse=True)
    posted_slugs = load_posted_slugs()
    skip_slugs = {"index", "about", "contact", "404"}
    remaining = len([f for f in html_files if f.stem not in posted_slugs and f.stem not in skip_slugs])
    print(f"Files: {len(html_files)}, Already posted: {len(posted_slugs)}, Remaining: {remaining}")

    posted_count = 0
    error_count = 0

    for html_file in html_files:
        if posted_count >= 5:
            break
        slug = html_file.stem
        if slug in skip_slugs:
            continue
        if slug in posted_slugs:
            continue

        try:
            html = html_file.read_text(encoding="utf-8")
        except Exception:
            continue

        title, desc = extract_title_and_desc(html)
        if not title or not desc:
            continue

        url = f"https://wiki.bjj-app.net/en/{slug}.html"
        print(f"[POST] {slug}: {title[:60]}")

        try:
            if post_to_pinterest(title, desc, url, board_id, access_token):
                save_posted_slug(slug)
                posted_count += 1
                error_count = 0
            else:
                error_count += 1
        except AuthFailure as e:
            print(f"[FATAL] 認証失敗: {e}")
            send_telegram(
                f"🚨 Pinterest認証失敗！refresh_tokenが期限切れの可能性\n"
                f"pinterest_oauth_setup.py を再実行してください\n"
                f"({datetime.now().strftime('%m/%d %H:%M')})"
            )
            sys.exit(1)

        if error_count >= 3:
            print("[WARN] 連続3件失敗 — 中断します")
            send_telegram(f"⚠️ Pinterest連続エラー3件で中断 ({datetime.now().strftime('%m/%d %H:%M')})")
            break

    print(f"Done: {posted_count} pins posted, {remaining - posted_count} remaining.")
    if posted_count > 0:
        send_telegram(f"📌 Pinterest: {posted_count}件投稿 (残{remaining - posted_count}件) ({datetime.now().strftime('%m/%d %H:%M')})")
    elif error_count == 0 and remaining == 0:
        send_telegram(f"✅ Pinterest: 全ページ投稿完了！ ({datetime.now().strftime('%m/%d %H:%M')})")

if __name__ == "__main__":
    main()
