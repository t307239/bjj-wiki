#!/usr/bin/env python3
"""
BJJ Wiki YouTube Patch
各記事に関連YouTube動画を自動埋め込み
Usage: python3 patch_youtube.py [--limit N] [--lang en|ja|pt|all]
Run from ~/Claude/bjj-wiki/
"""
import os, re, glob, json, time, urllib.request, urllib.parse, argparse

BASE    = os.path.expanduser("~/Claude/bjj-wiki")
SECRETS = os.path.expanduser("~/.secrets")
CACHE   = os.path.join(BASE, "youtube_cache.json")

def load_secrets():
    secrets = {}
    try:
        with open(SECRETS) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    secrets[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return secrets

def load_cache():
    try:
        with open(CACHE) as f:
            return json.load(f)
    except:
        return {}

def save_cache(cache):
    with open(CACHE, "w") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def search_youtube(query, api_key):
    """YouTube Data API v3で検索、動画IDとタイトルを返す"""
    params = urllib.parse.urlencode({
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 1,
        "relevanceLanguage": "en",
        "safeSearch": "none",
        "videoDuration": "medium",  # 4〜20分：タイムスタンプあり動画を優先
        "key": api_key,
    })
    url = f"https://www.googleapis.com/youtube/v3/search?{params}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        items = data.get("items", [])
        if items:
            vid_id = items[0]["id"]["videoId"]
            title  = items[0]["snippet"]["title"]
            return vid_id, title
    except Exception as e:
        print(f"  [YouTube ERROR] {e}")
    return None, None

def make_iframe(vid_id, title):
    return f"""
  <div class="yt-wrap">
    <h3 class="yt-label">関連動画 / Related Video</h3>
    <div class="yt-frame-wrap">
      <iframe
        src="https://www.youtube.com/embed/{vid_id}?rel=0&modestbranding=1"
        title="{title}"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen
        loading="lazy">
      </iframe>
    </div>
  </div>"""

YT_CSS = """
  /* YouTube embed */
  .yt-wrap{background:var(--card);border:1px solid var(--border);
    border-radius:14px;padding:24px;margin-bottom:8px}
  .yt-label{font-size:0.82rem;font-weight:700;color:var(--muted);
    text-transform:uppercase;letter-spacing:.08em;margin-bottom:14px}
  .yt-frame-wrap{position:relative;padding-bottom:56.25%;height:0;overflow:hidden;
    border-radius:10px}
  .yt-frame-wrap iframe{position:absolute;top:0;left:0;width:100%;height:100%}"""

def patch_file(path, vid_id, yt_title):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    # スキップ: 既にYT埋め込み済み
    if "yt-wrap" in html:
        return False

    # CSSを追加
    if YT_CSS.strip() not in html:
        html = html.replace("</style>", YT_CSS + "\n</style>", 1)

    # アフィリボックスの前 or Related Techniquesの前に挿入
    iframe_html = make_iframe(vid_id, yt_title)
    if 'class="aff-box"' in html:
        html = html.replace('<div class="aff-box">', iframe_html + '\n  <div class="aff-box">', 1)
    elif 'class="related-links"' in html:
        html = re.sub(r'(<h2[^>]*>.*?[Rr]elated)', iframe_html + r'\n  \1', html, count=1)
    else:
        html = html.replace("</div>\n</body>", iframe_html + "\n</div>\n</body>", 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return True

# 技名→YouTube検索クエリのマッピング
SEARCH_QUERIES = {
    "rear-naked-choke":   "BJJ rear naked choke tutorial technique",
    "triangle-choke":     "BJJ triangle choke tutorial",
    "guillotine-choke":   "BJJ guillotine choke technique",
    "armbar":             "BJJ armbar tutorial",
    "kimura":             "BJJ kimura lock tutorial",
    "americana":          "BJJ americana technique",
    "omoplata":           "BJJ omoplata tutorial",
    "heel-hook":          "BJJ heel hook technique tutorial",
    "inside-heel-hook":   "BJJ inside heel hook tutorial",
    "outside-heel-hook":  "BJJ outside heel hook tutorial",
    "berimbolo":          "BJJ berimbolo tutorial technique",
    "closed-guard":       "BJJ closed guard basics tutorial",
    "open-guard":         "BJJ open guard tutorial",
    "half-guard":         "BJJ half guard tutorial",
    "de-la-riva-guard":   "BJJ de la riva guard tutorial",
    "spider-guard":       "BJJ spider guard tutorial",
    "butterfly-guard":    "BJJ butterfly guard tutorial",
    "x-guard":            "BJJ x guard tutorial",
    "rubber-guard":       "BJJ rubber guard tutorial",
    "worm-guard":         "BJJ worm guard tutorial",
    "scissor-sweep":      "BJJ scissor sweep tutorial",
    "hip-bump-sweep":     "BJJ hip bump sweep tutorial",
    "flower-sweep":       "BJJ flower sweep tutorial",
    "pendulum-sweep":     "BJJ pendulum sweep tutorial",
    "mount":              "BJJ mount position tutorial",
    "back-mount":         "BJJ back mount tutorial",
    "side-control":       "BJJ side control tutorial",
    "north-south":        "BJJ north south position tutorial",
    "knee-on-belly":      "BJJ knee on belly tutorial",
    "turtle-position":    "BJJ turtle position tutorial",
    "guard-pass":         "BJJ guard passing tutorial",
    "torreando-pass":     "BJJ torreando pass tutorial",
    "knee-slice-pass":    "BJJ knee slice pass tutorial",
    "leg-drag-pass":      "BJJ leg drag pass tutorial",
    "headquarters-pass":  "BJJ headquarters pass tutorial",
    "bow-and-arrow-choke":"BJJ bow and arrow choke tutorial",
    "darce-choke":        "BJJ darce choke tutorial",
    "anaconda-choke":     "BJJ anaconda choke tutorial",
    "ezekiel-choke":      "BJJ ezekiel choke tutorial",
    "loop-choke":         "BJJ loop choke tutorial",
    "knee-bar":           "BJJ knee bar technique",
    "toe-hold":           "BJJ toe hold technique",
    "calf-slicer":        "BJJ calf slicer technique",
    "wrist-lock":         "BJJ wrist lock technique",
    "double-leg-takedown":"BJJ double leg takedown tutorial",
    "single-leg-takedown":"BJJ single leg takedown tutorial",
    "osoto-gari":         "BJJ osoto gari judo throw tutorial",
    "ankle-pick":         "BJJ ankle pick takedown tutorial",
    "sprawl":             "BJJ sprawl defense tutorial",
    "backtake":           "BJJ back take tutorial",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--lang", default="en")
    args = parser.parse_args()

    secrets = load_secrets()
    api_key = secrets.get("YOUTUBE_API_KEY")
    if not api_key:
        print("[ERROR] YOUTUBE_API_KEY が ~/.secrets に見つかりません")
        return

    cache = load_cache()
    langs = ["en","ja","pt"] if args.lang == "all" else [args.lang]
    count = 0

    # まずenで全技のYouTube IDを取得（言語共通）
    print("[INFO] YouTube動画IDを検索中...")
    for slug, query in SEARCH_QUERIES.items():
        if slug not in cache:
            print(f"  検索: {query}")
            vid_id, title = search_youtube(query, api_key)
            if vid_id:
                cache[slug] = {"id": vid_id, "title": title}
                print(f"  → {vid_id}: {title[:50]}")
            else:
                cache[slug] = None
            save_cache(cache)
            time.sleep(0.3)  # APIレート制限対策

    # 各言語の記事にパッチ適用
    for lang in langs:
        for slug in list(SEARCH_QUERIES.keys())[:args.limit]:
            path = os.path.join(BASE, lang, f"{slug}.html")
            if not os.path.exists(path):
                continue
            yt = cache.get(slug)
            if not yt:
                continue
            if patch_file(path, yt["id"], yt["title"]):
                print(f"[OK] {lang}/{slug}.html → {yt['id']}")
                count += 1

    print(f"\n[完了] {count}件に動画を埋め込みました")

if __name__ == "__main__":
    main()
