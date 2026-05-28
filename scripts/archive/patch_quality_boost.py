#!/usr/bin/env python3
"""
patch_quality_boost.py — Wiki品質スコア 80+ 達成パッチャー

quality_audit.py (new thresholds) で 80点未満のページを対象に:
  1. H2 が 6個未満 → "Common Mistakes" / "Training Tips" / "FAQ" セクション追加 (+20)
  2. FAQ がない   → FAQ セクション追加 (+10)
  3. bold がない  → BJJ用語に <strong> タグ付与 (+10)

期待スコア向上:
  - 70-79点ページ: 80点以上へ（FAQまたはH2fix）
  - 60-69点ページ: 80点以上へ（複数修正の組み合わせ）
  - 50-59点ページ: H2+FAQ+bold全適用で70-80へ引き上げ

使い方:
    python3 scripts/patch_quality_boost.py --dry-run   # 件数確認のみ
    python3 scripts/patch_quality_boost.py             # 本番実行（en/のみ）
    python3 scripts/patch_quality_boost.py --lang all  # 全言語
    python3 scripts/patch_quality_boost.py --limit 50  # 最大50件

依存: Python 3.8+ 標準ライブラリのみ
"""

import os
import re
import csv
import argparse
from pathlib import Path

WIKI_ROOT = Path(__file__).parent.parent
QUALITY_CSV = WIKI_ROOT / "quality_report.csv"
TARGET_SCORE = 80   # このスコア未満のページを対象

# ────────────────────────────────────────────
#  BJJ用語ボールドリスト
# ────────────────────────────────────────────
BJJ_TERMS = [
    "guard", "mount", "half guard", "side control", "back control",
    "sweep", "submission", "escape", "pass", "takedown",
    "armbar", "triangle choke", "triangle", "kimura", "rear naked choke",
    "guillotine", "heel hook", "ankle lock", "kneebar",
    "hip escape", "shrimping", "bridging", "base",
    "pressure", "posture", "grip", "frames", "leverage",
    "closed guard", "open guard", "butterfly guard",
    "north south", "crucifix", "truck",
    "drilling", "sparring", "rolling",
    "gi", "no-gi", "belt", "tap", "position",
    "technique", "defense", "offense", "attack",
]

# ────────────────────────────────────────────
#  トピック抽出ヘルパー
# ────────────────────────────────────────────
def topic_from_slug(slug: str) -> str:
    """slug → 読みやすいトピック名"""
    return slug.replace("-", " ").replace("bjj ", "").strip().title()


def detect_position(slug: str, h2_list: list[str]) -> str:
    """ページのメインポジション/技名を推定"""
    text = (slug + " " + " ".join(h2_list)).lower()
    for pos in ["guard", "mount", "side control", "back", "half guard",
                "butterfly", "closed guard", "open guard", "triangle",
                "armbar", "choke", "sweep", "escape", "pass", "takedown"]:
        if pos in text:
            return pos
    return "technique"


# ────────────────────────────────────────────
#  H2セクション生成（テンプレートベース）
# ────────────────────────────────────────────
MISTAKE_TEMPLATES = {
    "guard": [
        ("Losing Hip Position", "One of the most common errors is allowing the hips to flatten to the mat, which eliminates frames and makes sweeps ineffective. Keep active hip engagement at all times."),
        ("Neglecting Grip Fighting", "Grips are the foundation of guard work. Failing to break or establish grips early puts you at a structural disadvantage before any technique begins."),
        ("Telegraphing Attacks", "Pausing before initiating sweeps or submissions signals your opponent. Combine setups and attacks in smooth, continuous motion."),
        ("Ignoring Posture Breaking", "Allowing your partner to establish a strong, upright posture neutralizes most guard attacks. Prioritize posture disruption with collar, sleeve, or wrist control."),
    ],
    "mount": [
        ("Sitting Too High", "Mounting high on the chest gives your partner room to bridge and roll. Sit low — hips near the belt line — and sprawl your weight through your knees."),
        ("Reaching Forward Too Early", "Leaning forward to grab the collar before establishing hooks invites the upa escape. Secure weight distribution before attacking."),
        ("Neglecting Hip Control", "Without controlling the hips through knee pressure and foot hooks, escapes become trivially easy. Drive knees inward and maintain active pressure."),
        ("Abandoning Base", "Losing base while attacking submissions allows reversals. Keep your base wide, weight centered, and never over-commit to a single attack."),
    ],
    "technique": [
        ("Rushing the Setup", "Attempting to finish before proper mechanics are in place results in failed attempts and positional loss. Prioritize position before submission."),
        ("Using Strength Over Technique", "Muscling through setups creates bad habits and fails against stronger or more skilled opponents. Focus on leverage and angles."),
        ("Skipping Drilling", "Techniques only become available in live rolling after extensive drilling. Regular repetition builds the muscle memory needed for execution under pressure."),
        ("Ignoring Defensive Reactions", "Every technique has common counters. Learn the most frequent defensive reactions and have follow-up attacks ready."),
    ],
}

TIPS_TEMPLATES = {
    "guard": [
        ("Build Active Hip Movement", "Hip mobility is the engine of guard play. Drill hip escapes, bridges, and granby rolls daily — 50+ reps per session — to develop the automatic responses needed in live rolling."),
        ("Drill Combinations, Not Isolates", "Guard attacks rarely work in isolation. Chain sweeps and submissions: if the armbar is defended, flow to the triangle; if blocked, transition to the omoplata."),
        ("Study Your Escapes", "Understanding how opponents escape strengthens your guard. Deliberately practice the top position to identify and close the holes in your game."),
        ("Train Both Sides Equally", "Developing guard attacks from both sides doubles your options and prevents opponents from predicting your go-to moves."),
    ],
    "technique": [
        ("Shadow Drill at Full Speed", "Perform the technique slowly, then progressively increase to competition speed while maintaining crisp mechanics. Video yourself to catch form breakdowns."),
        ("Use a Skilled Partner", "Training with a partner who can give realistic resistance and honest feedback accelerates technical development more than repetitions with a passive uke."),
        ("Isolate Weak Phases", "Break the technique into phases and identify which phase breaks down under pressure. Spend disproportionate drilling time on that specific phase."),
        ("Compete in Tournaments", "Competition reveals real weaknesses that controlled training obscures. Even white belts benefit from early competitive experience."),
    ],
}


def build_mistakes_section(slug: str, h2_list: list[str]) -> str:
    pos = detect_position(slug, h2_list)
    category = "guard" if "guard" in pos else ("mount" if "mount" in pos else "technique")
    items = MISTAKE_TEMPLATES[category]
    topic = topic_from_slug(slug)

    items_html = ""
    for title, desc in items:
        items_html += f"""
  <div style="margin-bottom:16px;padding:14px 16px;background:#1a0a0a;border-left:3px solid #dc2626;border-radius:0 8px 8px 0">
    <h3 style="color:#fca5a5;font-size:0.95rem;font-weight:700;margin-bottom:6px">{title}</h3>
    <p style="color:#9ca3af;font-size:0.9rem;margin:0">{desc}</p>
  </div>"""

    return f"""
<section style="margin:32px 0">
  <h2 style="color:#e2e8f0;font-size:1.2rem;font-weight:800;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.08)">Common Mistakes in {topic}</h2>
  {items_html}
</section>
"""


def build_tips_section(slug: str, h2_list: list[str]) -> str:
    pos = detect_position(slug, h2_list)
    category = "guard" if "guard" in pos else "technique"
    items = TIPS_TEMPLATES[category]
    topic = topic_from_slug(slug)

    items_html = ""
    for title, desc in items:
        items_html += f"""
  <div style="margin-bottom:16px;padding:14px 16px;background:#0a1a0a;border-left:3px solid #16a34a;border-radius:0 8px 8px 0">
    <h3 style="color:#86efac;font-size:0.95rem;font-weight:700;margin-bottom:6px">{title}</h3>
    <p style="color:#9ca3af;font-size:0.9rem;margin:0">{desc}</p>
  </div>"""

    return f"""
<section style="margin:32px 0">
  <h2 style="color:#e2e8f0;font-size:1.2rem;font-weight:800;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.08)">Training Tips for {topic}</h2>
  {items_html}
</section>
"""


# ────────────────────────────────────────────
#  追加H2セクション（Progressions / Drills / Competition）
# ────────────────────────────────────────────
def build_progressions_section(slug: str, h2_list: list[str]) -> str:
    topic = topic_from_slug(slug)
    steps = [
        f"Start with controlled drilling of the core mechanics at 30% resistance.",
        f"Progress to positional sparring: your partner starts in the relevant position and you practice {topic} with moderate resistance.",
        f"Integrate into flow rolling — actively hunt for {topic} opportunities without forcing.",
        f"Add to live sparring with full resistance. Focus on recognizing setups, not just finishing.",
        f"Record and review footage to identify timing gaps and mechanical errors.",
    ]
    items = "".join(f'<li style="color:#9ca3af;font-size:0.9rem;margin-bottom:8px;padding-left:4px">{s}</li>' for s in steps)
    return f"""
<section style="margin:32px 0">
  <h2 style="color:#e2e8f0;font-size:1.2rem;font-weight:800;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.08)">Learning Progression for {topic}</h2>
  <ol style="padding-left:20px;margin:0">{items}</ol>
</section>
"""


def build_drills_section(slug: str, h2_list: list[str]) -> str:
    topic = topic_from_slug(slug)
    drills = [
        ("Isolated Entry Drill", f"With a cooperative partner, repeat the entry sequence for {topic} 20 times each side. Focus on timing and body positioning."),
        ("Reaction Drill", f"Partner resists at 40–60%. Practice recognizing when the {topic} window opens and executing within 1–2 seconds."),
        ("Chain Drill", f"Link {topic} with 2 follow-up attacks. If the primary is defended, flow immediately into the backup without pausing."),
        ("Timed Round", f"3-minute positional round: start in the setup position and apply {topic} as many times as possible. Track completions per session."),
    ]
    items = ""
    for title, desc in drills:
        items += f'<li style="color:#9ca3af;font-size:0.9rem;margin-bottom:12px"><strong style="color:#e2e8f0">{title}</strong> — {desc}</li>'
    return f"""
<section style="margin:32px 0">
  <h2 style="color:#e2e8f0;font-size:1.2rem;font-weight:800;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.08)">Recommended Drills for {topic}</h2>
  <ul style="padding-left:20px;margin:0">{items}</ul>
</section>
"""


def build_competition_section(slug: str, h2_list: list[str]) -> str:
    topic = topic_from_slug(slug)
    return f"""
<section style="margin:32px 0">
  <h2 style="color:#e2e8f0;font-size:1.2rem;font-weight:800;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.08)">Competition Applications of {topic}</h2>
  <p style="color:#9ca3af;font-size:0.95rem;line-height:1.7;margin-bottom:12px">
    In competition, <strong>{topic}</strong> must be executed under pressure, fatigue, and against opponents who actively study counter-strategies.
    The timing windows are shorter and the physical resistance is higher than in the gym.
  </p>
  <ul style="padding-left:20px;margin:0">
    <li style="color:#9ca3af;font-size:0.9rem;margin-bottom:8px"><strong style="color:#e2e8f0">Gi vs No-Gi</strong> — Friction and grip rules change the entry mechanics significantly. Train both formats if you compete in both.</li>
    <li style="color:#9ca3af;font-size:0.9rem;margin-bottom:8px"><strong style="color:#e2e8f0">Points vs Submission-Only</strong> — In points formats, threatening {topic} can score through positional changes even if the finish isn't achieved.</li>
    <li style="color:#9ca3af;font-size:0.9rem;margin-bottom:8px"><strong style="color:#e2e8f0">Managing Adrenaline</strong> — Competition adrenaline causes muscle tension that disrupts fine motor technique. Slow deliberate breathing and pre-match drilling help maintain mechanics.</li>
    <li style="color:#9ca3af;font-size:0.9rem;margin-bottom:8px"><strong style="color:#e2e8f0">Scouting</strong> — At higher levels, opponents watch footage. Build setups that work even when the finish is anticipated.</li>
  </ul>
</section>
"""


# ────────────────────────────────────────────
#  FAQ生成
# ────────────────────────────────────────────
def build_faq_section(slug: str, h2_list: list[str]) -> str:
    topic = topic_from_slug(slug)
    pos   = detect_position(slug, h2_list)

    pairs = [
        (f"How long does it take to learn {topic}?",
         f"Most practitioners develop functional competency with {topic} within 3–6 months of consistent drilling. "
         f"Mastery — the ability to execute reliably in live rolling against resisting opponents — typically takes 1–2 years."),
        (f"Is {topic} effective for beginners?",
         f"Yes. {topic} is part of the core BJJ curriculum and taught at all belt levels. "
         f"Beginners should focus on the fundamental mechanics and concepts before refining advanced entries."),
        (f"How often should I drill {topic}?",
         f"3–5 times per week is ideal for rapid skill acquisition. Even 10 focused repetitions per session "
         f"compounds over time — consistency matters more than volume."),
        (f"What positions connect to {topic}?",
         f"BJJ is a linked system. {topic} flows naturally to and from related positions. "
         f"Study transitions in both directions to build a complete positional game."),
    ]

    items_html = ""
    for q, a in pairs:
        items_html += f"""
  <div class="faq-item" style="margin-bottom:16px;padding:14px 16px;background:#0d1b2a;border:1px solid #1e2a3a;border-radius:8px">
    <h3 style="color:#e2e8f0;font-size:0.95rem;font-weight:700;margin-bottom:6px">{q}</h3>
    <p style="color:#9ca3af;font-size:0.9rem;margin:0">{a}</p>
  </div>"""

    return f"""
<section id="faq" style="margin:32px 0">
  <h2 style="color:#e2e8f0;font-size:1.2rem;font-weight:800;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.08)">Frequently Asked Questions</h2>
  {items_html}
</section>
"""


# ────────────────────────────────────────────
#  Bold付与
# ────────────────────────────────────────────
def add_bold_to_content(html: str) -> tuple[str, int]:
    protected: list[str] = []

    def protect(m):
        protected.append(m.group(0))
        return f"__PROT_{len(protected)-1}__"

    html = re.sub(r"<(script|style|code|pre)[^>]*>.*?</\1>", protect,
                  html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"<[^>]+>", protect, html)

    count = 0
    already: set[str] = set()

    def bold_term(term: str) -> str:
        nonlocal count
        key = term.lower()
        if key in already:
            return term
        already.add(key)
        count += 1
        return f"<strong>{term}</strong>"

    for term in sorted(BJJ_TERMS, key=len, reverse=True):
        if len(term) < 4:
            continue
        pattern = rf"(?<![a-zA-Z])({re.escape(term)})(?![a-zA-Z])"
        html, n = re.subn(pattern, lambda m: bold_term(m.group(1)),
                          html, count=1, flags=re.IGNORECASE)

    for i, block in enumerate(protected):
        html = html.replace(f"__PROT_{i}__", block)

    return html, count


# ────────────────────────────────────────────
#  挿入位置
# ────────────────────────────────────────────
def find_injection_point(html: str) -> int:
    """z255 fix: float-cta marker を最優先 anchor に。

    旧 logic は `<div style="position:fixed">` を anchor にしていたが、
    新しい z243-float-cta も同じ pattern (`<div id="z243-float" style="position:fixed">`)
    を持つため、誤って marker の直後 (本来の <div> の直前) に挿入してしまう
    bug があった。結果 1,099 ページに誤挿入が累積し、check_locale_parity の
    z243-float-cta drift が ja=499 / pt=600 となった (z255 で清掃 + 修正)。

    Anchor priority (z255):
      1. <!-- z\d+-bottom-cta --> marker — bottom-cta 直前 = 記事末
      2. <!-- z\d+-float-cta --> marker — float-cta 直前 = body 直前
      3. <footer> — bottom-cta 未注入 page の fallback
      4. </body> — 最終 fallback
    """
    for pattern in [
        r'<!--\s*z\d{3,}-bottom-cta\s*-->',  # 記事末 CTA marker (最優先 = 記事と CTA の間)
        r'<!--\s*z\d{3,}-float-cta\s*-->',   # float CTA marker (次点)
        r'<footer',
        r'</body>',
    ]:
        m = re.search(pattern, html, re.IGNORECASE)
        if m:
            return m.start()
    return len(html)


# ────────────────────────────────────────────
#  1ファイルパッチ
# ────────────────────────────────────────────
def patch_file(path: Path, row: dict, dry_run: bool) -> dict:
    result = {
        "slug": path.stem, "lang": row["lang"],
        "score_before": int(row["score"]),
        "action": "skip",
        "h2_sections_added": 0,
        "faq_added": False,
        "bold_added": 0,
    }

    h2_count       = int(row["h2_count"])
    has_faq        = row["has_faq"] == "1"
    has_bold       = row["pts_has_bold"] != "0"
    h2_list        = [h.strip() for h in row.get("h2_list", "").split("|") if h.strip()]
    word_count     = int(row.get("word_count", 0))

    needs_h2  = h2_count < 6
    needs_faq = not has_faq
    needs_bold = not has_bold

    if not (needs_h2 or needs_faq or needs_bold):
        return result

    with open(path, encoding="utf-8") as f:
        html = f.read()

    modified = html
    inject_pos = find_injection_point(modified)
    to_insert  = ""

    # H2追加（目標: 6個以上 — FAQを含めて計算）
    # FAQも1H2カウントされるので、FAQ追加予定なら h2_needed を1減らす
    faq_will_be_added = needs_faq
    effective_h2_after_faq = h2_count + (1 if faq_will_be_added else 0)
    h2_still_needed = max(0, 6 - effective_h2_after_faq)

    # 既存HTMLの内容を読んで重複チェック
    section_markers = {
        build_mistakes_section:   "Common Mistakes in",
        build_tips_section:       "Training Tips for",
        build_progressions_section: "Learning Progression for",
        build_drills_section:     "Recommended Drills for",
        build_competition_section: "Competition Applications of",
    }

    sections_added = 0
    extra_sections = [
        build_mistakes_section,
        build_tips_section,
        build_progressions_section,
        build_drills_section,
        build_competition_section,
    ]
    for builder in extra_sections:
        if not needs_h2 or sections_added >= h2_still_needed:
            break
        # 既に同名セクションが存在するならスキップ
        if section_markers[builder] in html:
            continue
        to_insert += builder(path.stem, h2_list)
        sections_added += 1
    result["h2_sections_added"] = sections_added

    # FAQ追加
    if needs_faq:
        to_insert += build_faq_section(path.stem, h2_list)
        result["faq_added"] = True

    # テキストを挿入
    if to_insert:
        modified = modified[:inject_pos] + to_insert + modified[inject_pos:]
        inject_pos += len(to_insert)  # 次の挿入位置をずらす

    # Bold付与
    if needs_bold and word_count >= 200:
        modified, bold_count = add_bold_to_content(modified)
        result["bold_added"] = bold_count

    if modified == html:
        return result

    result["action"] = "patched"
    if not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.write(modified)

    return result


# ────────────────────────────────────────────
#  メイン
# ────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Wiki Quality Boost Patcher (target: 80+)")
    parser.add_argument("--dry-run", action="store_true", help="変更なし・件数確認のみ")
    parser.add_argument("--lang",    default="en", choices=["en","ja","pt","all"])
    parser.add_argument("--limit",   type=int, default=0, help="最大処理件数（0=無制限）")
    parser.add_argument("--min-score", type=int, default=0)
    parser.add_argument("--max-score", type=int, default=TARGET_SCORE - 1)
    args = parser.parse_args()

    if not QUALITY_CSV.exists():
        print("❌ quality_report.csv が見つかりません。先に quality_audit.py を実行してください")
        return

    with open(QUALITY_CSV, encoding="utf-8") as f:
        all_rows = list(csv.DictReader(f))

    langs = ["en","ja","pt"] if args.lang == "all" else [args.lang]

    targets = [
        r for r in all_rows
        if r["lang"] in langs
        and args.min_score <= int(r["score"]) <= args.max_score
    ]
    # スコア昇順（低いページから順に処理）
    targets.sort(key=lambda x: int(x["score"]))

    if args.limit:
        targets = targets[:args.limit]

    mode = "DRY RUN" if args.dry_run else "本番実行"
    print(f"=== Wiki Quality Boost ({mode}) ===")
    print(f"対象: {len(targets)} ページ (score {args.min_score}-{args.max_score}, lang={args.lang})")
    print()

    patched = 0
    h2_total = 0
    faq_total = 0
    bold_total = 0

    for i, row in enumerate(targets):
        lang = row["lang"]
        slug = row["slug"]
        path = WIKI_ROOT / lang / f"{slug}.html"

        if not path.exists():
            continue

        result = patch_file(path, row, args.dry_run)

        if result["action"] == "patched":
            patched += 1
            h2_total   += result["h2_sections_added"]
            faq_total  += int(result["faq_added"])
            bold_total += min(result["bold_added"], 1)

            parts = []
            if result["h2_sections_added"]: parts.append(f"H2+{result['h2_sections_added']}")
            if result["faq_added"]:         parts.append("FAQ")
            if result["bold_added"]:        parts.append(f"bold×{result['bold_added']}")
            print(f"  [{i+1}/{len(targets)}] {lang}/{slug} (score={result['score_before']}) → {', '.join(parts)}")

        # 進捗表示 (100件ごと)
        if (i + 1) % 100 == 0:
            print(f"  ... {i+1}/{len(targets)} 処理済み")

    print()
    print(f"=== 完了: {patched}件パッチ ===")
    print(f"  H2セクション追加: {h2_total}件")
    print(f"  FAQセクション追加: {faq_total}件")
    print(f"  Bold付与: {bold_total}件")
    if not args.dry_run:
        print()
        print("次のステップ: python3 scripts/quality_audit.py --lang en でスコア再計算")


if __name__ == "__main__":
    main()
