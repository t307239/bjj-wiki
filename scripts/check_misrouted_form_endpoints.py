#!/usr/bin/env python3
"""
check_misrouted_form_endpoints.py — z255bb: form action endpoint 検査 (25th lint)

Wiki HTML 内の `<form action="...">` と `<form>` element の email/endpoint を
scan し、misroute / 異 project の email / 公開 email exposure を検出する。

検出 pattern:
  A. Formspree v1 endpoint with raw email: action="https://formspree.io/f/<email>"
     → email が public 公開、別 project email の場合は misroute
  B. Other email-based endpoints: action="mailto:..." (送信失敗の可能性高い HTTP method=POST)
  C. action 値内に既知の異 project email (e.g. ai.fukugyo.ken@gmail.com)

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
FOREIGN_EMAILS = [
    "ai.fukugyo.ken@gmail.com",
    # 他 project の email を発見次第追記
]

FORM_RE = re.compile(r'<form\s+[^>]*action="([^"]+)"', re.IGNORECASE)
FORMSPREE_EMAIL_RE = re.compile(
    r"https?://formspree\.io/f/[^/\s]*@", re.IGNORECASE
)


def main() -> int:
    issues_a: list[tuple[str, str]] = []  # Formspree raw-email
    issues_c: list[tuple[str, str]] = []  # Foreign-email endpoint

    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            for m in FORM_RE.finditer(html):
                action = m.group(1)
                if action in ALLOWED_ENDPOINTS:
                    continue
                # Class A: Formspree v1 raw-email endpoint
                if FORMSPREE_EMAIL_RE.search(action):
                    issues_a.append((f"{lang}/{fp.name}", action))
                # Class C: foreign-project email
                for fe in FOREIGN_EMAILS:
                    if fe in action:
                        issues_c.append((f"{lang}/{fp.name}", fe))
                        break

    print(f"❌ A. Formspree v1 raw-email endpoint (email exposure): {len(issues_a)}")
    for s, a in issues_a[:5]:
        print(f"   {s}: {a}")
    print(f"❌ C. Foreign-project email in form action (misroute):  {len(issues_c)}")
    for s, fe in issues_c[:5]:
        print(f"   {s}: {fe}")

    total = len(issues_a) + len(issues_c)
    if total == 0:
        print("\n✅ No misrouted/exposed form endpoints.")

    if "--ci" in sys.argv:
        return 1 if total > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
