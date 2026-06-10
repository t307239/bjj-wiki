#!/usr/bin/env python3
"""z273seo: Related チップの内部リンク切れ(404)を解消する一回限りの修復スクリプト。

check_broken_links.py が検出した 15 件の broken "Related Techniques" チップを修復する。
- 実在する正しいページがある概念語は、その実ページへ href を差し替え(意味的に妥当)。
- 対応する実ページが無い概念語は、チップ <a>...</a> ごと除去(誤誘導を防ぐ)。

Why: 旧世代の related チップが、未作成の概念ページ(joint-lock.html 等)を指していた。
     Google が internal link を辿って 404 → クロール無駄 + UX 低下。
     候補の近縁ページへ機械的に寄せると別概念へ誤誘導するため、
     「明確に正しい実ページがある語だけ差し替え、他は除去」という保守的方針を取る。

冪等: broken slug を全て処理済みにするため、再実行しても変化なし。
UTF-8 明示で mojibake を防ぐ(sed 等での直接編集は禁止)。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 概念語 → 実在する正しいページ slug(差し替え対象)
REPOINT = {
    "joint-lock": "bjj-joint-lock-mechanics",
    "leg-lock": "bjj-advanced-leg-lock-systems",
    "white-belt": "bjj-white-belt-curriculum",
}
# 実ページが無い概念語(チップごと除去)
REMOVE = {"submission", "choke", "carotid-artery", "sweep", "scissors-sweep", "white-belt-warning"}

BROKEN = set(REPOINT) | REMOVE


def target_exists(lang: str, slug: str) -> bool:
    return (ROOT / lang / f"{slug}.html").is_file()


def fix_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    original = text
    changes = 0

    for slug in BROKEN:
        # 該当 slug を href に持つチップ <a ...>...</a> を 1 つずつ処理
        pattern = re.compile(
            r'<a href="\.\./(en|ja|pt)/' + re.escape(slug) + r'\.html"[^>]*>.*?</a>',
            re.S,
        )

        def repl(m: re.Match) -> str:
            nonlocal changes
            lang = m.group(1)
            if slug in REPOINT and target_exists(lang, REPOINT[slug]):
                changes += 1
                # href の slug 部分のみ差し替え(style/テキストは保持)
                return m.group(0).replace(
                    f"../{lang}/{slug}.html", f"../{lang}/{REPOINT[slug]}.html"
                )
            # REMOVE 対象 or 差し替え先が無い → チップごと除去
            changes += 1
            return ""

        text = pattern.sub(repl, text)

    if text != original:
        path.write_text(text, encoding="utf-8")
    return changes


def main() -> int:
    total_files = 0
    total_changes = 0
    for html in ROOT.rglob("*.html"):
        # 自動生成物以外の本文 HTML のみ(node_modules 等は無い前提だが念のため)
        if any(part in {".git", "node_modules"} for part in html.parts):
            continue
        c = fix_file(html)
        if c:
            total_files += 1
            total_changes += c
            print(f"  fixed {c}x  {html.relative_to(ROOT)}")

    print(f"\n✅ {total_changes} chips fixed across {total_files} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
