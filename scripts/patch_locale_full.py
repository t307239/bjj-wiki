#!/usr/bin/env python3
"""
patch_locale_full.py — 全ページに対するlocale純粋性 + ヨガコメントアウト完全パッチ

前回のpatch_locale_yoga_footer.pyで漏れたファイルを含め、
全4,698ページを確実にパッチする。

パッチ内容:
  1. JA: 英語テキスト→日本語に置換
  2. PT: 英語テキスト→ポルトガル語に置換
  3. EN: 日本語混入テキスト→英語に置換（コンタクトフォーム等）
  4. 全言語: ヨガセクションのコメントアウト
  5. 全言語: ©年号を2026に更新
"""

import os
import re
import sys
from pathlib import Path

WIKI_ROOT = Path(__file__).parent.parent

# ── 言語別置換マップ ─────────────────────────
REPLACEMENTS = {
    "ja": [
        # Related Techniques header
        (r'<h3>🥋\s*Related\s+Techniques</h3>', '<h3>🥋 関連テクニック</h3>'),
        (r'<h3>\s*🥋\s*Related\s+Techniques\s*</h3>', '<h3>🥋 関連テクニック</h3>'),
        (r'>Related Techniques<', '>関連テクニック<'),
        # Related Video header
        (r'>関連動画\s*/\s*Related\s*Video<', '>関連動画<'),
        (r'>Related Video<', '>関連動画<'),
        # Contact form
        (r'お問い合わせ\s*/\s*Contact', 'お問い合わせ'),
        (r'>Contact Us<', '>お問い合わせ<'),
        (r'>Send<', '>送信<'),
        (r'placeholder="Your Name"', 'placeholder="お名前"'),
        (r'placeholder="Your Email"', 'placeholder="メールアドレス"'),
        (r'placeholder="Your Message"', 'placeholder="メッセージ"'),
        (r'placeholder="Your name"', 'placeholder="お名前"'),
        (r'placeholder="Your email"', 'placeholder="メールアドレス"'),
        (r'placeholder="Your message"', 'placeholder="メッセージ"'),
        # Footer links
        (r'>Privacy Policy<', '>プライバシーポリシー<'),
        (r'>About<(?!/)', '>概要<'),
        # Floating CTA
        (r'>Track Your BJJ Training<', '>柔術トレーニングを記録しよう<'),
        (r'Track Your BJJ Training', '柔術トレーニングを記録しよう'),
        # Copyright
        (r'&copy;\s*2025', '&copy; 2026'),
        (r'&copy;\s*2024', '&copy; 2026'),
    ],
    "en": [
        # Contact form (remove Japanese)
        (r'お問い合わせ\s*/\s*Contact', 'Contact Us'),
        (r'送信\s*/\s*Send', 'Send'),
        (r'お名前\s*/\s*Name', 'Your Name'),
        (r'メールアドレス\s*/\s*Email', 'Your Email'),
        (r'メッセージ\s*/\s*Message', 'Your Message'),
        # Related Video
        (r'>関連動画\s*/\s*Related\s*Video<', '>Related Video<'),
        # Pillar page CTA (Japanese → English)
        (r'>練習記録アプリ<', '>BJJ Training Log<'),
        (r'>BJJ練習記録アプリ<', '>BJJ Training Log App<'),
        (r'練習回数・テクニック・連続記録を一元管理。無料で始められます。', 'Track sessions, techniques, and streaks. Free forever.'),
        (r'>無料で始める →<', '>Start Free →<'),
        (r'>無料で始める<', '>Start Free<'),
        (r'>練習を記録しよう<', '>Log Your Training<'),
        (r'練習ログ・テクニック帳・目標トラッカー', 'Training log, technique journal, goal tracker'),
        (r'>トラッキングアプリ<', '>Tracking App<'),
        (r'>ホーム<', '>Home<'),
        # Copyright
        (r'&copy;\s*2025', '&copy; 2026'),
        (r'&copy;\s*2024', '&copy; 2026'),
    ],
    "pt": [
        # Related Techniques header
        (r'<h3>🥋\s*Related\s+Techniques</h3>', '<h3>🥋 Técnicas Relacionadas</h3>'),
        (r'<h3>\s*🥋\s*Related\s+Techniques\s*</h3>', '<h3>🥋 Técnicas Relacionadas</h3>'),
        (r'>Related Techniques<', '>Técnicas Relacionadas<'),
        # Related Video header
        (r'>関連動画\s*/\s*Related\s*Video<', '>Vídeo Relacionado<'),
        (r'>Related Video<', '>Vídeo Relacionado<'),
        # Contact form
        (r'お問い合わせ\s*/\s*Contact', 'Contato'),
        (r'>Contact Us<', '>Contato<'),
        (r'>Send<', '>Enviar<'),
        (r'placeholder="Your Name"', 'placeholder="Seu Nome"'),
        (r'placeholder="Your Email"', 'placeholder="Seu Email"'),
        (r'placeholder="Your Message"', 'placeholder="Sua Mensagem"'),
        (r'placeholder="Your name"', 'placeholder="Seu Nome"'),
        (r'placeholder="Your email"', 'placeholder="Seu Email"'),
        (r'placeholder="Your message"', 'placeholder="Sua Mensagem"'),
        # Footer links
        (r'>Privacy Policy<', '>Política de Privacidade<'),
        (r'>About<(?!/)', '>Sobre<'),
        # Floating CTA
        (r'>Track Your BJJ Training<', '>Acompanhe Seu Treino de BJJ<'),
        (r'Track Your BJJ Training', 'Acompanhe Seu Treino de BJJ'),
        # Copyright
        (r'&copy;\s*2025', '&copy; 2026'),
        (r'&copy;\s*2024', '&copy; 2026'),
        # Remove Japanese from PT pages
        (r'お問い合わせ', 'Contato'),
        (r'>送信<', '>Enviar<'),
    ],
}


def comment_out_yoga(html: str) -> str:
    """ヨガセクションをコメントアウト（まだされていない場合）"""
    if "YOGA SECTION HIDDEN" in html:
        return html  # 既にコメントアウト済み

    # yoga-box のstyleとdiv をコメントアウト
    # Pattern 1: <style>.yoga-box{...}</style> + <div class="yoga-box">...</div>
    pattern = re.compile(
        r'(\s*<style>\.yoga-box\{[^<]*</style>\s*'
        r'<div class="yoga-box">.*?</div>)',
        re.DOTALL,
    )
    match = pattern.search(html)
    if match:
        original = match.group(0)
        replacement = f"\n  <!-- YOGA SECTION HIDDEN\n{original}\nYOGA SECTION HIDDEN -->"
        html = html.replace(original, replacement)
    else:
        # Pattern 2: just the div
        pattern2 = re.compile(
            r'(\s*<div class="yoga-box">.*?</div>)',
            re.DOTALL,
        )
        match2 = pattern2.search(html)
        if match2:
            original = match2.group(0)
            replacement = f"\n  <!-- YOGA SECTION HIDDEN\n{original}\nYOGA SECTION HIDDEN -->"
            html = html.replace(original, replacement)

    return html


def patch_file(filepath: Path, lang: str) -> bool:
    """単一ファイルをパッチ。変更があればTrue返す"""
    try:
        original = filepath.read_text(encoding="utf-8")
    except Exception:
        return False

    html = original

    # 言語別テキスト置換
    for pattern, replacement in REPLACEMENTS.get(lang, []):
        html = re.sub(pattern, replacement, html)

    # ヨガコメントアウト
    html = comment_out_yoga(html)

    if html != original:
        filepath.write_text(html, encoding="utf-8")
        return True
    return False


def main():
    total = 0
    changed = 0

    for lang in ["en", "ja", "pt"]:
        lang_dir = WIKI_ROOT / lang
        if not lang_dir.exists():
            continue

        files = sorted(lang_dir.glob("*.html"))
        lang_changed = 0
        for f in files:
            total += 1
            if patch_file(f, lang):
                changed += 1
                lang_changed += 1

        print(f"  {lang}: {lang_changed}/{len(files)} ファイル修正")

    print(f"\n合計: {changed}/{total} ファイル修正")


if __name__ == "__main__":
    main()
