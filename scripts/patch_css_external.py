#!/usr/bin/env python3
"""
[IA-2] Wiki CSS外出しバッチパッチ
- 全HTMLファイルから <style>...</style> ブロックを除去
- <link rel="stylesheet" href="/wiki-components.css"> を除去
- <link rel="stylesheet" href="/wiki-v2.css"> を <head> 内に挿入
- ページ種別に応じた theme クラスを <body> に付与
- beta バッジの inline style を class="badge-beta" に置換
"""

import os
import re
import sys
from pathlib import Path

WIKI_ROOT = Path(__file__).resolve().parent.parent
LANG_DIRS = ["en", "ja", "pt"]

# CSS link to inject
CSS_LINK = '<link rel="stylesheet" href="/wiki-v2.css">'

# Stats
stats = {
    "processed": 0,
    "style_blocks_removed": 0,
    "wiki_components_removed": 0,
    "css_link_added": 0,
    "theme_class_added": 0,
    "beta_badge_fixed": 0,
    "errors": [],
}


def detect_theme(filepath: str) -> str:
    """Detect theme class from filename."""
    basename = os.path.basename(filepath)
    if basename.startswith("athlete-"):
        return "theme-athlete"
    if basename == "index.html":
        return "theme-index"
    # athletes-list, about etc could be theme-list, but currently none exist
    return ""  # default technique theme


def patch_file(filepath: str) -> bool:
    """Patch a single HTML file. Returns True if modified."""
    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()

    content = original

    # 1. Remove all <style>...</style> blocks (greedy within each block)
    style_count = len(re.findall(r"<style[\s>]", content, re.IGNORECASE))
    content = re.sub(
        r"\s*<style[^>]*>.*?</style>\s*",
        "\n",
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )
    stats["style_blocks_removed"] += style_count

    # 2. Remove <link rel="stylesheet" href="/wiki-components.css">
    if "/wiki-components.css" in content:
        content = re.sub(
            r'\s*<link\s+rel="stylesheet"\s+href="/wiki-components\.css"\s*/?\s*>\s*',
            "\n",
            content,
            flags=re.IGNORECASE,
        )
        stats["wiki_components_removed"] += 1

    # 3. Add wiki-v2.css link if not already present
    if "/wiki-v2.css" not in content:
        # Insert after <meta name="viewport" ...> or after <meta charset="UTF-8">
  <link rel="icon" href="https://wiki.bjj-app.net/favicon.svg" type="image/svg+xml">
        viewport_pattern = r'(<meta\s+name="viewport"[^>]*>)'
        charset_pattern = r'(<meta\s+charset="UTF-8"\s*/?>)'

        inserted = False
        if re.search(viewport_pattern, content, re.IGNORECASE):
            content = re.sub(
                viewport_pattern,
                r"\1\n" + CSS_LINK,
                content,
                count=1,
                flags=re.IGNORECASE,
            )
            inserted = True
        elif re.search(charset_pattern, content, re.IGNORECASE):
            content = re.sub(
                charset_pattern,
                r"\1\n" + CSS_LINK,
                content,
                count=1,
                flags=re.IGNORECASE,
            )
            inserted = True

        if inserted:
            stats["css_link_added"] += 1

    # 4. Add theme class to <body>
    theme = detect_theme(filepath)
    if theme:
        # <body> or <body class="...">
        if re.search(r"<body\s+class=", content, re.IGNORECASE):
            # Append theme to existing class if not already there
            if theme not in content:
                content = re.sub(
                    r'<body\s+class="([^"]*)"',
                    f'<body class="\\1 {theme}"',
                    content,
                    count=1,
                    flags=re.IGNORECASE,
                )
                stats["theme_class_added"] += 1
        elif re.search(r"<body>", content, re.IGNORECASE):
            content = content.replace("<body>", f'<body class="{theme}">', 1)
            stats["theme_class_added"] += 1
        elif re.search(r"<body\b", content, re.IGNORECASE):
            content = re.sub(
                r"<body\b",
                f'<body class="{theme}"',
                content,
                count=1,
                flags=re.IGNORECASE,
            )
            stats["theme_class_added"] += 1

    # 5. Replace beta badge inline style with class
    beta_pattern = r'<span\s+style="display:inline-block;font-size:\.6rem;font-weight:700;background:#7c3aed;color:#fff;border-radius:4px;padding:1px 5px;margin-left:5px;vertical-align:middle;letter-spacing:\.03em;line-height:1\.5">β</span>'
    if re.search(beta_pattern, content):
        content = re.sub(
            beta_pattern,
            '<span class="badge-beta">β</span>',
            content,
        )
        stats["beta_badge_fixed"] += 1

    # Write back only if changed
    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    dry_run = "--dry-run" in sys.argv

    for lang in LANG_DIRS:
        lang_dir = WIKI_ROOT / lang
        if not lang_dir.is_dir():
            print(f"⚠️  Directory not found: {lang_dir}")
            continue

        html_files = sorted(lang_dir.glob("*.html"))
        for filepath in html_files:
            try:
                if dry_run:
                    # Just count what would change
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    has_style = bool(re.search(r"<style[\s>]", content, re.IGNORECASE))
                    has_v2 = "/wiki-v2.css" in content
                    if has_style or not has_v2:
                        stats["processed"] += 1
                else:
                    modified = patch_file(str(filepath))
                    if modified:
                        stats["processed"] += 1
            except Exception as e:
                stats["errors"].append(f"{filepath}: {e}")

    # Report
    mode = "DRY RUN" if dry_run else "PATCHED"
    print(f"\n{'='*50}")
    print(f"  Wiki CSS External Patch — {mode}")
    print(f"{'='*50}")
    print(f"  Files modified:          {stats['processed']}")
    print(f"  <style> blocks removed:  {stats['style_blocks_removed']}")
    print(f"  wiki-components removed: {stats['wiki_components_removed']}")
    print(f"  wiki-v2.css link added:  {stats['css_link_added']}")
    print(f"  Theme classes added:     {stats['theme_class_added']}")
    print(f"  Beta badges fixed:       {stats['beta_badge_fixed']}")
    if stats["errors"]:
        print(f"\n  ⚠️  Errors ({len(stats['errors'])}):")
        for err in stats["errors"][:10]:
            print(f"    {err}")
    print()


if __name__ == "__main__":
    main()
