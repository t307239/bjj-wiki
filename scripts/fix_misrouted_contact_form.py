#!/usr/bin/env python3
"""
fix_misrouted_contact_form.py — z255bb: 46 PT page で contact form の Formspree
endpoint が別 project (uranai-side / 副業診断) の email `ai.fukugyo.ken@gmail.com`
に送信される misroute bug を修正.

3 重の問題:
  - Form 送信が誤った inbox に到達 (BJJ wiki の問い合わせ → 副業 project)
  - email address が HTML に公開されている (privacy/spam リスク)
  - EN/JA には form 無く、PT のみという不整合 UX

修正方針:
  Beehiiv 購読や app CTA で engagement channel は確保済みなので、
  この misrouted form は削除する (Option B)。
  `<!-- Formspree Contact Form -->` から `<!-- /Formspree -->` までを除去。

Idempotent.
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Marker-bounded removal pattern
FORM_BLOCK_RE = re.compile(
    r"\s*<!--\s*Formspree Contact Form\s*-->.*?<!--\s*/Formspree\s*-->\s*",
    re.DOTALL | re.IGNORECASE,
)


def main():
    print("🔧 fix_misrouted_contact_form.py — z255bb")
    fixed = 0
    for lang in ("pt", "ja", "en"):
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            new = FORM_BLOCK_RE.sub("\n", html)
            if new != html:
                fp.write_text(new, encoding="utf-8")
                fixed += 1
    print(f"  Removed misrouted contact form from {fixed} files")


if __name__ == "__main__":
    main()
