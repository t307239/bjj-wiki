#!/usr/bin/env python3
"""
patch_funnel_cta.py — z176: Wiki → アプリ登録 funnel (再設計版)

【z175 の反省】 4 CTA (top/中段/bottom/float) は過剰。Hevy/Strava/Notion を
ベンチマークすると業界標準は 1-2 placement に集中。本実装は **末尾 + Floating**
の 2 placement に絞り、コピーは generic ("Track your training") から具体的価値
("Map your weak positions") に変更。

【設置する CTA】
  1. Bottom CTA  — FAQ 後・footer 前 (記事完読後の最も意欲が高い瞬間)
  2. Floating CTA — fixed bottom-right、scroll 30% で出現 + ✕ で 7 日 dismiss

【削除した CTA】
  - Top Hero CTA (H1 直後) — 記事冒頭の集中阻害、CVR 寄与少と判定
    z175 の `<!-- z175-top-cta -->` ブロックは本スクリプトが自動除去する。

すべて i18n: lang ディレクトリ (en/ja/pt) で copy 切替。

【Idempotent】
  - <!-- z176-bottom-cta --> / z176-float-cta マーカーで再実行 OK
  - z175-top-cta マーカーがあれば自動削除 (rollback)
  - 既存の `cta-banner` (中段) は触らない

Usage:
    python3 scripts/patch_funnel_cta.py [--dry-run] [--lang all|en|ja|pt]
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── Localized copy (z176: 具体的価値ドリブン、Hevy/Strava スタイル) ──
COPY = {
    "en": {
        "bot_title": "📱 See your training as a heatmap",
        "bot_sub": "Map weak positions. Track technique mastery. Free forever.",
        "bot_btn": "Open BJJ App — Free →",
        "float_title": "📱 Track your roll",
        "float_sub": "Heatmap, skill map, streaks. Free.",
        "float_btn": "Open Free →",
    },
    "ja": {
        "bot_title": "📱 練習をヒートマップで可視化",
        "bot_sub": "弱点ポジションを見える化。技術習熟度をトラック。永久無料。",
        "bot_btn": "BJJ App を開く — 無料 →",
        "float_title": "📱 ロールを記録",
        "float_sub": "ヒートマップ・スキルマップ・連続記録。無料。",
        "float_btn": "無料で開く →",
    },
    "pt": {
        "bot_title": "📱 Veja seu treino como um mapa de calor",
        "bot_sub": "Mapeie posições fracas. Acompanhe domínio de técnicas. Grátis.",
        "bot_btn": "Abrir BJJ App — Grátis →",
        "float_title": "📱 Registre sua rola",
        "float_sub": "Mapa de calor, skill map, sequências. Grátis.",
        "float_btn": "Abrir Grátis →",
    },
}

# ── HTML templates (z176: top CTA 削除、bottom + float のみ) ──

def bottom_cta_html(c: dict, lang: str) -> str:
    return (
        f'<!-- z176-bottom-cta --><div class="z176-bottom-cta" '
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
    return f'''<!-- z176-float-cta --><div id="z176-float" style="position:fixed;bottom:20px;right:20px;max-width:280px;background:#0d2010;border:1px solid #2e7d32;border-radius:14px;padding:16px 18px;box-shadow:0 4px 20px rgba(0,200,83,.15);z-index:999;display:none;animation:slideUp .3s ease">
<button onclick="document.getElementById('z176-float').style.display='none';try{{localStorage.setItem('z176_float_dismissed',Date.now())}}catch(e){{}}" style="position:absolute;top:8px;right:12px;background:none;border:none;color:#546e7a;font-size:1rem;cursor:pointer;line-height:1" aria-label="Close">✕</button>
<div style="font-weight:700;color:#a5d6a7;margin-bottom:6px;font-size:.9rem">{c["float_title"]}</div>
<p style="font-size:.8rem;color:#c8e6c9;margin:0 0 12px">{c["float_sub"]}</p>
<a href="https://bjj-app.net/login?ref=wiki&page=float" style="display:block;background:#10B981;color:#fff;padding:8px 16px;border-radius:8px;text-decoration:none;font-weight:700;font-size:.85rem;text-align:center" onclick="window.gtag&&gtag('event','wiki_cta_click',{{position:'float',lang:'{lang}'}})">{c["float_btn"]}</a>
</div>
<style>@keyframes slideUp{{from{{transform:translateY(20px);opacity:0}}to{{transform:translateY(0);opacity:1}}}}</style>
<script>(function(){{
try{{
  var d=localStorage.getItem('z176_float_dismissed');
  if(d && (Date.now()-parseInt(d,10))<7*86400000) return;
}}catch(e){{}}
var el=document.getElementById('z176-float');
if(!el) return;
var shown=false;
function check(){{if(shown) return; var sp=(window.scrollY/(document.documentElement.scrollHeight-window.innerHeight))*100; if(sp>=30){{el.style.display='block';shown=true;window.removeEventListener('scroll',check);}}}}
window.addEventListener('scroll',check,{{passive:true}});
}})();</script>'''


# ── z175 rollback regex ────────────────────────────────────────────────────
# Remove z175-top-cta block and its old z175-bottom-cta / z175-float-cta.
# Replaced by z176 markers with new copy.
Z175_TOP_RE = re.compile(r'<!-- z175-top-cta -->.*?</div>(?=\s*<div class="difficulty-bar"|\s*<div class="meta"|\s*<p>|\s*\n)',
                          re.DOTALL)
Z175_BOTTOM_RE = re.compile(r'<!-- z175-bottom-cta -->.*?</div>\s*\n', re.DOTALL)
Z175_FLOAT_RE = re.compile(r'<!-- z175-float-cta -->.*?\}\)\(\);</script>\s*\n?', re.DOTALL)


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

    # ─── z176 rollback: remove z175 markers (Top/Bottom/Float) ────────
    # These had generic copy and excessive 4-CTA layout. Replaced by z176
    # 2-CTA design (Bottom + Float only) with concrete value props.
    if "z175-top-cta" in c:
        c2 = Z175_TOP_RE.sub("", c)
        if c2 != c:
            c = c2
            actions.append("rm_z175_top")
    if "z175-bottom-cta" in c:
        c2 = Z175_BOTTOM_RE.sub("", c)
        if c2 != c:
            c = c2
            actions.append("rm_z175_bottom")
    if "z175-float-cta" in c:
        c2 = Z175_FLOAT_RE.sub("", c)
        if c2 != c:
            c = c2
            actions.append("rm_z175_float")

    # ─── z176 inject: Bottom + Float only ─────────────────────────────
    # 1. Bottom CTA — insert before <footer>
    if "z176-bottom-cta" not in c:
        footer_matches = list(FOOTER_RE.finditer(c))
        if footer_matches:
            insert_at = footer_matches[-1].start()
            c = c[:insert_at] + bottom_cta_html(copy, lang) + "\n" + c[insert_at:]
            actions.append("bottom")

    # 2. Floating CTA — insert before </body>
    if "z176-float-cta" not in c:
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
