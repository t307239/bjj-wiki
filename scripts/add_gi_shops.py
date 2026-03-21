#!/usr/bin/env python3
"""
BJJ Wiki — 各国の有名道着ショップリンクを全ギア関連ページに追加

対象ページ: en/ja/pt の gi-brands, best-bjj-gi, gi-buying-guide, gi-care-guide
"""
import os
import re

WIKI_ROOT = os.path.join(os.path.dirname(__file__), "..")

SHOPS = {
    "en": {
        "title": "Where to Buy BJJ Gi — Top Shops by Country",
        "shops": [
            ("🇺🇸 USA", [
                ("BJJHQ", "https://www.bjjhq.com"),
                ("Scramble", "https://www.scramblestuff.com"),
                ("Tatami Fightwear", "https://www.tatamifightwear.com"),
                ("Hyperfly", "https://www.hyperfly.com"),
                ("Origin", "https://www.originmaine.com"),
            ]),
            ("🇧🇷 Brazil", [
                ("Keiko Raca", "https://www.keikoraca.com.br"),
                ("Vulkan", "https://www.vulkanfc.com"),
                ("Oss Clothing", "https://www.ossclothing.com.br"),
            ]),
            ("🇬🇧 UK / Europe", [
                ("Tatami Fightwear UK", "https://www.tatamifightwear.com"),
                ("Scramble UK", "https://www.scramblestuff.com"),
                ("Kingz Kimonos", "https://www.kingz.com"),
            ]),
            ("🇯🇵 Japan", [
                ("Isami", "https://www.isami.co.jp"),
                ("Bull Terrier", "https://www.bullterrier.co.jp"),
                ("Alma", "https://www.alma-fight.com"),
                ("Amazon.co.jp (BJJ Gi)", "https://www.amazon.co.jp/s?k=BJJ+道着"),
            ]),
            ("🇦🇺 Australia", [
                ("Kingz Australia", "https://www.kingz.com.au"),
                ("Progress Jiu Jitsu", "https://www.progressjj.com"),
            ]),
        ],
    },
    "ja": {
        "title": "道着の購入先 — 各国の有名ショップ",
        "shops": [
            ("🇯🇵 日本", [
                ("Isami", "https://www.isami.co.jp"),
                ("Bull Terrier", "https://www.bullterrier.co.jp"),
                ("Alma", "https://www.alma-fight.com"),
                ("Amazon.co.jp (BJJ道着)", "https://www.amazon.co.jp/s?k=BJJ+道着"),
            ]),
            ("🇺🇸 アメリカ", [
                ("BJJHQ", "https://www.bjjhq.com"),
                ("Scramble", "https://www.scramblestuff.com"),
                ("Tatami Fightwear", "https://www.tatamifightwear.com"),
                ("Hyperfly", "https://www.hyperfly.com"),
            ]),
            ("🇧🇷 ブラジル", [
                ("Keiko Raca", "https://www.keikoraca.com.br"),
                ("Vulkan", "https://www.vulkanfc.com"),
            ]),
            ("🇬🇧 イギリス / ヨーロッパ", [
                ("Tatami Fightwear", "https://www.tatamifightwear.com"),
                ("Kingz Kimonos", "https://www.kingz.com"),
            ]),
            ("🇦🇺 オーストラリア", [
                ("Kingz Australia", "https://www.kingz.com.au"),
            ]),
        ],
    },
    "pt": {
        "title": "Onde Comprar Kimono BJJ — Lojas por País",
        "shops": [
            ("🇧🇷 Brasil", [
                ("Keiko Raca", "https://www.keikoraca.com.br"),
                ("Vulkan", "https://www.vulkanfc.com"),
                ("Oss Clothing", "https://www.ossclothing.com.br"),
            ]),
            ("🇺🇸 EUA", [
                ("BJJHQ", "https://www.bjjhq.com"),
                ("Scramble", "https://www.scramblestuff.com"),
                ("Tatami Fightwear", "https://www.tatamifightwear.com"),
            ]),
            ("🇯🇵 Japão", [
                ("Isami", "https://www.isami.co.jp"),
                ("Bull Terrier", "https://www.bullterrier.co.jp"),
            ]),
            ("🇬🇧 Europa", [
                ("Tatami Fightwear", "https://www.tatamifightwear.com"),
                ("Kingz Kimonos", "https://www.kingz.com"),
            ]),
        ],
    },
}

GI_PAGES = [
    "bjj-gi-brands-guide.html",
    "best-bjj-gi-guide.html",
    "bjj-gi-buying-guide.html",
]

def build_shop_html(lang_data):
    html = f'\n<section class="gi-shops" style="margin:32px 0;padding:24px;background:#18181b;border:1px solid rgba(255,255,255,0.10);border-radius:12px">\n'
    html += f'  <h2 style="color:#e94560;margin-bottom:16px">{lang_data["title"]}</h2>\n'
    for region, shops in lang_data["shops"]:
        html += f'  <h3 style="color:#e2e8f0;margin:16px 0 8px;font-size:1rem">{region}</h3>\n'
        html += '  <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px">\n'
        for name, url in shops:
            html += f'    <a href="{url}" target="_blank" rel="noopener noreferrer" style="display:inline-block;padding:6px 14px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.10);border-radius:8px;color:#e2e8f0;text-decoration:none;font-size:0.85rem;transition:border-color 0.2s" onmouseover="this.style.borderColor=\'#e94560\'" onmouseout="this.style.borderColor=\'rgba(255,255,255,0.10)\'">{name}</a>\n'
        html += '  </div>\n'
    html += '</section>\n'
    return html

count = 0
for lang in ["en", "ja", "pt"]:
    if lang not in SHOPS:
        continue
    shop_html = build_shop_html(SHOPS[lang])
    langdir = os.path.join(WIKI_ROOT, lang)
    for page in GI_PAGES:
        fpath = os.path.join(langdir, page)
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        # Don't add if already present
        if "gi-shops" in content:
            continue
        # Insert before </body> or before footer
        if "<footer>" in content:
            content = content.replace("<footer>", shop_html + "<footer>")
        elif "</body>" in content:
            content = content.replace("</body>", shop_html + "</body>")
        else:
            continue
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        count += 1
        print(f"  Added shops to: {lang}/{page}")

print(f"\nTotal pages updated: {count}")
