#!/usr/bin/env python3
"""
check_login_cta_tracking.py — z255sss: 31st bjj-wiki lint

bjj-app.net/login CTA に ?ref=wiki tracking が必須
旧 silent attribution leak: 4,094 page で /login CTA に ref param 不在
→ Wiki funnel rate (z255rrr) が機能しなかった (z255sss で fix)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def check_page(fp: Path) -> int:
    try: html = fp.read_text(encoding="utf-8")
    except: return 0
    if "noindex" in html[:1500]: return 0
    count = 0
    for m in re.finditer(r'href="(https://bjj-app\.net/login[^"]*)"', html):
        href = m.group(1)
        if '?ref=' not in href and 'page=' not in href:
            count += 1
    return count


def main():
    failed = []
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists(): continue
        for fp in sorted(lang_dir.glob("*.html")):
            n = check_page(fp)
            if n > 0:
                failed.append((str(fp.relative_to(REPO_ROOT)), n))
    print(f"❌ Pages with /login CTA missing ?ref=wiki tracking: {len(failed)}")
    for fp, n in failed[:10]:
        print(f"  {fp}: {n} CTAs")
    if "--ci" in sys.argv:
        sys.exit(1 if failed else 0)
    if not failed:
        print("\n✅ All /login CTAs have wiki funnel tracking.")


if __name__ == "__main__":
    main()
