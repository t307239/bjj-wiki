#!/usr/bin/env python3
"""
check_sitemap_drift.py — z255r+hh: sitemap.xml と HTML ファイル群の整合性検査

検出する drift class:
  A. sitemap に載っているが disk 上に存在しない URL
     (削除された page を sitemap が指したまま → Google が 404 を index)
  B. disk 上に存在する HTML が sitemap に無い orphan
     (noindex redirect と Google Search Console 認証 file は除外)
  C. (z255hh) sitemap に載っているが page 自体が <meta robots noindex>
     → Google が conflict 扱い、wasted crawl + sitemap quality 低下

z255q broken-link 検査と相補的:
  - broken-link は HTML 内の <a href> 死活
  - sitemap drift は外部 (Google) に公開した URL の死活

--ci flag で drift > 0 → exit 1
"""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITEMAP = REPO_ROOT / "sitemap.xml"
LANGS = ["en", "ja", "pt"]
ALLOWED_ORPHANS = {
    # Google Search Console verification — sitemap に載せると逆に駄目
    "google9ef7b9e441cc36f8.html",
}
SITE_PREFIX = "https://wiki.bjj-app.net/"


def main() -> int:
    if not SITEMAP.exists():
        print(f"❌ {SITEMAP} not found")
        return 1

    sm = SITEMAP.read_text(encoding="utf-8")
    sitemap_urls = set(
        re.findall(rf"<loc>{re.escape(SITE_PREFIX)}([^<]+)</loc>", sm)
    )
    print(f"📋 Sitemap entries: {len(sitemap_urls):,}")

    # Class A: sitemap が指す page が disk に無い
    missing = []
    # Class C (z255hh): sitemap が指す page が noindex (conflict)
    noindex_in_sitemap = []
    for u in sitemap_urls:
        fp = REPO_ROOT / u
        if not fp.exists():
            missing.append(u)
            continue
        try:
            head = fp.read_text(encoding="utf-8")[:1500]
        except Exception:
            continue
        if "noindex" in head:
            noindex_in_sitemap.append(u)

    # Class B: disk にある HTML が sitemap に無い (noindex / 認証 file / redirect stub 除外)
    # z262: <!-- z262-redirect --> marker を持つ redirect stub は sitemap 対象外
    REDIRECT_MARKER = "<!-- z262-redirect -->"
    orphans = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            rel = f"{lang}/{fp.name}"
            if rel in sitemap_urls:
                continue
            try:
                head = fp.read_text(encoding="utf-8")[:1000]
            except Exception:
                continue
            if "noindex" in head:
                continue
            if REDIRECT_MARKER in head:
                continue  # z262: redirect stub — sitemap に載せると重複 canonical
            orphans.append(rel)
    for fp in REPO_ROOT.glob("*.html"):
        if fp.name in sitemap_urls or fp.name in ALLOWED_ORPHANS:
            continue
        try:
            head = fp.read_text(encoding="utf-8")[:1000]
        except Exception:
            continue
        if "noindex" in head:
            continue
        if REDIRECT_MARKER in head:
            continue  # z262: redirect stub
        orphans.append(fp.name)

    print(f"❌ Missing from disk (sitemap → 404): {len(missing)}")
    for m in missing[:20]:
        print(f"  - {m}")
    print(f"❌ Orphan HTMLs (not in sitemap):     {len(orphans)}")
    for o in orphans[:20]:
        print(f"  - {o}")
    print(f"❌ Sitemap → noindex page (conflict): {len(noindex_in_sitemap)}")
    for n in noindex_in_sitemap[:20]:
        print(f"  - {n}")

    drift = len(missing) + len(orphans) + len(noindex_in_sitemap)
    if drift == 0:
        print("\n✅ No sitemap drift.")
    else:
        print(f"\n🔴 Total drift: {drift}")

    if "--ci" in sys.argv:
        return 1 if drift > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
