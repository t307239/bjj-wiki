#!/usr/bin/env python3
"""
BJJ Wiki - タイムスタンプUI埋め込みスクリプト
timestamps.json を読み込んで各記事にタイムスタンプセクションを追加
Usage: python3 patch_timestamps.py [--lang en|ja|pt|all] [--limit N]
Run from ~/Claude/bjj-wiki/
"""
import os, json, argparse

BASE = os.path.expanduser("~/Claude/bjj-wiki")
TS_FILE = os.path.join(BASE, "timestamps.json")

TS_CSS = """
  /* Timestamps */
  .ts-wrap{background:var(--card);border:1px solid var(--border);
    border-radius:14px;padding:24px;margin-bottom:8px}
  .ts-header{display:flex;align-items:center;gap:10px;margin-bottom:16px}
  .ts-icon{font-size:1.2rem}
  .ts-title{font-size:0.82rem;font-weight:700;color:var(--muted);
    text-transform:uppercase;letter-spacing:.08em}
  .ts-video-title{font-size:0.9rem;color:var(--text);font-weight:600;margin-bottom:4px}
  .ts-channel{font-size:0.78rem;color:var(--muted);margin-bottom:14px}
  .ts-list{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:6px}
  .ts-item{display:flex;align-items:center;gap:10px}
  .ts-time{display:inline-block;min-width:46px;padding:2px 8px;
    background:var(--accent);color:#fff;border-radius:6px;
    font-size:0.78rem;font-weight:700;font-family:monospace;
    text-decoration:none;transition:opacity .2s}
  .ts-time:hover{opacity:.8;text-decoration:none}
  .ts-label{font-size:0.85rem;color:var(--text)}"""

def make_ts_html(slug, data):
    vid_id = data.get("video_id", "")
    title  = data.get("title", "")
    channel = data.get("channel", "")
    ts_list = data.get("timestamps", [])

    if not ts_list:
        return None

    items_html = "\n".join(
        f'      <li class="ts-item">'
        f'<a class="ts-time" href="https://www.youtube.com/watch?v={vid_id}&t={t["seconds"]}s" '
        f'target="_blank" rel="noopener">{t["time"]}</a>'
        f'<span class="ts-label">{t["label"]}</span></li>'
        for t in ts_list[:12]  # 最大12件
    )

    return f"""
  <div class="ts-wrap">
    <div class="ts-header">
      <span class="ts-icon">📺</span>
      <span class="ts-title">Video Timestamps</span>
    </div>
    <div class="ts-video-title">{title}</div>
    <div class="ts-channel">{channel}</div>
    <ul class="ts-list">
{items_html}
    </ul>
  </div>"""

def patch_file(path, slug, ts_data):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    # スキップ: 既に追加済み
    if "ts-wrap" in html:
        return False

    ts_html = make_ts_html(slug, ts_data)
    if not ts_html:
        return False

    # CSSを追加
    if TS_CSS.strip() not in html:
        html = html.replace("</style>", TS_CSS + "\n</style>", 1)

    # YouTube埋め込み（yt-wrap）の直前に挿入。なければaff-boxの前
    if 'class="yt-wrap"' in html:
        html = html.replace('<div class="yt-wrap">', ts_html + '\n  <div class="yt-wrap">', 1)
    elif 'class="aff-box"' in html:
        html = html.replace('<div class="aff-box">', ts_html + '\n  <div class="aff-box">', 1)
    else:
        html = html.replace("</div>\n</body>", ts_html + "\n</div>\n</body>", 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", default="en")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    if not os.path.exists(TS_FILE):
        print("[ERROR] timestamps.json が見つかりません")
        print("  先に generate_timestamps.py を実行してください")
        return

    with open(TS_FILE) as f:
        timestamps = json.load(f)

    langs  = ["en", "ja", "pt"] if args.lang == "all" else [args.lang]
    slugs  = list(timestamps.keys())[:args.limit]
    count  = 0
    skip_no_ts = 0

    for lang in langs:
        for slug in slugs:
            ts_data = timestamps.get(slug)
            if not ts_data or not ts_data.get("timestamps"):
                skip_no_ts += 1
                continue
            path = os.path.join(BASE, lang, f"{slug}.html")
            if not os.path.exists(path):
                continue
            if patch_file(path, slug, ts_data):
                print(f"[OK] {lang}/{slug}.html ({len(ts_data['timestamps'])}件)")
                count += 1

    print(f"\n[完了] {count}件に埋め込み")
    print(f"  タイムスタンプなし（スキップ）: {skip_no_ts // len(langs)}件")

if __name__ == "__main__":
    main()
