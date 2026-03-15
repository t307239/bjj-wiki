#!/usr/bin/env python3
"""
AdSense自動挿入スクリプト
使い方: python3 scripts/patch_adsense.py --pub-id ca-pub-3285779374433925

AdSense取得手順:
  1. https://adsense.google.com にアクセス
  2. 「ご利用開始」→ サイトURL: https://t307239.github.io/bjj-wiki/
  3. 承認後に「広告コード」からpub-IDを取得
  4. このスクリプトを --pub-id オプションで実行
"""
import os, sys, re, glob, argparse

BASE = os.path.expanduser("~/Claude/bjj-wiki")

def make_adsense_head_tag(pub_id: str) -> str:
    return f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={pub_id}" crossorigin="anonymous"></script>'

def make_adsense_ad_unit(pub_id: str) -> str:
    """記事本文の上部に挿入するレスポンシブ広告ユニット"""
    return f"""<!-- BJJ Wiki AdSense -->
<ins class="adsbygoogle"
     style="display:block;margin:16px 0;"
     data-ad-client="{pub_id}"
     data-ad-slot="auto"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>"""

def patch_file(path: str, pub_id: str) -> bool:
    with open(path, encoding="utf-8") as f:
        html = f.read()

    # すでに挿入済みならスキップ
    if "adsbygoogle" in html:
        return False

    # <head>にAdSenseスクリプトを追加
    head_tag = make_adsense_head_tag(pub_id)
    html = html.replace("</head>", f"{head_tag}\n</head>", 1)

    # 記事ページ（h1直後）に広告ユニットを挿入
    ad_unit = make_adsense_ad_unit(pub_id)
    # h1タグの直後を探す
    h1_match = re.search(r'(<h1[^>]*>.*?</h1>)', html, re.DOTALL)
    if h1_match:
        html = html[:h1_match.end()] + "\n" + ad_unit + html[h1_match.end():]

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pub-id", required=True, help="AdSense publisher ID (例: ca-pub-1234567890123456)")
    args = parser.parse_args()

    pub_id = args.pub_id
    if not pub_id.startswith("ca-pub-"):
        print(f"[ERROR] pub-idは 'ca-pub-' で始まる必要があります: {pub_id}")
        sys.exit(1)

    html_files = glob.glob(os.path.join(BASE, "**/*.html"), recursive=True)
    ok = skip = 0
    for path in sorted(html_files):
        if patch_file(path, pub_id):
            print(f"[OK] {os.path.relpath(path, BASE)}")
            ok += 1
        else:
            skip += 1

    print(f"\n完了: {ok}ページ更新 / {skip}ページスキップ（既存）")
    print(f"\n次のステップ:")
    print(f"  cd ~/Claude/bjj-wiki && git add -A && git commit -m 'Add Google AdSense' && git push")

if __name__ == "__main__":
    main()
