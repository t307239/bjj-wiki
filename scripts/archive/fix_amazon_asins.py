#!/usr/bin/env python3
# ⚠️ DEPRECATED — DO NOT RUN ⚠️
# このスクリプトはアフィリリンク(bjj06-22/bjjfanatics)を含む旧バッチスクリプトです。
# CLAUDE.md「アフィリリンク完全禁止」ルールにより使用禁止。
# 実行するとアフィリリンクが再注入され先祖返りします。
# 代わりに generate_bjj_wiki.py を使用してください。
"""
fix_amazon_asins.py
====================
Amazon 検索URL（amazon.co.jp/s?k=...）を特定商品の DP URL に一括置換する。

使い方:
  python3 scripts/fix_amazon_asins.py [--dry-run]

  --dry-run: ファイルを変更せず、置換対象だけ表示する

変換例:
  https://www.amazon.co.jp/s?k=bjj+gi+kimono&tag=bjj06-22
  → https://www.amazon.co.jp/dp/B01LXCQGR5/?tag=bjj06-22

ASIN マッピングについて:
  ・amazon.co.jp で実際に販売されている商品の ASIN を使用
  ・DP URL に tag=bjj06-22 アフィリエイトタグを付与
  ・カテゴリ別に代表商品を設定（ギ / ノーギ / 書籍 / 道具）
"""

import os
import re
import sys
import glob

# ────────────────────────────────────────────
#  ASIN マッピング（検索キーワード → DP URL）
#
#  ※ ASINは amazon.co.jp で実際に確認済みのものを使用
#    新しい商品が出た場合は ASIN_MAP を更新してください
# ────────────────────────────────────────────
TAG = "bjj06-22"


def dp(asin: str) -> str:
    """ASIN から DP URL を生成（アフィリエイトタグ付き）"""
    return f"https://www.amazon.co.jp/dp/{asin}/?tag={TAG}"


# ----------------------------------------------------------------
#  カテゴリ別代表商品 ASIN（amazon.co.jp 掲載確認済み）
# ----------------------------------------------------------------

# 道衣 (Gi)
ASIN_GI_WHITE     = "B01LXCQGR5"  # Fuji Sports Sekai BJJ Gi 白帯推奨
ASIN_GI_PREMIUM   = "B07Q2TDK1G"  # Scramble Athlete V4 道衣
ASIN_GI_TRAINING  = "B07WQZXY6C"  # Sanabul Essential Gi

# ノーギ (NoGi)
ASIN_NOGI_SHORTS  = "B09MVYZ3LJ"  # Scramble Combat Shorts
ASIN_NOGI_RASH    = "B07X3L6KFG"  # Tatami Hiro Vale Tudo Shorts

# 書籍 (Books)
ASIN_BOOK_UNIV    = "1934813036"   # Jiu-Jitsu University (Saulo Ribeiro)
ASIN_BOOK_MASTER  = "0736042865"   # Mastering Jiu-Jitsu (Renzo Gracie)
ASIN_BOOK_DRILL   = "1936608510"   # Drill to Win (Andre Galvao)
ASIN_BOOK_LEGLOCKS= "1936608863"   # Leg Locks (Rob Biernacki)

# トレーニング器具 (Equipment)
ASIN_GRAPPLING_DUMMY = "B07GNWFMBJ"  # グラップリングダミー
ASIN_MOUTHGUARD      = "B00DY5XGQK"  # Shock Doctor マウスガード
ASIN_GYM_BAG         = "B07Q5VLLLB"  # Sanabul BJJ バッグ
ASIN_EAR_GUARD       = "B01N5M47JC"  # Cliff Keen イヤーガード

# ────────────────────────────────────────────
#  キーワード → ASIN マッピングテーブル
#  ・キーはlower case で統一
#  ・部分一致（in）でマッチング
# ────────────────────────────────────────────
URL_TO_ASIN = {
    # ギ・道衣
    "bjj+gi+kimono":           ASIN_GI_WHITE,
    "bjj+gear":                ASIN_GI_TRAINING,
    "bjj+gi":                  ASIN_GI_WHITE,

    # ノーギ関連
    "bjj+grappling":           ASIN_NOGI_RASH,
    "nogi":                    ASIN_NOGI_SHORTS,

    # 書籍・学習リソース
    "bjj+grappling+book":      ASIN_BOOK_UNIV,
    "book":                    ASIN_BOOK_MASTER,

    # トレーニング器具
    "bjj+training+equipment":  ASIN_GRAPPLING_DUMMY,
    "mouthguard":              ASIN_MOUTHGUARD,
    "マウスガード":             ASIN_MOUTHGUARD,
    "bag":                     ASIN_GYM_BAG,
    "バッグ":                  ASIN_GYM_BAG,

    # テクニック別（書籍・インストラクショナルへ誘導）
    "armbar":                  ASIN_BOOK_UNIV,
    "triangle":                ASIN_BOOK_UNIV,
    "guillotine":              ASIN_BOOK_UNIV,
    "kimura":                  ASIN_BOOK_MASTER,
    "omoplata":                ASIN_BOOK_MASTER,
    "americana":               ASIN_BOOK_MASTER,
    "rear+naked":              ASIN_BOOK_MASTER,
    "rear_naked":              ASIN_BOOK_MASTER,
    "bow+and+arrow":           ASIN_BOOK_MASTER,
    "darce":                   ASIN_BOOK_MASTER,
    "anaconda":                ASIN_BOOK_MASTER,
    "heel+hook":               ASIN_BOOK_LEGLOCKS,
    "inside+heel+hook":        ASIN_BOOK_LEGLOCKS,
    "outside+heel+hook":       ASIN_BOOK_LEGLOCKS,
    "leg+lock":                ASIN_BOOK_LEGLOCKS,
    "レッグロック":             ASIN_BOOK_LEGLOCKS,
    "kneebar":                 ASIN_BOOK_LEGLOCKS,
    "knee+bar":                ASIN_BOOK_LEGLOCKS,
    "calf+slicer":             ASIN_BOOK_LEGLOCKS,
    "toe+hold":                ASIN_BOOK_LEGLOCKS,
    "ankle":                   ASIN_BOOK_LEGLOCKS,

    # ガード系
    "closed+guard":            ASIN_BOOK_UNIV,
    "half+guard":              ASIN_BOOK_UNIV,
    "butterfly+guard":         ASIN_BOOK_DRILL,
    "spider+guard":            ASIN_BOOK_DRILL,
    "de+la+riva":              ASIN_BOOK_DRILL,
    "berimbolo":               ASIN_BOOK_DRILL,
    "rubber+guard":            ASIN_BOOK_MASTER,
    "x+guard":                 ASIN_BOOK_DRILL,
    "open+guard":              ASIN_BOOK_DRILL,
    "worm+guard":              ASIN_BOOK_DRILL,

    # パッシング系
    "guard+pass":              ASIN_BOOK_UNIV,
    "torreando+pass":          ASIN_BOOK_UNIV,
    "knee+slice+pass":         ASIN_BOOK_UNIV,
    "leg+drag+pass":           ASIN_BOOK_DRILL,
    "headquarters+pass":       ASIN_BOOK_UNIV,
    "ガードパス":               ASIN_BOOK_UNIV,

    # ポジション系
    "side+control":            ASIN_BOOK_UNIV,
    "mount":                   ASIN_BOOK_UNIV,
    "back+mount":              ASIN_BOOK_UNIV,
    "backtake":                ASIN_BOOK_UNIV,
    "knee+on+belly":           ASIN_BOOK_UNIV,
    "north+south":             ASIN_BOOK_MASTER,
    "turtle+position":         ASIN_BOOK_MASTER,

    # スウィープ系
    "scissor+sweep":           ASIN_BOOK_UNIV,
    "hip+bump+sweep":          ASIN_BOOK_UNIV,
    "flower+sweep":            ASIN_BOOK_UNIV,
    "pendulum+sweep":          ASIN_BOOK_UNIV,

    # テイクダウン系
    "single+leg+takedown":     ASIN_BOOK_MASTER,
    "double+leg+takedown":     ASIN_BOOK_MASTER,
    "sprawl":                  ASIN_BOOK_MASTER,
    "osoto+gari":              ASIN_BOOK_MASTER,
    "ankle+pick":              ASIN_BOOK_MASTER,

    # コンセプト系
    "サブミッション+戦略":      ASIN_BOOK_UNIV,
    "トップゲーム+ポジション":  ASIN_BOOK_UNIV,
    "トレーニング+ピリオダイゼーション": ASIN_BOOK_DRILL,
    "wrist+lock":              ASIN_BOOK_MASTER,
    "loop+choke":              ASIN_BOOK_MASTER,
    "ezekiel+choke":           ASIN_BOOK_MASTER,
}

# ────────────────────────────────────────────
#  デフォルト ASIN（マッチなし時のフォールバック）
# ────────────────────────────────────────────
DEFAULT_ASIN = ASIN_BOOK_UNIV  # Jiu-Jitsu University（汎用的）


def get_asin_for_url(search_url: str) -> str:
    """検索URLのキーワードからASINを決定する"""
    # k= パラメータを抽出
    m = re.search(r'[?&]k=([^&"\'>\s]+)', search_url)
    if not m:
        return DEFAULT_ASIN

    keyword = m.group(1).lower().replace("%2b", "+").replace("%20", "+")

    # URL_TO_ASIN テーブルで部分一致検索（長いキー＝より具体的なキーを優先）
    for key, asin in sorted(URL_TO_ASIN.items(), key=lambda x: -len(x[0])):
        if key.lower() in keyword:
            return asin

    return DEFAULT_ASIN


def replace_in_file(filepath: str, dry_run: bool = False) -> int:
    """1ファイル内のAmazon検索URLをDP URLに置換。変更件数を返す"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  [SKIP] {filepath}: {e}")
        return 0

    # amazon.co.jp/s?... パターンにマッチ
    pattern = r'https?://www\.amazon\.co\.jp/s\?[^"\'>\s]+'
    matches = re.findall(pattern, content)

    if not matches:
        return 0

    new_content = content
    count = 0
    for old_url in set(matches):
        asin = get_asin_for_url(old_url)
        new_url = dp(asin)

        if dry_run:
            print(f"  [{os.path.basename(filepath)}] {old_url}")
            print(f"    → {new_url}")
        else:
            new_content = new_content.replace(old_url, new_url)
        count += matches.count(old_url)

    if not dry_run and new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

    return count


def main():
    dry_run = "--dry-run" in sys.argv

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_files = (
        glob.glob(os.path.join(base, "en", "*.html")) +
        glob.glob(os.path.join(base, "ja", "*.html")) +
        glob.glob(os.path.join(base, "pt", "*.html")) +
        glob.glob(os.path.join(base, "*.html"))
    )

    mode = "DRY RUN" if dry_run else "実行"
    print(f"=== Amazon ASIN直リンク化 ({mode}) ===")
    print(f"対象ファイル数: {len(html_files)}")
    print()

    total_replacements = 0
    total_files_changed = 0

    for filepath in sorted(html_files):
        n = replace_in_file(filepath, dry_run=dry_run)
        if n > 0:
            total_files_changed += 1
            total_replacements += n
            if not dry_run:
                rel = os.path.relpath(filepath, base)
                print(f"  ✅ {rel}: {n}件置換")

    print()
    print(f"=== 完了 ===")
    print(f"変更ファイル数: {total_files_changed}")
    print(f"置換件数合計:   {total_replacements}")

    if dry_run:
        print()
        print("[DRY RUN] ファイルは変更されていません。")
        print("実際に置換するには: python3 scripts/fix_amazon_asins.py")


if __name__ == "__main__":
    main()
