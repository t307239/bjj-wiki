#!/usr/bin/env python3
"""
patch_content_depth.py — z248: 既存 wiki content を Gemini で深掘り

template FAQ 量産 (z245 失敗) のリベンジ。各 page の既存 content を
Gemini に読み込ませて、page-specific な depth content を「既存セクションの後に」
unique な insight として append する。

具体改善:
  - biomechanics / 物理学的解説の追加
  - common mistakes (page topic specific)
  - 変化技 / counter / progression のヒント
  - 数字 / 統計 / 比較表の埋め込み
  - related techniques の internal link 推奨

⚠️ 設計原則 (z245 学習を反映):
  - template じゃなく page-specific (slug + 既存 h2 list を context に)
  - 既存 content は「触らない」、append only (破壊耐性)
  - idempotent marker `<!-- z248-depth -->` で重複生成防止
  - Gemini fail / quota 超過時は page skip (HTML 壊さない)
  - 100 page batch から段階的に

cost / 時間:
  - Gemini 2.0 Flash: $0.10/1M input, $0.40/1M output
  - 1 page: ~2K input + ~1.5K output = ~$0.001
  - 4,665 page (en+ja+pt) total ~$5、時間 1-2h
  - rate limit 60 req/min なので 1 page 1 sec で進む

setup:
  - 環境変数 GEMINI_API_KEY (既存)
  - python3 -m pip install google-generativeai

使い方:
  python3 scripts/patch_content_depth.py --dry-run                  # 1 page で sample 確認
  python3 scripts/patch_content_depth.py --apply --limit 10         # 10 page test
  python3 scripts/patch_content_depth.py --apply --limit 100        # 100 page batch
  python3 scripts/patch_content_depth.py --apply --lang en          # en/ 全体
  python3 scripts/patch_content_depth.py --apply --lang all         # 全 4,665 page
"""
from __future__ import annotations
import os
import sys
import re
import glob
import time
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEPTH_MARKER = "<!-- z248-depth -->"
DEFAULT_LIMIT = 100
RATE_LIMIT_SLEEP = 1.0  # seconds between Gemini calls


def import_gemini():
    try:
        import google.generativeai as genai
        return genai
    except ImportError:
        print("❌ google-generativeai 未 install")
        print("install: python3 -m pip install --upgrade google-generativeai")
        sys.exit(1)


def extract_page_context(html: str) -> tuple[str, list[str], str]:
    """page から (title, h2_list, body_excerpt) を抽出。"""
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip() if title_match else ""

    h2_matches = re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.IGNORECASE | re.DOTALL)
    h2_list = [re.sub(r"<[^>]+>", "", h).strip() for h in h2_matches[:8]]  # top 8

    # body 抜粋 (最初の 3 paragraph 程度)
    body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.IGNORECASE | re.DOTALL)
    body_text = body_match.group(1) if body_match else html
    body_text = re.sub(r"<[^>]+>", " ", body_text)
    body_text = re.sub(r"\s+", " ", body_text).strip()
    body_excerpt = body_text[:1500]

    return title, h2_list, body_excerpt


def build_prompt(slug: str, lang: str, title: str, h2_list: list[str], body: str) -> str:
    lang_instructions = {
        "en": "Write in clear, technical English. Use BJJ-specific terminology naturally.",
        "ja": "日本語で書く。BJJ 専門用語は柔術コミュニティでの定着形 (アームバー / ガード / スイープ等) を使う。h2/h3 heading および本文を必ず日本語で書くこと。",
        "pt": "Escreva em português brasileiro. Use termos técnicos de BJJ naturalmente. Os títulos h2/h3 e o texto devem estar em português.",
    }
    instr = lang_instructions.get(lang, lang_instructions["en"])

    # z255fff: lang-aware h2/h3 headings (avoid EN heading drift in JA/PT pages)
    headings = {
        "en": {
            "in_depth": f"In-Depth: {title}",
            "biomechanics": "Biomechanics & Physics",
            "mistakes": "Common Mistakes (Specific to This Technique)",
            "variations": "Variations & Counters",
            "drilling": "Drilling Recommendations",
        },
        "ja": {
            "in_depth": f"深掘り解説: {title}",
            "biomechanics": "バイオメカニクスと物理",
            "mistakes": "よくある失敗 (この技特有)",
            "variations": "バリエーションとカウンター",
            "drilling": "ドリル推奨",
        },
        "pt": {
            "in_depth": f"Aprofundamento: {title}",
            "biomechanics": "Biomecânica e Física",
            "mistakes": "Erros Comuns (Específicos desta Técnica)",
            "variations": "Variações e Contra-ataques",
            "drilling": "Recomendações de Treino",
        },
    }
    h = headings.get(lang, headings["en"])

    return f"""You are a BJJ technical writer specialized in adding depth to wiki articles.
You will receive an EXISTING wiki page about a BJJ topic. Your job is to add
500-800 words of UNIQUE, PAGE-SPECIFIC depth content that complements the existing content.

{instr}

## Page Info
- Slug: {slug}
- Title: {title}
- Existing H2 sections: {h2_list}
- Body excerpt: {body[:1500]}

## What to write (output structure, follow exactly)

<section class="z248-depth-content" style="margin:32px 0;padding:20px;background:#0d1b2a;border:1px solid #1e2a3a;border-radius:8px">
  <h2 style="color:#e2e8f0;font-size:1.2rem;font-weight:800;margin-bottom:16px">{h['in_depth']}</h2>

  <h3 style="color:#10b981;font-size:1rem;font-weight:700;margin-top:16px">{h['biomechanics']}</h3>
  <p style="color:#9ca3af;line-height:1.7">[150-200 words explaining the biomechanics — leverage points, force vectors, body positioning. Use specific anatomical terms]</p>

  <h3 style="color:#10b981;font-size:1rem;font-weight:700;margin-top:16px">{h['mistakes']}</h3>
  <ul style="color:#9ca3af;line-height:1.7">
    <li>[Specific mistake 1 with concrete example]</li>
    <li>[Specific mistake 2 with concrete example]</li>
    <li>[Specific mistake 3 with concrete example]</li>
  </ul>

  <h3 style="color:#10b981;font-size:1rem;font-weight:700;margin-top:16px">{h['variations']}</h3>
  <p style="color:#9ca3af;line-height:1.7">[150-200 words on how this technique connects to other techniques — variations, counter-attacks, transitions]</p>

  <h3 style="color:#10b981;font-size:1rem;font-weight:700;margin-top:16px">{h['drilling']}</h3>
  <p style="color:#9ca3af;line-height:1.7">[100-150 words on specific drills, rep counts, training partners' resistance levels]</p>
</section>

## Constraints
- Generate ONLY the <section> HTML above, nothing else
- NO generic advice ("be patient", "drill consistently") — be SPECIFIC to {title}
- NO duplicate content from existing H2 sections: {h2_list}
- Use real BJJ terminology (gi grips, posture, base, etc)
- Keep total under 800 words
- DO NOT use emoji

Output the HTML section now:
"""


def load_api_key() -> str:
    """env var → bjj-wiki/.env → ~/.secrets の優先順で GEMINI_API_KEY を load"""
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key
    for p in [REPO_ROOT / ".env", Path.home() / ".secrets",
              Path.home() / "Claude" / "bjj-wiki" / ".env"]:
        if p.exists():
            for line in p.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def gemini_generate(genai, prompt: str) -> str | None:
    api_key = load_api_key()
    if not api_key:
        print("❌ GEMINI_API_KEY 未設定 (env / .env / ~/.secrets いずれにもない)")
        return None
    try:
        genai.configure(api_key=api_key)
        # z248b: gemini-2.0-flash-exp deprecated 、2.5-flash-lite (free tier 15 RPM) に変更
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        print(f"     ⚠️  Gemini error: {e}")
        return None


def patch_page(genai, fp: Path, lang: str, dry_run: bool) -> bool:
    """Returns True if patched (or skipped because already has marker)."""
    try:
        html = fp.read_text(encoding="utf-8")
    except Exception as e:
        print(f"     ❌ read fail: {e}")
        return False

    # idempotent: marker あれば skip
    if DEPTH_MARKER in html:
        return True

    title, h2_list, body = extract_page_context(html)
    if not title:
        print(f"     ⏭  no <h1>: skip")
        return False

    prompt = build_prompt(fp.stem, lang, title, h2_list, body)

    if dry_run:
        print(f"     📝 (dry-run) prompt {len(prompt)} chars, would call Gemini")
        return True

    generated = gemini_generate(genai, prompt)
    if not generated:
        return False

    # Sanity: <section class="z248-depth-content"> 含むか確認
    if 'z248-depth-content' not in generated:
        # Gemini が prompt 通りに出さなかった、wrap で fallback
        generated = (
            f'<section class="z248-depth-content"><h2>In-Depth: {title}</h2>'
            f'{generated}</section>'
        )

    # Insert marker + generated content before <footer>
    insert = f"\n{DEPTH_MARKER}\n{generated}\n"
    footer_match = re.search(r"<footer\b", html, re.IGNORECASE)
    if footer_match:
        new_html = html[:footer_match.start()] + insert + html[footer_match.start():]
    else:
        # </body> の前に挿入
        body_close = re.search(r"</body>", html, re.IGNORECASE)
        if body_close:
            new_html = html[:body_close.start()] + insert + html[body_close.start():]
        else:
            print(f"     ⚠️  no <footer> or </body>: append at end")
            new_html = html + insert

    try:
        fp.write_text(new_html, encoding="utf-8")
        return True
    except Exception as e:
        print(f"     ❌ write fail: {e}")
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="実書込 (default: dry-run)")
    ap.add_argument("--lang", choices=["en", "ja", "pt", "all"], default="en")
    ap.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    ap.add_argument("--slug", help="single slug test")
    args = ap.parse_args()

    genai = import_gemini() if args.apply else None

    langs = ["en", "ja", "pt"] if args.lang == "all" else [args.lang]
    total_done = 0
    total_skip = 0
    total_fail = 0

    for lang in langs:
        lang_dir = REPO_ROOT / lang
        if not lang_dir.exists():
            continue
        files = sorted(lang_dir.glob("*.html"))
        if args.slug:
            files = [f for f in files if f.stem == args.slug]

        print(f"━━━ {lang}/ ({len(files)} files、limit={args.limit}) ━━━")
        for i, fp in enumerate(files):
            if total_done >= args.limit:
                break
            print(f"  [{i+1}/{len(files)}] {lang}/{fp.stem}")
            if patch_page(genai, fp, lang, dry_run=not args.apply):
                if args.apply:
                    total_done += 1
                    time.sleep(RATE_LIMIT_SLEEP)  # rate limit safety
                else:
                    total_done += 1
            else:
                total_fail += 1
        if total_done >= args.limit:
            break

    print()
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    mode = "APPLIED" if args.apply else "DRY-RUN (use --apply to write)"
    print(f"📊 [{mode}] done={total_done}, skip={total_skip}, fail={total_fail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
