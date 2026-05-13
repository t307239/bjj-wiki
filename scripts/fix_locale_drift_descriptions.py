#!/usr/bin/env python3
"""
fix_locale_drift_descriptions.py — z260u Phase B Round 2

Critical silent SEO bug: 5 JA pages + 15 PT pages have meta description
either entirely in English OR with English residue mixed into JA text.
Google SERP for ja-JP / pt-BR users sees these English snippets — page
positioning + CVR severely degraded.

Detection: lang-purity audit (B-2 round).
  - JA: ASCII-only or mixed JA + trailing English residue
  - PT: no PT markers + English keywords present

Fix: per-page hand-curated localized translations grounded in title/h1.
   (script-driven but with curated content, not auto-translation)

idempotent: re-running only writes if current desc still matches the bad pattern.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Translations — curated to match title/h1 of each page, keep BJJ terms in katakana,
# stay under 120 chars (JA) / 160 chars (PT) for SERP fit.
TRANSLATIONS: dict[str, str] = {
    # JA — fully replace English / mixed descriptions
    "ja/bjj-dlr-back-take-guide.html":
        "デラヒーバガードからのバックテイク移行を解説。ドミナントなポジショニングとコントロールシステムを学びましょう。",
    "ja/bjj-elbow-control-bjj.html":
        "BJJ（ブラジリアン柔術）のエルボーコントロールを解説。相手の肘をコントロールして有利なポジションとサブミッションを狙いましょう。",
    "ja/bjj-long-game-bjj.html":
        "BJJのロングゲーム戦略を解説。長期的なスキル開発とキャリアプランニングで上達を加速させる方法を学びましょう。",
    "ja/bjj-terminology.html":
        "BJJ用語集。ポルトガル語・日本語（柔道由来）・英語スラングが混ざる柔術独特のボキャブラリーを50語以上で解説。",
    "ja/bjj-marcelo-garcia-system-guide.html":
        "マルセロ・ガルシアのシステムを解説。アグレッシブなパッシングと上体プレッシャー、独自のポジションから繰り出すレッグロックアタック、技術的制御を維持したガードパッシングが特徴。",

    # PT — fully replace English descriptions
    "pt/bjj-back-escape-guide.html":
        "Aprenda a escapar da posição de costas (back mount) no Jiu-Jitsu Brasileiro. Frames, ponte e restauração de guarda explicados.",
    "pt/bjj-collar-sleeve-guard.html":
        "Domine a guarda collar and sleeve (gola-manga). Aprenda setup, raspagens e ameaças de finalização nesta guarda clássica.",
    "pt/bjj-guard-pull-strategy.html":
        "Estratégia de guard pull (puxar guarda) em competição. Aprenda timing e técnicas seguras de puxada de guarda no Jiu-Jitsu.",
    "pt/bjj-mata-leao-guide.html":
        "Mata leão (rear-naked choke) avançado desde as costas. Aprenda mecânica e setup desta finalização clássica do Jiu-Jitsu Brasileiro.",
    "pt/bjj-rdlr-back-take-guide.html":
        "Transição do Reverse De La Riva para back control no Jiu-Jitsu Brasileiro. Aprenda sequenciamento e sistema de pegadas (grips).",
    "pt/bjj-rdlr-entries-guide.html":
        "Aprenda entradas para a guarda Reverse De La Riva a partir de múltiplas posições e transições no Jiu-Jitsu Brasileiro.",
    "pt/bjj-rdlr-leg-attacks.html":
        "Ataques de pernas a partir do Reverse De La Riva. Domine heel hooks e sistemas avançados de leg lock no Jiu-Jitsu Brasileiro.",
    "pt/bjj-rdlr-sweeps-guide.html":
        "Execute raspagens (sweeps) poderosas a partir do Reverse De La Riva, usando posicionamento de quadril e sistemas de controle de pernas.",
    "pt/bjj-rdlr-x-guard-combo.html":
        "Combine Reverse De La Riva com X-guard para raspagens avançadas e oportunidades de ataques de pernas no Jiu-Jitsu Brasileiro.",
    "pt/bjj-seat-belt-control-guide.html":
        "Aprenda o seat belt control desde a posição de costas. Domine o posicionamento dos braços e a mecânica de controle no Jiu-Jitsu.",
    "pt/bjj-side-control-escape-guide.html":
        "Estratégias para escapar do side control (cem quilos). Aprenda a recuperar guarda e reverter posições no Jiu-Jitsu Brasileiro.",
    "pt/bjj-sit-up-guard-guide.html":
        "Aprenda a sit up guard e a combat base guard. Mantenha distância e execute raspagens a partir desta guarda no Jiu-Jitsu Brasileiro.",
    "pt/bjj-spider-guard-system.html":
        "Sistema spider guard (guarda aranha) explicado. Domine o controle com pés na gola e múltiplas raspagens no Jiu-Jitsu Brasileiro.",
    "pt/bjj-stiff-arm-frames.html":
        "Aprenda stiff arm frames (frames de braço estendido) para controlar distância, gerenciar pressão e prevenir finalizações no BJJ.",
    "pt/bjj-tripod-sweep-guide.html":
        "Domine a tripod sweep (raspagem de tripé) a partir da open guard. Aprenda controle em pé e mecânica de raspagem no Jiu-Jitsu Brasileiro.",
}


def find_meta(content: str) -> tuple[str, int, int] | None:
    """Returns (current_desc, start_idx, end_idx) of meta description content."""
    m = re.search(r'(<meta\s+name="description"\s+content=")([^"]*)("[^>]*>)', content, re.IGNORECASE)
    if not m:
        return None
    return m.group(2), m.start(2), m.end(2)


def find_og_desc(content: str) -> tuple[str, int, int] | None:
    m = re.search(r'(<meta\s+property="og:description"\s+content=")([^"]*)("[^>]*>)', content, re.IGNORECASE)
    if not m:
        return None
    return m.group(2), m.start(2), m.end(2)


def looks_bad_ja(desc: str) -> bool:
    """JA desc is bad if: 100% ASCII OR has 5+ English words after JA text."""
    if not desc:
        return False
    en_letters = sum(1 for c in desc if c.isascii() and c.isalpha())
    total_letters = sum(1 for c in desc if c.isalpha())
    if total_letters == 0:
        return False
    en_ratio = en_letters / total_letters
    if en_ratio > 0.5:
        return True
    # Mixed: detect English residue at end
    if re.search(r"\b(positional|positioning|advantage|technique|submissions|control|guards?)\b\s*\w*\s*$", desc, re.IGNORECASE):
        return True
    return False


def looks_bad_pt(desc: str) -> bool:
    if not desc:
        return False
    PT_MARKER = re.compile(r"(ção|ções|guarda|aprenda|conheça|técnica|posição|jiu-jitsu)", re.IGNORECASE)
    EN_ONLY = re.compile(r"\b(the|with|from|your|that|this|here|these|those|positioning|technique|opponent|guard|control|learn|master)\b", re.IGNORECASE)
    if not PT_MARKER.search(desc) and len(EN_ONLY.findall(desc)) >= 2:
        return True
    return False


def main() -> int:
    fixed: list[str] = []
    skipped_clean: list[str] = []
    missing: list[str] = []

    for rel, new_desc in TRANSLATIONS.items():
        fp = ROOT / rel
        if not fp.exists():
            missing.append(rel)
            continue
        html = fp.read_text(encoding="utf-8")
        current = find_meta(html)
        if not current:
            print(f"  SKIP no description: {rel}")
            continue
        cur_desc, s, e = current
        is_ja = rel.startswith("ja/")
        bad = looks_bad_ja(cur_desc) if is_ja else looks_bad_pt(cur_desc)
        if not bad:
            skipped_clean.append(rel)
            continue
        # Replace name="description" content
        new_html = html[:s] + new_desc + html[e:]
        # Also replace og:description if it matches the bad one
        og = find_og_desc(new_html)
        if og:
            og_desc, og_s, og_e = og
            if og_desc == cur_desc:
                new_html = new_html[:og_s] + new_desc + new_html[og_e:]
        fp.write_text(new_html, encoding="utf-8")
        fixed.append(rel)
        print(f"  FIX {rel}: new_desc[:80]={new_desc[:80]}")

    print(f"\nFixed: {len(fixed)} | Already clean (skipped): {len(skipped_clean)} | Missing: {len(missing)}")
    if skipped_clean:
        print("  Skipped (already clean):", skipped_clean)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
