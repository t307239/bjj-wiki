#!/usr/bin/env python3
"""
submit_indexnow.py — IndexNow API bulk URL submission for wiki.bjj-app.net

Parses sitemap.xml and submits all URLs to IndexNow API (Bing/Yandex).
Replaces github.io URLs with the canonical wiki.bjj-app.net domain.

Usage:
  python3 scripts/submit_indexnow.py [--dry-run] [--limit N]

Environment:
  INDEXNOW_KEY  — IndexNow API key (must match /fa79ec2d19ad4b1cae5db99a7d6e1f3b.txt)

API docs: https://www.indexnow.org/documentation
"""

import sys
import os
import json
import argparse
import re
import urllib.request
import urllib.error
from pathlib import Path
from xml.etree import ElementTree as ET

# ── Config ────────────────────────────────────────────────────────────────────

INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY", "fa79ec2d19ad4b1cae5db99a7d6e1f3b")
CANONICAL_HOST = "wiki.bjj-app.net"
CANONICAL_BASE = f"https://{CANONICAL_HOST}"
GITHUB_PAGES_BASE = "https://t307239.github.io/bjj-wiki"

# IndexNow allows max 10,000 URLs per request; use 9,000 to be safe
BATCH_SIZE = 9000

INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_sitemap(sitemap_path: str) -> list[str]:
    """Parse sitemap.xml and return all <loc> URLs as canonical wiki.bjj-app.net URLs."""
    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    urls = []
    for loc in root.findall(".//sm:loc", ns):
        url = (loc.text or "").strip()
        if not url:
            continue
        # Normalize to canonical domain
        url = url.replace(GITHUB_PAGES_BASE, CANONICAL_BASE)
        # Only include our domain
        if CANONICAL_HOST in url:
            urls.append(url)

    return urls


def submit_batch(urls: list[str], dry_run: bool = False) -> bool:
    """Submit a batch of URLs to IndexNow. Returns True on success."""
    payload = {
        "host": CANONICAL_HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{CANONICAL_BASE}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }

    if dry_run:
        print(f"[DRY RUN] Would submit {len(urls)} URLs to IndexNow")
        print(f"  First 3: {urls[:3]}")
        print(f"  Last 3:  {urls[-3:]}")
        return True

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        INDEXNOW_ENDPOINT,
        data=data,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "BJJ-Wiki-IndexNow/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            # IndexNow returns 200 (accepted) or 202 (queued) on success
            if status in (200, 202):
                print(f"  ✅ Submitted {len(urls)} URLs — HTTP {status}")
                return True
            else:
                print(f"  ⚠️  Unexpected HTTP {status}")
                return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  ❌ HTTP {e.code}: {body[:200]}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Submit wiki URLs to IndexNow API")
    parser.add_argument("--dry-run", action="store_true", help="Print URLs without submitting")
    parser.add_argument("--limit", type=int, default=0, help="Limit URL count (0 = all)")
    args = parser.parse_args()

    # Locate sitemap.xml relative to this script's parent
    wiki_root = Path(__file__).parent.parent
    sitemap_path = wiki_root / "sitemap.xml"

    if not sitemap_path.exists():
        print(f"❌ sitemap.xml not found at {sitemap_path}", file=sys.stderr)
        sys.exit(1)

    print(f"📄 Parsing sitemap: {sitemap_path}")
    urls = load_sitemap(str(sitemap_path))
    print(f"   Found {len(urls)} URLs")

    if args.limit > 0:
        urls = urls[: args.limit]
        print(f"   Limited to {args.limit} URLs")

    if not urls:
        print("⚠️  No URLs to submit")
        sys.exit(0)

    # Submit in batches
    total_submitted = 0
    success = True
    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i : i + BATCH_SIZE]
        print(f"📤 Batch {i // BATCH_SIZE + 1}: submitting {len(batch)} URLs...")
        ok = submit_batch(batch, dry_run=args.dry_run)
        if ok:
            total_submitted += len(batch)
        else:
            success = False

    if success:
        print(f"\n✅ IndexNow submission complete — {total_submitted} URLs submitted")
    else:
        print(f"\n⚠️  Partial submission — {total_submitted}/{len(urls)} URLs submitted")
        sys.exit(1)


if __name__ == "__main__":
    main()
