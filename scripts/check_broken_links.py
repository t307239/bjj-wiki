#!/usr/bin/env python3
"""
BJJ Wiki - Internal Link Checker (z255q rewrite)

z176b lint chain の 6 つ目。en/, ja/, pt/ 配下の HTML から内部リンクを抽出し、
リポジトリ内に実体が存在するかを検査する。

旧実装の欠陥 (z255q で修正):
  - valid_pages が「ファイル名のみ (lang を区別しない)」セットだったため
    `../en/index.html` 型の cross-locale 参照が常に broken 扱い
  - `/wiki-v2.css` のような root-relative path も filenames セットには無く
    全部 broken 扱い
  - 結果: 41,837 件の false positive で実質 silent pass していた

修正後:
  - 全ファイル (HTML/CSS/JS/PNG/SVG/...) を repo root からの相対 path として登録
  - リンク解決はソース HTML の親ディレクトリ起点で os.path.normpath
  - root-relative `/foo` は repo root 起点で解決
  - クエリ/フラグメント除去
  - --ci フラグ + CI_THRESHOLD env で許容数を超えたら exit 1
"""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
DEFAULT_THRESHOLD = 100  # 既知の cross-locale gap (未翻訳 page) を許容するための baseline


def get_all_files() -> set[str]:
    """repo root 配下の全ファイル相対 path セット (POSIX 区切り)"""
    valid = set()
    for root, _dirs, files in os.walk(REPO_ROOT):
        # .git や node_modules 等は除外
        rel_root = os.path.relpath(root, REPO_ROOT)
        if rel_root.startswith((".git", "node_modules", "archive")):
            continue
        for f in files:
            rel = os.path.normpath(os.path.join(rel_root, f)) if rel_root != "." else f
            valid.add(rel.replace("\\", "/"))
    return valid


_SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
_TEMPLATE_RE = re.compile(r"\$\{")  # JS テンプレートリテラル


def extract_links(html: str) -> list[str]:
    # <script>...</script> 内の dynamic href= を除外 (template literal が入る)
    cleaned = _SCRIPT_RE.sub("", html)
    return re.findall(r'href=["\']([^"\']+)["\']', cleaned)


def is_internal(link: str) -> bool:
    if link.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "data:")):
        return False
    # protocol-relative `//foo` は external (例: //pagead2.googlesyndication.com)
    if link.startswith("//"):
        return False
    if link.startswith("#") or link.strip() in ("", "/"):
        return False
    # 残った template literal も除外
    if _TEMPLATE_RE.search(link):
        return False
    return True


def resolve_link(link: str, source_rel_dir: str) -> str:
    """source HTML の親ディレクトリ起点で link を解決し repo-root 相対 path を返す"""
    # クエリ / fragment 除去
    if "#" in link:
        link = link.split("#", 1)[0]
    if "?" in link:
        link = link.split("?", 1)[0]
    if not link:
        return ""

    # root-relative
    if link.startswith("/"):
        target = link.lstrip("/")
    else:
        target = os.path.normpath(os.path.join(source_rel_dir, link))

    # ディレクトリ参照は index.html を補う (GitHub Pages 動作)
    if target.endswith("/") or (
        not Path(REPO_ROOT / target).suffix and (REPO_ROOT / target).is_dir()
    ):
        target = os.path.join(target, "index.html")

    return target.replace("\\", "/")


def main() -> int:
    valid = get_all_files()
    broken: dict[str, list[str]] = defaultdict(list)
    total_links = 0
    broken_count = 0

    print(f"🔍 Scanning BJJ Wiki for broken internal links...")
    print(f"   {len(valid):,} files indexed under repo root\n")

    for lang in LANGS:
        lang_dir = REPO_ROOT / lang
        if not lang_dir.is_dir():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            source_rel_dir = lang  # `../en/foo.html` 解決の起点
            for link in extract_links(html):
                if not is_internal(link):
                    continue
                total_links += 1
                target = resolve_link(link, source_rel_dir)
                if not target:
                    continue
                if target not in valid:
                    broken[f"{lang}/{fp.name}"].append(link)
                    broken_count += 1

    print(f"📊 Total internal links checked: {total_links:,}")
    print(f"❌ Broken links found:           {broken_count:,}")

    if broken_count > 0:
        all_broken = [l for links in broken.values() for l in links]
        print()
        print("=" * 70)
        print("MOST COMMON BROKEN LINKS (top 20):")
        print("=" * 70)
        for link, count in Counter(all_broken).most_common(20):
            print(f"  {count:5d}x  {link}")

    print()
    print("✅ Scan complete.")

    # --ci flag: CI_THRESHOLD env で fail 閾値制御
    if "--ci" in sys.argv:
        threshold = int(os.environ.get("CI_THRESHOLD", str(DEFAULT_THRESHOLD)))
        if broken_count > threshold:
            print(f"\n🔴 broken_count={broken_count} > threshold={threshold} → CI fail")
            return 1
        if broken_count > 0:
            print(f"\n🟡 broken_count={broken_count} ≤ threshold={threshold} → CI pass (許容内)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
