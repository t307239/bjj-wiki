#!/usr/bin/env python3
"""
fix_ja_meta_desc_drift.py — z255w: 13 ja page で EN fallback meta description が
そのまま残っていた bug の fix.

13 page 全てに同じ EN 文 ("Master the techniques of Brazilian Jiu-Jitsu with
detailed guides and expert strategies.") が出力されていた → Google が
duplicate meta description として SEO 評価低下 + JA SERP に EN 表示。

各 page の EN 版 meta description を JA 翻訳した文に差し替える。
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# slug → 翻訳済み JA description (EN desc を意味的に翻訳)
JA_DESCRIPTIONS = {
    "bjj-training-with-beginners":
        "初心者を守りながら自分の上達にも繋げる、BJJ ジムでの初心者との練習のコツとマインドセット。",
    "bjj-competition-day-nutrition":
        "BJJ 大会当日の朝から計量までの完全な栄養戦略。エネルギー維持と体重管理を両立する実践ガイド。",
    "bjj-understanding-bjj":
        "BJJ の原則を概念レベルで深く理解するためのアプローチ。技を超えた本質的な思考法を解説。",
    "bjj-three-year-bjj":
        "白帯から紫帯までの 3 年間の成長プログレッション。各段階で身につけるべき技術と意識を体系化。",
    "bjj-training-with-advanced":
        "上級者とのスパーリングで成長を加速する戦略。タップ前提の質問思考と意図的な負荷設計。",
    "bjj-progressive-overload-bjj":
        "BJJ トレーニングに漸進的過負荷の原則を応用する方法。スパーラウンド・ドリル量・強度の調整法。",
    "bjj-adaptation-bjj":
        "異なる相手やジム環境に適応するスキルの育て方。固定パターンから抜け出す思考法。",
    "bjj-first-year-bjj":
        "BJJ を始めて最初の 1 年間の完全ガイド。練習頻度、技の優先順位、白帯期に避けるべき罠。",
    "bjj-breakdown-technique-bjj":
        "複雑な BJJ テクニックを分解して理解する方法。動画分析・ステップ化・自分に適応させるプロセス。",
    "bjj-ice-bath-bjj":
        "冷水療法・アイスバスのプロトコルとリカバリー効果。BJJ 練習後に活用する実践的応用。",
    "bjj-shrimping-details":
        "シュリンプムーブのメカニクス・ヒップムーブ・応用パターンの詳細解説。ガード保持の基礎技術。",
    "bjj-film-study-bjj":
        "BJJ のフィルムスタディ手法。トップ選手の試合映像から技と判断を学ぶための分析フレーム。",
    "bjj-transfer-of-training":
        "異なるポジション・状況間でトレーニング効果を転移させる理論。効率的な練習設計の鍵となる概念。",
}


def main():
    print("🔧 fix_ja_meta_desc_drift.py — z255w")
    fixed = 0
    desc_re = re.compile(
        r'(<meta\s+name=["\']description["\']\s+content=["\'])([^"\']+)(["\'])',
        re.IGNORECASE,
    )
    og_desc_re = re.compile(
        r'(<meta\s+property=["\']og:description["\']\s+content=["\'])([^"\']+)(["\'])',
        re.IGNORECASE,
    )
    for slug, new_desc in JA_DESCRIPTIONS.items():
        fp = REPO_ROOT / "ja" / f"{slug}.html"
        if not fp.exists():
            print(f"  ⚠️  ja/{slug}.html not found")
            continue
        html = fp.read_text(encoding="utf-8")
        # Replace meta description (first occurrence)
        new = desc_re.sub(
            lambda m: f"{m.group(1)}{new_desc}{m.group(3)}",
            html,
            count=1,
        )
        # Also sync og:description if it has the same EN fallback
        new = og_desc_re.sub(
            lambda m: f"{m.group(1)}{new_desc}{m.group(3)}"
            if "Master the techniques of Brazilian Jiu-Jitsu" in m.group(2)
            else m.group(0),
            new,
            count=1,
        )
        if new != html:
            fp.write_text(new, encoding="utf-8")
            fixed += 1
            print(f"  ✅ ja/{slug}.html")
    print(f"\n✅ Total fixed: {fixed} files")


if __name__ == "__main__":
    main()
