#!/usr/bin/env python3
"""
fix_about_privacy_meta_drift.py — z260t Phase A-1

Localized about/privacy pages (en/ja/pt/{about,privacy}.html) are noindex
redirects to root /about.html and /privacy.html. They contain hreflang
clusters that point at themselves (noindex) which Google ignores -- a
broken hreflang cluster confuses SEO signals.

Cleanup:
  1. Normalize robots to "noindex, follow" on all 6 localized files
     (PT was "noindex, nofollow" -- drift)
  2. Remove hreflang alternate links from the 6 localized files
     (noindex pages should not advertise hreflang)
  3. Root /about.html: add <meta name="robots" content="index, follow">
     (was missing -- ambiguous indexation signal)
  4. Root /privacy.html: add canonical + robots
     (was missing canonical entirely)

idempotent: re-running is a no-op.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LOCALIZED = [
    ("en", "about.html"),
    ("ja", "about.html"),
    ("pt", "about.html"),
    ("en", "privacy.html"),
    ("ja", "privacy.html"),
    ("pt", "privacy.html"),
]

ROBOTS_RE = re.compile(r'<meta\s+name="robots"\s+content="[^"]*"\s*/?>', re.IGNORECASE)
HREFLANG_RE = re.compile(r'\s*<link\s+rel="alternate"\s+hreflang="[^"]*"\s+href="[^"]*"\s*/?>\s*', re.IGNORECASE)
CANONICAL_RE = re.compile(r'<link\s+rel="canonical"\s+href="[^"]*"\s*/?>', re.IGNORECASE)


def fix_localized(fp: Path) -> tuple[bool, list[str]]:
    """Returns (changed, log_lines)."""
    html = fp.read_text(encoding="utf-8")
    orig = html
    log: list[str] = []

    # 1. Normalize robots to "noindex, follow"
    target_robots = '<meta name="robots" content="noindex, follow">'
    if ROBOTS_RE.search(html):
        new = ROBOTS_RE.sub(target_robots, html, count=1)
        if new != html:
            log.append("normalized robots → noindex,follow")
            html = new
    else:
        # Insert after <head> opening
        m = re.search(r"<head[^>]*>", html)
        if m:
            html = html[: m.end()] + "\n  " + target_robots + html[m.end():]
            log.append("inserted robots meta")

    # 2. Remove hreflang alternates
    matches = HREFLANG_RE.findall(html)
    if matches:
        html = HREFLANG_RE.sub("", html)
        log.append(f"removed {len(matches)} hreflang alternates")

    if html != orig:
        fp.write_text(html, encoding="utf-8")
        return True, log
    return False, log


def fix_root_about(fp: Path) -> tuple[bool, list[str]]:
    html = fp.read_text(encoding="utf-8")
    orig = html
    log: list[str] = []
    target_robots = '<meta name="robots" content="index, follow">'

    if not ROBOTS_RE.search(html):
        # Insert before <title>
        m = re.search(r"<title>", html)
        if m:
            html = html[: m.start()] + target_robots + "\n" + html[m.start():]
            log.append("inserted robots index,follow")

    if html != orig:
        fp.write_text(html, encoding="utf-8")
        return True, log
    return False, log


def fix_root_privacy(fp: Path) -> tuple[bool, list[str]]:
    html = fp.read_text(encoding="utf-8")
    orig = html
    log: list[str] = []
    target_robots = '<meta name="robots" content="index, follow">'
    target_canonical = '<link rel="canonical" href="https://wiki.bjj-app.net/privacy.html">'

    if not ROBOTS_RE.search(html):
        m = re.search(r"<title>", html)
        if m:
            html = html[: m.start()] + target_robots + "\n" + html[m.start():]
            log.append("inserted robots index,follow")

    if not CANONICAL_RE.search(html):
        # Insert after <title>...</title>
        m = re.search(r"</title>", html)
        if m:
            html = html[: m.end()] + "\n" + target_canonical + html[m.end():]
            log.append("inserted canonical to /privacy.html")

    if html != orig:
        fp.write_text(html, encoding="utf-8")
        return True, log
    return False, log


def main() -> int:
    total_changed = 0
    print("=== Phase A-1: localized about/privacy cleanup ===")
    for lang, name in LOCALIZED:
        fp = ROOT / lang / name
        if not fp.exists():
            print(f"  SKIP missing: {fp}")
            continue
        changed, log = fix_localized(fp)
        if changed:
            total_changed += 1
            print(f"  FIX {lang}/{name}: {', '.join(log)}")
        else:
            print(f"  OK  {lang}/{name} (already clean)")

    print("\n=== Phase A-1: root about/privacy hardening ===")
    about_root = ROOT / "about.html"
    if about_root.exists():
        changed, log = fix_root_about(about_root)
        if changed:
            total_changed += 1
            print(f"  FIX about.html: {', '.join(log)}")
        else:
            print("  OK  about.html (already clean)")

    privacy_root = ROOT / "privacy.html"
    if privacy_root.exists():
        changed, log = fix_root_privacy(privacy_root)
        if changed:
            total_changed += 1
            print(f"  FIX privacy.html: {', '.join(log)}")
        else:
            print("  OK  privacy.html (already clean)")

    print(f"\nTotal files changed: {total_changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
