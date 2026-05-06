#!/usr/bin/env python3
"""
check_ui_label_locale_drift.py — z255uu: 19th bjj-wiki lint

JA/PT page で UI label (category badge / belt label / difficulty label) が
EN 残留していないかを永久 catch。

旧 silent UX bug: 1,184 JA + 1,242 PT page で <span class="badge">Joint Lock</span>
等が EN のまま残留 (z255uu fix_ui_labels_locale.py で fix)。

Generator script (generate_bjj_wiki.py) は hard-coded EN を出力するため、
新規 page 生成後に fix_ui_labels_locale.py を実行する必要がある。
このlintはその漏れを catch する。
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# EN labels that should not appear in JA/PT pages
EN_CATEGORIES = {"Choke", "Defense", "Escape", "Guard", "Joint Lock",
                 "Leg Lock", "Passing", "Position", "Sweep", "Takedown", "Transition"}
EN_BELTS = {"White", "Blue", "Purple", "Brown", "Black"}
EN_DIFFICULTIES = {"Beginner", "Intermediate", "Advanced"}


def check_page(fp: Path, lang: str) -> list[str]:
    """Returns list of drift violations."""
    if lang == "en":
        return []
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return []

    drifts = []

    # 1. <span class="badge">CATEGORY</span>
    for m in re.finditer(r'<span class="badge">([^<]+)</span>', html):
        if m.group(1).strip() in EN_CATEGORIES:
            drifts.append(f"badge='{m.group(1)}'")

    # 2. <span class="belt belt-X">BELT</span>
    for m in re.finditer(r'<span class="belt belt-[a-z]+">([^<]+)</span>', html):
        if m.group(1).strip() in EN_BELTS:
            drifts.append(f"belt='{m.group(1)}'")

    # 3. <span class="diff-belt" ...>BELT_UPPER</span>
    for m in re.finditer(r'<span class="diff-belt"[^>]*>([^<]+)</span>', html):
        if m.group(1).strip().title() in EN_BELTS:
            drifts.append(f"diff-belt='{m.group(1)}'")

    # 4. <span class="diff-label">DIFFICULTY</span>
    for m in re.finditer(r'<span class="diff-label">([^<]+)</span>', html):
        if m.group(1).strip() in EN_DIFFICULTIES:
            drifts.append(f"diff-label='{m.group(1)}'")

    # 5. <span class="belt-tag" ...>🥋 Blue Belt</span> — separate emoji-prefixed pattern
    EN_BELT_FULL = {"White Belt", "Blue Belt", "Purple Belt", "Brown Belt", "Black Belt"}
    for m in re.finditer(r'<span class="belt-tag"[^>]*>([^<]+)</span>', html):
        # Strip leading emoji + whitespace
        stripped = re.sub(r'^[^\w]+\s*', '', m.group(1).strip())
        if stripped in EN_BELT_FULL:
            drifts.append(f"belt-tag='{m.group(1).strip()}'")

    return drifts


def main():
    failed = []
    for lang in ("ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            drifts = check_page(fp, lang)
            if drifts:
                failed.append((str(fp.relative_to(REPO_ROOT)), drifts))

    print(f"❌ JA/PT pages with EN UI label drift: {len(failed)}")
    for fp, drifts in failed[:20]:
        print(f"  {fp}: {', '.join(drifts[:3])}")
    if len(failed) > 20:
        print(f"  ... and {len(failed) - 20} more")

    if "--ci" in sys.argv:
        sys.exit(1 if failed else 0)
    if not failed:
        print("\n✅ All JA/PT UI labels properly localized.")


if __name__ == "__main__":
    main()
