#!/usr/bin/env python3
"""
scan_pt_english_mixing.py — z254: PT wiki 英語混入 検出 (J-1 pt版)

ポルトガル語 wiki page の <title>/<h1>/<meta description> を scan、
英語のままになってる page を検出。

検出 logic (PT 版):
  - Portuguese は Latin alphabet なので char で判別困難
  - 但し PT 固有のアクセント文字 (ã â ç é ê í ó ô õ ú) を含む = PT 確定
  - 英語のみ含み、PT アクセント無し → CRITICAL (英語混入疑い)

出力: pt_english_mixing_report.csv
"""
from __future__ import annotations
import os
import re
import csv
import sys
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parent.parent
PT_DIR = REPO_ROOT / "pt"
OUT_CSV = REPO_ROOT / "pt_english_mixing_report.csv"

# PT 固有のアクセント文字
PT_ACCENT_RE = re.compile(r"[ãâáàçéêíóôõúÃÂÁÀÇÉÊÍÓÔÕÚ]")
ENGLISH_RE = re.compile(r"\b[A-Za-z]{5,}\b")

# 英語と PT で共通の単語 (allowed、検出から除外)
COMMON_WORDS = {
    "BJJ", "Jiu", "Jitsu", "MMA", "ADCC", "IBJJF", "EBI",
    "Brazilian", "Gracie", "Wiki",
    # PT 単語で 5 文字以上の一般語 (英語と判定されないよう)
    "guarda", "técnica", "armbar", "kimura", "triangle", "passagem",
    "ataque", "defesa", "completa", "técnicas", "ensina", "domine",
    "pratica", "iniciante", "branco", "blue", "purple", "black",
    "submissão", "como", "mestre", "guia", "fundamental", "moderna",
}

# z254d: PT 固有マーカー単語 — これらが含まれていれば「PT として書かれてる」と判定
# (アクセント無しでも自然な PT phrase を救済)
PT_MARKER_WORDS = {
    # 一般 PT 名詞 / 動詞
    "sobre", "regras", "chave", "guarda", "guia", "atletas", "atleta",
    "pegar", "raspagem", "passagem", "passar", "ataque", "defesa",
    "completa", "completo", "domine", "ensina", "como", "melhor",
    "melhores", "mestre", "fundamentos", "fundamental",
    "iniciante", "iniciantes", "tornozelo", "joelho", "perna", "braço",
    "costas", "montada", "estrangulamento", "finalizacao", "queda",
    "kimono", "rashguard", "protetores", "instrucionais", "joelheiras",
    "bolsa", "bucal", "ouvido", "cabeça", "campeao", "campeã",
    "treino", "técnica", "tecnica", "academia", "faixa", "graduacao",
    "moderna", "moderno", "história", "historia", "estilo", "fluxo",
    "essencial", "suplemento", "alongamento", "dieta", "nutricao",
    "preto", "azul", "marrom", "roxa", "branca", "lesao", "lesão",
    "evitar", "comum", "comuns", "principal", "principais", "domínio",
    "dominio", "explicado", "explicada",
    # よく title で使う PT preposition / connector (長め)
    "sistema", "vantagem", "vantagens", "controle", "axila", "técnicas",
    "tecnicas", "metodos", "métodos", "movimentos", "exercicios",
    "exercícios", "pegada", "pegadas", "transicao", "transição",
    "transicoes", "transições", "posicao", "posição", "posicoes",
    "posições", "estrategia", "estratégia", "estrategias", "estratégias",
    "treinamento", "competicao", "competição", "torneio", "torneios",
    "regulamento", "categoria", "categorias", "graduação", "kimonos",
    "para", "pelo", "pela", "pelos", "pelas",  # PT prepositions (4 chars but distinctive)
    "neste", "nesta", "estes", "estas", "deste", "desta",
    "feita", "feito", "feitas", "feitos",
    "explicada", "explicado", "explicadas", "explicados",
    "ensinada", "ensinado", "ensinadas", "ensinados",
}


def extract_field(html: str, pattern: str) -> str:
    m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    return re.sub(r"<[^>]+>", "", m.group(1)).strip()


def detect_english(text: str) -> list[str]:
    if not text:
        return []
    matches = ENGLISH_RE.findall(text)
    return [m for m in matches if m.lower() not in {a.lower() for a in COMMON_WORDS}]


def has_pt_accent(text: str) -> bool:
    return bool(PT_ACCENT_RE.search(text))


def has_pt_marker(text: str) -> bool:
    """z254d: アクセント無しでも PT marker word があれば PT 認定"""
    if not text:
        return False
    words = re.findall(r"[A-Za-zÀ-ÿ]+", text.lower())
    if any(w in PT_MARKER_WORDS for w in words):
        return True
    # PT 固有 phrase pattern: "X de Y", "no BJJ", "para BJJ", "Choke de X"
    if re.search(r"\b(de|do|da|dos|das|no|na|nos|nas|em|por)\b\s+\b[A-Za-zÀ-ÿ]", text, re.IGNORECASE):
        return True
    return False


def is_pt(text: str) -> bool:
    """PT として書かれていると判定 (accent OR marker word)"""
    return has_pt_accent(text) or has_pt_marker(text)


def main() -> int:
    if not PT_DIR.exists():
        print(f"❌ {PT_DIR} not found")
        return 1

    files = sorted(PT_DIR.glob("*.html"))
    print(f"📂 pt/ — {len(files)} ファイル scan 開始")

    issues = []
    severity_counter = Counter()

    for fp in files:
        try:
            html = fp.read_text(encoding="utf-8")
        except Exception:
            continue

        title = extract_field(html, r"<title[^>]*>(.*?)</title>")
        h1 = extract_field(html, r"<h1[^>]*>(.*?)</h1>")
        desc_m = re.search(
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
            html, re.IGNORECASE,
        )
        desc = desc_m.group(1) if desc_m else ""

        # CRITICAL: title または h1 が PT 認定 (accent or marker) されない + 英語含む
        # z254d: accent 無しでも marker word (sobre, regras, chave 等) があれば PT 扱い
        # athlete-* slug の場合 title/h1 が固有名詞のみ → OK と判定して除外
        is_athlete_page = fp.stem.startswith("athlete-")

        def proper_noun_only(s: str) -> bool:
            """すべての単語が大文字始まり (人名 pattern)、かつ PT 認定無し"""
            if not s:
                return False
            # "| BJJ Wiki" 等の suffix 除外
            core = re.sub(r"\s*\|\s*BJJ\s*Wiki\s*$", "", s).strip()
            words = core.split()
            if not words or len(words) > 4:
                return False
            return (
                all((w[0].isupper() if w and w[0].isalpha() else True) for w in words)
                and not is_pt(s)
            )

        title_no_pt = not is_pt(title) and bool(detect_english(title))
        if is_athlete_page and proper_noun_only(title):
            title_no_pt = False  # athlete page で固有名詞 title → OK
        h1_no_pt = bool(h1) and not is_pt(h1) and bool(detect_english(h1))
        if is_athlete_page and proper_noun_only(h1):
            h1_no_pt = False  # athlete page で固有名詞 h1 → OK
        desc_no_pt = not is_pt(desc) and bool(detect_english(desc))

        sev = ""
        if title_no_pt or h1_no_pt:
            sev = "CRITICAL"
        elif desc_no_pt:
            sev = "INFO"

        if sev:
            severity_counter[sev] += 1
            issues.append({
                "slug": fp.stem,
                "severity": sev,
                "title": title[:80],
                "title_english": ",".join(detect_english(title)[:5]),
                "h1": h1[:80],
                "h1_english": ",".join(detect_english(h1)[:5]),
                "desc": desc[:120],
                "desc_english": ",".join(detect_english(desc)[:5]),
            })

    if issues:
        with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(issues[0].keys()))
            writer.writeheader()
            writer.writerows(issues)
        print(f"✅ 出力: {OUT_CSV}")

    print()
    print("─" * 60)
    print(f"📊 結果 (1,566 pt page 中):")
    print(f"  🔴 CRITICAL (title/h1 に PT アクセントなし+英語): {severity_counter['CRITICAL']} 件")
    print(f"  🟢 INFO (meta だけ英語): {severity_counter['INFO']} 件")
    print(f"  ✅ 健全: {len(files) - sum(severity_counter.values())} 件")

    if issues:
        print()
        print("CRITICAL sample (top 5):")
        critical = [i for i in issues if i["severity"] == "CRITICAL"][:5]
        for i in critical:
            print(f"  - pt/{i['slug']}: title='{i['title'][:50]}' / h1='{i['h1'][:50]}'")

    return 0


if __name__ == "__main__":
    sys.exit(main())
