#!/usr/bin/env python3
"""
BJJ Wiki JA — 用語統一スクリプト
漢字表記をBJJ業界で一般的なカタカナ表記に置換する。
"""
import os
import re

JA_DIR = os.path.join(os.path.dirname(__file__), "..", "ja")

# 置換ルール: (検索, 置換)
# BJJ用語はカタカナ（外来語）の方が一般的
REPLACEMENTS = [
    ("防御", "ディフェンス"),
    ("攻撃", "アタック"),
    ("逃げ", "エスケープ"),
    ("投げ技", "テイクダウン"),
    ("関節技", "サブミッション"),
    ("絞め技", "チョーク"),
    # 既にカタカナのものはスキップ
]

def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False

def main():
    total = 0
    modified = 0
    for fname in os.listdir(JA_DIR):
        if not fname.endswith(".html"):
            continue
        total += 1
        filepath = os.path.join(JA_DIR, fname)
        if fix_file(filepath):
            modified += 1

    print(f"Scanned: {total} files")
    print(f"Modified: {modified} files")
    print("Replacements applied:")
    for old, new in REPLACEMENTS:
        print(f"  {old} → {new}")

if __name__ == "__main__":
    main()
