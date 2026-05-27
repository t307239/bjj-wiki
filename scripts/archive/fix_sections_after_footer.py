#!/usr/bin/env python3
"""
fix_sections_after_footer.py
============================
フッター（<footer>）の後に出ている <section class="wc-section-divider"> ブロックを
フッターの前に移動する。

対象: en/*.html (249ページ)
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def fix_file(path: Path) -> bool:
    """
    ファイルを修正する。変更があれば True を返す。
    """
    content = path.read_text(encoding="utf-8")

    # wc-section-divider がなければスキップ
    if "wc-section-divider" not in content:
        return False

    # ナビフッター（<footer>〜</footer>）の位置を特定
    # wc-footer クラスがついているのは免責事項フッター（後ろ）なので除外
    # ナビフッターは class なし or class="wc-footer" でないもの
    nav_footer_pat = re.compile(r'(<footer(?:\s[^>]*)?>.*?</footer>)', re.DOTALL)
    footers = list(nav_footer_pat.finditer(content))
    if not footers:
        return False

    # 最初の <footer> をナビフッターとみなす
    nav_footer = footers[0]
    nav_footer_end = nav_footer.end()

    # ナビフッターの後ろにある wc-section-divider セクションを収集
    after_footer = content[nav_footer_end:]
    section_pat = re.compile(
        r'(<section(?:\s[^>]*)?>.*?</section>)',
        re.DOTALL
    )
    sections_after = list(section_pat.finditer(after_footer))

    # wc-section-divider を含むセクションのみ抽出
    target_sections = [m for m in sections_after if "wc-section-divider" in m.group(1)]
    if not target_sections:
        return False

    # 抽出したセクション群を後ろから削除（位置がずれないよう逆順で）
    # after_footer 内の位置なので content 全体のオフセットに変換
    removed_positions = []
    for m in target_sections:
        abs_start = nav_footer_end + m.start()
        abs_end   = nav_footer_end + m.end()
        removed_positions.append((abs_start, abs_end))

    # セクション HTML を取得（順序保持）
    sections_html = "\n".join(m.group(1) for m in target_sections)

    # content から対象セクションを削除（後ろから）
    new_content = content
    for start, end in reversed(removed_positions):
        # 前後の空行もまとめてトリム
        seg_start = start
        seg_end   = end
        # 前後の空白行を削除
        while seg_start > 0 and new_content[seg_start - 1] in (" ", "\t"):
            seg_start -= 1
        while seg_end < len(new_content) and new_content[seg_end] == "\n":
            seg_end += 1
        new_content = new_content[:seg_start] + new_content[seg_end:]

    # ナビフッターの直前にセクション群を挿入
    # new_content 内でナビフッターを再度検索（削除後に位置がずれている）
    nav_footer_match2 = nav_footer_pat.search(new_content)
    if not nav_footer_match2:
        return False

    insert_pos = nav_footer_match2.start()
    new_content = (
        new_content[:insert_pos]
        + sections_html + "\n\n"
        + new_content[insert_pos:]
    )

    if new_content == content:
        return False

    path.write_text(new_content, encoding="utf-8")
    return True


def main():
    en_dir = BASE_DIR / "en"
    html_files = sorted(en_dir.glob("*.html"))

    fixed = 0
    skipped = 0
    for path in html_files:
        if fix_file(path):
            fixed += 1
        else:
            skipped += 1

    print(f"修正完了: {fixed}件 / スキップ: {skipped}件")


if __name__ == "__main__":
    main()
