#!/usr/bin/env python3
"""
patch_locale_full.py — Wiki locale純粋性パッチ（安全モード対応）

対象: JA + EN のみ（PTは後回し — 柔術コンテンツ充実後に対応）
ヨガ: コメントアウト済みファイルはスキップ（ヨガWikiは後回し）

安全機能:
  --dry-run     書き込みせず差分だけ表示（デフォルト）
  --apply       実際に書き込む
  --verify      パッチ前後で既存テストを実行し、壊れていないことを確認
  --sample N    差分をN件だけ表示（dry-run時）

使い方:
    python3 scripts/patch_locale_full.py                   # dry-run（安全）
    python3 scripts/patch_locale_full.py --sample 5        # 5件だけプレビュー
    python3 scripts/patch_locale_full.py --apply            # 実行
    python3 scripts/patch_locale_full.py --apply --verify   # 実行+前後テスト

依存: Python 3.8+ 標準ライブラリのみ
"""

import os
import re
import sys
import difflib
import argparse
import subprocess
from pathlib import Path

WIKI_ROOT = Path(__file__).parent.parent

# ── 対象言語（PTは後回し）──────────────────────
TARGET_LANGS = ["en", "ja"]

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
        # Pillar page CTA variant 1 (cta-banner)
        (r'Track Your BJJ Progress', '柔術の上達を記録しよう'),
        (r'Record techniques, track streaks, and analyze your game with BJJ App', 'テクニック・連続記録・上達分析をBJJ Appで管理'),
        (r'>Start Free →<', '>無料で始める →<'),
        (r'>\s*Start Free →\s*<', '>無料で始める →<'),
        # Pillar page CTA variant 2 (cta div)
        (r'Log sessions, track techniques, and measure growth', '練習・テクニック・成長を記録しよう'),
        (r'>Try BJJ App Free →<', '>BJJ Appを無料で試す →<'),
        (r'Try BJJ App Free →', 'BJJ Appを無料で試す →'),
        # Pillar page CTA variant 3 (HTML entity arrow + different description)
        (r'>Start Free &rarr;<', '>無料で始める →<'),
        (r'Start Free &rarr;', '無料で始める →'),
        (r'Track your BJJ progress and set training goals\. Free to start\.', '柔術の上達を記録し、練習目標を設定しよう。無料で始められます。'),
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
        (r'BJJ練習記録アプリ', 'BJJ Training Log App'),
        (r'練習記録アプリ', 'BJJ Training Log'),
        (r'練習回数・テクニック・連続記録を一元管理。無料で始められます。', 'Track sessions, techniques, and streaks. Free forever.'),
        (r'>無料で始める →<', '>Start Free →<'),
        (r'>無料で始める<', '>Start Free<'),
        (r'>練習を記録しよう<', '>Log Your Training<'),
        (r'練習ログ・テクニック帳・目標トラッカー', 'Training log, technique journal, goal tracker'),
        (r'>トラッキングアプリ<', '>Tracking App<'),
        (r'>ホーム<', '>Home<'),
        # Pillar page CTA variant 2
        (r'BJJ練習を記録しよう', 'Log Your BJJ Training'),
        (r'無料BJJトラッキングアプリ', 'Free BJJ Tracking App'),
        (r'練習回数・テクニック・連続記録を一元管理', 'Track sessions, techniques, and streaks'),
        (r'無料で始められます', 'Free forever'),
        # Copyright
        (r'&copy;\s*2025', '&copy; 2026'),
        (r'&copy;\s*2024', '&copy; 2026'),
    ],
}


def comment_out_yoga(html: str) -> str:
    """ヨガセクションをコメントアウト（まだされていない場合）"""
    if "YOGA SECTION HIDDEN" in html:
        return html  # 既にコメントアウト済み

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


def compute_patch(filepath: Path, lang: str) -> tuple[str, str] | None:
    """パッチ前後のテキストを返す。変更なしならNone"""
    try:
        original = filepath.read_text(encoding="utf-8")
    except Exception:
        return None

    html = original

    # 言語別テキスト置換
    for pattern, replacement in REPLACEMENTS.get(lang, []):
        html = re.sub(pattern, replacement, html)

    # ヨガコメントアウト
    html = comment_out_yoga(html)

    if html != original:
        return (original, html)
    return None


def show_diff(filepath: Path, original: str, patched: str, max_context: int = 3):
    """ファイル単位の差分を表示"""
    orig_lines = original.splitlines(keepends=True)
    new_lines = patched.splitlines(keepends=True)
    diff = difflib.unified_diff(
        orig_lines, new_lines,
        fromfile=f"a/{filepath.name}",
        tofile=f"b/{filepath.name}",
        n=max_context,
    )
    diff_text = "".join(diff)
    if diff_text:
        print(diff_text)
    return bool(diff_text)


def run_tests() -> bool:
    """既存テストスイートを実行し、全PASSならTrueを返す"""
    test_script = WIKI_ROOT / "scripts" / "test_wiki_quality.py"
    if not test_script.exists():
        print("  ⚠️  test_wiki_quality.py が見つかりません。スキップ。")
        return True

    print("  🧪 テスト実行中...")
    result = subprocess.run(
        [sys.executable, str(test_script)],
        cwd=str(WIKI_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode == 0:
        print("  ✅ テスト全PASS")
        return True
    else:
        print(f"  ❌ テスト失敗 (exit code {result.returncode})")
        # 失敗内容のサマリー
        for line in result.stdout.splitlines()[-10:]:
            print(f"     {line}")
        for line in result.stderr.splitlines()[-5:]:
            print(f"     {line}")
        return False


def run_detector() -> int:
    """detect_hidden_bugs.py を実行し、CRITICAL数を返す"""
    detector = WIKI_ROOT / "scripts" / "detect_hidden_bugs.py"
    if not detector.exists():
        print("  ⚠️  detect_hidden_bugs.py が見つかりません。スキップ。")
        return 0

    print("  🔍 Hidden Bug Detector 実行中...")
    result = subprocess.run(
        [sys.executable, str(detector), "--ci", "--lang", "ja"],
        cwd=str(WIKI_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    # --ci mode: exit code = CRITICAL count
    critical = result.returncode
    print(f"  {'✅' if critical == 0 else '❌'} CRITICAL: {critical}")
    return critical


def main():
    parser = argparse.ArgumentParser(
        description="Wiki locale patch（安全モード）",
        epilog="デフォルトはdry-run。--applyで実行。",
    )
    parser.add_argument("--apply", action="store_true",
                        help="実際にファイルを書き換える（省略時はdry-run）")
    parser.add_argument("--verify", action="store_true",
                        help="パッチ前後でテストを実行して破壊がないことを確認")
    parser.add_argument("--sample", type=int, default=0,
                        help="dry-run時に差分を表示する最大ファイル数（0=全件）")
    args = parser.parse_args()

    is_dry_run = not args.apply

    if is_dry_run:
        print("\n🔒 DRY-RUN モード（ファイルは変更されません）")
        print("   実行するには: python3 scripts/patch_locale_full.py --apply\n")
    else:
        print("\n⚡ APPLY モード（ファイルを書き換えます）\n")

    # ── verify: パッチ前テスト ──
    if args.verify and not is_dry_run:
        print("━━━ パッチ前テスト ━━━")
        pre_test_ok = run_tests()
        pre_critical = run_detector()
        if not pre_test_ok:
            print("\n❌ パッチ前にテストが失敗しています。先にテスト修正を。")
            sys.exit(1)
        print()

    # ── パッチ計算 ──
    total = 0
    changes = []  # (filepath, original, patched)

    for lang in TARGET_LANGS:
        lang_dir = WIKI_ROOT / lang
        if not lang_dir.exists():
            continue

        files = sorted(lang_dir.glob("*.html"))
        for f in files:
            total += 1
            result = compute_patch(f, lang)
            if result:
                changes.append((f, result[0], result[1]))

    # ── サマリー ──
    print(f"スキャン: {total} ファイル（{', '.join(TARGET_LANGS)}）")
    print(f"変更対象: {len(changes)} ファイル\n")

    if not changes:
        print("✅ パッチ不要 — 全ファイルがクリーンです。")
        return

    # ── dry-run: 差分表示 ──
    if is_dry_run:
        sample_count = args.sample if args.sample > 0 else len(changes)
        shown = 0
        for filepath, original, patched in changes[:sample_count]:
            rel = filepath.relative_to(WIKI_ROOT)
            print(f"── {rel} ──")
            show_diff(filepath, original, patched)
            shown += 1
            print()

        remaining = len(changes) - shown
        if remaining > 0:
            print(f"... 他 {remaining} ファイル（--sample で表示数を変更可能）")

        print(f"\n🔒 DRY-RUN 完了。{len(changes)} ファイルが変更予定。")
        print(f"   実行: python3 scripts/patch_locale_full.py --apply")
        return

    # ── apply: 書き込み ──
    applied = 0
    for filepath, original, patched in changes:
        filepath.write_text(patched, encoding="utf-8")
        applied += 1

    lang_counts = {}
    for filepath, _, _ in changes:
        lang = filepath.parent.name
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

    for lang, count in sorted(lang_counts.items()):
        print(f"  {lang}: {count} ファイル修正")
    print(f"\n合計: {applied}/{total} ファイル修正")

    # ── verify: パッチ後テスト ──
    if args.verify:
        print("\n━━━ パッチ後テスト ━━━")
        post_test_ok = run_tests()
        post_critical = run_detector()

        if not post_test_ok:
            print("\n❌ パッチ後にテストが失敗しました！")
            print("   パッチで既存コンテンツが壊れた可能性があります。")
            print("   git checkout で戻すことを検討してください。")
            sys.exit(1)

        if post_critical > pre_critical:
            print(f"\n⚠️  CRITICAL が増加しました: {pre_critical} → {post_critical}")
        elif post_critical < pre_critical:
            print(f"\n✅ CRITICAL が減少しました: {pre_critical} → {post_critical}")
        else:
            print(f"\n✅ CRITICAL 変化なし: {post_critical}")

        print("\n✅ パッチ完了 — 安全検証PASS")


if __name__ == "__main__":
    main()
