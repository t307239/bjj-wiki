#!/usr/bin/env python3
"""
fix_long_descriptions.py — z260v Phase B Round 3

Compress meta descriptions over Google SERP limits:
  - EN limit: 160 chars (Google truncates at ~155-160 chars on desktop)
  - JA limit: 130 chars (Japanese characters are wider visually)

Two categories:
  A. EN athlete-* (formulaic): "X 'Y' is an elite BJJ competitor known for ..."
     → "X 'Y' is known for ..." (saves 22 chars)
  B. EN/JA non-athlete: free-form, manual or sentence-boundary truncate.

idempotent: re-running only modifies if still over limit.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
META_DESC = re.compile(r'(<meta\s+name="description"\s+content=")([^"]*)("[^>]*>)', re.IGNORECASE)
OG_DESC = re.compile(r'(<meta\s+property="og:description"\s+content=")([^"]*)("[^>]*>)', re.IGNORECASE)

# Curated overrides for non-athlete pages (more careful editing to preserve meaning)
NON_ATHLETE_OVERRIDES: dict[str, str] = {
    "en/armbar.html":
        "Master the BJJ armbar with precise biomechanics for white belts. Learn safe execution, common mistakes, and effective drills.",
    "en/balloon-sweep.html":
        "Master the Balloon Sweep in BJJ. Precise biomechanical guide for white belts: grips, body positioning, and common pitfalls.",
    "en/bjj-andre-galvao-system.html":
        "Analyze André Galvão's complete BJJ system: butterfly guard, systematic back takes, top pressure, competition strategy.",
    "en/bjj-blue-belt-curriculum.html":
        "Complete BJJ blue belt curriculum: essential techniques, training strategy, and a step-by-step path from white to purple belt.",
    "en/bjj-guard-passing-chess.html":
        "Learn the chess-like strategic thinking behind BJJ guard passing: read opponent intentions, chain techniques, dominate control.",
    "en/rear-naked-choke.html":
        "Master the Rear Naked Choke with precise biomechanics for white belts. Grips, execution, warnings, and essential drills.",
    "en/russian-tie.html":
        "Master the Russian Tie takedown in BJJ. Biomechanically precise instructions for white belts to execute safely and effectively.",
    "en/sitting-guard.html":
        "Master Sitting Guard in BJJ. Precise biomechanical guide for white belts: setup, common errors, distance control, and drills.",
    "en/x-pass.html":
        "Master the X-Pass in Brazilian Jiu-Jitsu. Biomechanically accurate instructions for white belts: safe execution and common pitfalls.",
}


def truncate_at_sentence(desc: str, limit: int) -> str | None:
    """Truncate at last sentence boundary that fits under limit.
    Works for PT and JA. Use 。 for JA sentence end, . for Roman.
    """
    # Detect English residue contamination first (pattern: '<word>...)
    # like JA-after-PT periods. Drop trailing English fragment.
    m = re.search(r"\.\s*'\w[^']*$", desc)
    if m:
        desc = desc[: m.start()] + "."

    # Split on sentence-end punctuation
    pieces = re.split(r"(?<=[\.。!?！？])\s+", desc)
    acc = ""
    for p in pieces:
        cand = (acc + " " + p).strip() if acc else p.strip()
        if len(cand) <= limit:
            acc = cand
        else:
            break
    # Prefer descriptions >= 90 chars (Google snippet target ~ 120-160).
    # If sentence boundary truncation is too aggressive, fall through to hard-cut.
    if acc and 90 <= len(acc) <= limit:
        return acc
    # Fallback: hard cut at word boundary
    if len(desc) > limit:
        cut = desc[: limit - 1]
        # Trim back to last space
        if " " in cut[-30:]:
            cut = cut.rsplit(" ", 1)[0]
        cut = cut.rstrip(",;:") + "."
        if 40 <= len(cut) <= limit:
            return cut
    return None


def compress_athlete_en(desc: str, limit: int) -> str | None:
    """Apply formula compression to EN athlete description, preserving as
    much info (titles, technique list) as possible.
    Pattern: "X 'Y' is an elite BJJ competitor known for A. B" → "X 'Y' is known for A. B"
    """
    new = re.sub(
        r"\bis an elite BJJ competitor known for\b",
        "is known for",
        desc,
        count=1,
    )
    if new == desc:
        # Fallback for non-formulaic descriptions
        return None
    if len(new) <= limit:
        return new
    # Still too long; trim trailing achievements by shortest amount.
    # Achievement format ends like: "; <name> Champion N×; <name> Champion N×."
    # Drop one achievement clause at a time from the end.
    while len(new) > limit:
        m = re.search(r";\s*[^;]+\.\s*$", new)
        if not m:
            break
        new = new[: m.start()].rstrip(" ,;") + "."
    # If still too long, remove parenthetical clauses
    while len(new) > limit:
        m = re.search(r"\s*\([^)]*\)", new)
        if not m:
            break
        new = (new[: m.start()] + new[m.end():]).strip()
    # Final fallback: trim at last sentence boundary that fits
    if len(new) > limit:
        sentences = re.split(r"(?<=\.)\s+", new)
        acc = ""
        for s in sentences:
            cand = (acc + " " + s).strip() if acc else s
            if len(cand) <= limit:
                acc = cand
            else:
                break
        if acc:
            new = acc
    if len(new) <= limit:
        return new
    return None


def fix_file(fp: Path, limit_en: int = 160, limit_ja: int = 130) -> bool:
    html = fp.read_text(encoding="utf-8")
    rel = fp.relative_to(ROOT)
    is_ja = rel.parts and rel.parts[0] == "ja"
    is_athlete = fp.stem.startswith("athlete-")

    m = META_DESC.search(html)
    if not m:
        return False
    desc = m.group(2)
    limit = limit_ja if is_ja else limit_en
    if len(desc) <= limit:
        return False

    new_desc: str | None = None
    rel_str = rel.as_posix()

    # Override has priority
    if rel_str in NON_ATHLETE_OVERRIDES:
        new_desc = NON_ATHLETE_OVERRIDES[rel_str]
    # EN athlete formula
    elif is_athlete and not is_ja:
        new_desc = compress_athlete_en(desc, limit)
    # PT non-athlete: smart sentence truncation
    elif rel.parts[0] == "pt" and not is_athlete:
        new_desc = truncate_at_sentence(desc, limit)
    # JA non-athlete: smart sentence truncation (130 char)
    elif is_ja and not is_athlete:
        new_desc = truncate_at_sentence(desc, limit)

    if not new_desc:
        return False
    if len(new_desc) > limit:
        return False  # don't write a fix that doesn't fix

    # Write meta description
    new_html = html[: m.start(2)] + new_desc + html[m.end(2):]
    # Sync og:description
    og = OG_DESC.search(new_html)
    if og and og.group(2) == desc:
        new_html = new_html[: og.start(2)] + new_desc + new_html[og.end(2):]
    fp.write_text(new_html, encoding="utf-8")
    print(f"  FIX {rel}: {len(desc)} → {len(new_desc)}")
    return True


def main() -> int:
    fixed = 0
    for lang in ("en", "ja", "pt"):
        d = ROOT / lang
        for fp in sorted(d.glob("*.html")):
            if fix_file(fp):
                fixed += 1
    print(f"\nTotal fixed: {fixed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
