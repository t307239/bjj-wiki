#!/usr/bin/env python3
"""
check_locale_parity.py — z176b: 先祖返り構造的防止 lint

何度も繰り返した先祖返り pattern:
  1. PT 先に修正 → EN/JA 忘れる (z175 cleanup, z150/z151 等)
  2. 新規パッチ追加 → 既存類似パッチを grep せず重複/衝突 (z175 vs legacy float)
  3. generator スクリプトを修正せず HTML だけ修正 → 翌日 generate.yml で先祖返り

本 lint は 「marker count parity」 を強制することで、3 locale 不揃いを即検出する:
  - en/, ja/, pt/ 配下の HTML で各 z### marker の出現数を比較
  - 3 locale 間で件数差が 5% を超えれば 🔴 fail
  - これにより「PT だけ修正して EN/JA 忘れる」が CI で必ず検知される

また、generator script (generate_bjj_wiki.py / fix_docs.py 等) と既存 HTML
出力の marker 一致もチェック:
  - generator が出力する marker は HTML にも存在するはず
  - HTML にあるが generator にない marker → 先祖返りで日次再注入で剥がれる

Usage:
    python3 scripts/check_locale_parity.py [--ci]
"""
from __future__ import annotations
import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANG_DIRS = ["en", "ja", "pt"]

# z### marker 検出 regex (HTML 内のコメントマーカー)
MARKER_RE = re.compile(r"<!-- (z\d{3,}-[\w-]+) -->")

# z176c: 1% に縮小 (1556 × 1% = 16 ファイル)。
# 元 5% (78ファイルまで silent) は穴。
DIVERGENCE_THRESHOLD = 0.01


def count_markers_per_lang() -> dict[str, dict[str, int]]:
    """{lang: {marker: count}}"""
    out: dict[str, dict[str, int]] = {lang: defaultdict(int) for lang in LANG_DIRS}
    for lang in LANG_DIRS:
        d = ROOT / lang
        if not d.exists():
            continue
        for fp in d.glob("*.html"):
            if fp.name in ("index.html", "404.html"):
                continue
            try:
                c = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            for m in MARKER_RE.finditer(c):
                out[lang][m.group(1)] += 1
    return out


def find_divergence(counts: dict[str, dict[str, int]]) -> list[dict]:
    """Find markers where en/ja/pt counts differ by >5%."""
    findings = []
    all_markers = set()
    for lang_counts in counts.values():
        all_markers.update(lang_counts.keys())

    for marker in sorted(all_markers):
        per_lang = {lang: counts[lang].get(marker, 0) for lang in LANG_DIRS}
        max_count = max(per_lang.values())
        min_count = min(per_lang.values())
        if max_count == 0:
            continue
        diff_pct = (max_count - min_count) / max_count
        if diff_pct > DIVERGENCE_THRESHOLD:
            findings.append({
                "id": "LOCALE_PARITY_DIVERGENCE",
                "severity": "🔴",
                "marker": marker,
                "counts": per_lang,
                "diff_pct": round(diff_pct * 100, 1),
                "description": (
                    f"{marker}: en={per_lang['en']}, ja={per_lang['ja']}, pt={per_lang['pt']} "
                    f"(diff {round(diff_pct*100,1)}% > {int(DIVERGENCE_THRESHOLD*100)}%)"
                ),
            })
    return findings


def check_marker_content_consistency() -> list[dict]:
    """z176d (穴 #2): marker 内のコンテンツがロケール内で一貫しているか確認。

    例: z176-bottom-cta が EN 1556 件あるはずが、新しいコピーへ更新時に
    1500 件は新コピー、56 件は旧コピーのまま、という drift を検出する。

    各 marker × locale で content 部分 (タグ/属性除いた可視テキスト) を hash 化し、
    1 locale 内で hash 種類が 2 以上なら drift。
    """
    import hashlib
    findings = []
    # marker block 開始から最初の閉じタグまでを抽出
    BLOCK_RE = re.compile(
        r"<!-- (z\d{3,}-[\w-]+) -->(.*?)(?=<!-- z\d|<footer|</body>|$)",
        re.DOTALL,
    )
    # 可視テキストのみ残すため HTML タグ・属性・空白を正規化
    TAG_RE = re.compile(r"<[^>]+>")
    WS_RE = re.compile(r"\s+")

    def normalize(html: str) -> str:
        text = TAG_RE.sub(" ", html)
        text = WS_RE.sub(" ", text).strip()
        return text

    # {marker: {lang: {content_hash: count}}}
    per_marker_lang_hash: dict = {}
    for lang in LANG_DIRS:
        d = ROOT / lang
        if not d.exists():
            continue
        for fp in d.glob("*.html"):
            if fp.name in ("index.html", "404.html"):
                continue
            try:
                c = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            for m in BLOCK_RE.finditer(c):
                marker = m.group(1)
                content = normalize(m.group(2))
                if not content:
                    continue
                h = hashlib.sha256(content.encode("utf-8")).hexdigest()[:10]
                per_marker_lang_hash.setdefault(marker, {}).setdefault(lang, {}).setdefault(h, 0)
                per_marker_lang_hash[marker][lang][h] += 1

    # 各 marker × locale で hash 種類を数える。複数あれば drift。
    for marker, lang_data in per_marker_lang_hash.items():
        for lang, hash_counts in lang_data.items():
            if len(hash_counts) > 1:
                # ノイズ低減: 最頻出を「正規」とし、それ以外の合計が >1% なら fail
                total = sum(hash_counts.values())
                sorted_h = sorted(hash_counts.items(), key=lambda x: -x[1])
                primary_hash, primary_count = sorted_h[0]
                drift_count = total - primary_count
                drift_pct = drift_count / total
                # 同じ marker 内のコピー差は drift。z176d: threshold=0 (any drift = fail)
                # 1 ファイルでも違うコピーがあれば検出する。
                findings.append({
                    "id": "MARKER_CONTENT_DRIFT",
                    "severity": "🔴",
                    "description": (
                        f"{marker} ({lang}): {len(hash_counts)} 種類のコピー存在 "
                        f"(主要 {primary_count} / 異なる {drift_count} = {round(drift_pct*100,1)}%) "
                        f"→ patch_*.py 再実行 or marker を bump (z### 番号上げ) で全更新"
                    ),
                })
    return findings


def find_orphan_markers(counts: dict[str, dict[str, int]]) -> list[dict]:
    """Markers in HTML output that no generator script produces.
    These will be erased on next regeneration → silent regression."""
    findings = []
    # All markers seen in HTML
    html_markers = set()
    for lang_counts in counts.values():
        html_markers.update(lang_counts.keys())

    # All markers produced by any generator script
    script_markers = set()
    for fp in (ROOT / "scripts").glob("*.py"):
        try:
            c = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in MARKER_RE.finditer(c):
            script_markers.add(m.group(1))

    orphans = html_markers - script_markers
    for marker in sorted(orphans):
        # Estimate scope
        total = sum(counts[lang].get(marker, 0) for lang in LANG_DIRS)
        findings.append({
            "id": "ORPHAN_MARKER",
            "severity": "🟡",
            "marker": marker,
            "html_count": total,
            "description": (
                f"{marker}: HTML に {total} 件あるが、生成元スクリプトが見つからない "
                f"→ 次回 generate で剥がれる可能性 (script に再追加 or HTML から手動削除)"
            ),
        })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true", help="CI mode: exit 1 if 🔴 > 0")
    args = parser.parse_args()

    counts = count_markers_per_lang()

    print("=" * 70)
    print("🛡️  Wiki locale parity check (z176b)")
    print("=" * 70)
    print()

    # Per-marker summary
    all_markers = set()
    for lc in counts.values():
        all_markers.update(lc.keys())
    print(f"Markers detected: {len(all_markers)}")
    for marker in sorted(all_markers):
        per_lang = {lang: counts[lang].get(marker, 0) for lang in LANG_DIRS}
        print(f"  {marker}: en={per_lang['en']:>5}, ja={per_lang['ja']:>5}, pt={per_lang['pt']:>5}")
    print()

    # Findings
    divergence = find_divergence(counts)
    orphans = find_orphan_markers(counts)
    content_drift = check_marker_content_consistency()
    all_findings = divergence + orphans + content_drift
    criticals = [f for f in all_findings if f["severity"] == "🔴"]
    warnings = [f for f in all_findings if f["severity"] == "🟡"]

    if criticals:
        print(f"🔴 Critical: {len(criticals)}")
        for f in criticals[:20]:
            print(f"  🔴 [{f['id']}] {f['description']}")
    if warnings:
        print(f"🟡 Warning:  {len(warnings)}")
        for f in warnings[:20]:
            print(f"  🟡 [{f['id']}] {f['description']}")
    if not all_findings:
        print("✅ Locale parity OK — all markers consistent across en/ja/pt")
        print("✅ All markers traceable to generator scripts (no orphans)")

    if args.ci and criticals:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
