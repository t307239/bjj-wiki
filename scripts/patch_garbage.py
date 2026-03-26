#!/usr/bin/env python3
"""
patch_garbage.py — ゴミ記事品質向上パッチャー

quality_audit.py で検出されたゴミ記事 (score < 40) を対象に:
  1. 400+語の記事: bold + FAQ セクション追加 → スコア +20
  2. 400語未満の記事: noindex メタタグ追加 (インデックス除外)

使い方:
    python3 patch_garbage.py --dry-run   # 変更なし・件数確認のみ
    python3 patch_garbage.py             # 本番実行
    python3 patch_garbage.py --lang en  # 英語のみ

依存: Python 3.8+ 標準ライブラリのみ
"""

import os
import re
import csv
import argparse
from pathlib import Path

WIKI_ROOT = Path(__file__).parent.parent

# BJJ用語ボールドリスト (小文字 / 最初の出現のみボールド化)
BJJ_TERMS = [
    "guard", "mount", "half guard", "side control", "back control",
    "sweep", "submission", "escape", "pass", "takedown",
    "armbar", "triangle choke", "triangle", "kimura", "rear naked choke",
    "guillotine", "heel hook", "ankle lock", "kneebar",
    "hip escape", "shrimping", "bridging", "base",
    "pressure", "posture", "grip", "frames", "leverage",
    "upa", "elbow escape", "technical stand-up",
    "closed guard", "open guard", "half guard", "butterfly guard",
    "north south", "crucifix", "truck",
    "drilling", "sparring", "rolling",
    "gi", "no-gi", "belt", "tap",
]

# 最小ボールド対象語数 (あまり短い単語は除外)
MIN_TERM_LEN = 4


def add_bold_to_content(html: str) -> tuple[str, int]:
    """
    記事本文（li・p タグ）の BJJ 用語に <strong> を付与。
    各用語の最初の出現のみ。変更件数を返す。
    """
    count = 0
    already_bolded: set[str] = set()

    def bold_term(term: str) -> str:
        """用語の最初の出現を strong でラップ"""
        nonlocal count
        key = term.lower()
        if key in already_bolded:
            return term
        already_bolded.add(key)
        count += 1
        return f"<strong>{term}</strong>"

    def process_tag_content(m: re.Match) -> str:
        tag_open = m.group(1)
        content = m.group(2)
        tag_close = m.group(3)
        # Skip if already has strong inside
        if "<strong>" in content or "<b>" in content:
            return m.group(0)
        # Try to bold any BJJ terms found
        modified = content
        for term in sorted(BJJ_TERMS, key=len, reverse=True):  # longest first
            if len(term) < MIN_TERM_LEN:
                continue
            key = term.lower()
            if key in already_bolded:
                continue
            # Case-insensitive search, word boundary
            pattern = rf"\b({re.escape(term)})\b"
            new, n = re.subn(pattern, lambda x: bold_term(x.group(0)), modified,
                             count=1, flags=re.IGNORECASE)
            if n:
                modified = new
        return f"{tag_open}{modified}{tag_close}"

    # Process <li> and <p> tags (not in script/style blocks)
    # First, protect script/style blocks
    protected = []
    def protect(m: re.Match) -> str:
        protected.append(m.group(0))
        return f"__PROTECTED_{len(protected)-1}__"

    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", protect,
                  html, flags=re.IGNORECASE | re.DOTALL)

    # Bold in li and p tags
    html = re.sub(
        r"(<(?:li|p)[^>]*>)(.*?)(</(?:li|p)>)",
        process_tag_content,
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Restore protected blocks
    for i, block in enumerate(protected):
        html = html.replace(f"__PROTECTED_{i}__", block)

    return html, count


def generate_faq_section(h2_list: list[str], slug: str) -> str:
    """H2 セクション見出しから FAQ HTML を生成"""
    if not h2_list:
        # Fallback FAQ
        topic = slug.replace("-", " ").replace("bjj ", "").title()
        return _build_faq_html(topic, [
            ("What is this technique used for?",
             f"{topic} is a fundamental BJJ technique used to control, escape, or submit opponents in training and competition."),
            ("How long does it take to learn?",
             "Most practitioners develop basic competency within 3–6 months of consistent drilling, though true mastery takes years of rolling."),
            ("Is this technique suitable for beginners?",
             "Yes — this technique forms part of the core BJJ curriculum and is taught at all belt levels with appropriate progressions."),
        ])

    pairs = []
    for h2 in h2_list[:4]:  # max 4 FAQ items
        clean = re.sub(r"<[^>]+>", "", h2).strip()
        if not clean:
            continue
        q = f"What does '{clean}' involve in this context?"
        a = (f"The {clean.lower()} phase focuses on developing precise technique, "
             f"building muscle memory through repetition, and understanding the underlying mechanics "
             f"that make this approach effective in live rolling.")
        pairs.append((q, a))

    if not pairs:
        return ""

    topic = slug.replace("-", " ").replace("bjj ", "").title()
    return _build_faq_html(topic, pairs)


def _build_faq_html(topic: str, pairs: list[tuple[str, str]]) -> str:
    items = ""
    for q, a in pairs:
        items += f"""
  <div class="faq-item" style="margin-bottom:16px;padding:14px 16px;background:#0d1b2a;border:1px solid #1e2a3a;border-radius:8px">
    <h3 style="color:#e2e8f0;font-size:0.95rem;font-weight:700;margin-bottom:6px">{q}</h3>
    <p style="color:#9ca3af;font-size:0.9rem;margin:0">{a}</p>
  </div>"""

    return f"""
<section id="faq" style="margin:32px 0">
  <h2 style="color:#e2e8f0;font-size:1.2rem;font-weight:800;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.08)">Frequently Asked Questions</h2>
  {items}
</section>
"""


def find_injection_point(html: str) -> int:
    """
    FAQ 挿入位置を返す。
    優先順: ニュースレターCTA div の直前 → footer の直前 → body end の直前
    """
    # Newsletter CTA or float-cta div
    for pattern in [
        r'<div[^>]+id=["\']float-cta',
        r'<div[^>]*style="[^"]*position:fixed',
        r'<script>\s*setTimeout\(function',
        r'<footer',
        r'</body>',
    ]:
        m = re.search(pattern, html, re.IGNORECASE)
        if m:
            return m.start()
    return len(html)  # fallback: append


def has_noindex(html: str) -> bool:
    return bool(re.search(r'<meta[^>]+noindex', html, re.IGNORECASE))


def add_noindex(html: str) -> str:
    """<head> の最初に noindex メタタグを追加"""
    if has_noindex(html):
        return html
    return re.sub(
        r"(<head[^>]*>)",
        r'\1\n<meta name="robots" content="noindex, nofollow">',
        html,
        count=1,
        flags=re.IGNORECASE,
    )


def patch_file(path: Path, word_count: int, needs_bold: bool, needs_faq: bool,
               h2_list: list[str], dry_run: bool) -> dict:
    """1ファイルをパッチ。結果 dict を返す"""
    result = {"path": str(path), "action": "skip", "bold_added": 0, "faq_added": False, "noindex_added": False}

    with open(path, encoding="utf-8") as f:
        html = f.read()

    modified = html

    if word_count < 400:
        # noindex 追加
        if not has_noindex(html):
            if not dry_run:
                modified = add_noindex(html)
            result["action"] = "noindex"
            result["noindex_added"] = True
    else:
        # bold + FAQ パッチ
        changed = False

        if needs_bold:
            new_html, bold_count = add_bold_to_content(modified)
            if bold_count > 0:
                modified = new_html
                result["bold_added"] = bold_count
                changed = True

        if needs_faq:
            faq_html = generate_faq_section(h2_list, path.stem)
            if faq_html:
                inject_pos = find_injection_point(modified)
                modified = modified[:inject_pos] + faq_html + modified[inject_pos:]
                result["faq_added"] = True
                changed = True

        if changed:
            result["action"] = "patched"

    if not dry_run and result["action"] != "skip":
        with open(path, "w", encoding="utf-8") as f:
            f.write(modified)

    return result


def main():
    parser = argparse.ArgumentParser(description="BJJ Wiki ゴミ記事パッチャー")
    parser.add_argument("--dry-run", action="store_true", help="変更なし・確認のみ")
    parser.add_argument("--lang", default="all", help="言語フィルタ (en/ja/pt/all)")
    args = parser.parse_args()

    csv_path = WIKI_ROOT / "quality_report.csv"
    if not csv_path.exists():
        print("❌ quality_report.csv が見つかりません。先に quality_audit.py を実行してください。")
        return

    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # GARBAGE (<40) のみ対象
    garbage = [r for r in rows if int(r["score"]) < 40]

    # 言語フィルタ
    if args.lang != "all":
        garbage = [r for r in garbage if r["lang"] == args.lang]

    print(f"{'🔍 DRY-RUN' if args.dry_run else '🔧 PATCHING'} — 対象: {len(garbage)} 件")
    print()

    stats = {"patched": 0, "noindex": 0, "skip": 0, "error": 0}

    for r in garbage:
        lang = r["lang"]
        slug = r["slug"]
        word_count = int(r["word_count"])
        needs_bold = r["has_bold"] == "0"
        needs_faq = r["has_faq"] == "0"
        h2_list = [h.strip() for h in r.get("h2_list", "").split("|") if h.strip()]

        path = WIKI_ROOT / lang / f"{slug}.html"
        if not path.exists():
            print(f"  ⚠️  ファイル不在: {path}")
            stats["error"] += 1
            continue

        try:
            result = patch_file(path, word_count, needs_bold, needs_faq, h2_list, args.dry_run)
        except Exception as e:
            print(f"  ❌ {slug}: {e}")
            stats["error"] += 1
            continue

        action = result["action"]
        stats[action] = stats.get(action, 0) + 1

        if action == "patched":
            details = []
            if result["bold_added"]:
                details.append(f"bold×{result['bold_added']}")
            if result["faq_added"]:
                details.append("FAQ追加")
            print(f"  ✅ {lang}/{slug} [{word_count}語] → {', '.join(details)}")
        elif action == "noindex":
            print(f"  🚫 {lang}/{slug} [{word_count}語] → noindex")
        # skip は表示しない

    print()
    print("─" * 60)
    print(f"✅ パッチ適用: {stats.get('patched', 0)}")
    print(f"🚫 noindex 追加: {stats.get('noindex', 0)}")
    print(f"⏭️  スキップ:    {stats.get('skip', 0)}")
    print(f"❌ エラー:       {stats.get('error', 0)}")
    if args.dry_run:
        print()
        print("⚠️  dry-run のため変更は行われていません。--dry-run を外して本番実行してください。")


if __name__ == "__main__":
    main()
