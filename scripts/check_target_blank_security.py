#!/usr/bin/env python3
"""
check_target_blank_security.py — z255v: <a target=_blank> security 検査 (19th lint)

`<a target="_blank">` で rel に noopener/noreferrer のいずれも無い link は
tabnabbing 攻撃 (window.opener 経由で original tab を phishing 化) のリスクと、
Lighthouse SEO/security 監査で減点される silent SEO bug。

検査対象:
  - en/, ja/, pt/ の全 HTML 内 <a> tag
  - <script>...</script> 内は除外 (JS dynamic 生成)
  - target="_blank" を持つ tag で rel に noopener/noreferrer どちらも無いもの

--ci flag で issue > 0 → exit 1
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

A_TAG_RE = re.compile(r"<a\s+([^>]*?)>", re.IGNORECASE)
TARGET_BLANK_RE = re.compile(r'\btarget\s*=\s*["\']_blank["\']', re.IGNORECASE)
REL_RE = re.compile(r'\brel\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)


def is_unsafe(attrs: str) -> bool:
    if not TARGET_BLANK_RE.search(attrs):
        return False
    rel_m = REL_RE.search(attrs)
    if not rel_m:
        return True
    tokens = rel_m.group(1).lower().split()
    return "noopener" not in tokens and "noreferrer" not in tokens


def main() -> int:
    issues: list[tuple[str, str]] = []
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            cleaned = SCRIPT_RE.sub("", html)
            for m in A_TAG_RE.finditer(cleaned):
                if is_unsafe(m.group(1)):
                    issues.append((f"{lang}/{fp.name}", m.group(0)[:100]))

    print(f"❌ <a target=_blank> missing rel=noopener/noreferrer: {len(issues)}")
    for src, tag in issues[:8]:
        print(f"   {src}")
        print(f"     {tag}")

    if not issues:
        print("\n✅ All target=_blank links are safe.")

    if "--ci" in sys.argv:
        return 1 if issues else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
