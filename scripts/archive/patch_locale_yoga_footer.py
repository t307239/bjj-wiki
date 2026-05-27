#!/usr/bin/env python3
"""
Patch Wiki pages:
1. Comment out Yoga section (all languages)
2. Fix locale mixing in JA/PT pages (Related Techniques header, Privacy Policy, About)
3. Fix locale mixing in EN pages (お問い合わせ/Contact form)
4. Fix footer layout (wrap Comparisons/Tools in container)
5. Fix "関連動画 / Related Video" → locale-pure headers
6. Fix floating CTA locale for JA/PT
"""

import os
import re
import glob

WIKI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── i18n mappings ──
LOCALE_MAP = {
    "ja": {
        "related_techniques": "🥋 関連テクニック",
        "related_video": "関連動画",
        "privacy_policy": "プライバシーポリシー",
        "about": "概要",
        "contact_title": "📬 お問い合わせ",
        "contact_desc": "記事の誤り・追加情報・コラボ提案など、お気軽にどうぞ。",
        "name_placeholder": "お名前",
        "email_placeholder": "メールアドレス",
        "message_placeholder": "メッセージ",
        "send_button": "送信",
        "float_cta_title": "📱 BJJトレーニングを記録",
        "float_cta_desc": "練習記録・テクニック管理・ストリーク追跡。無料。",
        "float_cta_btn": "無料で始める →",
    },
    "en": {
        "related_techniques": "🥋 Related Techniques",
        "related_video": "Related Video",
        "privacy_policy": "Privacy Policy",
        "about": "About",
        "contact_title": "📬 Contact Us",
        "contact_desc": "Found an error? Have additional info or a collaboration idea? Let us know.",
        "name_placeholder": "Your Name",
        "email_placeholder": "Email Address",
        "message_placeholder": "Message",
        "send_button": "Send",
        "float_cta_title": "📱 Track Your BJJ Training",
        "float_cta_desc": "Log sessions &amp; techniques. Build your streak. Free.",
        "float_cta_btn": "Start Free →",
    },
    "pt": {
        "related_techniques": "🥋 Técnicas Relacionadas",
        "related_video": "Vídeo Relacionado",
        "privacy_policy": "Política de Privacidade",
        "about": "Sobre",
        "contact_title": "📬 Contato",
        "contact_desc": "Encontrou um erro? Tem informações adicionais ou uma ideia de colaboração? Entre em contato.",
        "name_placeholder": "Seu Nome",
        "email_placeholder": "E-mail",
        "message_placeholder": "Mensagem",
        "send_button": "Enviar",
        "float_cta_title": "📱 Registre Seu Treino de BJJ",
        "float_cta_desc": "Registre sessões e técnicas. Construa sua sequência. Grátis.",
        "float_cta_btn": "Comece Grátis →",
    },
}


def detect_lang(filepath: str) -> str:
    """Detect language from file path."""
    if "/ja/" in filepath:
        return "ja"
    elif "/pt/" in filepath:
        return "pt"
    else:
        return "en"


def patch_file(filepath: str) -> bool:
    """Patch a single HTML file. Returns True if modified."""
    lang = detect_lang(filepath)
    loc = LOCALE_MAP[lang]

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # ── 1. Comment out Yoga section ──
    # Match the yoga style + yoga-box div block
    yoga_pattern = r'(<style>\s*\.yoga-box\{.*?</style>\s*<div class="yoga-box">.*?</div>\s*</div>)'
    content = re.sub(yoga_pattern, r'<!-- YOGA SECTION HIDDEN\n\1\nYOGA SECTION HIDDEN -->', content, flags=re.DOTALL)

    # ── 2. Fix "Related Techniques" header ──
    content = re.sub(
        r'<h3>🥋 Related Techniques</h3>',
        f'<h3>{loc["related_techniques"]}</h3>',
        content
    )

    # ── 3. Fix "関連動画 / Related Video" → locale-pure ──
    content = re.sub(
        r'関連動画 / Related Video',
        loc["related_video"],
        content
    )

    # ── 4. Fix Contact Form ──
    # Title
    content = re.sub(
        r'📬 お問い合わせ / Contact',
        loc["contact_title"],
        content
    )
    # Description
    content = re.sub(
        r'記事の誤り・追加情報・コラボ提案など、お気軽にどうぞ。',
        loc["contact_desc"],
        content
    )
    # Placeholders
    content = re.sub(
        r'placeholder="お名前 / Name"',
        f'placeholder="{loc["name_placeholder"]}"',
        content
    )
    content = re.sub(
        r'placeholder="メールアドレス / Email"',
        f'placeholder="{loc["email_placeholder"]}"',
        content
    )
    content = re.sub(
        r'placeholder="メッセージ / Message"',
        f'placeholder="{loc["message_placeholder"]}"',
        content
    )
    # Send button
    content = re.sub(
        r'>\s*送信 / Send\s*<',
        f'>\n      {loc["send_button"]}\n    <',
        content
    )

    # ── 5. Fix Privacy Policy & About links in footer ──
    content = re.sub(
        r'>Privacy Policy</a>',
        f'>{loc["privacy_policy"]}</a>',
        content
    )
    content = re.sub(
        r'>About</a>',
        f'>{loc["about"]}</a>',
        content
    )

    # ── 6. Fix floating CTA locale ──
    content = re.sub(
        r'📱 Track Your BJJ Training',
        loc["float_cta_title"],
        content
    )
    content = re.sub(
        r'Log sessions &(?:amp;)? techniques\. Build your streak\. Free\.',
        loc["float_cta_desc"],
        content
    )
    content = re.sub(
        r'>Start Free →</a>',
        f'>{loc["float_cta_btn"]}</a>',
        content
    )

    # ── 7. Fix footer layout: wrap Comparisons/Tools in a proper container ──
    # The issue: after <!-- Share Bar -->, there's a stray </div> that causes
    # Comparisons/Tools to fall outside the main container.
    # Fix: wrap them in a div with padding
    footer_broken = re.compile(
        r'<!-- Share Bar -->\s*</div>\s*(<div>\s*<div style="font-size:\.75rem;font-weight:700;color:#546e7a)',
        re.DOTALL
    )
    content = footer_broken.sub(
        r'<!-- Share Bar -->\n  </div>\n  <div style="max-width:860px;margin:32px auto 0;padding:0 20px;display:flex;gap:40px;flex-wrap:wrap">\n  \1',
        content
    )

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    modified = 0
    total = 0

    for lang_dir in ["ja", "en", "pt"]:
        pattern = os.path.join(WIKI_ROOT, lang_dir, "*.html")
        files = glob.glob(pattern)
        for fp in files:
            total += 1
            if patch_file(fp):
                modified += 1

    print(f"✅ Patched {modified}/{total} files")


if __name__ == "__main__":
    main()
