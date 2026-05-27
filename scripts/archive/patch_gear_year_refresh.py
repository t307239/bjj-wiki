#!/usr/bin/env python3
"""
z260p: gear review page の年表記 2025 → 2026 一括更新

対象: en/ja/pt の best-bjj-*.html
対象範囲 (user-visible surfaces):
  - <title>...2025...</title>
  - <h1>...2025...</h1>
  - meta description / og:title / og:description / og:image:alt
  - twitter:title / twitter:description
  - schema headline / name (JSON-LD Article/HowTo/VideoObject/BreadcrumbList の name field)
  - 表示 breadcrumb (<div class="breadcrumb">)
  - "Last updated: December 2025" / "最終更新: December 2025" 文言
  - share URLs (twitter/reddit) の text param
  - FAQ visible / details summary に含まれる 2025

対象外 (genuine date signals 維持):
  - article:published_time content
  - datePublished JSON-LD field
  - dateModified (現在日でちゃんと更新されてる)

Idempotent: 既に 2026 になっていれば no-op
"""
import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TARGET_DIRS = ["en", "ja", "pt"]
GLOB_PATTERN = "best-bjj-*.html"

# 安全に置換できる行 pattern (line-level)
# article:published_time / datePublished は除外
# 安全に置換できない (= 維持したい) substring patterns
# 行内の他の 2025 は置換するが、これらは触らない
PROTECTED_SUBSTRINGS = [
    re.compile(r'article:published_time[^>]*content="\d{4}-\d{2}-\d{2}"'),
    re.compile(r'"datePublished"\s*:\s*"\d{4}-\d{2}-\d{2}"'),
]


def replace_year_in_line(line: str) -> str:
    """2025 → 2026 置換 (article:published_time / datePublished の値は維持)"""
    # 1. protected substrings を placeholder に退避
    placeholders = {}
    new_line = line
    for i, p in enumerate(PROTECTED_SUBSTRINGS):
        def _sub(m, i=i):
            key = f"__PROTECTED_{i}_{len(placeholders)}__"
            placeholders[key] = m.group(0)
            return key
        new_line = p.sub(_sub, new_line)

    # 2. 残り部分で 2025 → 2026
    new_line = new_line.replace("2025", "2026")

    # 3. placeholder を戻す
    for key, original in placeholders.items():
        new_line = new_line.replace(key, original)

    return new_line


def process_file(path: Path) -> int:
    """戻り値: 置換した 2025 件数"""
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    new_lines = []
    total_replaced = 0
    for line in original.split("\n"):
        before = line
        new_line = replace_year_in_line(line)
        if new_line != before:
            total_replaced += before.count("2025") - new_line.count("2025")
        new_lines.append(new_line)

    new_content = "\n".join(new_lines)

    if new_content == original:
        return 0

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return total_replaced


def main():
    total_files = 0
    total_repl = 0
    for d in TARGET_DIRS:
        dir_path = BASE / d
        if not dir_path.exists():
            continue
        for path in sorted(dir_path.glob(GLOB_PATTERN)):
            n = process_file(path)
            if n > 0:
                total_files += 1
                total_repl += n
                print(f"  {path.relative_to(BASE)}: {n} replacements")

    print(f"\n✅ {total_files} files updated, {total_repl} total replacements")


if __name__ == "__main__":
    main()
