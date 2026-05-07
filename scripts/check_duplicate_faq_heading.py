#!/usr/bin/env python3
"""
check_duplicate_faq_heading.py — z255ggg: 25th bjj-wiki lint

同 page 内で <h2> FAQ 系 heading が 2 回以上出現する duplicate を catch。
旧 silent UX/a11y bug: 3,892 page で重複 (z255ggg fix で rename)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FAQ_PATTERNS = re.compile(
    r'<h2[^>]*>\s*(?:Frequently Asked Questions|よくある質問|Perguntas Frequentes)\s*</h2>',
    re.IGNORECASE
)


def check_page(fp: Path) -> int:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return 0
    if "noindex" in html[:1500]:
        return 0
    return len(FAQ_PATTERNS.findall(html))


def main():
    failed = []
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            count = check_page(fp)
            if count > 1:
                failed.append((str(fp.relative_to(REPO_ROOT)), count))

    print(f"❌ Pages with duplicate FAQ heading: {len(failed)}")
    for fp, count in failed[:10]:
        print(f"  {fp}: {count}× FAQ headings")

    if "--ci" in sys.argv:
        sys.exit(1 if failed else 0)
    if not failed:
        print("\n✅ No duplicate FAQ headings.")


if __name__ == "__main__":
    main()
