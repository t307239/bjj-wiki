#!/usr/bin/env python3
"""
fix_broken_links.py — z255q: 21 件の真 broken link 修正

check_broken_links.py で検出された 3 class:
  A. ../../favicon.ico (15x) — 存在しない path、絶対 URL に置換
  B. imanari-roll.html 内の bare "ashi-garami.html" → "bjj-ashi-garami-setup.html"
  C. paper-cutter-choke.html 内の "bread-cutter-choke.html" → 同技なので self-link 除去
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]


def fix_a_favicon():
    """Class A: ../../favicon.ico 15 page を絶対 URL に修正"""
    fixed = 0
    pages = [
        "bjj-guard-setups-masterclass.html",
        "bjj-sweeps-to-submissions.html",
        "bjj-conditioning-science.html",
        "bjj-attacking-from-turtle-advanced.html",
        "bjj-back-control-finishing-details.html",
    ]
    for lang in LANGS:
        for slug in pages:
            fp = REPO_ROOT / lang / slug
            if not fp.exists():
                continue
            html = fp.read_text(encoding="utf-8")
            new = html.replace(
                '<link rel="icon" type="image/png" href="../../favicon.ico">',
                '<link rel="icon" type="image/svg+xml" href="https://wiki.bjj-app.net/favicon.svg">',
            )
            if new != html:
                fp.write_text(new, encoding="utf-8")
                fixed += 1
    return fixed


def fix_b_imanari():
    """Class B: imanari-roll.html の bare ashi-garami.html リンクを修正"""
    fixed = 0
    target_slug = "bjj-ashi-garami-setup.html"
    for lang in LANGS:
        fp = REPO_ROOT / lang / "imanari-roll.html"
        if not fp.exists():
            continue
        html = fp.read_text(encoding="utf-8")
        # 同じファイル内 prose の <a href='ashi-garami.html'>X</a> または "ashi-garami.html"
        # bjj- や outside を含まない bare path のみ置換
        new = re.sub(
            r'(href=[\'"])ashi-garami\.html([\'"])',
            rf'\g<1>{target_slug}\g<2>',
            html,
        )
        if new != html:
            fp.write_text(new, encoding="utf-8")
            fixed += 1
    return fixed


def fix_c_paper_cutter():
    """Class C: paper-cutter-choke.html の bread-cutter-choke.html リンク除去
    (paper cutter と bread cutter は同技なので self-link 撤去)"""
    fixed = 0
    for lang in LANGS:
        fp = REPO_ROOT / lang / "paper-cutter-choke.html"
        if not fp.exists():
            continue
        html = fp.read_text(encoding="utf-8")
        # <a href="bread-cutter-choke.html">X</a> → X
        new = re.sub(
            r'<a\s+href=[\'"]bread-cutter-choke\.html[\'"][^>]*>([^<]+)</a>',
            r"\1",
            html,
            flags=re.IGNORECASE,
        )
        if new != html:
            fp.write_text(new, encoding="utf-8")
            fixed += 1
    return fixed


def main():
    print("🔧 fix_broken_links.py — z255q")
    a = fix_a_favicon()
    print(f"  A. favicon ../../favicon.ico → absolute URL : {a} files")
    b = fix_b_imanari()
    print(f"  B. imanari-roll ashi-garami.html slug fix    : {b} files")
    c = fix_c_paper_cutter()
    print(f"  C. paper-cutter-choke self-link removed      : {c} files")
    print(f"\n✅ Total fixed: {a + b + c} files")


if __name__ == "__main__":
    main()
