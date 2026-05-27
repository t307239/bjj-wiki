#!/usr/bin/env python3
"""
z262 — Search Console 404 redirect fix
Root causes:
  Group A: 10 root-level URLs (Google cached from old sitemap/era)
  Group D:  4 en/ pages that were renamed
  Twitter: 436 en/ pages with <strong> in share URL text= params (HTML invalid)
"""
import re
from pathlib import Path

REPO = Path(__file__).parent.parent
SITE_URL = "https://wiki.bjj-app.net"
MARKER = "<!-- z262-redirect -->"

def make_redirect_html(canonical_url: str, title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  {MARKER}
  <meta http-equiv="refresh" content="0; url={canonical_url}">
  <link rel="canonical" href="{canonical_url}">
  <title>{title}</title>
</head>
<body>
  <p>Redirecting to <a href="{canonical_url}">{canonical_url}</a></p>
  <script>window.location.replace("{canonical_url}");</script>
</body>
</html>
"""

# ── Group A: root-level → en/ redirects ──────────────────────────────────────
ROOT_REDIRECTS = [
    "guard-pass",
    "knee-slice-pass",
    "de-la-riva-guard",
    "headquarters-pass",
    "leg-drag-pass",
    "closed-guard",
    "open-guard",
    "half-guard",
    "spider-guard",
    "techniques-az",
]

# ── Group D: missing en/ → correct en/ redirects ─────────────────────────────
EN_REDIRECTS = {
    "takedowns":    "bjj-collar-tie-takedowns",   # closest general takedowns
    "double-leg":   "double-leg-takedown",
    "collar-grip":  "bjj-collar-grip-guide",
    "lapel-guard":  "bjj-lapel-guard-guide",
}

created = 0
skipped = 0

# Group A
for slug in ROOT_REDIRECTS:
    dest = f"{SITE_URL}/en/{slug}.html"
    target = REPO / f"{slug}.html"
    # 既にmarkerがあればスキップ (idempotent)
    if target.exists() and MARKER in target.read_text(encoding="utf-8"):
        skipped += 1
        continue
    target.write_text(make_redirect_html(dest, f"Redirecting to {dest}"), encoding="utf-8")
    print(f"  [A] created {target.name} → {dest}")
    created += 1

# Group D
for slug, dest_slug in EN_REDIRECTS.items():
    dest = f"{SITE_URL}/en/{dest_slug}.html"
    target = REPO / "en" / f"{slug}.html"
    if target.exists() and MARKER in target.read_text(encoding="utf-8"):
        skipped += 1
        continue
    target.write_text(make_redirect_html(dest, f"Redirecting to {dest}"), encoding="utf-8")
    print(f"  [D] created en/{slug}.html → {dest}")
    created += 1

print(f"\n  Group A+D: {created} created, {skipped} skipped (already exist)")

# ── Fix 3: Twitter/Reddit share URL の <strong> 除去 ─────────────────────────
# en/のみ (ja/pt は0件)
SHARE_PATTERN = re.compile(
    r'(<a\s+[^>]*href="https://(twitter\.com/intent/tweet|www\.reddit\.com/submit)\?[^"]*)'
    r'(<strong>.*?</strong>)'
    r'([^"]*")',
    re.DOTALL
)

def strip_html_tags(s: str) -> str:
    return re.sub(r'<[^>]+>', '', s)

fixed_files = 0
fixed_links = 0

for html_file in sorted((REPO / "en").glob("*.html")):
    content = html_file.read_text(encoding="utf-8")
    if "<strong>" not in content:
        continue
    # Twitter/Reddit shareのhref内にある<strong>を除去
    # href="https://twitter.com/...text=XXX <strong>YYY</strong> ZZZ..."
    # → href="https://twitter.com/...text=XXX YYY ZZZ..."
    def fix_share_href(m: re.Match) -> str:
        full = m.group(0)
        # href全体を取得してから<strong>を除去
        return re.sub(r'<strong>(.*?)</strong>', r'\1', full)

    # より正確なパターン: href="..."内の<strong>のみ対象
    HREF_TAG_PAT = re.compile(
        r'(href="https://(twitter\.com|reddit\.com)[^"]*)<(?:/?strong)[^>]*>([^"]*")',
        re.DOTALL
    )
    new_content = content
    count = 0
    while True:
        m = HREF_TAG_PAT.search(new_content)
        if not m:
            break
        replacement = m.group(1) + m.group(3)
        new_content = new_content[:m.start()] + replacement + new_content[m.end():]
        count += 1

    if count > 0:
        html_file.write_text(new_content, encoding="utf-8")
        fixed_files += 1
        fixed_links += count
        print(f"  [T] {html_file.name}: {count} <strong> removed from share URLs")

print(f"\n  Twitter/Reddit fix: {fixed_files} files, {fixed_links} occurrences fixed")
