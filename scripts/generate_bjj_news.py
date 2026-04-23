#!/usr/bin/env python3
"""
BJJ News Auto-Generator
Sources: r/bjj RSS, BJJee RSS, FloGrappling (scrape)
→ Geminiで英語/日本語要約 → news.html 生成
"""
import os, json, time, datetime, urllib.request, urllib.error, re
from xml.etree import ElementTree as ET

SITE_URL  = "https://wiki.bjj-app.net"
OUT_DIR   = os.path.join(os.path.dirname(__file__), "..")
GA4_ID    = "G-7LM8L3TRZM"
ADSENSE   = "ca-pub-5529701443220352"

RSS_SOURCES = [
    ("Reddit r/bjj",    "https://www.reddit.com/r/bjj/.rss?limit=15"),
    ("BJJee",           "https://www.bjjee.com/feed/"),
    ("Grapplearts",     "https://www.grapplearts.com/feed/"),
]

def fetch_rss(url, max_items=8):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; BJJWikiBot/1.0)"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            xml = r.read()
        root = ET.fromstring(xml)
        ns = {"atom": "http://www.w3.org/2005/Atom",
              "media": "http://search.yahoo.com/mrss/"}
        items = []
        # Atom (Reddit) or RSS
        entries = root.findall(".//atom:entry", ns) or root.findall(".//item")
        for entry in entries[:max_items]:
            def get(tag, ns_prefix=None):
                t = f"{ns_prefix}:{tag}" if ns_prefix else tag
                e = entry.find(t, ns) if ns_prefix else entry.find(tag)
                return e.text.strip() if e is not None and e.text else ""
            
            title = (get("title","atom") or get("title")).replace("<![CDATA[","").replace("]]>","").strip()
            link  = get("link","atom") or get("link")
            if hasattr(entry.find("link","atom" if ns else None), "get"):
                link = entry.find("atom:link",ns).get("href","") or link
            # Atom link fix
            le = entry.find("atom:link", ns)
            if le is not None:
                link = le.get("href", link)
            
            summary = (get("summary","atom") or get("description"))[:300]
            # strip HTML
            summary = re.sub(r"<[^>]+>","",summary).strip()[:200]
            
            if title and len(title) > 5:
                items.append({"title": title, "url": link, "summary": summary})
        return items
    except Exception as e:
        print(f"  RSS fetch error {url}: {e}")
        return []

def gemini_summarize(items_text, api_key, lang="en"):
    if lang == "ja":
        prompt = f"""以下のBJJニュース記事リストを日本語で簡潔に要約してください。
各記事を1-2文で要約し、読者が「何が起きたか」をすぐ理解できるようにしてください。
JSON配列で返してください: [{{"title":"日本語タイトル","summary":"日本語要約1-2文"}}]

記事リスト:
{items_text}"""
    else:
        prompt = f"""Summarize these BJJ news items in English. 
For each item write a 1-2 sentence summary that captures the key point.
Return JSON array: [{{"title":"clear title","summary":"1-2 sentence summary"}}]

Items:
{items_text}"""
    
    models = ["gemini-2.5-flash-lite","gemini-2.5-flash"]
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        data = json.dumps({"contents":[{"parts":[{"text":prompt}]}]}).encode()
        req = urllib.request.Request(url, data=data,
            headers={"Content-Type":"application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                res = json.loads(r.read())
            text = res["candidates"][0]["content"]["parts"][0]["text"]
            # JSON抽出
            m = re.search(r"\[.*\]", text, re.DOTALL)
            if m:
                return json.loads(m.group(0))
        except:
            continue
    return []

# ニュース本文に技名が含まれていたらWikiリンクに変換（ファネル強化）
TECHNIQUE_MAP = {
    "armbar":"en/armbar.html","triangle choke":"en/triangle-choke.html",
    "rear naked choke":"en/rear-naked-choke.html","guillotine":"en/guillotine-choke.html",
    "kimura":"en/kimura.html","heel hook":"en/heel-hook.html",
    "inside heel hook":"en/inside-heel-hook.html","outside heel hook":"en/outside-heel-hook.html",
    "leg lock":"en/heel-hook.html","leg locks":"en/heel-hook.html",
    "berimbolo":"en/berimbolo.html","back take":"en/backtake.html",
    "omoplata":"en/omoplata.html","darce":"en/darce-choke.html",
    "anaconda":"en/anaconda-choke.html","half guard":"en/half-guard.html",
    "closed guard":"en/closed-guard.html","butterfly guard":"en/butterfly-guard.html",
    "de la riva":"en/de-la-riva-guard.html","x guard":"en/x-guard.html",
    "double leg":"en/double-leg-takedown.html","single leg":"en/single-leg-takedown.html",
    "knee bar":"en/knee-bar.html","toe hold":"en/toe-hold.html",
    "americana":"en/americana.html","bow and arrow":"en/bow-and-arrow-choke.html",
    "baseball choke":"en/baseball-choke.html","north south":"en/north-south-choke.html",
    "calf slicer":"en/calf-slicer.html","ankle lock":"en/ankle-lock.html",
    "wrist lock":"en/wrist-lock.html","ezekiel":"en/ezekiel-choke.html",
    "torreando":"en/torreando-pass.html","knee slice":"en/knee-slice-pass.html",
    "leg drag":"en/leg-drag-pass.html","spider guard":"en/spider-guard.html",
    "lasso guard":"en/lasso-guard.html","worm guard":"en/worm-guard.html",
    "50/50":"en/50-50-guard.html","50-50":"en/50-50-guard.html",
    "deep half":"en/deep-half-guard.html","rubber guard":"en/rubber-guard.html",
    "body triangle":"en/body-triangle.html","seat belt":"en/seat-belt-control.html",
    "clock choke":"en/clock-choke.html","loop choke":"en/loop-choke.html",
    "scissor sweep":"en/scissor-sweep.html","tripod sweep":"en/tripod-sweep.html",
    "hip bump":"en/hip-bump-sweep.html","back control":"en/back-mount.html",
    "mount":"en/mount.html","side control":"en/side-control.html",
}

def find_technique_links(text):
    found = []
    seen = set()
    for tech_name, tech_path in TECHNIQUE_MAP.items():
        if tech_name in seen: continue
        if re.search(re.escape(tech_name), text, re.IGNORECASE):
            found.append((tech_name, tech_path))
            seen.add(tech_name)
            if len(found) >= 2: break
    return found

def build_html(news_en, news_ja, date_str):
    def card(item, lang):
        url = item.get("url","#")
        title = item.get("title","")
        summary = item.get("summary","")
        techs = find_technique_links(title + " " + summary)
        tech_html = ""
        if techs:
            links = " · ".join(
                f'<a href="{t[1]}" style="color:var(--accent2,#a78bfa);font-size:0.78rem;font-weight:600">🥋 {t[0].title()} →</a>'
                for t in techs
            )
            tech_html = f'<div style="margin-top:8px;padding-top:8px;border-top:1px solid #1f2840">{links}</div>'
        return f'''<div class="news-card">
<a href="{url}" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none">
  <div class="news-title">{title}</div>
  <div class="news-summary">{summary}</div>
  <span class="news-src">↗ Full article</span>
</a>{tech_html}</div>'''

    en_cards = "\n".join(card(i,"en") for i in news_en[:10])
    ja_cards = "\n".join(card(i,"ja") for i in news_ja[:10])
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.googletagmanager.com">
<meta charset="UTF-8">
  <link rel="icon" href="https://wiki.bjj-app.net/favicon.svg" type="image/svg+xml">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BJJ News Today — Brazilian Jiu-Jitsu Latest Updates | BJJ Wiki</title>
<meta name="description" content="Latest BJJ news, competition results, and technique updates. Daily Brazilian Jiu-Jitsu news aggregated from r/bjj, BJJee, and Grapplearts.">
<meta property="og:title" content="BJJ News Today — Latest Brazilian Jiu-Jitsu Updates">
    <meta property="og:site_name" content="BJJ Wiki">
<meta property="og:description" content="Daily BJJ news: competition results, new instructionals, rule changes.">
<meta property="og:image" content="{SITE_URL}/og-image.svg">
<meta property="og:url" content="{SITE_URL}/news.html">
<link rel="canonical" href="{SITE_URL}/news.html">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/news.html">
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE}" crossorigin="anonymous"></script>
<style>
:root{{--bg:#080b12;--surface:#0f1420;--card:#141926;--border:#1f2840;--text:#e8eaf6;--muted:#6b7699;--accent:#7c6af7;--accent2:#a78bfa;--green:#22c55e}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif;line-height:1.7;padding:0 16px}}
a{{color:var(--accent2);text-decoration:none}}
.container{{max-width:860px;margin:0 auto;padding-bottom:80px}}
header{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;padding:20px 0;border-bottom:1px solid var(--border);margin-bottom:32px}}
.logo{{font-size:1.3rem;font-weight:800;color:var(--text)}}.logo span{{color:var(--accent)}}
header nav a{{font-size:0.85rem;color:var(--muted);padding:4px 10px;border-radius:6px;border:1px solid transparent}}
header nav a:hover{{color:var(--text);border-color:var(--border)}}
h1{{font-size:2rem;font-weight:800;margin:0 0 8px;letter-spacing:-0.02em}}
.date-badge{{display:inline-block;background:#1f2840;color:var(--muted);font-size:0.8rem;padding:4px 12px;border-radius:20px;margin-bottom:24px}}
.tabs{{display:flex;gap:8px;margin-bottom:24px;border-bottom:1px solid var(--border);padding-bottom:0}}
.tab{{padding:8px 20px;border-radius:8px 8px 0 0;font-size:0.9rem;font-weight:600;cursor:pointer;color:var(--muted);border:1px solid transparent;border-bottom:none;background:transparent}}
.tab.active{{color:var(--accent2);border-color:var(--border);background:var(--surface)}}
.tab-content{{display:none}}.tab-content.active{{display:block}}
.news-grid{{display:grid;gap:16px}}
.news-card{{display:block;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;transition:border-color .2s;color:var(--text)}}
.news-card:hover{{border-color:var(--accent);text-decoration:none}}
.news-title{{font-size:1rem;font-weight:700;margin-bottom:8px;line-height:1.4}}
.news-summary{{font-size:0.88rem;color:var(--muted);line-height:1.6}}
.news-src{{display:inline-block;margin-top:10px;font-size:0.75rem;color:var(--accent);opacity:0.7}}
.section-label{{font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin:32px 0 12px}}
.beehiiv-cta{{background:linear-gradient(135deg,#1a0a2e,#0d1a2e);border:1px solid var(--accent);border-radius:12px;padding:24px;margin:32px 0;text-align:center}}
.beehiiv-cta h3{{font-size:1.1rem;margin-bottom:8px}}
.beehiiv-cta p{{color:var(--muted);font-size:0.9rem;margin-bottom:16px}}
footer{{margin-top:48px;padding-top:24px;border-top:1px solid var(--border);text-align:center;color:var(--muted);font-size:0.85rem}}
</style>
</head>
<body>
<div class="container">
<header>
  <a href="index.html" class="logo">BJJ<span>Wiki</span></a>
  <nav style="display:flex;gap:16px">
    <a href="en/index.html">Techniques</a>
    <a href="news.html" style="color:var(--accent2)">News</a>
    <a href="about.html">About</a>
  </nav>
</header>

<h1>BJJ News</h1>
<div class="date-badge">Updated: {date_str}</div>

<div class="tabs">
  <div class="tab active" onclick="switchTab('en',this)">🌐 English</div>
  <div class="tab" onclick="switchTab('ja',this)">🇯🇵 日本語</div>
</div>

<div id="tab-en" class="tab-content active">
  <div class="section-label">Latest from r/bjj &amp; BJJ Community</div>
  <div class="news-grid">
{en_cards}
  </div>
</div>

<div id="tab-ja" class="tab-content">
  <div class="section-label">BJJニュース（日本語要約）</div>
  <div class="news-grid">
{ja_cards}
  </div>
</div>

<div class="beehiiv-cta">
  <h3>🐝 毎週BJJニュースをメールで受け取る</h3>
  <p>週1回、厳選BJJニュース + 技解説をお届け。無料。</p>
  <a href="https://bjj-wiki.beehiiv.com/subscribe" target="_blank" rel="noopener"
    style="display:inline-block;padding:10px 28px;background:#7c3aed;color:#fff;border-radius:8px;font-weight:700;font-size:0.9rem">
    Subscribe Free →
  </a>
</div>

<div style="text-align:center;margin:24px 0">
  <a href="en/index.html" style="display:inline-block;padding:10px 24px;border:1px solid var(--accent);border-radius:8px;color:var(--accent2);font-weight:600">
    🥋 Browse 100+ BJJ Techniques →
  </a>
</div>

<footer>
  <p>BJJ Wiki — Daily news aggregated from r/bjj, BJJee, Grapplearts</p>
  <p style="margin-top:8px">· <a href="privacy.html">Privacy Policy</a> · <a href="about.html">About</a></p>
</footer>
</div>

<script>
function switchTab(lang, el) {{
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tab-'+lang).classList.add('active');
  el.classList.add('active');
}}
</script>
</body>
</html>'''

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", default=os.environ.get("GEMINI_API_KEY",""))
    parser.add_argument("--out", default=OUT_DIR)
    args = parser.parse_args()
    
    api_key = args.api_key
    if not api_key:
        # ~/.secrets から読み込み
        try:
            with open(os.path.expanduser("~/.secrets")) as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        api_key = line.split("=",1)[1].strip()
        except:
            pass
    
    print("📰 BJJ News Generator")
    
    # RSS収集
    all_items = []
    for source_name, url in RSS_SOURCES:
        print(f"  Fetching {source_name}...")
        items = fetch_rss(url)
        print(f"    {len(items)} items")
        all_items.extend(items)
    
    if not all_items:
        print("❌ No items fetched")
        return
    
    # 重複排除
    seen = set()
    unique = []
    for item in all_items:
        if item["title"] not in seen:
            seen.add(item["title"])
            unique.append(item)
    unique = unique[:15]
    
    items_text = "\n".join(f"- {i['title']}: {i['summary']}" for i in unique)
    
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    
    print("  Generating English summaries...")
    news_en = []
    if api_key:
        news_en = gemini_summarize(items_text, api_key, "en") or []
        # URLを元のitemから引き継ぐ
        for j, item in enumerate(news_en):
            if j < len(unique):
                item["url"] = unique[j].get("url","#")
    
    if not news_en:
        news_en = [{"title": i["title"], "summary": i["summary"], "url": i.get("url","#")} for i in unique[:10]]
    
    print("  Generating Japanese summaries...")
    news_ja = []
    if api_key:
        news_ja = gemini_summarize(items_text, api_key, "ja") or []
        for j, item in enumerate(news_ja):
            if j < len(unique):
                item["url"] = unique[j].get("url","#")
    if not news_ja:
        news_ja = news_en  # fallback
    
    html = build_html(news_en, news_ja, date_str)
    out_path = os.path.join(args.out, "news.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Generated: {out_path}")
    print(f"   Items: {len(news_en)} EN, {len(news_ja)} JA")

if __name__ == "__main__":
    main()
