#!/usr/bin/env python3
"""
Generate search.json per language from existing HTML pages.
Output: en/search.json, ja/search.json, pt/search.json
Each entry: {slug, title, desc, category, belt}
"""
import os, re, json

WIKI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKIP_FILES = {"index.html", "404.html"}

CATEGORY_KEYWORDS = {
    "choke":      ["choke","strangle","strangulation","チョーク","絞め","estrangulamento"],
    "submission": ["submission","tap","lock","kimura","armbar","triangle","heel","estrangulamento","finalização","サブミッション","絞め","関節"],
    "guard":      ["guard","closed guard","open guard","butterfly","spider","dlr","ガード","guarda"],
    "passing":    ["pass","passing","toreando","smash","stack","パス","passagem"],
    "sweep":      ["sweep","スウィープ","raspagem"],
    "takedown":   ["takedown","throw","osoto","seoi","single","double","テイクダウン","queda"],
    "escape":     ["escape","逃げ","脱出","fuga","saída"],
    "position":   ["mount","back","side control","turtle","north south","マウント","バック","posição"],
    "conditioning":["conditioning","strength","nutrition","flexibility","コンディショニング","condicionamento"],
    "concepts":   ["concept","principle","theory","コンセプト","conceito","strategy","戦略"],
}

def extract_category(title_lower, desc_lower, slug):
    slug_lower = slug.lower()
    # Try to detect category from slug/title/desc
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in slug_lower or kw in title_lower:
                return cat
    # Fallback from description
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                return cat
    return "technique"

def extract_belt(content):
    """Detect difficulty belt level from HTML content."""
    c = content.lower()
    if "black belt" in c or "黒帯" in c or "faixa preta" in c:
        return "black"
    if "brown belt" in c or "茶帯" in c or "faixa marrom" in c:
        return "brown"
    if "purple belt" in c or "紫帯" in c or "faixa roxa" in c:
        return "purple"
    if "blue belt" in c or "青帯" in c or "faixa azul" in c:
        return "blue"
    return "white"

def parse_html(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None

    # Title
    m = re.search(r"<title>([^<]+)</title>", content, re.IGNORECASE)
    title = m.group(1).strip() if m else ""
    # Remove " | BJJ Wiki" suffix etc.
    title = re.sub(r"\s*[\|—\-]\s*(BJJ Wiki|BJJ ウィキ|BJJ Guia).*$", "", title).strip()

    # Meta description
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', content, re.IGNORECASE)
    if not m:
        m = re.search(r'<meta\s+content="([^"]*)"\s+name="description"', content, re.IGNORECASE)
    desc = m.group(1).strip() if m else ""

    # Category from meta keywords or breadcrumb
    m = re.search(r'class="breadcrumb[^"]*"[^>]*>.*?<span[^>]*>([^<]+)</span>', content, re.IGNORECASE | re.DOTALL)
    cat_hint = m.group(1).strip().lower() if m else ""

    category = extract_category(title.lower() + " " + cat_hint, desc.lower(), os.path.basename(filepath))
    belt = extract_belt(content[:2000])

    return {"title": title, "desc": desc, "category": category, "belt": belt}

def build_language(lang):
    lang_dir = os.path.join(WIKI_DIR, lang)
    if not os.path.isdir(lang_dir):
        print(f"  ⚠️  {lang}/ not found")
        return []

    entries = []
    files = sorted(f for f in os.listdir(lang_dir)
                   if f.endswith(".html") and f not in SKIP_FILES)

    for fname in files:
        slug = fname.replace(".html", "")
        result = parse_html(os.path.join(lang_dir, fname))
        if not result or not result["title"]:
            continue
        entries.append({
            "s": slug,
            "t": result["title"],
            "d": result["desc"][:120] if result["desc"] else "",
            "c": result["category"],
            "b": result["belt"],
        })

    out_path = os.path.join(lang_dir, "search.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, separators=(",", ":"))

    size_kb = os.path.getsize(out_path) / 1024
    print(f"  ✅ {lang}/search.json — {len(entries)} entries ({size_kb:.0f}KB)")
    return entries

if __name__ == "__main__":
    print("Building search.json...")
    for lang in ["en", "ja", "pt"]:
        build_language(lang)
    print("Done.")
