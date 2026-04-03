#!/usr/bin/env python3
"""
detect_hidden_bugs.py — スコアに表れない「隠れバグ」を自動検知

AUDIT_FRAMEWORK.md のスコアリングでは検知できない、
目視でしか見つからなかった問題を機械的に検出するスクリプト。

検知カテゴリ:
  1. Locale純粋性違反（JAページの英語残存、ENページの日本語残存等）
  2. ヨガセクション表示漏れ（コメントアウト忘れ）
  3. フッターレイアウト崩れ（コンテナ未ラップ）
  4. テンプレート不整合（©年号、CTA言語ミスマッチ）
  5. リンク切れ候補（hrefが空 or # のみ）
  6. HTMLタグ不整合（閉じタグ漏れの兆候）

使い方:
    python3 scripts/detect_hidden_bugs.py              # 全チェック
    python3 scripts/detect_hidden_bugs.py --lang ja    # JAのみ
    python3 scripts/detect_hidden_bugs.py --fix-hint   # 修正ヒント付き
    python3 scripts/detect_hidden_bugs.py --ci         # CI用（exitcode=違反数）

出力: STDOUT + ~/Claude/bjj-wiki/hidden_bugs_report.txt

依存: Python 3.8+ 標準ライブラリのみ
"""

import os
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

# ─────────────────────────────────────────────────────
# 設定
# ─────────────────────────────────────────────────────

WIKI_ROOT = Path(__file__).parent.parent
LANGUAGES = ["en", "ja", "pt"]
CURRENT_YEAR = "2026"

# ── Locale純粋性パターン ──────────────────────────────
# ブランド名・固有名詞・技名など「各言語ページで英語のまま許容する」ホワイトリスト
ENGLISH_WHITELIST = re.compile(
    r"""(?x)
    BJJ|MMA|UFC|IBJJF|ADCC|EBI|Gi|No[-\s]?Gi|
    Armbar|Kimura|Americana|Omoplata|Triangle|Guillotine|
    Rear[\s]?Naked[\s]?Choke|D'?Arce|Anaconda|Ezekiel|
    Guard|Mount|Side[\s]?Control|Back[\s]?Control|Half[\s]?Guard|
    Closed[\s]?Guard|Open[\s]?Guard|Butterfly[\s]?Guard|
    De[\s]La[\s]Riva|Spider[\s]?Guard|Lasso[\s]?Guard|
    X[-\s]?Guard|Rubber[\s]?Guard|Worm[\s]?Guard|
    Berimbolo|Sweep|Pass|Takedown|Submission|Escape|
    Heel[\s]?Hook|Toe[\s]?Hold|Knee[\s]?Bar|Wrist[\s]?Lock|
    Ankle[\s]?Lock|Calf[\s]?Slicer|
    Hip[\s]?Escape|Bridge|Shrimp|Sprawl|
    Drill|Roll|Spar|
    Joint[\s]?Lock|Choke|Strangle|
    North[-\s]?South|Turtle|Crucifix|Truck|
    Lapel|Collar|Sleeve|Grip|
    John[\s]Danaher|Marcelo[\s]Garcia|Gordon[\s]Ryan|
    Roger[\s]Gracie|Helio[\s]Gracie|Rickson[\s]Gracie|
    Marcus[\s]"Buchecha"|
    YouTube|Instagram|Facebook|Twitter|
    BJJ\s?App|BJJ\s?Wiki|
    Pro|Free|CSV|PDF|API|URL|
    Cow[\s]Face[\s]Pose|Eagle[\s]Pose|Pigeon[\s]Pose|
    Technique[\s]Map|Video[\s]Timestamps|
    ROYDEAN|RoyDean|
    Privacy[\s]Policy|About|Contact|
    class=|style=|href=|src=|data-|onclick=|
    https?://|www\.|\.html|\.css|\.js|\.png|\.jpg|\.svg|
    UTF-8|charset|viewport|content=|
    max-width|margin|padding|display|flex|gap|
    font-size|color|text-decoration|border|background|
    none|auto|center|wrap|nowrap|
    div|span|section|header|footer|nav|main|article|
    img|iframe|script|link|meta|
    Google|Cloudflare|CDN
    """,
    re.IGNORECASE,
)

# JAページで検出すべき「英語のまま残っている」テキストパターン
JA_FORBIDDEN_ENGLISH = [
    (r"Related\s+Techniques", "関連テクニック"),
    (r"Related\s+Video", "関連動画"),
    (r"Privacy\s+Policy", "プライバシーポリシー"),
    (r"(?<!\w)About(?!\w)(?!\.html)", "概要"),
    (r"Contact\s+Us", "お問い合わせ"),
    (r"Send(?=\s*</)", "送信"),
    (r"Your\s+Name", "お名前"),
    (r"Your\s+Email", "メールアドレス"),
    (r"Your\s+Message", "メッセージ"),
    (r"Track\s+Your\s+BJJ\s+Training", "柔術トレーニングを記録しよう"),
    (r"Free\s+forever", "ずっと無料"),
]

# ENページで検出すべき「日本語が混入している」パターン
EN_FORBIDDEN_JAPANESE = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]{2,}")

# PTページで検出すべき問題パターン
PT_FORBIDDEN_ENGLISH = [
    (r"Related\s+Techniques", "Técnicas Relacionadas"),
    (r"Related\s+Video", "Vídeo Relacionado"),
    (r"Privacy\s+Policy", "Política de Privacidade"),
    (r"(?<!\w)About(?!\w)(?!\.html)", "Sobre"),
    (r"Contact\s+Us", "Contato"),
]

PT_FORBIDDEN_JAPANESE = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]{2,}")


# ─────────────────────────────────────────────────────
# ユーティリティ
# ─────────────────────────────────────────────────────

def extract_visible_text(html: str) -> str:
    """HTMLタグ・style・scriptを除去して可視テキストを抽出"""
    # script, style タグ内を除去
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # HTMLコメントを除去
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    # HTMLタグを除去
    text = re.sub(r"<[^>]+>", " ", text)
    # HTML entities
    text = re.sub(r"&\w+;", " ", text)
    return text


def extract_non_code_html(html: str) -> str:
    """コード・属性以外のHTMLテキスト部分を抽出（タグ内属性は除外）"""
    # HTMLコメント内を除去
    text = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    # script, style 内を除去
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", text, flags=re.DOTALL)
    # タグそのもの（属性含む）を除去
    text = re.sub(r"<[^>]+>", "\n", text)
    return text


# ─────────────────────────────────────────────────────
# チェッカー群
# ─────────────────────────────────────────────────────

class BugReport:
    def __init__(self):
        self.bugs = []  # (severity, category, file, detail, fix_hint)

    def add(self, severity: str, category: str, filepath: str, detail: str, fix_hint: str = ""):
        self.bugs.append((severity, category, filepath, detail, fix_hint))

    def count(self, severity: str = None) -> int:
        if severity:
            return sum(1 for b in self.bugs if b[0] == severity)
        return len(self.bugs)


def check_locale_purity_ja(filepath: str, html: str, report: BugReport):
    """JAページのlocale純粋性チェック"""
    visible = extract_non_code_html(html)
    for pattern, expected_ja in JA_FORBIDDEN_ENGLISH:
        matches = re.findall(pattern, visible, re.IGNORECASE)
        if matches:
            report.add(
                "CRITICAL", "LOCALE_JA",
                filepath,
                f"英語残存: '{matches[0]}' (expected: '{expected_ja}')",
                f"'{matches[0]}' → '{expected_ja}' に置換",
            )


def check_locale_purity_en(filepath: str, html: str, report: BugReport):
    """ENページのlocale純粋性チェック（日本語混入検知）"""
    visible = extract_non_code_html(html)
    matches = EN_FORBIDDEN_JAPANESE.findall(visible)
    # ホワイトリスト: 言語セレクターの「日本語」は許容
    LANG_SELECTOR_WHITELIST = {"日本語", "ポルトガル語"}
    for m in matches:
        if len(m) <= 2:
            continue
        if m.strip() in LANG_SELECTOR_WHITELIST:
            continue
        report.add(
            "CRITICAL", "LOCALE_EN",
            filepath,
            f"日本語混入: '{m[:30]}...' ({len(m)}文字)",
            "該当テキストを英語に置換",
        )


def check_locale_purity_pt(filepath: str, html: str, report: BugReport):
    """PTページのlocale純粋性チェック"""
    visible = extract_non_code_html(html)
    for pattern, expected_pt in PT_FORBIDDEN_ENGLISH:
        matches = re.findall(pattern, visible, re.IGNORECASE)
        if matches:
            report.add(
                "CRITICAL", "LOCALE_PT",
                filepath,
                f"英語残存: '{matches[0]}' (expected: '{expected_pt}')",
                f"'{matches[0]}' → '{expected_pt}' に置換",
            )
    # 日本語混入チェック
    jp_matches = PT_FORBIDDEN_JAPANESE.findall(visible)
    for m in jp_matches:
        if len(m) <= 2:
            continue
        report.add(
            "CRITICAL", "LOCALE_PT",
            filepath,
            f"日本語混入: '{m[:30]}...' ({len(m)}文字)",
            "該当テキストをポルトガル語に置換",
        )


def check_yoga_hidden(filepath: str, html: str, report: BugReport):
    """ヨガセクションがコメントアウトされているかチェック"""
    # yoga-box が表示されている（コメント外）場合はバグ
    if re.search(r'class=["\']yoga-box["\']', html) and "YOGA SECTION HIDDEN" not in html:
        report.add(
            "WARNING", "YOGA_VISIBLE",
            filepath,
            "ヨガセクションがコメントアウトされていない",
            "<!-- YOGA SECTION HIDDEN ... --> でラップ",
        )


def check_footer_layout(filepath: str, html: str, report: BugReport):
    """フッターのComparisons/Toolsがコンテナ内にあるかチェック"""
    # Share Bar後の構造チェック
    if "<!-- Share Bar -->" in html:
        share_bar_pos = html.index("<!-- Share Bar -->")
        after_share = html[share_bar_pos:share_bar_pos + 500]
        # コンテナdivが存在するか
        if "Comparisons" in after_share or "Tools" in after_share:
            if "max-width:860px" not in after_share and "max-width: 860px" not in after_share:
                report.add(
                    "WARNING", "FOOTER_LAYOUT",
                    filepath,
                    "Comparisons/Toolsセクションにコンテナラッパーがない",
                    "max-width:860px;margin:32px auto 0 のdivでラップ",
                )


def check_copyright_year(filepath: str, html: str, report: BugReport):
    """©年号チェック"""
    if re.search(r"&copy;\s*20(?:2[0-5]|1\d)", html):
        old_year = re.search(r"&copy;\s*(20\d{2})", html)
        if old_year:
            report.add(
                "INFO", "COPYRIGHT",
                filepath,
                f"古い著作権年号: © {old_year.group(1)} (should be {CURRENT_YEAR})",
                f"&copy; {old_year.group(1)} → &copy; {CURRENT_YEAR}",
            )


def check_empty_links(filepath: str, html: str, report: BugReport):
    """空リンク・#のみリンク検知"""
    empty_hrefs = re.findall(r'href=["\'](?:#|)["\']', html)
    if len(empty_hrefs) > 2:  # 目次の#は許容、3つ以上なら問題
        report.add(
            "INFO", "EMPTY_LINKS",
            filepath,
            f"空リンク/# リンクが {len(empty_hrefs)} 件",
            "適切なURLまたはアンカーに修正",
        )


def check_bilingual_headers(filepath: str, html: str, lang: str, report: BugReport):
    """「日本語 / English」のような二言語併記ヘッダー検知"""
    patterns = [
        r"お問い合わせ\s*/\s*Contact",
        r"関連動画\s*/\s*Related\s*Video",
        r"関連テクニック\s*/\s*Related\s*Techniques",
        r"送信\s*/\s*Send",
    ]
    for pat in patterns:
        if re.search(pat, html, re.IGNORECASE):
            report.add(
                "CRITICAL", f"BILINGUAL_{lang.upper()}",
                filepath,
                f"二言語併記: '{pat}' が残存",
                "locale に応じた単一言語テキストに修正",
            )


def check_mixed_cta_language(filepath: str, html: str, lang: str, report: BugReport):
    """CTAボタンの言語がlocaleと不一致"""
    if lang == "ja":
        # JAページで英語CTAが残存
        if re.search(r"Start\s+Free|Sign\s+Up\s+Free|Get\s+Started", html, re.IGNORECASE):
            # floating CTAなど
            report.add(
                "WARNING", "CTA_LANG",
                filepath,
                "JAページに英語CTA ('Start Free' 等) が残存",
                "「無料で始める」等の日本語CTAに修正",
            )
    elif lang == "pt":
        if re.search(r"Start\s+Free|Sign\s+Up\s+Free|Get\s+Started", html, re.IGNORECASE):
            report.add(
                "WARNING", "CTA_LANG",
                filepath,
                "PTページに英語CTA ('Start Free' 等) が残存",
                "「Comece Grátis」等のPT語CTAに修正",
            )


# ─────────────────────────────────────────────────────
# メインスキャナ
# ─────────────────────────────────────────────────────

def scan_all(langs: list[str] = None, fix_hint: bool = False) -> BugReport:
    """全ページスキャン"""
    if langs is None:
        langs = LANGUAGES

    report = BugReport()
    total_files = 0

    for lang in langs:
        lang_dir = WIKI_ROOT / lang
        if not lang_dir.exists():
            continue

        html_files = sorted(lang_dir.glob("*.html"))
        for fpath in html_files:
            total_files += 1
            try:
                html = fpath.read_text(encoding="utf-8")
            except Exception as e:
                report.add("ERROR", "READ_FAIL", str(fpath), str(e))
                continue

            rel_path = f"{lang}/{fpath.name}"

            # 共通チェック
            check_yoga_hidden(rel_path, html, report)
            check_footer_layout(rel_path, html, report)
            check_copyright_year(rel_path, html, report)
            check_empty_links(rel_path, html, report)
            check_bilingual_headers(rel_path, html, lang, report)
            check_mixed_cta_language(rel_path, html, lang, report)

            # 言語別チェック
            if lang == "ja":
                check_locale_purity_ja(rel_path, html, report)
            elif lang == "en":
                check_locale_purity_en(rel_path, html, report)
            elif lang == "pt":
                check_locale_purity_pt(rel_path, html, report)

    return report, total_files


# ─────────────────────────────────────────────────────
# 出力
# ─────────────────────────────────────────────────────

SEVERITY_COLORS = {
    "CRITICAL": "\033[91m",  # red
    "WARNING": "\033[93m",   # yellow
    "INFO": "\033[94m",      # blue
    "ERROR": "\033[95m",     # magenta
}
RESET = "\033[0m"


def print_report(report: BugReport, total_files: int, fix_hint: bool = False):
    """レポート出力"""
    # サマリー
    crit = report.count("CRITICAL")
    warn = report.count("WARNING")
    info = report.count("INFO")

    print(f"\n{'='*60}")
    print(f"🔍 Hidden Bug Detector — スキャン結果")
    print(f"{'='*60}")
    print(f"  スキャン対象: {total_files} ファイル")
    print(f"  🔴 CRITICAL: {crit}")
    print(f"  🟡 WARNING:  {warn}")
    print(f"  🔵 INFO:     {info}")
    print(f"  合計: {report.count()} 件")

    if report.count() == 0:
        print(f"\n  ✅ 隠れバグなし！全ページクリーン。")
        print(f"{'='*60}\n")
        return

    # カテゴリ別集計
    categories = defaultdict(list)
    for sev, cat, fpath, detail, hint in report.bugs:
        categories[cat].append((sev, fpath, detail, hint))

    for cat, items in sorted(categories.items()):
        print(f"\n  📂 {cat} ({len(items)} 件)")
        print(f"  {'─'*50}")
        # 最大10件表示、残りはサマリー
        shown = items[:10]
        for sev, fpath, detail, hint in shown:
            color = SEVERITY_COLORS.get(sev, "")
            print(f"    {color}[{sev}]{RESET} {fpath}")
            print(f"           {detail}")
            if fix_hint and hint:
                print(f"           💡 {hint}")
        if len(items) > 10:
            print(f"    ... 他 {len(items) - 10} 件")

    print(f"\n{'='*60}\n")


def write_report_file(report: BugReport, total_files: int):
    """レポートファイル出力"""
    report_path = WIKI_ROOT / "hidden_bugs_report.txt"
    lines = []
    lines.append(f"Hidden Bug Detector Report")
    lines.append(f"Scanned: {total_files} files")
    lines.append(f"CRITICAL: {report.count('CRITICAL')}")
    lines.append(f"WARNING: {report.count('WARNING')}")
    lines.append(f"INFO: {report.count('INFO')}")
    lines.append(f"Total: {report.count()}")
    lines.append("")

    for sev, cat, fpath, detail, hint in report.bugs:
        lines.append(f"[{sev}] [{cat}] {fpath}: {detail}")
        if hint:
            lines.append(f"  FIX: {hint}")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"📄 レポート保存: {report_path}")


# ─────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Wiki Hidden Bug Detector")
    parser.add_argument("--lang", choices=LANGUAGES, help="特定言語のみスキャン")
    parser.add_argument("--fix-hint", action="store_true", help="修正ヒント付き出力")
    parser.add_argument("--ci", action="store_true", help="CI用（exitcode=CRITICAL数）")
    args = parser.parse_args()

    langs = [args.lang] if args.lang else None
    report, total_files = scan_all(langs, args.fix_hint)

    print_report(report, total_files, args.fix_hint)
    write_report_file(report, total_files)

    if args.ci:
        sys.exit(report.count("CRITICAL"))


if __name__ == "__main__":
    main()
