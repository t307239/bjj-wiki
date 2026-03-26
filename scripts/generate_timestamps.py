#!/usr/bin/env python3
"""
BJJ Wiki - タイムスタンプDB生成スクリプト
youtube_cache.json の動画IDを使ってYouTube説明欄からタイムスタンプを抽出
Usage: python3 generate_timestamps.py [--limit N]
Run from ~/Claude/bjj-wiki/
"""
import os, re, json, time, urllib.request, urllib.parse, argparse

BASE    = os.path.expanduser("~/Claude/bjj-wiki")
SECRETS = os.path.expanduser("~/.secrets")
CACHE   = os.path.join(BASE, "cache", "youtube_cache.json")
OUT     = os.path.join(BASE, "cache", "timestamps.json")

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

def load_timestamps():
    try:
        with open(OUT) as f:
            return json.load(f)
    except:
        return {}

def save_timestamps(data):
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_video_info(video_id, api_key):
    """YouTube APIで動画の説明欄・タイトル・チャンネルを取得（1ユニット）"""
    params = urllib.parse.urlencode({
        "part": "snippet",
        "id": video_id,
        "key": api_key,
    })
    url = f"https://www.googleapis.com/youtube/v3/videos?{params}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        items = data.get("items", [])
        if not items:
            return None
        snippet = items[0]["snippet"]
        return {
            "title":       snippet.get("title", ""),
            "channel":     snippet.get("channelTitle", ""),
            "description": snippet.get("description", ""),
        }
    except Exception as e:
        print(f"  [API ERROR] {e}")
        return None

def check_video_exists(video_id, api_key):
    """動画が存在するか確認（削除チェック用）"""
    info = fetch_video_info(video_id, api_key)
    return info is not None

def parse_timestamps(description):
    """説明欄からタイムスタンプを抽出"""
    timestamps = []
    # パターン: 0:00, 00:00, 0:00:00 + ラベル
    pattern = re.compile(
        r'^[ \t]*(\d{1,2}:\d{2}(?::\d{2})?)'  # 時刻
        r'[ \t\-–—|:]+(.+)$',                   # ラベル
        re.MULTILINE
    )
    for m in pattern.finditer(description):
        time_str = m.group(1).strip()
        label    = m.group(2).strip()
        # 不要な文字を除去
        label = re.sub(r'[\[\]()【】]', '', label).strip()
        if not label or len(label) > 80:
            continue
        # 秒数に変換
        parts = time_str.split(":")
        if len(parts) == 2:
            seconds = int(parts[0]) * 60 + int(parts[1])
        else:
            seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        timestamps.append({
            "time":    time_str,
            "label":   label,
            "seconds": seconds,
        })
    return timestamps

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--validate", action="store_true", help="削除チェックのみ実行")
    args = parser.parse_args()

    secrets = load_secrets()
    api_key = secrets.get("YOUTUBE_API_KEY")
    if not api_key:
        print("[ERROR] YOUTUBE_API_KEY が ~/.secrets に見つかりません")
        return

    cache      = load_cache()
    timestamps = load_timestamps()
    slugs      = list(cache.keys())[:args.limit]

    if args.validate:
        # ===== 削除チェックモード =====
        print("[INFO] 動画削除チェック中...")
        removed = []
        for slug in slugs:
            entry = cache.get(slug)
            if not entry:
                continue
            vid_id = entry.get("id")
            if not vid_id:
                continue
            exists = check_video_exists(vid_id, api_key)
            if not exists:
                print(f"  [DELETED] {slug}: {vid_id}")
                removed.append(slug)
                # キャッシュからNoneにしてリセット
                cache[slug] = None
            else:
                print(f"  [OK] {slug}: {vid_id}")
            time.sleep(0.3)

        if removed:
            print(f"\n[警告] {len(removed)}件の動画が削除されています: {removed}")
            print("youtube_cache.json を更新しました。patch_youtube.py を再実行してください。")
            with open(CACHE, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        else:
            print(f"\n[完了] 全{len(slugs)}件の動画が有効です")
        return

    # ===== タイムスタンプ生成モード =====
    print("[INFO] タイムスタンプ取得中...")
    new_count = 0

    for slug in slugs:
        entry = cache.get(slug)
        if not entry:
            continue
        vid_id = entry.get("id")
        if not vid_id:
            continue

        # 既に取得済みはスキップ
        if slug in timestamps and timestamps[slug].get("timestamps"):
            print(f"  [SKIP] {slug} (キャッシュ済み)")
            continue

        print(f"  取得: {slug} ({vid_id})")
        info = fetch_video_info(vid_id, api_key)
        if not info:
            print(f"  [ERROR] 動画情報取得失敗: {slug}")
            continue

        ts = parse_timestamps(info["description"])
        timestamps[slug] = {
            "video_id":  vid_id,
            "title":     info["title"],
            "channel":   info["channel"],
            "timestamps": ts,
        }

        if ts:
            print(f"  → {len(ts)}件のタイムスタンプ取得")
        else:
            print(f"  → タイムスタンプなし（説明欄に記載がない動画）")

        new_count += 1
        save_timestamps(timestamps)
        time.sleep(0.3)

    # 統計
    with_ts  = sum(1 for v in timestamps.values() if v and v.get("timestamps"))
    without  = sum(1 for v in timestamps.values() if v and not v.get("timestamps"))
    print(f"\n[完了] {new_count}件を新規取得")
    print(f"  タイムスタンプあり: {with_ts}件")
    print(f"  タイムスタンプなし: {without}件（説明欄に記載がない動画）")
    print(f"  → timestamps.json を保存しました")

if __name__ == "__main__":
    main()
