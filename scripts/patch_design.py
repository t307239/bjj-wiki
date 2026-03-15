#!/usr/bin/env python3
"""
BJJ Wiki Design Patch Script
Usage: python3 patch_design.py
Run from ~/Claude/bjj-wiki/
"""
import os, re, glob

BASE = os.path.expanduser("~/Claude/bjj-wiki")

# ── New CSS for article pages ─────────────────────────────────────────────────
ARTICLE_CSS = """
  :root{
    --bg:#080b12;--surface:#0f1420;--card:#141926;
    --border:#1f2840;--text:#e8eaf6;--muted:#6b7699;
    --accent:#7c6af7;--accent2:#a78bfa;--green:#22c55e;
    --red:#ef4444;--yellow:#f59e0b;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--text);
    font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif;
    line-height:1.7;padding:0 16px}
  a{color:var(--accent2);text-decoration:none}
  a:hover{text-decoration:underline}

  /* Nav */
  nav{max-width:860px;margin:0 auto;padding:20px 0;
    display:flex;align-items:center;justify-content:space-between;
    border-bottom:1px solid var(--border)}
  .logo{font-size:1.3rem;font-weight:800;color:var(--text)}
  .logo span{color:var(--accent)}
  .nav-links{display:flex;gap:16px;font-size:0.85rem;color:var(--muted)}
  .nav-links a{color:var(--muted)}
  .nav-links a:hover{color:var(--text)}

  /* Hero */
  .hero{max-width:860px;margin:48px auto 0;padding:40px;
    background:linear-gradient(135deg,#141926 0%,#1a1440 100%);
    border:1px solid var(--border);border-radius:20px;position:relative;overflow:hidden}
  .hero::before{content:'';position:absolute;top:-60px;right:-60px;
    width:200px;height:200px;background:var(--accent);opacity:0.06;border-radius:50%}
  .category-badge{display:inline-block;padding:4px 12px;border-radius:20px;
    font-size:0.75rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;
    background:#1f2840;color:var(--accent2);border:1px solid var(--border);margin-bottom:16px}
  .hero h1{font-size:2.4rem;font-weight:800;line-height:1.2;margin-bottom:12px}
  .hero-meta{display:flex;gap:12px;flex-wrap:wrap;margin-top:16px}
  .badge{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;
    border-radius:8px;font-size:0.8rem;font-weight:600;border:1px solid var(--border);
    background:var(--card)}
  .badge.beginner{color:var(--green);border-color:#166534}
  .badge.intermediate{color:var(--yellow);border-color:#78350f}
  .badge.advanced{color:var(--red);border-color:#7f1d1d}

  /* Content */
  .content{max-width:860px;margin:32px auto 80px;
    display:grid;grid-template-columns:1fr 280px;gap:24px}
  @media(max-width:700px){.content{grid-template-columns:1fr}}
  .main-col{}
  .side-col{}

  /* Sections */
  .section{background:var(--card);border:1px solid var(--border);
    border-radius:16px;padding:28px;margin-bottom:20px}
  .section h2{font-size:1rem;font-weight:700;color:var(--accent2);
    text-transform:uppercase;letter-spacing:.08em;margin-bottom:16px;
    display:flex;align-items:center;gap:8px}
  .section h2::before{content:'';width:3px;height:16px;
    background:var(--accent);border-radius:2px;display:block}
  .section p{color:#c4c9e0;margin-bottom:12px;font-size:0.95rem}
  .section p:last-child{margin-bottom:0}
  .section ul,.section ol{padding-left:20px;color:#c4c9e0;font-size:0.95rem}
  .section li{margin-bottom:6px}

  /* Steps */
  .steps{list-style:none;padding:0}
  .steps li{display:flex;gap:12px;margin-bottom:16px;align-items:flex-start}
  .step-num{min-width:28px;height:28px;border-radius:50%;
    background:linear-gradient(135deg,var(--accent),var(--accent2));
    display:flex;align-items:center;justify-content:center;
    font-size:0.75rem;font-weight:700;color:white;flex-shrink:0}

  /* Sidebar cards */
  .info-card{background:var(--card);border:1px solid var(--border);
    border-radius:16px;padding:20px;margin-bottom:16px}
  .info-card h3{font-size:0.85rem;font-weight:700;color:var(--muted);
    text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px}
  .info-row{display:flex;justify-content:space-between;align-items:center;
    padding:8px 0;border-bottom:1px solid var(--border);font-size:0.88rem}
  .info-row:last-child{border-bottom:none}
  .info-row .label{color:var(--muted)}
  .info-row .value{font-weight:600}

  /* Tag list */
  .tag-list{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
  .tag{padding:4px 10px;border-radius:6px;font-size:0.78rem;
    background:#1f2840;color:var(--muted);border:1px solid var(--border)}

  /* Related */
  .related-links{display:flex;flex-direction:column;gap:8px}
  .related-link{padding:10px 14px;border-radius:10px;border:1px solid var(--border);
    background:var(--surface);font-size:0.88rem;color:var(--text);
    transition:border-color .2s,background .2s}
  .related-link:hover{border-color:var(--accent);background:#141926;text-decoration:none}

  /* Lang switch */
  .lang-switch{display:flex;gap:8px}
  .lang-switch a{padding:4px 10px;border-radius:6px;font-size:0.8rem;
    border:1px solid var(--border);color:var(--muted)}
  .lang-switch a.active,.lang-switch a:hover{border-color:var(--accent);color:var(--text)}

  footer{max-width:860px;margin:0 auto;padding:24px 0;
    border-top:1px solid var(--border);text-align:center;
    color:var(--muted);font-size:0.8rem}
"""

# ── New CSS + JS for category index pages ────────────────────────────────────
INDEX_CSS = """
  :root{
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
  .page-header{margin-bottom:36px}
  .page-header h1{font-size:2rem;font-weight:800;margin-bottom:8px}
  .page-header p{color:var(--muted)}

  /* Search */
  .search-wrap{position:relative;margin-bottom:24px}
  .search-wrap input{width:100%;padding:12px 16px 12px 44px;
    background:var(--card);border:1px solid var(--border);border-radius:12px;
    color:var(--text);font-size:0.95rem;outline:none;
    transition:border-color .2s}
  .search-wrap input:focus{border-color:var(--accent)}
  .search-wrap input::placeholder{color:var(--muted)}
  .search-icon{position:absolute;left:14px;top:50%;transform:translateY(-50%);
    color:var(--muted);pointer-events:none}

  /* Filter pills */
  .filter-bar{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:28px}
  .filter-pill{padding:6px 16px;border-radius:20px;font-size:0.83rem;font-weight:600;
    border:1px solid var(--border);color:var(--muted);cursor:pointer;
    background:var(--card);transition:all .2s}
  .filter-pill:hover,.filter-pill.active{
    background:var(--accent);border-color:var(--accent);color:white}

  /* Category grid */
  .cat-section{margin-bottom:32px}
  .cat-header{display:flex;align-items:center;gap:10px;margin-bottom:16px}
  .cat-header h2{font-size:1rem;font-weight:700;color:var(--accent2)}
  .cat-count{font-size:0.75rem;color:var(--muted);
    background:var(--card);border:1px solid var(--border);
    padding:2px 8px;border-radius:10px}
  .tech-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}
  .tech-card{padding:14px 16px;background:var(--card);border:1px solid var(--border);
    border-radius:12px;font-size:0.88rem;font-weight:500;
    transition:border-color .2s,transform .15s,background .2s;
    display:flex;align-items:center;justify-content:space-between}
  .tech-card:hover{border-color:var(--accent);background:#1a1e30;
    transform:translateY(-1px)}
  .tech-card .arrow{color:var(--muted);font-size:0.75rem;transition:color .2s}
  .tech-card:hover .arrow{color:var(--accent2)}

  .no-results{text-align:center;padding:60px 0;color:var(--muted)}
  footer{max-width:960px;margin:0 auto;padding:24px 0;
    border-top:1px solid var(--border);text-align:center;
    color:var(--muted);font-size:0.8rem}
"""

INDEX_JS = """
  const pills = document.querySelectorAll('.filter-pill');
  const searchInput = document.querySelector('#tech-search');
  const catSections = document.querySelectorAll('.cat-section');
  let activeFilter = 'all';

  function applyFilter() {
    const q = searchInput ? searchInput.value.toLowerCase() : '';
    let anyVisible = false;
    catSections.forEach(sec => {
      const cat = sec.dataset.cat;
      const cards = sec.querySelectorAll('.tech-card');
      let secVisible = false;
      cards.forEach(card => {
        const name = card.querySelector('.tech-name').textContent.toLowerCase();
        const matchFilter = activeFilter === 'all' || cat === activeFilter;
        const matchSearch = name.includes(q);
        const show = matchFilter && matchSearch;
        card.style.display = show ? '' : 'none';
        if (show) secVisible = true;
      });
      sec.style.display = secVisible ? '' : 'none';
      if (secVisible) anyVisible = true;
    });
    let noRes = document.querySelector('.no-results');
    if (!noRes) {
      noRes = document.createElement('p');
      noRes.className = 'no-results';
      noRes.textContent = 'No techniques found.';
      document.querySelector('.container').appendChild(noRes);
    }
    noRes.style.display = anyVisible ? 'none' : '';
  }

  pills.forEach(p => {
    p.addEventListener('click', () => {
      pills.forEach(x => x.classList.remove('active'));
      p.classList.add('active');
      activeFilter = p.dataset.filter;
      applyFilter();
    });
  });

  if (searchInput) searchInput.addEventListener('input', applyFilter);
  applyFilter();
"""

# ── Category metadata ─────────────────────────────────────────────────────────
CAT_META = {
    "Choke": ("Submission", "#ef4444"),
    "Strangulation": ("Submission", "#ef4444"),
    "Joint Lock": ("Submission", "#f97316"),
    "Leg Lock": ("Submission", "#f97316"),
    "Guard": ("Guard", "#3b82f6"),
    "Passing": ("Passing", "#8b5cf6"),
    "Position": ("Position", "#22c55e"),
    "Sweep": ("Sweep", "#f59e0b"),
    "Takedown": ("Takedown", "#06b6d4"),
    "Transition": ("Transition", "#a78bfa"),
    "Defense": ("Defense", "#6b7280"),
}

def get_filter_categories(cats):
    filters = {"all": "All"}
    for c in cats:
        for key, (label, _) in CAT_META.items():
            if key.lower() in c.lower():
                filters[label.lower()] = label
                break
    return filters

def patch_index_html(path, lang):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    # Extract existing cat sections
    cats = re.findall(r'<h2[^>]*>(.*?)</h2>', html)
    links_by_cat = {}
    for m in re.finditer(r'<h2[^>]*>(.*?)</h2>.*?<div class=["\']tech-links["\']>(.*?)</div>', html, re.DOTALL):
        cat = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        links_raw = m.group(2)
        hrefs = re.findall(r'href=["\']([^"\']+)["\'].*?>(.*?)</a>', links_raw)
        links_by_cat[cat] = hrefs

    # Build category sections
    # Translations
    TRANS = {
        "en": {"title": "All BJJ Techniques", "sub": "Browse all guards, submissions, positions and more.",
               "search": "Search techniques...", "all_filter": "All"},
        "ja": {"title": "全BJJ技一覧", "sub": "ガード、サブミッション、ポジションなど全技術を網羅。",
               "search": "技を検索...", "all_filter": "すべて"},
        "pt": {"title": "Todas as Técnicas de BJJ", "sub": "Explore guardas, finalizações, posições e mais.",
               "search": "Buscar técnicas...", "all_filter": "Todos"},
    }
    t = TRANS.get(lang, TRANS["en"])

    # Collect all filter categories
    filters_seen = {}
    for cat in links_by_cat:
        for key, (label, _) in CAT_META.items():
            if key.lower() in cat.lower():
                filters_seen[label.lower()] = label
                break

    # Filter pills HTML
    pills_html = f'<button class="filter-pill active" data-filter="all">{t["all_filter"]}</button>\n'
    for fk, fl in filters_seen.items():
        pills_html += f'    <button class="filter-pill" data-filter="{fk}">{fl}</button>\n'

    # Category sections HTML
    sections_html = ""
    for cat, hrefs in links_by_cat.items():
        filter_key = "other"
        for key, (label, _) in CAT_META.items():
            if key.lower() in cat.lower():
                filter_key = label.lower()
                break
        count = len(hrefs)
        cards = ""
        for href, name in hrefs:
            cards += f'      <a class="tech-card" href="{href}"><span class="tech-name">{name}</span><span class="arrow">→</span></a>\n'
        sections_html += f"""
  <div class="cat-section" data-cat="{filter_key}">
    <div class="cat-header">
      <h2>{cat}</h2><span class="cat-count">{count}</span>
    </div>
    <div class="tech-grid">
{cards}    </div>
  </div>
"""

    lang_links = ""
    langs = [("en","EN"), ("ja","日本語"), ("pt","PT")]
    for lc, ln in langs:
        active = ' class="active"' if lc == lang else ''
        rel = "../" if lang != lc else ""
        lang_links += f'<a href="{rel}{lc}/index.html"{active}>{ln}</a>'

    new_html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{t["title"]} | BJJ Wiki</title>
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
    <h1>{t["title"]}</h1>
    <p>{t["sub"]}</p>
  </div>
  <div class="search-wrap">
    <span class="search-icon">🔍</span>
    <input type="text" id="tech-search" placeholder="{t["search"]}">
  </div>
  <div class="filter-bar">
    {pills_html}
  </div>
  {sections_html}
</div>
<footer><p>BJJ Wiki — Free & Open Knowledge</p></footer>
<script>
{INDEX_JS}
</script>
</body>
</html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"[OK] {path}")

def patch_article_css(path):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    # Replace <style> block only
    new_html = re.sub(
        r'<style>.*?</style>',
        f'<style>\n{ARTICLE_CSS}\n</style>',
        html, count=1, flags=re.DOTALL
    )

    # Improve nav: wrap logo in nav tag if not already
    # Add .category-badge class to category span if present
    # Wrap content sections in .section divs if not already
    # (Best effort: only do CSS replacement to avoid breaking content)

    if new_html != html:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_html)
        return True
    return False

def main():
    count = 0
    # Patch category index pages
    for lang in ["en", "ja", "pt"]:
        idx = os.path.join(BASE, lang, "index.html")
        if os.path.exists(idx):
            patch_index_html(idx, lang)

    # Patch article pages
    for lang in ["en", "ja", "pt"]:
        for html_file in glob.glob(os.path.join(BASE, lang, "*.html")):
            if os.path.basename(html_file) == "index.html":
                continue
            if patch_article_css(html_file):
                count += 1

    print(f"\n[完了] {count}件の記事ページのCSSを更新しました")

if __name__ == "__main__":
    main()
