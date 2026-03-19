#!/usr/bin/env python3
"""
Rebuild bjj-gi-brands-guide.html for en / ja / pt
with country-specific Amazon links and famous local brands.

EN → amazon.com  (US brands: Fuji, Sanabul, Hayabusa, Origin, Tatami)
JA → amazon.co.jp (JP brands: Isami, A-Force, FUJI, Scramble, Venum)
PT → amazon.com.br (BR brands: Atama, Koral, Gameness, Storm, Tatami)
"""

import os

WIKI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = "bjj06-22"

# ── Per-language config ──────────────────────────────────────────────────────
LANG_CFG = {
    "en": {
        "html_lang": "en",
        "title": "Top BJJ Gi Brands 2026: Complete Buyer's Guide | BJJ Wiki",
        "h1":    "Top BJJ Gi Brands 2026",
        "desc":  "Best BJJ Gi brands compared: Fuji, Sanabul, Hayabusa, Origin, Tatami & more. Reviews, recommendations, and direct links to top gis.",
        "canon": "https://t307239.github.io/bjj-wiki/en/bjj-gi-brands-guide.html",
        "nav_home": "🏠 Home",
        "nav_home_href": "../en/index.html",
        "amazon_domain": "amazon.com",
        "aff_tag": TAG,
        "hero_sub": "Best gis available on Amazon.com — reviewed by competitors",
        "cta_note": "PR: Affiliate links — price is the same for you",
        "section_premium": "🇺🇸 Top US/International Brands",
        "section_budget": "💰 Budget Picks",
        "section_nogi": "🩳 No-Gi Gear",
        "section_compare": "📊 Quick Comparison",
        "section_tips": "📐 Sizing & Care Tips",
        # Famous brands with Amazon search links
        "brands": [
            {
                "name": "Fuji Sports All Around BJJ Gi",
                "badge": "🏆 Best Seller",
                "desc": "Trusted by competitors worldwide. Gold weave, IBJJF legal, multiple colors.",
                "price": "$140–$165",
                "asin": "B071GFHRBB",  # direct DP link
                "label": "View on Amazon",
            },
            {
                "name": "Sanabul Essential BJJ Gi",
                "badge": "💲 Best Budget",
                "desc": "Top-rated starter gi. Pearl weave, lightweight, great for training.",
                "price": "$80–$100",
                "asin": "B0BLX6G61R",  # white
                "label": "View on Amazon",
            },
            {
                "name": "Hayabusa Pearl Weave BJJ Gi",
                "badge": "⚡ Lightweight",
                "desc": "500 GSM pearl weave — cool and durable for hot gyms.",
                "price": "$130–$160",
                "asin": "B079XB9VKH",
                "label": "View on Amazon",
            },
            {
                "name": "Origin American Jiu-Jitsu Gi",
                "badge": "🇺🇸 Made in USA",
                "desc": "Made in Maine. Rip-stop weave, excellent durability for heavy training.",
                "price": "$180–$220",
                "search": "Origin+BJJ+gi+american+made",
                "label": "Search on Amazon",
            },
            {
                "name": "Tatami Estilo 7.0 BJJ Gi",
                "badge": "🎖 Competition Grade",
                "desc": "Slim-fit competition cut. Ultra-light, IBJJF approved, used at Worlds.",
                "price": "$160–$200",
                "search": "Tatami+Estilo+BJJ+gi",
                "label": "Search on Amazon",
            },
        ],
        "budget_brands": [
            {
                "name": "Venum Contender BJJ Gi",
                "badge": "🔵 Popular",
                "search": "Venum+Contender+BJJ+gi",
                "label": "View on Amazon",
            },
            {
                "name": "Elite Sports BJJ Gi",
                "badge": "🟢 Beginner",
                "search": "Elite+Sports+BJJ+gi",
                "label": "View on Amazon",
            },
        ],
        "nogi": [
            {
                "name": "Sanabul Submission No-Gi Shorts",
                "search": "Sanabul+no+gi+grappling+shorts",
                "label": "View on Amazon",
            },
            {
                "name": "Hayabusa Athletic BJJ Rash Guard",
                "search": "Hayabusa+rash+guard+BJJ",
                "label": "View on Amazon",
            },
        ],
        "compare_rows": [
            ("Fuji All Around", "$140–165", "Gold", "IBJJF ✓", "★★★★★"),
            ("Sanabul Essential", "$80–100", "Pearl", "IBJJF ✓", "★★★★☆"),
            ("Hayabusa Pearl", "$130–160", "Pearl", "IBJJF ✓", "★★★★☆"),
            ("Origin American", "$180–220", "Rip-stop", "IBJJF ✓", "★★★★★"),
            ("Tatami Estilo", "$160–200", "Ultra-light", "IBJJF ✓", "★★★★★"),
        ],
        "tips": [
            ("Sizing", "Order your normal size then pre-shrink with hot wash + dryer once. Gis typically shrink 3–5%."),
            ("Fit", "Sleeve ends 2\" above wrist. Pants end 2\" above ankle. Test mobility: hip escape, armbar drill."),
            ("Care", "Cold wash + hang dry extends life. Wash immediately after every session to prevent bacteria."),
            ("IBJJF rules", "Patches must not cover more than 35 cm². Check color rules: white, blue, or black only for IBJJF."),
        ],
    },

    "ja": {
        "html_lang": "ja",
        "title": "BJJ道衣ブランドガイド 2026：柔術着おすすめ比較 | BJJ Wiki",
        "h1":    "BJJ道衣ブランドガイド 2026",
        "desc":  "ブラジリアン柔術の道衣（ギ）おすすめブランド比較：伊佐見・FUJI・Scramble・Venum・Tatami。アマゾンで買える人気道衣を一覧で紹介。",
        "canon": "https://t307239.github.io/bjj-wiki/ja/bjj-gi-brands-guide.html",
        "nav_home": "🏠 ホーム",
        "nav_home_href": "../ja/index.html",
        "amazon_domain": "amazon.co.jp",
        "aff_tag": TAG,
        "hero_sub": "Amazon.co.jp で買える人気BJJ道衣レビュー",
        "cta_note": "PR: アフィリエイトリンク — 価格は変わりません",
        "section_premium": "🇯🇵 日本で人気のBJJ道衣ブランド",
        "section_budget": "💰 コスパ重視の道衣",
        "section_nogi": "🩳 ノーギ / ラッシュガード",
        "section_compare": "📊 ブランド比較表",
        "section_tips": "📐 サイズ・ケアのコツ",
        "brands": [
            {
                "name": "伊佐見（Isami）BJJ柔術着",
                "badge": "🇯🇵 国産ブランド",
                "desc": "日本の柔道・柔術道衣メーカー。丈夫な二重織り、IJFアマゾン取り扱いあり。",
                "price": "¥12,000–¥25,000",
                "search": "伊佐見+柔術着+BJJ",
                "label": "Amazonで検索",
            },
            {
                "name": "FUJI Sports BJJ Gi",
                "badge": "🏆 定番人気",
                "desc": "国際的に定評のあるFUJIの道衣。ゴールドウィーブで耐久性が高く試合向き。",
                "price": "¥15,000–¥22,000",
                "search": "FUJI+柔術着+BJJ+道衣",
                "label": "Amazonで検索",
            },
            {
                "name": "Scramble BJJ Gi",
                "badge": "⚡ デザイン豊富",
                "desc": "英国発・日本でも人気のScramble。軽量パールウィーブで動きやすい。",
                "price": "¥18,000–¥28,000",
                "search": "Scramble+BJJ+道衣+ギ",
                "label": "Amazonで検索",
            },
            {
                "name": "Venum Contender BJJ Gi",
                "badge": "🔵 コスパ良好",
                "desc": "Venumのエントリーモデル。初心者から中級者まで対応、カラー展開豊富。",
                "price": "¥10,000–¥16,000",
                "search": "Venum+柔術道衣+BJJ",
                "label": "Amazonで検索",
            },
            {
                "name": "Tatami Estilo BJJ Gi",
                "badge": "🎖 試合用",
                "desc": "世界大会でも使用される軽量試合用道衣。IBJJF公認カラー対応。",
                "price": "¥20,000–¥30,000",
                "search": "Tatami+BJJ+道衣+柔術",
                "label": "Amazonで検索",
            },
        ],
        "budget_brands": [
            {
                "name": "Sanabul エッセンシャル BJJ Gi",
                "badge": "💲 入門向け",
                "search": "Sanabul+BJJ+道衣",
                "label": "Amazonで検索",
            },
            {
                "name": "A-Force 柔術着",
                "badge": "🟢 日本製",
                "search": "A-Force+柔術着",
                "label": "Amazonで検索",
            },
        ],
        "nogi": [
            {
                "name": "グラップリング用ショーツ",
                "search": "グラップリングショーツ+ノーギ+柔術",
                "label": "Amazonで検索",
            },
            {
                "name": "ラッシュガード 長袖 BJJ",
                "search": "ラッシュガード+長袖+柔術+BJJ",
                "label": "Amazonで検索",
            },
        ],
        "compare_rows": [
            ("伊佐見", "¥12,000–25,000", "二重織り", "IBJJF ✓", "★★★★☆"),
            ("FUJI", "¥15,000–22,000", "ゴールド", "IBJJF ✓", "★★★★★"),
            ("Scramble", "¥18,000–28,000", "パール", "IBJJF ✓", "★★★★★"),
            ("Venum", "¥10,000–16,000", "パール", "IBJJF ✓", "★★★★☆"),
            ("Tatami Estilo", "¥20,000–30,000", "超軽量", "IBJJF ✓", "★★★★★"),
        ],
        "tips": [
            ("サイズ選び", "熱いお湯で1回洗って縮みを確認してから本格使用を。道衣は一般的に3〜5%縮みます。"),
            ("フィット感", "袖口は手首から5cm上、裾はくるぶしから5cm上が目安。可動域をチェックして。"),
            ("お手入れ", "練習後すぐに洗濯（冷水）→陰干しが基本。臭い・菌の繁殖を防ぎます。"),
            ("IBJJF規定", "パッチの合計面積は35cm²以下。色はホワイト・ブルー・ブラックのみ試合OK。"),
        ],
    },

    "pt": {
        "html_lang": "pt",
        "title": "Melhores Marcas de Kimono BJJ 2026: Guia Completo | BJJ Wiki",
        "h1":    "Melhores Marcas de Kimono BJJ 2026",
        "desc":  "Comparação das melhores marcas de kimono de Jiu-Jitsu Brasileiro: Atama, Koral, Tatami, Gameness e mais. Links diretos para comprar na Amazon.",
        "canon": "https://t307239.github.io/bjj-wiki/pt/bjj-gi-brands-guide.html",
        "nav_home": "🏠 Início",
        "nav_home_href": "../pt/index.html",
        "amazon_domain": "amazon.com.br",
        "aff_tag": TAG,
        "hero_sub": "Os melhores kimonos disponíveis na Amazon.com.br",
        "cta_note": "PR: Links de afiliado — preço é o mesmo para você",
        "section_premium": "🇧🇷 Marcas Brasileiras e Internacionais Top",
        "section_budget": "💰 Opções Custo-Benefício",
        "section_nogi": "🩳 Equipamento No-Gi",
        "section_compare": "📊 Comparação Rápida",
        "section_tips": "📐 Dicas de Tamanho e Cuidados",
        "brands": [
            {
                "name": "Atama Single Weave Gi",
                "badge": "🇧🇷 Marca Icônica",
                "desc": "A marca mais tradicional do BJJ. Qualidade comprovada, usada por campeões mundiais desde os anos 90.",
                "price": "R$ 250–450",
                "search": "Atama+kimono+jiu+jitsu",
                "label": "Ver na Amazon",
            },
            {
                "name": "Koral Classic BJJ Gi",
                "badge": "🏆 Alta Performance",
                "desc": "Marca brasileira premium. Tecido resistente, corte atlético, IBJJF aprovado.",
                "price": "R$ 300–550",
                "search": "Koral+kimono+jiu-jitsu+bjj",
                "label": "Ver na Amazon",
            },
            {
                "name": "Gameness Pearl Gi",
                "badge": "⚡ Peso Leve",
                "desc": "Kimono pearl weave leve e durável. Ótimo para competição e treinos intensos.",
                "price": "R$ 280–480",
                "search": "Gameness+kimono+jiu-jitsu",
                "label": "Ver na Amazon",
            },
            {
                "name": "Storm Kimonos BJJ Gi",
                "badge": "🎨 Design Moderno",
                "desc": "Marca brasileira com designs exclusivos. Algodão de alta qualidade, fit atlético.",
                "price": "R$ 260–420",
                "search": "Storm+kimono+BJJ+jiu-jitsu",
                "label": "Ver na Amazon",
            },
            {
                "name": "Tatami Estilo BJJ Gi",
                "badge": "🎖 Internacional",
                "desc": "Kimono ultra-leve usado em campeonatos mundiais. IBJJF aprovado, corte slim.",
                "price": "R$ 400–650",
                "search": "Tatami+kimono+BJJ+brasil",
                "label": "Ver na Amazon",
            },
        ],
        "budget_brands": [
            {
                "name": "Venum Contender BJJ Gi",
                "badge": "🔵 Custo-Benefício",
                "search": "Venum+kimono+jiu-jitsu",
                "label": "Ver na Amazon",
            },
            {
                "name": "Sanabul Essential BJJ Gi",
                "badge": "💲 Iniciante",
                "search": "Sanabul+kimono+BJJ",
                "label": "Ver na Amazon",
            },
        ],
        "nogi": [
            {
                "name": "Short de Grappling No-Gi",
                "search": "short+grappling+no-gi+jiu-jitsu",
                "label": "Ver na Amazon",
            },
            {
                "name": "Rash Guard Manga Longa BJJ",
                "search": "rash+guard+jiu-jitsu+bjj+manga+longa",
                "label": "Ver na Amazon",
            },
        ],
        "compare_rows": [
            ("Atama", "R$ 250–450", "Single/Double", "IBJJF ✓", "★★★★★"),
            ("Koral", "R$ 300–550", "Pearl", "IBJJF ✓", "★★★★★"),
            ("Gameness", "R$ 280–480", "Pearl", "IBJJF ✓", "★★★★☆"),
            ("Storm", "R$ 260–420", "Cotton", "IBJJF ✓", "★★★★☆"),
            ("Tatami Estilo", "R$ 400–650", "Ultra-light", "IBJJF ✓", "★★★★★"),
        ],
        "tips": [
            ("Escolha do tamanho", "Faça uma pré-lavagem em água quente para verificar a encolhimento (3–5%). Consulte a tabela de medidas da marca."),
            ("Caimento", "Manga deve terminar 5 cm acima do pulso. Calça deve terminar 5 cm acima do tornozelo."),
            ("Cuidados", "Lave imediatamente após o treino (água fria) e seque na sombra. Evita bactérias e odores."),
            ("Regras IBJJF", "Patches no máximo 35 cm². Cores aceitas: branco, azul ou preto. Verifique antes de competir."),
        ],
    },
}

# ── HTML template ────────────────────────────────────────────────────────────
GTM_JS = """<script async src="https://www.googletagmanager.com/gtag/js?id=G-7LM8L3TRZM"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','G-7LM8L3TRZM');</script>"""

def amazon_link(cfg, brand):
    domain = cfg["amazon_domain"]
    tag    = cfg["aff_tag"]
    if "asin" in brand:
        return f"https://www.{domain}/dp/{brand['asin']}?tag={tag}"
    else:
        q = brand["search"]
        return f"https://www.{domain}/s?k={q}&tag={tag}"

def brand_card(cfg, brand):
    link  = amazon_link(cfg, brand)
    name  = brand["name"]
    badge = brand.get("badge", "")
    desc  = brand.get("desc", "")
    price = brand.get("price", "")
    label = brand.get("label", "View")
    return f"""
  <div style="background:#111827;border:1px solid #1e2a3a;border-radius:12px;padding:18px;margin-bottom:14px">
    <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:8px">
      <strong style="color:#e2b714;font-size:1rem">{name}</strong>
      <span style="background:#1e2a3a;color:#7c3aed;border-radius:20px;padding:3px 10px;font-size:.78rem;white-space:nowrap">{badge}</span>
    </div>
    {f'<p style="color:#9ca3af;font-size:.88rem;margin:0 0 10px">{desc}</p>' if desc else ''}
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
      {f'<span style="color:#4ade80;font-weight:700;font-size:.9rem">{price}</span>' if price else '<span></span>'}
      <a href="{link}" rel="sponsored noopener" target="_blank"
         style="background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;padding:7px 16px;border-radius:8px;text-decoration:none;font-size:.85rem;font-weight:700">
        🛒 {label}
      </a>
    </div>
  </div>"""

def build_page(lang, cfg):
    hreflang_links = "\n".join([
        f'  <link rel="alternate" hreflang="{l}" href="https://t307239.github.io/bjj-wiki/{l}/bjj-gi-brands-guide.html">'
        for l in ["en","ja","pt"]
    ])
    hreflang_links += '\n  <link rel="alternate" hreflang="x-default" href="https://t307239.github.io/bjj-wiki/en/bjj-gi-brands-guide.html">'

    premium_cards = "\n".join(brand_card(cfg, b) for b in cfg["brands"])
    budget_cards  = "\n".join(brand_card(cfg, b) for b in cfg["budget_brands"])
    nogi_cards    = "\n".join(brand_card(cfg, b) for b in cfg["nogi"])

    compare_rows_html = "\n".join(
        f"    <tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"
        for r in cfg["compare_rows"]
    )

    tips_html = "\n".join(
        f'  <div style="background:#111827;border:1px solid #1e2a3a;border-radius:10px;padding:14px 18px;margin-bottom:10px"><strong style="color:#7c3aed">{t[0]}</strong><p style="color:#9ca3af;margin:6px 0 0;font-size:.88rem">{t[1]}</p></div>'
        for t in cfg["tips"]
    )

    nav_links_by_lang = {
        "en": [("../en/index.html","🏠 Home"),("../en/bjj-gi-buying-guide.html","🛍 Buying Guide"),
               ("../en/bjj-gi-care-guide.html","🧺 Gi Care"),("../en/bjj-nogi-gear-guide.html","👕 No-Gi"),
               ("../en/bjj-training-equipment-guide.html","🏋 Equipment")],
        "ja": [("../ja/index.html","🏠 ホーム"),("../ja/bjj-gi-buying-guide.html","🛍 購入ガイド"),
               ("../ja/bjj-gi-care-guide.html","🧺 道衣ケア"),("../ja/bjj-nogi-gear-guide.html","👕 ノーギ"),
               ("../ja/bjj-training-equipment-guide.html","🏋 練習器具")],
        "pt": [("../pt/index.html","🏠 Início"),("../pt/bjj-gi-buying-guide.html","🛍 Guia de Compra"),
               ("../pt/bjj-gi-care-guide.html","🧺 Cuidados"),("../pt/bjj-nogi-gear-guide.html","👕 No-Gi"),
               ("../pt/bjj-training-equipment-guide.html","🏋 Equipamentos")],
    }
    nav_html = "\n  ".join(f'<a href="{h}">{l}</a>' for h,l in nav_links_by_lang[lang])

    compare_headers = {
        "en": ("Brand","Price","Weave","IBJJF","Rating"),
        "ja": ("ブランド","価格","生地","IBJJF","評価"),
        "pt": ("Marca","Preço","Tecido","IBJJF","Avaliação"),
    }[lang]

    ld_lang = {"en":"en","ja":"ja","pt":"pt-BR"}[lang]
    ld_pub_name = "BJJ Wiki"

    html = f"""<!DOCTYPE html>
<html lang="{cfg['html_lang']}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{cfg['title']}</title>
  <meta name="description" content="{cfg['desc']}">
  <link rel="canonical" href="{cfg['canon']}">
{hreflang_links}
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5529701443220352" crossorigin="anonymous"></script>
  <style>
    :root{{--bg:#0b0f1a;--card:#111827;--accent:#7c3aed;--accent2:#e94560;--text:#e2e8f0;--muted:#64748b;--border:rgba(255,255,255,.08)}}
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',sans-serif;font-size:16px;line-height:1.8}}
    #read-progress{{position:fixed;top:0;left:0;width:0%;height:3px;background:var(--accent);z-index:9999;transition:width .1s linear}}
    header{{background:linear-gradient(135deg,#0f1a2e,#1a1040);padding:24px 20px;text-align:center;border-bottom:2px solid var(--accent)}}
    header h1{{color:#e2b714;font-size:1.8rem;margin-bottom:6px}}
    header p{{color:var(--muted);font-size:.9rem}}
    nav{{background:var(--card);padding:10px 20px;display:flex;gap:12px;flex-wrap:wrap;justify-content:center;font-size:.85rem;border-bottom:1px solid var(--border)}}
    nav a{{color:var(--muted);text-decoration:none}}nav a:hover{{color:#e2b714}}
    .container{{max-width:800px;margin:0 auto;padding:28px 16px}}
    h2{{color:#e2b714;font-size:1.15rem;font-weight:700;margin:32px 0 14px;padding-left:12px;border-left:3px solid var(--accent);scroll-margin-top:80px}}
    p{{color:#c2c2d9;margin-bottom:14px;font-size:.95rem}}
    table{{width:100%;border-collapse:collapse;margin:16px 0;font-size:.88rem}}
    th{{background:#1e2a3a;color:#e2b714;padding:10px;text-align:left}}
    td{{padding:9px 10px;border-bottom:1px solid #1e2a3a;color:var(--text)}}
    tr:hover td{{background:rgba(255,255,255,.03)}}
    .tip-box{{background:#0d2d0d;border-left:4px solid #4ade80;border-radius:8px;padding:14px 18px;margin:20px 0}}
    .tip-box strong{{color:#4ade80}}
    footer{{background:#060d1a;text-align:center;padding:28px;color:var(--muted);font-size:.8rem;margin-top:40px}}
    footer a{{color:var(--muted);text-decoration:none}}
    /* wiki sidebar */
    .wiki-sidebar{{position:fixed;top:88px;left:max(12px,calc(50% - 560px));width:180px;max-height:calc(100vh - 108px);overflow-y:auto;scrollbar-width:none;z-index:20}}
    .wiki-sidebar::-webkit-scrollbar{{display:none}}
    .wiki-toc-link{{display:block;font-size:.78rem;color:var(--muted);text-decoration:none;padding:5px 10px;border-radius:5px;margin:1px 0;border-left:2px solid transparent;transition:all .15s;line-height:1.35}}
    .wiki-toc-link:hover{{color:var(--text);background:rgba(255,255,255,.05)}}
    .wiki-toc-link.active{{color:#e2b714;border-left-color:#e2b714;background:rgba(226,183,20,.07)}}
    @media(max-width:1200px){{.wiki-sidebar{{display:none}}}}
  </style>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Article","headline":"{cfg['h1']}","description":"{cfg['desc']}","url":"{cfg['canon']}","datePublished":"2026-03-19","dateModified":"2026-03-19","publisher":{{"@type":"Organization","name":"{ld_pub_name}","url":"https://t307239.github.io/bjj-wiki/"}},"inLanguage":"{ld_lang}"}}
  </script>
  {GTM_JS}
</head>
<body>
<div id="read-progress"></div>
<header><h1>{cfg['h1']}</h1><p>{cfg['hero_sub']}</p></header>
<nav>
  {nav_html}
</nav>
<div class="container">

<h2>{cfg['section_premium']}</h2>
{premium_cards}

<h2>{cfg['section_budget']}</h2>
{budget_cards}

<h2>{cfg['section_nogi']}</h2>
{nogi_cards}

<h2>{cfg['section_compare']}</h2>
<table>
<tr><th>{compare_headers[0]}</th><th>{compare_headers[1]}</th><th>{compare_headers[2]}</th><th>{compare_headers[3]}</th><th>{compare_headers[4]}</th></tr>
{compare_rows_html}
</table>

<h2>{cfg['section_tips']}</h2>
{tips_html}

<div class="tip-box">
  <strong>🥋 BJJ App</strong>
  <p style="margin-top:6px">Track your training, techniques & streaks — free at <a href="https://bjj-app-one.vercel.app" style="color:#4ade80">bjj-app-one.vercel.app</a></p>
</div>

</div><!-- /container -->

<footer>
  <p>BJJ Wiki — Free Brazilian Jiu-Jitsu resource · <a href="https://bjj-app-one.vercel.app">Train smarter with BJJ App →</a></p>
  <p>Affiliate links support this site at no extra cost to you.</p>
</footer>

<script>
(function(){{
  var prog=document.getElementById('read-progress');
  if(prog){{
    window.addEventListener('scroll',function(){{
      var st=window.scrollY,dh=document.body.scrollHeight-window.innerHeight;
      if(dh>0)prog.style.width=(st/dh*100)+'%';
    }});
  }}
  if(window.innerWidth<1200)return;
  var hs=document.querySelectorAll('.container h2');
  if(hs.length<2)return;
  hs.forEach(function(h,i){{if(!h.id)h.id='hs'+i;}});
  var sb=document.createElement('nav');sb.className='wiki-sidebar';
  var logo=document.createElement('div');
  logo.style.cssText='font-size:.78rem;font-weight:800;color:#e2e8f0;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid rgba(255,255,255,.08)';
  logo.innerHTML='BJJ<span style="color:#e2b714">Wiki</span>';sb.appendChild(logo);
  var links=[];
  hs.forEach(function(h){{
    var a=document.createElement('a');a.className='wiki-toc-link';
    a.href='#'+h.id;a.textContent=h.textContent.replace(/^[\\s\\u200b]+/,'');
    sb.appendChild(a);links.push(a);
  }});
  document.body.appendChild(sb);
  if('IntersectionObserver' in window){{
    var io=new IntersectionObserver(function(entries){{
      entries.forEach(function(e){{
        if(e.isIntersecting){{
          links.forEach(function(l){{l.classList.remove('active');}});
          var al=sb.querySelector('a[href="#'+e.target.id+'"]');
          if(al)al.classList.add('active');
        }}
      }});
    }},{{rootMargin:'-15% 0px -75% 0px'}});
    hs.forEach(function(h){{io.observe(h);}});
  }}
}})();
</script>
</body>
</html>"""
    return html

def main():
    print("Rebuilding gear pages with country-specific Amazon links...")
    for lang, cfg in LANG_CFG.items():
        out_path = os.path.join(WIKI_DIR, lang, "bjj-gi-brands-guide.html")
        html = build_page(lang, cfg)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        size_kb = os.path.getsize(out_path) / 1024
        print(f"  ✅ {lang}/bjj-gi-brands-guide.html — {size_kb:.0f}KB")
    print("Done.")

if __name__ == "__main__":
    main()
