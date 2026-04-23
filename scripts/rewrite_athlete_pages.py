#!/usr/bin/env python3
"""
BJJ アスリートページ 一括リライト
- Gemini Flash で 1000語+ の高品質コンテンツ生成
- 25選手 × en/ja/pt = 75ページ
- アフィリリンクなし / CTA はアプリ登録のみ
"""
import os, json, time, datetime, urllib.request, re, argparse, sys

BASE     = os.path.dirname(__file__) + "/.."
SITE_URL = "https://wiki.bjj-app.net"
GA4_ID   = "G-7LM8L3TRZM"
ADSENSE  = "ca-pub-5529701423220352"
APP_URL  = "https://bjj-app.net/login"

ATHLETES = [
    {
        "slug": "gordon-ryan",
        "name": "Gordon Ryan",
        "nickname": "The King",
        "country": "US",
        "belt": "black",
        "team": "New Wave Jiu-Jitsu",
        "weight": "Heavyweight",
        "known_for": ["rear-naked-choke","heel-hook","inside-heel-hook","darce-choke","back-mount","leg-entanglement"],
        "titles": ["ADCC Absolute Champion 2017, 2019, 2022", "ADCC +99kg Champion 2017, 2019", "EBI Champion", "WNO Champion"],
        "born": "1995",
        "nationality": "American",
    },
    {
        "slug": "mikey-musumeci",
        "name": "Mikey Musumeci",
        "nickname": "Darth Rigatoni",
        "country": "US",
        "belt": "black",
        "team": "New Wave Jiu-Jitsu",
        "weight": "Flyweight / Strawweight",
        "known_for": ["triangle-choke","omoplata","lasso-guard","rubber-guard","spider-guard","berimbolo"],
        "titles": ["ADCC 57kg Champion 2022", "IBJJF World Champion 5x", "ONE Championship MMA debut winner"],
        "born": "1996",
        "nationality": "American",
    },
    {
        "slug": "craig-jones",
        "name": "Craig Jones",
        "nickname": "El Monstro",
        "country": "AU",
        "belt": "black",
        "team": "B-Team",
        "weight": "Middleweight",
        "known_for": ["heel-hook","outside-heel-hook","knee-bar","50-50-guard","triangle-choke","leg-entanglement"],
        "titles": ["ADCC 2017 Superfight Winner", "WNO Champion multiple times", "B-Team founder"],
        "born": "1993",
        "nationality": "Australian",
    },
    {
        "slug": "john-danaher",
        "name": "John Danaher",
        "nickname": "The Professor",
        "country": "NZ",
        "belt": "black",
        "team": "New Wave Jiu-Jitsu",
        "weight": "N/A (Coach)",
        "known_for": ["heel-hook","rear-naked-choke","back-mount","leg-entanglement","arm-triangle-choke"],
        "titles": ["Head coach of Gordon Ryan (ADCC 3x)", "Developed the modern leg lock system", "Renzo Gracie Academy head instructor"],
        "born": "1967",
        "nationality": "New Zealander",
    },
    {
        "slug": "marcelo-garcia",
        "name": "Marcelo Garcia",
        "nickname": "MG",
        "country": "BR",
        "belt": "black",
        "team": "Marcelo Garcia Academy (NYC)",
        "weight": "Lightweight / Middleweight",
        "known_for": ["guillotine-choke","rear-naked-choke","butterfly-guard","x-guard","anaconda-choke","arm-drag"],
        "titles": ["ADCC Champion 2003, 2005, 2007, 2009", "IBJJF World Champion 5x", "Greatest pound-for-pound grappler of his era"],
        "born": "1983",
        "nationality": "Brazilian",
    },
    {
        "slug": "bernardo-faria",
        "name": "Bernardo Faria",
        "nickname": "The Half Guard King",
        "country": "BR",
        "belt": "black",
        "team": "Alliance",
        "weight": "Super Heavyweight",
        "known_for": ["half-guard","deep-half-guard","double-under-pass","omoplata","scissor-sweep"],
        "titles": ["IBJJF World Champion 5x", "ADCC Champion 2015", "Pan American Champion 4x"],
        "born": "1987",
        "nationality": "Brazilian",
    },
    {
        "slug": "andre-galvao",
        "name": "Andre Galvao",
        "nickname": "Buchecha's rival / ATOS chief",
        "country": "BR",
        "belt": "black",
        "team": "ATOS Jiu-Jitsu",
        "weight": "Middleweight / Light Heavyweight",
        "known_for": ["rear-naked-choke","arm-drag","double-leg","back-mount","takedowns"],
        "titles": ["ADCC Champion 2011, 2013", "IBJJF World Champion 8x", "ATOS head instructor"],
        "born": "1985",
        "nationality": "Brazilian",
    },
    {
        "slug": "caio-terra",
        "name": "Caio Terra",
        "nickname": "The Lightweight Master",
        "country": "BR",
        "belt": "black",
        "team": "Caio Terra Association",
        "weight": "Rooster / Light Feather",
        "known_for": ["triangle-choke","omoplata","inverted-guard","spider-guard","berimbolo"],
        "titles": ["IBJJF World Champion 8x", "Most decorated lightweight in IBJJF history"],
        "born": "1986",
        "nationality": "Brazilian",
    },
    {
        "slug": "keenan-cornelius",
        "name": "Keenan Cornelius",
        "nickname": "The Lapel Guard Inventor",
        "country": "US",
        "belt": "black",
        "team": "Legion AJJ (founder)",
        "weight": "Middleweight",
        "known_for": ["worm-guard","lapel-guard","triangle-choke","armbar","berimbolo"],
        "titles": ["ADCC Finalist 2013, 2015", "IBJJF World Champion (brown belt)", "Pioneer of lapel guard systems"],
        "born": "1993",
        "nationality": "American",
    },
    {
        "slug": "xande-ribeiro",
        "name": "Xande Ribeiro",
        "nickname": "The Rock",
        "country": "BR",
        "belt": "black",
        "team": "Unity Jiu-Jitsu",
        "weight": "Super Heavyweight",
        "known_for": ["rear-naked-choke","arm-triangle-choke","armbar","side-control","smash-pass"],
        "titles": ["ADCC Champion 2005, 2007", "IBJJF World Champion 6x", "Multiple weight + absolute titles"],
        "born": "1981",
        "nationality": "Brazilian",
    },
    {
        "slug": "xande-ribeiro-2",
        "name": "Saulo Ribeiro",
        "nickname": "The Professor / Xande's brother",
        "country": "BR",
        "belt": "black",
        "team": "University of Jiu-Jitsu (San Diego)",
        "weight": "Middleweight / Light Heavyweight",
        "known_for": ["armbar","rear-naked-choke","half-guard","pressure-passing","survival-defense"],
        "titles": ["IBJJF World Champion 6x", "ADCC Champion 2003", "Author of 'Jiu-Jitsu University'"],
        "born": "1974",
        "nationality": "Brazilian",
    },
    {
        "slug": "garry-tonon",
        "name": "Garry Tonon",
        "nickname": "The Lion Killer",
        "country": "US",
        "belt": "black",
        "team": "Renzo Gracie / New Wave",
        "weight": "Lightweight",
        "known_for": ["heel-hook","guillotine-choke","leg-entanglement","kneebar","rear-naked-choke"],
        "titles": ["EBI Champion", "ADCC silver medalist 2015", "ONE Championship MMA 10-0"],
        "born": "1994",
        "nationality": "American",
    },
    {
        "slug": "mackenzie-dern",
        "name": "Mackenzie Dern",
        "nickname": "The Brazilian American",
        "country": "US",
        "belt": "black",
        "team": "Alliance",
        "weight": "Strawweight",
        "known_for": ["triangle-choke","armbar","rear-naked-choke","omoplata","guard-game"],
        "titles": ["IBJJF World Champion 3x", "ADCC silver medalist", "UFC fighter (strawweight)"],
        "born": "1993",
        "nationality": "American-Brazilian",
    },
    {
        "slug": "ffion-davies",
        "name": "Ffion Davies",
        "nickname": "The Welsh Wizard",
        "country": "GB",
        "belt": "black",
        "team": "10th Planet Jiu-Jitsu",
        "weight": "Featherweight",
        "known_for": ["heel-hook","leg-entanglement","50-50-guard","triangle-choke","arm-lock"],
        "titles": ["ADCC 60kg Champion 2022", "EBI Champion", "IBJJF European Champion"],
        "born": "1996",
        "nationality": "Welsh / British",
    },
    {
        "slug": "rafael-lovato-jr",
        "name": "Rafael Lovato Jr.",
        "nickname": "The American",
        "country": "US",
        "belt": "black",
        "team": "Lovato Jiu-Jitsu",
        "weight": "Middleweight",
        "known_for": ["armbar","rear-naked-choke","triangle-choke","side-control","guard-passing"],
        "titles": ["IBJJF World Champion", "ADCC Champion 2009", "WBO middleweight boxing-related notes (separate career)"],
        "born": "1984",
        "nationality": "American",
    },
    {
        "slug": "romulo-barral",
        "name": "Romulo Barral",
        "nickname": "Romulinho",
        "country": "BR",
        "belt": "black",
        "team": "Gracie Barra",
        "weight": "Middleweight / Light Heavyweight",
        "known_for": ["spider-guard","lasso-guard","triangle-choke","omoplata","guard-game"],
        "titles": ["IBJJF World Champion 5x", "ADCC silver 2009", "Gracie Barra champion"],
        "born": "1982",
        "nationality": "Brazilian",
    },
    {
        "slug": "claudio-calasans",
        "name": "Claudio Calasans",
        "nickname": "The Middleweight Beast",
        "country": "BR",
        "belt": "black",
        "team": "Atos Jiu-Jitsu",
        "weight": "Middleweight",
        "known_for": ["rear-naked-choke","armbar","side-control","guard-passing","takedowns"],
        "titles": ["ADCC Champion 2013 (88kg)", "IBJJF World Champion", "Pan American Champion"],
        "born": "1986",
        "nationality": "Brazilian",
    },
    {
        "slug": "nicky-ryan",
        "name": "Nicky Ryan",
        "nickname": "The Prodigy",
        "country": "US",
        "belt": "black",
        "team": "New Wave Jiu-Jitsu",
        "weight": "Lightweight / Featherweight",
        "known_for": ["heel-hook","leg-entanglement","50-50-guard","back-mount","rear-naked-choke"],
        "titles": ["Youngest ADCC finalist (16 years old, 2017)", "WNO Champion", "Gordon Ryan's brother"],
        "born": "2001",
        "nationality": "American",
    },
    {
        "slug": "bia-mesquita",
        "name": "Bia Mesquita",
        "nickname": "La Princesa",
        "country": "BR",
        "belt": "black",
        "team": "Gracie Humaitá / Soul Fighters",
        "weight": "Lightweight / Featherweight",
        "known_for": ["triangle-choke","armbar","guard-game","omoplata","collar-choke"],
        "titles": ["IBJJF World Champion 8x", "ADCC Champion 2013, 2015", "Most decorated female grappler of her era"],
        "born": "1988",
        "nationality": "Brazilian",
    },
    {
        "slug": "buchecha",
        "name": "Marcus Buchecha Almeida",
        "nickname": "Buchecha",
        "country": "BR",
        "belt": "black",
        "team": "Check Mat",
        "weight": "Ultra Heavyweight",
        "known_for": ["armbar","rear-naked-choke","double-leg","guard-passing","pressure-game"],
        "titles": ["IBJJF World Champion 13x", "ADCC Absolute Champion 2013", "ONE Championship MMA debut"],
        "born": "1990",
        "nationality": "Brazilian",
    },
    {
        "slug": "cobrinha",
        "name": "Rubens Charles Maciel",
        "nickname": "Cobrinha (The Snake)",
        "country": "BR",
        "belt": "black",
        "team": "Alliance / Cobrinha BJJ",
        "weight": "Featherweight / Light Feather",
        "known_for": ["berimbolo","spider-guard","triangle-choke","inverted-guard","omoplata"],
        "titles": ["IBJJF World Champion 6x", "ADCC Champion 2007, 2009, 2011", "Pioneer of berimbolo"],
        "born": "1978",
        "nationality": "Brazilian",
    },
    {
        "slug": "gianni-grippo",
        "name": "Gianni Grippo",
        "nickname": "The New York Kid",
        "country": "US",
        "belt": "black",
        "team": "Marcelo Garcia Academy",
        "weight": "Lightweight / Featherweight",
        "known_for": ["berimbolo","back-mount","triangle-choke","x-guard","guard-game"],
        "titles": ["IBJJF World Champion", "Multiple Pan American titles", "Trained under Marcelo Garcia"],
        "born": "1993",
        "nationality": "American",
    },
    {
        "slug": "lachlan-giles",
        "name": "Lachlan Giles",
        "nickname": "The Australian Heel Hook Specialist",
        "country": "AU",
        "belt": "black",
        "team": "Absolute MMA (Melbourne)",
        "weight": "Featherweight / Lightweight",
        "known_for": ["heel-hook","inside-heel-hook","50-50-guard","leg-entanglement","back-mount"],
        "titles": ["ADCC 2019 Absolute bronze (submitted 3 heavyweights)", "WNO Champion", "Podcast host & coach"],
        "born": "1991",
        "nationality": "Australian",
    },
    {
        "slug": "leandro-lo",
        "name": "Leandro Lo",
        "nickname": "Lo",
        "country": "BR",
        "belt": "black",
        "team": "NS Brotherhood / Cicero Costha",
        "weight": "Lightweight to Super Heavyweight (won 5 different weight classes)",
        "known_for": ["leg-drag","knee-slice","back-mount","rear-naked-choke","guard-passing"],
        "titles": ["IBJJF World Champion 8x (5 different weight classes)", "Known as the greatest IBJJF competitor ever"],
        "born": "1991",
        "nationality": "Brazilian",
    },
    {
        "slug": "rafael-mendes",
        "name": "Rafael Mendes",
        "nickname": "Rafa / The Berimbolo Master",
        "country": "BR",
        "belt": "black",
        "team": "Art of Jiu-Jitsu (founder)",
        "weight": "Featherweight",
        "known_for": ["berimbolo","back-mount","triangle-choke","leg-drag","omoplata"],
        "titles": ["IBJJF World Champion 6x", "ADCC Champion 2011, 2013", "Co-founder of Art of Jiu-Jitsu"],
        "born": "1990",
        "nationality": "Brazilian",
    },
]

GEMINI_MODELS = ["gemini-2.0-flash", "gemini-1.5-flash"]

def gemini_call(prompt, api_key):
    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        data = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
        }).encode()
        req = urllib.request.Request(url, data=data,
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                res = json.loads(r.read())
            return res["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"    [{model}] error: {e}")
            continue
    return None

def generate_content(athlete, lang, api_key):
    lang_label = {"en": "English", "ja": "Japanese", "pt": "Brazilian Portuguese"}[lang]
    name = athlete["name"]
    nickname = athlete.get("nickname", "")
    titles = athlete.get("titles", [])
    known_for = athlete.get("known_for", [])
    team = athlete.get("team", "")
    nationality = athlete.get("nationality", "")
    born = athlete.get("born", "")
    weight = athlete.get("weight", "")

    prompt = f"""You are writing a comprehensive BJJ encyclopedia article about {name} ("{nickname}") in {lang_label}.

Athlete facts:
- Nationality: {nationality}, Born: {born}
- Team: {team}
- Weight class: {weight}
- Major titles: {'; '.join(titles)}
- Signature techniques: {', '.join(known_for)}

Write a LONG, detailed, high-quality BJJ encyclopedia article. The total content should be at least 900 words.

Return ONLY valid JSON (no markdown, no code blocks):
{{
  "title": "SEO page title under 65 chars with athlete name",
  "meta": "Meta description 140-160 chars with athlete name and key achievements",
  "intro": "Opening paragraph (80-100 words) introducing the athlete's significance in BJJ",
  "biography": "Full biography (300-400 words) covering: early life, BJJ beginnings, rise to prominence, major championship moments, and legacy. Write in engaging encyclopedia style with specific competition results and years.",
  "style_analysis": "Deep analysis of fighting style (150-200 words): how they approach the match, guard game, passing game, submission preferences, and what makes them distinctive",
  "signature_technique": "Describe their most iconic technique in detail (80-100 words): what it is, how they use it, why it's effective in their system",
  "why_study": "Why practitioners should study this athlete (100-120 words): what specific skills and concepts students can learn, appropriate skill levels",
  "career_highlights": ["3-5 specific notable match/competition highlights as array of strings, each 30-50 words"],
  "training_tips": ["3-4 actionable training tips inspired by this athlete's style, each 30-50 words"],
  "faq": [
    {{"q": "First frequently asked question about this athlete", "a": "Detailed answer 50-80 words"}},
    {{"q": "Second frequently asked question", "a": "Detailed answer 50-80 words"}},
    {{"q": "Third frequently asked question", "a": "Detailed answer 50-80 words"}}
  ]
}}"""

    text = gemini_call(prompt, api_key)
    if not text:
        return None
    # JSON抽出
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    m = re.search(r'\{[\s\S]*\}', text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception as e:
            print(f"    JSON parse error: {e}")
    return None

def build_html(athlete, content, lang):
    slug = athlete["slug"]
    name = athlete["name"]
    nickname = athlete.get("nickname", "")
    titles = athlete.get("titles", [])
    known_for = athlete.get("known_for", [])
    team = athlete.get("team", "")
    weight = athlete.get("weight", "")
    country = athlete.get("country", "")

    title_tag = content.get("title", f"{name} BJJ Profile")
    meta_desc = content.get("meta", "")
    intro = content.get("intro", "")
    biography = content.get("biography", "").replace("\n", "<br><br>")
    style_analysis = content.get("style_analysis", "").replace("\n", "<br>")
    signature_technique = content.get("signature_technique", "")
    why_study = content.get("why_study", "").replace("\n", "<br>")
    career_highlights = content.get("career_highlights", [])
    training_tips = content.get("training_tips", [])
    faqs = content.get("faq", [])

    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+09:00")
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # Internal technique links
    tech_links_html = "\n".join(
        f'<a href="{t}.html" class="tech-tag">🥋 {t.replace("-"," ").title()}</a>'
        for t in known_for[:6]
    )

    # Titles list
    titles_html = "\n".join(f"<li>{t}</li>" for t in titles)

    # Career highlights
    highlights_html = "\n".join(f"<li>{h}</li>" for h in career_highlights)

    # Training tips
    tips_html = "\n".join(f"<li>{t}</li>" for t in training_tips)

    # FAQ Schema + HTML
    faq_schema = json.dumps([{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs])
    faq_html = "\n".join(
        f'''<div class="faq-item">
  <h3 class="faq-q">{f["q"]}</h3>
  <p class="faq-a">{f["a"]}</p>
</div>''' for f in faqs
    )

    # Lang nav links
    lang_nav = {
        "en": f'<a href="../../en/athlete-{slug}.html" class="{"active" if lang=="en" else ""}">🇺🇸 EN</a>',
        "ja": f'<a href="../../ja/athlete-{slug}.html" class="{"active" if lang=="ja" else ""}">🇯🇵 JA</a>',
        "pt": f'<a href="../../pt/athlete-{slug}.html" class="{"active" if lang=="pt" else ""}">🇧🇷 PT</a>',
    }
    lang_nav_html = " ".join(lang_nav.values())

    # Labels per language
    L = {
        "en": {
            "back": "← All Athletes", "bio": "Biography", "style": "Fighting Style",
            "signature": "Signature Technique", "study": "Why Study This Athlete",
            "highlights": "Career Highlights", "tips": "Training Tips",
            "faq_title": "Frequently Asked Questions",
            "cta_text": "Track your techniques & training on BJJ App",
            "cta_btn": "Start Free on BJJ App →",
            "techniques": "Signature Techniques",
        },
        "ja": {
            "back": "← 選手一覧", "bio": "経歴・バイオグラフィー", "style": "戦闘スタイル分析",
            "signature": "シグネチャーテクニック", "study": "この選手から学べること",
            "highlights": "キャリアハイライト", "tips": "トレーニングのヒント",
            "faq_title": "よくある質問",
            "cta_text": "技術とトレーニングを記録しよう",
            "cta_btn": "BJJ Appを無料で始める →",
            "techniques": "得意技・技術リンク",
        },
        "pt": {
            "back": "← Todos os Atletas", "bio": "Biografia", "style": "Análise de Estilo de Luta",
            "signature": "Técnica Assinatura", "study": "Por que Estudar Este Atleta",
            "highlights": "Destaques da Carreira", "tips": "Dicas de Treinamento",
            "faq_title": "Perguntas Frequentes",
            "cta_text": "Registre suas técnicas e treinos no BJJ App",
            "cta_btn": "Começar Grátis no BJJ App →",
            "techniques": "Técnicas Assinatura",
        },
    }[lang]

    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
  <link rel="icon" href="https://wiki.bjj-app.net/favicon.svg" type="image/svg+xml">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title_tag} | BJJ Wiki</title>
<meta name="description" content="{meta_desc}">
<meta property="og:title" content="{title_tag}">
    <meta property="og:site_name" content="BJJ Wiki">
<meta property="og:description" content="{meta_desc}">
<meta property="og:image" content="{SITE_URL}/og-image.png">
<meta property="og:url" content="{SITE_URL}/{lang}/athlete-{slug}.html">
<meta name="twitter:card" content="summary_large_image">
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
  "@context":"https://schema.org",
  "@type":"FAQPage",
  "mainEntity":{faq_schema}
}}
</script>
<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"ProfilePage",
  "name":"{title_tag}",
  "description":"{meta_desc}",
  "url":"{SITE_URL}/{lang}/athlete-{slug}.html",
  "datePublished":"2026-03-30T00:00:00+09:00",
  "dateModified":"{now}",
  "mainEntity":{{
    "@type":"Person",
    "name":"{name}",
    "jobTitle":"Brazilian Jiu-Jitsu Athlete",
    "affiliation":"{team}"
  }}
}}
</script>
<style>
:root{{--bg:#0f172a;--card:#141926;--border:#1e293b;--text:#e2e8f0;--muted:#64748b;--accent:#e94560;--accent2:#a78bfa}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:16px;line-height:1.8;padding:0 16px}}
a{{color:var(--accent2);text-decoration:none}}a:hover{{text-decoration:underline}}
.container{{max-width:860px;margin:0 auto;padding-bottom:80px}}
header{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;padding:16px 0;border-bottom:1px solid var(--border);margin-bottom:24px}}
.logo{{font-size:1.2rem;font-weight:800;color:var(--accent);letter-spacing:-0.02em}}
.lang-nav{{display:flex;gap:8px}}
.lang-nav a{{color:var(--muted);font-size:.82rem;padding:4px 10px;border-radius:4px;border:1px solid var(--border)}}
.lang-nav a.active,.lang-nav a:hover{{color:var(--text);border-color:var(--accent)}}
.breadcrumb{{font-size:.78rem;color:var(--muted);margin-bottom:16px}}
.breadcrumb a{{color:var(--muted)}}
.hero{{background:linear-gradient(135deg,rgba(233,69,96,0.08),rgba(167,139,250,0.06));border:1px solid var(--border);border-radius:16px;padding:28px;margin-bottom:28px}}
.hero h1{{font-size:2rem;font-weight:800;margin-bottom:4px;color:var(--text)}}
.hero .nick{{color:var(--accent2);font-size:1rem;margin-bottom:14px}}
.badges{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}}
.badge{{background:#1e293b;color:var(--muted);font-size:.75rem;padding:3px 10px;border-radius:20px}}
.titles-list{{list-style:none;padding:0}}
.titles-list li{{padding:3px 0;color:#f59e0b;font-size:.9rem}}
.titles-list li::before{{content:"🏆 "}}
h2{{font-size:.88rem;font-weight:700;color:var(--accent2);text-transform:uppercase;letter-spacing:.07em;margin:28px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--border)}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px;font-size:.95rem;line-height:1.8}}
.tech-tags{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}}
.tech-tag{{display:inline-block;padding:5px 12px;background:#1e293b;border:1px solid var(--accent2);border-radius:20px;font-size:.8rem;color:var(--accent2);font-weight:600}}
.tech-tag:hover{{background:var(--accent2);color:#0f172a;text-decoration:none}}
ul.highlights,ul.tips{{padding-left:20px;margin:0}}
ul.highlights li,ul.tips li{{margin-bottom:10px;font-size:.93rem}}
.faq-item{{border-bottom:1px solid var(--border);padding:16px 0}}
.faq-item:last-child{{border-bottom:none}}
.faq-q{{font-size:.95rem;font-weight:700;color:var(--text);margin-bottom:8px}}
.faq-a{{font-size:.9rem;color:var(--muted);line-height:1.7}}
.cta-box{{background:linear-gradient(135deg,rgba(233,69,96,0.12),rgba(167,139,250,0.08));border:1px solid rgba(233,69,96,0.4);border-radius:16px;padding:24px;text-align:center;margin:28px 0}}
.cta-box p{{color:var(--muted);margin-bottom:14px;font-size:.95rem}}
.cta-btn{{display:inline-block;background:var(--accent);color:#fff;padding:12px 28px;border-radius:8px;font-weight:700;font-size:.95rem;text-decoration:none}}
.cta-btn:hover{{opacity:.9;text-decoration:none}}
footer{{margin-top:48px;padding-top:16px;border-top:1px solid var(--border);text-align:center;color:var(--muted);font-size:.78rem;line-height:1.6}}
@media(max-width:600px){{.hero h1{{font-size:1.5rem}}}}
</style>
</head>
<body>
<div class="container">

<header>
  <a href="../index.html" class="logo">🥋 BJJ Wiki</a>
  <div class="lang-nav">{lang_nav_html}</div>
</header>

<div class="breadcrumb">
  <a href="../index.html">BJJ Wiki</a> / <a href="../athletes.html">Athletes</a> / {name}
</div>

<div class="hero">
  <h1>{name}</h1>
  <div class="nick">"{nickname}"</div>
  <div class="badges">
    <span class="badge">🌍 {country}</span>
    <span class="badge">🥋 Black Belt</span>
    <span class="badge">⚖️ {weight}</span>
    <span class="badge">🏫 {team}</span>
  </div>
  <ul class="titles-list">{titles_html}</ul>
</div>

<p class="card" style="font-size:1rem">{intro}</p>

<h2>{L["bio"]}</h2>
<div class="card"><p>{biography}</p></div>

<h2>{L["style"]}</h2>
<div class="card"><p>{style_analysis}</p></div>

<h2>{L["signature"]}</h2>
<div class="card"><p>{signature_technique}</p>
<div class="tech-tags">{tech_links_html}</div>
</div>

<h2>{L["study"]}</h2>
<div class="card"><p>{why_study}</p></div>

<h2>{L["highlights"]}</h2>
<div class="card"><ul class="highlights">{highlights_html}</ul></div>

<h2>{L["tips"]}</h2>
<div class="card"><ul class="tips">{tips_html}</ul></div>

<h2>{L["faq_title"]}</h2>
<div class="card">{faq_html}</div>

<div class="cta-box">
  <p>{L["cta_text"]}</p>
  <a href="{APP_URL}" class="cta-btn">{L["cta_btn"]}</a>
</div>

<footer>
  <p>BJJ Wiki — Free multilingual BJJ encyclopedia</p>
  <p style="margin-top:6px">Last updated: {today} · <a href="../privacy.html">Privacy</a> · <a href="../about.html">About</a></p>
</footer>

</div>
</body>
</html>'''

def main():
    parser = argparse.ArgumentParser(description="Rewrite BJJ athlete pages with Gemini")
    parser.add_argument("--api-key", default=os.environ.get("GEMINI_API_KEY", ""))
    parser.add_argument("--limit", type=int, default=3, help="Number of athletes to process")
    parser.add_argument("--all", action="store_true", help="Process all athletes")
    parser.add_argument("--slug", help="Process a specific athlete by slug")
    parser.add_argument("--langs", default="en,ja,pt", help="Languages to generate (comma-separated)")
    args = parser.parse_args()

    api_key = args.api_key
    if not api_key:
        print("❌ Gemini API key required. Use --api-key or set GEMINI_API_KEY env var")
        sys.exit(1)

    langs = args.langs.split(",")
    cache_file = os.path.join(BASE, "cache", "athlete_rewrite_cache.json")
    cache = {}
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            cache = json.load(f)

    if args.slug:
        todo = [a for a in ATHLETES if a["slug"] == args.slug]
    elif args.all:
        todo = ATHLETES
    else:
        todo = [a for a in ATHLETES if a["slug"] not in cache][:args.limit]

    print(f"🥋 Processing {len(todo)} athletes × {len(langs)} languages = {len(todo)*len(langs)} pages\n")

    success = 0
    for athlete in todo:
        slug = athlete["slug"]
        name = athlete["name"]
        print(f"👤 {name} ({slug})")

        for lang in langs:
            out_dir = os.path.join(BASE, lang)
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"athlete-{slug}.html")

            print(f"  [{lang}] Generating...", end=" ", flush=True)
            content = generate_content(athlete, lang, api_key)
            if not content:
                print("❌ FAILED (using fallback)")
                content = {
                    "title": f"{name} BJJ Profile | BJJ Wiki",
                    "meta": f"{name} is a world-class BJJ athlete known for {', '.join(athlete['known_for'][:3])}.",
                    "intro": f"{name} is one of the most decorated Brazilian Jiu-Jitsu competitors in the world.",
                    "biography": f"{name} has built a legendary career in BJJ, winning numerous world championships.",
                    "style_analysis": f"{name} is known for a highly effective game based on {', '.join(athlete['known_for'][:3])}.",
                    "signature_technique": f"Their most famous technique is {athlete['known_for'][0].replace('-', ' ')}.",
                    "why_study": f"Studying {name}'s game will improve your {athlete['known_for'][0].replace('-', ' ')} significantly.",
                    "career_highlights": athlete.get("titles", []),
                    "training_tips": [f"Study {athlete['known_for'][0].replace('-', ' ')} deeply", "Focus on fundamentals"],
                    "faq": [{"q": f"What is {name} known for?", "a": f"Known for {', '.join(athlete['known_for'][:3])}."}]
                }

            html = build_html(athlete, content, lang)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
            words = len(re.findall(r'\w+', re.sub(r'<[^>]+>', '', html)))
            print(f"✅ {words} words")
            time.sleep(0.5)  # Rate limit respect

        cache[slug] = {"done": True, "ts": datetime.datetime.now().isoformat()}
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
        success += 1
        print()

    print(f"\n✅ Done: {success}/{len(todo)} athletes, {success*len(langs)} pages written")
    print(f"Next: cd ~/Claude/bjj-wiki && git add -A && git commit -m 'feat: rewrite athlete pages with Gemini (1000+ words)' && git push")

if __name__ == "__main__":
    main()
