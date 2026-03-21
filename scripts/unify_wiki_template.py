#!/usr/bin/env python3
"""
BJJ Wiki — フルテンプレート統一スクリプト

全ページの <style> ブロックを Type C（最新テンプレート）の統一CSSに完全差し替え。
HTML構造は変えず、CSSだけで見た目を統一する。

統一CSS:
- :root変数: bg/#0f172a, card/#18181b, accent/#e94560, accent2/#7c3aed
- header: minimal border-bottom, logo + lang-nav
- container: max-width 860px
- h2: #e94560 accent color with border-bottom
- フォント: 16px, line-height 1.8
- progress bar + back-to-top
"""
import os
import re

WIKI_ROOT = os.path.join(os.path.dirname(__file__), "..")
LANGS = ["en", "ja", "pt"]

# 統一CSS（Type Cベース、App UI_DESIGN.mdに準拠）
UNIFIED_CSS = """    :root{--bg:#0f172a;--card:#18181b;--card-hover:#1c1c22;--border:rgba(255,255,255,0.10);--border-hover:rgba(233,69,96,0.5);--text:#e2e8f0;--muted:#64748b;--accent:#e94560;--accent2:#7c3aed}
    *{box-sizing:border-box;margin:0;padding:0}
    body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:16px;line-height:1.8}
    .container{max-width:860px;margin:0 auto;padding:20px 16px 80px}
    header{border-bottom:1px solid var(--border);padding-bottom:16px;margin-bottom:24px;text-align:left}
    header h1{color:var(--accent);font-size:1.6rem;font-weight:800;margin-bottom:6px;letter-spacing:-0.02em}
    header p{color:var(--muted);font-size:.95rem}
    .logo{font-size:1.1rem;font-weight:700;color:var(--accent);letter-spacing:-0.02em;text-decoration:none}
    .lang-nav{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
    .lang-nav a{color:var(--muted);text-decoration:none;font-size:.85rem;padding:2px 8px;border-radius:4px;border:1px solid var(--border);transition:all .2s}
    .lang-nav a.active,.lang-nav a:hover{color:var(--text);border-color:var(--accent)}
    nav{background:var(--card);padding:10px 20px;display:flex;gap:12px;flex-wrap:wrap;justify-content:center;font-size:.85rem;border-radius:8px;margin-bottom:16px}
    nav a{color:var(--muted);text-decoration:none}
    nav a:hover{color:var(--accent)}
    .breadcrumb{font-size:.8rem;color:var(--muted);margin-bottom:12px}
    .breadcrumb a{color:var(--muted);text-decoration:none}
    .breadcrumb a:hover{color:var(--text)}
    h1{font-size:1.6rem;font-weight:800;line-height:1.3;margin-bottom:12px;letter-spacing:-0.02em}
    h2{font-size:1.2rem;font-weight:700;color:var(--accent);margin:28px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--border)}
    h3{color:#7c3aed;margin:20px 0 8px;font-size:1.05rem}
    p{color:var(--text);margin-bottom:12px}
    ul,ol{padding-left:20px;margin-bottom:14px}
    li{margin-bottom:6px;color:var(--text)}
    a{color:var(--accent);text-decoration:none}
    a:hover{text-decoration:underline}
    .meta-badges{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;align-items:center}
    .badge{font-size:.75rem;padding:3px 10px;border-radius:12px;font-weight:600;border:1px solid var(--border)}
    .badge-belt{color:#fff;background:#1d4ed833;border-color:#1d4ed866}
    .badge-cat{color:var(--accent);background:rgba(233,69,96,0.1);border-color:rgba(233,69,96,0.3)}
    .badge-diff{color:var(--muted)}
    .intro{color:var(--muted);font-size:1rem;margin-bottom:24px;padding:14px 16px;background:var(--card);border-left:3px solid var(--accent);border-radius:0 8px 8px 0}
    .toc{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px 20px;margin-bottom:28px}
    .toc h3{font-size:.85rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin-bottom:10px}
    .toc ol{padding-left:20px}
    .toc li{margin:4px 0}
    .toc a{color:var(--accent);text-decoration:none;font-size:.9rem}
    .toc a:hover{text-decoration:underline}
    section{margin-bottom:32px;scroll-margin-top:80px}
    .tips-box,.tip-box{background:var(--card);border:1px solid rgba(233,69,96,0.2);border-radius:12px;padding:16px 20px;margin:28px 0}
    .tips-box h3,.tip-box h3{font-size:.85rem;text-transform:uppercase;letter-spacing:.05em;color:var(--accent);margin-bottom:12px}
    .tips-box ul,.tip-box ul{list-style:none;padding:0}
    .tips-box li,.tip-box li{padding:6px 0 6px 20px;position:relative;font-size:.95rem;color:var(--text)}
    .tips-box li::before,.tip-box li::before{content:'▸';position:absolute;left:0;color:var(--accent)}
    .cta-banner{background:linear-gradient(135deg,rgba(233,69,96,0.15),rgba(124,58,237,0.1));border:1px solid rgba(233,69,96,0.3);border-radius:12px;padding:16px 20px;text-align:center;margin:28px 0}
    .cta-banner a{color:var(--accent);text-decoration:none;font-weight:700;font-size:1rem}
    .cta-banner a:hover{text-decoration:underline}
    .share-bar{display:flex;align-items:center;gap:10px;margin-top:32px;padding-top:16px;border-top:1px solid var(--border)}
    .share-bar a{color:var(--text);text-decoration:none;font-size:.85rem;padding:6px 14px;border:1px solid var(--border);border-radius:20px;transition:all .2s}
    .share-bar a:hover{border-color:var(--accent);color:var(--accent)}
    footer{text-align:center;color:var(--muted);font-size:.8rem;margin-top:48px;padding-top:16px;border-top:1px solid var(--border)}
    footer a{color:var(--muted);text-decoration:none}
    .progress-bar{position:fixed;top:0;left:0;width:0%;height:3px;background:linear-gradient(to right,var(--accent),var(--accent2));z-index:999;transition:width .1s}
    .back-to-top,#back-to-top{position:fixed;bottom:24px;right:24px;background:var(--accent);color:#fff;border:none;border-radius:50%;width:40px;height:40px;font-size:18px;cursor:pointer;display:none;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(233,69,96,0.4);z-index:100}
    .float-cta{position:fixed;bottom:80px;right:20px;background:var(--accent2);color:#fff;padding:8px 16px;border-radius:20px;font-size:.85rem;font-weight:600;text-decoration:none;display:none;align-items:center;z-index:100;box-shadow:0 4px 12px rgba(0,0,0,0.3)}
    .gi-shops h2{color:var(--accent)}
    .gi-shops h3{color:var(--text)}
    @media(max-width:600px){h1{font-size:1.3rem}header h1{font-size:1.3rem}}"""

count = 0
for lang in LANGS:
    langdir = os.path.join(WIKI_ROOT, lang)
    if not os.path.isdir(langdir):
        continue
    for fname in os.listdir(langdir):
        if not fname.endswith(".html") or fname == "index.html":
            continue
        fpath = os.path.join(langdir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace existing <style>...</style> with unified CSS
        new_content = re.sub(
            r'<style>.*?</style>',
            f'<style>\n{UNIFIED_CSS}\n  </style>',
            content,
            count=1,
            flags=re.DOTALL
        )

        if new_content != content:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            count += 1

print(f"Template CSS unified in {count} pages")
