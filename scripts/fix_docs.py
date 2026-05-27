#!/usr/bin/env python3
"""fix_docs.py — docs/ ディレクトリの旧フォーマットページ修正"""

import os
import re

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs')

def get_lang(path):
    if '/ja/' in path: return 'ja'
    if '/pt/' in path: return 'pt'
    return 'en'

CTA = {
    'en': '''<div class="app-cta" style="background:linear-gradient(135deg,#0f172a,#1e1b4b);border:1px solid rgba(139,92,246,0.3);border-radius:12px;padding:20px;margin:28px 0;text-align:center">
  <p style="color:#a78bfa;font-size:.85rem;margin-bottom:12px">Track every technique in BJJ App — free forever</p>
  <a href="https://bjj-app.net/login" target="_blank" rel="noopener noreferrer" style="display:inline-block;padding:10px 24px;background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;border-radius:10px;text-decoration:none;font-weight:700;font-size:.9rem">Start Tracking Free →</a>
</div>''',
    'ja': '''<div class="app-cta" style="background:linear-gradient(135deg,#0f172a,#1e1b4b);border:1px solid rgba(139,92,246,0.3);border-radius:12px;padding:20px;margin:28px 0;text-align:center">
  <p style="color:#a78bfa;font-size:.85rem;margin-bottom:12px">テクニックを BJJ App で無料記録しよう</p>
  <a href="https://bjj-app.net/login" target="_blank" rel="noopener noreferrer" style="display:inline-block;padding:10px 24px;background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;border-radius:10px;text-decoration:none;font-weight:700;font-size:.9rem">無料で始める →</a>
</div>''',
    'pt': '''<div class="app-cta" style="background:linear-gradient(135deg,#0f172a,#1e1b4b);border:1px solid rgba(139,92,246,0.3);border-radius:12px;padding:20px;margin:28px 0;text-align:center">
  <p style="color:#a78bfa;font-size:.85rem;margin-bottom:12px">Registre cada técnica no BJJ App — gratuitamente</p>
  <a href="https://bjj-app.net/login" target="_blank" rel="noopener noreferrer" style="display:inline-block;padding:10px 24px;background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;border-radius:10px;text-decoration:none;font-weight:700;font-size:.9rem">Começar Gratuitamente →</a>
</div>''',
}

FLOAT_CTA = {
    'en': '''<div id="float-cta" style="display:none;position:fixed;bottom:20px;right:20px;z-index:9999;background:linear-gradient(135deg,#1e1b4b,#0f172a);border:1px solid rgba(139,92,246,0.4);border-radius:16px;padding:16px 20px;box-shadow:0 8px 32px rgba(0,0,0,0.5);max-width:280px">
  <p style="color:#a78bfa;font-size:.8rem;margin:0 0 10px">Train smarter with BJJ App</p>
  <a href="https://bjj-app.net/login" target="_blank" rel="noopener noreferrer" style="display:block;text-align:center;padding:8px 16px;background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;border-radius:8px;text-decoration:none;font-weight:700;font-size:.85rem">Start Free →</a>
  <button onclick="document.getElementById('float-cta').style.display='none'" style="position:absolute;top:8px;right:10px;background:none;border:none;color:#6b7280;cursor:pointer;font-size:16px;line-height:1">×</button>
</div>''',
    'ja': '''<div id="float-cta" style="display:none;position:fixed;bottom:20px;right:20px;z-index:9999;background:linear-gradient(135deg,#1e1b4b,#0f172a);border:1px solid rgba(139,92,246,0.4);border-radius:16px;padding:16px 20px;box-shadow:0 8px 32px rgba(0,0,0,0.5);max-width:280px">
  <p style="color:#a78bfa;font-size:.8rem;margin:0 0 10px">BJJ App でスマートに練習記録</p>
  <a href="https://bjj-app.net/login" target="_blank" rel="noopener noreferrer" style="display:block;text-align:center;padding:8px 16px;background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;border-radius:8px;text-decoration:none;font-weight:700;font-size:.85rem">無料で始める →</a>
  <button onclick="document.getElementById('float-cta').style.display='none'" style="position:absolute;top:8px;right:10px;background:none;border:none;color:#6b7280;cursor:pointer;font-size:16px;line-height:1">×</button>
</div>''',
    'pt': '''<div id="float-cta" style="display:none;position:fixed;bottom:20px;right:20px;z-index:9999;background:linear-gradient(135deg,#1e1b4b,#0f172a);border:1px solid rgba(139,92,246,0.4);border-radius:16px;padding:16px 20px;box-shadow:0 8px 32px rgba(0,0,0,0.5);max-width:280px">
  <p style="color:#a78bfa;font-size:.8rem;margin:0 0 10px">Treine melhor com BJJ App</p>
  <a href="https://bjj-app.net/login" target="_blank" rel="noopener noreferrer" style="display:block;text-align:center;padding:8px 16px;background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;border-radius:8px;text-decoration:none;font-weight:700;font-size:.85rem">Começar Grátis →</a>
  <button onclick="document.getElementById('float-cta').style.display='none'" style="position:absolute;top:8px;right:10px;background:none;border:none;color:#6b7280;cursor:pointer;font-size:16px;line-height:1">×</button>
</div>''',
}

def fix_file(path):
    lang = get_lang(path)
    content = open(path, encoding='utf-8').read()

    if 'bjj-app.net' in content:
        return False  # already has CTA

    # 1. Remove BJJ Weekly Digest / beehiiv-style empty div
    content = re.sub(
        r'<div[^>]*style=["\'][^"\']*background[^"\']*0d1b2a[^"\']*["\'][^>]*>.*?</div>',
        '', content, flags=re.DOTALL
    )
    # 2. Remove elite competitors fanatics remnant div
    content = re.sub(
        r'<div[^>]*>\s*<div[^>]*>World-class BJJ[^<]*</div>\s*</div>',
        '', content, flags=re.DOTALL
    )
    content = re.sub(
        r'<div[^>]*>\s*<div[^>]*>.*?elite competitors.*?</div>\s*</div>',
        '', content, flags=re.DOTALL
    )
    # 3. Remove broken float-cta script (references non-existent element)
    content = re.sub(
        r'<script>\s*setTimeout\(function\(\)\{\{document\.getElementById\(\'float-cta\'\).*?</script>',
        '', content, flags=re.DOTALL
    )
    # 4. Inject proper float-cta element and script before </body>
    float_div = FLOAT_CTA[lang]
    float_script = """<script>
setTimeout(function(){document.getElementById('float-cta').style.display='block'},30000);
window.addEventListener('scroll',function(){if(window.scrollY>window.innerHeight*.5)document.getElementById('float-cta').style.display='block'});
</script>"""
    content = content.replace('</body>', f'{float_div}\n{float_script}\n</body>')

    # 5. Inject inline CTA before </div> closing the main container
    #    Insert before the footer
    content = content.replace(
        '</div>\n\n<script>',
        f'{CTA[lang]}\n</div>\n\n<script>'
    )
    # Fallback: insert before </footer>
    if 'bjj-app.net' not in content:
        content = content.replace('</footer>', f'{CTA[lang]}\n</footer>', 1)

    open(path, 'w', encoding='utf-8').write(content)
    return True


def main():
    fixed = 0
    for root, dirs, files in os.walk(DOCS_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if not f.endswith('.html'): continue
            path = os.path.join(root, f)
            if fix_file(path):
                fixed += 1
    print(f'Fixed {fixed} docs/ pages')


if __name__ == '__main__':
    main()
