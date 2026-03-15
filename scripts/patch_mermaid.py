#!/usr/bin/env python3
"""
BJJ Wiki Mermaid.js Patch
技ページに「関連技フローチャート」を追加
Usage: python3 patch_mermaid.py
Run from ~/Claude/bjj-wiki/
"""
import os, re, glob

BASE = os.path.expanduser("~/Claude/bjj-wiki")

# カテゴリ別の色設定
CAT_COLORS = {
    "choke":      ("#ef4444", "#7f1d1d"),
    "joint lock": ("#f97316", "#7c2d12"),
    "leg lock":   ("#f59e0b", "#78350f"),
    "guard":      ("#3b82f6", "#1e3a8a"),
    "passing":    ("#8b5cf6", "#4c1d95"),
    "position":   ("#22c55e", "#14532d"),
    "sweep":      ("#06b6d4", "#164e63"),
    "takedown":   ("#ec4899", "#831843"),
    "transition": ("#a78bfa", "#4c1d95"),
    "defense":    ("#6b7280", "#1f2937"),
}

def slug_to_name(slug):
    """rear-naked-choke → Rear Naked Choke"""
    return slug.replace(".html", "").replace("-", " ").title()

def get_cat_color(category_text):
    cat = category_text.lower()
    for key, colors in CAT_COLORS.items():
        if key in cat:
            return colors
    return ("#7c6af7", "#2e1065")

def make_node_id(name):
    """Make safe Mermaid node ID"""
    return re.sub(r'[^a-zA-Z0-9]', '_', name)[:20]

def build_mermaid(current_name, category, related_links):
    """
    Build a Mermaid flowchart showing:
    - Current technique (center, highlighted)
    - Category node
    - Related techniques
    """
    accent, _ = get_cat_color(category)
    cur_id = make_node_id(current_name)

    lines = ["graph LR"]

    # Category node
    cat_id = make_node_id(category)
    lines.append(f'    {cat_id}["{category}"]:::catNode')
    lines.append(f'    {cat_id} --> {cur_id}')

    # Current technique (center)
    lines.append(f'    {cur_id}["{current_name}"]:::currentNode')

    # Related techniques
    added = set()
    for href, name in related_links[:6]:  # max 6 related
        rel_id = make_node_id(name)
        if rel_id in added or rel_id == cur_id:
            continue
        added.add(rel_id)
        lines.append(f'    {cur_id} -.-> {rel_id}["{name}"]:::relNode')

    # Styles
    lines.append(f'    classDef currentNode fill:{accent},stroke:#fff,color:#fff,font-weight:700')
    lines.append(f'    classDef relNode fill:#141926,stroke:#1f2840,color:#a78bfa')
    lines.append(f'    classDef catNode fill:#1f2840,stroke:#7c6af7,color:#7c6af7,font-style:italic')

    return "\n".join(lines)

def patch_article(path):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    # Skip if already patched
    if 'mermaid' in html and 'classDef currentNode' in html:
        return False

    # Extract technique name from <h1>
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if not h1_match:
        return False
    # Use the filename as fallback name
    filename = os.path.splitext(os.path.basename(path))[0]
    current_name = slug_to_name(filename)

    # Extract category badge
    badge_match = re.search(r'class="badge"[^>]*>\s*(.*?)\s*</span>', html)
    category = badge_match.group(1) if badge_match else "Technique"

    # Extract related links
    related_section = re.search(
        r'<div class="related-links">(.*?)</div>', html, re.DOTALL)
    related_links = []
    if related_section:
        for m in re.finditer(r'href="([^"]+)"[^>]*>(.*?)</a>', related_section.group(1)):
            href = m.group(1)
            name = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            if name:
                related_links.append((href, name))

    if not related_links:
        return False

    # Build diagram
    diagram = build_mermaid(current_name, category, related_links)

    # Mermaid CSS
    mermaid_css = """
  /* Mermaid diagram container */
  .mermaid-wrap{background:var(--card);border:1px solid var(--border);
    border-radius:14px;padding:24px;margin-bottom:8px;overflow-x:auto}
  .mermaid-wrap h3{font-size:0.82rem;font-weight:700;color:var(--muted);
    text-transform:uppercase;letter-spacing:.08em;margin-bottom:16px}
  .mermaid{max-width:100%}
  .mermaid svg{max-width:100%;height:auto}"""

    # Mermaid HTML block
    mermaid_html = f"""
  <div class="mermaid-wrap">
    <h3>Technique Map</h3>
    <div class="mermaid">
{diagram}
    </div>
  </div>
"""

    # Insert mermaid CSS into <style> block
    if mermaid_css.strip() not in html:
        html = html.replace('</style>', mermaid_css + '\n</style>', 1)

    # Insert diagram before <h2> of first section (after lead paragraph)
    # Find position: after first <p> that follows <h1>
    insert_pattern = r'(</p>\s*\n\s*<h2)'
    match = re.search(insert_pattern, html)
    if match:
        html = html[:match.start()] + '</p>\n' + mermaid_html + '\n  <h2' + html[match.end():]
    else:
        # Fallback: insert before first <h2>
        h2_match = re.search(r'<h2', html)
        if h2_match:
            html = html[:h2_match.start()] + mermaid_html + html[h2_match.start():]

    # Add Mermaid.js CDN before </body>
    mermaid_script = """<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({startOnLoad:true,theme:'dark',
  themeVariables:{darkMode:true,background:'#141926',primaryColor:'#7c6af7',
    primaryTextColor:'#e8eaf6',lineColor:'#6b7699',edgeLabelBackground:'#141926'}
});</script>"""

    if 'mermaid.min.js' not in html:
        html = html.replace('</body>', mermaid_script + '\n</body>')

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return True

def main():
    count = 0
    skip = 0
    for lang in ["en", "ja", "pt"]:
        files = glob.glob(os.path.join(BASE, lang, "*.html"))
        for f in files:
            if os.path.basename(f) == "index.html":
                continue
            if patch_article(f):
                count += 1
            else:
                skip += 1
    print(f"[完了] {count}件にMermaid追加, {skip}件スキップ")

if __name__ == "__main__":
    main()
