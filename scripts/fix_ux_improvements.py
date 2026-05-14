#!/usr/bin/env python3
"""
fix_ux_improvements.py
Bulk-patches all existing BJJ Wiki HTML pages (en/ja/pt) with UX improvements:
  W1 - Back-to-top button (CSS + HTML + JS)
  W2 - Reading progress bar (CSS + HTML + JS)
  W3 - Auto Table of Contents (JS)
  W4 - Font-size 16px + line-height 1.8 in body rule

Usage:
  cd ~/Claude/bjj-wiki
  python3 scripts/fix_ux_improvements.py
"""

import os
import re
from pathlib import Path

# Repository root (one level up from scripts/)
REPO_ROOT = Path(__file__).parent.parent

LANGUAGES = ["en", "ja", "pt"]

# ── CSS to inject (before </style>) ──────────────────────────────────────────
NEW_CSS = """  /* Reading progress bar */
  #read-progress{position:fixed;top:0;left:0;width:0%;height:3px;background:var(--accent);z-index:9999;transition:width .1s linear}
  /* Back to top */
  #back-to-top{position:fixed;bottom:24px;right:20px;background:var(--accent);color:#fff;border:none;border-radius:50%;width:42px;height:42px;font-size:1.3rem;cursor:pointer;display:none;align-items:center;justify-content:center;z-index:999;opacity:.85;box-shadow:0 2px 8px rgba(0,0,0,.5);transition:opacity .2s}
  #back-to-top:hover{opacity:1}
  /* Auto TOC */
  .toc{background:#0d0d1a;border:1px solid var(--border);border-radius:10px;padding:16px 20px;margin:20px 0 28px;display:none}
  .toc-title{font-size:.78rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px}
  .toc-list{list-style:none;padding:0;margin:0}
  .toc-list li{margin:4px 0}
  .toc-list a{color:var(--accent);font-size:.88rem;text-decoration:none}
  .toc-list a:hover{text-decoration:underline}"""

# ── JS + HTML to inject (before </body>) ─────────────────────────────────────
INJECT_BEFORE_BODY_CLOSE = """  <button id="back-to-top" aria-label="Back to top" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑</button>
  <script>
  (function(){
    var prog=document.getElementById('read-progress');
    var btn=document.getElementById('back-to-top');
    window.addEventListener('scroll',function(){
      var scrolled=window.scrollY;
      var total=document.body.scrollHeight-window.innerHeight;
      if(total>0){prog.style.width=(scrolled/total*100)+'%';}
      if(scrolled>300){btn.style.display='flex';}else{btn.style.display='none';}
    },{passive:true});
    var headings=document.querySelectorAll('h2');
    if(headings.length>=3){
      var tocEl=document.getElementById('toc');
      var listEl=document.getElementById('toc-list');
      if(tocEl&&listEl){
        headings.forEach(function(h,i){
          var id='section-'+i;
          if(!h.id)h.id=id;
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
  </script>
"""

# TOC HTML div placeholder (inserted after intro <p>, before first <h2>)
def make_toc_html(lang):
    labels = {"en": "Contents", "ja": "目次", "pt": "Conteúdo"}
    label = labels.get(lang, "Contents")
    return (
        f'  <div id="toc" class="toc">\n'
        f'    <div class="toc-title">{label}</div>\n'
        f'    <ul class="toc-list" id="toc-list"></ul>\n'
        f'  </div>\n'
    )


def detect_lang(filepath: Path) -> str:
    """Detect language from directory name."""
    parts = filepath.parts
    for lang in LANGUAGES:
        if lang in parts:
            return lang
    return "en"


def patch_file(filepath: Path) -> bool:
    """Apply UX patches to a single HTML file. Returns True if modified."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            content = filepath.read_text(encoding="latin-1")
        except Exception:
            return False

    original = content
    lang = detect_lang(filepath)

    # ── W4: Fix body font-size + line-height ──────────────────────────────
    # Match body rule and ensure font-size:16px and line-height:1.8 are present
    def fix_body_rule(m):
        rule = m.group(0)
        if "font-size" not in rule:
            rule = rule.replace("font-family:", "font-size:16px;font-family:")
        if "line-height:1.7" in rule:
            rule = rule.replace("line-height:1.7", "line-height:1.8")
        elif "line-height" not in rule:
            rule = rule.replace("padding:", "line-height:1.8;padding:")
        return rule

    content = re.sub(r'body\{[^}]+\}', fix_body_rule, content)

    # ── W1+W2: Add CSS before </style> (first occurrence only) ───────────
    if "read-progress" not in content:
        # inject before first </style>
        content = content.replace("</style>", NEW_CSS + "\n</style>", 1)

    # ── W2: Add progress bar div right after <body> ───────────────────────
    if 'id="read-progress"' not in content:
        content = content.replace("<body>\n", '<body>\n<div id="read-progress"></div>\n', 1)

    # ── W3: Add TOC placeholder after intro paragraph ─────────────────────
    if 'id="toc"' not in content:
        toc_html = make_toc_html(lang)
        # Insert before the first <h2> that's inside the article
        content = re.sub(r'(<h2[^>]*>)', toc_html + r'\1', content, count=1)

    # ── W1: Inject back-to-top button + JS before </body> ─────────────────
    if "back-to-top" not in content:
        content = content.replace("</body>", INJECT_BEFORE_BODY_CLOSE + "</body>", 1)

    if content == original:
        return False  # no changes

    filepath.write_text(content, encoding="utf-8")
    return True


def main():
    total = 0
    patched = 0
    skipped = 0
    errors = 0

    for lang in LANGUAGES:
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            print(f"  [SKIP] {lang}/ directory not found")
            continue

        html_files = sorted(lang_dir.glob("*.html"))
        print(f"\nProcessing {lang}/ — {len(html_files)} HTML files...")

        for fpath in html_files:
            total += 1
            try:
                changed = patch_file(fpath)
                if changed:
                    patched += 1
                else:
                    skipped += 1
            except Exception as e:
                errors += 1
                print(f"  [ERROR] {fpath.name}: {e}")

        print(f"  Done {lang}/")

    print(f"\n{'='*50}")
    print(f"Total files : {total}")
    print(f"Patched     : {patched}")
    print(f"Already OK  : {skipped}")
    print(f"Errors      : {errors}")
    print(f"{'='*50}")
    print("\n✅ UX improvements applied to all existing pages.")
    print("   - W1: Back-to-top button added")
    print("   - W2: Reading progress bar added")
    print("   - W3: Auto TOC added (shows when 3+ h2 sections present)")
    print("   - W4: font-size:16px + line-height:1.8 applied to body")


if __name__ == "__main__":
    main()
