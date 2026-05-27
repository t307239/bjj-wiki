#!/usr/bin/env python3
"""
Add BreadcrumbList JSON-LD to all pages missing it.
"""
import os, re, json

BASE_URL = 'https://wiki.bjj-app.net'
fixed = 0

for lang in ['en', 'ja', 'pt']:
    for fname in sorted(os.listdir(lang)):
        if not fname.endswith('.html'): continue
        path = f'{lang}/{fname}'
        with open(path) as f:
            content = f.read()

        if 'BreadcrumbList' in content:
            continue

        # Build breadcrumb
        title_m = re.search(r'<title>([^<|]+)', content)
        page_title = title_m.group(1).strip() if title_m else fname.replace('.html','').replace('-',' ').title()

        breadcrumb = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "BJJ Wiki",
                    "item": f"{BASE_URL}/{lang}/index.html"
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": page_title,
                    "item": f"{BASE_URL}/{lang}/{fname}"
                }
            ]
        }

        schema_html = f'<script type="application/ld+json">\n{json.dumps(breadcrumb, ensure_ascii=False, indent=2)}\n</script>'
        content = content.replace('</head>', f'{schema_html}\n</head>', 1)

        with open(path, 'w') as f:
            f.write(content)
        fixed += 1

print(f"Added BreadcrumbList to: {fixed} pages")
