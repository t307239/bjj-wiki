#!/usr/bin/env python3
"""
Generate per-page OG images (SVG) for all BJJ Wiki pages.

Each page gets a unique SVG OG image with:
- The page title prominently displayed
- BJJ Wiki branding
- Consistent dark SaaS design

Updates each HTML file's og:image meta tag to point to the page-specific SVG.
twitter:image uses the default og-image.png (Twitter does not support SVG).

Usage:
    python3 scripts/gen_og_images.py          # Generate for all pages
    python3 scripts/gen_og_images.py --dry-run # Preview without writing
"""

import os
import re
import sys
import html

WIKI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OG_DIR = os.path.join(WIKI_ROOT, "og")
SITE_URL = "https://wiki.bjj-app.net"
LANGS = ["en", "ja", "pt"]

# Default PNG for Twitter (SVG not supported by Twitter)
DEFAULT_TWITTER_IMAGE = f"{SITE_URL}/og-image.png"

# Maximum title length before we shrink font
TITLE_MAX_SINGLE_LINE = 35


def escape_svg(text: str) -> str:
    """Escape text for SVG XML content."""
    return html.escape(text, quote=True)


def wrap_title(title: str, max_chars: int = 30) -> list[str]:
    """Split title into multiple lines for SVG display."""
    words = title.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if len(test) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines[:3]  # Max 3 lines


def generate_og_svg(title: str, lang: str) -> str:
    """Generate an SVG OG image for a specific page."""
    safe_title = escape_svg(title)
    lines = wrap_title(title, max_chars=30)

    # Dynamic font sizing based on title length
    if len(lines) == 1 and len(title) <= 20:
        font_size = 64
        y_start = 310
    elif len(lines) == 1:
        font_size = 52
        y_start = 310
    elif len(lines) == 2:
        font_size = 48
        y_start = 280
    else:
        font_size = 40
        y_start = 260

    line_height = int(font_size * 1.3)

    # Build title lines
    title_elements = ""
    for i, line in enumerate(lines):
        y = y_start + (i * line_height)
        title_elements += f'  <text x="600" y="{y}" font-family="Arial Black, sans-serif" font-size="{font_size}" font-weight="900" fill="#e8eaf6" text-anchor="middle">{escape_svg(line)}</text>\n'

    # Language badge
    lang_labels = {"en": "English", "ja": "日本語", "pt": "Português"}
    lang_label = lang_labels.get(lang, lang.upper())

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0B1120"/>
      <stop offset="50%" stop-color="#141930"/>
      <stop offset="100%" stop-color="#0B1120"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#7c6af7"/>
      <stop offset="100%" stop-color="#a78bfa"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect x="0" y="0" width="1200" height="5" fill="url(#accent)"/>
  <rect x="0" y="625" width="1200" height="5" fill="url(#accent)"/>
  <text x="600" y="160" font-family="Arial Black, sans-serif" font-size="28" fill="#6b7699" text-anchor="middle" letter-spacing="6">BJJ WIKI</text>
{title_elements}  <text x="600" y="500" font-family="Arial, sans-serif" font-size="22" fill="#4a5170" text-anchor="middle">wiki.bjj-app.net</text>
  <rect x="510" y="520" width="180" height="32" rx="16" fill="#7c6af720" stroke="#7c6af740" stroke-width="1"/>
  <text x="600" y="542" font-family="Arial, sans-serif" font-size="15" fill="#a78bfa" text-anchor="middle">{escape_svg(lang_label)}</text>
</svg>'''


def extract_title(html_content: str) -> str | None:
    """Extract page title from HTML."""
    # Try og:title first
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html_content)
    if m:
        return html.unescape(m.group(1))
    # Fallback to <title>
    m = re.search(r"<title>([^<]+)</title>", html_content)
    if m:
        title = html.unescape(m.group(1))
        # Strip common suffixes
        title = re.sub(r"\s*[|–—]\s*BJJ Wiki.*$", "", title)
        return title.strip()
    return None


def update_og_image_tag(html_content: str, og_image_url: str) -> str:
    """Replace or add og:image meta tag in HTML."""
    new_tag = f'<meta property="og:image" content="{og_image_url}">'
    if 'property="og:image"' in html_content:
        html_content = re.sub(
            r'<meta\s+property="og:image"\s+content="[^"]*"\s*/?>',
            new_tag,
            html_content,
        )
    else:
        html_content = html_content.replace("</head>", f"  {new_tag}\n</head>")
    return html_content


def update_twitter_image_tag(html_content: str, twitter_image_url: str) -> str:
    """Replace or add twitter:image meta tag (PNG for Twitter compatibility)."""
    new_tag = f'<meta name="twitter:image" content="{twitter_image_url}">'
    if 'name="twitter:image"' in html_content:
        html_content = re.sub(
            r'<meta\s+name="twitter:image"\s+content="[^"]*"\s*/?>',
            new_tag,
            html_content,
        )
    else:
        # Insert after og:image or before </head>
        if 'property="og:image"' in html_content:
            html_content = re.sub(
                r'(<meta\s+property="og:image"\s+content="[^"]*"\s*/?>)',
                rf'\1\n{new_tag}',
                html_content,
            )
        else:
            html_content = html_content.replace("</head>", f"  {new_tag}\n</head>")
    return html_content


def main():
    dry_run = "--dry-run" in sys.argv

    os.makedirs(OG_DIR, exist_ok=True)

    total = 0
    updated = 0

    for lang in LANGS:
        lang_dir = os.path.join(WIKI_ROOT, lang)
        if not os.path.isdir(lang_dir):
            continue

        for fname in sorted(os.listdir(lang_dir)):
            if not fname.endswith(".html"):
                continue

            total += 1
            fpath = os.path.join(lang_dir, fname)
            slug = fname.replace(".html", "")

            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            title = extract_title(content)
            if not title:
                continue

            # Generate SVG
            svg_content = generate_og_svg(title, lang)
            svg_filename = f"{lang}-{slug}.svg"
            svg_path = os.path.join(OG_DIR, svg_filename)
            og_image_url = f"{SITE_URL}/og/{svg_filename}"

            if not dry_run:
                with open(svg_path, "w", encoding="utf-8") as f:
                    f.write(svg_content)

                # Update HTML — og:image = per-page SVG, twitter:image = default PNG
                new_content = update_og_image_tag(content, og_image_url)
                new_content = update_twitter_image_tag(new_content, DEFAULT_TWITTER_IMAGE)
                if new_content != content:
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    updated += 1

            if total <= 3:
                print(f"  [{lang}] {title[:50]} → {svg_filename}")

    action = "Would generate" if dry_run else "Generated"
    print(f"\n{action} {total} OG images, updated {updated} HTML files")


if __name__ == "__main__":
    main()
