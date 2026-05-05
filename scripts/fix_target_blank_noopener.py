#!/usr/bin/env python3
"""
fix_target_blank_noopener.py — z255v: target=_blank に rel=noopener を付加

`<a target="_blank">` が rel=noopener を持たない link は tabnabbing 攻撃
(window.opener 経由で original tab を phishing 化) のリスクと、Lighthouse
SEO/security 監査で落とされる。

修正方針:
  - rel 属性が無い → rel="noopener" を追加
  - rel 属性に noopener / noreferrer どちらも無い → 既存 rel 値に noopener を append
  - <script>...</script> 内は除外 (動的生成は別途確認)

Idempotent: 何度実行しても rel="noopener" は重複付加されない。
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

A_TAG_RE = re.compile(r"<a\s+([^>]*?)>", re.IGNORECASE)
TARGET_BLANK_RE = re.compile(r'\btarget\s*=\s*["\']_blank["\']', re.IGNORECASE)
REL_RE = re.compile(r'\brel\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)


def patch_html(html: str) -> tuple[str, int]:
    # Mask script blocks so we don't touch dynamic JS strings
    masks: list[str] = []

    def stash(m):
        masks.append(m.group(0))
        return f"\x00SCRIPT_{len(masks)-1}\x00"

    masked = SCRIPT_RE.sub(stash, html)
    fixed = 0

    def fix_tag(m):
        nonlocal fixed
        attrs = m.group(1)
        if not TARGET_BLANK_RE.search(attrs):
            return m.group(0)
        rel_m = REL_RE.search(attrs)
        if rel_m:
            rel_val = rel_m.group(1)
            tokens = rel_val.split()
            if "noopener" in tokens or "noreferrer" in tokens:
                return m.group(0)
            new_rel = (rel_val + " noopener").strip()
            new_attrs = REL_RE.sub(f'rel="{new_rel}"', attrs, count=1)
        else:
            new_attrs = attrs.rstrip() + ' rel="noopener"'
        fixed += 1
        return f"<a {new_attrs}>"

    masked = A_TAG_RE.sub(fix_tag, masked)
    # Restore script blocks
    for i, src in enumerate(masks):
        masked = masked.replace(f"\x00SCRIPT_{i}\x00", src)
    return masked, fixed


def main() -> int:
    print("🔧 fix_target_blank_noopener.py — z255v")
    files_fixed = 0
    total_fixed = 0
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            new, n = patch_html(html)
            if n > 0:
                fp.write_text(new, encoding="utf-8")
                files_fixed += 1
                total_fixed += n
    print(f"  Fixed {total_fixed} <a target=_blank> tags across {files_fixed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
