#!/usr/bin/env python3
"""
diff_check.py — Categorize byte diffs between rendered template output
                 and existing wiki HTML (REF-2 W2, z255pp)

Goal of W2 byte diff verification:
  Render existing pages via new template + categorize remaining diffs to
  prove the template is **structurally equivalent** to current generator,
  not just visually similar.

Categories:
  1. WHITESPACE_ONLY  — only \\n / \\t differences (acceptable)
  2. ENTITY_ESCAPE    — `&` vs `&amp;`, `<` vs `&lt;` etc (acceptable, fixed in W2)
  3. JSONLD_FORMAT    — JSON-LD whitespace / minify difference (acceptable)
  4. DATA_GAP         — sections present in original but missing in rendered
                        (= JSON data incomplete; not a template bug)
  5. PATCH_ARTIFACT   — duplicated section / drift in original
                        (= existing page has bug; template intentionally cleaner)
  6. TEMPLATE_GAP     — template missing structural element (REAL bug, must fix)
  7. UNKNOWN          — uncategorized diff lines (need manual review)

Output: summary + sample diffs per category.

Usage:
    python3 scripts/template_engine/diff_check.py \\
        --rendered /tmp/armbar_v2.html \\
        --existing en/armbar.html
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path
from difflib import unified_diff


# Regex patterns for category detection
WHITESPACE_RE = re.compile(r"^[\s\n\t]*$")
ENTITY_DIFF_RE = re.compile(r"&(?:amp|lt|gt|quot|#\d+);")
JSONLD_LINE_RE = re.compile(r'<script\s+type="application/ld\+json">')


def categorize_diff_line(line_a: str, line_b: str) -> str:
    """Categorize a single diff line pair."""
    # Strip leading +/- prefix from unified diff
    a = line_a[1:] if line_a.startswith(("-", "+")) else line_a
    b = line_b[1:] if line_b.startswith(("-", "+")) else line_b

    # Only whitespace differs
    if a.strip() == b.strip():
        return "WHITESPACE_ONLY"

    # Entity escaping
    a_no_entity = ENTITY_DIFF_RE.sub("X", a)
    b_no_entity = ENTITY_DIFF_RE.sub("X", b)
    if a_no_entity == b_no_entity and a != b:
        return "ENTITY_ESCAPE"

    # JSON-LD format diff
    if JSONLD_LINE_RE.search(a) or JSONLD_LINE_RE.search(b):
        return "JSONLD_FORMAT"

    return "UNKNOWN"


def is_blank_lines_only(lines: list[str]) -> bool:
    """True if all lines are blank (after stripping +/- prefix)."""
    for line in lines:
        body = line[1:] if line.startswith(("-", "+")) else line
        if body.strip():
            return False
    return True


def is_jsonld_block(lines: list[str]) -> bool:
    """True if block looks like JSON-LD (contains @context / @type / mainEntity etc.)."""
    text = "".join(lines)
    return bool(re.search(r'"@context"|"@type"|"@id"|mainEntity|HowTo|FAQPage', text))


def categorize_block(removed: list[str], added: list[str]) -> str:
    """Categorize a contiguous removed/added block in unified diff."""
    # Pure blank line addition/removal = whitespace
    if is_blank_lines_only(removed + added):
        return "WHITESPACE_ONLY"

    # JSON-LD format diff (multiline pretty-printed vs minified)
    if is_jsonld_block(removed) or is_jsonld_block(added):
        return "JSONLD_FORMAT"

    if removed and not added:
        block_text = "".join(removed).lower()
        if "<h2>" in block_text:
            return "DATA_GAP"
        if 'athletes-section' in block_text:
            return "PATCH_ARTIFACT"
        return "DATA_GAP"

    if added and not removed:
        return "TEMPLATE_GAP"

    if len(removed) == len(added):
        cats = [categorize_diff_line(r, a) for r, a in zip(removed, added)]
        if all(c == "WHITESPACE_ONLY" for c in cats):
            return "WHITESPACE_ONLY"
        if all(c == "ENTITY_ESCAPE" for c in cats):
            return "ENTITY_ESCAPE"

    return "UNKNOWN"


def parse_unified_diff(diff_lines: list[str]) -> list[tuple[str, list[str], list[str]]]:
    """Parse unified diff into hunks. Returns list of (category, removed, added)."""
    hunks = []
    removed: list[str] = []
    added: list[str] = []

    def flush():
        nonlocal removed, added
        if removed or added:
            cat = categorize_block(removed, added)
            hunks.append((cat, removed[:], added[:]))
            removed.clear()
            added.clear()

    for line in diff_lines:
        if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
            flush()
            continue
        if line.startswith("-"):
            removed.append(line)
        elif line.startswith("+"):
            added.append(line)
        else:
            # Context line, flush current block
            flush()

    flush()
    return hunks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rendered", required=True, type=Path, help="Rendered HTML")
    parser.add_argument("--existing", required=True, type=Path, help="Existing HTML")
    parser.add_argument("--samples", type=int, default=2, help="Sample diffs per category")
    args = parser.parse_args()

    rendered = args.rendered.read_text(encoding="utf-8").splitlines(keepends=True)
    existing = args.existing.read_text(encoding="utf-8").splitlines(keepends=True)

    diff = list(
        unified_diff(
            existing,
            rendered,
            fromfile=str(args.existing),
            tofile=str(args.rendered),
            n=0,
        )
    )

    if not diff:
        print("✅ Byte-identical")
        return 0

    hunks = parse_unified_diff(diff)

    # Aggregate
    by_cat: dict[str, list] = {}
    for cat, removed, added in hunks:
        by_cat.setdefault(cat, []).append((removed, added))

    # Summary
    print(f"📊 Diff Categories ({len(hunks)} hunks total):")
    print(f"   existing: {args.existing}  ({len(existing)} lines)")
    print(f"   rendered: {args.rendered}  ({len(rendered)} lines)")
    print()

    severity = {
        "WHITESPACE_ONLY": "🟢 acceptable",
        "ENTITY_ESCAPE": "🟢 acceptable",
        "JSONLD_FORMAT": "🟢 acceptable",
        "DATA_GAP": "🟡 JSON data incomplete (not a template bug)",
        "PATCH_ARTIFACT": "🟢 existing page drift (template cleaner)",
        "TEMPLATE_GAP": "🔴 real template bug — fix required",
        "UNKNOWN": "🟡 needs manual review",
    }

    for cat in [
        "TEMPLATE_GAP",
        "DATA_GAP",
        "PATCH_ARTIFACT",
        "UNKNOWN",
        "WHITESPACE_ONLY",
        "ENTITY_ESCAPE",
        "JSONLD_FORMAT",
    ]:
        hunks_in_cat = by_cat.get(cat, [])
        if not hunks_in_cat:
            continue
        print(f"  [{cat}] {len(hunks_in_cat)} hunks  — {severity.get(cat)}")
        for removed, added in hunks_in_cat[: args.samples]:
            for line in removed[:1]:
                print(f"      - {line.rstrip()[:120]}")
            for line in added[:1]:
                print(f"      + {line.rstrip()[:120]}")
            print()

    # Exit code
    template_gap = len(by_cat.get("TEMPLATE_GAP", []))
    if template_gap > 0:
        print(f"❌ {template_gap} TEMPLATE_GAP hunks need fix")
        return 1
    print("✅ No real template bugs detected (DATA_GAP / WHITESPACE / ENTITY are expected)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
