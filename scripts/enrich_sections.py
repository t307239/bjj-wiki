#!/usr/bin/env python3
"""
enrich_sections.py — Gemini無料枠でFAQ・Difficulty・Belt Levelを既存Wikiページに注入

【戦略】
  - フルregen（高コスト）ではなく、欠落セクションだけをGeminiに生成させてHTMLに注入
  - 1コールで FAQ(3問) + Difficulty + Belt Level を一括取得（軽量プロンプト ~200tok入力/~400tok出力）
  - 進捗ファイルで冪等性を保証。途中停止→再実行で安全に続行

【Gemini Free Tier制約】
  gemini-2.0-flash: 15 RPM, 1,500 RPD, 1M TPM
  → 1バッチ = 最大500ページ/実行（安全マージン込み）

【使い方】
  python3 enrich_sections.py                     # ja 500ページ処理
  python3 enrich_sections.py --lang en           # 英語版
  python3 enrich_sections.py --limit 10          # テスト用に10ページだけ
  python3 enrich_sections.py --dry-run           # API呼ばずにターゲット一覧表示
  python3 enrich_sections.py --reset-progress    # 進捗リセット

【前提】
  ~/Claude/bjj-wiki/.env または ~/.secrets に GEMINI_API_KEY を記載
"""

import os, sys, re, json, time, argparse, urllib.request, urllib.error
from pathlib import Path

# ── Config ──
WIKI_ROOT = Path(__file__).resolve().parent.parent
PROGRESS_FILE = WIKI_ROOT / "scripts" / ".enrich_progress.json"
DEFAULT_LANG = "ja"
DEFAULT_LIMIT = 1600
RPM_LIMIT = 12          # 15 RPM free tier, 12 for safety
SLEEP_BETWEEN = 60 / RPM_LIMIT  # ~5s between calls
MAX_RETRIES = 3

# ── API Key ──
def load_api_key():
    """Load GEMINI_API_KEY from multiple sources"""
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key
    for p in [WIKI_ROOT / ".env", Path.home() / ".secrets", Path.home() / "Claude" / "bjj-wiki" / ".env"]:
        if p.exists():
            for line in p.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""

GEMINI_API_KEY = load_api_key()

# ── Gemini Call ──
def call_gemini(prompt):
    """Call Gemini 2.0 Flash (free tier) with fallback models"""
    if not GEMINI_API_KEY:
        print("[ERROR] GEMINI_API_KEY not found")
        return None

    models = [
        ("gemini-2.5-flash-lite", "v1beta"),   # 無料tier: 15 RPM, 1000 RPD
        ("gemini-2.5-flash-lite", "v1"),
        ("gemini-2.5-flash", "v1beta"),         # 無料tier: 5 RPM, 100 RPD
        ("gemini-2.5-flash", "v1"),
    ]
    data = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.5, "maxOutputTokens": 1024}
    }).encode()

    for model, api_ver in models:
        url = f"https://generativelanguage.googleapis.com/{api_ver}/models/{model}:generateContent?key={GEMINI_API_KEY}"
        for attempt in range(MAX_RETRIES):
            try:
                req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=30) as res:
                    result = json.loads(res.read())
                    text = result["candidates"][0]["content"]["parts"][0]["text"]
                    return text
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait = 30 * (attempt + 1)
                    print(f"  [429] Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                elif e.code == 503:
                    time.sleep(10)
                else:
                    print(f"  [{model}] HTTP {e.code} → next model")
                    break
            except Exception as e:
                print(f"  [{model}] Error: {e}")
                break
    return None

# ── Prompt ──
def build_enrich_prompt(tech_name, lang):
    lang_instructions = {
        "en": "Write everything in English.",
        "ja": "すべて日本語で書いてください。",
        "pt": "Escreva tudo em Português brasileiro.",
    }
    return f"""You are a BJJ black belt instructor. {lang_instructions[lang]}

For the technique "{tech_name}", generate:
1. difficulty_level: One of "Beginner", "Intermediate", "Advanced", "Expert"
2. belt_level: One of "white", "blue", "purple", "brown", "black"
3. stars: Difficulty stars like "★★☆☆☆" (1-5 filled stars ★, rest ☆)
4. faq: 3 unique questions that real BJJ students Google about this technique.
   Each has a question and a precise 2-3 sentence answer.

Return ONLY valid JSON (no markdown, no explanation):
{{"difficulty_level": "...", "belt_level": "...", "stars": "...", "faq": [{{"q": "...", "a": "..."}}, {{"q": "...", "a": "..."}}, {{"q": "...", "a": "..."}}]}}"""

# ── HTML Injection ──
def inject_faq(content, faq_items, lang):
    """Inject FAQ section before footer"""
    faq_title = {"en": "Frequently Asked Questions", "ja": "よくある質問", "pt": "Perguntas Frequentes"}[lang]

    details_html = ""
    for item in faq_items:
        q = item.get("q", "")
        a = item.get("a", "")
        if q and a:
            details_html += f"""    <details><summary>{q}</summary><p>{a}</p></details>\n"""

    faq_section = f"""<section class="faq-section">
  <h2>{faq_title}</h2>
{details_html}</section>
"""
    # Insert before footer
    footer_pos = content.rfind("<footer")
    if footer_pos < 0:
        footer_pos = content.rfind("</body")
    if footer_pos < 0:
        return content  # Can't inject safely

    return content[:footer_pos] + faq_section + "\n" + content[footer_pos:]


def inject_difficulty(content, belt_level, stars, difficulty_level):
    """Inject difficulty bar after first h1"""
    belt_colors = {
        "white": ("#e2e2ee", "#111"),
        "blue": ("#2563eb", "#fff"),
        "purple": ("#7c3aed", "#fff"),
        "brown": ("#92400e", "#fff"),
        "black": ("#111", "#fff"),
    }
    bg, fg = belt_colors.get(belt_level, ("#2563eb", "#fff"))

    badge_html = (
        f'<span class="belt belt-{belt_level}">'
        f'🥋 {belt_level.title()}</span>'
    )
    diff_html = f"""<div class="difficulty-bar">
  {badge_html}
  <span class="stars">{stars}</span>
  <span class="diff-label">{difficulty_level}</span>
</div>"""

    # Insert after closing </h1>
    h1_end = re.search(r"</h1>", content)
    if not h1_end:
        return content

    insert_pos = h1_end.end()
    # Skip any whitespace/newline
    while insert_pos < len(content) and content[insert_pos] in "\n\r ":
        insert_pos += 1

    return content[:h1_end.end()] + "\n" + diff_html + "\n" + content[h1_end.end():]


def inject_faq_jsonld(content, faq_items, page_url):
    """Inject FAQPage JSON-LD for rich snippets"""
    faq_entities = []
    for item in faq_items:
        q = item.get("q", "")
        a = item.get("a", "")
        if q and a:
            # Escape for JSON
            q_esc = q.replace('"', '\\"')
            a_esc = a.replace('"', '\\"')
            faq_entities.append(
                f'{{"@type":"Question","name":"{q_esc}","acceptedAnswer":{{"@type":"Answer","text":"{a_esc}"}}}}'
            )

    if not faq_entities:
        return content

    jsonld = (
        '<script type="application/ld+json">'
        '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":['
        + ",".join(faq_entities)
        + "]}</script>"
    )

    # Insert before </head>
    head_end = content.find("</head>")
    if head_end < 0:
        return content

    return content[:head_end] + jsonld + "\n" + content[head_end:]

# ── Progress Tracking ──
def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return {"completed": {}}

def save_progress(progress):
    PROGRESS_FILE.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")

# ── Target Detection ──
def find_targets(lang, limit):
    """Find pages missing FAQ or Difficulty"""
    lang_dir = WIKI_ROOT / lang
    if not lang_dir.is_dir():
        print(f"[ERROR] Directory {lang_dir} not found")
        return []

    progress = load_progress()
    completed = set(progress.get("completed", {}).get(lang, []))

    targets = []
    for f in sorted(lang_dir.iterdir()):
        if not f.suffix == ".html":
            continue
        slug = f.stem
        if slug in completed:
            continue

        content = f.read_text(encoding="utf-8")

        # Skip redirects, index, special pages
        if "http-equiv" in content and "refresh" in content:
            continue
        if slug in ("index", "about", "privacy"):
            continue
        # Skip athlete pages
        if slug.startswith("athlete-"):
            continue

        # Check what's missing
        has_faq = bool(re.search(r"faq.section|<details.*?<summary", content, re.IGNORECASE | re.DOTALL))
        has_difficulty = bool(re.search(r"difficulty-bar|class=\"belt ", content))

        if not has_faq or not has_difficulty:
            # Extract technique name from h1
            h1_match = re.search(r"<h1[^>]*>([^<]+)</h1>", content)
            tech_name = h1_match.group(1).strip() if h1_match else slug.replace("-", " ").title()

            targets.append({
                "slug": slug,
                "file": f,
                "tech_name": tech_name,
                "needs_faq": not has_faq,
                "needs_difficulty": not has_difficulty,
            })

        if len(targets) >= limit:
            break

    return targets

# ── Parse Gemini Response ──
def parse_response(text):
    """Extract JSON from Gemini response (handles markdown code blocks)"""
    # Strip markdown code fence if present
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON in the text
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None

# ── Main ──
def main():
    parser = argparse.ArgumentParser(description="Enrich wiki pages with FAQ + Difficulty via Gemini")
    parser.add_argument("--lang", default=DEFAULT_LANG, choices=["en", "ja", "pt"])
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reset-progress", action="store_true")
    args = parser.parse_args()

    os.chdir(WIKI_ROOT)

    if args.reset_progress:
        if PROGRESS_FILE.exists():
            PROGRESS_FILE.unlink()
        print("Progress reset.")
        return

    if not GEMINI_API_KEY and not args.dry_run:
        print("[ERROR] GEMINI_API_KEY not found. Set in .env or ~/.secrets")
        sys.exit(1)

    targets = find_targets(args.lang, args.limit)
    print(f"=== enrich_sections.py ===")
    print(f"  Language: {args.lang}")
    print(f"  Targets: {len(targets)} pages")
    print(f"  Dry run: {args.dry_run}")
    print()

    if not targets:
        print("No pages to enrich. All done!")
        return

    if args.dry_run:
        for t in targets[:20]:
            needs = []
            if t["needs_faq"]:
                needs.append("FAQ")
            if t["needs_difficulty"]:
                needs.append("Difficulty")
            print(f"  {t['slug']}: {', '.join(needs)}")
        if len(targets) > 20:
            print(f"  ... +{len(targets)-20} more")
        return

    # Process
    progress = load_progress()
    if args.lang not in progress["completed"]:
        progress["completed"][args.lang] = []

    success = 0
    fail = 0
    api_calls = 0

    for i, target in enumerate(targets, 1):
        slug = target["slug"]
        tech_name = target["tech_name"]
        filepath = target["file"]

        print(f"[{i}/{len(targets)}] {slug} ({tech_name})")

        # Rate limiting
        if api_calls > 0:
            time.sleep(SLEEP_BETWEEN)

        # Call Gemini
        prompt = build_enrich_prompt(tech_name, args.lang)
        raw = call_gemini(prompt)
        api_calls += 1

        if not raw:
            print(f"  ✗ Gemini returned empty")
            fail += 1
            continue

        data = parse_response(raw)
        if not data:
            print(f"  ✗ Failed to parse JSON")
            fail += 1
            continue

        # Read current file
        content = filepath.read_text(encoding="utf-8")
        modified = False

        # Inject FAQ
        if target["needs_faq"] and "faq" in data:
            faq_items = data["faq"]
            if isinstance(faq_items, list) and len(faq_items) >= 1:
                content = inject_faq(content, faq_items, args.lang)
                page_url = f"https://wiki.bjj-app.net/{args.lang}/{slug}.html"
                content = inject_faq_jsonld(content, faq_items, page_url)
                modified = True
                print(f"  ✓ FAQ ({len(faq_items)} questions)")

        # Inject Difficulty
        if target["needs_difficulty"] and "belt_level" in data:
            belt = data.get("belt_level", "blue")
            stars = data.get("stars", "★★☆☆☆")
            diff = data.get("difficulty_level", "Intermediate")
            content = inject_difficulty(content, belt, stars, diff)
            modified = True
            print(f"  ✓ Difficulty ({belt} / {diff})")

        if modified:
            filepath.write_text(content, encoding="utf-8")
            success += 1
        else:
            fail += 1

        # Save progress
        progress["completed"][args.lang].append(slug)
        if i % 10 == 0:
            save_progress(progress)

    # Final save
    save_progress(progress)

    print()
    print(f"=== Results ===")
    print(f"  Success: {success}")
    print(f"  Failed:  {fail}")
    print(f"  API calls: {api_calls}")
    print(f"  Progress saved to: {PROGRESS_FILE}")

if __name__ == "__main__":
    main()
