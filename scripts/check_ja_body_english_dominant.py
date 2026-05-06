#!/usr/bin/env python3
"""
check_ja_body_english_dominant.py — z255nn: JA page で body content が
English-dominant な状態を検出 (translation gap 監視).

Pattern: title / h1 / meta は JA に翻訳済 (z255ii fix で 0 件達成) だが、
body の paragraph 中身が English のまま残っている page。

検出 criteria:
  - body text (script/style 除外) で en_chars > 2000
  - en_chars > ja_chars * 2 (English-dominant)
  - これに該当する JA page を report

⚠️ 本 lint は **WARNING level (CI を block しない)**:
  - 既知 translation gap 94 page (BACKLOG WIKI-8 として登録)
  - 全部 fix には Gemini batch ~30-60 min + ~$2 必要
  - 本 lint は「regression 監視」目的: 数が増えたら警告

--ci flag で count を report、exit 0 (block しない)
--strict flag で count > THRESHOLD なら exit 1
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
JA_DIR = REPO_ROOT / "ja"
THRESHOLD = 100  # 既知 94 + 余裕、increase したら CI fail


def main() -> int:
    if not JA_DIR.exists():
        print(f"❌ {JA_DIR} not found")
        return 0

    suspect = []
    for fp in sorted(JA_DIR.glob("*.html")):
        try:
            html = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        if "noindex" in html[:1500]:
            continue
        body_m = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
        if not body_m:
            continue
        body = body_m.group(1)
        body = re.sub(r"<script[^>]*>.*?</script>", "", body, flags=re.DOTALL | re.IGNORECASE)
        body = re.sub(r"<style[^>]*>.*?</style>", "", body, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", body)
        text = re.sub(r"\s+", " ", text).strip()
        ja_chars = len(re.findall(r"[぀-ゟ゠-ヿ一-鿿]", text))
        en_chars = len(re.findall(r"[A-Za-z]", text))
        if en_chars > 2000 and ja_chars < en_chars * 0.5:
            suspect.append((fp.name, ja_chars, en_chars))

    print(f"📊 JA pages with English-dominant body: {len(suspect)}")
    for name, ja, en in suspect[:10]:
        print(f"  ja/{name}: ja={ja} en={en}")
    if len(suspect) > 10:
        print(f"  ... and {len(suspect) - 10} more")

    print(
        f"\n💡 Translation gap: BACKLOG WIKI-8 で fix 予定 "
        f"(Gemini batch ~30-60 min, ~$2)"
    )

    if "--strict" in sys.argv:
        if len(suspect) > THRESHOLD:
            print(
                f"\n🔴 count={len(suspect)} > THRESHOLD={THRESHOLD}: regression detected"
            )
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
