#!/usr/bin/env python3
"""
fix_title_html_tags.py — z255kk: <title> 内 inline HTML element strip

`<title>Foo <strong>Bar</strong> Baz</title>` → `<title>Foo Bar Baz</title>`
中の text を保持しつつ任意の inline tag (a/strong/em/span/i/b/code) を除去。
余計な double space は 1 space に collapse。

Idempotent: 既に clean な title はそのまま。
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

TITLE_RE = re.compile(r"(<title>)([\s\S]*?)(</title>)", re.IGNORECASE)
INLINE_TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")
WS_COLLAPSE_RE = re.compile(r"\s+")


def clean_title(inner: str) -> str:
    stripped = INLINE_TAG_RE.sub("", inner)
    return WS_COLLAPSE_RE.sub(" ", stripped).strip()


def main() -> int:
    apply = "--apply" in sys.argv
    fixed = 0
    candidates: list[tuple[str, str, str]] = []

    for lang in LANGS:
        lang_dir = REPO_ROOT / lang
        if not lang_dir.is_dir():
            continue
        for fp in lang_dir.glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            m = TITLE_RE.search(html)
            if not m:
                continue
            inner = m.group(2)
            if not re.search(r"<[a-zA-Z]", inner):
                continue
            cleaned = clean_title(inner)
            new_html = TITLE_RE.sub(f"<title>{cleaned}</title>", html, count=1)
            candidates.append((f"{lang}/{fp.name}", inner.strip(), cleaned))
            if apply and new_html != html:
                fp.write_text(new_html, encoding="utf-8")
                fixed += 1

    print(f"📋 candidates: {len(candidates)}, applied: {fixed}")
    for src, before, after in candidates[:8]:
        print(f"   {src}")
        print(f"     - {before[:120]}")
        print(f"     + {after[:120]}")
    if not apply and candidates:
        print("\n   (run with --apply to write changes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
