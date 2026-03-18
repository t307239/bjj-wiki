#!/usr/bin/env python3
"""
BJJ Wiki → Pinterest 自動投稿スクリプト
- /en/ ディレクトリの最新HTMLページをスキャン
- titleとdescriptionを抽出
- already_posted_pinterest.txt で重複投稿を防止
- Pinterest API v5で最大5件投稿
- Telegram通知で結果を報告
"""

import os
import json
import re
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path


# ===== Telegram通知関数 =====
def send_telegram(msg: str) -> None:
    """GitHub Actions の TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID を使って通知"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        payload = json.dumps({"chat_id": chat_id, "text": msg}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass  # 通知失敗は無視してビルドを継続


# ===== Pinterest API関数 =====
def post_to_pinterest(title: str, description: str, link: str, board_id: str) -> bool:
    """Pinterest API v5でピンを作成"""
    access_token = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
    if not access_token:
        print("[WARN] PINTEREST_ACCESS_TOKEN not set. Skipping actual post.")
        return False

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "board_id": board_id,
        "title": title[:100],  # Pinterestは最大100文字
        "description": description[:500],  # 説明は最大500文字
        "link": link,
        "media_source": {
            "source_type": "image_url",
            "url": "https://t307239.github.io/bjj-wiki/og-image.svg"
        },
        "alt_text": title + " - BJJ technique guide"
    }

    try:
        req = urllib.request.Request(
            "https://api.pinterest.com/v5/pins",
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST",
        )
        response = urllib.request.urlopen(req, timeout=15)
        result = json.loads(response.read().decode())
        print(f"[OK] Pin created: {result.get('id')} — {title[:50]}")
        return True
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()
        print(f"[ERROR] Pinterest API: {e.code} — {error_msg}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to post: {str(e)}")
        return False


# ===== HTMLパース関数 =====
def extract_title_and_desc(html_content: str) -> tuple:
    """HTMLから<title>と最初の<p>を抽出"""
    # <title>タグを抽出
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL)
    title = title_match.group(1) if title_match else "Untitled"
    # ' | BJJ Wiki' を削除
    title = title.replace(" | BJJ Wiki", "").strip()

    # <meta name="description">を抽出（titleが長い場合の代替）
    desc_match = re.search(r'<meta name="description" content="([^"]*)"', html_content)
    description = desc_match.group(1) if desc_match else ""

    # 最初の<p>タグを抽出（説明が無い場合の代替）
    if not description:
        p_match = re.search(r'<p>(.*?)</p>', html_content, re.DOTALL)
        if p_match:
            description = p_match.group(1)
            # HTMLタグを削除
            description = re.sub(r'<[^>]+>', '', description)
            description = description.strip()[:200]

    return title, description


# ===== 投稿済み管理 =====
def load_posted_slugs() -> set:
    """already_posted_pinterest.txt から投稿済みのslugセットを読み込む"""
    script_dir = Path(__file__).parent
    posted_file = script_dir / "already_posted_pinterest.txt"
    if posted_file.exists():
        with open(posted_file, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_posted_slug(slug: str) -> None:
    """投稿済みのslugをファイルに追記"""
    script_dir = Path(__file__).parent
    posted_file = script_dir / "already_posted_pinterest.txt"
    with open(posted_file, "a", encoding="utf-8") as f:
        f.write(slug + "\n")


# ===== メイン処理 =====
def main():
    """メイン処理"""
    print("\n=== BJJ Wiki Pinterest Auto Poster ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Pinterest設定
    access_token = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
    board_id = os.environ.get("PINTEREST_BOARD_ID", "")

    if not access_token or not board_id:
        print("[WARN] PINTEREST_ACCESS_TOKEN or PINTEREST_BOARD_ID not set.")
        print("[INFO] Running in dry-run mode (will not post).")

    # /en/ ディレクトリからHTMLファイルを取得
    en_dir = Path(__file__).parent.parent / "en"
    if not en_dir.exists():
        print(f"[ERROR] Directory not found: {en_dir}")
        return

    # HTMLファイルをリスト化（修正時刻でソート、最新順）
    html_files = sorted(
        en_dir.glob("*.html"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    if not html_files:
        print("[WARN] No HTML files found.")
        return

    print(f"Found {len(html_files)} HTML files in {en_dir}\n")

    # 投稿済みslugを読み込む
    posted_slugs = load_posted_slugs()
    print(f"Already posted: {len(posted_slugs)} pages")

    # 最新ファイルから順に処理（最大5件）
    posted_count = 0
    max_posts = 5

    for html_file in html_files:
        if posted_count >= max_posts:
            break

        slug = html_file.stem  # ファイル名（拡張子なし）

        # 特殊ページはスキップ
        if slug in ("index", "about", "contact", "404"):
            continue

        # 投稿済みならスキップ
        if slug in posted_slugs:
            print(f"[SKIP] Already posted: {slug}")
            continue

        # HTMLを読み込む
        try:
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()
        except Exception as e:
            print(f"[ERROR] Failed to read {html_file}: {str(e)}")
            continue

        # titleとdescriptionを抽出
        title, description = extract_title_and_desc(html_content)

        if not title or not description:
            print(f"[SKIP] Missing title or description: {slug}")
            continue

        # ページURL
        page_url = f"https://t307239.github.io/bjj-wiki/en/{slug}.html"

        print(f"\n[INFO] Processing: {slug}")
        print(f"  Title: {title}")
        print(f"  Desc: {description[:80]}...")
        print(f"  URL: {page_url}")

        # Pinterestに投稿
        if access_token and board_id:
            success = post_to_pinterest(title, description, page_url, board_id)
            if success:
                save_posted_slug(slug)
                posted_count += 1
        else:
            # Dry-run mode
            print(f"[DRY-RUN] Would post: {title}")
            save_posted_slug(slug)
            posted_count += 1

    # 結果を表示・通知
    print(f"\n✅ Done! {posted_count} pins posted.")

    msg = f"📌 BJJ Wiki Pinterest: {posted_count} ピン投稿 ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
    if posted_count > 0:
        msg += f"\n投稿済み: {posted_count}件\n総投稿数: {len(posted_slugs) + posted_count}件"
    else:
        msg = f"📌 BJJ Wiki Pinterest: 新規投稿なし ({datetime.now().strftime('%Y-%m-%d %H:%M')})"

    send_telegram(msg)


if __name__ == "__main__":
    main()
