#!/usr/bin/env python3
"""
fix_wiki4.py — 第4パス Wiki クリーンアップ
対象:
  1. docs/ ディレクトリ（これまで未処理）の beehiiv + fanatics 除去
  2. en/ja/pt に残存する fanatics <a> タグと孤立した div ラッパーを除去
  3. docs/ の beehiiv iframe/link → BJJ App login CTA 置換
"""

import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── CTA templates ────────────────────────────────────────────────────────────

CTA_EN = '''<div class="app-cta" style="background:linear-gradient(135deg,#0f172a,#1e1b4b);border:1px solid rgba(139,92,246,0.3);border-radius:12px;padding:20px;margin:28px 0;text-align:center">
  <p style="color:#a78bfa;font-size:.85rem;margin-bottom:12px">Track every technique, every roll — for free</p>
  <a href="https://bjj-app.net/login" target="_blank" rel="noopener" style="display:inline-block;padding:10px 24px;background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;border-radius:10px;text-decoration:none;font-weight:700;font-size:.9rem">
    Start Tracking Free →
  </a>
</div>'''

CTA_JA = '''<div class="app-cta" style="background:linear-gradient(135deg,#0f172a,#1e1b4b);border:1px solid rgba(139,92,246,0.3);border-radius:12px;padding:20px;margin:28px 0;text-align:center">
  <p style="color:#a78bfa;font-size:.85rem;margin-bottom:12px">テクニックと練習を無料で記録しよう</p>
  <a href="https://bjj-app.net/login" target="_blank" rel="noopener" style="display:inline-block;padding:10px 24px;background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;border-radius:10px;text-decoration:none;font-weight:700;font-size:.9rem">
    無料で始める →
  </a>
</div>'''

CTA_PT = '''<div class="app-cta" style="background:linear-gradient(135deg,#0f172a,#1e1b4b);border:1px solid rgba(139,92,246,0.3);border-radius:12px;padding:20px;margin:28px 0;text-align:center">
  <p style="color:#a78bfa;font-size:.85rem;margin-bottom:12px">Registre cada técnica e treino — gratuitamente</p>
  <a href="https://bjj-app.net/login" target="_blank" rel="noopener" style="display:inline-block;padding:10px 24px;background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;border-radius:10px;text-decoration:none;font-weight:700;font-size:.9rem">
    Começar Gratuitamente →
  </a>
</div>'''

def get_cta(filepath):
    """Infer language from path."""
    if '/ja/' in filepath:
        return CTA_JA
    if '/pt/' in filepath:
        return CTA_PT
    return CTA_EN


def fix_html(content, filepath):
    original = content

    # 1. Remove beehiiv iframes (entire iframe tag)
    content = re.sub(
        r'<iframe[^>]*beehiiv[^>]*>.*?</iframe>',
        '', content, flags=re.DOTALL | re.IGNORECASE
    )
    content = re.sub(
        r'<iframe[^>]*bjjwiki\.beehiiv[^>]*/?>',
        '', content, flags=re.DOTALL | re.IGNORECASE
    )

    # 2. Remove beehiiv subscribe links <a href="https://bjjwiki.beehiiv.com/...">...</a>
    content = re.sub(
        r'<a[^>]*href=["\']https?://bjjwiki\.beehiiv\.com[^"\']*["\'][^>]*>.*?</a>',
        '', content, flags=re.DOTALL | re.IGNORECASE
    )

    # 3. Replace beehiiv-wrap containers (already have inner content or empty)
    #    If the container still has a beehiiv iframe/link inside, convert to app CTA
    #    If already converted (has bjj-app.net), leave it
    def replace_beehiiv_wrap(m):
        block = m.group()
        if 'bjj-app.net' in block:
            return block  # already fixed
        return get_cta(filepath)

    content = re.sub(
        r'<div[^>]*class=["\'][^"\']*beehiiv-wrap[^"\']*["\'][^>]*>.*?</div>\s*</div>',
        replace_beehiiv_wrap, content, flags=re.DOTALL | re.IGNORECASE
    )

    # 4. Remove standalone beehiiv divs left over
    content = re.sub(
        r'<div[^>]*class=["\'][^"\']*beehiiv[^"\']*["\'][^>]*>\s*</div>',
        '', content, flags=re.DOTALL | re.IGNORECASE
    )

    # 5. Remove BJJ Fanatics aff-box divs (with various attributes)
    content = re.sub(
        r'<div[^>]*class=["\'][^"\']*aff-box[^"\']*["\'][^>]*>.*?</div>',
        '', content, flags=re.DOTALL | re.IGNORECASE
    )

    # 6. Remove standalone fanatics <a> tags (not inside aff-box — those were caught above)
    content = re.sub(
        r'<a[^>]*href=["\']https?://bjjfanatics\.com[^"\']*["\'][^>]*>.*?</a>',
        '', content, flags=re.DOTALL | re.IGNORECASE
    )

    # 7. Remove BJJ Fanatics comment markers
    content = re.sub(
        r'<!--\s*BJJ Fanatics[^>]*-->',
        '', content, flags=re.IGNORECASE
    )

    # 8. Remove empty div wrappers left after fanatics removal
    content = re.sub(r'<div[^>]*>\s*</div>', '', content)
    content = re.sub(r'<div[^>]*>\s*</div>', '', content)  # second pass for nested

    return content


def main():
    fixed = 0
    skipped = 0

    for root, dirs, files in os.walk(BASE):
        # Skip non-content directories
        dirs[:] = [d for d in dirs if d not in [
            '.git', 'node_modules', 'scripts', 'cache', 'logs',
            'e2e', 'reports', 'test-results', 'playwright-report', 'supabase', 'sns'
        ]]

        for filename in files:
            if not filename.endswith('.html'):
                continue
            path = os.path.join(root, filename)

            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                skipped += 1
                continue

            # Only process if there's something to fix
            has_beehiiv = 'beehiiv.com' in content
            has_fanatics = 'bjjfanatics.com' in content.lower() or 'Browse BJJ Fanatics' in content

            if not has_beehiiv and not has_fanatics:
                continue

            new_content = fix_html(content, path)

            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                fixed += 1

    print(f"Fixed: {fixed} files | Skipped: {skipped}")


if __name__ == '__main__':
    main()
