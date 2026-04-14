#!/usr/bin/env python3
"""
Pinterest OAuth 2.0 初回セットアップスクリプト

【使い方】
  1. Pinterest Developer Console (https://developers.pinterest.com/apps/) でアプリを作成
  2. Redirect URI に http://localhost:9876/callback を追加
  3. このスクリプトを実行:
     python3 scripts/pinterest_oauth_setup.py --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET
  4. ブラウザが開くので Pinterest にログインして認可
  5. refresh_token が表示されるので GitHub Secrets に保存:
     - PINTEREST_APP_ID
     - PINTEREST_APP_SECRET
     - PINTEREST_REFRESH_TOKEN

【必要なスコープ】
  pins:read, pins:write, boards:read, boards:write, user_accounts:read
"""
import argparse, base64, json, os, sys, threading, urllib.parse, urllib.request, urllib.error, webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

# ── 設定 ──
REDIRECT_URI = "http://localhost:9876/callback"
SCOPES = "pins:read,pins:write,boards:read,boards:write,user_accounts:read"
TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"

# グローバル変数で認可コードを受け取る
auth_code = None
server_should_stop = threading.Event()


class CallbackHandler(BaseHTTPRequestHandler):
    """OAuth コールバック受信用ローカルサーバー"""

    def do_GET(self):
        global auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>OK!</h1>"
                b"<p>Pinterest OAuth authorization successful. You can close this tab.</p>"
                b"<p>Pinterest OAuth \xe8\xaa\x8d\xe5\x8f\xaf\xe6\x88\x90\xe5\x8a\x9f\xe3\x80\x82\xe3\x81\x93\xe3\x81\xae\xe3\x82\xbf\xe3\x83\x96\xe3\x82\x92\xe9\x96\x89\xe3\x81\x98\xe3\x81\xa6\xe3\x81\x8f\xe3\x81\xa0\xe3\x81\x95\xe3\x81\x84\xe3\x80\x82</p>"
                b"</body></html>"
            )
            server_should_stop.set()
        else:
            error = params.get("error", ["unknown"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Error: {error}</h1></body></html>".encode())
            server_should_stop.set()

    def log_message(self, format, *args):
        pass  # サーバーログを抑制


def exchange_code_for_tokens(app_id, app_secret, code):
    """認可コード → access_token + refresh_token"""
    credentials = base64.b64encode(f"{app_id}:{app_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }).encode()

    req = urllib.request.Request(TOKEN_URL, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.loads(res.read().decode())


def main():
    parser = argparse.ArgumentParser(description="Pinterest OAuth 2.0 Setup")
    parser.add_argument("--app-id", required=True, help="Pinterest App ID")
    parser.add_argument("--app-secret", required=True, help="Pinterest App Secret")
    parser.add_argument("--port", type=int, default=9876, help="Callback server port")
    args = parser.parse_args()

    # Step 1: 認可URL生成
    auth_params = urllib.parse.urlencode({
        "client_id": args.app_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "state": "bjj-wiki-setup",
    })
    auth_url = f"https://www.pinterest.com/oauth/?{auth_params}"

    print("=" * 60)
    print("Pinterest OAuth 2.0 Setup")
    print("=" * 60)
    print()
    print(f"1. Opening browser for Pinterest authorization...")
    print(f"   URL: {auth_url}")
    print()
    print(f"2. Waiting for callback on http://localhost:{args.port}/callback")
    print()

    # Step 2: ローカルサーバー起動 + ブラウザ起動
    server = HTTPServer(("localhost", args.port), CallbackHandler)
    server.timeout = 1

    webbrowser.open(auth_url)

    # コールバック待ち（最大5分）
    for _ in range(300):
        server.handle_request()
        if server_should_stop.is_set():
            break

    server.server_close()

    if not auth_code:
        print("[ERROR] Authorization code not received. Timed out or user denied access.")
        sys.exit(1)

    print(f"3. Authorization code received. Exchanging for tokens...")
    print()

    # Step 3: トークン交換
    try:
        tokens = exchange_code_for_tokens(args.app_id, args.app_secret, auth_code)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[ERROR] Token exchange failed: HTTP {e.code}: {body}")
        sys.exit(1)

    access_token = tokens.get("access_token", "")
    refresh_token = tokens.get("refresh_token", "")
    expires_in = tokens.get("expires_in", 0)
    scope = tokens.get("scope", "")

    if not refresh_token:
        print("[ERROR] No refresh_token in response!")
        print(f"Response: {json.dumps(tokens, indent=2)}")
        sys.exit(1)

    # Step 4: 結果表示
    print("=" * 60)
    print("SUCCESS! Tokens obtained.")
    print("=" * 60)
    print()
    print(f"  access_token:  {access_token[:20]}...{access_token[-10:]}")
    print(f"  refresh_token: {refresh_token[:20]}...{refresh_token[-10:]}")
    print(f"  expires_in:    {expires_in}s (~{expires_in // 86400} days)")
    print(f"  scope:         {scope}")
    print()
    print("=" * 60)
    print("NEXT STEPS: Add these to GitHub Secrets")
    print("=" * 60)
    print()
    print(f"  PINTEREST_APP_ID={args.app_id}")
    print(f"  PINTEREST_APP_SECRET={args.app_secret}")
    print(f"  PINTEREST_REFRESH_TOKEN={refresh_token}")
    print()
    print("GitHub Secrets URL:")
    print("  https://github.com/t307239/bjj-wiki/settings/secrets/actions")
    print()
    print("refresh_token is valid for ~365 days.")
    print("The auto_post_pinterest.py script will auto-refresh access_token each run.")


if __name__ == "__main__":
    main()
