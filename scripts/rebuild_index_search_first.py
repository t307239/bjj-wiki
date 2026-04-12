#!/usr/bin/env python3
"""
Rebuild index.html (en/ja/pt) as Search-First design.
Replaces the 5000-line hard-coded card list with dynamic JS search.
"""
import os, json

WIKI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- Language config ----
LANGS = {
    "en": {
        "title": "BJJ Wiki — Complete Brazilian Jiu-Jitsu Guide",
        "desc":  "Free BJJ techniques, guides & tutorials. 1,500+ pages covering submissions, guards, passes, sweeps and competition strategy.",
        "og_locale": "en_US",
        "hero_h1": "BJJ Wiki",
        "hero_sub": "1,500+ techniques, guides & tutorials for all belt levels",
        "search_ph": "Search techniques, positions, submissions…",
        "cats": [
            ("🥋", "All",          "all"),
            ("💀", "Submissions",  "submission"),
            ("🛡️", "Guard",       "guard"),
            ("⚔️", "Passing",      "passing"),
            ("🌀", "Sweeps",       "sweep"),
            ("🤸", "Takedowns",    "takedown"),
            ("🏔️", "Positions",   "position"),
            ("🔓", "Escapes",      "escape"),
            ("⚡", "Conditioning", "conditioning"),
            ("🧠", "Concepts",     "concepts"),
        ],
        "no_results": "No results found. Try a different search term.",
        "belt_labels": {"white":"White Belt","blue":"Blue Belt","purple":"Purple Belt","brown":"Brown Belt","black":"Black Belt"},
        "popular_title": "Popular Guides",
        "cta_text": "Track your BJJ training",
        "cta_btn":  "Free App →",
        "beehiiv_title": "Join 2,000+ BJJ Practitioners",
        "beehiiv_desc":  "Get the free BJJ White Belt Guide",
        "beehiiv_btn":   "Get Free Access →",
        "lang_nav": [("🇺🇸 EN", "../en/index.html"), ("🇯🇵 JA", "../ja/index.html"), ("🇧🇷 PT", "../pt/index.html")],
        "pub_id": "pub_3b7e80fc-2a63-4b5b-a0bf-35649de37d37",
    },
    "ja": {
        "title": "BJJ Wiki — ブラジリアン柔術完全ガイド",
        "desc":  "BJJテクニック・ガイド・チュートリアル無料。チョーク、ガード、パス、スウィープなど1,500+ページ。",
        "og_locale": "ja_JP",
        "hero_h1": "BJJ Wiki",
        "hero_sub": "1,500+テクニック・ガイド — 全帯対応",
        "search_ph": "テクニック・ポジション・サブミッションを検索…",
        "cats": [
            ("🥋", "すべて",       "all"),
            ("💀", "チョーク",     "submission"),
            ("🛡️", "ガード",      "guard"),
            ("⚔️", "パス",        "passing"),
            ("🌀", "スウィープ",  "sweep"),
            ("🤸", "テイクダウン","takedown"),
            ("🏔️", "ポジション", "position"),
            ("🔓", "エスケープ",  "escape"),
            ("⚡", "コンディショニング","conditioning"),
            ("🧠", "コンセプト",  "concepts"),
        ],
        "no_results": "結果が見つかりませんでした。別のキーワードで試してください。",
        "belt_labels": {"white":"白帯","blue":"青帯","purple":"紫帯","brown":"茶帯","black":"黒帯"},
        "popular_title": "人気のガイド",
        "cta_text": "BJJ練習を記録しよう",
        "cta_btn":  "無料アプリ →",
        "beehiiv_title": "2,000人以上が登録中",
        "beehiiv_desc":  "無料BJJ白帯ガイドをゲット",
        "beehiiv_btn":   "無料でアクセス →",
        "lang_nav": [("🇺🇸 EN", "../en/index.html"), ("🇯🇵 JA", "../ja/index.html"), ("🇧🇷 PT", "../pt/index.html")],
        "pub_id": "pub_3b7e80fc-2a63-4b5b-a0bf-35649de37d37",
    },
    "pt": {
        "title": "BJJ Wiki — Guia Completo de Jiu-Jitsu Brasileiro",
        "desc":  "Técnicas de BJJ, guias e tutoriais gratuitos. Mais de 1.500 páginas cobrindo finalizações, guardas, passagens e estratégias de competição.",
        "og_locale": "pt_BR",
        "hero_h1": "BJJ Wiki",
        "hero_sub": "Mais de 1.500 técnicas, guias e tutoriais para todas as faixas",
        "search_ph": "Pesquisar técnicas, posições, finalizações…",
        "cats": [
            ("🥋", "Todos",        "all"),
            ("💀", "Finalizações", "submission"),
            ("🛡️", "Guarda",      "guard"),
            ("⚔️", "Passagens",   "passing"),
            ("🌀", "Raspagens",   "sweep"),
            ("🤸", "Quedas",      "takedown"),
            ("🏔️", "Posições",   "position"),
            ("🔓", "Fugas",       "escape"),
            ("⚡", "Condicionamento","conditioning"),
            ("🧠", "Conceitos",   "concepts"),
        ],
        "no_results": "Nenhum resultado encontrado. Tente outro termo de pesquisa.",
        "belt_labels": {"white":"Faixa Branca","blue":"Faixa Azul","purple":"Faixa Roxa","brown":"Faixa Marrom","black":"Faixa Preta"},
        "popular_title": "Guias Populares",
        "cta_text": "Rastreie seu treinamento de BJJ",
        "cta_btn":  "App Grátis →",
        "beehiiv_title": "Junte-se a 2.000+ Praticantes de BJJ",
        "beehiiv_desc":  "Receba o guia gratuito para faixa branca",
        "beehiiv_btn":   "Acesso Gratuito →",
        "lang_nav": [("🇺🇸 EN", "../en/index.html"), ("🇯🇵 JA", "../ja/index.html"), ("🇧🇷 PT", "../pt/index.html")],
        "pub_id": "pub_3b7e80fc-2a63-4b5b-a0bf-35649de37d37",
    },
}

# Popular pages to show by default (before user searches)
POPULAR = {
    "en": [
        ("bjj-triangle-choke-guide","Triangle Choke","⬛","submission"),
        ("bjj-rear-naked-choke","Rear Naked Choke","⬛","submission"),
        ("bjj-armbar-guide","Armbar Guide","⬛","submission"),
        ("bjj-closed-guard-attacks","Closed Guard Attacks","🔒","guard"),
        ("bjj-guard-passing-concepts","Guard Passing Concepts","⚔️","passing"),
        ("bjj-open-guard-mastery","Open Guard Mastery","🌐","guard"),
        ("bjj-leg-lock-system","Leg Lock System","🦵","submission"),
        ("bjj-back-control-system","Back Control System","🎯","position"),
        ("bjj-competition-strategy","Competition Strategy","🏆","concepts"),
        ("bjj-beginners-guide","Beginner's Guide","🥋","concepts"),
        ("bjj-drilling-guide","Drilling Guide","🔁","concepts"),
        ("bjj-flow-rolling","Flow Rolling","🌊","concepts"),
    ],
    "ja": [
        ("bjj-triangle-choke-guide","トライアングルチョーク","⬛","submission"),
        ("bjj-rear-naked-choke","裸絞め（RNC）","⬛","submission"),
        ("bjj-armbar-guide","腕十字固め","⬛","submission"),
        ("bjj-closed-guard-attacks","クローズドガード攻撃","🔒","guard"),
        ("bjj-guard-passing-concepts","ガードパス基礎","⚔️","passing"),
        ("bjj-open-guard-mastery","オープンガード完全習得","🌐","guard"),
        ("bjj-leg-lock-system","レッグロックシステム","🦵","submission"),
        ("bjj-back-control-system","バックコントロール","🎯","position"),
        ("bjj-competition-strategy","競技戦略","🏆","concepts"),
        ("bjj-beginners-guide","初心者ガイド","🥋","concepts"),
        ("bjj-drilling-guide","ドリリングガイド","🔁","concepts"),
        ("bjj-flow-rolling","フローローリング","🌊","concepts"),
    ],
    "pt": [
        ("bjj-triangle-choke-guide","Triângulo","⬛","submission"),
        ("bjj-rear-naked-choke","Mata Leão","⬛","submission"),
        ("bjj-armbar-guide","Chave de Braço","⬛","submission"),
        ("bjj-closed-guard-attacks","Ataques da Guarda Fechada","🔒","guard"),
        ("bjj-guard-passing-concepts","Conceitos de Passagem","⚔️","passing"),
        ("bjj-open-guard-mastery","Domínio da Guarda Aberta","🌐","guard"),
        ("bjj-leg-lock-system","Sistema de Leg Locks","🦵","submission"),
        ("bjj-back-control-system","Controle das Costas","🎯","position"),
        ("bjj-competition-strategy","Estratégia de Competição","🏆","concepts"),
        ("bjj-beginners-guide","Guia do Iniciante","🥋","concepts"),
        ("bjj-drilling-guide","Guia de Drilling","🔁","concepts"),
        ("bjj-flow-rolling","Flow Rolling","🌊","concepts"),
    ],
}

GTM_SCRIPT = """<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,'dataLayer','script','dataLayer','GTM-WC3DKRB');</script>
<!-- End Google Tag Manager -->"""

GTM_NOSCRIPT = """<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WC3DKRB"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->"""

def make_popular_cards_js(popular):
    """Build JS array for popular pages."""
    items = []
    for slug, title, emoji, cat in popular:
        items.append(f'{{s:"{slug}",t:{json.dumps(title)},e:"{emoji}",c:"{cat}"}}')
    return "[" + ",".join(items) + "]"

def build_index(lang):
    L = LANGS[lang]
    popular_js = make_popular_cards_js(POPULAR[lang])

    cats_html = "\n".join(
        f'<button class="cat-pill{" active" if c == "all" else ""}" data-cat="{c}" onclick="filterCat(\'{c}\',this)">'
        f'{e} {n}</button>'
        for e, n, c in L["cats"]
    )

    lang_nav_html = " | ".join(
        f'<a href="{url}" style="color:{"#e2b714" if url.startswith("../"+lang) else "#9ca3af"};text-decoration:none">{label}</a>'
        for label, url in L["lang_nav"]
    )

    belt_js = json.dumps(L["belt_labels"], ensure_ascii=False)
    no_results = L["no_results"]
    popular_title = L["popular_title"]

    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{L["title"]}</title>
<meta name="description" content="{L["desc"]}">
<meta property="og:title" content="{L["title"]}">
<meta property="og:description" content="{L["desc"]}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{L["og_locale"]}">
<meta name="twitter:card" content="summary">
<link rel="alternate" hreflang="en" href="https://wiki.bjj-app.net/en/index.html">
<link rel="alternate" hreflang="ja" href="https://wiki.bjj-app.net/ja/index.html">
<link rel="alternate" hreflang="pt" href="https://wiki.bjj-app.net/pt/index.html">
<link rel="alternate" hreflang="x-default" href="https://wiki.bjj-app.net/en/index.html">
{GTM_SCRIPT}
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#0b0f1a;--card:#111827;--card-hover:#161f31;--border:rgba(255,255,255,0.08);--border-hover:rgba(124,58,237,0.5);--text:#e2e8f0;--muted:#64748b;--accent:#7c3aed;--accent2:#e94560}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh}}
a{{color:inherit;text-decoration:none}}
/* Header */
header{{background:rgba(11,15,26,0.95);border-bottom:1px solid var(--border);padding:12px 20px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;backdrop-filter:blur(8px)}}
.logo{{font-weight:800;font-size:1.2rem;letter-spacing:-0.02em;color:#fff}}.logo span{{color:var(--accent2)}}
/* Hero */
.hero{{text-align:center;padding:48px 20px 32px;max-width:680px;margin:0 auto}}
.hero h1{{font-size:2.4rem;font-weight:800;letter-spacing:-0.03em;margin-bottom:10px}}
.hero h1 span{{color:var(--accent2)}}
.hero-sub{{color:var(--muted);font-size:1rem;margin-bottom:28px}}
/* Search */
.search-wrap{{position:relative;max-width:560px;margin:0 auto 20px}}
#search{{width:100%;padding:14px 48px 14px 18px;background:var(--card);border:1px solid var(--border);border-radius:12px;color:var(--text);font-size:1rem;outline:none;transition:border-color .2s}}
#search:focus{{border-color:var(--accent)}}
#search::placeholder{{color:var(--muted)}}
.search-icon{{position:absolute;right:16px;top:50%;transform:translateY(-50%);color:var(--muted);pointer-events:none}}
/* Category pills */
.cat-pills{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-bottom:32px;padding:0 16px}}
.cat-pill{{padding:6px 14px;background:var(--card);border:1px solid var(--border);border-radius:20px;font-size:.85rem;cursor:pointer;color:var(--muted);transition:all .15s}}
.cat-pill:hover,.cat-pill.active{{background:var(--accent);border-color:var(--accent);color:#fff}}
/* Results */
.container{{max-width:1200px;margin:0 auto;padding:0 16px 60px}}
.results-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;color:var(--muted);font-size:.85rem}}
.results-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}}
.result-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;transition:border-color .2s,background .2s;cursor:pointer}}
.result-card:hover{{border-color:var(--border-hover);background:var(--card-hover)}}
.result-title{{font-weight:600;font-size:.95rem;margin-bottom:6px;color:var(--text)}}
.result-desc{{font-size:.8rem;color:var(--muted);line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.result-meta{{display:flex;gap:6px;margin-top:8px}}
.badge{{font-size:.7rem;padding:2px 8px;border-radius:10px;background:rgba(124,58,237,.15);color:var(--accent)}}
.no-results{{text-align:center;color:var(--muted);padding:60px 20px}}
#load-more-wrap{{text-align:center;margin-top:24px}}
#load-more{{padding:10px 28px;background:var(--card);border:1px solid var(--border);border-radius:8px;color:var(--text);cursor:pointer;font-size:.9rem;transition:all .15s}}
#load-more:hover{{border-color:var(--accent)}}
/* CTA banner */
.cta-banner{{background:linear-gradient(135deg,rgba(124,58,237,.15),rgba(233,69,96,.1));border:1px solid rgba(124,58,237,.3);border-radius:14px;padding:20px 24px;display:flex;align-items:center;justify-content:space-between;gap:12px;margin:32px 0}}
.cta-btn{{white-space:nowrap;padding:10px 20px;background:var(--accent2);color:#fff;border-radius:8px;font-weight:600;font-size:.9rem}}
/* Beehiiv */
.bee-wrap{{background:linear-gradient(135deg,rgba(124,58,237,.1),rgba(233,69,96,.08));border:1px solid rgba(124,58,237,.25);border-radius:14px;padding:28px;text-align:center;margin:32px 0}}
.bee-title{{font-size:1.1rem;font-weight:700;margin-bottom:6px}}
.bee-desc{{color:var(--muted);font-size:.9rem;margin-bottom:16px}}
.bee-form{{display:flex;gap:8px;max-width:400px;margin:0 auto;flex-wrap:wrap;justify-content:center}}
.bee-input{{flex:1;min-width:200px;padding:10px 14px;background:var(--card);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:.9rem;outline:none}}
.bee-input:focus{{border-color:var(--accent)}}
.bee-btn{{padding:10px 18px;background:var(--accent);color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:.9rem}}
.bee-note{{font-size:.75rem;color:var(--muted);margin-top:8px}}
/* Footer */
footer{{border-top:1px solid var(--border);padding:24px;text-align:center;color:var(--muted);font-size:.8rem}}
@media(max-width:600px){{.hero h1{{font-size:1.8rem}}.cta-banner{{flex-direction:column;text-align:center}}}}
</style>
</head>
<body>
{GTM_NOSCRIPT}
<header>
  <a href="index.html" class="logo">BJJ<span>.</span>Wiki</a>
  <div style="font-size:.85rem">{lang_nav_html}</div>
</header>

<div class="hero">
  <h1>BJJ<span> Wiki</span></h1>
  <p class="hero-sub">{L["hero_sub"]}</p>
  <div class="search-wrap">
    <input id="search" type="search" placeholder="{L["search_ph"]}" autocomplete="off" oninput="onSearch(this.value)">
    <svg class="search-icon" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
  </div>
  <div class="cat-pills">
{cats_html}
  </div>
</div>

<div class="container">
  <!-- CTA Banner -->
  <div class="cta-banner">
    <span style="font-size:.95rem">{L["cta_text"]}</span>
    <a href="https://bjj-app-one.vercel.app" class="cta-btn" onclick="gtag('event','cta_click',{{'page':'index'}})">{L["cta_btn"]}</a>
  </div>

  <!-- Results section -->
  <div class="results-header">
    <span id="results-count"></span>
    <span id="results-label"></span>
  </div>
  <div id="results-grid" class="results-grid"></div>
  <div id="load-more-wrap" style="display:none">
    <button id="load-more" onclick="loadMore()">Load more</button>
  </div>
  <div id="no-results" class="no-results" style="display:none">{no_results}</div>

  <!-- Beehiiv subscription -->
  <div class="bee-wrap">
    <div class="bee-title">{L["beehiiv_title"]}</div>
    <div class="bee-desc">{L["beehiiv_desc"]}</div>
    <div class="bee-form">
      <input class="bee-input" type="email" id="bee-email" placeholder="email@example.com">
      <button class="bee-btn" onclick="submitBee()">{L["beehiiv_btn"]}</button>
    </div>
    <div class="bee-note">No spam. Unsubscribe anytime.</div>
  </div>
</div>

<footer>
  <div style="margin-bottom:8px">{lang_nav_html}</div>
  &copy; 2025 BJJ Wiki — Free Brazilian Jiu-Jitsu guides
</footer>

<script>
// ---- Config ----
var POPULAR = {popular_js};
var BELT = {belt_js};
var allData = null;
var filtered = [];
var shown = 0;
var PAGE = 24;
var activeCat = "all";
var searchQ = "";

// ---- Init ----
window.addEventListener('load', function() {{
  renderCards(POPULAR.map(function(p){{
    return {{s:p.s,t:p.t,d:"",c:p.c,b:"white"}};
  }}), false);
  document.getElementById('results-count').textContent = "{popular_title}";
  // Lazy load search.json
  fetch('search.json').then(function(r){{return r.json();}}).then(function(data){{
    allData = data;
  }}).catch(function(){{}});
}});

// ---- Search ----
function onSearch(q) {{
  searchQ = q.trim().toLowerCase();
  if (!allData) {{
    fetch('search.json').then(function(r){{return r.json();}}).then(function(data){{
      allData = data;
      doFilter();
    }});
  }} else {{
    doFilter();
  }}
}}

function filterCat(cat, el) {{
  activeCat = cat;
  document.querySelectorAll('.cat-pill').forEach(function(p){{p.classList.remove('active');}});
  el.classList.add('active');
  if (!allData) {{
    fetch('search.json').then(function(r){{return r.json();}}).then(function(data){{
      allData = data;
      doFilter();
    }});
  }} else {{
    doFilter();
  }}
}}

function doFilter() {{
  var q = searchQ;
  var cat = activeCat;
  if (!allData) return;
  filtered = allData.filter(function(item) {{
    var catOk = cat === "all" || item.c === cat;
    var qOk   = !q || item.t.toLowerCase().includes(q) || (item.d && item.d.toLowerCase().includes(q)) || item.s.includes(q.replace(/ /g,'-'));
    return catOk && qOk;
  }});
  shown = 0;
  renderCards(filtered.slice(0, PAGE), true);
  shown = Math.min(PAGE, filtered.length);
  document.getElementById('results-count').textContent = filtered.length + " results";
  document.getElementById('no-results').style.display = filtered.length ? 'none' : '';
  document.getElementById('load-more-wrap').style.display = filtered.length > PAGE ? '' : 'none';
}}

function loadMore() {{
  var next = filtered.slice(shown, shown + PAGE);
  appendCards(next);
  shown += next.length;
  if (shown >= filtered.length) {{
    document.getElementById('load-more-wrap').style.display = 'none';
  }}
}}

function renderCards(items, clear) {{
  var grid = document.getElementById('results-grid');
  if (clear) grid.innerHTML = '';
  appendCards(items);
}}

function appendCards(items) {{
  var grid = document.getElementById('results-grid');
  var html = '';
  items.forEach(function(item) {{
    var slug = item.s || item.slug || '';
    var title = item.t || item.title || slug;
    var desc = item.d || item.desc || '';
    var belt = BELT[item.b] || BELT['white'] || '';
    html += '<a href="' + slug + '.html" class="result-card">';
    html += '<div class="result-title">' + esc(title) + '</div>';
    if (desc) html += '<div class="result-desc">' + esc(desc) + '</div>';
    html += '<div class="result-meta"><span class="badge">' + esc(belt) + '</span></div>';
    html += '</a>';
  }});
  grid.innerHTML += html;
}}

function esc(s) {{
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

// ---- Beehiiv ----
function submitBee() {{
  var email = document.getElementById('bee-email').value.trim();
  if (!email || !email.includes('@')) return;
  fetch('https://api.beehiiv.com/v2/publications/{L["pub_id"]}/subscriptions', {{
    method:'POST',
    headers:{{'Content-Type':'application/json'}},
    body:JSON.stringify({{email:email,reactivate_existing:false,send_welcome_email:true}})
  }}).catch(function(){{}});
  var form = document.querySelector('.bee-form');
  if (form) form.innerHTML = '<p style="color:#4ade80;font-size:.95rem">✓ Subscribed!</p>';
  gtag('event','newsletter_signup',{{'page':'index_{lang}'}});
}}
</script>
</body>
</html>"""
    return html

def write_index(lang):
    html = build_index(lang)
    out_path = os.path.join(WIKI_DIR, lang, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    size_kb = len(html.encode("utf-8")) / 1024
    print(f"  ✅ {lang}/index.html — {size_kb:.0f}KB (was 560-580KB)")

if __name__ == "__main__":
    print("Rebuilding index.html (Search-First)...")
    for lang in ["en", "ja", "pt"]:
        write_index(lang)
    print("Done.")
