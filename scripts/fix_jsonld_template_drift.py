#!/usr/bin/env python3
"""
fix_jsonld_template_drift.py — z255t: 100 ja + 4 pt page の FAQPage JSON-LD で
literal `{tech["name"]}` が未置換のまま JSON に混入していた bug を fix.

generate_bjj_wiki.py 850 行の f-string nested 三項演算子で、JA/PT branch が
plain string (f-string でない) として書かれていたため、`{tech["name"]}` が
literal で出力されていた。これにより:
  - JSON parse error (unescaped double quote 含むため)
  - 技名が表示されない
  - rich snippet が機能しない

修正方針:
  各 page の <h1> から技名抽出 → `{tech["name"]}` を JSON-escaped value に置換。

generator script は別途 (line 850) で恒久 fix 済み。
"""
from __future__ import annotations
import re
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def extract_h1(html: str) -> str:
    """h1 から技名抽出 (HTML タグ除去)"""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    return re.sub(r"<[^>]+>", "", m.group(1)).strip()


def main():
    print("🔧 fix_jsonld_template_drift.py — z255t")
    fixed = 0
    failed = []
    for lang in ("ja", "pt"):
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            if '{tech["name"]}' not in html:
                continue
            name = extract_h1(html)
            if not name:
                # fallback to title
                m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
                if m:
                    title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                    # strip "| BJJ Wiki" etc.
                    name = re.split(r"\s*[|｜]\s*", title)[0].strip()
            if not name:
                failed.append(f"{lang}/{fp.name}")
                continue
            # JSON-safe replacement (escape " and \)
            name_json_safe = name.replace("\\", "\\\\").replace('"', '\\"')
            new = html.replace('{tech["name"]}', name_json_safe)
            if new != html:
                fp.write_text(new, encoding="utf-8")
                fixed += 1
    print(f"  ja + pt fixed: {fixed} files")
    if failed:
        print(f"  ⚠️  failed (no h1/title): {len(failed)}")
        for f in failed[:5]:
            print(f"     - {f}")


if __name__ == "__main__":
    main()
