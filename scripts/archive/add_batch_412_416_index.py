#!/usr/bin/env python3
"""Add Batch 412-416 cards to index.html (en/ja/pt)."""
import os, re

WIKI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cards per language
CARDS = {
    "en": [
        {
            "href": "bjj-open-guard-mastery.html",
            "emoji": "🌐",
            "title": "Open Guard Mastery",
            "desc": "Complete open guard system: grips, sweeps & submissions"
        },
        {
            "href": "bjj-pressure-passing-advanced.html",
            "emoji": "🔥",
            "title": "Advanced Pressure Passing",
            "desc": "Smash, stack & torreando pass strategies for advanced grapplers"
        },
        {
            "href": "bjj-mount-control-details.html",
            "emoji": "🏔️",
            "title": "Mount Control Details",
            "desc": "Detailed mechanics of high mount, S-mount & submission setups"
        },
        {
            "href": "bjj-double-guard-pull.html",
            "emoji": "🤝",
            "title": "Double Guard Pull Tactics",
            "desc": "Strategy, timing & guard pull rules in competition BJJ"
        },
        {
            "href": "bjj-bottom-game-mastery.html",
            "emoji": "⬇️",
            "title": "Bottom Game Mastery",
            "desc": "Complete defensive & offensive system from the bottom position"
        },
    ],
    "ja": [
        {
            "href": "bjj-open-guard-mastery.html",
            "emoji": "🌐",
            "title": "オープンガード完全習得",
            "desc": "グリップ・スウィープ・サブミッション完全システム"
        },
        {
            "href": "bjj-pressure-passing-advanced.html",
            "emoji": "🔥",
            "title": "アドバンストプレッシャーパス",
            "desc": "上級者向けスマッシュ・スタック・トレランドパス戦略"
        },
        {
            "href": "bjj-mount-control-details.html",
            "emoji": "🏔️",
            "title": "マウントコントロール詳細",
            "desc": "ハイマウント・Sマウント・サブミッション設定の詳細メカニクス"
        },
        {
            "href": "bjj-double-guard-pull.html",
            "emoji": "🤝",
            "title": "ダブルガードプル戦術",
            "desc": "試合でのガードプル戦略・タイミング・ルール理解"
        },
        {
            "href": "bjj-bottom-game-mastery.html",
            "emoji": "⬇️",
            "title": "ボトムゲーム完全習得",
            "desc": "ボトムポジションからの防御・攻撃完全システム"
        },
    ],
    "pt": [
        {
            "href": "bjj-open-guard-mastery.html",
            "emoji": "🌐",
            "title": "Domínio da Guarda Aberta",
            "desc": "Sistema completo: pegadas, rasteiras e finalizações"
        },
        {
            "href": "bjj-pressure-passing-advanced.html",
            "emoji": "🔥",
            "title": "Passagem por Pressão Avançada",
            "desc": "Estratégias avançadas de smash pass, stack e torreando"
        },
        {
            "href": "bjj-mount-control-details.html",
            "emoji": "🏔️",
            "title": "Detalhes do Controle na Montada",
            "desc": "Mecânicas detalhadas do high mount, S-mount e finalizações"
        },
        {
            "href": "bjj-double-guard-pull.html",
            "emoji": "🤝",
            "title": "Táticas de Double Guard Pull",
            "desc": "Estratégia, timing e regras do guard pull em competição"
        },
        {
            "href": "bjj-bottom-game-mastery.html",
            "emoji": "⬇️",
            "title": "Domínio do Jogo de Baixo",
            "desc": "Sistema completo defensivo e ofensivo da posição inferior"
        },
    ],
}

CARD_STYLE = 'style="display:block;background:#111827;border:1px solid #1e2a3a;border-radius:10px;padding:16px;text-decoration:none;transition:border-color .2s" onmouseover="this.style.borderColor=\'#e2b714\'" onmouseout="this.style.borderColor=\'#1e2a3a\'"'

def make_card(card):
    return (
        f'<a href="{card["href"]}" {CARD_STYLE}>'
        f'<strong style="color:#e2b714">{card["emoji"]} {card["title"]}</strong>'
        f'<p style="color:#aaa;font-size:.85rem;margin-top:4px">{card["desc"]}</p>'
        f'</a>'
    )

def add_cards_to_index(lang, cards):
    filepath = os.path.join(WIKI_DIR, lang, "index.html")
    if not os.path.exists(filepath):
        print(f"  ⚠️  Not found: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if already added
    if cards[0]["href"] in content and cards[-1]["href"] in content:
        print(f"  ⏭️  {lang}/index.html — already has cards, skipping")
        return

    new_cards_html = "".join(make_card(c) for c in cards)

    # Find the guide-new section's closing </div></section> to insert before it
    # Pattern: last </div> before </section> in the guide-new section
    # We'll find the guide-new section and append cards just before its closing </div>
    # The section ends with </div>\n</section> or </div></section>

    # Find guide-new section
    guide_new_match = re.search(r'<section id="guide-new".*?</section>', content, re.DOTALL)
    if not guide_new_match:
        print(f"  ⚠️  guide-new section not found in {lang}/index.html")
        return

    section_start = guide_new_match.start()
    section_end = guide_new_match.end()
    section_content = guide_new_match.group(0)

    # Find the last </div> before </section>
    # Insert new cards before the closing </div></section>
    insert_pos_in_section = section_content.rfind('</div>')
    if insert_pos_in_section == -1:
        print(f"  ⚠️  Could not find closing </div> in guide-new section of {lang}/index.html")
        return

    new_section_content = (
        section_content[:insert_pos_in_section]
        + new_cards_html
        + section_content[insert_pos_in_section:]
    )

    new_content = content[:section_start] + new_section_content + content[section_end:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  ✅ {lang}/index.html — added {len(cards)} cards")


for lang, cards in CARDS.items():
    add_cards_to_index(lang, cards)

print("\nDone.")
