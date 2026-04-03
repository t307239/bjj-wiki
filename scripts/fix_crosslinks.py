#!/usr/bin/env python3
"""
fix_crosslinks.py — Wiki孤立ページ解消（クロスリンク自動注入）

処理内容:
  1. 全ページのキーワードインデックスを構築
  2. 各ページに対して関連度の高いページを5件選定
  3. Related Techniquesセクションに不足リンクを追加
  4. セクションがないページには新規作成

使い方:
    python3 scripts/fix_crosslinks.py --dry-run     # プレビュー
    python3 scripts/fix_crosslinks.py               # 実行
    python3 scripts/fix_crosslinks.py --lang en      # ENのみ

依存: Python 3.8+ 標準ライブラリのみ
"""

import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

WIKI_ROOT = Path(__file__).parent.parent
LANGUAGES = ["en", "ja"]
TARGET_LINKS = 5  # 各ページの目標Related links数


# ─────────────────────────────────────────────────────
# キーワード抽出
# ─────────────────────────────────────────────────────

# BJJのトピック分類キーワード
TOPIC_KEYWORDS = {
    "guard": ["guard", "ガード"],
    "mount": ["mount", "マウント"],
    "side_control": ["side-control", "side control", "サイドコントロール"],
    "back": ["back-control", "back control", "rear", "バックコントロール"],
    "half_guard": ["half-guard", "half guard", "ハーフガード"],
    "choke": ["choke", "strangle", "チョーク", "絞め"],
    "armlock": ["armbar", "arm-bar", "kimura", "americana", "omoplata", "アームバー", "キムラ", "アメリカーナ"],
    "leglock": ["heel-hook", "heel hook", "knee-bar", "knee bar", "toe-hold", "ankle-lock",
                "leg-lock", "leg lock", "ヒールフック", "ニーバー", "レッグロック"],
    "sweep": ["sweep", "スイープ"],
    "pass": ["pass", "passing", "パス", "パスガード"],
    "takedown": ["takedown", "take-down", "テイクダウン"],
    "escape": ["escape", "defense", "defence", "エスケープ", "ディフェンス"],
    "submission": ["submission", "サブミッション"],
    "position": ["position", "control", "ポジション"],
    "turtle": ["turtle", "タートル"],
    "inversion": ["inversion", "berimbolo", "インバージョン", "ベリンボロ"],
    "drill": ["drill", "training", "ドリル", "トレーニング"],
    "competition": ["competition", "comp", "tournament", "コンペ", "大会"],
    "athlete": ["athlete", "選手"],
    "beginner": ["beginner", "white-belt", "fundamental", "初心者", "基本"],
    "advanced": ["advanced", "black-belt", "上級"],
    "nogi": ["no-gi", "nogi", "ノーギ"],
    "grip": ["grip", "lapel", "collar", "sleeve", "グリップ"],
    "concept": ["concept", "strategy", "principle", "コンセプト", "戦略"],
}


def extract_keywords(filename: str, title: str) -> set:
    """ファイル名とタイトルからトピックキーワードを抽出"""
    topics = set()
    text = f"{filename.lower()} {title.lower()}"

    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                topics.add(topic)
                break

    return topics


def compute_relevance(topics_a: set, topics_b: set) -> float:
    """2ページ間のトピック関連度を計算"""
    if not topics_a or not topics_b:
        return 0.0
    intersection = topics_a & topics_b
    union = topics_a | topics_b
    return len(intersection) / len(union) if union else 0.0


def get_page_title(html: str, filename: str) -> str:
    """ページタイトルを取得"""
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    if h1:
        return re.sub(r'<[^>]+>', '', h1.group(1)).strip()
    title = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    if title:
        t = title.group(1).strip()
        t = re.sub(r'\s*[|–—]\s*BJJ\s*(Wiki|App).*$', '', t).strip()
        return t
    return filename.replace('.html', '').replace('-', ' ').title()


def get_existing_related_links(html: str) -> list:
    """Related Techniquesセクションの既存リンクを取得"""
    m = re.search(r'class="related-grid">(.*?)</div>', html, re.DOTALL)
    if m:
        return re.findall(r'href="([^"]+\.html)"', m.group(1))
    return []


def is_redirect(html: str) -> bool:
    return bool(re.search(r'Redirecting to|window\.location\.replace', html, re.IGNORECASE))


def is_pillar_page(filename: str) -> bool:
    """ピラーページ（インデックスページ）か判定"""
    pillar_names = {
        'techniques-az.html', 'index.html', 'about.html', 'privacy.html',
        'contact.html', 'sitemap.html',
    }
    return filename in pillar_names or filename.startswith('best-')


# ─────────────────────────────────────────────────────
# メイン処理
# ─────────────────────────────────────────────────────

def build_index(lang_dir: Path) -> dict:
    """全ページのインデックスを構築"""
    index = {}  # filename -> {title, topics, html, has_related, existing_links}

    for fpath in sorted(lang_dir.glob('*.html')):
        html = fpath.read_text(encoding='utf-8')
        if is_redirect(html):
            continue

        name = fpath.name
        title = get_page_title(html, name)
        topics = extract_keywords(name, title)
        existing_links = get_existing_related_links(html)
        has_related = 'related-section' in html or 'Related Techniques' in html

        index[name] = {
            'title': title,
            'topics': topics,
            'path': fpath,
            'has_related': has_related,
            'existing_links': [l.split('/')[-1] for l in existing_links],
        }

    return index


def find_related_pages(page: str, index: dict, max_results: int = TARGET_LINKS) -> list:
    """指定ページに関連するページを relevance 順で返す"""
    page_info = index[page]
    page_topics = page_info['topics']
    existing = set(page_info['existing_links'])

    candidates = []
    for other, info in index.items():
        if other == page or other in existing:
            continue
        if is_pillar_page(other):
            continue

        relevance = compute_relevance(page_topics, info['topics'])
        if relevance > 0:
            candidates.append((other, info['title'], relevance))

    # 関連度でソート、同点はタイトルでソート
    candidates.sort(key=lambda x: (-x[2], x[1]))

    # 既存リンク数を考慮して不足分だけ返す
    needed = max(0, max_results - len(existing))
    return candidates[:needed]


def inject_links_into_related(html: str, new_links: list, lang: str) -> str:
    """Related Techniquesセクションにリンクを追加"""
    # related-grid の中に追加
    m = re.search(r'(class="related-grid">)(.*?)(</div>)', html, re.DOTALL)
    if m:
        existing_content = m.group(2)
        new_link_html = ''
        for filename, title in new_links:
            # 重複チェック
            if filename in existing_content:
                continue
            new_link_html += f'\n<a href="{filename}">{title}</a>'

        if new_link_html:
            new_grid = m.group(1) + existing_content.rstrip() + new_link_html + '\n  ' + m.group(3)
            html = html[:m.start()] + new_grid + html[m.end():]
        return html

    return html


def create_related_section(html: str, links: list, lang: str) -> str:
    """Related Techniquesセクションを新規作成して挿入"""
    if not links:
        return html

    # セクション見出しの言語
    heading = "🥋 関連テクニック" if lang == "ja" else "🥋 Related Techniques"

    link_html = '\n'.join(f'<a href="{filename}">{title}</a>' for filename, title in links)

    section = f"""
<div class="related-section">
  <h3>{heading}</h3>
  <div class="related-grid">
{link_html}
  </div>
</div>
"""

    # 挿入位置: Share Bar の直前、またはフッターの直前
    insert_patterns = [
        r'(<!-- Share Bar -->)',
        r'(<!-- Footer -->)',
        r'(<footer)',
        r'(</main>)',
        r'(</body>)',
    ]
    for pattern in insert_patterns:
        m = re.search(pattern, html, re.IGNORECASE)
        if m:
            html = html[:m.start()] + section + '\n' + html[m.start():]
            return html

    # どのパターンにもマッチしない場合は</body>前
    body_end = html.rfind('</body>')
    if body_end > 0:
        html = html[:body_end] + section + '\n' + html[body_end:]

    return html


def process_lang(lang: str, dry_run: bool = False) -> dict:
    """1言語分を処理"""
    lang_dir = WIKI_ROOT / lang
    if not lang_dir.exists():
        return {"total": 0, "modified": 0, "links_added": 0}

    print(f"\n  [{lang.upper()}] インデックス構築中...")
    index = build_index(lang_dir)
    print(f"  [{lang.upper()}] {len(index)} ページをインデックス化")

    modified = 0
    links_added = 0
    pages_with_new_links = 0

    for page_name, page_info in sorted(index.items()):
        if is_pillar_page(page_name):
            continue

        related = find_related_pages(page_name, index)
        if not related:
            continue

        new_links = [(name, index[name]['title']) for name, _, _ in related]

        if dry_run:
            if new_links:
                pages_with_new_links += 1
                links_added += len(new_links)
            continue

        fpath = page_info['path']
        html = fpath.read_text(encoding='utf-8')

        if page_info['has_related']:
            new_html = inject_links_into_related(html, new_links, lang)
        else:
            new_html = create_related_section(html, new_links, lang)

        if new_html != html:
            fpath.write_text(new_html, encoding='utf-8')
            modified += 1
            links_added += len(new_links)

    if dry_run:
        modified = pages_with_new_links

    return {"total": len(index), "modified": modified, "links_added": links_added}


def main():
    parser = argparse.ArgumentParser(description="Fix Wiki Cross-links")
    parser.add_argument("--dry-run", action="store_true", help="変更を加えずにプレビューのみ")
    parser.add_argument("--lang", choices=["en", "ja", "pt"], help="特定言語のみ処理")
    args = parser.parse_args()

    langs = [args.lang] if args.lang else LANGUAGES

    print(f"\n{'='*60}")
    print(f"🔗 Cross-link Fix — {'DRY RUN' if args.dry_run else 'APPLYING'}")
    print(f"{'='*60}")

    total_modified = 0
    total_links = 0

    for lang in langs:
        result = process_lang(lang, args.dry_run)
        total_modified += result["modified"]
        total_links += result["links_added"]
        print(f"  [{lang.upper()}] {result['modified']} ページ修正、{result['links_added']} リンク追加")

    print(f"\n  合計: {total_modified} ページ修正、{total_links} リンク追加")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
