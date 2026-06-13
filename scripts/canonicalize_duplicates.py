#!/usr/bin/env python3
"""
z262idx: 近似重複ページの canonical 統合（キーワード共食い解消）。

Why:
  同一トピックが複数 slug で存在（例: bjj-anaconda-choke / bjj-anaconda-choke-guide /
  anaconda-choke）。Google から見ると重複コンテンツで、被リンク/権威が分散し
  インデックス評価が下がる (docs/WIKI_INDEXING_DIAGNOSIS.md)。
  弱い方の <link rel="canonical"> を「正」ページに向け、評価を 1 本に集約する。
  ページ自体は残す（noindex でなく canonical なので安全・可逆）。

クラスタ化:
  slug を正規化キーに畳む。先頭 "bjj-"、末尾 "-bjj"、末尾 "-guide" を除去した
  コアが一致するものを 1 クラスタとする（= 同一トピックの affix 違い）。

「正（canonical）」の選定ルール（ユーザー合意 z262idx）:
  1. 末尾 "-bjj"（二重サフィックス）は正にしない（非 "-bjj" 兄弟がいる限り除外）
  2. 残る候補から「内部被リンク数が最多」を正に
  3. 同数なら: "bjj-" 接頭辞あり > なし、"-guide" なし > あり、slug 短い順

使い方:
  dry-run（既定・変更なし）: python3 scripts/canonicalize_duplicates.py
  適用:                      python3 scripts/canonicalize_duplicates.py --apply
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ("en", "ja", "pt")
BASE_URL = "https://wiki.bjj-app.net"

CANONICAL_RE = re.compile(
    r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']*)["\']\s*/?>',
    re.IGNORECASE,
)


def normalize_key(slug: str) -> str:
    """affix を剥がしてトピックのコアを返す。"""
    s = slug
    if s.endswith("-bjj"):
        s = s[: -len("-bjj")]
    if s.endswith("-guide"):
        s = s[: -len("-guide")]
    while s.startswith("bjj-"):
        s = s[len("bjj-"):]
    return s


def form_score(slug: str) -> tuple[int, int, int]:
    """正の好ましさ（大きいほど優先）。inbound 同数時の tie-break。"""
    has_bjj_prefix = 1 if slug.startswith("bjj-") else 0
    no_guide = 0 if slug.endswith("-guide") else 1
    shorter = -len(slug)  # 短い slug を優先
    return (has_bjj_prefix, no_guide, shorter)


def build_inbound_counts(loc: str, slugs: set[str]) -> dict[str, int]:
    """locale 内の各 slug への内部被リンク数（自己参照は除外）。"""
    counts: dict[str, int] = defaultdict(int)
    link_re = re.compile(
        re.escape(f"{BASE_URL}/{loc}/") + r"([A-Za-z0-9\-]+)\.html"
    )
    for html_path in (ROOT / loc).glob("*.html"):
        self_slug = html_path.stem
        html = html_path.read_text(encoding="utf-8")
        seen: set[str] = set()
        for m in link_re.finditer(html):
            target = m.group(1)
            if target == self_slug or target not in slugs:
                continue
            seen.add(target)
        for target in seen:  # 1 ページからの複数リンクは 1 と数える
            counts[target] += 1
    return counts


def choose_canonical(members: list[str], inbound: dict[str, int]) -> str:
    candidates = [m for m in members if not m.endswith("-bjj")] or members
    return max(candidates, key=lambda s: (inbound.get(s, 0), form_score(s)))


def main() -> int:
    apply = "--apply" in sys.argv
    total_clusters = 0
    total_redirected = 0
    changed = 0
    lines: list[str] = []

    for loc in LOCALES:
        loc_dir = ROOT / loc
        if not loc_dir.is_dir():
            continue
        slugs = {p.stem for p in loc_dir.glob("*.html")}
        clusters: dict[str, list[str]] = defaultdict(list)
        for slug in slugs:
            clusters[normalize_key(slug)].append(slug)
        dup_clusters = {k: v for k, v in clusters.items() if len(v) > 1}
        if not dup_clusters:
            continue
        inbound = build_inbound_counts(loc, slugs)

        for key, members in sorted(dup_clusters.items()):
            canonical = choose_canonical(members, inbound)
            dups = [m for m in members if m != canonical]
            total_clusters += 1
            canon_url = f"{BASE_URL}/{loc}/{canonical}.html"
            lines.append(
                f"[{loc}] 正: {canonical} (in={inbound.get(canonical,0)})  ← "
                + ", ".join(f"{d}(in={inbound.get(d,0)})" for d in dups)
            )
            for dup in dups:
                total_redirected += 1
                if not apply:
                    continue
                dup_path = loc_dir / f"{dup}.html"
                html = dup_path.read_text(encoding="utf-8")
                m = CANONICAL_RE.search(html)
                if not m:
                    continue
                if m.group(1) == canon_url:
                    continue  # 既に正を指している（idempotent）
                new_tag = f'<link rel="canonical" href="{canon_url}">'
                new_html = html[: m.start()] + new_tag + html[m.end():]
                dup_path.write_text(new_html, encoding="utf-8")
                changed += 1

    mode = "APPLIED" if apply else "DRY-RUN（変更なし）"
    print(f"=== canonicalize_duplicates [{mode}] ===")
    print(f"重複クラスタ: {total_clusters} / canonical を張り替える弱ページ: {total_redirected}")
    print("\n".join(lines))
    if apply:
        print(f"\n書き換えたファイル数: {changed}")
        print("→ 次に: python3 scripts/patch_sitemap.py（必要なら）, make verify")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
