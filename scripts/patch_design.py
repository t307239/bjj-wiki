#!/usr/bin/env python3
"""BJJ Wiki Design Patch v2 — run from ~/Claude/bjj-wiki/"""
import os, re, glob

BASE = os.path.expanduser("~/Claude/bjj-wiki")

# ── Article page CSS (matches actual HTML structure) ──────────────────────────
ARTICLE_CSS = """:root{
  --bg:#080b12;--surface:#0f1420;--card:#141926;
  --border:#1f2840;--text:#e8eaf6;--muted:#6b7699;
  --accent:#7c6af7;--accent2:#a78bfa;
  --green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--blue:#3b82f6;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif;
  line-height:1.75;padding:0 16px}
a{color:var(--accent2);text-decoration:none}
a:hover{text-decoration:underline}

/* Layout */
.container{max-width:860px;margin:0 auto;padding-bottom:80px}

/* Header / Nav */
header{display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:12px;padding:20px 0;border-bottom:1px solid var(--border);
  margin-bottom:40px}
.logo{font-size:1.3rem;font-weight:800;color:var(--text)}
.logo span{color:var(--accent)}
header nav{display:flex;gap:16px}
header nav a{font-size:0.85rem;color:var(--muted);padding:4px 10px;
  border-radius:6px;border:1px solid transparent}
header nav a:hover{color:var(--text);border-color:var(--border);text-decoration:none}
.lang-switcher{font-size:0.82rem;color:var(--muted)}
.lang-switcher a{color:var(--muted);padding:3px 8px;border-radius:5px;
  border:1px solid var(--border)}
.lang-switcher a:hover{color:var(--text);border-color:var(--accent);text-decoration:none}

/* Category & belt badges */
.badge{display:inline-block;padding:4px 12px;border-radius:20px;
  font-size:0.72rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;
  background:#1f2840;color:var(--accent2);border:1px solid #2d2060}
.belt{display:inline-block;padding:3px 10px;border-radius:20px;
  font-size:0.72rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
  margin-left:6px;border:1px solid var(--border)}
.belt-white{color:#e8eaf6;border-color:#3a3a4a;background:#1e1e2e}
.belt-blue{color:var(--blue);border-color:#1e3a6e;background:#0f1e38}
.belt-purple{color:#c084fc;border-color:#4c1d95;background:#1e0f38}
.belt-brown{color:#d97706;border-color:#78350f;background:#241500}
.belt-black{color:#9ca3af;border-color:#374151;background:#111827}

/* H1 */
h1{font-size:2.2rem;font-weight:800;line-height:1.25;margin:12px 0 16px;
  letter-spacing:-0.02em}
@media(max-width:600px){h1{font-size:1.7rem}}

/* Lead paragraph */
h1 + p{font-size:1.05rem;color:#b0b8d4;margin-bottom:32px;line-height:1.8}

/* Section headings */
h2{font-size:1rem;font-weight:700;color:var(--accent2);
  text-transform:uppercase;letter-spacing:.08em;
  display:flex;align-items:center;gap:8px;
  margin:28px 0 12px}
h2::before{content:'';width:3px;height:14px;
  background:linear-gradient(180deg,var(--accent),var(--accent2));
  border-radius:2px;display:block;flex-shrink:0}

/* Content cards */
.card{background:var(--card);border:1px solid var(--border);
  border-radius:14px;padding:24px;margin-bottom:8px}
.card p{color:#c4cce8;font-size:0.95rem;margin-bottom:0}
.card p + p{margin-top:12px}
.card strong{color:var(--text)}

/* Step items inside cards */
.card .step{display:flex;gap:12px;margin-bottom:14px;align-items:flex-start}
.card .step:last-child{margin-bottom:0}
.step-num{min-width:26px;height:26px;border-radius:50%;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  display:flex;align-items:center;justify-content:center;
  font-size:0.72rem;font-weight:700;color:#fff;flex-shrink:0;margin-top:2px}

/* Affiliate box */
.aff-box{background:linear-gradient(135deg,#141926,#1a1040);
  border:1px solid #2d2060;border-radius:14px;
  padding:24px;margin:32px 0;text-align:center}
.aff-box p{color:var(--muted);font-size:0.9rem;margin-bottom:14px}
.aff-btn{display:inline-block;padding:10px 24px;border-radius:10px;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff;font-weight:700;font-size:0.9rem;
  transition:opacity .2s,transform .15s}
.aff-btn:hover{opacity:.88;transform:translateY(-1px);text-decoration:none}

/* FAQ */
.faq{background:var(--card);border:1px solid var(--border);
  border-radius:14px;padding:24px;margin-top:8px}
.faq-q{font-weight:700;color:var(--accent2);margin-bottom:10px;font-size:0.95rem}
.faq p{color:#c4cce8;font-size:0.92rem}

/* Related links */
.related-links{display:grid;
  grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}
.related-links a{display:flex;align-items:center;justify-content:space-between;
  padding:11px 16px;background:var(--card);border:1px solid var(--border);
  border-radius:10px;font-size:0.88rem;color:var(--text);
  transition:border-color .2s,background .2s}
.related-links a::after{content:'→';color:var(--muted);font-size:0.8rem;
  transition:color .2s,transform .2s}
.related-links a:hover{border-color:var(--accent);background:#1a1e30;
  text-decoration:none}
.related-links a:hover::after{color:var(--accent2);transform:translateX(3px)}

footer{padding:28px 0;border-top:1px solid var(--border);
  text-align:center;color:var(--muted);font-size:0.8rem;margin-top:48px}"""

# ── Category index CSS + JS ───────────────────────────────────────────────────
INDEX_CSS = """:root{
  --bg:#080b12;--surface:#0f1420;--card:#141926;
  --border:#1f2840;--text:#e8eaf6;--muted:#6b7699;
  --accent:#7c6af7;--accent2:#a78bfa;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif;
  line-height:1.6;padding:0 16px}
a{color:inherit;text-decoration:none}
nav{max-width:960px;margin:0 auto;padding:20px 0;
  display:flex;align-items:center;justify-content:space-between;
  border-bottom:1px solid var(--border)}
.logo{font-size:1.3rem;font-weight:800}
.logo span{color:var(--accent)}
.lang-switch{display:flex;gap:8px}
.lang-switch a{padding:4px 10px;border-radius:6px;font-size:0.8rem;
  border:1px solid var(--border);color:var(--muted)}
.lang-switch a.active,.lang-switch a:hover{border-color:var(--accent);color:var(--text)}
.container{max-width:960px;margin:0 auto;padding:40px 0 80px}
.page-header{margin-bottom:32px}
.page-header h1{font-size:2rem;font-weight:800;margin-bottom:6px}
.page-header p{color:var(--muted);font-size:0.95rem}
.search-wrap{position:relative;margin-bottom:20px}
.search-wrap input{width:100%;padding:12px 16px 12px 42px;
  background:var(--card);border:1px solid var(--border);border-radius:12px;
  color:var(--text);font-size:0.95rem;outline:none;transition:border-color .2s}
.search-wrap input:focus{border-color:var(--accent)}
.search-wrap input::placeholder{color:var(--muted)}
.search-icon{position:absolute;left:14px;top:50%;transform:translateY(-50%);
  color:var(--muted);font-size:1rem;pointer-events:none}
.filter-bar{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:28px}
.filter-pill{padding:6px 16px;border-radius:20px;font-size:0.82rem;font-weight:600;
  border:1px solid var(--border);color:var(--muted);cursor:pointer;
  background:var(--card);transition:all .18s}
.filter-pill:hover,.filter-pill.active{
  background:var(--accent);border-color:var(--accent);color:#fff}
.cat-section{margin-bottom:28px}
.cat-header{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.cat-header h2{font-size:0.85rem;font-weight:700;color:var(--accent2);
  text-transform:uppercase;letter-spacing:.08em}
.cat-count{font-size:0.72rem;color:var(--muted);
  background:var(--card);border:1px solid var(--border);
  padding:2px 8px;border-radius:10px}
.tech-grid{display:grid;
  grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:8px}
.tech-card{padding:12px 16px;background:var(--card);border:1px solid var(--border);
  border-radius:10px;font-size:0.88rem;font-weight:500;
  display:flex;align-items:center;justify-content:space-between;
  transition:border-color .18s,transform .15s,background .18s}
.tech-card:hover{border-color:var(--accent);background:#1a1e30;
  transform:translateY(-1px)}
.tech-card .arrow{color:var(--muted);font-size:0.8rem;transition:color .18s}
.tech-card:hover .arrow{color:var(--accent2)}
.no-results{text-align:center;padding:60px 0;color:var(--muted)}
footer{max-width:960px;margin:0 auto;padding:24px 0;
  border-top:1px solid var(--border);text-align:center;
  color:var(--muted);font-size:0.8rem}"""

INDEX_JS = """
const pills = document.querySelectorAll('.filter-pill');
const searchInput = document.getElementById('tech-search');
const catSections = document.querySelectorAll('.cat-section');
let activeFilter = 'all';
function applyFilter(){
  const q = searchInput ? searchInput.value.toLowerCase() : '';
  let any = false;
  catSections.forEach(sec=>{
    const cat = sec.dataset.cat;
    const cards = sec.querySelectorAll('.tech-card');
    let vis = false;
    cards.forEach(card=>{
      const name = card.querySelector('.tech-name').textContent.toLowerCase();
      const show = (activeFilter==='all'||cat===activeFilter) && name.includes(q);
      card.style.display = show ? '' : 'none';
      if(show) vis = true;
    });
    sec.style.display = vis ? '' : 'none';
    if(vis) any = true;
  });
  let nr = document.querySelector('.no-results');
  if(!nr){nr=document.createElement('p');nr.className='no-results';
    nr.textContent='No techniques found.';
    document.querySelector('.container').appendChild(nr);}
  nr.style.display = any ? 'none' : '';
}
pills.forEach(p=>{p.addEventListener('click',()=>{
  pills.forEach(x=>x.classList.remove('active'));
  p.classList.add('active');
  activeFilter=p.dataset.filter;
  applyFilter();
})});
if(searchInput) searchInput.addEventListener('input',applyFilter);
applyFilter();"""

CAT_FILTER = {
    "choke":"submission","strangulation":"submission",
    "joint lock":"submission","leg lock":"submission",
    "guard":"guard","passing":"passing","position":"position",
    "sweep":"sweep","takedown":"takedown","transition":"transition",
    "defense":"defense",
}

def md_to_html(text):
    """Convert **bold** and <br> step lists to clean HTML."""
    # **text** → <strong>text</strong>
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Split on <br> and turn into step items if multiple steps detected
    parts = [p.strip() for p in re.split(r'<br\s*/?>', text) if p.strip()]
    if len(parts) > 2:
        items = ""
        for i, part in enumerate(parts, 1):
            items += f'<div class="step"><div class="step-num">{i}</div><div>{part}</div></div>\n'
        return items
    return '<br>'.join(parts)

def patch_article(path):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    # 1) Replace CSS
    html = re.sub(r'<style>.*?</style>',
        f'<style>\n{ARTICLE_CSS}\n</style>', html, count=1, flags=re.DOTALL)

    # 2) Convert **bold** inside .card <p> tags
    def fix_card(m):
        inner = m.group(1)
        inner = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', inner)
        # Turn <br>-separated steps into step divs
        parts = [p.strip() for p in re.split(r'<br\s*/?>', inner) if p.strip()]
        if len(parts) > 2:
            items = "".join(
                f'<div class="step"><div class="step-num">{i}</div><div>{p}</div></div>'
                for i, p in enumerate(parts, 1))
            return f'<div class="card">{items}</div>'
        return f'<div class="card"><p>{inner}</p></div>'

    html = re.sub(r'<div class="card"><p>(.*?)</p></div>',
                  fix_card, html, flags=re.DOTALL)

    # 3) Fix YOUR_USERNAME in URLs
    html = html.replace("YOUR_USERNAME.github.io/bjj-wiki", "wiki.bjj-app.net")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return True

def patch_index_html(path, lang):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    cats_data = {}
    for m in re.finditer(
        r'<div class=["\']cat-section["\'][^>]*data-cat=["\']([^"\']+)["\'][^>]*>.*?'
        r'<h2[^>]*>(.*?)</h2>.*?<div class=["\']tech-grid["\']>(.*?)</div>\s*</div>',
        html, re.DOTALL):
        filter_key, cat_name, grid_html = m.group(1), m.group(2), m.group(3)
        cards = re.findall(
            r'<a class=["\']tech-card["\'][^>]*href=["\']([^"\']+)["\'][^>]*>'
            r'<span class=["\']tech-name["\']>(.*?)</span>', grid_html)
        if not cards:
            # fallback: try old format
            cards = re.findall(r'href=["\']([^"\']+)["\'].*?class=["\']tech-name["\']>(.*?)<', grid_html)
        cats_data[cat_name] = (filter_key, cards)

    # If no new format found, try old cat-card format
    if not cats_data:
        for m in re.finditer(
            r'<div class=["\']cat-card["\'][^>]*>.*?<h2[^>]*>(.*?)</h2>.*?'
            r'<div class=["\']tech-links["\']>(.*?)</div>\s*</div>',
            html, re.DOTALL):
            cat = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            hrefs = re.findall(r'href=["\']([^"\']+)["\'].*?>(.*?)</a>', m.group(2))
            fk = "other"
            for k, v in CAT_FILTER.items():
                if k in cat.lower():
                    fk = v; break
            cats_data[cat] = (fk, hrefs)

    TRANS = {
        "en": ("All BJJ Techniques",
               "Browse all guards, submissions, positions and more.",
               "Search techniques...", "All"),
        "ja": ("全BJJ技一覧",
               "ガード、サブミッション、ポジションなど全技術を網羅。",
               "技を検索...", "すべて"),
        "pt": ("Todas as Técnicas de BJJ",
               "Explore guardas, finalizações, posições e mais.",
               "Buscar técnicas...", "Todos"),
    }
    title, sub, placeholder, all_label = TRANS.get(lang, TRANS["en"])

    # Collect unique filter keys
    filters = {}
    filter_labels = {
        "submission":"Submission","guard":"Guard","passing":"Passing",
        "position":"Position","sweep":"Sweep","takedown":"Takedown",
        "transition":"Transition","defense":"Defense","other":"Other",
    }
    for _, (fk, _) in cats_data.items():
        if fk not in filters:
            filters[fk] = filter_labels.get(fk, fk.title())

    pills = f'<button class="filter-pill active" data-filter="all">{all_label}</button>\n'
    for fk, fl in filters.items():
        pills += f'    <button class="filter-pill" data-filter="{fk}">{fl}</button>\n'

    sections = ""
    for cat, (fk, hrefs) in cats_data.items():
        cards = "".join(
            f'<a class="tech-card" href="{href}">'
            f'<span class="tech-name">{name}</span>'
            f'<span class="arrow">→</span></a>\n'
            for href, name in hrefs)
        sections += f"""
<div class="cat-section" data-cat="{fk}">
  <div class="cat-header">
    <h2>{cat}</h2><span class="cat-count">{len(hrefs)}</span>
  </div>
  <div class="tech-grid">
{cards}  </div>
</div>"""

    lang_links = ""
    for lc, ln in [("en","EN"),("ja","日本語"),("pt","PT")]:
        active = ' class="active"' if lc == lang else ''
        prefix = "../" if lc != lang else ""
        lang_links += f'<a href="{prefix}{lc}/index.html"{active}>{ln}</a>'

    out = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
  <link rel="icon" href="https://wiki.bjj-app.net/favicon.svg" type="image/svg+xml">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | BJJ Wiki</title>
<style>
{INDEX_CSS}
</style>
</head>
<body>
<nav>
  <a href="../index.html" class="logo">BJJ<span>Wiki</span></a>
  <div class="lang-switch">{lang_links}</div>
</nav>
<div class="container">
  <div class="page-header">
    <h1>{title}</h1>
    <p>{sub}</p>
  </div>
  <div class="search-wrap">
    <span class="search-icon">🔍</span>
    <input type="text" id="tech-search" placeholder="{placeholder}">
  </div>
  <div class="filter-bar">
    {pills}
  </div>
  {sections}
</div>
<footer><p>BJJ Wiki — Free & Open Knowledge</p></footer>
<script>{INDEX_JS}</script>
</body>
</html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"[OK] index → {path}")

def main():
    art = 0
    for lang in ["en","ja","pt"]:
        idx = os.path.join(BASE, lang, "index.html")
        if os.path.exists(idx):
            patch_index_html(idx, lang)
        for f in glob.glob(os.path.join(BASE, lang, "*.html")):
            if os.path.basename(f) == "index.html": continue
            patch_article(f)
            art += 1
    print(f"\n[完了] {art}件の記事を更新しました")

if __name__ == "__main__":
    main()
