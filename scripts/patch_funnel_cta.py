#!/usr/bin/env python3
"""
patch_funnel_cta.py — z175: Wiki → アプリ登録 funnel 強化

各記事に CTA は中段 1 箇所しかなく、上部/末尾/floating が欠落していたため、
スクロール 0% / 末尾到達 / 中スクロール の 3 機会で離脱していた問題を解消。

【追加する CTA】
  1. Top Hero CTA — H1 直後 (above the fold, fold 上で見える)
  2. Bottom CTA  — FAQ 後・footer 前 (記事完読後)
  3. Floating CTA — fixed bottom-right, スクロール 30% で出現 + ✕で dismiss
                    (localStorage に dismiss 状態 7日間保持)

すべて i18n: lang ディレクトリ (en/ja/pt) で copy 切替。

【Idempotent】
  - <!-- z175-top-cta --> / z175-bottom-cta / z175-float-cta マーカー付与で再実行 OK
  - 既存の `cta-banner` (中段) は触らない

Usage:
    python3 scripts/patch_funnel_cta.py [--dry-run]
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── Localized copy ─────────────────────────────────────────────────────────
COPY = {
    "en": {
        "top_title": "🥋 Track your BJJ training",
        "top_sub": "Free forever. Sessions, techniques, streaks — all in one app.",
        "top_btn": "Start Free →",
        "bot_title": "📱 Stop forgetting what you drilled",
        "bot_sub": "Log every roll. Map every technique. Build the streak.",
        "bot_btn": "Open BJJ App — Free →",
        "float_title": "📱 Track your training",
        "float_sub": "Sessions, techniques, streaks. Free.",
        "float_btn": "Start Free →",
    },
    "ja": {
        "top_title": "🥋 練習を記録するならBJJ App",
        "top_sub": "永久無料。セッション・テクニック・連続記録をひとつに。",
        "top_btn": "無料で始める →",
        "bot_title": "📱 ドリルした技、明日も覚えてる？",
        "bot_sub": "全ロールを記録。全技をマップ化。連続記録を伸ばそう。",
        "bot_btn": "BJJ App を開く — 無料 →",
        "float_title": "📱 練習を記録",
        "float_sub": "セッション・技術・連続。無料。",
        "float_btn": "無料で始める →",
    },
    "pt": {
        "top_title": "🥋 Registre seu treino de BJJ",
        "top_sub": "Grátis para sempre. Sessões, técnicas e sequências em um só lugar.",
        "top_btn": "Começar Grátis →",
        "bot_title": "📱 Pare de esquecer o que treinou",
        "bot_sub": "Registre cada rola. Mapeie cada técnica. Construa a sequência.",
        "bot_btn": "Abrir BJJ App — Grátis →",
        "float_title": "📱 Registre seu BJJ",
        "float_sub": "Sessões, técnicas e sequências. Grátis.",
        "float_btn": "Começar Grátis →",
    },
}

# ── HTML templates ─────────────────────────────────────────────────────────

def top_cta_html(c: dict, lang: str) -> str:
    return (
        f'<!-- z175-top-cta --><div class="z175-top-cta" '
        f'style="margin:1rem 0 1.5rem;padding:14px 18px;background:linear-gradient(135deg,#0d2010 0%,#0a1a0d 100%);'
        f'border:1px solid #2e7d32;border-radius:12px;display:flex;align-items:center;justify-content:space-between;'
        f'gap:1rem;flex-wrap:wrap">'
        f'<div style="flex:1;min-width:200px">'
        f'<div style="font-weight:700;color:#a5d6a7;font-size:.95rem">{c["top_title"]}</div>'
        f'<div style="font-size:.85rem;color:#c8e6c9;margin-top:2px">{c["top_sub"]}</div>'
        f'</div>'
        f'<a href="https://bjj-app.net/login?ref=wiki&page=top" '
        f'style="background:#10B981;color:#fff;padding:8px 16px;border-radius:8px;text-decoration:none;'
        f'font-weight:700;font-size:.9rem;white-space:nowrap" '
        f"onclick=\"window.gtag&&gtag('event','wiki_cta_click',{{position:'top',lang:'{lang}'}})\">"
        f'{c["top_btn"]}</a>'
        f'</div>'
    )


def bottom_cta_html(c: dict, lang: str) -> str:
    return (
        f'<!-- z175-bottom-cta --><div class="z175-bottom-cta" '
        f'style="margin:2rem 0;padding:24px 24px;background:linear-gradient(135deg,#0d2010 0%,#0a1a0d 100%);'
        f'border:2px solid #2e7d32;border-radius:14px;text-align:center">'
        f'<div style="font-weight:700;color:#a5d6a7;font-size:1.1rem;margin-bottom:6px">{c["bot_title"]}</div>'
        f'<div style="font-size:.9rem;color:#c8e6c9;margin-bottom:16px">{c["bot_sub"]}</div>'
        f'<a href="https://bjj-app.net/login?ref=wiki&page=bottom" '
        f'style="display:inline-block;background:#10B981;color:#fff;padding:12px 28px;border-radius:10px;'
        f'text-decoration:none;font-weight:700;font-size:1rem" '
        f"onclick=\"window.gtag&&gtag('event','wiki_cta_click',{{position:'bottom',lang:'{lang}'}})\">"
        f'{c["bot_btn"]}</a>'
        f'</div>'
    )


def float_cta_html(c: dict, lang: str) -> str:
    """Sticky floating CTA — appears after scroll 30%, dismissable for 7 days."""
    return f'''<!-- z175-float-cta --><div id="z175-float" style="position:fixed;bottom:20px;right:20px;max-width:280px;background:#0d2010;border:1px solid #2e7d32;border-radius:14px;padding:16px 18px;box-shadow:0 4px 20px rgba(0,200,83,.15);z-index:999;display:none;animation:slideUp .3s ease">
<button onclick="document.getElementById('z175-float').style.display='none';try{{localStorage.setItem('z175_float_dismissed',Date.now())}}catch(e){{}}" style="position:absolute;top:8px;right:12px;background:none;border:none;color:#546e7a;font-size:1rem;cursor:pointer;line-height:1" aria-label="Close">✕</button>
<div style="font-weight:700;color:#a5d6a7;margin-bottom:6px;font-size:.9rem">{c["float_title"]}</div>
<p style="font-size:.8rem;color:#c8e6c9;margin:0 0 12px">{c["float_sub"]}</p>
<a href="https://bjj-app.net/login?ref=wiki&page=float" style="display:block;background:#10B981;color:#fff;padding:8px 16px;border-radius:8px;text-decoration:none;font-weight:700;font-size:.85rem;text-align:center" onclick="window.gtag&&gtag('event','wiki_cta_click',{{position:'float',lang:'{lang}'}})">{c["float_btn"]}</a>
</div>
<style>@keyframes slideUp{{from{{transform:translateY(20px);opacity:0}}to{{transform:translateY(0);opacity:1}}}}</style>
<script>(function(){{
try{{
  var d=localStorage.getItem('z175_float_dismissed');
  if(d && (Date.now()-parseInt(d,10))<7*86400000) return;
}}catch(e){{}}
var el=document.getElementById('z175-float');
if(!el) return;
var shown=false;
function check(){{if(shown) return; var sp=(window.scrollY/(document.documentElement.scrollHeight-window.innerHeight))*100; if(sp>=30){{el.style.display='block';shown=true;window.removeEventListener('scroll',check);}}}}
window.addEventListener('scroll',check,{{passive:true}});
}})();</script>'''


# ── Patch logic ────────────────────────────────────────────────────────────

H1_END_RE = re.compile(r"</h1>", re.IGNORECASE)
FAQ_SECTION_END_RE = re.compile(r"</section>\s*\n\s*</div>\s*\n\s*<footer", re.IGNORECASE | re.DOTALL)
FOOTER_RE = re.compile(r"<footer\b", re.IGNORECASE)
BODY_END_RE = re.compile(r"</body>", re.IGNORECASE)


def patch_file(fp: Path, lang: str, dry_run: bool) -> tuple[bool, list[str]]:
    """Returns (modified, actions_list)."""
    try:
        c = fp.read_text(encoding="utf-8")
    except Exception:
        return False, [f"read_error"]

    actions = []
    orig = c

    if lang not in COPY:
        return False, [f"unknown_lang_{lang}"]

    copy = COPY[lang]

    # 1. Top CTA — insert after first </h1>
    if "z175-top-cta" not in c:
        m = H1_END_RE.search(c)
        if m:
            insert_at = m.end()
            c = c[:insert_at] + "\n" + top_cta_html(copy, lang) + c[insert_at:]
            actions.append("top")

    # 2. Bottom CTA — insert before <footer> (after FAQ if any)
    if "z175-bottom-cta" not in c:
        # Find the LAST <footer> tag (in case of nested/multiple)
        footer_matches = list(FOOTER_RE.finditer(c))
        if footer_matches:
            insert_at = footer_matches[-1].start()
            # Walk back to find the closing </div> or </section> just before <footer>
            # We just want to insert right before <footer>
            c = c[:insert_at] + bottom_cta_html(copy, lang) + "\n" + c[insert_at:]
            actions.append("bottom")

    # 3. Floating CTA — insert before </body>
    if "z175-float-cta" not in c:
        m = BODY_END_RE.search(c)
        if m:
            insert_at = m.start()
            c = c[:insert_at] + float_cta_html(copy, lang) + "\n" + c[insert_at:]
            actions.append("float")

    if c == orig:
        return False, []

    if not dry_run:
        fp.write_text(c, encoding="utf-8")

    return True, actions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Don't write files")
    parser.add_argument("--lang", choices=["en", "ja", "pt", "all"], default="all")
    args = parser.parse_args()

    langs = ["en", "ja", "pt"] if args.lang == "all" else [args.lang]
    total_modified = 0
    total_actions = {"top": 0, "bottom": 0, "float": 0}

    for lang in langs:
        d = ROOT / lang
        if not d.exists():
            print(f"  ⚠️  {lang}/ not found, skipping")
            continue
        files = sorted(d.glob("*.html"))
        modified_in_lang = 0
        for fp in files:
            # Skip non-article pages (index, 404 etc. — these have own CTA design)
            if fp.name in ("index.html", "404.html", "about.html", "search.html"):
                continue
            modified, actions = patch_file(fp, lang, args.dry_run)
            if modified:
                modified_in_lang += 1
                for a in actions:
                    total_actions[a] = total_actions.get(a, 0) + 1
        print(f"  {lang}/: {modified_in_lang}/{len(files)} files modified")
        total_modified += modified_in_lang

    print()
    print(f"Total files modified: {total_modified}")
    print(f"  + Top CTA:    {total_actions['top']} insertions")
    print(f"  + Bottom CTA: {total_actions['bottom']} insertions")
    print(f"  + Float CTA:  {total_actions['float']} insertions")
    if args.dry_run:
        print("(dry-run — no writes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
