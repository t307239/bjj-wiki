#!/usr/bin/env python3
"""
check_seo_meta_completeness.py — z255jjjj-WW: SEO meta tag completeness lint

Verifies indexable pages have both:
  A. <meta name="robots"> with `max-image-preview:large` (Google rich SERP CTR)
  B. <meta property="og:image:alt"> when og:image is present (a11y + SEO)

Skips noindex / redirect pages (those legitimately omit these).

--ci flag → exit 1 if any indexable page is missing.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

NOINDEX_RE = re.compile(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', re.IGNORECASE)
ROBOTS_LARGE_RE = re.compile(
    r'name=["\']robots["\'][^>]*content=["\'][^"\']*max-image-preview:large',
    re.IGNORECASE,
)
OG_IMAGE_RE = re.compile(r'property=["\']og:image["\']', re.IGNORECASE)
OG_IMAGE_ALT_RE = re.compile(r'property=["\']og:image:alt["\']', re.IGNORECASE)


def main() -> int:
    missing_robots: list[str] = []
    missing_og_alt: list[str] = []
    total = 0
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                head = fp.read_text(encoding="utf-8", errors="ignore")[:6000]
            except Exception:
                continue
            if NOINDEX_RE.search(head):
                continue
            total += 1
            src = f"{lang}/{fp.name}"
            if not ROBOTS_LARGE_RE.search(head):
                missing_robots.append(src)
            if OG_IMAGE_RE.search(head) and not OG_IMAGE_ALT_RE.search(head):
                missing_og_alt.append(src)

    print(f"📊 Indexable pages scanned: {total:,}")
    print(f"❌ Missing max-image-preview:large robots: {len(missing_robots)}")
    for s in missing_robots[:6]:
        print(f"   {s}")
    print(f"❌ og:image without og:image:alt:           {len(missing_og_alt)}")
    for s in missing_og_alt[:6]:
        print(f"   {s}")
    total_err = len(missing_robots) + len(missing_og_alt)
    if total_err == 0:
        print("\n✅ All indexable pages have complete SEO meta.")
    if "--ci" in sys.argv:
        return 1 if total_err > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
