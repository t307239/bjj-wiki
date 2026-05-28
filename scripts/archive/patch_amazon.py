#!/usr/bin/env python3
"""
Amazon アソシエイト リンク挿入スクリプト
BJJ道着・本・器具のアフィリリンクを全記事に追加

使い方:
  python3 scripts/patch_amazon.py --tag YOUR-ASSOCIATE-TAG

Amazon Associates 登録手順:
  1. https://affiliate.amazon.co.jp (日本) または
     https://affiliate-program.amazon.com (US/グローバル) にアクセス
  2. 申請 → 承認後にトラッキングIDを取得
  3. このスクリプトを --tag オプションで実行

収益モデル:
  - 道着: 約5,000〜30,000円 × 3〜8%コミッション
  - 書籍: 約2,000〜4,000円 × 3〜4%コミッション
  - BJJの読者は購買意欲が高い（装備への投資を惜しまない）
"""
import os, sys, glob, re, argparse

BASE = os.path.expanduser("~/Claude/bjj-wiki")

# 技カテゴリ別の関連アマゾン商品 (検索キーワード)
PRODUCT_MAP = {
    # 絞め技 → ラッシュガード・ノーギウェア推奨
    "rear-naked-choke":    ("no gi grappling rashguard", "No-Gi Rashguard"),
    "triangle-choke":      ("bjj gi uniform", "BJJ Gi"),
    "guillotine-choke":    ("mma grappling gloves", "Grappling Gloves"),
    "bow-and-arrow-choke": ("bjj gi uniform", "BJJ Gi"),
    "darce-choke":         ("bjj rashguard", "BJJ Rashguard"),
    "anaconda-choke":      ("bjj rashguard", "BJJ Rashguard"),
    # 関節技 → プロテクター
    "armbar":              ("bjj knee pad", "BJJ Knee Pad"),
    "kimura":              ("mma ear guard headgear", "Ear Guard"),
    "americana":           ("bjj gi uniform white", "BJJ Gi"),
    "omoplata":            ("yoga mat stretching", "Yoga Mat"),
    "heel-hook":           ("ankle brace bjj", "Ankle Brace"),
    "inside-heel-hook":    ("ankle brace bjj", "Ankle Brace"),
    "knee-bar":            ("knee brace bjj", "Knee Brace"),
    "toe-hold":            ("ankle brace bjj", "Ankle Brace"),
    # ガード系 → BJJ本
    "closed-guard":        ("brazilian jiu-jitsu book", "BJJ Book"),
    "half-guard":          ("bjj half guard book", "BJJ Book"),
    "butterfly-guard":     ("bjj guard book", "BJJ Book"),
    "de-la-riva-guard":    ("bjj open guard dvd", "BJJ Instructional"),
    "berimbolo":           ("bjj berimbolo instructional", "BJJ Instructional"),
    "x-guard":             ("bjj leg lock instructional", "BJJ Instructional"),
    "worm-guard":          ("bjj guard system book", "BJJ Book"),
    "rubber-guard":        ("bjj rubber guard book", "BJJ Book"),
    # テイクダウン → レスリングシューズ
    "double-leg-takedown": ("wrestling shoes", "Wrestling Shoes"),
    "single-leg-takedown": ("wrestling shoes", "Wrestling Shoes"),
    "ankle-pick":          ("wrestling shoes", "Wrestling Shoes"),
    "osoto-gari":          ("judo gi uniform", "Judo Gi"),
    # デフォルト
    "default":             ("brazilian jiu-jitsu equipment", "BJJ Equipment"),
}

def make_amazon_block(tag: str, search_kw: str, product_label: str, lang: str) -> str:
    # Amazon検索URL（アソシエイトタグ付き）
    import urllib.parse
    q = urllib.parse.quote_plus(search_kw)

    if lang == "ja":
        base_url = f"https://www.amazon.co.jp/s?k={q}&tag={tag}"
        label = f"🛒 Amazonで「{product_label}」を探す"
        sub = "道具を揃えてもっと上達しよう"
    elif lang == "pt":
        base_url = f"https://www.amazon.com/s?k={q}&tag={tag}"
        label = f"🛒 Comprar {product_label} na Amazon"
        sub = "Equipe-se para treinar melhor"
    else:
        base_url = f"https://www.amazon.com/s?k={q}&tag={tag}"
        label = f"🛒 Shop {product_label} on Amazon"
        sub = "Get the gear to level up your training"

    return f"""
<!-- Amazon Affiliate -->
<div style="background:linear-gradient(135deg,#0f1a0f,#0a1a0a);border:1px solid #2d5a2d;border-radius:12px;padding:20px;margin:24px 0;text-align:center">
  <p style="color:#6b9e6b;font-size:0.85rem;margin-bottom:8px">{sub}</p>
  <a href="{base_url}" target="_blank" rel="noopener noreferrer nofollow"
     style="display:inline-block;background:#ff9900;color:#111;padding:10px 24px;border-radius:8px;text-decoration:none;font-weight:700;font-size:0.9rem">
    {label}
  </a>
</div>"""

def patch_file(path: str, slug: str, lang: str, tag: str) -> bool:
    with open(path, encoding="utf-8") as f:
        html = f.read()

    if "amazon" in html.lower() and tag in html:
        return False  # 既に挿入済み

    search_kw, product_label = PRODUCT_MAP.get(slug, PRODUCT_MAP["default"])
    amazon_block = make_amazon_block(tag, search_kw, product_label, lang)

    # aff-box（BJJ Fanatics）の直後に挿入
    if 'class="aff-box"' in html:
        html = html.replace('</div>\n\n  <div class="faq"',
                            f'</div>{amazon_block}\n\n  <div class="faq"', 1)
    elif "<footer" in html:
        html = html.replace("<footer", amazon_block + "\n<footer", 1)
    else:
        return False

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, help="Amazonアソシエイトタグ (例: bjjwiki-22 または bjjwiki-20)")
    args = parser.parse_args()

    tag = args.tag
    ok = skip = 0

    for lang in ["en", "ja", "pt"]:
        lang_dir = os.path.join(BASE, lang)
        for path in sorted(glob.glob(os.path.join(lang_dir, "*.html"))):
            if "index" in path:
                continue
            slug = os.path.basename(path).replace(".html", "")
            if patch_file(path, slug, lang, tag):
                ok += 1
            else:
                skip += 1

    print(f"\n完了: {ok}ページ更新 / {skip}ページスキップ")
    print(f"\n次のステップ:")
    print(f"  cd ~/Claude/bjj-wiki && git add -A && git commit -m 'Add Amazon affiliate links' && git push")
    print(f"\n収益見込み:")
    print(f"  月100PV × 1%クリック × 5%コミッション × 平均5,000円 = 月250円〜")
    print(f"  トラフィック増加で青天井")

if __name__ == "__main__":
    main()
