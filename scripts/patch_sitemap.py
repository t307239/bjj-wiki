#!/usr/bin/env python3
"""
sitemap.xml を完全再生成（既存 + 新規ページ全対応）
- athletes / gear / news ページも自動追加
- 全 lastmod を今日の日付に更新
- priority を適切に設定
"""

import os
import glob
import datetime

SITE_URL = "https://wiki.bjj-app.net"
SITE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TODAY    = datetime.date.today().isoformat()


def is_noindex(html_path: str) -> bool:
    """z255hh: page が <meta robots noindex> なら sitemap から除外
    (Google の sitemap quality 評価向上 + wasted crawl 防止)"""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            head = f.read(1500)
        return "noindex" in head
    except Exception:
        return False


def build_sitemap():
    urls = []

    # ===== ルートページ =====
    # z255r: athletes.html (root) を追加 — 旧 sitemap.xml から漏れ orphan だった
    root_pages = [
        ("index.html",    "weekly",  "1.0"),
        ("privacy.html",  "yearly",  "0.3"),
        ("about.html",    "monthly", "0.5"),
        ("404.html",      "yearly",  "0.1"),
        ("athletes.html", "weekly",  "0.7"),
    ]
    for page, freq, prio in root_pages:
        path = os.path.join(SITE_DIR, page)
        if os.path.exists(path):
            urls.append(f"  <url><loc>{SITE_URL}/{page}</loc>"
                        f"<lastmod>{TODAY}</lastmod>"
                        f"<changefreq>{freq}</changefreq>"
                        f"<priority>{prio}</priority></url>")

    # ===== 言語別インデックス =====
    for lang in ["en", "ja", "pt"]:
        urls.append(f"  <url><loc>{SITE_URL}/{lang}/index.html</loc>"
                    f"<lastmod>{TODAY}</lastmod>"
                    f"<changefreq>daily</changefreq>"
                    f"<priority>0.9</priority></url>")
        # atoms.html (category index)
        cat_path = os.path.join(SITE_DIR, lang, "categories.html")
        if os.path.exists(cat_path):
            urls.append(f"  <url><loc>{SITE_URL}/{lang}/categories.html</loc>"
                        f"<lastmod>{TODAY}</lastmod>"
                        f"<changefreq>weekly</changefreq>"
                        f"<priority>0.8</priority></url>")

    # ===== ニュース・選手・ギアの特別ページ（高頻度更新） =====
    special_patterns = [
        ("news.html",      "daily",  "0.9"),
        ("athletes.html",  "weekly", "0.8"),
    ]
    for pattern, freq, prio in special_patterns:
        for lang in ["en", "ja", "pt"]:
            path = os.path.join(SITE_DIR, lang, pattern)
            if os.path.exists(path):
                urls.append(f"  <url><loc>{SITE_URL}/{lang}/{pattern}</loc>"
                            f"<lastmod>{TODAY}</lastmod>"
                            f"<changefreq>{freq}</changefreq>"
                            f"<priority>{prio}</priority></url>")

    # ===== トピッククラスター・ガイドページ =====
    cluster_pages = [
        "best-bjj-guards", "best-submissions", "best-sweeps",
        "beginner-guide", "advanced-techniques", "no-gi-guide",
        "leg-lock-guide", "guard-passing-guide", "takedown-guide",
    ]
    for lang in ["en", "ja", "pt"]:
        for slug in cluster_pages:
            path = os.path.join(SITE_DIR, lang, f"{slug}.html")
            if os.path.exists(path):
                urls.append(f"  <url><loc>{SITE_URL}/{lang}/{slug}.html</loc>"
                            f"<lastmod>{TODAY}</lastmod>"
                            f"<changefreq>monthly</changefreq>"
                            f"<priority>0.85</priority></url>")

    # ===== 選手個別ページ =====
    for lang in ["en", "ja", "pt"]:
        for html_path in sorted(glob.glob(os.path.join(SITE_DIR, lang, "athlete-*.html"))):
            slug = os.path.basename(html_path)
            urls.append(f"  <url><loc>{SITE_URL}/{lang}/{slug}</loc>"
                        f"<lastmod>{TODAY}</lastmod>"
                        f"<changefreq>monthly</changefreq>"
                        f"<priority>0.75</priority></url>")

    # ===== ギアレビューページ =====
    for html_path in sorted(glob.glob(os.path.join(SITE_DIR, "gear", "*.html"))):
        slug = os.path.basename(html_path)
        urls.append(f"  <url><loc>{SITE_URL}/gear/{slug}</loc>"
                    f"<lastmod>{TODAY}</lastmod>"
                    f"<changefreq>monthly</changefreq>"
                    f"<priority>0.75</priority></url>")

    # ===== 技記事（en/ja/pt） =====
    skip_patterns = {"index", "categories", "athletes", "news", "privacy", "about", "404"}
    for lang in ["en", "ja", "pt"]:
        for html_path in sorted(glob.glob(os.path.join(SITE_DIR, lang, "*.html"))):
            base = os.path.splitext(os.path.basename(html_path))[0]
            # 特別ページ・クラスターは既に追加済み
            if any(base == s or base.startswith(s) for s in
                   skip_patterns | set(cluster_pages) | {"athlete-", "best-bjj-guards",
                                                           "best-submissions","best-sweeps",
                                                           "beginner-guide","advanced-techniques",
                                                           "no-gi-guide","leg-lock-guide",
                                                           "guard-passing-guide","takedown-guide"}):
                continue
            if base.startswith("athlete-"):
                continue  # 選手ページは既に処理済み
            # z255hh: noindex page は sitemap 除外 (Google が conflict として
            # 扱い wasted crawl + sitemap quality 低下を防ぐ)
            if is_noindex(html_path):
                continue
            urls.append(f"  <url><loc>{SITE_URL}/{lang}/{base}.html</loc>"
                        f"<lastmod>{TODAY}</lastmod>"
                        f"<changefreq>monthly</changefreq>"
                        f"<priority>0.8</priority></url>")

    # XML出力
    sitemap_path = os.path.join(SITE_DIR, "sitemap.xml")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
    xml += '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    xml += "\n".join(urls) + "\n"
    xml += "</urlset>\n"

    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(xml)

    print(f"[OK] sitemap.xml 更新完了: {len(urls)} URLs (lastmod: {TODAY})")

if __name__ == "__main__":
    build_sitemap()
