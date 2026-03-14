#!/usr/bin/env python3
"""
BJJ Wiki - 多言語柔術技辞典 自動生成スクリプト
- Gemini APIで英語/日本語/ポルトガル語の技解説記事を生成
- 静的HTMLとしてGitHub Pagesにデプロイ
"""

import os, json, time, datetime, urllib.request, urllib.error, re

# ===== ~/.secrets からAPIキーを補完 =====
def _load_secrets():
    path = os.path.expanduser("~/.secrets")
    if not os.path.exists(path): return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            line = line.removeprefix("export").strip()
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
_load_secrets()

# ===== 設定 =====
IS_CI          = os.environ.get("GITHUB_ACTIONS") == "true"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SITE_DIR       = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if IS_CI else os.path.expanduser("~/Claude/bjj-wiki")
SITE_URL       = "https://YOUR_USERNAME.github.io/bjj-wiki"  # ← GitHub Pages URL に変更

LANGUAGES = {
    "en": {"name": "English",    "dir": "en"},
    "ja": {"name": "日本語",      "dir": "ja"},
    "pt": {"name": "Português",  "dir": "pt"},
}

# ===== 技リスト（初期50技）=====
TECHNIQUES = [
    # ガード系
    {"slug": "closed-guard",        "name": "Closed Guard",        "category": "Guard"},
    {"slug": "open-guard",          "name": "Open Guard",          "category": "Guard"},
    {"slug": "half-guard",          "name": "Half Guard",          "category": "Guard"},
    {"slug": "spider-guard",        "name": "Spider Guard",        "category": "Guard"},
    {"slug": "de-la-riva-guard",    "name": "De La Riva Guard",    "category": "Guard"},
    {"slug": "berimbolo",           "name": "Berimbolo",           "category": "Guard"},
    {"slug": "butterfly-guard",     "name": "Butterfly Guard",     "category": "Guard"},
    {"slug": "rubber-guard",        "name": "Rubber Guard",        "category": "Guard"},
    {"slug": "x-guard",             "name": "X-Guard",             "category": "Guard"},
    {"slug": "worm-guard",          "name": "Worm Guard",          "category": "Guard"},
    # パス系
    {"slug": "guard-pass",          "name": "Guard Pass",          "category": "Passing"},
    {"slug": "torreando-pass",      "name": "Torreando Pass",      "category": "Passing"},
    {"slug": "knee-slice-pass",     "name": "Knee Slice Pass",     "category": "Passing"},
    {"slug": "leg-drag-pass",       "name": "Leg Drag Pass",       "category": "Passing"},
    {"slug": "headquarters-pass",   "name": "Headquarters Pass",   "category": "Passing"},
    # テイクダウン
    {"slug": "double-leg-takedown", "name": "Double Leg Takedown", "category": "Takedown"},
    {"slug": "single-leg-takedown", "name": "Single Leg Takedown", "category": "Takedown"},
    {"slug": "osoto-gari",          "name": "Osoto Gari",          "category": "Takedown"},
    {"slug": "ankle-pick",          "name": "Ankle Pick",          "category": "Takedown"},
    # 絞め技
    {"slug": "rear-naked-choke",    "name": "Rear Naked Choke",    "category": "Choke"},
    {"slug": "triangle-choke",      "name": "Triangle Choke",      "category": "Choke"},
    {"slug": "guillotine-choke",    "name": "Guillotine Choke",    "category": "Choke"},
    {"slug": "bow-and-arrow-choke", "name": "Bow and Arrow Choke", "category": "Choke"},
    {"slug": "ezekiel-choke",       "name": "Ezekiel Choke",       "category": "Choke"},
    {"slug": "darce-choke",         "name": "D'Arce Choke",        "category": "Choke"},
    {"slug": "anaconda-choke",      "name": "Anaconda Choke",      "category": "Choke"},
    {"slug": "loop-choke",          "name": "Loop Choke",          "category": "Choke"},
    # 関節技
    {"slug": "armbar",              "name": "Armbar",              "category": "Joint Lock"},
    {"slug": "kimura",              "name": "Kimura",              "category": "Joint Lock"},
    {"slug": "americana",           "name": "Americana",           "category": "Joint Lock"},
    {"slug": "omoplata",            "name": "Omoplata",            "category": "Joint Lock"},
    {"slug": "wrist-lock",          "name": "Wrist Lock",          "category": "Joint Lock"},
    {"slug": "heel-hook",           "name": "Heel Hook",           "category": "Leg Lock"},
    {"slug": "inside-heel-hook",    "name": "Inside Heel Hook",    "category": "Leg Lock"},
    {"slug": "outside-heel-hook",   "name": "Outside Heel Hook",   "category": "Leg Lock"},
    {"slug": "knee-bar",            "name": "Knee Bar",            "category": "Leg Lock"},
    {"slug": "toe-hold",            "name": "Toe Hold",            "category": "Leg Lock"},
    {"slug": "calf-slicer",         "name": "Calf Slicer",         "category": "Leg Lock"},
    # ポジション
    {"slug": "mount",               "name": "Mount",               "category": "Position"},
    {"slug": "back-mount",          "name": "Back Mount",          "category": "Position"},
    {"slug": "side-control",        "name": "Side Control",        "category": "Position"},
    {"slug": "north-south",         "name": "North-South",         "category": "Position"},
    {"slug": "knee-on-belly",       "name": "Knee on Belly",       "category": "Position"},
    # スイープ
    {"slug": "scissor-sweep",       "name": "Scissor Sweep",       "category": "Sweep"},
    {"slug": "flower-sweep",        "name": "Flower Sweep",        "category": "Sweep"},
    {"slug": "hip-bump-sweep",      "name": "Hip Bump Sweep",      "category": "Sweep"},
    {"slug": "pendulum-sweep",      "name": "Pendulum Sweep",      "category": "Sweep"},
    # その他
    {"slug": "backtake",            "name": "Back Take",           "category": "Transition"},
    {"slug": "turtle-position",     "name": "Turtle Position",     "category": "Position"},
    {"slug": "sprawl",              "name": "Sprawl",              "category": "Defense"},
]

# ===== Gemini API（複数モデルフォールバック）=====
def call_gemini(prompt):
    models = [
        ("gemini-2.5-flash",        "v1beta"),
        ("gemini-2.0-flash",        "v1beta"),
        ("gemini-2.0-flash",        "v1"),
        ("gemini-2.0-flash-lite-001","v1beta"),
        ("gemini-1.5-flash-latest", "v1beta"),
    ]
    data = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
    }).encode()
    for model, api_ver in models:
        url = f"https://generativelanguage.googleapis.com/{api_ver}/models/{model}:generateContent?key={GEMINI_API_KEY}"
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=60) as res:
                    result = json.loads(res.read())
                    text   = result["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"[OK] [{model}] 生成成功")
                    return text
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(30 * (attempt + 1))
                else:
                    print(f"[{model}] HTTP {e.code} → 次のモデルへ"); break
            except Exception as e:
                print(f"[{model}] エラー: {e}"); break
    return None

# ===== 記事生成プロンプト =====
def build_article_prompt(technique, lang_code):
    lang_instructions = {
        "en": "Write in English.",
        "ja": "日本語で書いてください。",
        "pt": "Escreva em Português brasileiro.",
    }
    instruction = lang_instructions[lang_code]
    return f"""You are an expert Brazilian Jiu-Jitsu instructor and SEO content writer.
{instruction}

Write a comprehensive BJJ technique guide for: **{technique['name']}** (Category: {technique['category']})

Return ONLY valid JSON with this exact structure (no markdown, no extra text):
{{
  "title": "SEO-optimized page title (include BJJ and technique name)",
  "meta_description": "150-160 char meta description for search engines",
  "h1": "Main heading for the article",
  "intro": "2-3 sentence introduction explaining what this technique is",
  "how_to": "Step-by-step instructions (4-6 steps, each 1-2 sentences)",
  "key_details": "Important details, common mistakes, and tips (3-4 points)",
  "variations": "2-3 common variations or related techniques",
  "when_to_use": "Situations and positions where this technique works best",
  "counters": "2-3 main defenses or counters against this technique",
  "belt_level": "Recommended belt level (White/Blue/Purple/Brown/Black)",
  "faq_q1": "Frequently asked question about this technique",
  "faq_a1": "Answer to the FAQ",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}}"""

# ===== 記事JSONをHTMLに変換 =====
def article_to_html(tech, lang_code, article, all_techniques):
    lang = LANGUAGES[lang_code]
    nav_labels = {
        "en": {"home": "Home", "all": "All Techniques", "category": "Category"},
        "ja": {"home": "ホーム", "all": "全技一覧", "category": "カテゴリ"},
        "pt": {"home": "Início", "all": "Todas as Técnicas", "category": "Categoria"},
    }
    labels = nav_labels[lang_code]

    # リスト or 文字列を安全に文字列化するヘルパー
    def to_str(v):
        if isinstance(v, list): return "\n".join(str(i) for i in v)
        return str(v) if v else ""

    # 同カテゴリの関連技リンク
    related = [t for t in all_techniques if t["category"] == tech["category"] and t["slug"] != tech["slug"]][:5]
    related_links = "\n".join([
        f'<a href="../{t["slug"]}.html">{t["name"]}</a>'
        for t in related
    ])

    # 言語切替リンク
    lang_switcher = " | ".join([
        f'<a href="../../{lc}/{tech["slug"]}.html">{LANGUAGES[lc]["name"]}</a>'
        for lc in LANGUAGES if lc != lang_code
    ])

    keywords_str = ", ".join(article.get("keywords", []))

    return f"""<!DOCTYPE html>
<html lang="{lang_code}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{article.get('title', tech['name'])} | BJJ Wiki</title>
<meta name="description" content="{article.get('meta_description', '')}">
<meta name="keywords" content="{keywords_str}">
<meta property="og:title" content="{article.get('title', tech['name'])}">
<meta property="og:description" content="{article.get('meta_description', '')}">
<meta property="og:type" content="article">
<meta property="og:url" content="{SITE_URL}/{lang_code}/{tech['slug']}.html">
<link rel="canonical" href="{SITE_URL}/{lang_code}/{tech['slug']}.html">
<link rel="alternate" hreflang="en" href="{SITE_URL}/en/{tech['slug']}.html">
<link rel="alternate" hreflang="ja" href="{SITE_URL}/ja/{tech['slug']}.html">
<link rel="alternate" hreflang="pt" href="{SITE_URL}/pt/{tech['slug']}.html">
<style>
  :root {{--bg:#0a0a0f;--card:#111119;--border:#1e1e2e;--text:#e2e2ee;--muted:#7a7a9a;--accent:#6e40c9;--green:#22c55e}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.7;padding:0 16px}}
  .container{{max-width:800px;margin:0 auto;padding:24px 0 64px}}
  header{{padding:20px 0;border-bottom:1px solid var(--border);margin-bottom:32px}}
  .logo{{font-size:1.4rem;font-weight:800;color:var(--text);text-decoration:none}}
  .logo span{{color:var(--accent)}}
  nav{{margin-top:8px;font-size:0.85rem;color:var(--muted)}}
  nav a{{color:var(--muted);text-decoration:none;margin-right:12px}}
  nav a:hover{{color:var(--text)}}
  .lang-switcher{{font-size:0.8rem;color:var(--muted);margin-top:6px}}
  .lang-switcher a{{color:var(--accent);text-decoration:none;margin:0 4px}}
  .badge{{display:inline-block;font-size:0.72rem;padding:2px 10px;border-radius:20px;background:#1e1e2e;color:var(--muted);border:1px solid var(--border);margin-bottom:12px}}
  h1{{font-size:2rem;font-weight:800;margin-bottom:16px;line-height:1.2}}
  h2{{font-size:1.2rem;font-weight:700;margin:32px 0 12px;padding-left:12px;border-left:3px solid var(--accent)}}
  p{{color:#c2c2d9;margin-bottom:16px}}
  .card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px}}
  .belt{{display:inline-block;padding:3px 12px;border-radius:4px;font-size:0.8rem;font-weight:700;margin-bottom:16px}}
  .belt-white{{background:#e2e2ee;color:#111}}
  .belt-blue{{background:#2563eb;color:#fff}}
  .belt-purple{{background:#7c3aed;color:#fff}}
  .belt-brown{{background:#92400e;color:#fff}}
  .belt-black{{background:#111;color:#fff;border:1px solid #444}}
  .faq{{background:#0d0d1a;border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px}}
  .faq-q{{font-weight:700;color:var(--accent);margin-bottom:8px}}
  .related-links{{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}}
  .related-links a{{background:#1e1e2e;color:var(--muted);text-decoration:none;padding:4px 12px;border-radius:6px;font-size:0.85rem;border:1px solid var(--border)}}
  .related-links a:hover{{color:var(--text);border-color:var(--accent)}}
  .aff-box{{background:linear-gradient(135deg,#1a0a2e,#0d0d1a);border:1px solid var(--accent);border-radius:12px;padding:20px;margin:32px 0;text-align:center}}
  .aff-box p{{color:var(--muted);font-size:0.9rem;margin-bottom:12px}}
  .aff-btn{{display:inline-block;background:var(--accent);color:#fff;padding:10px 24px;border-radius:8px;text-decoration:none;font-weight:700;font-size:0.9rem}}
  footer{{border-top:1px solid var(--border);padding:24px 0;text-align:center;color:var(--muted);font-size:0.8rem}}
</style>
</head>
<body>
<div class="container">
  <header>
    <a href="../../index.html" class="logo">BJJ<span>Wiki</span></a>
    <nav>
      <a href="../../index.html">{labels['home']}</a>
      <a href="../index.html">{labels['all']}</a>
    </nav>
    <div class="lang-switcher">{lang_switcher}</div>
  </header>

  <span class="badge">{tech['category']}</span><br>
  <span class="belt belt-{to_str(article.get('belt_level','white')).lower().split('/')[0].strip()}">{to_str(article.get('belt_level','All Levels'))}</span>
  <h1>{to_str(article.get('h1', tech['name']))}</h1>
  <p>{to_str(article.get('intro', ''))}</p>

  <h2>{'How to Execute' if lang_code=='en' else 'やり方' if lang_code=='ja' else 'Como Executar'}</h2>
  <div class="card"><p>{to_str(article.get('how_to','')).replace(chr(10),'<br>')}</p></div>

  <h2>{'Key Details & Tips' if lang_code=='en' else 'コツと注意点' if lang_code=='ja' else 'Detalhes e Dicas'}</h2>
  <div class="card"><p>{to_str(article.get('key_details','')).replace(chr(10),'<br>')}</p></div>

  <h2>{'Variations' if lang_code=='en' else 'バリエーション' if lang_code=='ja' else 'Variações'}</h2>
  <div class="card"><p>{to_str(article.get('variations','')).replace(chr(10),'<br>')}</p></div>

  <h2>{'When to Use' if lang_code=='en' else '使うタイミング' if lang_code=='ja' else 'Quando Usar'}</h2>
  <div class="card"><p>{to_str(article.get('when_to_use','')).replace(chr(10),'<br>')}</p></div>

  <h2>{'Counters & Defenses' if lang_code=='en' else 'カウンター・防御' if lang_code=='ja' else 'Defesas e Contra-ataques'}</h2>
  <div class="card"><p>{to_str(article.get('counters','')).replace(chr(10),'<br>')}</p></div>

  <!-- BJJ Fanatics アフィリエイト -->
  <div class="aff-box">
    <p>{'Master this technique with world-class instruction' if lang_code=='en' else 'この技を世界レベルの指導で習得しよう' if lang_code=='ja' else 'Domine esta técnica com instrução de classe mundial'}</p>
    <a class="aff-btn" href="https://bjjfanatics.com/search?q={urllib.parse.quote(tech['name']) if False else tech['name'].replace(' ','+')}" target="_blank" rel="noopener noreferrer nofollow">
      {'Browse Instructionals →' if lang_code=='en' else '教則動画を見る →' if lang_code=='ja' else 'Ver Instrucionais →'}
    </a>
  </div>

  <div class="faq">
    <div class="faq-q">Q: {article.get('faq_q1','')}</div>
    <p>{article.get('faq_a1','')}</p>
  </div>

  {'<h2>Related Techniques</h2>' if lang_code=='en' else '<h2>関連技</h2>' if lang_code=='ja' else '<h2>Técnicas Relacionadas</h2>'}
  <div class="related-links">{related_links}</div>

  <footer>
    <p>BJJ Wiki — {'The free BJJ technique encyclopedia' if lang_code=='en' else '無料BJJ技術百科事典' if lang_code=='ja' else 'A enciclopédia gratuita de técnicas de BJJ'}</p>
  </footer>
</div>
</body>
</html>"""

# ===== カテゴリ別インデックスページ =====
def generate_category_index(lang_code, techniques_by_category):
    lang = LANGUAGES[lang_code]
    titles = {"en": "All BJJ Techniques", "ja": "全BJJ技一覧", "pt": "Todas as Técnicas de BJJ"}
    descs  = {
        "en": "Complete encyclopedia of Brazilian Jiu-Jitsu techniques. Learn guards, passes, submissions, sweeps and more.",
        "ja": "ブラジリアン柔術（BJJ）の技術百科事典。ガード、パス、絞め技、関節技、スイープを網羅。",
        "pt": "Enciclopédia completa de técnicas de Jiu-Jitsu Brasileiro. Aprenda guardas, passagens, finalizações e muito mais."
    }
    cards = ""
    for cat, techs in sorted(techniques_by_category.items()):
        links = "".join([f'<a href="{t["slug"]}.html">{t["name"]}</a>' for t in techs])
        cards += f'<div class="cat-card"><h2>{cat}</h2><div class="tech-links">{links}</div></div>'

    return f"""<!DOCTYPE html>
<html lang="{lang_code}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titles[lang_code]} | BJJ Wiki</title>
<meta name="description" content="{descs[lang_code]}">
<style>
  :root{{--bg:#0a0a0f;--card:#111119;--border:#1e1e2e;--text:#e2e2ee;--muted:#7a7a9a;--accent:#6e40c9}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;padding:0 16px}}
  .container{{max-width:900px;margin:0 auto;padding:24px 0 64px}}
  header{{padding:20px 0;border-bottom:1px solid var(--border);margin-bottom:32px}}
  .logo{{font-size:1.4rem;font-weight:800;color:var(--text);text-decoration:none}}
  .logo span{{color:var(--accent)}}
  h1{{font-size:2rem;font-weight:800;margin-bottom:8px}}
  .subtitle{{color:var(--muted);margin-bottom:32px}}
  .cat-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px}}
  .cat-card h2{{font-size:1rem;font-weight:700;color:var(--accent);margin-bottom:12px}}
  .tech-links{{display:flex;flex-wrap:wrap;gap:8px}}
  .tech-links a{{background:#1e1e2e;color:var(--muted);text-decoration:none;padding:4px 12px;border-radius:6px;font-size:0.85rem;border:1px solid var(--border)}}
  .tech-links a:hover{{color:var(--text);border-color:var(--accent)}}
  footer{{border-top:1px solid var(--border);padding:24px 0;text-align:center;color:var(--muted);font-size:0.8rem}}
</style>
</head>
<body>
<div class="container">
  <header><a href="../index.html" class="logo">BJJ<span>Wiki</span></a></header>
  <h1>{titles[lang_code]}</h1>
  <p class="subtitle">{descs[lang_code]}</p>
  {cards}
  <footer><p>BJJ Wiki</p></footer>
</div>
</body>
</html>"""

# ===== トップページ =====
def generate_index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BJJ Wiki — Brazilian Jiu-Jitsu Technique Encyclopedia</title>
<meta name="description" content="Free multilingual encyclopedia of Brazilian Jiu-Jitsu techniques. Available in English, Japanese and Portuguese.">
<style>
  :root{--bg:#0a0a0f;--card:#111119;--border:#1e1e2e;--text:#e2e2ee;--muted:#7a7a9a;--accent:#6e40c9}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;padding:0 16px;min-height:100vh;display:flex;align-items:center;justify-content:center}
  .container{max-width:640px;width:100%;text-align:center;padding:48px 0}
  .logo{font-size:3rem;font-weight:900;margin-bottom:16px}
  .logo span{color:var(--accent)}
  .subtitle{color:var(--muted);margin-bottom:48px;font-size:1.1rem}
  .lang-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:32px}
  .lang-btn{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:32px 16px;text-decoration:none;color:var(--text);transition:border-color 0.2s}
  .lang-btn:hover{border-color:var(--accent)}
  .lang-flag{font-size:2.5rem;margin-bottom:8px}
  .lang-name{font-size:1.1rem;font-weight:700}
  .lang-sub{font-size:0.8rem;color:var(--muted);margin-top:4px}
  footer{color:var(--muted);font-size:0.8rem}
</style>
</head>
<body>
<div class="container">
  <div class="logo">BJJ<span>Wiki</span></div>
  <p class="subtitle">The free Brazilian Jiu-Jitsu technique encyclopedia</p>
  <div class="lang-grid">
    <a class="lang-btn" href="en/index.html">
      <div class="lang-flag">🇺🇸</div>
      <div class="lang-name">English</div>
      <div class="lang-sub">Browse in English</div>
    </a>
    <a class="lang-btn" href="ja/index.html">
      <div class="lang-flag">🇯🇵</div>
      <div class="lang-name">日本語</div>
      <div class="lang-sub">日本語で読む</div>
    </a>
    <a class="lang-btn" href="pt/index.html">
      <div class="lang-flag">🇧🇷</div>
      <div class="lang-name">Português</div>
      <div class="lang-sub">Ler em Português</div>
    </a>
  </div>
  <footer><p>BJJ Wiki — Free & Open Knowledge</p></footer>
</div>
</body>
</html>"""

# ===== キャッシュ管理 =====
def load_cache():
    path = os.path.join(SITE_DIR, "generated.json")
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return {}

def save_cache(cache):
    path = os.path.join(SITE_DIR, "generated.json")
    with open(path, "w") as f: json.dump(cache, f, ensure_ascii=False, indent=2)

# ===== メイン =====
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="キャッシュ無視して全再生成")
    parser.add_argument("--limit", type=int, default=5, help="1回の実行で生成する最大記事数（コスト管理）")
    parser.add_argument("--lang", default="all", help="生成する言語 (en/ja/pt/all)")
    args = parser.parse_args()

    os.makedirs(SITE_DIR, exist_ok=True)
    cache  = {} if args.force else load_cache()
    langs  = list(LANGUAGES.keys()) if args.lang == "all" else [args.lang]
    count  = 0

    # トップページ生成
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(generate_index())
    print("[OK] index.html 生成完了")

    # 技ページ生成
    for lang_code in langs:
        lang_dir = os.path.join(SITE_DIR, lang_code)
        os.makedirs(lang_dir, exist_ok=True)
        techniques_by_category = {}

        for tech in TECHNIQUES:
            cache_key = f"{lang_code}/{tech['slug']}"
            out_path  = os.path.join(lang_dir, f"{tech['slug']}.html")

            # カテゴリ分類
            cat = tech["category"]
            techniques_by_category.setdefault(cat, []).append(tech)

            # キャッシュ済みかつファイル存在ならスキップ
            if cache_key in cache and os.path.exists(out_path) and not args.force:
                continue

            if count >= args.limit:
                print(f"[INFO] 上限({args.limit}件)に達しました。次回実行で続きを生成します。")
                break

            print(f"[{lang_code}] {tech['name']} 生成中...")
            raw = call_gemini(build_article_prompt(tech, lang_code))
            if not raw:
                print(f"[WARNING] {tech['name']} 生成失敗。スキップ")
                continue

            # JSONパース
            try:
                text    = re.sub(r'^```[a-z]*\n?', '', raw.strip(), flags=re.MULTILINE)
                text    = re.sub(r'\n?```$', '', text, flags=re.MULTILINE)
                article = json.loads(text.strip())
            except Exception as e:
                print(f"[WARNING] JSONパース失敗: {e}")
                continue

            # HTML生成・保存
            html = article_to_html(tech, lang_code, article, TECHNIQUES)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)

            cache[cache_key] = datetime.datetime.now().isoformat()
            count += 1
            print(f"[OK] {cache_key} → {out_path}")
            time.sleep(1)  # API負荷軽減

        # カテゴリインデックス生成
        idx_html = generate_category_index(lang_code, techniques_by_category)
        with open(os.path.join(lang_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(idx_html)
        print(f"[OK] {lang_code}/index.html 生成完了")

    save_cache(cache)
    print(f"\n[完了] {count}件の新規記事を生成しました")
    remaining = sum(
        1 for tech in TECHNIQUES
        for lc in langs
        if f"{lc}/{tech['slug']}" not in cache
    )
    print(f"[残り] あと{remaining}件未生成")

if __name__ == "__main__":
    main()
