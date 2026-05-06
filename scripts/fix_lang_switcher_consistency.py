#!/usr/bin/env python3
"""
fix_lang_switcher_consistency.py — z255ww: lang-switcher format normalization + 207 page injection

旧 silent UX bug:
- 207 page で <header class="site-header"> に lang-switcher が無い
  (hreflang in head はあるが UI で切替不能 = JA user は JA 版が存在しても気づかない)
- 6 page で Pattern B 形式 (English / 日本語 / Português, no flag)
- 21 page で Pattern C 形式 (🇺🇸 English / 🇯🇵 日本語 / 🇧🇷 Português)
- 4,218 page (majority) は Pattern A (🇺🇸 EN / 🇯🇵 JA / 🇧🇷 PT)

修正:
- 全 page を Pattern A に normalize
- 207 page には header inject (logo の直後に挿入)
- 6 / 21 page は format swap

idempotent: 既に Pattern A は touch しない。
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def make_lang_nav(lang: str, slug: str) -> str:
    """Build standard Pattern A lang switcher."""
    items = []
    for code, label in [("en", "🇺🇸 EN"), ("ja", "🇯🇵 JA"), ("pt", "🇧🇷 PT")]:
        active = ' class="active"' if code == lang else ""
        items.append(f'<a href="../{code}/{slug}.html"{active}>{label}</a>')
    return '<nav class="lang-nav" aria-label="Language">' + "".join(items) + "</nav>"


def patch_page(fp: Path) -> str:
    """Returns: 'inject', 'normalize-b', 'normalize-c', 'skip-pattern-a', 'skip-noindex', 'skip-no-header'."""
    html = fp.read_text(encoding="utf-8")
    if "noindex" in html[:1500]:
        return "skip-noindex"

    lang = fp.parts[-2]  # en/ja/pt
    slug = fp.stem

    # Already Pattern A?
    if "🇺🇸 EN" in html or "🇯🇵 JA" in html or "🇧🇷 PT" in html:
        return "skip-pattern-a"

    nav_html = make_lang_nav(lang, slug)

    # Pattern B: <(nav|div) class="lang-nav">English / 日本語 / Português (no flag)
    # Both <nav> and <div> wrappers used historically
    pattern_b = re.search(
        r'<(nav|div) class="lang-nav"[^>]*>\s*<a[^>]*>English</a>\s*<a[^>]*>日本語</a>\s*<a[^>]*>Português</a>\s*</\1>',
        html
    )
    if pattern_b:
        new = html[:pattern_b.start()] + nav_html + html[pattern_b.end():]
        fp.write_text(new, encoding="utf-8")
        return "normalize-b"

    # Pattern C: 🇺🇸 English / 🇯🇵 日本語 / 🇧🇷 Português (flag + native name)
    # Try matching the broader lang-nav block
    if re.search(r'>🇺🇸 English<', html) or re.search(r'>🇯🇵 日本語<', html):
        # Replace the whole lang-nav / div.lang-nav block
        new = re.sub(
            r'<(?:nav|div) class="lang-nav"[^>]*>.*?</(?:nav|div)>',
            nav_html, html, count=1, flags=re.DOTALL
        )
        if new != html:
            fp.write_text(new, encoding="utf-8")
            return "normalize-c"

    # No lang switcher exists, but has <header class="site-header">?
    # Inject after the logo link
    m = re.search(
        r'(<header class="site-header">\s*<div class="container">\s*<a [^>]+class="logo"[^>]*>[^<]*(?:<[^>]+>[^<]*</[^>]+>[^<]*)*</a>)',
        html
    )
    if m:
        new = html[:m.end()] + nav_html + html[m.end():]
        fp.write_text(new, encoding="utf-8")
        return "inject"

    return "skip-no-header"


def main():
    print("🔧 fix_lang_switcher_consistency.py — z255ww")
    stats = {"inject": 0, "normalize-b": 0, "normalize-c": 0,
             "skip-pattern-a": 0, "skip-noindex": 0, "skip-no-header": 0}
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            result = patch_page(fp)
            stats[result] = stats.get(result, 0) + 1
    for k, v in stats.items():
        if v > 0:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
