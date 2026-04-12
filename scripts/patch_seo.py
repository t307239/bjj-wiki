#!/usr/bin/env python3
"""
BJJ Wiki - SEO強化：JSON-LD構造化データ一括追加
- Article schema
- FAQPage schema（Q&A抽出）
- BreadcrumbList schema
Usage: python3 scripts/patch_seo.py
Run from ~/Claude/bjj-wiki/
"""
import os, re, glob, json

BASE = os.path.expanduser("~/Claude/bjj-wiki")
ALREADY_MARKER = "application/ld+json"

BASE_URL = "https://wiki.bjj-app.net"

LANG_LABELS = {
    "en": ("BJJ Wiki", "BJJ Techniques"),
    "ja": ("BJJ Wiki", "BJJ テクニック"),
    "pt": ("BJJ Wiki", "Técnicas de BJJ"),
}

LANG_CODES = {"en": "en", "ja": "ja", "pt": "pt-BR"}

def extract_title(html):
    m = re.search(r'<title>([^<]+)</title>', html)
    return m.group(1).strip() if m else ""

def extract_description(html):
    m = re.search(r'<meta name="description" content="([^"]+)"', html)
    return m.group(1).strip() if m else ""

def extract_faq(html):
    """Q&Aペアを抽出"""
    pairs = []
    faq_blocks = re.findall(
        r'<div class="faq">\s*<div class="faq-q">Q:\s*(.*?)</div>\s*<p>(.*?)</p>',
        html, re.DOTALL
    )
    for q, a in faq_blocks:
        q_clean = re.sub(r'<[^>]+>', '', q).strip()
        a_clean = re.sub(r'<[^>]+>', '', a).strip()
        if q_clean and a_clean:
            pairs.append((q_clean, a_clean))
    return pairs

def build_jsonld(html, slug, lang):
    title = extract_title(html)
    desc = extract_description(html)
    url = f"{BASE_URL}/{lang}/{slug}.html"
    site_label, cat_label = LANG_LABELS.get(lang, LANG_LABELS["en"])
    lang_code = LANG_CODES.get(lang, lang)

    schemas = []

    # 1. Article schema
    schemas.append({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc,
        "url": url,
        "inLanguage": lang_code,
        "publisher": {
            "@type": "Organization",
            "name": "BJJ Wiki",
            "url": f"{BASE_URL}/"
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": url
        }
    })

    # 2. BreadcrumbList schema
    schemas.append({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": site_label,
                "item": f"{BASE_URL}/{lang}/index.html"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": title.split("|")[0].strip(),
                "item": url
            }
        ]
    })

    # 3. FAQPage schema（Q&Aがある場合のみ）
    faqs = extract_faq(html)
    if faqs:
        schemas.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": a
                    }
                }
                for q, a in faqs
            ]
        })

    blocks = "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(s, ensure_ascii=False, indent=2)}\n</script>'
        for s in schemas
    )
    return blocks

def patch_file(path, slug, lang):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    if ALREADY_MARKER in html:
        return "skip"

    jsonld = build_jsonld(html, slug, lang)
    # </head>の直前に挿入
    html = html.replace("</head>", jsonld + "\n</head>", 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return "ok"

def main():
    ok = skip = 0
    for lang in ["en", "ja", "pt"]:
        for path in sorted(glob.glob(os.path.join(BASE, lang, "*.html"))):
            if path.endswith("index.html"):
                continue
            slug = os.path.basename(path).replace(".html", "")
            result = patch_file(path, slug, lang)
            if result == "ok":
                print(f"[OK] {lang}/{slug}.html")
                ok += 1
            else:
                skip += 1

    print(f"\n[完了] {ok}件を更新（スキップ {skip}件）")

if __name__ == "__main__":
    main()
