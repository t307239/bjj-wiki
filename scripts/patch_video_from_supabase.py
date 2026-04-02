#!/usr/bin/env python3
"""
scripts/patch_video_from_supabase.py

Supabase の wiki_pages.video_url を読み取り、対応する en/ ja/ pt/ の HTML ファイルに
iframe を後付け注入するスクリプト（Gemini 不要・SerpApi 不要）。

【役割】
  video_fetcher.py が Supabase に保存した video_url を HTML に橋渡しする。
  patch_youtube.py と同じ .yt-wrap フォーマットで注入するため score_quality.py の
  has_iframe チェックに合格（vid_score 15 → 25 に昇格）。

【使い方】
  python scripts/patch_video_from_supabase.py                  # 全言語
  python scripts/patch_video_from_supabase.py --lang en        # 英語のみ
  python scripts/patch_video_from_supabase.py --dry-run        # 書き込みなし
  python scripts/patch_video_from_supabase.py --limit 100      # 最大100件
  python scripts/patch_video_from_supabase.py --force          # 既存iframe上書き

【前提】
  環境変数 SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY が設定済み
"""

import os
import re
import json
import argparse
import urllib.request
import urllib.parse
from pathlib import Path

IS_CI    = os.environ.get("GITHUB_ACTIONS") == "true"
WIKI_DIR = Path(__file__).parent.parent if IS_CI else Path.home() / "Claude" / "bjj-wiki"

# ─────────────────────────────────────────
# 設定読み込み
# ─────────────────────────────────────────

def _load_env() -> None:
    secrets_path = Path.home() / ".secrets"
    env_path     = WIKI_DIR / ".env"
    for path in [env_path, secrets_path]:
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip().removeprefix("export").strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_env()

SUPABASE_URL     = os.environ.get("SUPABASE_URL", "")
SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

# ─────────────────────────────────────────
# Supabase REST ヘルパー
# ─────────────────────────────────────────

def _headers() -> dict:
    return {
        "apikey":        SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type":  "application/json",
    }

def supabase_get(path: str) -> list:
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

# ─────────────────────────────────────────
# iframe HTML 生成
# ─────────────────────────────────────────

YT_CSS = """  /* YouTube embed */
  .yt-wrap{background:var(--card);border:1px solid var(--border);
    border-radius:14px;padding:24px;margin-bottom:8px}
  .yt-label{font-size:0.82rem;font-weight:700;color:var(--muted);
    text-transform:uppercase;letter-spacing:.08em;margin-bottom:14px}
  .yt-frame-wrap{position:relative;padding-bottom:56.25%;height:0;overflow:hidden;
    border-radius:10px}
  .yt-frame-wrap iframe{position:absolute;top:0;left:0;width:100%;height:100%}"""


def extract_video_id(url: str) -> str | None:
    """YouTube URL から video ID を抽出"""
    patterns = [
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
        r"youtube\.com/watch\?v=([A-Za-z0-9_-]{11})",
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"youtube\.com/v/([A-Za-z0-9_-]{11})",
    ]
    for pat in patterns:
        m = re.search(pat, url or "")
        if m:
            return m.group(1)
    return None


def make_iframe(video_url: str, lang_code: str) -> str:
    vid_id = extract_video_id(video_url)
    if not vid_id:
        # embed URL そのまま使えるケース
        embed_url = video_url if "embed" in video_url else f"https://www.youtube.com/embed/{video_url.split('/')[-1]}"
    else:
        embed_url = f"https://www.youtube.com/embed/{vid_id}?rel=0&modestbranding=1"

    label = {"en": "Related Video", "ja": "関連動画", "pt": "Vídeo Relacionado"}.get(lang_code, "Related Video")

    return (
        f'\n  <div class="yt-wrap">'
        f'\n    <h3 class="yt-label">{label}</h3>'
        f'\n    <div class="yt-frame-wrap">'
        f'\n      <iframe'
        f'\n        src="{embed_url}"'
        f'\n        title="BJJ technique tutorial"'
        f'\n        frameborder="0"'
        f'\n        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"'
        f'\n        allowfullscreen'
        f'\n        loading="lazy">'
        f'\n      </iframe>'
        f'\n    </div>'
        f'\n  </div>'
    )


def patch_html(html: str, video_url: str, lang_code: str, force: bool = False) -> str | None:
    """HTML に iframe を注入して返す。変更なしの場合は None。"""
    if "yt-wrap" in html and not force:
        return None  # 既存 iframe あり、スキップ

    # CSS を <style> タグに追加（未追加の場合のみ）
    if ".yt-wrap" not in html:
        html = html.replace("</style>", YT_CSS + "\n  </style>", 1)

    iframe = make_iframe(video_url, lang_code)

    # 挿入位置: aff-box の前 > share-bar の前 > footer の前 > </body> の前
    if 'class="aff-box"' in html:
        html = html.replace('<div class="aff-box">', iframe + '\n  <div class="aff-box">', 1)
    elif 'class="share-bar"' in html:
        html = html.replace('<div class="share-bar">', iframe + '\n  <div class="share-bar">', 1)
    elif "<footer>" in html:
        html = html.replace("<footer>", iframe + "\n  <footer>", 1)
    else:
        html = html.replace("</body>", iframe + "\n</body>", 1)

    return html


# ─────────────────────────────────────────
# メイン
# ─────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang",    default="all", help="対象言語 (en/ja/pt/all)")
    parser.add_argument("--limit",   type=int, default=0, help="処理件数上限 (0=全件)")
    parser.add_argument("--dry-run", action="store_true", help="ファイル書き込みなし")
    parser.add_argument("--force",   action="store_true", help="既存 iframe を上書き")
    args = parser.parse_args()

    if not SUPABASE_URL or not SERVICE_ROLE_KEY:
        print("❌ SUPABASE_URL と SUPABASE_SERVICE_ROLE_KEY を設定してください")
        return

    langs = ["en", "ja", "pt"] if args.lang == "all" else [args.lang]

    # Supabase から video_url が設定済みの slug を全件取得
    print("📡 Supabase から video_url 取得中...")
    rows = supabase_get("wiki_pages?select=slug,video_url&video_url=not.is.null")
    slug_to_url = {r["slug"]: r["video_url"] for r in rows if r.get("video_url")}
    print(f"  {len(slug_to_url)} 件の動画 URL を取得")

    if not slug_to_url:
        print("動画 URL がありません。video_fetcher.py を先に実行してください。")
        return

    total_patched = 0
    total_skipped = 0
    total_missing = 0

    for lang in langs:
        lang_dir = WIKI_DIR / lang
        if not lang_dir.is_dir():
            print(f"[SKIP] {lang}/ ディレクトリなし")
            continue

        lang_patched = 0
        for slug, video_url in slug_to_url.items():
            if args.limit and total_patched >= args.limit:
                break

            html_path = lang_dir / f"{slug}.html"
            if not html_path.exists():
                total_missing += 1
                continue

            html = html_path.read_text(encoding="utf-8")
            new_html = patch_html(html, video_url, lang, force=args.force)

            if new_html is None:
                total_skipped += 1
                continue

            if not args.dry_run:
                html_path.write_text(new_html, encoding="utf-8")

            marker = " (dry-run)" if args.dry_run else ""
            print(f"  ✅ {lang}/{slug}.html{marker}")
            total_patched += 1
            lang_patched += 1

        print(f"[{lang}] {lang_patched} ページに動画注入")

    print(f"\n✅ 完了: {total_patched} ファイル注入 / {total_skipped} スキップ(既存) / {total_missing} ファイル未存在")
    if args.dry_run:
        print("  ⚠️  --dry-run モード: ファイルへの書き込みは行っていません")


if __name__ == "__main__":
    main()
