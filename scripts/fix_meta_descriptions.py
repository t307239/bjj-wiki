#!/usr/bin/env python3
"""
fix_meta_descriptions.py — meta descriptionの品質改善

処理内容:
  1. meta description 欠落 → 本文冒頭1-2文から自動生成
  2. meta description 短すぎ（< 50文字）→ 本文冒頭から補完
  3. meta description 長すぎ（> 160文字）→ 文境界でトリミング
  4. リダイレクトページはスキップ

使い方:
    python3 scripts/fix_meta_descriptions.py --dry-run     # プレビュー
    python3 scripts/fix_meta_descriptions.py               # 実行
    python3 scripts/fix_meta_descriptions.py --lang ja     # JA のみ

依存: Python 3.8+ 標準ライブラリのみ
"""

import os
import re
import sys
import argparse
from pathlib import Path

WIKI_ROOT = Path(__file__).parent.parent
LANGUAGES = ["en", "ja"]
TARGET_MIN = 50
TARGET_MAX = 155  # 160より少し短めに（安全マージン）


def extract_first_paragraph(html: str) -> str:
    """本文から最初の意味のあるパラグラフを抽出"""
    # script, style, nav, header, footer を除去
    clean = re.sub(r'<(script|style|nav|header|footer)[^>]*>.*?</\1>', '', html,
                   flags=re.DOTALL | re.IGNORECASE)
    # HTMLコメント除去
    clean = re.sub(r'<!--.*?-->', '', clean, flags=re.DOTALL)

    # pタグからテキスト抽出
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', clean, flags=re.DOTALL)
    for p in paragraphs:
        text = re.sub(r'<[^>]+>', '', p).strip()
        # HTMLエンティティ
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
        # 空白正規化
        text = re.sub(r'\s+', ' ', text).strip()
        # リダイレクトページやナビテキストはスキップ
        if 'Redirecting to' in text:
            return ""
        if len(text) > 30:
            return text
    return ""


def trim_to_length(text: str, max_len: int = 155) -> str:
    """文境界またはワード境界で指定長にトリミング"""
    if len(text) <= max_len:
        return text

    # 文境界（. ! ?）でカット
    truncated = text[:max_len]
    # 最後の文末を探す
    last_period = max(truncated.rfind('. '), truncated.rfind('。'),
                      truncated.rfind('! '), truncated.rfind('? '))
    if last_period > max_len * 0.5:  # 半分以上の位置に文末があればそこでカット
        return text[:last_period + 1].strip()

    # ワード境界でカット
    last_space = truncated.rfind(' ')
    if last_space > max_len * 0.6:
        return text[:last_space].strip() + '...'

    # 日本語の場合（スペースが少ない）
    return truncated.strip() + '...'


def extract_sentences(text: str, min_len: int = 50, max_len: int = 155) -> str:
    """テキストから適切な長さの冒頭文を抽出"""
    if not text:
        return ""

    # 文単位で分割（英語: ". " / 日本語: "。"）
    sentences = re.split(r'(?<=[.!?。！？])\s+', text)

    result = ""
    for sent in sentences:
        candidate = (result + " " + sent).strip() if result else sent
        if len(candidate) > max_len:
            if len(result) >= min_len:
                return trim_to_length(result, max_len)
            return trim_to_length(candidate, max_len)
        result = candidate
        if len(result) >= min_len:
            return result

    # 文が足りない場合はそのまま返す
    if result:
        return trim_to_length(result, max_len)
    return ""


def get_meta_description(html: str):
    """既存のmeta descriptionを取得（match objectを返す）"""
    m = re.search(
        r'(<meta\s+name=["\']description["\']\s+content=["\'])([^"\']*)(["\']\s*/?>)',
        html, re.IGNORECASE
    )
    if m:
        return m
    # content が先のパターン
    m = re.search(
        r'(<meta\s+content=["\'])([^"\']*)(["\']\s+name=["\']description["\']\s*/?>)',
        html, re.IGNORECASE
    )
    return m


def is_redirect_page(html: str) -> bool:
    """リダイレクトページか判定"""
    return bool(re.search(r'Redirecting to|window\.location\.replace|http-equiv=["\']refresh["\']',
                          html, re.IGNORECASE))


def get_page_title(html: str) -> str:
    """H1またはtitleからページタイトルを取得"""
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    if h1:
        return re.sub(r'<[^>]+>', '', h1.group(1)).strip()
    title = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    if title:
        t = title.group(1).strip()
        # " | BJJ Wiki" などのサフィックスを除去
        t = re.sub(r'\s*[|–—]\s*BJJ\s*(Wiki|App).*$', '', t).strip()
        return t
    return ""


def fix_file(filepath: Path, lang: str, dry_run: bool = False) -> dict:
    """1ファイルのmeta descriptionを修正"""
    result = {"file": str(filepath), "action": "skip", "old": "", "new": ""}

    html = filepath.read_text(encoding='utf-8')

    # リダイレクトページはスキップ
    if is_redirect_page(html):
        result["action"] = "redirect_skip"
        return result

    meta_match = get_meta_description(html)
    current_desc = meta_match.group(2).strip() if meta_match else ""
    result["old"] = current_desc

    # 改善が必要か判定
    needs_fix = False
    if not meta_match:
        needs_fix = True
    elif len(current_desc) < TARGET_MIN:
        needs_fix = True
    elif len(current_desc) > 160:
        needs_fix = True

    if not needs_fix:
        result["action"] = "ok"
        return result

    # 本文からdescription候補を抽出
    body_text = extract_first_paragraph(html)
    title = get_page_title(html)

    if len(current_desc) > 160:
        # 長すぎ → トリミング
        new_desc = trim_to_length(current_desc, TARGET_MAX)
        result["action"] = "trimmed"
    elif body_text:
        # 本文から抽出
        new_desc = extract_sentences(body_text, TARGET_MIN, TARGET_MAX)
        if not new_desc or len(new_desc) < 20:
            result["action"] = "no_good_text"
            return result
        result["action"] = "generated"
    else:
        result["action"] = "no_body_text"
        return result

    result["new"] = new_desc

    if dry_run:
        return result

    # HTMLに反映
    if meta_match:
        # 既存のmeta descriptionを置換
        new_html = html[:meta_match.start()] + \
                   meta_match.group(1) + new_desc + meta_match.group(3) + \
                   html[meta_match.end():]
    else:
        # meta descriptionが存在しない → headに追加
        head_end = re.search(r'</head>', html, re.IGNORECASE)
        if head_end:
            insert_tag = f'<meta name="description" content="{new_desc}">\n'
            new_html = html[:head_end.start()] + insert_tag + html[head_end.start():]
        else:
            result["action"] = "no_head_tag"
            return result

    filepath.write_text(new_html, encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description="Fix Wiki Meta Descriptions")
    parser.add_argument("--dry-run", action="store_true", help="変更を加えずにプレビューのみ")
    parser.add_argument("--lang", choices=["en", "ja", "pt"], help="特定言語のみ処理")
    args = parser.parse_args()

    langs = [args.lang] if args.lang else LANGUAGES

    stats = {"ok": 0, "generated": 0, "trimmed": 0, "redirect_skip": 0,
             "no_good_text": 0, "no_body_text": 0, "skip": 0, "no_head_tag": 0}
    changes = []

    for lang in langs:
        lang_dir = WIKI_ROOT / lang
        if not lang_dir.exists():
            continue

        for fpath in sorted(lang_dir.glob("*.html")):
            result = fix_file(fpath, lang, dry_run=args.dry_run)
            stats[result["action"]] = stats.get(result["action"], 0) + 1
            if result["action"] in ("generated", "trimmed"):
                changes.append(result)

    # レポート
    print(f"\n{'='*60}")
    print(f"📝 Meta Description Fix — {'DRY RUN' if args.dry_run else 'APPLIED'}")
    print(f"{'='*60}")
    print(f"  ✅ OK (変更不要):    {stats['ok']}")
    print(f"  📝 生成 (本文抽出):  {stats['generated']}")
    print(f"  ✂️  トリミング:      {stats['trimmed']}")
    print(f"  🔄 リダイレクト:    {stats['redirect_skip']}")
    print(f"  ⚠️  テキスト不足:    {stats['no_good_text'] + stats['no_body_text']}")
    print(f"  合計変更: {stats['generated'] + stats['trimmed']} 件")

    if changes:
        print(f"\n  変更内容サンプル（先頭10件）:")
        for c in changes[:10]:
            old_len = len(c['old'])
            new_len = len(c['new'])
            print(f"    {c['file'].split('/')[-1]}: [{c['action']}] {old_len}→{new_len} chars")
            if c['old']:
                print(f"      OLD: {c['old'][:60]}...")
            print(f"      NEW: {c['new'][:60]}...")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
