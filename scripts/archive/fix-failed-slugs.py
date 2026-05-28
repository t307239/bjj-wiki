#!/usr/bin/env python3
"""
Retry the 3 slugs that failed with 502 during the main migration.
"""
import os, json, requests
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import dotenv_values

BASE_DIR = Path(__file__).parent.parent
env = dotenv_values(BASE_DIR / ".env")

SUPABASE_URL = env.get("SUPABASE_URL", "")
SERVICE_KEY  = env.get("SUPABASE_SERVICE_ROLE_KEY", "")

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation,resolution=merge-duplicates",
}

FAILED = [
    ("bjj-curriculum-bjj", "ja"),
    ("bjj-guard-recovery-drills", "pt"),
    ("bjj-turtle-position-guide", "pt"),
]


def extract(html_path: Path):
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    # Skip redirects
    if soup.find("meta", attrs={"http-equiv": "refresh"}):
        return None
    title = (soup.find("title") or soup.find("h1") or soup.find("h2"))
    title_text = title.get_text(strip=True) if title else html_path.stem
    desc_tag = soup.find("meta", attrs={"name": "description"})
    desc = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else None
    article = soup.find("article") or soup.find("main") or soup.find(id="content") or soup.body
    content_html = str(article) if article else str(soup.body)
    return title_text, desc, content_html


def upsert_page(slug: str):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/wiki_pages",
        headers=HEADERS,
        json={"slug": slug},
    )
    if r.status_code in (200, 201):
        data = r.json()
        return data[0]["id"] if isinstance(data, list) else data["id"]
    # Already exists — fetch
    r2 = requests.get(
        f"{SUPABASE_URL}/rest/v1/wiki_pages",
        headers=HEADERS,
        params={"slug": f"eq.{slug}", "select": "id"},
    )
    r2.raise_for_status()
    return r2.json()[0]["id"]


def upsert_translation(page_id: str, lang: str, title: str, desc, content_html: str):
    from datetime import datetime, timezone
    payload = {
        "page_id": page_id,
        "language_code": lang,
        "title": title,
        "description": desc,
        "content_html": content_html,
        "content_type": None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/wiki_translations",
        headers={**HEADERS, "Prefer": "return=minimal,resolution=merge-duplicates"},
        json=payload,
    )
    if r.status_code not in (200, 201, 204):
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")


def main():
    for slug, lang in FAILED:
        html_path = BASE_DIR / lang / f"{slug}.html"
        if not html_path.exists():
            print(f"⚠️  File not found: {html_path}")
            continue
        result = extract(html_path)
        if result is None:
            print(f"⏭  Redirect skipped: {slug}/{lang}")
            continue
        title, desc, content_html = result
        print(f"🔄 Upserting {slug}/{lang} …", end=" ")
        try:
            page_id = upsert_page(slug)
            upsert_translation(page_id, lang, title, desc, content_html)
            print("✅")
        except Exception as e:
            print(f"❌ {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
