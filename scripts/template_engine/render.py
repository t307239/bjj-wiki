#!/usr/bin/env python3
"""
render.py — Template-driven Wiki page renderer (REF-2 W1, z255oo)

Renders a Wiki page (Technique archetype) from:
  - templates/archetypes/<archetype>.html.j2 (Jinja2 template)
  - templates/messages/<lang>.yml          (locale strings)
  - <input>.json                            (page-specific data)

Output: stdout or file. Goal is byte-equivalent (or near) to current
generate_bjj_wiki.py + patch chain output.

This is the **foundation** for REF-2 (Wiki template-driven refactor).
W1 = build the template + renderer.
W2 = run on 100 pages and verify byte diff = lint-fix-only.
W3 = expand to all 7 archetypes.
W4 = cutover (replace generator + retire patches).

Usage:
    python3 scripts/template_engine/render.py \\
        --archetype technique \\
        --lang en \\
        --data path/to/armbar.json \\
        --output /tmp/armbar.html

    # or pipe to stdout
    python3 scripts/template_engine/render.py \\
        --archetype technique \\
        --lang en \\
        --data path/to/armbar.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"
ARCHETYPES_DIR = TEMPLATES_DIR / "archetypes"
MESSAGES_DIR = TEMPLATES_DIR / "messages"


def load_locale(lang: str) -> dict:
    """Load locale messages YAML for the given language code."""
    fp = MESSAGES_DIR / f"{lang}.yml"
    if not fp.exists():
        raise FileNotFoundError(f"Locale file not found: {fp}")
    with fp.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_data(path: Path) -> dict:
    """Load page-specific data from JSON file."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def render_page(
    archetype: str,
    lang: str,
    page_data: dict,
    *,
    include_z243_cta: bool = True,
) -> str:
    """Render a page using archetype template + locale + page data.

    Note: HTML auto-escaping is OFF because the existing wiki output uses
    raw HTML in many fields (intro_paragraphs, faq.answer, etc.). This is
    consistent with how generate_bjj_wiki.py emits HTML today.
    """
    env = Environment(
        loader=FileSystemLoader(str(ARCHETYPES_DIR)),
        autoescape=False,  # match existing generator behavior
        undefined=StrictUndefined,  # fail loudly on missing variables
        trim_blocks=False,
        lstrip_blocks=False,
        keep_trailing_newline=True,
    )

    template = env.get_template(f"{archetype}.html.j2")
    locale = load_locale(lang)

    return template.render(
        page=page_data,
        t=locale,
        lang=lang,
        include_z243_cta=include_z243_cta,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archetype",
        required=True,
        choices=["technique"],  # W1: technique only; W3 will expand
        help="Page archetype (technique / concept / rule / etc.)",
    )
    parser.add_argument(
        "--lang",
        required=True,
        choices=["en", "ja", "pt"],
        help="Locale code",
    )
    parser.add_argument(
        "--data",
        required=True,
        type=Path,
        help="Path to JSON file with page-specific data",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output HTML file path (default: stdout)",
    )
    parser.add_argument(
        "--no-z243-cta",
        action="store_true",
        help="Skip z243 CTA marker blocks (let patch_funnel_cta handle it)",
    )
    args = parser.parse_args()

    if not args.data.exists():
        print(f"❌ data file not found: {args.data}", file=sys.stderr)
        return 1

    page_data = load_data(args.data)

    html = render_page(
        archetype=args.archetype,
        lang=args.lang,
        page_data=page_data,
        include_z243_cta=not args.no_z243_cta,
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(html, encoding="utf-8")
        print(f"✅ Rendered: {args.output} ({len(html)} bytes)", file=sys.stderr)
    else:
        sys.stdout.write(html)

    return 0


if __name__ == "__main__":
    sys.exit(main())
