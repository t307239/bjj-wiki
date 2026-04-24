#!/usr/bin/env python3
"""
BJJ選手名鑑 自動生成
- 選手プロフィール × 得意技（Wikiリンク）× BJJ Fanatics教則DVDリンク
- en/ja/pt 3言語対応
- GitHub Actions で定期実行
"""
import os, json, time, datetime, urllib.request, urllib.error, re, argparse

BASE     = os.path.dirname(__file__) + "/.."
SITE_URL = "https://wiki.bjj-app.net"
GA4_ID   = "G-7LM8L3TRZM"
ADSENSE  = "ca-pub-5529701443220352"
# AMAZON_TAG removed (CLAUDE.md: affiliate links prohibited)

# 選手マスターデータ（手動メンテ + 自動生成の組み合わせ）
ATHLETES = [
    {
        "slug": "gordon-ryan",
        "name": "Gordon Ryan",
        "nickname": "The King",
        "country": "us",
        "belt": "black",
        "team": "New Wave Jiu-Jitsu",
        "known_for": ["rear-naked-choke","heel-hook","inside-heel-hook","darce-choke","back-mount","leg-entanglement"],        "fanatics_title": "Systematically Attacking the Legs",
        "weight": "Heavyweight",
        "titles": ["ADCC Champion 2017, 2019, 2022", "EBI Champion", "Who's Number One Champion"],
    },
    {
        "slug": "mikey-musumeci",
        "name": "Mikey Musumeci",
        "nickname": "Darth Rigatoni",
        "country": "us",
        "belt": "black",
        "team": "New Wave Jiu-Jitsu",
        "known_for": ["triangle-choke","omoplata","lasso-guard","rubber-guard","spider-guard","berimbolo"],        "fanatics_title": "My Leg Attack and Defense System",
        "weight": "Flyweight / Strawweight",
        "titles": ["ADCC Champion 2022", "Multiple IBJJF World Champion", "ONE Championship MMA"],
    },
    {
        "slug": "craig-jones",
        "name": "Craig Jones",
        "nickname": "El Monstro",
        "country": "au",
        "belt": "black",
        "team": "B-Team",
        "known_for": ["heel-hook","outside-heel-hook","knee-bar","50-50-guard","triangle-choke","leg-entanglement"],        "fanatics_title": "Down Under Leg Locks",
        "weight": "Middleweight",
        "titles": ["ADCC 2017 Superfight", "Multiple WNO Championships"],
    },
    {
        "slug": "john-danaher",
        "name": "John Danaher",
        "nickname": "The Professor",
        "country": "nz",
        "belt": "black",
        "team": "New Wave Jiu-Jitsu",
        "known_for": ["heel-hook","rear-naked-choke","back-mount","leg-entanglement","arm-triangle-choke"],        "fanatics_title": "Enter The System: Rear Naked Choke",
        "weight": "N/A (Coach)",
        "titles": ["Head coach of multiple ADCC Champions", "Most influential BJJ coach"],
    },
    {
        "slug": "marcelo-garcia",
        "name": "Marcelo Garcia",
        "nickname": "MG",
        "country": "br",
        "belt": "black",
        "team": "Marcelo Garcia Academy",
        "known_for": ["guillotine-choke","rear-naked-choke","butterfly-guard","x-guard","anaconda-choke","arm-drag"],        "fanatics_title": "High Percentage Chokes: No Gi",
        "weight": "Lightweight / Middleweight",
        "titles": ["ADCC Champion 2003, 2005, 2007, 2009", "5x IBJJF World Champion"],
    },
    {
        "slug": "bernardo-faria",
        "name": "Bernardo Faria",
        "nickname": "The Half Guard King",
        "country": "br",
        "belt": "black",
        "team": "Alliance",
        "known_for": ["half-guard","deep-half-guard","double-under-pass","omoplata","scissor-sweep"],        "fanatics_title": "Battle Tested Half Guard",
        "weight": "Super Heavyweight",
        "titles": ["5x IBJJF World Champion", "ADCC Champion 2015"],
    },
    {
        "slug": "andre-galvao",
        "name": "André Galvão",
        "nickname": "Buchecha",
        "country": "br",
        "belt": "black",
        "team": "Atos",
        "known_for": ["back-mount","bow-and-arrow-choke","guard-pass","arm-drag","double-leg-takedown"],        "fanatics_title": "Back Attacks",
        "weight": "Absolute",
        "titles": ["ADCC Champion 2011, 2013", "Multiple IBJJF World Champion"],
    },
    {
        "slug": "caio-terra",
        "name": "Caio Terra",
        "nickname": "The Technician",
        "country": "br",
        "belt": "black",
        "team": "Caio Terra Association",
        "known_for": ["closed-guard","triangle-choke","armbar","omoplata","berimbolo","spider-guard"],        "fanatics_title": "Guard Passing and Beating Bigger Guys",
        "weight": "Rooster / Light Feather",
        "titles": ["9x IBJJF World Champion", "2x ADCC Champion"],
    },
    {
        "slug": "keenan-cornelius",
        "name": "Keenan Cornelius",
        "nickname": "Lapel Master",
        "country": "us",
        "belt": "black",
        "team": "Legion AJJ",
        "known_for": ["lasso-guard","worm-guard","de-la-riva-guard","reverse-de-la-riva","omoplata"],        "fanatics_title": "Lapel Encyclopedia",
        "weight": "Ultra Heavyweight",
        "titles": ["ADCC Absolute Finalist 2013", "Multiple IBJJF Pans/Worlds medals"],
    },
    {
        "slug": "xande-ribeiro",
        "name": "Xande Ribeiro",
        "nickname": "The Foundation",
        "country": "br",
        "belt": "black",
        "team": "SBG",
        "known_for": ["closed-guard","side-control","mount","armbar","kimura","guard-pass"],        "fanatics_title": "Secrets of the Closed Guard",
        "weight": "Superheavy / Absolute",
        "titles": ["2x ADCC Champion", "6x IBJJF World Champion"],
    },
    {
        "slug": "garry-tonon",
        "name": "Garry Tonon",
        "nickname": "The Lion Killer",
        "country": "us",
        "belt": "black",
        "team": "Danaher Death Squad / Renzo Gracie",
        "known_for": ["heel-hook","kneebar","back-take","arm-drag","rear-naked-choke"],        "fanatics_title": "Leg Lock Systems by Garry Tonon",
        "weight": "Lightweight",
        "titles": ["3x ADCC Medalist", "EBI Champion", "ONE Championship MMA (12-1)"],
    },
    {
        "slug": "mackenzie-dern",
        "name": "Mackenzie Dern",
        "nickname": "The Brazilian Beauty",
        "country": "us",
        "belt": "black",
        "team": "Gracie Barra",
        "known_for": ["triangle-choke","armbar","omoplata","closed-guard","kimura"],        "fanatics_title": "Guard Attacks by Mackenzie Dern",
        "weight": "Strawweight",
        "titles": ["3x IBJJF World Champion", "Absolute World Champion", "UFC Strawweight Top 5"],
    },
    {
        "slug": "ffion-davies",
        "name": "Ffion Davies",
        "nickname": "The Welsh Dragon",
        "country": "gb",
        "belt": "black",
        "team": "Checkmat BJJ",
        "known_for": ["leg-drag-pass","heel-hook","back-take","single-leg-takedown","x-pass"],        "fanatics_title": "Leg Drag System by Ffion Davies",
        "weight": "Featherweight (-60kg)",
        "titles": ["ADCC World Champion 2022", "ADCC Silver 2019", "EBI Champion", "5x British Champion"],
    },
    {
        "slug": "rafael-lovato-jr",
        "name": "Rafael Lovato Jr.",
        "nickname": "The American",
        "country": "us",
        "belt": "black",
        "team": "Lovato BJJ",
        "known_for": ["closed-guard","kimura","armbar","mount","triangle-choke"],        "fanatics_title": "Closed Guard Masterclass by Rafael Lovato Jr.",
        "weight": "Middleweight",
        "titles": ["IBJJF World Champion", "3x Pan American Champion", "First American Bellator Middleweight Champion"],
    },
    {
        "slug": "romulo-barral",
        "name": "Romulo Barral",
        "nickname": "The Terminator",
        "country": "br",
        "belt": "black",
        "team": "Gracie Barra",
        "known_for": ["spider-guard","triangle-choke","armbar","de-la-riva-guard","berimbolo"],        "fanatics_title": "Spider Guard by Romulo Barral",
        "weight": "Medium Heavy",
        "titles": ["5x IBJJF World Champion", "ADCC Veteran", "Pan American Champion"],
    },
    {
        "slug": "claudio-calasans",
        "name": "Claudio Calasans",
        "nickname": "Calasinhas",
        "country": "br",
        "belt": "black",
        "team": "Atos BJJ",
        "known_for": ["heel-hook","ankle-lock","leg-drag-pass","50-50-guard","toe-hold"],        "fanatics_title": "Leg Lock System by Claudio Calasans",
        "weight": "Medium Heavy",
        "titles": ["ADCC Champion", "IBJJF World Champion", "Pan American Champion"],
    },
    {
        "slug": "xande-ribeiro-2",
        "name": "Pablo Popovitch",
        "nickname": "The Brazilian Tank",
        "country": "br",
        "belt": "black",
        "team": "Alliance",
        "known_for": ["closed-guard","kimura","armbar","mount","double-under-pass"],        "fanatics_title": "Closed Guard & Passing by Pablo Popovitch",
        "weight": "Super Heavy",
        "titles": ["ADCC Champion", "Multiple IBJJF World Champion", "No-Gi World Champion"],
    },
    {
        "slug": "nicky-ryan",
        "name": "Nicky Ryan",
        "nickname": "The Prodigy",
        "country": "us",
        "belt": "brown",
        "team": "Danaher Death Squad",
        "known_for": ["heel-hook","inside-heel-hook","butterfly-guard","x-guard","leg-drag-pass"],        "fanatics_title": "Leg Lock System by Nicky Ryan",
        "weight": "Lightweight",
        "titles": ["ADCC Medalist", "WNO Champion", "IBJJF No-Gi World Champion"],
    },
    {
        "slug": "bia-mesquita",
        "name": "Bia Mesquita",
        "nickname": "Cyborg",
        "country": "br",
        "belt": "black",
        "team": "Gracie Humaita",
        "known_for": ["triangle-choke","armbar","spider-guard","closed-guard","omoplata"],        "fanatics_title": "Guard Game by Bia Mesquita",
        "weight": "Lightweight",
        "titles": ["6x IBJJF World Champion", "ADCC Silver Medalist", "Pan American Champion"],
    },
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
            return res["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            # exception message に URL/key が混ざらないよう種別のみ
            print(f"  {model}: {type(e).__name__}")
            continue
    return None

def generate_athlete_content(athlete, lang, api_key):
    lang_label = {"en":"English","ja":"Japanese","pt":"Portuguese"}[lang]
    prompt = f"""Write a BJJ athlete profile for {athlete['name']} ({athlete.get('nickname','')}) in {lang_label}.
Known for: {', '.join(athlete['known_for'])}
Titles: {', '.join(athlete['titles'])}
Team: {athlete['team']}

Return JSON only:
{{
  "title": "SEO title (60 chars max)",
  "meta": "meta description (155 chars)",
  "bio": "2-3 paragraph biography focusing on competition achievements and BJJ style",
  "style": "2 sentences describing their specific BJJ style and game",
  "signature_move": "Their most iconic technique (1 sentence)",
  "why_study": "Why should a BJJ student study this athlete's game (1-2 sentences)"
}}"""
    
    text = gemini_call(prompt, api_key)
    if not text: return None
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except:
            pass
    return None

def build_athlete_html(athlete, content, lang):
    slug        = athlete["slug"]
    name        = athlete["name"]
    nickname    = athlete.get("nickname","")
    titles      = athlete.get("titles",[])
    techniques  = athlete.get("known_for",[])
    fanatics_url  = athlete.get("fanatics_url","")
    fanatics_featured = athlete.get("fanatics_featured","")
    fanatics_title = athlete.get("fanatics_title","")
    
    title_tag   = content.get("title", name)
    meta_desc   = content.get("meta", "")
    bio         = content.get("bio","").replace("\n","<br>")
    style_txt   = content.get("style","")
    sig_move    = content.get("signature_move","")
    why_study   = content.get("why_study","")
    
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+09:00")
    
    # 技リンク（wiki技ページへ）
    tech_links = []
    for tech_slug in techniques[:6]:
        tech_name = tech_slug.replace("-"," ").title()
        tech_links.append(
            f'<a href="../{lang}/{tech_slug}.html" class="tech-tag">🥋 {tech_name}</a>'
        )
    tech_links_html = "\n".join(tech_links)
    
    # タイトルリスト
    titles_html = "\n".join(f"<li>{t}</li>" for t in titles)
    
    # 言語別ラベル
    labels = {
        "en": {"signature":"Signature Techniques","titles":"Major Titles",
               "style":"Fighting Style","study":"Why Study This Athlete",
               "instructional":"Featured Instructional","browse":"Browse All Instructionals",
               "gear":"Shop Training Gear","back":"← All Athletes"},
        "ja": {"signature":"得意技・シグネチャームーブ","titles":"主なタイトル",
               "style":"戦闘スタイル","study":"なぜこの選手を研究すべきか",
               "instructional":"おすすめ教則DVD","browse":"全教則DVDを見る",
               "gear":"練習器具を探す","back":"← 選手一覧へ"},
        "pt": {"signature":"Técnicas Assinatura","titles":"Principais Títulos",
               "style":"Estilo de Luta","study":"Por que estudar este atleta",
               "instructional":"Instrucional em Destaque","browse":"Ver todos os instrucionais",
               "gear":"Comprar equipamentos","back":"← Todos os Atletas"},
    }
    L = labels.get(lang, labels["en"])
    
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.googletagmanager.com">
<meta charset="UTF-8">
  <link rel="icon" href="https://wiki.bjj-app.net/favicon.svg" type="image/svg+xml">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title_tag} | BJJ Wiki</title>
<meta name="description" content="{meta_desc}">
<meta property="og:title" content="{title_tag}">
    <meta property="og:site_name" content="BJJ Wiki">
<meta property="og:description" content="{meta_desc}">
<meta property="og:image" content="{SITE_URL}/og-image.svg">
<meta property="og:url" content="{SITE_URL}/{lang}/athlete-{slug}.html">
<link rel="canonical" href="{SITE_URL}/{lang}/athlete-{slug}.html">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/en/athlete-{slug}.html">
<link rel="alternate" hreflang="en" href="{SITE_URL}/en/athlete-{slug}.html">
<link rel="alternate" hreflang="ja" href="{SITE_URL}/ja/athlete-{slug}.html">
<link rel="alternate" hreflang="pt" href="{SITE_URL}/pt/athlete-{slug}.html">
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE}" crossorigin="anonymous"></script>
<script type="application/ld+json">
{{
  "@context":"https://schema.org","@type":"ProfilePage",
  "name":"{title_tag}","description":"{meta_desc}",
  "url":"{SITE_URL}/{lang}/athlete-{slug}.html",
  "datePublished":"2026-03-13T00:00:00+09:00",
  "dateModified":"{now}",
  "mainEntity":{{
    "@type":"Person","name":"{name}",
    "jobTitle":"Brazilian Jiu-Jitsu Athlete",
    "affiliation":"{athlete.get('team','')}"
  }}
}}
</script>
<style>
:root{{--bg:#080b12;--surface:#0f1420;--card:#141926;--border:#1f2840;--text:#e8eaf6;--muted:#6b7699;--accent:#7c6af7;--accent2:#a78bfa;--gold:#f59e0b}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif;line-height:1.75;padding:0 16px}}
a{{color:var(--accent2);text-decoration:none}}a:hover{{text-decoration:underline}}
.container{{max-width:860px;margin:0 auto;padding-bottom:80px}}
header{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;padding:20px 0;border-bottom:1px solid var(--border);margin-bottom:32px}}
.logo{{font-size:1.3rem;font-weight:800;color:var(--text)}}.logo span{{color:var(--accent)}}
header nav a{{font-size:0.85rem;color:var(--muted);padding:4px 10px;border-radius:6px;border:1px solid transparent}}
.athlete-hero{{background:linear-gradient(135deg,#1a0a2e,#0d1a2e);border:1px solid var(--accent);border-radius:16px;padding:32px;margin-bottom:32px}}
.athlete-name{{font-size:2.2rem;font-weight:800;margin-bottom:4px}}
.athlete-nick{{color:var(--accent2);font-size:1rem;margin-bottom:16px}}
.athlete-meta{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px}}
.meta-badge{{background:#1f2840;color:var(--muted);font-size:0.78rem;padding:4px 12px;border-radius:20px}}
.titles-list{{list-style:none;padding:0}}
.titles-list li{{padding:4px 0;color:var(--gold);font-size:0.9rem}}
.titles-list li::before{{content:"🏆 "}}
h2{{font-size:0.9rem;font-weight:700;color:var(--accent2);text-transform:uppercase;letter-spacing:.08em;margin:28px 0 12px}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px}}
.tech-tags{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}}
.tech-tag{{display:inline-block;padding:6px 14px;background:#1f2840;border:1px solid var(--accent);border-radius:20px;font-size:0.82rem;color:var(--accent2);font-weight:600}}
.tech-tag:hover{{background:var(--accent);color:#fff;text-decoration:none}}
.fanatics-box{{background:linear-gradient(135deg,#1a0a1a,#0a0a1a);border:2px solid var(--accent);border-radius:16px;padding:28px;margin:28px 0;text-align:center}}
.fanatics-box h3{{font-size:1.1rem;margin-bottom:8px;color:var(--accent2)}}
.fanatics-box p{{color:var(--muted);font-size:0.9rem;margin-bottom:20px}}
.btn-fanatics{{display:inline-block;background:linear-gradient(135deg,#7c6af7,#a78bfa);color:#fff;padding:12px 28px;border-radius:8px;font-weight:700;font-size:0.95rem;margin:4px}}
.btn-fanatics:hover{{opacity:.9;text-decoration:none}}
.btn-amazon{{display:inline-block;background:#ff9900;color:#111;padding:12px 28px;border-radius:8px;font-weight:700;font-size:0.95rem;margin:4px}}
.btn-amazon:hover{{opacity:.9;text-decoration:none}}
.back-link{{display:inline-block;margin-bottom:20px;color:var(--muted);font-size:0.88rem}}
footer{{margin-top:48px;padding-top:24px;border-top:1px solid var(--border);text-align:center;color:var(--muted);font-size:0.85rem}}
</style>
</head>
<body>
<div class="container">
<header>
  <a href="../index.html" class="logo">BJJ<span>Wiki</span></a>
  <nav style="display:flex;gap:12px">
    <a href="index.html">Techniques</a>
    <a href="../athletes.html" style="color:var(--accent2)">Athletes</a>
    <a href="../news.html">News</a>
  </nav>
</header>

<a href="../athletes.html" class="back-link">{L['back']}</a>

<div class="athlete-hero">
  <h1 class="athlete-name">{name}</h1>
  <div class="athlete-nick">"{nickname}"</div>
  <div class="athlete-meta">
    <span class="meta-badge">🌍 {athlete.get('country','').upper()}</span>
    <span class="meta-badge">🥋 Black Belt</span>
    <span class="meta-badge">⚖️ {athlete.get('weight','')}</span>
    <span class="meta-badge">🏫 {athlete.get('team','')}</span>
  </div>
  <ul class="titles-list">{titles_html}</ul>
</div>

<h2>{L['style']}</h2>
<div class="card"><p>{style_txt}</p><p style="margin-top:12px;color:var(--muted)">{sig_move}</p></div>

<h2>{L['signature']}</h2>
<div class="card">
  <p style="color:var(--muted);font-size:0.88rem;margin-bottom:12px">Click to learn each technique:</p>
  <div class="tech-tags">{tech_links_html}</div>
</div>

<h2>{L['study']}</h2>
<div class="card"><p>{why_study}</p></div>

<h2>Biography</h2>
<div class="card"><p>{bio}</p></div>

<div class="fanatics-box">
  <h3>📚 {L['instructional']}</h3>
  <p style="font-weight:700;color:var(--text);font-size:1rem">"{fanatics_title}"</p>
  <p>Learn directly from {name}'s proven systems</p>
  <a href="{fanatics_featured}" target="_blank" rel="noopener noreferrer nofollow" class="btn-fanatics">
    🎬 {L['instructional']} →
  </a>
  <a href="{fanatics_url}" target="_blank" rel="noopener noreferrer nofollow" class="btn-fanatics" style="background:linear-gradient(135deg,#1f2840,#2d3a60)">
    {L['browse']}
  </a>
  <br>
</div>

<footer>
  <p>BJJ Wiki — Free multilingual BJJ encyclopedia</p>
  <p style="margin-top:8px">· <a href="../privacy.html">Privacy Policy</a> · <a href="../about.html">About</a></p>
</footer>
</div>
</body>
</html>'''

def build_athletes_index(athletes_data, lang):
    """選手一覧ページ (athletes.html)"""
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    
    labels = {
        "en": {"title":"BJJ Athletes — Elite Competitor Profiles","desc":"Browse profiles of the world's best BJJ athletes",
               "known":"Known for","view":"View Profile →","subtitle":"Elite Competitors & Their Techniques"},
        "ja": {"title":"BJJ選手名鑑 — エリート選手プロフィール","desc":"世界トップBJJ選手のプロフィールと得意技",
               "known":"得意技","view":"プロフィールを見る →","subtitle":"エリート選手と得意技"},
        "pt": {"title":"Atletas BJJ — Perfis de Elite","desc":"Perfis dos melhores atletas de BJJ do mundo",
               "known":"Técnicas","view":"Ver Perfil →","subtitle":"Competidores Elite"},
    }
    L = labels.get(lang, labels["en"])
    
    cards = []
    for a in athletes_data:
        if not a.get("generated"): continue
        tech_tags = " ".join(
            f'<a href="{lang}/{t}.html" style="font-size:0.75rem;color:var(--muted)">{t.replace("-"," ").title()}</a>'
            for t in a["known_for"][:3]
        )
        cards.append(f'''<a href="{lang}/athlete-{a['slug']}.html" class="athlete-card">
  <div class="ac-name">{a['name']}</div>
  <div class="ac-nick" style="color:var(--muted);font-size:0.85rem">"{a.get('nickname','')}"</div>
  <div style="margin:8px 0;font-size:0.78rem;color:var(--accent2)">{a.get('team','')}</div>
  <div style="font-size:0.75rem;color:var(--muted)">{L['known']}: {', '.join(t.replace('-',' ').title() for t in a['known_for'][:3])}</div>
  <div class="ac-cta">{L['view']}</div>
</a>''')
    
    cards_html = "\n".join(cards)
    
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{L['title']} | BJJ Wiki</title>
<meta name="description" content="{L['desc']}">
<meta property="og:title" content="{L['title']}">
    <meta property="og:site_name" content="BJJ Wiki">
<meta property="og:image" content="{SITE_URL}/og-image.svg">
<link rel="canonical" href="{SITE_URL}/athletes.html">
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE}" crossorigin="anonymous"></script>
<style>
:root{{--bg:#080b12;--card:#141926;--border:#1f2840;--text:#e8eaf6;--muted:#6b7699;--accent:#7c6af7;--accent2:#a78bfa}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,sans-serif;line-height:1.7;padding:0 16px}}
a{{color:var(--accent2);text-decoration:none}}
.container{{max-width:1000px;margin:0 auto;padding-bottom:80px}}
header{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;padding:20px 0;border-bottom:1px solid var(--border);margin-bottom:32px}}
.logo{{font-size:1.3rem;font-weight:800;color:var(--text)}}.logo span{{color:var(--accent)}}
h1{{font-size:2rem;font-weight:800;margin-bottom:8px}}
.athletes-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;margin-top:24px}}
.athlete-card{{display:block;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;transition:border-color .2s;color:var(--text)}}
.athlete-card:hover{{border-color:var(--accent);text-decoration:none}}
.ac-name{{font-size:1.1rem;font-weight:700;margin-bottom:2px}}
.ac-cta{{margin-top:14px;color:var(--accent);font-size:0.85rem;font-weight:600}}
footer{{margin-top:48px;padding-top:24px;border-top:1px solid var(--border);text-align:center;color:var(--muted);font-size:0.85rem}}
</style>
</head>
<body>
<div class="container">
<header>
  <a href="index.html" class="logo">BJJ<span>Wiki</span></a>
  <nav style="display:flex;gap:12px">
    <a href="en/index.html">Techniques</a>
    <a href="athletes.html" style="color:var(--accent2)">Athletes</a>
    <a href="news.html">News</a>
  </nav>
</header>
<h1>{L['title']}</h1>
<p style="color:var(--muted);margin-bottom:8px">{L['subtitle']}</p>
<div class="athletes-grid">{cards_html}</div>
<footer><p>BJJ Wiki — Free multilingual BJJ encyclopedia</p></footer>
</div>
</body>
</html>'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--regen", action="store_true")
    args = parser.parse_args()
    
    secrets = load_secrets()
    api_key = os.environ.get("GEMINI_API_KEY") or secrets.get("GEMINI_API_KEY","")
    if not api_key:
        print("❌ GEMINI_API_KEY required"); return
    
    cache_file = os.path.join(BASE, "cache", "athletes_cache.json")
    cache = {}
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            cache = json.load(f)
    
    todo = [a for a in ATHLETES if a["slug"] not in cache or args.regen][:args.limit]
    print(f"🥋 Generating {len(todo)} athlete profiles...")
    
    athletes_data = []
    for athlete in ATHLETES:
        slug = athlete["slug"]
        if slug in cache and not args.regen:
            athlete["generated"] = True
            athletes_data.append(athlete)
            continue
        
        print(f"  {athlete['name']}...")
        for lang in ["en","ja","pt"]:
            out_dir = os.path.join(BASE, lang)
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"athlete-{slug}.html")
            if os.path.exists(out_path) and not args.regen:
                continue
            content = generate_athlete_content(athlete, lang, api_key)
            if not content:
                content = {"title":f"{athlete['name']} BJJ Profile","meta":"","bio":"","style":"","signature_move":"","why_study":""}
            html = build_athlete_html(athlete, content, lang)
            with open(out_path,"w",encoding="utf-8") as f:
                f.write(html)
            print(f"    ✅ {lang}/athlete-{slug}.html")
            time.sleep(1)
        
        cache[slug] = True
        athlete["generated"] = True
        athletes_data.append(athlete)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    
    # athletes.html 生成（英語版をルートに）
    idx_html = build_athletes_index(athletes_data, "en")
    with open(os.path.join(BASE,"athletes.html"),"w",encoding="utf-8") as f:
        f.write(idx_html)
    print(f"✅ athletes.html generated")
    
    # sitemap更新
    sitemap_path = os.path.join(BASE,"sitemap.xml")
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(sitemap_path):
        with open(sitemap_path) as f:
            sitemap = f.read()
        new_entries = []
        if "athletes.html" not in sitemap:
            new_entries.append(f"  <url><loc>{SITE_URL}/athletes.html</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>")
        for a in athletes_data:
            for lang in ["en","ja","pt"]:
                u = f"{SITE_URL}/{lang}/athlete-{a['slug']}.html"
                if u not in sitemap:
                    new_entries.append(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>")
        if new_entries:
            sitemap = sitemap.replace("</urlset>", "\n".join(new_entries)+"\n</urlset>")
            with open(sitemap_path,"w",encoding="utf-8") as f:
                f.write(sitemap)
            print(f"✅ sitemap updated (+{len(new_entries)} URLs)")
    
    print(f"\n完了: {len([a for a in athletes_data if a.get('generated')])}選手のプロフィール生成済み")

if __name__ == "__main__":
    main()
