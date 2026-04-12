#!/usr/bin/env python3
"""
BJJ Wiki → Pinterest 自動投稿スクリプト
- BJJページからランダムに選んでPinterestにピン投稿
- 1日1-3回程度の運用を想定
"""
import requests
import random
import json
import os
from datetime import datetime

try:
    from config import ACCESS_TOKEN, BASE_URL
except ImportError:
    ACCESS_TOKEN = os.environ.get("PINTEREST_TOKEN", "")
    BASE_URL = "https://wiki.bjj-app.net"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# BJJ Wiki ページリスト（カテゴリ別）
PAGES = [
    # テクニック系
    {"slug": "en/bjj-armbar-guide", "title": "BJJ Armbar Guide — Master the Most Effective Submission", "desc": "Complete guide to the armbar — setup, finish, and defense from every position."},
    {"slug": "en/bjj-rear-naked-choke", "title": "Rear Naked Choke — The Ultimate Finishing Move", "desc": "How to apply the RNC with perfect mechanics. The most submitted technique in BJJ and MMA."},
    {"slug": "en/bjj-triangle-choke-guide", "title": "Triangle Choke Setup & Finish Guide", "desc": "Master the triangle from guard — angles, hip position, and finishing details."},
    {"slug": "en/bjj-guard-passing-fundamentals", "title": "BJJ Guard Passing Fundamentals", "desc": "Break down every guard with proven passing techniques for gi and no-gi."},
    {"slug": "en/bjj-mount-system", "title": "BJJ Mount System — Control and Attack", "desc": "Dominate from mount position with proven control and submission sequences."},
    {"slug": "en/bjj-heel-hook-entry-guide", "title": "Heel Hook Entry Guide for BJJ", "desc": "Safe and effective heel hook entries from common leg entanglement positions."},
    {"slug": "en/bjj-kimura-trap-guide", "title": "The Kimura Trap System", "desc": "Use the kimura as a control system to attack from guard, top, and back."},
    {"slug": "en/bjj-butterfly-guard-attacks", "title": "Butterfly Guard Attacks & Sweeps", "desc": "Dominate from butterfly guard with hooks, sweeps, and back takes."},
    {"slug": "en/bjj-de-la-riva-guard", "title": "De La Riva Guard — Complete Guide", "desc": "Master DLR guard entries, sweeps, and back takes for modern open guard BJJ."},
    {"slug": "en/bjj-back-control-system", "title": "Back Control System in BJJ", "desc": "Take the back and stay there — hooks, seat belt, and finishing sequences."},
    # 初心者系
    {"slug": "en/bjj-beginners-guide", "title": "BJJ Beginner's Complete Guide", "desc": "Everything you need to start Brazilian Jiu-Jitsu — positions, submissions, and first steps."},
    {"slug": "en/bjj-belt-system", "title": "BJJ Belt System Explained", "desc": "From white to black belt — what each rank means and how long it takes."},
    {"slug": "en/bjj-positions-guide", "title": "BJJ Positions Guide — All Positions Explained", "desc": "Learn every position in Brazilian Jiu-Jitsu with clear explanations and strategies."},
]

# 投稿用画像URL（BJJ Wikiのカバー画像）
DEFAULT_IMAGE = "https://wiki.bjj-app.net/og-image.png"


def get_boards():
    """ボード一覧を取得"""
    r = requests.get("https://api.pinterest.com/v5/boards", headers=HEADERS)
    if r.status_code == 200:
        return r.json().get("items", [])
    print(f"[ERROR] Boards: {r.status_code} {r.text}")
    return []


def create_pin(board_id, page):
    """ピンを作成"""
    url_full = f"{BASE_URL}/{page['slug']}.html"
    payload = {
        "board_id": board_id,
        "title": page["title"],
        "description": f"{page['desc']}\n\n🥋 Learn more at BJJ Wiki → {url_full}",
        "link": url_full,
        "media_source": {
            "source_type": "image_url",
            "url": DEFAULT_IMAGE
        }
    }
    r = requests.post("https://api.pinterest.com/v5/pins", headers=HEADERS, json=payload)
    if r.status_code == 201:
        pin = r.json()
        print(f"[OK] Pin created: {pin.get('id')} — {page['title'][:50]}")
        return pin
    else:
        print(f"[ERROR] Pin failed: {r.status_code} {r.text}")
        return None


def main(count=3):
    print(f"\n=== BJJ Wiki Pinterest Auto Poster ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # ボード取得
    boards = get_boards()
    if not boards:
        print("[ERROR] No boards found. Create a board on Pinterest first!")
        return

    print(f"Found {len(boards)} board(s):")
    for b in boards:
        print(f"  - {b['name']} (ID: {b['id']})")

    # 最初のボードを使用
    board_id = boards[0]["id"]
    board_name = boards[0]["name"]
    print(f"\nPosting to: {board_name}\n")

    # ランダムにページを選んで投稿
    selected = random.sample(PAGES, min(count, len(PAGES)))
    for page in selected:
        create_pin(board_id, page)

    print(f"\n✅ Done! {len(selected)} pins posted.")


if __name__ == "__main__":
    main(count=3)
