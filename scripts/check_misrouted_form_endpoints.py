#!/usr/bin/env python3
"""
check_misrouted_form_endpoints.py — z255bb+cc: form/mailto/text の email exposure
検査 (25th lint, z255cc で root pages + mailto + plain text に拡張)

Wiki HTML 全体 (lang dir + root pages) を scan し、misroute / 異 project の email
/ 公開 email exposure を検出する。

検出 pattern:
  A. Formspree v1 endpoint with raw email: action="https://formspree.io/f/<email>"
     → email が URL-encoded で公開、別 project email の場合は misroute
  C. FOREIGN_EMAILS 既知 list の email が以下のいずれかに出現:
     - <form action=...> 内
     - <a href="mailto:..."> 内
     - HTML 表示テキスト内 (about.html / privacy.html など)

許容: BJJ Wiki の正式 contact channel (Beehiiv subscribe form 等) は別途。

--ci flag で hit > 0 → exit 1
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]

# 既知の正式 endpoint (BJJ Wiki の subscribe form 等)
ALLOWED_ENDPOINTS = {
    "https://bjjwiki.beehiiv.com/subscribe",
}

# 別 project email pattern (uranai-side / 副業診断 etc.)
# BJJ Wiki の正式 email は 307239t777@gmail.com (CLAUDE.md 参照)
FOREIGN_EMAILS = [
    "ai.fukugyo.ken@gmail.com",  # uranai-side / 副業診断 project
    # 他 project の email を発見次第追記
]

FORM_RE = re.compile(r'<form\s+[^>]*action="([^"]+)"', re.IGNORECASE)
FORMSPREE_EMAIL_RE = re.compile(
    r"https?://formspree\.io/f/[^/\s]*@", re.IGNORECASE
)
SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
STYLE_RE = re.compile(r"<style[^>]*>.*?</style>", re.IGNORECASE | re.DOTALL)


def iter_html_files():
    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            yield fp, f"{lang}/{fp.name}"
    for fp in REPO_ROOT.glob("*.html"):
        yield fp, fp.name


def main() -> int:
    issues_a: list[tuple[str, str]] = []  # Formspree raw-email
    issues_c: list[tuple[str, str]] = []  # Foreign-email anywhere

    for fp, label in iter_html_files():
        try:
            html = fp.read_text(encoding="utf-8")
        except Exception:
            continue

        # Class A: <form action="https://formspree.io/f/<email>">
        for m in FORM_RE.finditer(html):
            action = m.group(1)
            if action in ALLOWED_ENDPOINTS:
                continue
            if FORMSPREE_EMAIL_RE.search(action):
                issues_a.append((label, action))

        # Class C: foreign email anywhere (form action / mailto / plain text)
        # Strip script/style to avoid noise
        cleaned = SCRIPT_RE.sub("", html)
        cleaned = STYLE_RE.sub("", cleaned)
        for fe in FOREIGN_EMAILS:
            if fe.lower() in cleaned.lower():
                issues_c.append((label, fe))

    print(f"❌ A. Formspree v1 raw-email endpoint (email exposure): {len(issues_a)}")
    for s, a in issues_a[:5]:
        print(f"   {s}: {a}")
    print(f"❌ C. Foreign-project email in HTML (misroute):         {len(issues_c)}")
    for s, fe in issues_c[:5]:
        print(f"   {s}: {fe}")

    total = len(issues_a) + len(issues_c)
    if total == 0:
        print("\n✅ No misrouted/exposed form endpoints or emails.")

    if "--ci" in sys.argv:
        return 1 if total > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
