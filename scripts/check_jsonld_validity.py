#!/usr/bin/env python3
"""
check_jsonld_validity.py — z255t: JSON-LD structured data validity (17th lint)

Schema.org JSON-LD は Google rich snippet の source。malformed JSON-LD は
silent fail で rich snippet が表示されないため検出が難しい。

検出する drift class:
  A. JSON parse error (literal `{var}` 未置換 / unescaped quotes 等)
  B. Missing @context (Schema.org spec 違反)
  C. Missing @type and missing @graph (top-level も @graph 配列もない)
  D. literal `{python_var}` template が JSON 文字列値に残留

--ci flag で error > 0 → exit 1
"""
from __future__ import annotations
import re
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "ja", "pt"]
SCRIPT_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL,
)
TEMPLATE_RE = re.compile(r"\{[a-zA-Z_]+(?:\[[^\]]+\])?\}")


def main() -> int:
    parse_errors = []
    no_context = []
    no_type = []
    template_residue = []
    total = 0

    for lang in LANGS:
        for fp in (REPO_ROOT / lang).glob("*.html"):
            try:
                html = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            src = f"{lang}/{fp.name}"
            for m in SCRIPT_RE.finditer(html):
                total += 1
                payload = m.group(1).strip()

                # Class D: literal template residue (raw text before JSON parse)
                # Allowlist: SearchAction's {search_term_string} is valid Schema.org syntax
                ALLOWED_TEMPLATE_VARS = {"{search_term_string}"}
                tm = TEMPLATE_RE.search(payload)
                if tm and tm.group(0) not in ALLOWED_TEMPLATE_VARS:
                    template_residue.append((src, tm.group(0)))

                # Class A: parse
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError as e:
                    parse_errors.append((src, str(e)[:60]))
                    continue

                if not isinstance(data, dict):
                    continue

                # Class B
                if "@context" not in data:
                    no_context.append(src)

                # Class C: needs @type OR @graph (Schema.org spec accepts both)
                if "@type" not in data and "@graph" not in data:
                    no_type.append(src)

    print(f"📋 Total ld+json blocks scanned: {total:,}")
    print(f"❌ A. JSON parse error:           {len(parse_errors)}")
    for src, e in parse_errors[:6]:
        print(f"   {src}: {e}")
    print(f"❌ B. Missing @context:           {len(no_context)}")
    for s in no_context[:6]:
        print(f"   {s}")
    print(f"❌ C. Missing @type and @graph:   {len(no_type)}")
    for s in no_type[:6]:
        print(f"   {s}")
    print(f"❌ D. Template {{var}} residue:    {len(template_residue)}")
    for src, t in template_residue[:6]:
        print(f"   {src}: {t}")

    total_err = (
        len(parse_errors) + len(no_context) + len(no_type) + len(template_residue)
    )
    if total_err == 0:
        print("\n✅ JSON-LD fully valid.")
    else:
        print(f"\n🔴 Total errors: {total_err}")

    if "--ci" in sys.argv:
        return 1 if total_err > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
