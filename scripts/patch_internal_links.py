#!/usr/bin/env python3
"""
内部リンク自動挿入スクリプト
記事本文中の技名キーワードを他記事へのリンクに変換
使い方: HOME=~/... python3 scripts/patch_internal_links.py
"""
import os, re, glob

BASE = os.path.expanduser("~/Claude/bjj-wiki")

# slug → (en表示名, ja表示名, pt表示名)
TECHNIQUES = {
    "americana":           ("Americana",         "アメリカーナ",       "Americana"),
    "anaconda-choke":      ("Anaconda Choke",     "アナコンダチョーク", "Anaconda Choke"),
    "ankle-pick":          ("Ankle Pick",         "アンクルピック",     "Ankle Pick"),
    "armbar":              ("Armbar",             "アームバー",         "Armbar"),
    "back-mount":          ("Back Mount",         "バックマウント",     "Back Mount"),
    "backtake":            ("Back Take",          "バックテイク",       "Back Take"),
    "berimbolo":           ("Berimbolo",          "ベリンボロ",         "Berimbolo"),
    "bow-and-arrow-choke": ("Bow and Arrow Choke","弓矢絞め",           "Bow and Arrow Choke"),
    "butterfly-guard":     ("Butterfly Guard",    "バタフライガード",   "Butterfly Guard"),
    "calf-slicer":         ("Calf Slicer",        "カーフスライサー",   "Calf Slicer"),
    "closed-guard":        ("Closed Guard",       "クローズドガード",   "Closed Guard"),
    "darce-choke":         ("D'Arce Choke",       "ダースチョーク",     "D'Arce Choke"),
    "de-la-riva-guard":    ("De La Riva Guard",   "デラヒーバガード",   "De La Riva Guard"),
    "double-leg-takedown": ("Double Leg Takedown","ダブルレッグ",       "Double Leg Takedown"),
    "ezekiel-choke":       ("Ezekiel Choke",      "エゼキエルチョーク", "Ezekiel Choke"),
    "flower-sweep":        ("Flower Sweep",       "フラワースイープ",   "Flower Sweep"),
    "guard-pass":          ("Guard Pass",         "ガードパス",         "Guard Pass"),
    "guillotine-choke":    ("Guillotine Choke",   "ギロチンチョーク",   "Guillotine Choke"),
    "half-guard":          ("Half Guard",         "ハーフガード",       "Half Guard"),
    "headquarters-pass":   ("Headquarters Pass",  "HQパス",             "Headquarters Pass"),
    "heel-hook":           ("Heel Hook",          "ヒールフック",       "Heel Hook"),
    "hip-bump-sweep":      ("Hip Bump Sweep",     "ヒップバンプスイープ","Hip Bump Sweep"),
    "inside-heel-hook":    ("Inside Heel Hook",   "インサイドヒールフック","Inside Heel Hook"),
    "kimura":              ("Kimura",             "木村ロック",         "Kimura"),
    "knee-bar":            ("Knee Bar",           "ニーバー",           "Knee Bar"),
    "knee-on-belly":       ("Knee on Belly",      "ニーオンベリー",     "Knee on Belly"),
    "knee-slice-pass":     ("Knee Slice Pass",    "ニースライスパス",   "Knee Slice Pass"),
    "leg-drag-pass":       ("Leg Drag Pass",      "レッグドラッグ",     "Leg Drag Pass"),
    "loop-choke":          ("Loop Choke",         "ループチョーク",     "Loop Choke"),
    "mount":               ("Mount",              "マウント",           "Mount"),
    "north-south":         ("North-South",        "ノースサウス",       "North-South"),
    "omoplata":            ("Omoplata",           "オモプラータ",       "Omoplata"),
    "open-guard":          ("Open Guard",         "オープンガード",     "Open Guard"),
    "osoto-gari":          ("Osoto Gari",         "大外刈り",           "Osoto Gari"),
    "outside-heel-hook":   ("Outside Heel Hook",  "アウトサイドヒールフック","Outside Heel Hook"),
    "pendulum-sweep":      ("Pendulum Sweep",     "ペンデュラムスイープ","Pendulum Sweep"),
    "rear-naked-choke":    ("Rear Naked Choke",   "裸絞め",             "Rear Naked Choke"),
    "rubber-guard":        ("Rubber Guard",       "ラバーガード",       "Rubber Guard"),
    "scissor-sweep":       ("Scissor Sweep",      "シザースイープ",     "Scissor Sweep"),
    "side-control":        ("Side Control",       "サイドコントロール", "Side Control"),
    "single-leg-takedown": ("Single Leg Takedown","シングルレッグ",     "Single Leg Takedown"),
    "spider-guard":        ("Spider Guard",       "スパイダーガード",   "Spider Guard"),
    "sprawl":              ("Sprawl",             "スプロール",         "Sprawl"),
    "toe-hold":            ("Toe Hold",           "トーホールド",       "Toe Hold"),
    "torreando-pass":      ("Torreando Pass",     "トレアンドパス",     "Torreando Pass"),
    "triangle-choke":      ("Triangle Choke",     "三角絞め",           "Triangle Choke"),
    "turtle-position":     ("Turtle Position",    "タートルポジション", "Turtle Position"),
    "worm-guard":          ("Worm Guard",         "ワームガード",       "Worm Guard"),
    "wrist-lock":          ("Wrist Lock",         "リストロック",       "Wrist Lock"),
    "x-guard":             ("X-Guard",            "Xガード",            "X-Guard"),
}

LANG_NAME_IDX = {"en": 0, "ja": 1, "pt": 2}

def get_display_name(slug, lang):
    return TECHNIQUES[slug][LANG_NAME_IDX.get(lang, 0)]

def insert_internal_links(html: str, current_slug: str, lang: str) -> tuple[str, int]:
    """
    <p>タグ内のテキストにのみ内部リンクを挿入。
    各技につき1ページ内で最初の1回のみリンク化。
    """
    count = 0
    linked_slugs = set()

    def process_paragraph(m):
        nonlocal count
        p_html = m.group(0)
        # すでにリンクタグが含まれるpはスキップ（二重リンク防止）
        if '<a ' in p_html:
            return p_html

        for slug, names in TECHNIQUES.items():
            if slug == current_slug:
                continue
            if slug in linked_slugs:
                continue

            display_name = names[LANG_NAME_IDX.get(lang, 0)]
            # 大文字小文字を無視して検索（英語・ポルトガル語対応）
            pattern = re.compile(re.escape(display_name), re.IGNORECASE)
            if pattern.search(p_html):
                url = f"../{lang}/{slug}.html"
                replacement = f'<a href="{url}" style="color:var(--accent,#7c6af7);text-decoration:underline">{display_name}</a>'
                p_html = pattern.sub(replacement, p_html, count=1)
                linked_slugs.add(slug)
                count += 1
                break  # 1段落につき1リンクまで

        return p_html

    # <p>...</p> ブロックのみ対象
    result = re.sub(r'<p[^>]*>.*?</p>', process_paragraph, html, flags=re.DOTALL)
    return result, count


def patch_file(path: str, slug: str, lang: str) -> int:
    with open(path, encoding="utf-8") as f:
        html = f.read()

    new_html, n = insert_internal_links(html, slug, lang)
    if n == 0:
        return 0

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    return n


def main():
    total_links = 0
    total_files = 0

    for lang in ["en", "ja", "pt"]:
        lang_dir = os.path.join(BASE, lang)
        for slug in TECHNIQUES:
            path = os.path.join(lang_dir, f"{slug}.html")
            if not os.path.exists(path):
                continue
            n = patch_file(path, slug, lang)
            if n > 0:
                print(f"[OK] {lang}/{slug}.html → {n}リンク挿入")
                total_links += n
                total_files += 1

    print(f"\n完了: {total_files}ファイル / {total_links}内部リンク挿入")
    print("\n次のステップ:")
    print("  cd ~/Claude/bjj-wiki && git add -A && git commit -m 'SEO: Add internal links' && git push")


if __name__ == "__main__":
    main()
