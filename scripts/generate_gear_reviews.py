#!/usr/bin/env python3
"""
BJJ Gear Reviews Wiki 自動生成
- Geminiで「Best BJJ Gi for beginners」等の購買意欲高いクエリ向けページを生成
- Amazonアフィリエイトリンク埋め込み
"""
import os, json, time, datetime, urllib.request, urllib.error, re, argparse

BASE     = os.path.dirname(__file__) + "/.."
SITE_URL = "https://wiki.bjj-app.net"
# AMAZON_TAG removed (CLAUDE.md: affiliate links prohibited)
GA4_ID   = "G-7LM8L3TRZM"
ADSENSE  = "ca-pub-5529701443220352"

GEAR_PAGES = [
    {"slug":"best-bjj-gi-beginners","query":"best BJJ gi for beginners","category":"gi",
     "title":"Best BJJ Gi for Beginners 2026 — Top Picks & Buyer's Guide",
     "brands":["Sanabul","Tatami","Hayabusa","Gold BJJ","Fuji"]},
    {"slug":"best-no-gi-shorts","query":"best no-gi BJJ shorts","category":"nogi",
     "title":"Best No-Gi BJJ Shorts 2026 — MMA & Grappling Shorts Review",
     "brands":["Scramble","Tatami","Venum","Hyperfly","Sanabul"]},
    {"slug":"best-bjj-rashguard","query":"best BJJ rash guard","category":"nogi",
     "title":"Best BJJ Rash Guards 2026 — Compression & Long Sleeve Reviews",
     "brands":["Hayabusa","Scramble","Hyperfly","93brand","Tatami"]},
    {"slug":"best-bjj-belt","query":"best BJJ belt","category":"gear",
     "title":"Best BJJ Belts 2026 — Ranked by Color & Durability",
     "brands":["Tatami","Sanabul","Fuji","Kataaro","Scramble"]},
    {"slug":"best-bjj-mouthguard","query":"best mouthguard for BJJ","category":"gear",
     "title":"Best Mouthguard for BJJ 2026 — Protect Your Teeth While Rolling",
     "brands":["SISU","Shock Doctor","Venum","Opro","Makura"]},
    {"slug":"best-bjj-knee-pads","query":"best knee pads for BJJ","category":"gear",
     "title":"Best Knee Pads for BJJ 2026 — Knee Protection for Grapplers",
     "brands":["Bauerfeind","Nike","Rehband","Hayabusa","Sanabul"]},
]

GEMINI_MODELS = ["gemini-2.0-flash","gemini-1.5-flash","gemini-2.5-flash-preview-04-17"]

def load_secrets():
    s = {}
    try:
        with open(os.path.expanduser("~/.secrets")) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=",1)
                    s[k.strip()] = v.strip().strip('"').strip("'")
    except: pass
    return s

def gemini_call(prompt, api_key):
    # Security: API key は x-goog-api-key header 送信 (z143/z152 共通方針)
    req_headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        data = json.dumps({"contents":[{"parts":[{"text":prompt}]}]}).encode()
        req = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                res = json.loads(r.read())
            text = res["candidates"][0]["content"]["parts"][0]["text"]
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                return json.loads(m.group(0))
        except Exception as e:
            # exception message に URL/key が混ざらないよう種別のみ
            print(f"  {model}: {type(e).__name__}")
    return None

def generate_gear_content(page, api_key):
    prompt = f"""Write a detailed buying guide for "{page['query']}" in English.
Brands to mention: {', '.join(page['brands'])}

Return JSON only:
{{
  "meta": "155 char meta description with keyword '{page['query']}'",
  "intro": "2 paragraph introduction about why this gear matters for BJJ",
  "top_pick": "{page['brands'][0]}",
  "top_pick_reason": "2 sentences why this is the best overall pick",
  "budget_pick": "{page['brands'][-1]}",
  "budget_reason": "1-2 sentences for budget option",
  "reviews": [
    {{"brand":"{page['brands'][0]}","pros":"3 pros","cons":"1-2 cons","best_for":"who it's best for","rating":5}},
    {{"brand":"{page['brands'][1]}","pros":"3 pros","cons":"1-2 cons","best_for":"who it's best for","rating":4}},
    {{"brand":"{page['brands'][2]}","pros":"3 pros","cons":"1-2 cons","best_for":"who it's best for","rating":4}}
  ],
  "buying_tips": "3-4 bullet points on what to look for",
  "faq_q": "Most common question about {page['query']}",
  "faq_a": "Detailed answer"
}}"""
    return gemini_call(prompt, api_key)

def build_gear_html(page, content):
    slug      = page["slug"]
    title     = page["title"]
    query     = page["query"]
    meta      = content.get("meta","")
    intro     = content.get("intro","").replace("\n","<br>")
    top_pick  = content.get("top_pick","")
    top_reason = content.get("top_pick_reason","")
    budget    = content.get("budget_pick","")
    budget_r  = content.get("budget_reason","")
    reviews   = content.get("reviews",[])
    tips      = content.get("buying_tips","")
    faq_q     = content.get("faq_q","")
    faq_a     = content.get("faq_a","")
    now       = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+09:00")
    year      = datetime.datetime.now().year
    
    def review_card(r):
        brand   = r.get("brand","")
        pros    = r.get("pros","")
        cons    = r.get("cons","")
        bf      = r.get("best_for","")
        rating  = r.get("rating",4)
        stars   = "★"*rating + "☆"*(5-rating)
        amz_url = f"https://www.amazon.com/s?k=BJJ+{brand.replace(' ','+')}+{page['category']}"
        return f'''<div class="review-card">
  <div class="review-header">
    <span class="brand-name">{brand}</span>
    <span class="stars" style="color:#f59e0b">{stars}</span>
  </div>
  <div class="review-meta">Best for: <strong>{bf}</strong></div>
  <div class="pros-cons">
    <div class="pros">✅ {pros}</div>
    <div class="cons" style="color:#ef4444">⚠️ {cons}</div>
  </div>
  <a href="{amz_url}" target="_blank" rel="noopener noreferrer nofollow" class="amz-btn">
    🛒 Shop {brand} on Amazon
  </a>
</div>'''
    
    reviews_html = "\n".join(review_card(r) for r in reviews[:5])
    
    # FAQPage schema
    faq_schema = json.dumps({
        "@context":"https://schema.org","@type":"FAQPage",
        "mainEntity":[{"@type":"Question","name":faq_q,
            "acceptedAnswer":{"@type":"Answer","text":faq_a}}]
    }, ensure_ascii=False)

    # z260c: 旧 Product schema + 架空 AggregateRating は削除
    # 理由: ratingValue/reviewCount を `len(reviews)*40+100` 等の formula で生成しており
    # CLAUDE.md ルール -3 (嘘より沈黙) + Google 構造化データガイドライン (fake reviews 禁止)
    # の両方に違反。代わりに schema を出力しない (omit) ことで silent な honest 状態に。
    # 本物の review が集まり次第、real data ベースで schema 再導入可。
    # NOTE: generate_bjj_wiki.py が後段でこれらの page を Article schema で上書きしている
    # ため live page には影響なし (defense in depth)。
    product_schema = ""
    product_schema_block = f'<script type="application/ld+json">{product_schema}</script>' if product_schema else ''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
  <link rel="icon" href="https://wiki.bjj-app.net/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" sizes="180x180" href="https://wiki.bjj-app.net/apple-touch-icon.png"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | BJJ Wiki</title>
<meta name="description" content="{meta}">
<meta property="og:title" content="{title}">
    <meta property="og:site_name" content="BJJ Wiki">
<meta property="og:description" content="{meta}">
<meta property="og:image" content="{SITE_URL}/og-image.svg">
<meta property="og:url" content="{SITE_URL}/en/{slug}.html">
<link rel="canonical" href="{SITE_URL}/en/{slug}.html">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/en/{slug}.html">
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE}" crossorigin="anonymous"></script>
<script type="application/ld+json">
{{
  "@context":"https://schema.org","@type":"Article",
  "headline":"{title}",
  "description":"{meta}",
  "datePublished":"2026-03-13T00:00:00+09:00",
  "dateModified":"{now}",
  "url":"{SITE_URL}/en/{slug}.html",
  "author":{{"@type":"Organization","name":"BJJ Wiki","url":"{SITE_URL}/"}},
  "publisher":{{"@type":"Organization","name":"BJJ Wiki","url":"{SITE_URL}/"}}
}}
</script>
<script type="application/ld+json">{faq_schema}</script>
{product_schema_block}
<style>
:root{{--bg:#080b12;--card:#141926;--border:#1f2840;--text:#e8eaf6;--muted:#6b7699;--accent:#7c6af7;--accent2:#a78bfa}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,sans-serif;line-height:1.75;padding:0 16px}}
a{{color:var(--accent2);text-decoration:none}}a:hover{{text-decoration:underline}}
.container{{max-width:860px;margin:0 auto;padding-bottom:80px}}
header{{display:flex;align-items:center;justify-content:space-between;padding:20px 0;border-bottom:1px solid var(--border);margin-bottom:32px}}
.logo{{font-size:1.3rem;font-weight:800;color:var(--text)}}.logo span{{color:var(--accent)}}
h1{{font-size:2rem;font-weight:800;margin-bottom:16px}}
h2{{font-size:0.9rem;font-weight:700;color:var(--accent2);text-transform:uppercase;letter-spacing:.08em;margin:28px 0 14px}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px}}
.top-pick-box{{background:linear-gradient(135deg,#0a1a0a,#0f2010);border:2px solid #22c55e;border-radius:12px;padding:20px;margin:20px 0}}
.review-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:12px}}
.review-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}}
.brand-name{{font-size:1.1rem;font-weight:700}}
.stars{{font-size:1rem}}
.review-meta{{font-size:0.85rem;color:var(--muted);margin-bottom:10px}}
.pros-cons{{font-size:0.88rem;margin-bottom:12px;display:grid;gap:6px}}
.amz-btn{{display:inline-block;background:#ff9900;color:#111;padding:8px 20px;border-radius:8px;font-weight:700;font-size:0.85rem}}
footer{{margin-top:48px;padding-top:24px;border-top:1px solid var(--border);text-align:center;color:var(--muted);font-size:0.85rem}}
</style>
</head>
<body>
<div class="container">
<header>
  <a href="../index.html" class="logo">BJJ<span>Wiki</span></a>
  <nav style="display:flex;gap:12px">
    <a href="index.html">Techniques</a>
    <a href="../athletes.html">Athletes</a>
    <a href="../news.html">News</a>
  </nav>
</header>

<h1>{title}</h1>
<p style="color:var(--muted);font-size:0.85rem;margin-bottom:20px">Updated: {year} · BJJ Wiki Editorial Team</p>

<div class="card"><p>{intro}</p></div>

<div class="top-pick-box">
  <div style="font-size:0.75rem;font-weight:700;color:#22c55e;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px">⭐ TOP PICK</div>
  <div style="font-size:1.2rem;font-weight:800;margin-bottom:6px">{top_pick}</div>
  <p style="color:var(--muted);font-size:0.9rem">{top_reason}</p>
  <a href="https://www.amazon.com/s?k=BJJ+{top_pick.replace(' ','+')}+{page['category']}" 
     target="_blank" rel="noopener noreferrer nofollow"
     style="display:inline-block;margin-top:12px;background:#ff9900;color:#111;padding:10px 24px;border-radius:8px;font-weight:700">
    🛒 Shop {top_pick} on Amazon
  </a>
</div>

<h2>Top Reviews</h2>
{reviews_html}

<h2>Budget Pick</h2>
<div class="card">
  <strong>{budget}</strong> — {budget_r}
  <br>
  <a href="https://www.amazon.com/s?k=BJJ+{budget.replace(' ','+')}+{page['category']}"
     target="_blank" rel="noopener noreferrer nofollow"
     style="display:inline-block;margin-top:12px;background:#ff9900;color:#111;padding:8px 20px;border-radius:8px;font-weight:700;font-size:0.85rem">
    🛒 Shop Budget Pick
  </a>
</div>

<h2>What to Look For</h2>
<div class="card"><p>{tips}</p></div>

<div class="card">
  <strong>FAQ: {faq_q}</strong>
  <p style="margin-top:8px">{faq_a}</p>
</div>

<footer><p>BJJ Wiki — Free BJJ encyclopedia & gear guides</p>
<p style="margin-top:8px">· <a href="../privacy.html">Privacy Policy</a> · <a href="../about.html">About</a></p></footer>
</div>
</body>
</html>'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    
    secrets = load_secrets()
    api_key = os.environ.get("GEMINI_API_KEY") or secrets.get("GEMINI_API_KEY","")
    if not api_key:
        print("❌ GEMINI_API_KEY required"); return
    
    cache_file = os.path.join(BASE, "cache", "gear_cache.json")
    cache = json.load(open(cache_file)) if os.path.exists(cache_file) else {}
    
    todo = [p for p in GEAR_PAGES if p["slug"] not in cache][:args.limit]
    print(f"🛒 Generating {len(todo)} gear review pages...")
    
    out_dir = os.path.join(BASE,"en")
    os.makedirs(out_dir, exist_ok=True)
    
    sitemap_path = os.path.join(BASE,"sitemap.xml")
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    for page in todo:
        print(f"  {page['slug']}...")
        content = generate_gear_content(page, api_key)
        if not content:
            print(f"  ❌ Gemini failed"); continue
        html = build_gear_html(page, content)
        out_path = os.path.join(out_dir, page["slug"]+".html")
        with open(out_path,"w",encoding="utf-8") as f:
            f.write(html)
        print(f"  ✅ {out_path}")
        cache[page["slug"]] = True
        time.sleep(1)
    
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f)
    
    # sitemap更新
    if os.path.exists(sitemap_path):
        with open(sitemap_path) as f:
            sm = f.read()
        new_entries = []
        for p in GEAR_PAGES:
            u = f"{SITE_URL}/en/{p['slug']}.html"
            if u not in sm:
                new_entries.append(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>")
        if new_entries:
            sm = sm.replace("</urlset>", "\n".join(new_entries)+"\n</urlset>")
            with open(sitemap_path,"w",encoding="utf-8") as f: f.write(sm)
            print(f"✅ sitemap +{len(new_entries)} gear pages")

if __name__ == "__main__":
    main()
