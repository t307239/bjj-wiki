#!/usr/bin/env python3
"""
scripts/patch_faq.py

FAQ セクションが存在しない既存ページに Gemini で FAQ 3本を後付け注入するパッチスクリプト。
フルページ再生成より 10 倍以上軽量（FAQ JSON のみ生成）。

対象: class="faq-q" が存在しない en/ ja/ pt/ の全ページ
挿入: 最後の </section> 直後 or <footer> 直前

使い方:
  python scripts/patch_faq.py                  # デフォルト: en のみ 100 件
  python scripts/patch_faq.py --limit 200      # 200 件処理
  python scripts/patch_faq.py --lang all       # 3 言語まとめて処理
  python scripts/patch_faq.py --lang ja        # 特定言語のみ
  python scripts/patch_faq.py --dry-run        # ファイル書き込みなし（確認用）
  python scripts/patch_faq.py --force          # キャッシュ無視して再処理
"""

import os, json, time, re, glob, argparse, datetime, html, urllib.request, urllib.error

# ===== シークレット読み込み =====
def _load_secrets():
    path = os.path.expanduser("~/.secrets")
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            line = line.removeprefix("export").strip()
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
_load_secrets()

# ===== 設定 =====
IS_CI          = os.environ.get("GITHUB_ACTIONS") == "true"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SITE_DIR       = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if IS_CI else os.path.expanduser("~/Claude/bjj-wiki")
CACHE_PATH     = os.path.join(SITE_DIR, "cache", "faq_patched.json")

LANG_CONFIG = {
    "en": {
        "h2":         "Common BJJ Problems & FAQ",
        "instruction": "Write all questions and answers in English.",
        "prompt_lang": "English",
    },
    "ja": {
        "h2":         "よくある質問・トラブル",
        "instruction": "すべての質問と回答を日本語で書いてください。",
        "prompt_lang": "Japanese",
    },
    "pt": {
        "h2":         "Perguntas Frequentes",
        "instruction": "Escreva todas as perguntas e respostas em Português brasileiro.",
        "prompt_lang": "Portuguese (Brazilian)",
    },
}

# FAQ スタイル（generate_bjj_wiki.py と統一）
FAQ_SECTION_STYLE = (
    'background:var(--card,#18181b);border-top:1px solid var(--border,rgba(255,255,255,0.10));'
    'padding:32px 0;margin-top:32px'
)
FAQ_H2_STYLE = 'color:var(--text,#e2e8f0);font-size:1.3rem;margin-bottom:20px'
FAQ_DIV_STYLE = 'background:var(--card,#18181b);border:1px solid var(--border,rgba(255,255,255,0.10));border-radius:12px;padding:20px;margin-bottom:16px'
FAQ_Q_STYLE   = 'font-weight:700;color:var(--accent,#7c3aed);margin-bottom:8px'

# ===== Telegram =====
def send_telegram(msg: str) -> None:
    token   = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        payload = json.dumps({"chat_id": chat_id, "text": msg}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload, headers={"Content-Type": "application/json"}, method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass

# ===== Gemini API（マルチモデルフォールバック）=====
def call_gemini(prompt: str) -> str | None:
    models = [
        ("gemini-2.5-flash-lite", "v1beta"),   # 無料tier: 15 RPM, 1000 RPD
        ("gemini-2.5-flash-lite", "v1"),
        ("gemini-2.5-flash",      "v1beta"),   # 無料tier: 5 RPM, 100 RPD
        ("gemini-2.5-flash",      "v1"),
    ]
    data = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.6, "maxOutputTokens": 1024},
    }).encode()
    # Security: API key は URL query ではなく x-goog-api-key ヘッダで送る
    # (z143 enrich_sections.py と同じ pattern)
    # URL query だとネットワーク中継/GHAログ/例外の str 化経由で漏洩する。
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }
    for model, api_ver in models:
        url = (f"https://generativelanguage.googleapis.com/{api_ver}"
               f"/models/{model}:generateContent")
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    url, data=data, headers=headers, method="POST",
                )
                with urllib.request.urlopen(req, timeout=60) as res:
                    result = json.loads(res.read())
                    return result["candidates"][0]["content"]["parts"][0]["text"]
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(30 * (attempt + 1))
                else:
                    break
            except Exception as e:
                # 例外メッセージに URL / key が混ざらないよう種別のみ出力
                print(f"  [{model}] Error: {type(e).__name__}")
                break
    return None

# ===== FAQ プロンプト（軽量版）=====
def build_faq_prompt(tech_name: str, lang_code: str) -> str:
    cfg = LANG_CONFIG[lang_code]
    return f"""You are a Brazilian Jiu-Jitsu black belt instructor.
{cfg['instruction']}

Generate 3 FAQ Q&As about BJJ technique: "{tech_name}"

Rules:
- Questions must be long-tail queries that real WHITE BELT beginners Google
  (e.g. "why does my neck hurt when I do {tech_name}", "how to {tech_name} against bigger opponent")
- Answers must be biomechanically specific (2-3 sentences, exact body mechanics)
- No vague answers like "practice more"

Return ONLY valid JSON, no markdown:
{{
  "faq_q1": "first white belt question",
  "faq_a1": "precise biomechanical answer",
  "faq_q2": "second white belt question",
  "faq_a2": "precise biomechanical answer",
  "faq_q3": "third white belt question",
  "faq_a3": "precise biomechanical answer"
}}"""

# ===== FAQ HTML ブロック生成 =====
def build_faq_html(faq: dict, lang_code: str) -> str:
    cfg = LANG_CONFIG[lang_code]
    q1, a1 = faq.get("faq_q1", ""), faq.get("faq_a1", "")
    q2, a2 = faq.get("faq_q2", ""), faq.get("faq_a2", "")
    q3, a3 = faq.get("faq_q3", ""), faq.get("faq_a3", "")
    # Security: Gemini 出力の q/a は prompt injection 経由で
    # `</div><script>...` 等が混入する恐れがあるため必ず html.escape
    # (z143 enrich_sections.py と同じ方針で persistent XSS を封殺)
    items = ""
    for q, a in [(q1, a1), (q2, a2), (q3, a3)]:
        if q and a:
            q_safe = html.escape(q, quote=True)
            a_safe = html.escape(a, quote=True)
            items += (
                f'\n  <div class="faq" style="{FAQ_DIV_STYLE}">'
                f'<div class="faq-q" style="{FAQ_Q_STYLE}">Q: {q_safe}</div>'
                f'<p style="color:#c2c2d9;margin:0">{a_safe}</p></div>'
            )
    if not items:
        return ""
    return (
        f'\n<section style="{FAQ_SECTION_STYLE}">\n'
        f'  <h2 style="{FAQ_H2_STYLE}">{cfg["h2"]}</h2>'
        f'{items}\n</section>'
    )

# ===== HTML へ FAQ 挿入 =====
def insert_faq_into_html(html: str, faq_html: str) -> str:
    # 優先: 最後の </section> 直後
    last_section = html.rfind("</section>")
    if last_section != -1:
        insert_pos = last_section + len("</section>")
        return html[:insert_pos] + faq_html + html[insert_pos:]
    # フォールバック: <footer> 直前
    footer_pos = html.find("<footer")
    if footer_pos != -1:
        return html[:footer_pos] + faq_html + "\n" + html[footer_pos:]
    # 最終フォールバック: </body> 直前
    body_end = html.rfind("</body>")
    if body_end != -1:
        return html[:body_end] + faq_html + "\n" + html[body_end:]
    return html + faq_html

# ===== h1 からテクニック名を抽出 =====
def extract_tech_name(html: str) -> str:
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    m = re.search(r'<title>(.*?)\s*[|\-]', html, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return "BJJ technique"

# ===== キャッシュ =====
def load_cache() -> dict:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache: dict) -> None:
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# ===== FAQ JSON パース（修復ロジック付き）=====
def parse_faq_json(raw: str) -> dict | None:
    """Gemini が返す malformed JSON を段階的に修復してパース。"""
    # Step 1: markdown コードブロック除去
    text = re.sub(r'^```[a-z]*\n?', '', raw.strip(), flags=re.MULTILINE)
    text = re.sub(r'\n?```$', '', text, flags=re.MULTILINE)
    text = text.strip()

    # Try 1: 直接パース
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try 2: trailing comma 除去（,} / ,]）
    try:
        fixed = re.sub(r',\s*([}\]])', r'\1', text)
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    # Try 3: regex で Q&A を直接抽出（JSON truncated の場合のフォールバック）
    faq: dict = {}
    for i in range(1, 4):
        q_m = re.search(rf'"faq_q{i}"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
        a_m = re.search(rf'"faq_a{i}"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
        if q_m:
            faq[f'faq_q{i}'] = q_m.group(1).replace('\\"', '"')
        if a_m:
            faq[f'faq_a{i}'] = a_m.group(1).replace('\\"', '"')
    return faq if len(faq) >= 2 else None


# ===== メイン =====
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit",   type=int, default=100, help="処理する最大ページ数")
    parser.add_argument("--lang",    default="en",           help="対象言語 (en/ja/pt/all)")
    parser.add_argument("--dry-run", action="store_true",    help="ファイル書き込みなし")
    parser.add_argument("--force",   action="store_true",    help="キャッシュ無視して再処理")
    args = parser.parse_args()

    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY が未設定")
        return

    langs = ["en", "ja", "pt"] if args.lang == "all" else [args.lang]
    cache = {} if args.force else load_cache()
    count = 0

    for lang in langs:
        lang_dir = os.path.join(SITE_DIR, lang)
        if not os.path.isdir(lang_dir):
            print(f"[SKIP] {lang}/ ディレクトリなし")
            continue

        files = sorted(glob.glob(os.path.join(lang_dir, "*.html")))
        # FAQ 0本のページに絞る
        targets = []
        for f in files:
            with open(f, encoding="utf-8") as fp:
                html = fp.read()
            if not re.search(r'class=["\']faq-q["\']', html):
                targets.append((f, html))

        print(f"[{lang}] FAQ 0本: {len(targets)} ページ")

        for filepath, html in targets:
            if count >= args.limit:
                print(f"[INFO] 上限 {args.limit} 件到達。次回続行。")
                break

            slug = os.path.basename(filepath).replace(".html", "")
            cache_key = f"{lang}/{slug}"

            if cache_key in cache and not args.force:
                continue

            tech_name = extract_tech_name(html)
            print(f"  [{lang}] {slug} ({tech_name}) ...")

            raw = call_gemini(build_faq_prompt(tech_name, lang))
            if not raw:
                print(f"  [WARN] Gemini 失敗: {slug}")
                continue

            # JSON パース（修復ロジック付き）
            faq = parse_faq_json(raw)
            if faq is None:
                print(f"  [WARN] JSON パース失敗 ({slug}): 修復不可")
                continue

            faq_html = build_faq_html(faq, lang)
            if not faq_html.strip():
                print(f"  [WARN] FAQ HTML 空: {slug}")
                continue

            new_html = insert_faq_into_html(html, faq_html)

            if not args.dry_run:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_html)
                cache[cache_key] = datetime.datetime.now().isoformat()
                save_cache(cache)

            count += 1
            print(f"  ✅ {cache_key} → FAQ 3本注入完了")

            # 10件ごとに Telegram 通知
            if count % 10 == 0:
                send_telegram(f"📝 FAQ パッチ: {count} 件完了")

            time.sleep(0.5)  # API 負荷軽減

        if count >= args.limit:
            break

    print(f"\n✅ 完了: {count} 件の FAQ パッチ適用")
    remaining = sum(
        1 for lang in langs
        for f in glob.glob(os.path.join(SITE_DIR, lang, "*.html"))
        if not re.search(r'class=["\']faq-q["\']', open(f, encoding="utf-8").read())
    )
    print(f"残り FAQ 未注入: {remaining} ページ")

if __name__ == "__main__":
    main()
