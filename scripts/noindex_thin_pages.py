#!/usr/bin/env python3
"""
z262idx: 薄い/ソフトトピックページを noindex 化する（インデックス止血）。

Why:
  GSC で 616 page (未登録の76%) が「クロール済み/検出 - インデックス未登録」=
  薄い量産ページがクロールバジェットとサイト評価を圧迫していた
  (docs/WIKI_INDEXING_DIAGNOSIS.md)。技術解説でないマインド/栄養系や、
  slug 語尾の "-bjj" 二重化（生成テンプレの filler）を Google が採用していない。

方針:
  - robots meta の "index" を "noindex" に置換（"follow" は残し内部リンク評価は維持）。
  - 既に noindex のページは skip（idempotent）。
  - <meta robots> が無いページにも noindex を挿入（charset の直後）。
  - sitemap.xml は scripts/patch_sitemap.py の is_noindex() が自動除外するため、
    本スクリプト適用後に patch_sitemap.py を再実行すること。

判定（いずれかに該当で thin と判定）:
  1. slug 語尾が "-bjj"（"bjj-...-bjj" の二重サフィックス = 生成 filler）
  2. slug が SOFT_KEYWORDS のいずれかを含む（mindset/栄養/メンタル等の非技術トピック）
  3. garbage_slugs.txt に列挙済み（既存の手動キュレーション）

使い方:
  dry-run（既定・変更しない）: python3 scripts/noindex_thin_pages.py
  適用:                        python3 scripts/noindex_thin_pages.py --apply
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ("en", "ja", "pt")

# z262idx: マインド/メンタル/栄養など「技術解説でない」薄トピックの slug トークン。
# 誤検出を抑えるため、検索意図が曖昧で量産されやすい語に限定（fitness 系の
# 正当なガイドになりうる conditioning / mobility / recovery 等は除外）。
SOFT_KEYWORDS: tuple[str, ...] = (
    "confidence", "mindset", "mental", "motivation", "discipline",
    "anxiety", "nervous", "fear", "focus", "concentration", "patience",
    "consistency", "understanding", "journey", "lifestyle", "growth-mindset",
    "adversity", "resilience", "plateau", "longevity", "willpower",
    "nutrition", "diet", "performance",  # "mental-performance" 等
)

# slug が以下のいずれか厳密一致なら除外（誤検出ガード）。
# 例: "weight-cutting" は nutrition 文脈だが competition で正当 → 触らない。
ALLOWLIST_EXACT: frozenset[str] = frozenset({
    "bjj-competition-nutrition-guide",  # 試合前栄養は検索需要あり、残す例
})

ROBOTS_RE = re.compile(
    r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']*)["\']\s*/?>',
    re.IGNORECASE,
)
MARKER = "<!-- z262idx-noindex -->"


def load_garbage_slugs() -> set[str]:
    """garbage_slugs.txt（"<locale>/<slug>" 形式）を locale 無視の slug 集合に。"""
    path = ROOT / "garbage_slugs.txt"
    slugs: set[str] = set()
    if not path.exists():
        return slugs
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        slug = line.split("/", 1)[1] if "/" in line else line
        slugs.add(slug)
    return slugs


def is_thin(slug: str, garbage: set[str]) -> str | None:
    """thin と判定した理由を返す（該当しなければ None）。"""
    if slug in ALLOWLIST_EXACT:
        return None
    if slug.endswith("-bjj"):
        return "doubled-bjj-suffix"
    if slug in garbage:
        return "garbage-slug-list"
    tokens = set(slug.split("-"))
    for kw in SOFT_KEYWORDS:
        # 複合語（growth-mindset 等）は部分一致、単語は token 一致で誤検出抑制
        if "-" in kw:
            if kw in slug:
                return f"soft-topic:{kw}"
        elif kw in tokens:
            return f"soft-topic:{kw}"
    return None


def already_noindex(html: str) -> bool:
    m = ROBOTS_RE.search(html)
    if m and "noindex" in m.group(1).lower():
        return True
    return MARKER in html


def apply_noindex(html: str) -> str | None:
    """robots を noindex,follow 化。変更後 html を返す（変更不要なら None）。"""
    if already_noindex(html):
        return None
    m = ROBOTS_RE.search(html)
    if m:
        new_meta = '<meta name="robots" content="noindex, follow">'
        return html[: m.start()] + MARKER + new_meta + html[m.end():]
    # robots meta が無い場合は <head> 直後 / charset 後に挿入
    insert = f'{MARKER}<meta name="robots" content="noindex, follow">'
    charset = re.search(r'<meta\s+charset=["\'][^"\']*["\']\s*/?>', html, re.IGNORECASE)
    if charset:
        return html[: charset.end()] + insert + html[charset.end():]
    head = re.search(r"<head[^>]*>", html, re.IGNORECASE)
    if head:
        return html[: head.end()] + insert + html[head.end():]
    return None  # head が無い異常ファイルは触らない


def main() -> int:
    apply = "--apply" in sys.argv
    garbage = load_garbage_slugs()
    by_locale: dict[str, int] = {loc: 0 for loc in LOCALES}
    by_reason: dict[str, int] = {}
    samples: list[str] = []
    changed = 0

    for loc in LOCALES:
        loc_dir = ROOT / loc
        if not loc_dir.is_dir():
            continue
        for html_path in sorted(loc_dir.glob("*.html")):
            slug = html_path.stem
            reason = is_thin(slug, garbage)
            if not reason:
                continue
            html = html_path.read_text(encoding="utf-8")
            if already_noindex(html):
                continue
            by_locale[loc] += 1
            by_reason[reason.split(":")[0]] = by_reason.get(reason.split(":")[0], 0) + 1
            if len(samples) < 25:
                samples.append(f"  [{reason}] {loc}/{slug}")
            if apply:
                new_html = apply_noindex(html)
                if new_html is not None:
                    html_path.write_text(new_html, encoding="utf-8")
                    changed += 1

    total = sum(by_locale.values())
    mode = "APPLIED" if apply else "DRY-RUN（変更なし）"
    print(f"=== noindex_thin_pages [{mode}] ===")
    print(f"対象（現在 indexable な thin ページ）: {total}")
    print(f"  locale別: " + ", ".join(f"{k}={v}" for k, v in by_locale.items()))
    print(f"  理由別:   " + ", ".join(f"{k}={v}" for k, v in by_reason.items()))
    print("サンプル:")
    print("\n".join(samples))
    if apply:
        print(f"\n変更したファイル数: {changed}")
        print("→ 次に: python3 scripts/patch_sitemap.py で sitemap を再生成すること")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
