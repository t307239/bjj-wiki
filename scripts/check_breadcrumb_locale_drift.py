#!/usr/bin/env python3
"""
check_breadcrumb_locale_drift.py — z255xx: 21st bjj-wiki lint

JA/PT page で <div class="breadcrumb"> last crumb が EN 残留していないか catch。

旧 silent UX bug: 987 page で `BJJ Wiki › Tomoe Nage for BJJ` 等 EN 残留
(z255xx fix_breadcrumb_locale_drift.py で 1,593 page を h1 と sync)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# BJJ proper noun whitelist (EN でも OK な技名)
BJJ_PROPER_NOUNS = {
    "Berimbolo", "Kimura", "Omoplata", "Americana", "Ezekiel",
    "Granby Roll", "Heel Hook", "Toe Hold", "Knee Bar",
    "Gogoplata", "Imanari Roll",
}


def check_page(fp: Path, lang: str) -> str | None:
    if lang == "en":
        return None
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception:
        return None
    if "noindex" in html[:1500]:
        return None

    bc_m = re.search(r'<div class="breadcrumb">(.*?)</div>', html, re.DOTALL)
    if not bc_m:
        return None

    crumb = bc_m.group(1)
    last_match = re.search(r'›\s*([^›]+?)\s*$', crumb.replace('\n', ' '))
    if not last_match:
        return None
    last = last_match.group(1).strip()

    # Strip HTML tags
    last_text = re.sub(r'<[^>]+>', '', last).strip()

    if not last_text:
        return None

    # Brand suffix leak in breadcrumb
    if re.search(r'\|\s*BJJ\s*Wiki', last_text, re.IGNORECASE):
        return f"brand suffix leaked: '{last_text[:60]}'"

    # BJJ proper noun OK
    if last_text in BJJ_PROPER_NOUNS:
        return None

    # Locale-specific check
    if lang == "ja":
        if re.search(r'[A-Za-z]', last_text) and not re.search(r'[ぁ-んァ-ヶー一-龯]', last_text):
            return f"EN-only crumb: '{last_text[:60]}'"
    elif lang == "pt":
        # Skip if it has any PT marker (broader list to reduce false positives)
        # PT diacritics, common words, verb forms, BR-specific tokens
        text_lower = last_text.lower()
        pt_markers = (
            # Diacritics
            'ã', 'á', 'â', 'ç', 'é', 'ê', 'í', 'ó', 'ô', 'õ', 'ú',
            # Common words / prepositions / articles
            'ção', 'ões', 'guarda', 'jiu', 'técnica', ' do ', ' da ', ' de ',
            ' no ', ' os ', ' as ', ' um ', ' uma ', ' para ', ' em ',
            ' na ', ' nas ', ' nos ', ' sua ', ' seu ', ' sem ',
            'qual ', ' vs.', 'entre',
            # Verb forms (-ando/-endo/-indo gerunds, -ado/-ido past participles)
            'ando', 'endo', 'indo', 'iz ', 'ido ', 'ada ', 'ado ',
            'domine', 'aprenda', 'defenda', 'controle', 'defesa', 'finaliz',
            'treinar', 'lutar', 'comp',
            # Nouns/adjectives common to BJJ PT content
            'regras', 'completo', 'completa', 'guia', 'sistema', 'queda',
            'raspagem', 'passagem', 'estrang', 'chave', 'ataque', 'contra',
            'finalização', 'iniciante', 'avançado', 'fundamento',
            'pegada', 'lutas', 'energia', 'requisitos', 'faixa', 'azul',
            'roxa', 'marrom', 'preta', 'branca', 'kimono', 'costas',
            'cotovelo', 'joelho', 'sobrecarga', 'progressiva',
            'filosofia', 'categoria', 'arco', 'flecha', 'brabo',
            'entrada', 'escudo', 'gerenciando',
        )
        has_pt = any(m in text_lower for m in pt_markers)
        if not has_pt and len(last_text) > 20:
            return f"likely EN-only crumb: '{last_text[:60]}'"

    return None


def main():
    failed = []
    for lang in ("ja", "pt"):
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        for fp in sorted(lang_dir.glob("*.html")):
            err = check_page(fp, lang)
            if err:
                failed.append((str(fp.relative_to(REPO_ROOT)), err))

    print(f"❌ Pages with EN-residue breadcrumb in JA/PT: {len(failed)}")
    for fp, err in failed[:20]:
        print(f"  {fp}: {err}")
    if len(failed) > 20:
        print(f"  ... and {len(failed) - 20} more")

    if "--ci" in sys.argv:
        sys.exit(1 if failed else 0)
    if not failed:
        print("\n✅ All JA/PT breadcrumbs properly localized.")


if __name__ == "__main__":
    main()
