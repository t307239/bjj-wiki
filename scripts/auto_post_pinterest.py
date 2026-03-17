#!/usr/bin/env python3
"""
BJJ Wiki -> Pinterest Auto Post Script
Scans /en/ HTML pages, extracts title/description, posts to Pinterest API v5
Tracks posted pages in already_posted_pinterest.txt
"""
import os, json, re, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

def send_telegram(msg):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id: return
    try:
        payload = json.dumps({"chat_id": chat_id, "text": msg}).encode()
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload, headers={"Content-Type": "application/json"}, method="POST")
        urllib.request.urlopen(req, timeout=10)
    except: pass

def post_to_pinterest(title, description, link, board_id):
    access_token = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
    if not access_token:
        print("[WARN] PINTEREST_ACCESS_TOKEN not set.")
        return False
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {
        "board_id": board_id,
        "title": title[:100],
        "description": description[:500],
        "link": link,
        "media_source": {"source_type": "image_url", "url": "https://t307239.github.io/bjj-wiki/og-image.svg"},
        "alt_text": title + " - BJJ technique guide"
    }
    try:
        req = urllib.request.Request("https://api.pinterest.com/v5/pins",
            data=json.dumps(payload).encode(), headers=headers, method="POST")
        result = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
        print(f"[OK] Pin: {result.get('id')} - {title[:50]}")
        return True
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Pinterest {e.code}: {e.read().decode()}")
        return False
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

def extract_title_and_desc(html):
    t = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    title = t.group(1).replace(" | BJJ Wiki", "").strip() if t else "Untitled"
    d = re.search(r'<meta name="description" content="([^"]*)"', html)
    desc = d.group(1) if d else ""
    if not desc:
        p = re.search(r'<p>(.*?)</p>', html, re.DOTALL)
        if p: desc = re.sub(r'<[^>]+>', '', p.group(1)).strip()[:200]
    return title, desc

def load_posted_slugs():
    f = Path(__file__).parent / "already_posted_pinterest.txt"
    return set(line.strip() for line in f.read_text(encoding="utf-8").splitlines() if line.strip()) if f.exists() else set()

def save_posted_slug(slug):
    f = Path(__file__).parent / "already_posted_pinterest.txt"
    with open(f, "a", encoding="utf-8") as fp: fp.write(slug + "\n")

def main():
    print(f"=== BJJ Wiki Pinterest Auto Poster === {datetime.now()}")
    access_token = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
    board_id = os.environ.get("PINTEREST_BOARD_ID", "")
    en_dir = Path(__file__).parent.parent / "en"
    if not en_dir.exists():
        print(f"[ERROR] {en_dir} not found"); return
    html_files = sorted(en_dir.glob("*.html"), key=lambda f: f.stat().st_mtime, reverse=True)
    posted_slugs = load_posted_slugs()
    print(f"Files: {len(html_files)}, Already posted: {len(posted_slugs)}")
    posted_count = 0
    for html_file in html_files:
        if posted_count >= 5: break
        slug = html_file.stem
        if slug in ("index", "about", "contact", "404"): continue
        if slug in posted_slugs: continue
        try: html = html_file.read_text(encoding="utf-8")
        except: continue
        title, desc = extract_title_and_desc(html)
        if not title or not desc: continue
        url = f"https://t307239.github.io/bjj-wiki/en/{slug}.html"
        print(f"[POST] {slug}: {title[:60]}")
        if access_token and board_id:
            if post_to_pinterest(title, desc, url, board_id):
                save_posted_slug(slug); posted_count += 1
        else:
            print(f"[DRY-RUN] {title}")
            save_posted_slug(slug); posted_count += 1
    print(f"Done: {posted_count} pins posted.")
    send_telegram(f"📌 Pinterest: {posted_count}件投稿 ({datetime.now().strftime('%m/%d %H:%M')})")

if __name__ == "__main__":
    main()
