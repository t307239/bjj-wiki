#!/usr/bin/env python3
"""
BJJ Wiki — CSS統一スクリプト

全テクニックページのCSS変数を統一デザインシステムに合わせる。
HTML構造は変えず、<style>ブロック内のCSS変数とカラー値のみ更新。

統一先（UI_DESIGN.md準拠）:
  --bg: #0f172a
  --card: #18181b
  --accent: #e94560 (red, not gold)
  --accent2: #7c3aed (purple)
  --text: #e2e8f0
  --muted: #64748b
"""
import os
import re

WIKI_ROOT = os.path.join(os.path.dirname(__file__), "..")
LANGS = ["en", "ja", "pt"]

# Old accent color (#e2b714 gold) → new (#e94560 red)
# Old header gradient → solid dark
CSS_REPLACEMENTS = [
    # Accent colors
    ("--accent:#e2b714", "--accent:#e94560"),
    ("--accent: #e2b714", "--accent:#e94560"),
    ("color:var(--accent)", "color:var(--accent)"),  # keep as-is
    # Card colors
    ("--card:#111827", "--card:#18181b"),
    # Header gradient → solid
    ("background:linear-gradient(135deg,#0f1a2e,#1a1040)", "background:#0f172a"),
    # Border accent → red
    ("border-bottom:2px solid var(--accent)", "border-bottom:1px solid rgba(255,255,255,0.10)"),
    ("border-bottom: 2px solid var(--accent)", "border-bottom:1px solid rgba(255,255,255,0.10)"),
    # h3 color (blue → muted)
    ("h3{color:#93c5fd", "h3{color:#e94560"),
    # Old nav background
    ("background:#111827;padding:10px 20px", "background:#18181b;padding:10px 20px"),
    # Strong/tip box colors
    (".tip-box{background:#1e293b", ".tip-box{background:#18181b"),
    ("background:#1e293b", "background:#18181b"),
    # Breadcrumb colors
    ("color:#e2b714", "color:#e94560"),
]

count = 0

for lang in LANGS:
    langdir = os.path.join(WIKI_ROOT, lang)
    if not os.path.isdir(langdir):
        continue
    for fname in os.listdir(langdir):
        if not fname.endswith(".html") or fname == "index.html":
            continue
        fpath = os.path.join(langdir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        original = content
        for old, new in CSS_REPLACEMENTS:
            content = content.replace(old, new)

        if content != original:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            count += 1

print(f"CSS unified in {count} pages across {len(LANGS)} languages")
