#!/usr/bin/env python3
"""
check_twitter_image_sync.py — z255lll: 28th bjj-wiki lint

twitter:image ≠ og:image を catch (SNS preview の Twitter で old image が出る)

旧 silent UX/SEO bug: 4,244 page で twitter:image=old static og-image.png
だが og:image=dynamic technique-specific card → SNS preview 不整合
(z255lll で sync して 1 image policy)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def check_page(fp: Path) -> str | None:
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return None
    if "noindex" in html[:1500]:
        return None
    og_m = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    tw_m = re.search(r'<meta name="twitter:image" content="([^"]+)"', html)
    if og_m and tw_m and og_m.group(1) != tw_m.group(1):
        return f"og={og_m.group(1)[:40]} tw={tw_m.group(1)[:40]}"
    return None


def main():
    failed = []
    for lang in ("en", "ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            err = check_page(fp)
            if err:
                failed.append((str(fp.relative_to(REPO_ROOT)), err))

    print(f"❌ Pages with twitter:image ≠ og:image drift: {len(failed)}")
    for fp, err in failed[:10]:
        print(f"  {fp}: {err}")
    if "--ci" in sys.argv:
        sys.exit(1 if failed else 0)
    if not failed:
        print("\n✅ All twitter:image match og:image (SNS preview sync).")


if __name__ == "__main__":
    main()
