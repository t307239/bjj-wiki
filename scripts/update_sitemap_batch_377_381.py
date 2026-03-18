#!/usr/bin/env python3
"""Update sitemap.xml with batch 377-381 URLs."""

import os
from datetime import datetime

IS_CI = os.environ.get("GITHUB_ACTIONS") == "true"
SITE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if IS_CI else "/sessions/keen-sharp-davinci/mnt/Claude/bjj-wiki"
SITE_URL = "https://t307239.github.io/bjj-wiki"

# 5 themes × 3 languages = 15 new URLs
NEW_ARTICLES = [
    "bjj-attacking-from-turtle",
    "bjj-conditioning-science",
    "bjj-guard-setups-masterclass",
    "bjj-back-control-finishing",
    "bjj-sweeps-to-submissions",
]

LANGUAGES = ["en", "ja", "pt"]

def update_sitemap():
    """Add new URLs to sitemap.xml."""
    sitemap_path = os.path.join(SITE_DIR, "sitemap.xml")

    # Read existing sitemap
    with open(sitemap_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Generate new URL entries
    new_entries = []
    for article in NEW_ARTICLES:
        for lang in LANGUAGES:
            url = f"{SITE_URL}/{lang}/{article}.html"
            entry = f"""  <url>
    <loc>{url}</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
"""
            new_entries.append(entry)

    # Insert before closing </urlset>
    new_content = content.replace("</urlset>", "".join(new_entries) + "</urlset>")

    # Write back
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ Updated sitemap.xml with {len(new_entries)} new URLs")

if __name__ == "__main__":
    update_sitemap()
