#!/usr/bin/env python3
"""
fix_noreferrer.py — z262: rel="noopener" に noreferrer を追加 (privacy leak 修正)

check_external_link_noreferrer.py で検出された203ファイルの
target="_blank" 外部リンクに noreferrer を追加する。
generator script も同時修正で先祖返り防止。
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

# noopener のみ (noreferrer 不在) を noopener noreferrer に置換
# Why: 単純な文字列置換だと rel="noopener noreferrer" を二重置換するため
#      wordboundary を使い noreferrer が既に含まれる場合はスキップ
PATTERN = re.compile(r'\brel="noopener"')
REPLACEMENT = 'rel="noopener noreferrer"'

fixed_files = 0
fixed_links = 0

for lang in LANGS:
    for fp in (REPO_ROOT / lang).glob("*.html"):
        try:
            content = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        count = len(PATTERN.findall(content))
        if count == 0:
            continue
        new_content = PATTERN.sub(REPLACEMENT, content)
        fp.write_text(new_content, encoding="utf-8")
        fixed_files += 1
        fixed_links += count

print(f"✅ Fixed {fixed_links} links across {fixed_files} files")
