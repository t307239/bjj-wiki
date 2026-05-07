#!/usr/bin/env python3
"""
check_internal_link_relative.py — z255jjj: 27th bjj-wiki lint

body <a> 内で同 locale internal page を absolute URL で参照 catch
旧 silent UX/perf bug: 33 page で 99 link drift (z255jjj fix)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE = "https://wiki.bjj-app.net"


def check_page(fp: Path) -> int:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return 0
    if "noindex" in html[:1500]:
        return 0
    lang = fp.parts[-2]
    count = 0
    for m in re.finditer(r'<a\b[^>]*>', html):
        tag = m.group(0)
        href_m = re.search(r'href="(' + re.escape(SITE) + r'/' + lang + r'/[^"]+\.html)"', tag)
        if href_m and '?' not in href_m.group(1):
            count += 1
    return count


def main():
    failed = []
    for lang in ("en","ja","pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists(): continue
        for fp in sorted(lang_dir.glob("*.html")):
            n = check_page(fp)
            if n > 0:
                failed.append((str(fp.relative_to(REPO_ROOT)), n))
    print(f"❌ Pages with absolute internal-link URL in <a>: {len(failed)}")
    for fp, n in failed[:10]:
        print(f"  {fp}: {n} links")
    if "--ci" in sys.argv:
        sys.exit(1 if failed else 0)
    if not failed:
        print("\n✅ All same-locale internal links use relative URLs.")


if __name__ == "__main__":
    main()
