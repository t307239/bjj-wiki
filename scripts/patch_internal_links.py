#!/usr/bin/env python3
"""
scripts/patch_internal_links.py

内部リンクが min-links 本未満のページに、テクニック名キーワードマッチで
内部リンクを後付け注入するパッチスクリプト（Gemini 不要・無料）。

対象: href="../{lang}/{slug}.html" が min-links 本未満の en/ ja/ pt/ の全ページ
処理: <p> タグ内に TECHNIQUES のキーワードが出現したらアンカーに変換

使い方:
  python scripts/patch_internal_links.py                 # デフォルト: 3言語全て
  python scripts/patch_internal_links.py --lang en       # 特定言語のみ
  python scripts/patch_internal_links.py --dry-run       # ファイル書き込みなし
  python scripts/patch_internal_links.py --min-links 3   # 基準を3本に変更（デフォルト: 2）
"""

import os, re, glob, argparse

IS_CI    = os.environ.get("GITHUB_ACTIONS") == "true"
BASE     = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if IS_CI else os.path.expanduser("~/Claude/bjj-wiki")

# slug → (en表示名, ja表示名, pt表示名)
TECHNIQUES = {
    "americana":           ("Americana",          "アメリカーナ",          "Americana"),
    "anaconda-choke":      ("Anaconda Choke",      "アナコンダチョーク",    "Anaconda Choke"),
    "ankle-pick":          ("Ankle Pick",          "アンクルピック",        "Ankle Pick"),
    "ankle-lock":          ("Ankle Lock",          "アンクルロック",        "Chave de Pé"),
    "armbar":              ("Armbar",              "アームバー",            "Armbar"),
    "arm-triangle-choke":  ("Arm Triangle",        "アームトライアングル",  "Braçadeira"),
    "back-mount":          ("Back Mount",          "バックマウント",        "Controle das Costas"),
    "backtake":            ("Back Take",           "バックテイク",          "Back Take"),
    "berimbolo":           ("Berimbolo",           "ベリンボロ",            "Berimbolo"),
    "bow-and-arrow-choke": ("Bow and Arrow Choke", "弓矢絞め",              "Choke Arco e Flecha"),
    "butterfly-guard":     ("Butterfly Guard",     "バタフライガード",      "Guarda Borboleta"),
    "calf-slicer":         ("Calf Slicer",         "カーフスライサー",      "Calf Slicer"),
    "closed-guard":        ("Closed Guard",        "クローズドガード",      "Guarda Fechada"),
    "darce-choke":         ("D'Arce Choke",        "ダースチョーク",        "D'Arce Choke"),
    "de-la-riva-guard":    ("De La Riva Guard",    "デラヒーバガード",      "De La Riva"),
    "deep-half-guard":     ("Deep Half Guard",     "ディープハーフガード",  "Deep Half Guard"),
    "double-leg-takedown": ("Double Leg Takedown", "ダブルレッグ",          "Double Leg Takedown"),
    "ezekiel-choke":       ("Ezekiel Choke",       "エゼキエルチョーク",    "Ezekiel Choke"),
    "flower-sweep":        ("Flower Sweep",        "フラワースイープ",      "Flower Sweep"),
    "guard-pass":          ("Guard Pass",          "ガードパス",            "Passagem de Guarda"),
    "guillotine-choke":    ("Guillotine Choke",    "ギロチンチョーク",      "Guillotine"),
    "half-guard":          ("Half Guard",          "ハーフガード",          "Meia Guarda"),
    "heel-hook":           ("Heel Hook",           "ヒールフック",          "Heel Hook"),
    "hip-bump-sweep":      ("Hip Bump Sweep",      "ヒップバンプスイープ",  "Hip Bump Sweep"),
    "hip-escape":          ("Hip Escape",          "ヒップエスケープ",      "Hip Escape"),
    "inside-heel-hook":    ("Inside Heel Hook",    "インサイドヒールフック","Inside Heel Hook"),
    "kimura":              ("Kimura",              "木村ロック",            "Kimura"),
    "knee-bar":            ("Knee Bar",            "ニーバー",              "Knee Bar"),
    "knee-on-belly":       ("Knee on Belly",       "ニーオンベリー",        "Knee on Belly"),
    "knee-slice-pass":     ("Knee Slice",          "ニースライスパス",      "Knee Slice"),
    "lasso-guard":         ("Lasso Guard",         "ラッソーガード",        "Lasso Guard"),
    "leg-drag-pass":       ("Leg Drag",            "レッグドラッグ",        "Leg Drag"),
    "loop-choke":          ("Loop Choke",          "ループチョーク",        "Loop Choke"),
    "mount":               ("Mount",               "マウント",              "Montada"),
    "north-south":         ("North-South",         "ノースサウス",          "North-South"),
    "omoplata":            ("Omoplata",            "オモプラータ",          "Omoplata"),
    "open-guard":          ("Open Guard",          "オープンガード",        "Open Guard"),
    "outside-heel-hook":   ("Outside Heel Hook",   "アウトサイドヒールフック","Outside Heel Hook"),
    "pendulum-sweep":      ("Pendulum Sweep",      "ペンデュラムスイープ",  "Pendulum Sweep"),
    "rear-naked-choke":    ("Rear Naked Choke",    "裸絞め",               "Rear Naked Choke"),
    "reverse-de-la-riva":  ("Reverse De La Riva",  "リバースデラヒーバ",   "Reverse De La Riva"),
    "rubber-guard":        ("Rubber Guard",        "ラバーガード",          "Rubber Guard"),
    "scissor-sweep":       ("Scissor Sweep",       "シザースイープ",        "Raspagem Tesoura"),
    "shrimp-escape":       ("Shrimp Escape",       "シュリンプエスケープ",  "Shrimp Escape"),
    "side-control":        ("Side Control",        "サイドコントロール",    "Side Control"),
    "single-leg-takedown": ("Single Leg",          "シングルレッグ",        "Single Leg"),
    "spider-guard":        ("Spider Guard",        "スパイダーガード",      "Guarda Aranha"),
    "sprawl":              ("Sprawl",              "スプロール",            "Sprawl"),
    "toe-hold":            ("Toe Hold",            "トーホールド",          "Toe Hold"),
    "torreando-pass":      ("Torreando Pass",      "トレアンドパス",        "Torreando Pass"),
    "triangle-choke":      ("Triangle Choke",      "三角絞め",             "Triangle Choke"),
    "turtle-position":     ("Turtle",              "タートルポジション",   "Turtle"),
    "worm-guard":          ("Worm Guard",          "ワームガード",          "Worm Guard"),
    "wrist-lock":          ("Wrist Lock",          "リストロック",          "Wrist Lock"),
    "x-guard":             ("X-Guard",             "Xガード",               "X-Guard"),
}

LANG_NAME_IDX = {"en": 0, "ja": 1, "pt": 2}

# ===== 内部リンク数カウント =====
def count_internal_links(html: str, lang: str) -> int:
    return len(re.findall(rf'href=["\']\.\./{lang}/[a-z][^"\']+\.html["\']', html))

# ===== <p> タグ内リンク注入 =====
def insert_internal_links(html: str, current_slug: str, lang: str) -> tuple[str, int]:
    """
    <p>タグ内のテキストにのみ内部リンクを挿入。
    各技につき1ページ内で最初の1回のみリンク化。
    すでにリンクタグがある <p> はスキップ（二重リンク防止）。
    """
    idx = LANG_NAME_IDX.get(lang, 0)
    count = 0
    linked_slugs: set[str] = set()

    def process_paragraph(m: re.Match) -> str:
        nonlocal count
        p_html = m.group(0)
        if '<a ' in p_html:
            return p_html

        for slug, names in TECHNIQUES.items():
            if slug == current_slug or slug in linked_slugs:
                continue
            display_name = names[idx]
            pattern = re.compile(re.escape(display_name), re.IGNORECASE)
            if pattern.search(p_html):
                url = f"../{lang}/{slug}.html"
                replacement = f'<a href="{url}" style="color:var(--accent,#7c3aed);text-decoration:underline">{display_name}</a>'
                p_html = pattern.sub(replacement, p_html, count=1)
                linked_slugs.add(slug)
                count += 1
                break  # 1段落につき1リンクまで

        return p_html

    result = re.sub(r'<p[^>]*>.*?</p>', process_paragraph, html, flags=re.DOTALL)
    return result, count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang",      default="all",  help="対象言語 (en/ja/pt/all)")
    parser.add_argument("--min-links", type=int, default=2, help="この本数未満のページを対象とする（デフォルト: 2）")
    parser.add_argument("--dry-run",   action="store_true", help="ファイル書き込みなし（確認用）")
    args = parser.parse_args()

    langs = ["en", "ja", "pt"] if args.lang == "all" else [args.lang]
    total_patched = 0
    total_no_match = 0

    for lang in langs:
        lang_dir = os.path.join(BASE, lang)
        if not os.path.isdir(lang_dir):
            print(f"[SKIP] {lang}/ ディレクトリなし")
            continue

        files = sorted(glob.glob(os.path.join(lang_dir, "*.html")))
        targets = []
        for f in files:
            with open(f, encoding="utf-8") as fp:
                html = fp.read()
            links = count_internal_links(html, lang)
            if links < args.min_links:
                targets.append((f, html, links))

        print(f"[{lang}] 内部リンク {args.min_links}本未満: {len(targets)} ページ")

        for filepath, html, before_count in targets:
            slug = os.path.basename(filepath).replace(".html", "")
            new_html, added = insert_internal_links(html, slug, lang)
            after_count = count_internal_links(new_html, lang)

            if added == 0:
                print(f"  [SKIP] {lang}/{slug}: キーワードマッチなし ({before_count}本のまま)")
                total_no_match += 1
                continue

            if not args.dry_run:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_html)

            marker = " (dry-run)" if args.dry_run else ""
            print(f"  ✅ {lang}/{slug}: {before_count}本 → {after_count}本{marker}")
            total_patched += 1

    print(f"\n✅ 完了: {total_patched} ページにリンク注入 / {total_no_match} ページはキーワード未マッチ")
    if args.dry_run:
        print("  ⚠️  --dry-run モード: ファイルへの書き込みは行っていません")


if __name__ == "__main__":
    main()
