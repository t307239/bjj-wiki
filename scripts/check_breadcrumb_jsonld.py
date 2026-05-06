#!/usr/bin/env python3
"""
check_breadcrumb_jsonld.py — z255tt: 18th bjj-wiki lint

idempotent BreadcrumbList JSON-LD presence check.
- index.html / 4 root page と全 indexable article で BreadcrumbList が必須。
- noindex page は除外 (sitemap 整合)
- h1 が無い page は redirect / consolidated として skip

旧 silent bug: 3,853 page で BreadcrumbList 不在 → SERP breadcrumb navigation
不在 → CTR 機会喪失 (z255tt patch_breadcrumb_jsonld.py で fix)。
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def check_page(fp: Path) -> str | None:
    """Returns error message if check fails, None if passes."""
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception as e:
        return f"read error: {e}"

    head_part = html[:2000]
    if "noindex" in head_part:
        return None  # noindex page: skip

    if not re.search(r"<h1[^>]*>([^<]+)</h1>", html):
        return None  # no h1: redirect/consolidated, skip

    if "BreadcrumbList" not in html:
        return "missing BreadcrumbList JSON-LD"

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
                failed.append(f"  {fp.relative_to(REPO_ROOT)}: {err}")

    print(f"❌ Pages missing BreadcrumbList JSON-LD: {len(failed)}")
    for line in failed[:20]:
        print(line)
    if len(failed) > 20:
        print(f"  ... and {len(failed) - 20} more")

    if "--ci" in sys.argv:
        sys.exit(1 if failed else 0)
    print("\n✅ All indexable pages have BreadcrumbList JSON-LD." if not failed else "")


if __name__ == "__main__":
    main()
