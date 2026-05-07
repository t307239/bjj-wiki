#!/usr/bin/env python3
"""
check_analytics_id_drift.py — z255ppp: 30th bjj-wiki lint

GA4 ID + GTM ID の placeholder/drift catch
旧 silent analytics bug: 105 page で G-XXXXXXXXXX (placeholder) のまま放置
→ tracking が機能せず、analytics 不在 (z255ppp で fix)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_GA4 = "G-7LM8L3TRZM"
EXPECTED_GTM = "GTM-WC3DKRB"


def check_page(fp: Path) -> list[str]:
    try: html = fp.read_text(encoding="utf-8")
    except: return []
    if "noindex" in html[:1500]: return []
    issues = []
    for m in re.finditer(r'G-([A-Z0-9]{8,})', html):
        if m.group(0) != EXPECTED_GA4:
            issues.append(f"GA4: {m.group(0)} ≠ {EXPECTED_GA4}")
            break
    for m in re.finditer(r'GTM-([A-Z0-9]+)', html):
        if m.group(0) != EXPECTED_GTM:
            issues.append(f"GTM: {m.group(0)} ≠ {EXPECTED_GTM}")
            break
    return issues


def main():
    failed = []
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists(): continue
        for fp in sorted(lang_dir.glob("*.html")):
            errs = check_page(fp)
            if errs:
                failed.append((str(fp.relative_to(REPO_ROOT)), errs))
    print(f"❌ Pages with analytics ID drift: {len(failed)}")
    for fp, errs in failed[:10]:
        print(f"  {fp}: {', '.join(errs)}")
    if "--ci" in sys.argv:
        sys.exit(1 if failed else 0)
    if not failed:
        print("\n✅ All pages use canonical GA4 + GTM IDs.")


if __name__ == "__main__":
    main()
