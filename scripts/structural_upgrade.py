#!/usr/bin/env python3
"""
structural_upgrade.py — Wiki全テクニックページに不足構造要素を注入

既存コンテンツを一切変更せず、以下の「chrome」を不足ページに追加:
 1. Reading progress bar (<body>直後)
 2. Back-to-top button (</body>直前)
 3. CTA banner (footer直前)
 4. Share bar (footer直前)
 5. Beehiiv newsletter CTA (footer直前)
 6. Progress/Back-to-top/TOC JavaScript (</body>直前)

安全設計:
 - 既に存在する要素は二重注入しない
 - リダイレクトページはスキップ
 - athlete-* / index.html / about.html はスキップ
"""

import re
import os
import sys
import glob
from pathlib import Path

WIKI_ROOT = Path(__file__).resolve().parent.parent
LANG_DIRS = ["en", "ja", "pt"]

SKIP_FILES = {"index.html", "about.html", "athletes.html", "privacy.html", "terms.html"}

# ── Injection fragments ──

PROGRESS_BAR = '<div id="read-progress" class="progress-bar"></div>'

BACK_TO_TOP = '<button id="back-to-top" class="back-to-top" aria-label="Back to top" onclick="window.scrollTo({top:0,behavior:\'smooth\'})">↑</button>'

# Language-aware CTA / Share / Beehiiv
CTA_TEMPLATES = {
    "en": {
        "cta_banner": '<div class="cta-banner"><a href="https://bjj-app.net/login">🥋 Track your BJJ training for free — Try BJJ App →</a></div>',
        "share_bar": '''<div class="share-bar">
<span style="color:var(--muted);font-size:.85rem">Share:</span>
<a href="https://twitter.com/intent/tweet?url={url}&text={title}" target="_blank" rel="noopener">𝕏 Post</a>
<a href="https://www.reddit.com/submit?url={url}&title={title}" target="_blank" rel="noopener">Reddit</a>
</div>''',
        "beehiiv": '''<div class="beehiiv-wrap"><h3>📬 Free BJJ Newsletter</h3>
<p>Get the free BJJ White Belt Guide plus technique breakdowns, training tips &amp; exclusive content every week. No spam. Unsubscribe anytime.</p>
<a class="beehiiv-btn" href="https://bjj-wiki.beehiiv.com/subscribe" target="_blank" rel="noopener">Get Free Access →</a></div>''',
    },
    "ja": {
        "cta_banner": '<div class="cta-banner"><a href="https://bjj-app.net/login">🥋 BJJ練習を無料で記録しよう — BJJ Appを試す →</a></div>',
        "share_bar": '''<div class="share-bar">
<span style="color:var(--muted);font-size:.85rem">共有:</span>
<a href="https://twitter.com/intent/tweet?url={url}&text={title}" target="_blank" rel="noopener">𝕏 ポスト</a>
<a href="https://www.reddit.com/submit?url={url}&title={title}" target="_blank" rel="noopener">Reddit</a>
</div>''',
        "beehiiv": '''<div class="beehiiv-wrap"><h3>📬 BJJ 無料ニュースレター</h3>
<p>無料BJJ白帯ガイド＋毎週の技術解説・練習のコツ・独占コンテンツ。スパムなし。いつでも配信停止可能。</p>
<a class="beehiiv-btn" href="https://bjj-wiki.beehiiv.com/subscribe" target="_blank" rel="noopener">無料アクセスを取得 →</a></div>''',
    },
    "pt": {
        "cta_banner": '<div class="cta-banner"><a href="https://bjj-app.net/login">🥋 Registre seu treino de BJJ grátis — Experimente o BJJ App →</a></div>',
        "share_bar": '''<div class="share-bar">
<span style="color:var(--muted);font-size:.85rem">Compartilhar:</span>
<a href="https://twitter.com/intent/tweet?url={url}&text={title}" target="_blank" rel="noopener">𝕏 Post</a>
<a href="https://www.reddit.com/submit?url={url}&title={title}" target="_blank" rel="noopener">Reddit</a>
</div>''',
        "beehiiv": '''<div class="beehiiv-wrap"><h3>📬 Newsletter BJJ Grátis</h3>
<p>Receba o Guia Gratuito do Brás Branco + análises de técnicas semanais, dicas de treino e conteúdo exclusivo. Sem spam. Desinscrever a qualquer momento.</p>
<a class="beehiiv-btn" href="https://bjj-wiki.beehiiv.com/subscribe" target="_blank" rel="noopener">Obter Acesso Gratuito →</a></div>''',
    },
}

UPGRADE_JS = """<script>
(function(){
  // Reading progress bar
  var prog=document.getElementById('read-progress');
  // Back to top
  var btn=document.getElementById('back-to-top');
  if(prog||btn){
    window.addEventListener('scroll',function(){
      var scrolled=window.scrollY;
      var total=document.body.scrollHeight-window.innerHeight;
      if(total>0&&prog){prog.style.width=(scrolled/total*100)+'%';}
      if(btn){btn.style.display=scrolled>300?'flex':'none';}
    },{passive:true});
  }
  // Auto TOC from h2 elements
  var headings=document.querySelectorAll('h2');
  if(headings.length>=3){
    var tocEl=document.getElementById('toc');
    var listEl=document.getElementById('toc-list');
    if(tocEl&&listEl){
      headings.forEach(function(h,i){
        var id='section-'+i;
        h.id=id;
        var li=document.createElement('li');
        var a=document.createElement('a');
        a.href='#'+id;
        a.textContent=h.textContent;
        li.appendChild(a);
        listEl.appendChild(li);
      });
      tocEl.style.display='block';
    }
  }
})();
</script>"""

# Stats
stats = {
    "processed": 0,
    "skipped_redirect": 0,
    "skipped_already_complete": 0,
    "progress_added": 0,
    "back_to_top_added": 0,
    "cta_added": 0,
    "share_added": 0,
    "beehiiv_added": 0,
    "js_added": 0,
    "errors": [],
}


def detect_lang(filepath: str) -> str:
    """Detect language from directory path."""
    parts = Path(filepath).parts
    for lang in LANG_DIRS:
        if lang in parts:
            return lang
    return "en"


def extract_page_info(content: str, filepath: str) -> dict:
    """Extract title and URL for share links."""
    title_match = re.search(r"<title>(.*?)</title>", content)
    title = title_match.group(1) if title_match else ""
    slug = Path(filepath).stem
    lang = detect_lang(filepath)
    url = f"https://wiki.bjj-app.net/{lang}/{slug}.html"
    return {"title": title, "url": url, "slug": slug, "lang": lang}


def upgrade_page(filepath: str) -> bool:
    """Upgrade a single page. Returns True if modified."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip redirects
    if "http-equiv" in content and "refresh" in content:
        stats["skipped_redirect"] += 1
        return False

    original = content
    info = extract_page_info(content, filepath)
    lang = info["lang"]
    templates = CTA_TEMPLATES.get(lang, CTA_TEMPLATES["en"])

    injections_before_footer = []

    # 1. Progress bar — inject after <body...>
    if "read-progress" not in content and "progress-bar" not in content:
        content = re.sub(
            r"(<body[^>]*>)",
            r"\1\n" + PROGRESS_BAR,
            content,
            count=1,
            flags=re.IGNORECASE,
        )
        stats["progress_added"] += 1

    # 2. CTA banner
    if "cta-banner" not in content and "cta-box" not in content:
        injections_before_footer.append(templates["cta_banner"])
        stats["cta_added"] += 1

    # 3. Share bar
    if "share-bar" not in content and "share-btn" not in content:
        share_html = templates["share_bar"].format(
            url=info["url"], title=info["title"].replace('"', "&quot;")
        )
        injections_before_footer.append(share_html)
        stats["share_added"] += 1

    # 4. Beehiiv
    if "beehiiv" not in content:
        injections_before_footer.append(templates["beehiiv"])
        stats["beehiiv_added"] += 1

    # Inject accumulated elements before footer
    if injections_before_footer:
        injection_block = "\n".join(injections_before_footer)
        # Try to inject before <footer
        if re.search(r"<footer", content, re.IGNORECASE):
            content = re.sub(
                r"(<footer)",
                injection_block + r"\n\1",
                content,
                count=1,
                flags=re.IGNORECASE,
            )
        else:
            # No footer found — inject before </body>
            content = re.sub(
                r"(</body>)",
                injection_block + r"\n\1",
                content,
                count=1,
                flags=re.IGNORECASE,
            )

    # 5. Back-to-top button
    if "back-to-top" not in content:
        content = re.sub(
            r"(</body>)",
            BACK_TO_TOP + r"\n\1",
            content,
            count=1,
            flags=re.IGNORECASE,
        )
        stats["back_to_top_added"] += 1

    # 6. Upgrade JS (progress + back-to-top + TOC)
    # Only add if we don't already have the combined script
    if "read-progress" in content and "section-" not in content:
        # Has progress bar but no TOC JS — inject the combined script
        content = re.sub(
            r"(</body>)",
            UPGRADE_JS + r"\n\1",
            content,
            count=1,
            flags=re.IGNORECASE,
        )
        stats["js_added"] += 1

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    else:
        stats["skipped_already_complete"] += 1
        return False


def main():
    dry_run = "--dry-run" in sys.argv

    for lang in LANG_DIRS:
        lang_dir = WIKI_ROOT / lang
        if not lang_dir.is_dir():
            continue

        html_files = sorted(lang_dir.glob("*.html"))
        for filepath in html_files:
            basename = filepath.name
            # Skip non-technique pages
            if basename in SKIP_FILES or basename.startswith("athlete-"):
                continue

            try:
                if not dry_run:
                    modified = upgrade_page(str(filepath))
                    if modified:
                        stats["processed"] += 1
                else:
                    with open(filepath, "r", encoding="utf-8") as f:
                        c = f.read()
                    needs_work = (
                        "beehiiv" not in c
                        or "share-bar" not in c
                        or "cta-banner" not in c
                        or "back-to-top" not in c
                    )
                    if needs_work:
                        stats["processed"] += 1
            except Exception as e:
                stats["errors"].append(f"{filepath}: {e}")

    mode = "DRY RUN" if dry_run else "UPGRADED"
    print(f"\n{'='*55}")
    print(f"  Wiki Structural Upgrade — {mode}")
    print(f"{'='*55}")
    print(f"  Files modified:        {stats['processed']}")
    print(f"  Skipped (redirect):    {stats['skipped_redirect']}")
    print(f"  Skipped (complete):    {stats['skipped_already_complete']}")
    print(f"  Progress bars added:   {stats['progress_added']}")
    print(f"  Back-to-top added:     {stats['back_to_top_added']}")
    print(f"  CTA banners added:     {stats['cta_added']}")
    print(f"  Share bars added:      {stats['share_added']}")
    print(f"  Beehiiv CTAs added:    {stats['beehiiv_added']}")
    print(f"  JS bundles added:      {stats['js_added']}")
    if stats["errors"]:
        print(f"\n  ⚠️ Errors ({len(stats['errors'])}):")
        for err in stats["errors"][:10]:
            print(f"    {err}")
    print()


if __name__ == "__main__":
    main()
