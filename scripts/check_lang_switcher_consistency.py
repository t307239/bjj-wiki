#!/usr/bin/env python3
"""
check_lang_switcher_consistency.py — z255ww: 20th bjj-wiki lint

全 indexable page で lang switcher が標準 Pattern A (🇺🇸 EN / 🇯🇵 JA / 🇧🇷 PT) を
持つことを永久 catch。

旧 silent UX bug:
- 207 page で lang switcher 不在 (UI で locale 切替不能)
- 6 page で Pattern B (English/日本語/Português, no flag)
- 21 page で Pattern C (🇺🇸 English/🇯🇵 日本語/🇧🇷 Português)
(z255ww fix_lang_switcher_consistency.py で 234 page を Pattern A に統一)

例外: 特殊レイアウト (sparring-simulator 等 <div class="hero"> 系) は許容。
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# 許容される特殊 page (interactive/hero layout)
ALLOWED_SPECIAL = {"sparring-simulator"}


def check_page(fp: Path) -> str | None:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return None
    if "noindex" in html[:1500]:
        return None
    if fp.stem in ALLOWED_SPECIAL:
        return None

    # Pattern A check (standard)
    if "🇺🇸 EN" in html or "🇯🇵 JA" in html or "🇧🇷 PT" in html:
        return None

    # Pattern B drift
    if re.search(r'>English</a>', html) and re.search(r'>日本語</a>', html):
        return "Pattern B (English/日本語/Português, no flag)"

    # Pattern C drift
    if "🇺🇸 English" in html or "🇯🇵 日本語" in html:
        return "Pattern C (flag + native name)"

    # No switcher at all (but has site-header)
    if '<header class="site-header">' in html or 'lang-nav' in html or 'lang-switcher' in html:
        return "missing standard lang-switcher"

    return None  # No header at all - skip (may be intentional minimal page)


def main():
    failed = []
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            err = check_page(fp, )
            if err:
                failed.append((str(fp.relative_to(REPO_ROOT)), err))

    print(f"❌ Pages with lang-switcher format drift: {len(failed)}")
    for fp, err in failed[:20]:
        print(f"  {fp}: {err}")
    if len(failed) > 20:
        print(f"  ... and {len(failed) - 20} more")

    if "--ci" in sys.argv:
        sys.exit(1 if failed else 0)
    if not failed:
        print("\n✅ All pages use standard lang-switcher (Pattern A).")


if __name__ == "__main__":
    main()
