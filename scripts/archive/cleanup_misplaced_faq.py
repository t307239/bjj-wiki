#!/usr/bin/env python3
"""
cleanup_misplaced_faq.py — z255: float-cta marker 内に誤挿入された FAQ template 除去

【発見経緯】
make verify で z243-float-cta drift (ja=499 / pt=600 種のコピー) が判明。
原因: patch_quality_boost.py の find_injection_point() が z243-float-cta の
<div style="position:fixed"> を旧 legacy float-cta と誤認し、marker 直後に
FAQ template を挿入していた。

【誤挿入の構造】
正常:  <!-- z243-float-cta --><div id="z243-float">...
誤挿入: <!-- z243-float-cta -->
        <section id="faq" style=...>...Frequently Asked Questions...</section>
        <div id="z243-float">...

【除去対象】
- `<!-- z\d+-float-cta -->` marker 直後 〜 `<div id="z243-float"` (or `<div id="z\d+-float"`) の
  間にある <section> block を削除。
- これは template FAQ で、z245 で「逆効果」と判定済 (BACKLOG W-1/W-2)。

【Idempotent】
- 既に正常配置の page (marker 直後に <div id="z\d+-float"> が来る) は無変更
- 複数 section が誤挿入されてる page も全て除去

【先祖返り防止】
- patch_quality_boost.py の find_injection_point() を本コミットで同時修正
  (float-cta marker を anchor の最優先に変更)

Usage:
  python3 scripts/cleanup_misplaced_faq.py --dry-run            # 確認
  python3 scripts/cleanup_misplaced_faq.py --apply              # 全 lang 実行
  python3 scripts/cleanup_misplaced_faq.py --apply --lang ja    # 特定 lang
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANG_DIRS = ["en", "ja", "pt"]

# float-cta marker (z176/z224/z243 何でも) と、その本来 <div> の間に
# 誤挿入された <section>...</section> を捉える regex。
# pattern: <!-- z###-float-cta --> ([^<]*<section ...>...</section>)+ <div id="z###-float"
MISPLACED_FAQ_RE = re.compile(
    r"(<!--\s*z\d{3,}-float-cta\s*-->)"           # marker (group 1)
    r"((?:\s*<section\b[^>]*>.*?</section>)+)"    # 1+ misplaced sections (group 2)
    r"(\s*<div\s+id=\"z\d{3,}-float\")",          # actual float-cta div (group 3)
    re.DOTALL | re.IGNORECASE,
)


def cleanup_html(html: str) -> tuple[str, int]:
    """Returns (modified_html, num_sections_removed)."""
    sections_removed = 0

    def replace(m):
        nonlocal sections_removed
        # group 2 contains the misplaced sections
        # Count how many <section> tags
        n = len(re.findall(r"<section\b", m.group(2), re.IGNORECASE))
        sections_removed += n
        return m.group(1) + m.group(3)

    new_html = MISPLACED_FAQ_RE.sub(replace, html)
    return new_html, sections_removed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Write changes (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be changed (default)")
    parser.add_argument("--lang", choices=["en", "ja", "pt", "all"], default="all")
    args = parser.parse_args()

    do_write = args.apply
    if not args.apply and not args.dry_run:
        do_write = False  # default = dry-run

    langs = LANG_DIRS if args.lang == "all" else [args.lang]
    total_files_modified = 0
    total_sections_removed = 0

    for lang in langs:
        d = ROOT / lang
        if not d.exists():
            print(f"  ⚠️  {lang}/ not found, skipping")
            continue
        files = sorted(d.glob("*.html"))
        files_in_lang = 0
        sections_in_lang = 0
        for fp in files:
            if fp.name in ("index.html", "404.html"):
                continue
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            new_html, n = cleanup_html(html)
            if n > 0:
                files_in_lang += 1
                sections_in_lang += n
                if do_write:
                    fp.write_text(new_html, encoding="utf-8")
        action = "removed" if do_write else "would remove"
        print(f"  {lang}/: {files_in_lang} files ({sections_in_lang} sections {action})")
        total_files_modified += files_in_lang
        total_sections_removed += sections_in_lang

    print()
    mode = "APPLIED" if do_write else "DRY-RUN"
    print(f"📊 [{mode}] {total_files_modified} files, {total_sections_removed} sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
