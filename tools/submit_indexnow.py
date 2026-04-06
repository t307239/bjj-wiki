#!/usr/bin/env python3
"""
submit_indexnow.py — IndexNow API への URL 一括送信スクリプト
wiki.bjj-app.net の sitemap.xml を読み込み、
Bing/Yandex 対応の IndexNow エンドポイントへ POST する。

使用方法:
    python tools/submit_indexnow.py
    python tools/submit_indexnow.py --dry-run    # 送信せず URL 件数のみ表示
    python tools/submit_indexnow.py --limit 500  # 最初の 500 URL のみ送信

環境変数:
    INDEXNOW_KEY  — IndexNow APIキー (例: 5197ea3b13c8e7a9cebdae996368322e)
                    未設定の場合はデフォルトキー使用
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# ── 設定 ─────────────────────────────────────────────────────────────────────
HOST = "wiki.bjj-app.net"
SITEMAP_URL = f"https://{HOST}/sitemap.xml"
INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY", "5197ea3b13c8e7a9cebdae996368322e")
KEY_LOCATION = f"https://{HOST}/{INDEXNOW_KEY}.txt"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/IndexNow"  # 全エンジン対応アグリゲーター
BATCH_SIZE = 10_000  # IndexNow API の 1 リクエストあたり最大 URL 数
RATE_LIMIT_DELAY = 1.0  # バッチ間の待機秒数（レートリミット対策）


def fetch_sitemap_urls(sitemap_url: str) -> list[str]:
    """sitemap.xml から全 URL を取得して返す。"""
    print(f"📡 Fetching sitemap: {sitemap_url}", flush=True)
    try:
        with urllib.request.urlopen(sitemap_url, timeout=30) as resp:
            xml_data = resp.read()
    except Exception as e:
        print(f"❌ Failed to fetch sitemap: {e}", file=sys.stderr)
        sys.exit(1)

    # Namespace-aware parse
    root = ET.fromstring(xml_data)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    # Handle sitemap index (nested sitemaps) or regular sitemap
    urls: list[str] = []

    # Try sitemap index first
    sitemaps = root.findall("sm:sitemap/sm:loc", ns)
    if sitemaps:
        print(f"  Found sitemap index with {len(sitemaps)} sub-sitemaps", flush=True)
        for sitemap_loc in sitemaps:
            sub_url = sitemap_loc.text.strip()
            print(f"  Fetching sub-sitemap: {sub_url}", flush=True)
            try:
                with urllib.request.urlopen(sub_url, timeout=30) as resp:
                    sub_xml = resp.read()
                sub_root = ET.fromstring(sub_xml)
                for loc in sub_root.findall("sm:url/sm:loc", ns):
                    urls.append(loc.text.strip())
            except Exception as e:
                print(f"  ⚠️ Failed to fetch {sub_url}: {e}", file=sys.stderr)
    else:
        # Regular sitemap
        for loc in root.findall("sm:url/sm:loc", ns):
            urls.append(loc.text.strip())

    return urls


def submit_batch(urls: list[str], dry_run: bool = False) -> bool:
    """URL バッチを IndexNow API に POST する。成功で True を返す。"""
    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    if dry_run:
        print(f"  [DRY-RUN] Would POST {len(urls)} URLs to {INDEXNOW_ENDPOINT}")
        return True

    req = urllib.request.Request(
        INDEXNOW_ENDPOINT,
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "BJJ-Wiki-IndexNow/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            if status in (200, 202):
                print(f"  ✅ Accepted: {len(urls)} URLs (HTTP {status})")
                return True
            else:
                print(f"  ⚠️ Unexpected status {status} for {len(urls)} URLs", file=sys.stderr)
                return False
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        print(f"  ❌ HTTP {e.code}: {body_text[:200]}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  ❌ Request failed: {e}", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Submit wiki URLs to IndexNow API")
    parser.add_argument("--dry-run", action="store_true", help="Print URL count without sending")
    parser.add_argument("--limit", type=int, default=0, help="Submit only the first N URLs (0=all)")
    parser.add_argument("--sitemap", default=SITEMAP_URL, help="Sitemap URL to parse")
    args = parser.parse_args()

    urls = fetch_sitemap_urls(args.sitemap)
    print(f"🗺  Total URLs found: {len(urls)}", flush=True)

    if args.limit > 0:
        urls = urls[: args.limit]
        print(f"🔢 Limiting to first {len(urls)} URLs", flush=True)

    if not urls:
        print("No URLs to submit. Exiting.", flush=True)
        return

    # Split into batches
    batches = [urls[i : i + BATCH_SIZE] for i in range(0, len(urls), BATCH_SIZE)]
    print(f"📦 Submitting {len(urls)} URLs in {len(batches)} batch(es)…", flush=True)

    success_count = 0
    for i, batch in enumerate(batches, 1):
        print(f"\n🚀 Batch {i}/{len(batches)} ({len(batch)} URLs):", flush=True)
        ok = submit_batch(batch, dry_run=args.dry_run)
        if ok:
            success_count += len(batch)
        if i < len(batches):
            time.sleep(RATE_LIMIT_DELAY)

    print(f"\n🎉 Done! {success_count}/{len(urls)} URLs submitted to IndexNow.")
    if not args.dry_run:
        print(f"   Key: {INDEXNOW_KEY}")
        print(f"   Key file must be accessible at: {KEY_LOCATION}")


if __name__ == "__main__":
    main()
