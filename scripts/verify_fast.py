#!/usr/bin/env python3
"""
verify_fast.py — z262: 全 lint を並列実行して make verify を高速化

戦略:
  既存 check_*.py / detect_*.py / scan_*.py を一切変更せず、
  サブプロセスとして並列実行するだけ。
  - 逐次実行: 60〜90 秒 (53 スクリプト × 1〜3 秒)
  - 並列実行: 5〜10 秒 (CPUバウンドでなくI/Oバウンドのため)

Why subprocess: ロジックを移植すると先祖返り・仕様漏れリスクがある。
既存スクリプトをそのまま呼ぶことで 0 regression を保証する。

Usage:
    python3 scripts/verify_fast.py          # 全 lint 並列実行
    python3 scripts/verify_fast.py --ci     # exit 1 on any failure
"""
from __future__ import annotations
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"

# スクリプト名 → 呼び出しオプション のマップ
# Makefile の呼び出し方を忠実に再現する
LINT_SPECS: list[tuple[str, list[str], dict[str, str]]] = [
    # (script, extra_args, extra_env)
    ("check_locale_parity.py",                ["--ci"], {}),
    ("detect_gha_regression.py",              ["--ci"], {}),
    ("scan_ja_english_mixing.py",             ["--ci"], {}),
    ("scan_pt_english_mixing.py",             ["--ci"], {"CI_THRESHOLD": "50"}),
    ("check_broken_links.py",                 ["--ci"], {}),
    ("check_sitemap_drift.py",                ["--ci"], {}),
    ("check_hreflang_validity.py",            ["--ci"], {}),
    ("check_jsonld_validity.py",              ["--ci"], {}),
    ("check_breadcrumb_jsonld.py",            ["--ci"], {}),
    ("check_ui_label_locale_drift.py",        ["--ci"], {}),
    ("check_lang_switcher_consistency.py",    ["--ci"], {}),
    ("check_breadcrumb_locale_drift.py",      ["--ci"], {}),
    ("check_h1_brand_pollution.py",           ["--ci"], {}),
    ("check_duplicate_bjj_prefix.py",         ["--ci"], {}),
    ("check_external_link_noreferrer.py",     ["--ci"], {}),
    ("check_duplicate_faq_heading.py",        ["--ci"], {}),
    ("check_jsonld_url_drift.py",             ["--ci"], {}),
    ("check_internal_link_relative.py",       ["--ci"], {}),
    ("check_twitter_image_sync.py",           ["--ci"], {}),
    ("check_no_meta_keywords.py",             ["--ci"], {}),
    ("check_analytics_id_drift.py",           ["--ci"], {}),
    ("check_login_cta_tracking.py",           ["--ci"], {}),
    ("check_duplicate_titles.py",             ["--ci"], {}),
    ("check_target_blank_security.py",        ["--ci"], {}),
    ("check_duplicate_meta_desc.py",          ["--ci"], {}),
    ("check_brand_suffix_pollution.py",       ["--ci"], {}),
    ("check_naked_bjj_app_cta.py",            ["--ci"], {}),
    ("check_broken_anchors.py",               ["--ci"], {}),
    ("check_meta_attribute_quotes.py",        ["--ci"], {}),
    ("check_misrouted_form_endpoints.py",     ["--ci"], {}),
    ("check_duplicate_word_in_title.py",      ["--ci"], {}),
    # --strict (CI block しない、WARNING 表示のみ)
    ("check_ja_body_english_dominant.py",     ["--strict"], {}),
    ("check_title_html_tags.py",              ["--ci"], {}),
    ("check_cta_text_locale_drift.py",        ["--ci"], {}),
    ("check_seo_meta_completeness.py",        ["--ci"], {}),
    ("check_duplicate_related_techniques.py", ["--ci"], {}),
    ("check_no_nested_p.py",                  ["--ci"], {}),
    ("check_og_locale_completeness.py",       ["--ci"], {}),
    ("check_mobile_a11y_meta.py",             ["--ci"], {}),
    ("check_main_tag_present.py",             ["--ci"], {}),
    ("check_videoobject_when_yt_embed.py",    ["--ci"], {}),
    ("check_apple_touch_icon_png.py",         ["--ci"], {}),
    ("check_skip_link.py",                    ["--ci"], {}),
    ("check_pwa_iframe_twitter.py",           ["--ci"], {}),
    ("check_no_fake_subscriber_claim.py",     ["--ci"], {}),
    ("check_og_video_when_yt.py",             ["--ci"], {}),
    ("check_no_generic_h1.py",                ["--ci"], {}),
    ("check_thin_content_indexable.py",       ["--ci"], {}),
    ("check_index_locale_parity.py",          ["--ci"], {}),
    ("check_no_duplicate_html_id.py",         ["--ci"], {}),
    ("check_html_quality_minor.py",           ["--ci"], {}),
    ("check_og_image_url_encoding.py",        ["--ci"], {}),
    ("check_description_quality.py",          ["--ci"], {}),
    ("check_h2_id_clobber.py",                ["--ci"], {}),
    ("check_zindex_hardcode_in_html.py",      ["--ci"], {}),
    ("check_heading_hierarchy.py",            ["--ci"], {}),
]


def run_lint(spec: tuple[str, list[str], dict[str, str]]) -> dict:
    script, args, extra_env = spec
    fp = SCRIPTS_DIR / script
    env = {**os.environ, **extra_env}
    result = subprocess.run(
        [sys.executable, str(fp)] + args,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )
    return {
        "script": script,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> int:
    ci_mode = "--ci" in sys.argv

    # Why ThreadPoolExecutor: スクリプトはI/Oバウンド (4,500 HTML 読み込み)
    # CPUバウンドでないため GIL の影響は軽微、subprocess は別プロセスなので完全並列
    workers = min(len(LINT_SPECS), 12)  # 12並列以上はI/Oサチュレートするため上限

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(run_lint, spec): spec[0] for spec in LINT_SPECS}
        for future in as_completed(futures):
            results.append(future.result())

    # 出力はスクリプト名でソートして再現性を確保（並列で順番が変わるため）
    results.sort(key=lambda r: r["script"])

    failed = []
    for r in results:
        # 各スクリプトの出力をそのまま表示
        if r["stdout"]:
            print(r["stdout"], end="")
        if r["stderr"]:
            print(r["stderr"], end="", file=sys.stderr)
        if r["returncode"] != 0:
            failed.append(r["script"])

    print()
    if failed:
        print(f"🔴 {len(failed)} lint(s) failed:")
        for s in failed:
            print(f"  ✗ {s}")
        if ci_mode:
            return 1
    else:
        print(f"✅ All {len(results)} lints passed.")
        print("   Safe to commit.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
