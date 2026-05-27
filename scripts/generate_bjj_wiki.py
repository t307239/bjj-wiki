#!/usr/bin/env python3
"""
BJJ Wiki - 多言語柔術技辞典 自動生成スクリプト
- Gemini APIで英語/日本語/ポルトガル語の技解説記事を生成
- 静的HTMLとしてGitHub Pagesにデプロイ
"""

import os, json, time, datetime, html, urllib.request, urllib.error, urllib.parse, re

# ===== Telegram通知 =====
def send_telegram(msg: str) -> None:
    """GitHub Actions の TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID を使って通知"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        payload = json.dumps({"chat_id": chat_id, "text": msg}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass  # 通知失敗は無視してビルドを継続

# ===== 内部リンク辞書（技名→スラッグ）=====
INTERNAL_LINK_MAP = {
    "en": {
        "Armbar": "armbar", "Triangle Choke": "triangle-choke",
        "Rear Naked Choke": "rear-naked-choke", "Guillotine Choke": "guillotine-choke",
        "Kimura": "kimura", "Americana": "americana", "Omoplata": "omoplata",
        "Closed Guard": "closed-guard", "Half Guard": "half-guard",
        "Butterfly Guard": "butterfly-guard", "De La Riva Guard": "de-la-riva-guard",
        "Spider Guard": "spider-guard", "X-Guard": "x-guard",
        "Berimbolo": "berimbolo", "Back Mount": "back-mount",
        "Side Control": "side-control", "Mount": "mount",
        "Guard Pass": "guard-pass", "Heel Hook": "heel-hook",
        "Bow and Arrow Choke": "bow-and-arrow-choke",
        "Inside Heel Hook": "inside-heel-hook", "Outside Heel Hook": "outside-heel-hook",
        "Knee Bar": "knee-bar", "Toe Hold": "toe-hold", "Ankle Lock": "ankle-lock",
        "D'Arce Choke": "darce-choke", "Anaconda Choke": "anaconda-choke",
        "Ezekiel Choke": "ezekiel-choke", "Arm Triangle": "arm-triangle-choke",
        "North-South Choke": "north-south-choke", "Baseball Choke": "baseball-choke",
        "Wrist Lock": "wrist-lock", "Calf Slicer": "calf-slicer",
        "Torreando Pass": "torreando-pass", "Knee Slice": "knee-slice-pass",
        "Leg Drag": "leg-drag-pass", "Double Under Pass": "double-under-pass",
        "Deep Half Guard": "deep-half-guard", "50/50": "50-50-guard",
        "Lasso Guard": "lasso-guard", "Reverse De La Riva": "reverse-de-la-riva",
        "Rubber Guard": "rubber-guard", "Z-Guard": "z-guard",
        "Scissor Sweep": "scissor-sweep", "Hip Bump Sweep": "hip-bump-sweep",
        "Tripod Sweep": "tripod-sweep", "Elevator Sweep": "elevator-sweep",
        "Back Take": "backtake", "Shrimp Escape": "shrimp-escape",
        "Hip Escape": "hip-escape", "Arm Drag": "arm-drag",
        "Body Triangle": "body-triangle", "Seat Belt": "seat-belt-control",
        "Front Headlock": "front-headlock", "Underhook": "underhook",
        "Double Leg Takedown": "double-leg-takedown", "Single Leg": "single-leg-takedown",
        "Sprawl": "sprawl", "Knee on Belly": "knee-on-belly",
        "North-South": "north-south", "Turtle": "turtle-position",
    },
    "ja": {
        "アームバー": "armbar", "三角絞め": "triangle-choke",
        "裸絞め": "rear-naked-choke", "ギロチンチョーク": "guillotine-choke",
        "木村ロック": "kimura", "アメリカーナ": "americana", "オモプラータ": "omoplata",
        "クローズドガード": "closed-guard", "ハーフガード": "half-guard",
        "バタフライガード": "butterfly-guard", "デラヒーバガード": "de-la-riva-guard",
        "バックマウント": "back-mount", "サイドコントロール": "side-control",
        "マウント": "mount", "ヒールフック": "heel-hook",
        "インサイドヒールフック": "inside-heel-hook", "アウトサイドヒールフック": "outside-heel-hook",
        "ニーバー": "knee-bar", "トーホールド": "toe-hold", "アンクルロック": "ankle-lock",
        "ダーシーチョーク": "darce-choke", "アナコンダチョーク": "anaconda-choke",
        "エゼキエルチョーク": "ezekiel-choke", "カーフスライサー": "calf-slicer",
        "スパイダーガード": "spider-guard", "ラバーガード": "rubber-guard",
        "ラッソーガード": "lasso-guard", "ディープハーフガード": "deep-half-guard",
        "トレアンドパス": "torreando-pass", "ニースライスパス": "knee-slice-pass",
        "シザースイープ": "scissor-sweep", "ヒップバンプスイープ": "hip-bump-sweep",
        "バックテイク": "backtake", "シュリンプエスケープ": "shrimp-escape",
        "アームドラッグ": "arm-drag", "ダブルレッグ": "double-leg-takedown",
        "スプロール": "sprawl", "ノースサウス": "north-south",
    },
    "pt": {
        "Armbar": "armbar", "Triangle Choke": "triangle-choke",
        "Rear Naked Choke": "rear-naked-choke", "Guillotine": "guillotine-choke",
        "Kimura": "kimura", "Americana": "americana", "Omoplata": "omoplata",
        "Guarda Fechada": "closed-guard", "Meia Guarda": "half-guard",
        "Berimbolo": "berimbolo", "Heel Hook": "heel-hook",
        "Knee Bar": "knee-bar", "Rasteira": "ankle-pick",
        "Passagem de Guarda": "guard-pass", "Guarda Aranha": "spider-guard",
        "Guarda Borboleta": "butterfly-guard", "De La Riva": "de-la-riva-guard",
        "Choke Arco e Flecha": "bow-and-arrow-choke", "Montada": "mount",
        "Controle das Costas": "back-mount", "Raspagem Tesoura": "scissor-sweep",
        "Braçadeira": "arm-triangle-choke", "Chave de Pé": "ankle-lock",
    },
}

def add_internal_links(html: str, current_slug: str, lang: str) -> str:
    """<p>タグ内の技名を内部リンクに変換（各技1回のみ）"""
    link_map = INTERNAL_LINK_MAP.get(lang, INTERNAL_LINK_MAP["en"])
    linked = set()

    def replace_in_p(m):
        p = m.group(0)
        if '<a ' in p:
            return p
        for name, slug in link_map.items():
            if slug == current_slug or slug in linked:
                continue
            pat = re.compile(re.escape(name), re.IGNORECASE)
            if pat.search(p):
                url = f"../{lang}/{slug}.html"
                p = pat.sub(
                    f'<a href="{url}" style="color:var(--accent,#7c3aed);text-decoration:underline">{name}</a>',
                    p, count=1)
                linked.add(slug)
                break
        return p

    return re.sub(r'<p[^>]*>.*?</p>', replace_in_p, html, flags=re.DOTALL)

# ===== ~/.secrets からAPIキーを補完 =====
def _load_secrets():
    path = os.path.expanduser("~/.secrets")
    if not os.path.exists(path): return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            line = line.removeprefix("export").strip()
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
_load_secrets()

# ===== 設定 =====
IS_CI          = os.environ.get("GITHUB_ACTIONS") == "true"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SITE_DIR       = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if IS_CI else os.path.expanduser("~/Claude/bjj-wiki")
SITE_URL       = "https://wiki.bjj-app.net"
## AMAZON_TAG / AMAZON_ASIN_MAP / get_amazon_url — REMOVED (CLAUDE.md: アフィリリンク完全禁止)

LANGUAGES = {
    "en": {"name": "English",    "dir": "en"},
    "ja": {"name": "日本語",      "dir": "ja"},
    "pt": {"name": "Português",  "dir": "pt"},
}

# ===== 技リスト（100技）=====
TECHNIQUES = [
    # ガード系
    {"slug": "closed-guard",        "name": "Closed Guard",        "category": "Guard"},
    {"slug": "open-guard",          "name": "Open Guard",          "category": "Guard"},
    {"slug": "half-guard",          "name": "Half Guard",          "category": "Guard"},
    {"slug": "spider-guard",        "name": "Spider Guard",        "category": "Guard"},
    {"slug": "de-la-riva-guard",    "name": "De La Riva Guard",    "category": "Guard"},
    {"slug": "berimbolo",           "name": "Berimbolo",           "category": "Guard"},
    {"slug": "butterfly-guard",     "name": "Butterfly Guard",     "category": "Guard"},
    {"slug": "rubber-guard",        "name": "Rubber Guard",        "category": "Guard"},
    {"slug": "x-guard",             "name": "X-Guard",             "category": "Guard"},
    {"slug": "worm-guard",          "name": "Worm Guard",          "category": "Guard"},
    {"slug": "reverse-de-la-riva",  "name": "Reverse De La Riva",  "category": "Guard"},
    {"slug": "50-50-guard",         "name": "50/50 Guard",         "category": "Guard"},
    {"slug": "lasso-guard",         "name": "Lasso Guard",         "category": "Guard"},
    {"slug": "deep-half-guard",     "name": "Deep Half Guard",     "category": "Guard"},
    {"slug": "z-guard",             "name": "Z-Guard",             "category": "Guard"},
    # パス系
    {"slug": "guard-pass",          "name": "Guard Pass",          "category": "Passing"},
    {"slug": "torreando-pass",      "name": "Torreando Pass",      "category": "Passing"},
    {"slug": "knee-slice-pass",     "name": "Knee Slice Pass",     "category": "Passing"},
    {"slug": "leg-drag-pass",       "name": "Leg Drag Pass",       "category": "Passing"},
    {"slug": "headquarters-pass",   "name": "Headquarters Pass",   "category": "Passing"},
    {"slug": "stack-pass",          "name": "Stack Pass",          "category": "Passing"},
    {"slug": "double-under-pass",   "name": "Double Under Pass",   "category": "Passing"},
    {"slug": "pressure-pass",       "name": "Pressure Pass",       "category": "Passing"},
    {"slug": "smash-pass",          "name": "Smash Pass",          "category": "Passing"},
    {"slug": "x-pass",              "name": "X-Pass",              "category": "Passing"},
    # テイクダウン
    {"slug": "double-leg-takedown", "name": "Double Leg Takedown", "category": "Takedown"},
    {"slug": "single-leg-takedown", "name": "Single Leg Takedown", "category": "Takedown"},
    {"slug": "osoto-gari",          "name": "Osoto Gari",          "category": "Takedown"},
    {"slug": "ankle-pick",          "name": "Ankle Pick",          "category": "Takedown"},
    {"slug": "harai-goshi",         "name": "Harai Goshi",         "category": "Takedown"},
    {"slug": "ippon-seoi-nage",     "name": "Ippon Seoi Nage",     "category": "Takedown"},
    {"slug": "morote-seoi-nage",    "name": "Morote Seoi Nage",    "category": "Takedown"},
    {"slug": "snap-down",           "name": "Snap Down",           "category": "Takedown"},
    # 絞め技
    {"slug": "rear-naked-choke",    "name": "Rear Naked Choke",    "category": "Choke"},
    {"slug": "triangle-choke",      "name": "Triangle Choke",      "category": "Choke"},
    {"slug": "guillotine-choke",    "name": "Guillotine Choke",    "category": "Choke"},
    {"slug": "bow-and-arrow-choke", "name": "Bow and Arrow Choke", "category": "Choke"},
    {"slug": "ezekiel-choke",       "name": "Ezekiel Choke",       "category": "Choke"},
    {"slug": "darce-choke",         "name": "D'Arce Choke",        "category": "Choke"},
    {"slug": "anaconda-choke",      "name": "Anaconda Choke",      "category": "Choke"},
    {"slug": "loop-choke",          "name": "Loop Choke",          "category": "Choke"},
    {"slug": "arm-triangle-choke",  "name": "Arm Triangle Choke",  "category": "Choke"},
    {"slug": "north-south-choke",   "name": "North-South Choke",   "category": "Choke"},
    {"slug": "baseball-choke",      "name": "Baseball Choke",      "category": "Choke"},
    {"slug": "cross-collar-choke",  "name": "Cross Collar Choke",  "category": "Choke"},
    {"slug": "clock-choke",         "name": "Clock Choke",         "category": "Choke"},
    {"slug": "lapel-choke",         "name": "Lapel Choke",         "category": "Choke"},
    # 関節技
    {"slug": "armbar",              "name": "Armbar",              "category": "Joint Lock"},
    {"slug": "kimura",              "name": "Kimura",              "category": "Joint Lock"},
    {"slug": "americana",           "name": "Americana",           "category": "Joint Lock"},
    {"slug": "omoplata",            "name": "Omoplata",            "category": "Joint Lock"},
    {"slug": "wrist-lock",          "name": "Wrist Lock",          "category": "Joint Lock"},
    {"slug": "straight-armbar",     "name": "Straight Armbar",     "category": "Joint Lock"},
    {"slug": "monoplata",           "name": "Monoplata",           "category": "Joint Lock"},
    # レッグロック
    {"slug": "heel-hook",           "name": "Heel Hook",           "category": "Leg Lock"},
    {"slug": "inside-heel-hook",    "name": "Inside Heel Hook",    "category": "Leg Lock"},
    {"slug": "outside-heel-hook",   "name": "Outside Heel Hook",   "category": "Leg Lock"},
    {"slug": "knee-bar",            "name": "Knee Bar",            "category": "Leg Lock"},
    {"slug": "toe-hold",            "name": "Toe Hold",            "category": "Leg Lock"},
    {"slug": "calf-slicer",         "name": "Calf Slicer",         "category": "Leg Lock"},
    {"slug": "ankle-lock",          "name": "Ankle Lock",          "category": "Leg Lock"},
    {"slug": "estima-lock",         "name": "Estima Lock",         "category": "Leg Lock"},
    # ポジション
    {"slug": "mount",               "name": "Mount",               "category": "Position"},
    {"slug": "back-mount",          "name": "Back Mount",          "category": "Position"},
    {"slug": "side-control",        "name": "Side Control",        "category": "Position"},
    {"slug": "north-south",         "name": "North-South",         "category": "Position"},
    {"slug": "knee-on-belly",       "name": "Knee on Belly",       "category": "Position"},
    {"slug": "s-mount",             "name": "S-Mount",             "category": "Position"},
    {"slug": "modified-mount",      "name": "Modified Mount",      "category": "Position"},
    {"slug": "body-triangle",       "name": "Body Triangle",       "category": "Position"},
    # スイープ
    {"slug": "scissor-sweep",       "name": "Scissor Sweep",       "category": "Sweep"},
    {"slug": "flower-sweep",        "name": "Flower Sweep",        "category": "Sweep"},
    {"slug": "hip-bump-sweep",      "name": "Hip Bump Sweep",      "category": "Sweep"},
    {"slug": "pendulum-sweep",      "name": "Pendulum Sweep",      "category": "Sweep"},
    {"slug": "tripod-sweep",        "name": "Tripod Sweep",        "category": "Sweep"},
    {"slug": "elevator-sweep",      "name": "Elevator Sweep",      "category": "Sweep"},
    {"slug": "sickle-sweep",        "name": "Sickle Sweep",        "category": "Sweep"},
    {"slug": "overhead-sweep",      "name": "Overhead Sweep",      "category": "Sweep"},
    {"slug": "balloon-sweep",       "name": "Balloon Sweep",       "category": "Sweep"},
    {"slug": "x-guard-sweep",       "name": "X-Guard Sweep",       "category": "Sweep"},
    # サブミッション連携
    {"slug": "arm-drag",            "name": "Arm Drag",            "category": "Transition"},
    {"slug": "granby-roll",         "name": "Granby Roll",         "category": "Transition"},
    {"slug": "shrimp-escape",       "name": "Shrimp Escape",       "category": "Escape"},
    {"slug": "bridge-and-roll",     "name": "Bridge and Roll",     "category": "Escape"},
    {"slug": "elbow-knee-escape",   "name": "Elbow-Knee Escape",   "category": "Escape"},
    # ディフェンス・エスケープ
    {"slug": "guard-retention",     "name": "Guard Retention",     "category": "Defense"},
    {"slug": "hip-escape",          "name": "Hip Escape",          "category": "Defense"},
    {"slug": "frame",               "name": "Frame",               "category": "Defense"},
    {"slug": "sprawl",              "name": "Sprawl",              "category": "Defense"},
    {"slug": "back-defense",        "name": "Back Defense",        "category": "Defense"},
    # トランジション
    {"slug": "backtake",            "name": "Back Take",           "category": "Transition"},
    {"slug": "turtle-position",     "name": "Turtle Position",     "category": "Position"},
    {"slug": "technical-standup",   "name": "Technical Stand-Up",  "category": "Transition"},
    {"slug": "stand-in-base",       "name": "Stand In Base",       "category": "Transition"},
    {"slug": "sitting-guard",       "name": "Sitting Guard",       "category": "Guard"},
    # ノーギ特化
    {"slug": "seat-belt-control",   "name": "Seat Belt Control",   "category": "Position"},
    {"slug": "front-headlock",      "name": "Front Headlock",      "category": "Position"},
    {"slug": "russian-tie",         "name": "Russian Tie",         "category": "Takedown"},
    {"slug": "underhook",           "name": "Underhook",           "category": "Position"},
    {"slug": "overhook",            "name": "Overhook",            "category": "Position"},
]

# ===== Gemini API（複数モデルフォールバック）=====
def call_gemini(prompt):
    # 無料tierを先頭→有料(2.5系)は最終フォールバックのみ
    models = [
        ("gemini-2.5-flash-lite", "v1beta"),   # free: 15 RPM, 1000 RPD
        ("gemini-2.5-flash-lite", "v1"),
        ("gemini-2.5-flash",      "v1beta"),   # free: 5 RPM, 100 RPD
        ("gemini-2.5-flash",      "v1"),
    ]
    data = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
    }).encode()
    # Security: API key は x-goog-api-key header 送信 (z143/z152 共通方針)
    # URL query だとネットワーク中継/GHAログ/例外の str 化経由で漏洩する。
    req_headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
    for model, api_ver in models:
        url = f"https://generativelanguage.googleapis.com/{api_ver}/models/{model}:generateContent"
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
                with urllib.request.urlopen(req, timeout=60) as res:
                    result = json.loads(res.read())
                    text   = result["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"[OK] [{model}] 生成成功")
                    return text
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(30 * (attempt + 1))
                else:
                    print(f"[{model}] HTTP {e.code} → 次のモデルへ"); break
            except Exception as e:
                # exception message に URL/key が混ざらないよう種別のみ
                print(f"[{model}] エラー: {type(e).__name__}"); break
    return None

# ===== 記事生成プロンプト =====
def build_article_prompt(technique, lang_code, all_slugs=None):
    # z255ii: lang_code 別 prompt + title/h1 の examples で英語化 regression を防ぐ
    # (旧: title 指示が "{tech_name} と BJJ を含む" だけで Gemini が JA でも英語 title
    #  を出すケースがあり 92 page で z254e fix が --force regen で revert していた)
    lang_instructions = {
        "en": "Write everything in English.",
        "ja": "すべて日本語で書いてください。**特に title / h1 / meta_description は必ず日本語で書く** (英語の \"BJJ\" / \"Guide\" / \"White Belt\" 等の単語を直接使わず、カタカナまたは漢字に翻訳)。",
        "pt": "Escreva tudo em Português brasileiro. **Em particular title / h1 / meta_description devem ser em português** (não usar palavras inglesas como \"BJJ Guide\" / \"White Belt\" diretamente — traduzir para português).",
    }
    instruction = lang_instructions[lang_code]

    # title/h1/meta の lang-specific 例示で Gemini を anchoring
    title_examples = {
        "en": '例: "Armbar BJJ: White Belt Guide | BJJ Wiki" / "Heel Hook for BJJ — Setup & Defense | BJJ Wiki"',
        "ja": '例: 「アームバー：BJJ白帯ガイド | BJJ Wiki」「ヒールフックの仕組みと防御 | BJJ Wiki」（必ず技名はカタカナ表記）',
        "pt": '例: "Armbar no BJJ: Guia Faixa Branca | BJJ Wiki" / "Heel Hook no BJJ — Setup e Defesa | BJJ Wiki"',
    }
    h1_examples = {
        "en": '例: "Armbar: A White Belt\'s Biomechanical Guide"',
        "ja": '例: 「アームバー：白帯のためのバイオメカニクス完全ガイド」（カタカナ + 日本語）',
        "pt": '例: "Armbar: Guia Biomecânico para Faixa Branca"',
    }

    tech_name = technique["name"]
    tech_slug = technique["slug"]
    slug_hint = ""
    if all_slugs:
        other = [s for s in all_slugs if s != tech_slug][:80]
        slug_hint = f"\n\nAVAILABLE RELATED SLUGS (pick 3 for semantic_links): {', '.join(other)}"

    return f"""You are a world-class Brazilian Jiu-Jitsu black belt instructor with 20+ years of teaching experience.
{instruction}

Your reader is a WHITE BELT — a beginner with no body movement habits yet and high injury risk.
Write a precise, biomechanically accurate technique guide for: **{tech_name}** (Category: {technique["category"]}){slug_hint}

ABSOLUTE RULES:
1. NEVER use vague language: ban "pull hard", "move quickly", "engage properly". Describe exact grips (collar, sleeve, pants, wrist), exact weight distribution (hip angle, knee direction, base width), exact frame positions.
2. Every paragraph must be 3 lines or fewer. Long prose blocks are forbidden.
3. All list fields must use markdown bullet points (- item) or numbered steps (1. step).
4. White belt warning section is MANDATORY — minimum 3 specific injury risks with EXACT biomechanical failure mode.
5. Drill progressions: minimum 6 numbered steps from 0% to live rolling. Include rep counts.
6. Each section (biomechanics, warnings, drills, counters) must have minimum 5 substantive points.
7. FAQ: write 3 DIFFERENT long-tail questions that real white belts Google (e.g. "why does my wrist hurt when I do {tech_name}", "how do I {tech_name} against a bigger opponent"). Include specific biomechanical answers.

Return ONLY valid JSON with this exact structure (no markdown wrapper, no extra text):
{{{{
  "title": "SEO title (60 chars max). {title_examples[lang_code]}",
  "meta_description": "150-160 char meta in the target language ({lang_code}). Must NOT be English-only when lang is ja or pt.",
  "h1": "Main H1 heading in target language ({lang_code}). {h1_examples[lang_code]}",
  "belt_level": "Recommended belt level: White/Blue/Purple/Brown/Black",
  "technique_overview_md": "3 paragraphs. Paragraph 1: what position this starts from and what it achieves. Paragraph 2: why white belts fail at this (frame of mind). Paragraph 3: the ONE key mechanical insight that makes it work. Each paragraph max 3 lines.",
  "biomechanics_and_grips_md": "Numbered step-by-step execution. Each step: EXACT grip name, EXACT hip/pelvis angle, EXACT weight transfer direction. Minimum 7 steps. Use 1. 2. 3. format.",
  "white_belt_warning_md": "Bullet list of 3-5 common white belt errors. Each bullet: (a) wrong movement described precisely, (b) which joint/ligament is damaged and HOW, (c) exact correct alternative movement. Use - format.",
  "drill_progressions_md": "Numbered progression from isolated solo drilling to live rolling. Minimum 6 steps. Each step has rep count and resistance percentage (0%, 25%, 50%, 75%, 90%, 100%). Use 1. 2. 3. format.",
  "counters_and_when_to_use_md": "Two clearly labeled sections: WHEN TO ATTEMPT (3 specific positional triggers) and PRIMARY COUNTERS (3 defenses with exact body mechanics). Use - format.",
  "faq_q1": "Long-tail white belt question about a specific failure/pain/confusion with {tech_name}",
  "faq_a1": "Biomechanically precise answer (3-4 sentences) with exact fix",
  "faq_q2": "Second different long-tail question (e.g. against bigger opponent, no-gi variation, competition scenario)",
  "faq_a2": "Biomechanically precise answer (3-4 sentences) with exact fix",
  "faq_q3": "Third long-tail question about a common misconception or timing issue with {tech_name}",
  "faq_a3": "Biomechanically precise answer (3-4 sentences) with exact fix",
  "semantic_links": ["slug-1", "slug-2", "slug-3"],
  "keywords": ["{tech_slug}", "bjj {tech_name.lower()}", "{tech_name.lower()} technique", "bjj white belt", "{tech_name.lower()} tutorial"]
}}}}"""

# ===== 難易度・選手・Yoga・ギア マッピング =====
DIFFICULTY_MAP = {
    "armbar":("blue","★★★☆☆","Intermediate"),"triangle-choke":("blue","★★★☆☆","Intermediate"),
    "rear-naked-choke":("white","★★☆☆☆","Beginner"),"guillotine-choke":("blue","★★★☆☆","Intermediate"),
    "kimura":("blue","★★★☆☆","Intermediate"),"americana":("white","★★☆☆☆","Beginner"),
    "omoplata":("purple","★★★★☆","Advanced"),"heel-hook":("brown","★★★★★","Expert"),
    "inside-heel-hook":("brown","★★★★★","Expert"),"outside-heel-hook":("brown","★★★★★","Expert"),
    "berimbolo":("purple","★★★★☆","Advanced"),"rubber-guard":("purple","★★★★☆","Advanced"),
    "closed-guard":("white","★☆☆☆☆","Beginner"),"half-guard":("white","★★☆☆☆","Beginner"),
    "butterfly-guard":("blue","★★★☆☆","Intermediate"),"de-la-riva-guard":("blue","★★★☆☆","Intermediate"),
    "x-guard":("purple","★★★★☆","Advanced"),"worm-guard":("purple","★★★★☆","Advanced"),
    "50-50-guard":("blue","★★★☆☆","Intermediate"),"knee-bar":("purple","★★★★☆","Advanced"),
    "toe-hold":("blue","★★★☆☆","Intermediate"),"ankle-lock":("blue","★★☆☆☆","Intermediate"),
    "bow-and-arrow-choke":("blue","★★★☆☆","Intermediate"),"back-mount":("blue","★★★☆☆","Intermediate"),
    "mount":("white","★★☆☆☆","Beginner"),"side-control":("white","★★☆☆☆","Beginner"),
    "guard-pass":("blue","★★★☆☆","Intermediate"),"scissor-sweep":("white","★★☆☆☆","Beginner"),
    "hip-bump-sweep":("white","★★☆☆☆","Beginner"),"shrimp-escape":("white","★☆☆☆☆","Beginner"),
    "double-leg-takedown":("blue","★★★☆☆","Intermediate"),"single-leg-takedown":("white","★★☆☆☆","Beginner"),
    "darce-choke":("blue","★★★☆☆","Intermediate"),"anaconda-choke":("blue","★★★☆☆","Intermediate"),
    "arm-triangle-choke":("blue","★★★☆☆","Intermediate"),"north-south-choke":("purple","★★★★☆","Advanced"),
    "baseball-choke":("blue","★★★☆☆","Intermediate"),"lasso-guard":("blue","★★★☆☆","Intermediate"),
    "calf-slicer":("purple","★★★★☆","Advanced"),"wrist-lock":("blue","★★★☆☆","Intermediate"),
    "torreando-pass":("blue","★★★☆☆","Intermediate"),"knee-slice-pass":("blue","★★★☆☆","Intermediate"),
    "north-south":("white","★★☆☆☆","Beginner"),"knee-on-belly":("blue","★★★☆☆","Intermediate"),
}
BELT_BG = {"white":"#e2e2ee","blue":"#2563eb","purple":"#7c3aed","brown":"#92400e","black":"#111"}
BELT_FG = {"white":"#111","blue":"#fff","purple":"#fff","brown":"#fff","black":"#fff"}

ATHLETE_MAP = {
    "armbar":[("john-danaher","John Danaher","🇺🇸"),("marcelo-garcia","Marcelo Garcia","🇧🇷"),("gordon-ryan","Gordon Ryan","🇺🇸")],
    "triangle-choke":[("marcelo-garcia","Marcelo Garcia","🇧🇷"),("john-danaher","John Danaher","🇺🇸")],
    "rear-naked-choke":[("gordon-ryan","Gordon Ryan","🇺🇸"),("marcelo-garcia","Marcelo Garcia","🇧🇷")],
    "guillotine-choke":[("marcelo-garcia","Marcelo Garcia","🇧🇷"),("john-danaher","John Danaher","🇺🇸")],
    "kimura":[("marcelo-garcia","Marcelo Garcia","🇧🇷"),("john-danaher","John Danaher","🇺🇸")],
    "heel-hook":[("gordon-ryan","Gordon Ryan","🇺🇸"),("craig-jones","Craig Jones","🇦🇺"),("john-danaher","John Danaher","🇺🇸")],
    "inside-heel-hook":[("gordon-ryan","Gordon Ryan","🇺🇸"),("craig-jones","Craig Jones","🇦🇺")],
    "outside-heel-hook":[("gordon-ryan","Gordon Ryan","🇺🇸"),("craig-jones","Craig Jones","🇦🇺")],
    "berimbolo":[("mikey-musumeci","Mikey Musumeci","🇺🇸"),("caio-terra","Caio Terra","🇧🇷")],
    "closed-guard":[("marcelo-garcia","Marcelo Garcia","🇧🇷"),("bernardo-faria","Bernardo Faria","🇧🇷")],
    "half-guard":[("bernardo-faria","Bernardo Faria","🇧🇷"),("marcelo-garcia","Marcelo Garcia","🇧🇷")],
    "butterfly-guard":[("marcelo-garcia","Marcelo Garcia","🇧🇷"),("john-danaher","John Danaher","🇺🇸")],
    "omoplata":[("caio-terra","Caio Terra","🇧🇷"),("mikey-musumeci","Mikey Musumeci","🇺🇸")],
    "rubber-guard":[("mikey-musumeci","Mikey Musumeci","🇺🇸")],
    "bow-and-arrow-choke":[("marcelo-garcia","Marcelo Garcia","🇧🇷"),("andre-galvao","André Galvão","🇧🇷")],
    "back-mount":[("gordon-ryan","Gordon Ryan","🇺🇸"),("marcelo-garcia","Marcelo Garcia","🇧🇷")],
    "x-guard":[("marcelo-garcia","Marcelo Garcia","🇧🇷")],
    "de-la-riva-guard":[("caio-terra","Caio Terra","🇧🇷"),("keenan-cornelius","Keenan Cornelius","🇺🇸")],
    "worm-guard":[("keenan-cornelius","Keenan Cornelius","🇺🇸")],
    "lasso-guard":[("keenan-cornelius","Keenan Cornelius","🇺🇸"),("caio-terra","Caio Terra","🇧🇷")],
    "mount":[("andre-galvao","André Galvão","🇧🇷"),("marcelo-garcia","Marcelo Garcia","🇧🇷")],
    "side-control":[("gordon-ryan","Gordon Ryan","🇺🇸"),("xande-ribeiro","Xande Ribeiro","🇧🇷")],
    "50-50-guard":[("gordon-ryan","Gordon Ryan","🇺🇸"),("craig-jones","Craig Jones","🇦🇺")],
    "knee-bar":[("gordon-ryan","Gordon Ryan","🇺🇸"),("craig-jones","Craig Jones","🇦🇺")],
    "double-leg-takedown":[("marcelo-garcia","Marcelo Garcia","🇧🇷"),("andre-galvao","André Galvão","🇧🇷")],
    "arm-drag":[("marcelo-garcia","Marcelo Garcia","🇧🇷")],
    "anaconda-choke":[("marcelo-garcia","Marcelo Garcia","🇧🇷"),("craig-jones","Craig Jones","🇦🇺")],
    "darce-choke":[("john-danaher","John Danaher","🇺🇸"),("gordon-ryan","Gordon Ryan","🇺🇸")],
}

YOGA_SLUG_MAP = {
    "armbar":[("cow-face-pose","Cow Face Pose"),("eagle-pose","Eagle Pose"),("thread-the-needle","Thread the Needle")],
    "triangle-choke":[("reclined-pigeon","Reclined Pigeon"),("fire-log-pose","Fire Log Pose")],
    "kimura":[("cow-face-pose","Cow Face Pose"),("eagle-pose","Eagle Pose")],
    "omoplata":[("thread-the-needle","Thread the Needle"),("cow-face-pose","Cow Face Pose")],
    "heel-hook":[("happy-baby-pose","Happy Baby Pose"),("reclined-pigeon","Reclined Pigeon"),("lizard-pose","Lizard Pose")],
    "inside-heel-hook":[("happy-baby-pose","Happy Baby Pose"),("reclined-pigeon","Reclined Pigeon")],
    "outside-heel-hook":[("happy-baby-pose","Happy Baby Pose"),("pigeon-pose","Pigeon Pose")],
    "knee-bar":[("low-lunge","Low Lunge"),("half-splits","Half Splits")],
    "closed-guard":[("butterfly-pose","Butterfly Pose"),("happy-baby-pose","Happy Baby Pose")],
    "half-guard":[("pigeon-pose","Pigeon Pose"),("low-lunge","Low Lunge")],
    "butterfly-guard":[("butterfly-pose","Butterfly Pose"),("wide-legged-fold","Wide-Legged Fold")],
    "berimbolo":[("revolved-chair-pose","Revolved Chair"),("twisted-lunge","Twisted Lunge")],
    "rubber-guard":[("happy-baby-pose","Happy Baby Pose"),("lizard-pose","Lizard Pose")],
    "de-la-riva-guard":[("pigeon-pose","Pigeon Pose"),("half-splits","Half Splits")],
    "x-guard":[("wide-legged-fold","Wide-Legged Fold"),("lizard-pose","Lizard Pose")],
    "50-50-guard":[("happy-baby-pose","Happy Baby Pose"),("reclined-pigeon","Reclined Pigeon")],
    "guillotine-choke":[("cat-cow-pose","Cat-Cow Pose"),("childs-pose","Child's Pose")],
    "rear-naked-choke":[("cat-cow-pose","Cat-Cow Pose"),("bridge-pose","Bridge Pose")],
    "double-leg-takedown":[("warrior-i-pose","Warrior I"),("chair-pose","Chair Pose")],
    "single-leg-takedown":[("warrior-i-pose","Warrior I"),("low-lunge","Low Lunge")],
}
YOGA_CAT_DEFAULTS = {
    "Guard":[("pigeon-pose","Pigeon Pose"),("lizard-pose","Lizard Pose")],
    "Joint Lock":[("cow-face-pose","Cow Face Pose"),("eagle-pose","Eagle Pose")],
    "Leg Lock":[("happy-baby-pose","Happy Baby Pose"),("reclined-pigeon","Reclined Pigeon")],
    "Choke":[("cat-cow-pose","Cat-Cow Pose"),("childs-pose","Child's Pose")],
    "Sweep":[("warrior-ii-pose","Warrior II"),("low-lunge","Low Lunge")],
    "Takedown":[("warrior-i-pose","Warrior I"),("chair-pose","Chair Pose")],
    "Passing":[("low-lunge","Low Lunge"),("half-splits","Half Splits")],
    "Position":[("bridge-pose","Bridge Pose"),("boat-pose","Boat Pose")],
    "Escape":[("bridge-pose","Bridge Pose"),("thread-the-needle","Thread the Needle")],
    "Transition":[("downward-dog","Downward Dog"),("plank-pose","Plank Pose")],
    "Defense":[("childs-pose","Child's Pose"),("downward-dog","Downward Dog")],
}

GEAR_CAT_MAP = {
    "Guard":[("best-bjj-gi-guide","🥋 Best BJJ Gi"),("best-bjj-rash-guard","👕 Best Rashguard")],
    "Joint Lock":[("best-bjj-gi-guide","🥋 Best BJJ Gi"),("best-bjj-mouthguard","🦷 Best Mouthguard")],
    "Leg Lock":[("best-bjj-rash-guard","👕 Best Rashguard"),("best-bjj-knee-pads","🦵 Best Knee Pads")],
    "Choke":[("best-bjj-gi-guide","🥋 Best BJJ Gi"),("best-bjj-mouthguard","🦷 Best Mouthguard")],
    "Sweep":[("best-bjj-gi-guide","🥋 Best BJJ Gi"),("best-bjj-rash-guard","👕 Best Rashguard")],
    "Takedown":[("best-bjj-rash-guard","👕 Best Rashguard"),("best-bjj-knee-pads","🦵 Best Knee Pads")],
    "Passing":[("best-bjj-knee-pads","🦵 Best Knee Pads"),("best-bjj-rash-guard","👕 Best Rashguard")],
    "Position":[("best-bjj-gi-guide","🥋 Best BJJ Gi"),("best-bjj-mouthguard","🦷 Best Mouthguard")],
    "Escape":[("best-bjj-rash-guard","👕 Best Rashguard"),("best-bjj-knee-pads","🦵 Best Knee Pads")],
    "Transition":[("best-bjj-rash-guard","👕 Best Rashguard"),("best-bjj-gi-guide","🥋 Best BJJ Gi")],
    "Defense":[("best-bjj-mouthguard","🦷 Best Mouthguard"),("best-bjj-rash-guard","👕 Best Rashguard")],
}

# ===== 記事JSONをHTMLに変換 =====
# ===== Markdownライト変換ヘルパー =====
def md_to_html(text: str) -> str:
    """ライトMarkdown (numbered list / bullet list / bold) → HTML変換"""
    import re as _re
    if not text:
        return ""
    lines = text.split("\n")
    out = []
    in_ul = False
    in_ol = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_ul: out.append("</ul>"); in_ul = False
            if in_ol: out.append("</ol>"); in_ol = False
            continue
        # numbered list
        if _re.match(r"^\d+\.\s", stripped):
            if in_ul: out.append("</ul>"); in_ul = False
            if not in_ol: out.append('<ol style="padding-left:20px;margin:8px 0">'); in_ol = True
            item = _re.sub(r"^\d+\.\s*", "", stripped)
            item = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", item)
            out.append(f"<li style=\"color:#c2c2d9;margin-bottom:6px\">{item}</li>")
        # bullet list
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if in_ol: out.append("</ol>"); in_ol = False
            if not in_ul: out.append('<ul style="padding-left:20px;margin:8px 0">'); in_ul = True
            item = stripped[2:].strip()
            item = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", item)
            out.append(f"<li style=\"color:#c2c2d9;margin-bottom:6px\">{item}</li>")
        else:
            if in_ul: out.append("</ul>"); in_ul = False
            if in_ol: out.append("</ol>"); in_ol = False
            para = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
            out.append(f"<p style=\"color:#c2c2d9;margin-bottom:10px\">{para}</p>")
    if in_ul: out.append("</ul>")
    if in_ol: out.append("</ol>")
    return "\n".join(out)


def article_to_html(tech, lang_code, article, all_techniques):
    lang = LANGUAGES[lang_code]
    nav_labels = {
        "en": {"home": "Home", "all": "All Techniques", "category": "Category"},
        "ja": {"home": "ホーム", "all": "全技一覧", "category": "カテゴリ"},
        "pt": {"home": "Início", "all": "Todas as Técnicas", "category": "Categoria"},
    }
    labels = nav_labels[lang_code]

    # リスト or 文字列を安全に文字列化するヘルパー
    def to_str(v):
        if isinstance(v, list): return "\n".join(str(i) for i in v)
        return str(v) if v else ""

    # 同カテゴリの関連技リンク
    related = [t for t in all_techniques if t["category"] == tech["category"] and t["slug"] != tech["slug"]][:5]
    related_links = "\n".join([
        f'<a href="../{lang_code}/{t["slug"]}.html">{t["name"]}</a>'
        for t in related
    ])

    # 言語切替リンク
    # 言語切替ナビ (lang-nav)
    _lang_flags = {"en": "🇺🇸 EN", "ja": "🇯🇵 JA", "pt": "🇧🇷 PT"}
    lang_nav_links = "".join([
        '<a href="../' + lc + '/' + tech["slug"] + '.html"' + (' class="active"' if lc == lang_code else '') + '>' + _lang_flags[lc] + '</a>'
        for lc in LANGUAGES
    ])
    lang_nav = f'<nav class="lang-nav">{lang_nav_links}</nav>'

    keywords_str = ", ".join(article.get("keywords", []))

    # Security: Gemini 出力の title / meta_description は prompt injection 経由で
    # </title>, </script>, `"` を含む可能性がある。html.escape() で HTML 属性・
    # テキスト全てを安全化 (title / meta tags / JSON-LD すべて共通化)。
    # JSON-LD の文字列値は json.dumps で別途 escape する。
    _raw_title = article.get("title", tech["name"])
    _raw_desc = article.get("meta_description", "")
    _html_title = html.escape(_raw_title, quote=True)
    _html_desc = html.escape(_raw_desc, quote=True)
    _keywords_safe = html.escape(keywords_str, quote=True)

    # z223: technique-specific dynamic OG image (auto-post 視覚化)
    # 旧: 全ページ共通 static SVG → SNS share preview generic
    # 新: bjj-app.net /api/og で技 name + category + lang ごとに動的生成
    # cross-origin (wiki.bjj-app.net → bjj-app.net) は SNS scraper 問題なし
    _og_title_q = urllib.parse.quote(tech["name"][:60], safe="")
    # category mapping: tech["category"] は generator 内 tag (technique/sweep/guard 等)
    # → OG endpoint の TECHNIQUE_CONFIG カテゴリ (technique/athlete/history/rules/training) に集約
    _og_cat = "technique"  # 技ページは全て technique カテゴリで統一 (将来 athlete 等は別 generator で)
    _og_image_url = f"https://bjj-app.net/api/og?mode=technique&category={_og_cat}&title={_og_title_q}&lang={lang_code}"

    # JSON-LD: f-string 直挿入だと Gemini 出力の `"`/`\`/`</script>` で破壊される。
    # json.dumps + `.replace("</","<\\/")` で script breakout を封殺。
    # (z143 enrich_sections.py と同じ pattern)
    def _jsonld(payload: dict) -> str:
        s = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        return '<script type="application/ld+json">' + s.replace("</", "<\\/") + '</script>'

    _article_url = f"{SITE_URL}/{lang_code}/{tech['slug']}.html"
    _article_jsonld_block = _jsonld({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": _raw_title,
        "description": _raw_desc,
        "url": _article_url,
        "inLanguage": lang_code,
        "datePublished": "2026-03-13T00:00:00+09:00",
        "dateModified": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+09:00"),
        "author": {"@type": "Organization", "name": "BJJ Wiki", "url": f"{SITE_URL}/"},
        "publisher": {"@type": "Organization", "name": "BJJ Wiki", "url": f"{SITE_URL}/"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": _article_url},
    })
    _breadcrumb_jsonld_block = _jsonld({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "BJJ Wiki",
             "item": f"{SITE_URL}/{lang_code}/index.html"},
            {"@type": "ListItem", "position": 2, "name": _raw_title,
             "item": _article_url},
        ],
    })

    # --- 難易度バー ---
    diff = DIFFICULTY_MAP.get(tech["slug"], ("white","★★☆☆☆","Intermediate"))
    diff_belt, diff_stars, diff_label_txt = diff
    diff_bg  = BELT_BG.get(diff_belt, "#e2e2ee")
    diff_fg  = BELT_FG.get(diff_belt, "#111")
    difficulty_html = (
        f'<div class="difficulty-bar">'
        f'<span class="diff-belt" style="background:{diff_bg};color:{diff_fg}">{diff_belt.upper()}</span>'
        f'<span class="diff-stars">{diff_stars}</span>'
        f'<span class="diff-label">{diff_label_txt}</span>'
        f'</div>'
    )

    # --- ベルトガイドクロスリンク ---
    _belt_guide_map = {
        "white": {"en": ("white-belt-bjj-guide.html","White Belt Guide"), "ja": ("white-belt-bjj-guide.html","白帯ガイド"), "pt": ("white-belt-bjj-guide.html","Guia Faixa Branca")},
        "blue":  {"en": ("blue-belt-bjj-guide.html","Blue Belt Guide"),  "ja": ("blue-belt-bjj-guide.html","青帯ガイド"),  "pt": ("blue-belt-bjj-guide.html","Guia Faixa Azul")},
        "purple":{"en": ("bjj-purple-belt-requirements.html","Purple Belt Requirements"),"ja": ("bjj-purple-belt-requirements.html","紫帯昇格要件"),"pt": ("bjj-purple-belt-requirements.html","Requisitos Faixa Roxa")},
        "brown": {"en": ("bjj-brown-belt-requirements.html","Brown Belt Requirements"),"ja": ("bjj-brown-belt-requirements.html","茶帯昇格要件"),"pt": ("bjj-brown-belt-requirements.html","Requisitos Faixa Marrom")},
        "black": {"en": ("bjj-black-belt-requirements.html","Black Belt Requirements"),"ja": ("bjj-black-belt-requirements.html","黒帯昇格要件"),"pt": ("bjj-black-belt-requirements.html","Requisitos Faixa Preta")},
    }
    _cta_see_guide = {"en":"📖 See Full Guide →","ja":"📖 完全ガイドを見る →","pt":"📖 Ver Guia Completo →"}
    _belt_level_label = {"en":f"{diff_belt.title()} Belt Technique","ja":f"{diff_belt.title()}帯テクニック","pt":f"Técnica Faixa {diff_belt.title()}"}
    if diff_belt in _belt_guide_map and lang_code in _belt_guide_map[diff_belt]:
        _guide_href, _guide_label = _belt_guide_map[diff_belt][lang_code]
        belt_guide_html = (
            f'<div class="belt-guide-box" style="border:2px solid {diff_bg};border-radius:10px;padding:16px;margin:24px 0;background:#0f1420">'
            f'<span style="background:{diff_bg};color:{diff_fg};padding:4px 12px;border-radius:20px;font-size:.85em;font-weight:700">{_belt_level_label[lang_code]}</span>'
            f'<br><a href="../{lang_code}/{_guide_href}" style="color:#e2b714;font-weight:600;text-decoration:none;margin-top:8px;display:inline-block">{_cta_see_guide[lang_code]} {_guide_label}</a>'
            f'</div>'
        )
    else:
        belt_guide_html = ""

    # --- 選手セクション ---
    athlete_label = {"en":"🏆 Elite Athletes Who Use This","ja":"🏆 この技を使うエリート選手","pt":"🏆 Atletas de Elite"}[lang_code]
    athletes_list = ATHLETE_MAP.get(tech["slug"], [])
    if athletes_list:
        chips = "".join([
            f'<a class="athlete-chip" href="../{lang_code}/athlete-{s}.html">'
            f'<span style="font-size:1.2rem">{fl}</span>'
            f'<span><strong style="display:block;font-size:.9rem">{nm}</strong></span></a>'
            for s, nm, fl in athletes_list
        ])
        athletes_html = f'<div class="athletes-section"><h2>{athlete_label}</h2><div class="athlete-chips">{chips}</div></div>'
    else:
        athletes_html = ""

    # --- Yoga クロスリンク ---
    yoga_poses = YOGA_SLUG_MAP.get(tech["slug"], YOGA_CAT_DEFAULTS.get(tech["category"], []))[:3]
    yoga_label  = {"en":"🧘 Yoga Poses to Improve This Technique","ja":"🧘 この技に効くヨガポーズ","pt":"🧘 Yoga para Esta Técnica"}[lang_code]
    yoga_sub    = {"en":"These poses build the flexibility & mobility you need:","ja":"必要な柔軟性・可動域を高めます：","pt":"Melhore sua flexibilidade e mobilidade:"}[lang_code]
    if yoga_poses:
        yoga_chips = "".join([
            f'<a class="yoga-chip" href="https://t307239.github.io/yoga-wiki/en/{sl}.html" target="_blank" rel="noopener">🧘 {nm}</a>'
            for sl, nm in yoga_poses
        ])
        yoga_html = f'<div class="yoga-box"><h3>{yoga_label}</h3><p>{yoga_sub}</p><div class="yoga-chips">{yoga_chips}</div></div>'
    else:
        yoga_html = ""

    # --- コンディショニングボックス ---
    _strength_slugs = {"double-leg-takedown","single-leg-takedown","hip-throw","o-soto-gari",
                       "harai-goshi","ippon-seoi-nage","snap-down","torreando-pass",
                       "knee-slice-pass","leg-drag-pass","x-pass","heel-hook","kimura",
                       "americana","rear-naked-choke","hip-escape","bridge-and-roll",
                       "guard-retention","back-take","deep-half-guard","wrestling"}
    _nutrition_slugs = {"bjj-training-tips","bjj-competition-guide","bjj-belt-system",
                        "white-belt-bjj-guide","blue-belt-bjj-guide","bjj-strength-training",
                        "double-leg-takedown","single-leg-takedown","wrestling",
                        "bjj-competition-calendar-2026"}
    _str_lbl = {"en":("⚡ Strength & Conditioning","Build explosive power for this technique:","bjj-strength-training.html","💪 Strength Training Guide →"),
                "ja":("⚡ 筋トレ・コンディショニング","この技の爆発力を高めるトレーニング:","bjj-strength-training.html","💪 筋トレガイドを見る →"),
                "pt":("⚡ Força & Condicionamento","Desenvolva potência explosiva para esta técnica:","bjj-strength-training.html","💪 Guia de Musculação →")}
    _nut_lbl = {"en":("🥗 BJJ Nutrition","Fuel your training with the right diet:","bjj-diet-nutrition.html","🥗 Nutrition Guide →"),
                "ja":("🥗 BJJ栄養学","正しい食事で練習パフォーマンスを最大化:","bjj-diet-nutrition.html","🥗 栄養ガイドを見る →"),
                "pt":("🥗 Nutrição para BJJ","Alimente seu treino com a dieta certa:","bjj-diet-nutrition.html","🥗 Guia de Nutrição →")}
    def _cond_box(lbl, sub, pg, cta):
        return (f'<div class="conditioning-box" style="background:#1a2a1a;border-left:4px solid #4ade80;border-radius:8px;padding:14px 18px;margin:20px 0;">'
                f'<p style="margin:0 0 6px;font-weight:700;color:#4ade80;">{lbl}</p>'
                f'<p style="margin:0 0 10px;font-size:13px;color:#ccc;">{sub}</p>'
                f'<a href="{pg}" style="display:inline-block;background:#4ade80;color:#0a0a1a;padding:6px 14px;border-radius:6px;text-decoration:none;font-weight:700;font-size:13px;">{cta}</a></div>')
    conditioning_html = ""
    if tech["slug"] in _strength_slugs:
        conditioning_html += _cond_box(*_str_lbl[lang_code])
    if tech["slug"] in _nutrition_slugs:
        conditioning_html += _cond_box(*_nut_lbl[lang_code])

    # --- ギアボックス ---
    gear_items  = GEAR_CAT_MAP.get(tech["category"], [])
    gear_label  = {"en":"⚙️ Recommended Gear","ja":"⚙️ おすすめギア","pt":"⚙️ Equipamento Recomendado"}[lang_code]
    if gear_items:
        gear_links = "".join([
            f'<a class="gear-link" href="{sl}.html">{nm}</a>'
            for sl, nm in gear_items
        ])
        gear_html = f'<div class="gear-box"><h3>{gear_label}</h3><div class="gear-links">{gear_links}</div></div>'
    else:
        gear_html = ""

    # --- Beehiiv CTA ---
    # z260o: CLAUDE.md rule -3 (嘘より沈黙) — fake "2,000+ Practitioners" 削除し honest copy に。
    # generate_bjj_wiki.py の generator が再生成時に 2,000+ を再注入する 先祖返り を恒久 fix
    # (z255jjjj-WW Round9 の `fix_fake_subscriber_count.py` を template source 側でも適用)
    bee_title = {"en":"📬 Free BJJ Newsletter","ja":"📬 BJJ 無料ニュースレター","pt":"📬 Newsletter BJJ Grátis"}[lang_code]
    bee_desc  = {"en":"Get the free BJJ White Belt Guide plus technique breakdowns, training tips & exclusive content every week. No spam. Unsubscribe anytime.","ja":"無料BJJ白帯ガイド＋毎週の技術解説・練習のコツ・独占コンテンツ。スパムなし。いつでも配信停止可能。","pt":"Receba o Guia Gratuito do Brás Branco + análises de técnicas semanais, dicas de treino e conteúdo exclusivo. Sem spam. Desinscrever a qualquer momento."}[lang_code]
    bee_btn   = {"en":"Get Free Access →","ja":"無料アクセスを取得 →","pt":"Obter Acesso Gratuito →"}[lang_code]
    beehiiv_html = (
        f'<div class="beehiiv-wrap"><h3>{bee_title}</h3>'
        f'<p>{bee_desc}</p>'
        f'<a class="beehiiv-btn" href="https://bjj-wiki.beehiiv.com/subscribe" target="_blank" rel="noopener">{bee_btn}</a>'
        f'</div>'
    )

    # CTA strings that can't have backslash in f-string expression (Python < 3.12)
    _cta_video_msg = {
        "en": "🥋 Can’t find the exact detail you need? Save your instructor’s video URL in ",
        "ja": "🥋 道場のコーチのディテールが違う場合は、",
        "pt": "🥋 N\u00e3o encontrou o detalhe que precisa? Salve o URL do seu instrutor no ",
    }[lang_code]
    _cta_video_link = {
        "en": "BJJ App (free) →",
        "ja": "BJJ App（無料）のTechnique Logに保存しよう →",
        "pt": "BJJ App (grátis) →",
    }[lang_code]
    _related_video_label = {
        "en": "Related Video",
        "ja": "関連動画",
        "pt": "Vídeo Relacionado",
    }[lang_code]
    _video_sub_label = {
        "en": "Watch step-by-step breakdowns from black belt instructors:",
        "ja": "黒帯インストラクターのステップ解説を見る：",
        "pt": "Assista breakdowns de instrutores faixa preta:",
    }[lang_code]
    _search_label = {
        "en": "▶ Search ",
        "ja": "▶ ",
        "pt": "▶ Buscar ",
    }[lang_code]
    _search_suffix = {
        "en": " on YouTube",
        "ja": " をYouTubeで検索",
        "pt": " no YouTube",
    }[lang_code]
    _warn_label = {
        "en": "⚠️ White Belt Warnings",
        "ja": "⚠️ 白帯の注意点",
        "pt": "⚠️ Avisos para Faixa Branca",
    }[lang_code]
    _grips_label = {
        "en": "Grips &amp; Mechanics",
        "ja": "グリップ・生体力学",
        "pt": "Pegadas e Mecânica",
    }[lang_code]
    _drills_label = {
        "en": "Drill Progressions",
        "ja": "ドリル段階",
        "pt": "Progressão de Drills",
    }[lang_code]
    _when_counters_label = {
        "en": "When to Use &amp; Counters",
        "ja": "使うタイミング・カウンター",
        "pt": "Quando Usar e Defesas",
    }[lang_code]
    _yt_btn_label = {
        "en": "\u25b6 Watch on YouTube",
        "ja": "\u25b6 YouTube\u3067\u52d5\u753b\u3092\u898b\u308b",
        "pt": "\u25b6 Assistir no YouTube",
    }[lang_code]

    # J: Dynamic Contextual CTA based on technique category
    _cat = tech.get("category", "").lower()
    if lang_code == "en":
        if "submission" in _cat or "choke" in _cat or "lock" in _cat:
            _cta_headline = f"Landed your first {tech['name']}? Log every tap."
            _cta_sub = "Track submissions, sessions & streaks — free forever."
        elif "guard" in _cat:
            _cta_headline = f"Building your {tech['name']} game?"
            _cta_sub = f"Log every {tech['name']} attempt and measure your progress in BJJ App."
        elif "sweep" in _cat:
            _cta_headline = f"How many times did you hit {tech['name']} this week?"
            _cta_sub = "Track sweep success rate and training streaks — free."
        elif "pass" in _cat:
            _cta_headline = f"Drilling your {tech['name']} pass?"
            _cta_sub = "Log guard pass success rate and sparring sessions in BJJ App."
        elif "escape" in _cat or "defense" in _cat:
            _cta_headline = f"Surviving with {tech['name']}? Track your progress."
            _cta_sub = "Log survival rate, escapes & training consistency — free forever."
        elif "takedown" in _cat or "throw" in _cat:
            _cta_headline = f"Shot a {tech['name']} today? Record it."
            _cta_sub = "Track takedown attempts, training sessions & improvement — free."
        else:
            _cta_headline = f"Practicing {tech['name']} today?"
            _cta_sub = "Log sessions, track techniques & streaks — free forever."
    elif lang_code == "ja":
        _cta_headline = f"{tech['name']}を練習中ですか？"
        _cta_sub = "練習回数・テクニック・連続記録を一元管理。ずっと無料。"
    else:
        _cta_headline = f"Praticando {tech['name']} hoje?"
        _cta_sub = "Registre treinos, técnicas e sequências — sempre gratuito."

    # I: Semantic Links section
    _sem_slugs = article.get("semantic_links", [])
    if isinstance(_sem_slugs, list) and _sem_slugs:
        _sem_items = []
        for _s in _sem_slugs[:4]:
            _t = next((t for t in all_techniques if t["slug"] == _s), None)
            if _t:
                _sem_items.append(f'<a href="../{lang_code}/{_s}.html" style="display:inline-block;background:var(--card,#18181b);border:1px solid var(--border,rgba(255,255,255,0.10));border-radius:8px;padding:8px 14px;color:var(--accent,#7c3aed);text-decoration:none;font-size:.85rem;font-weight:600">{_t["name"]} →</a>')
        if _sem_items:
            _dig_label = {"en": "Dig Deeper", "ja": "関連テクニックを深掘り", "pt": "Aprofunde-se"}[lang_code]
            _dig_sub = {"en": "Techniques that connect with " + tech["name"], "ja": tech["name"] + "と組み合わせて使う技", "pt": "Técnicas que se conectam com " + tech["name"]}[lang_code]
            _semantic_links_html = f'<div style="background:var(--card,#18181b);border:1px solid var(--border,rgba(255,255,255,0.10));border-radius:12px;padding:20px 24px;margin:28px 0"><h3 style="font-size:.9rem;font-weight:700;color:var(--accent,#7c3aed);margin-bottom:6px">🔗 {_dig_label}</h3><p style="font-size:.8rem;color:var(--muted,#64748b);margin-bottom:14px">{_dig_sub}</p><div style="display:flex;flex-wrap:wrap;gap:8px">{"".join(_sem_items)}</div></div>'
        else:
            _semantic_links_html = ""
    else:
        _semantic_links_html = ""

    return f"""<!DOCTYPE html>
<html lang="{lang_code}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.googletagmanager.com">
<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
<link rel="dns-prefetch" href="https://www.google-analytics.com">
<title>{_html_title} | BJJ Wiki</title>
<meta name="description" content="{_html_desc}">
<meta name="keywords" content="{_keywords_safe}">
<meta property="og:title" content="{_html_title}">
<meta property="og:description" content="{_html_desc}">
<meta property="og:type" content="article">
    <meta property="og:site_name" content="BJJ Wiki">
<meta property="og:url" content="{SITE_URL}/{lang_code}/{tech['slug']}.html">
<meta property="og:image" content="{_og_image_url}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@bjj_wiki">
<meta name="twitter:title" content="{_html_title}">
<meta name="twitter:description" content="{html.escape(_raw_desc[:200], quote=True)}">
<meta name="twitter:image" content="{_og_image_url}">
<link rel="canonical" href="{SITE_URL}/{lang_code}/{tech['slug']}.html">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/en/{tech['slug']}.html">
<link rel="alternate" hreflang="en" href="{SITE_URL}/en/{tech['slug']}.html">
<link rel="alternate" hreflang="ja" href="{SITE_URL}/ja/{tech['slug']}.html">
<link rel="alternate" hreflang="pt" href="{SITE_URL}/pt/{tech['slug']}.html">
<link rel="icon" href="{SITE_URL}/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" sizes="180x180" href="{SITE_URL}/apple-touch-icon.png">
<link rel="stylesheet" href="/wiki-v2.css">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-7LM8L3TRZM"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-7LM8L3TRZM');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5529701443220352" crossorigin="anonymous"></script>
{_article_jsonld_block}
{_breadcrumb_jsonld_block}
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "What is {tech['name']} in BJJ?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "{'It is a fundamental BJJ technique in the ' + tech.get('category','grappling') + ' category. See the full breakdown above.' if lang_code=='en' else tech['name'] + 'はBJJの技です。詳細は上記を参照。' if lang_code=='ja' else tech['name'] + ' é uma técnica de BJJ. Veja o detalhamento completo acima.'}"
      }}
    }},
    {{
      "@type": "Question",
      "name": "{'How do I learn ' + tech['name'] + '?' if lang_code=='en' else tech['name'] + 'の習得方法は？' if lang_code=='ja' else 'Como aprender ' + tech['name'] + '?'}",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "{'Follow the step-by-step guide above, drill with a partner, and watch competition footage. BJJ Fanatics instructionals also cover this technique in depth.' if lang_code=='en' else '上記のステップバイステップガイドに従い、パートナーとドリルし、試合映像を見てください。' if lang_code=='ja' else 'Siga o guia passo a passo acima, treine com um parceiro e assista a filmagens de competição.'}"
      }}
    }}
  ]
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to do {tech['name']} in BJJ",
  "description": "Step-by-step guide to executing {tech['name']} in Brazilian Jiu-Jitsu",
  "step": [
    {{
      "@type": "HowToStep",
      "name": "{'Set up the position' if lang_code=='en' else 'ポジションのセットアップ' if lang_code=='ja' else 'Configurar a posição'}",
      "text": "{'Position yourself correctly relative to your opponent before attempting the technique.' if lang_code=='en' else '技を試みる前に相手に対して正しいポジションを取る。' if lang_code=='ja' else 'Posicione-se corretamente em relação ao seu oponente antes de tentar a técnica.'}"
    }},
    {{
      "@type": "HowToStep",
      "name": "{'Execute the technique' if lang_code=='en' else '技の実行' if lang_code=='ja' else 'Executar a técnica'}",
      "text": "{'Apply the technique with proper mechanics as described in the guide above.' if lang_code=='en' else '上記ガイドの正しいメカニクスで技を実行する。' if lang_code=='ja' else 'Aplique a técnica com a mecânica adequada conforme descrito no guia acima.'}"
    }},
    {{
      "@type": "HowToStep",
      "name": "{'Finish or transition' if lang_code=='en' else 'フィニッシュまたはトランジション' if lang_code=='ja' else 'Finalizar ou fazer transição'}",
      "text": "{'Finish the submission or transition to a dominant position. Drill until the movement is automatic.' if lang_code=='en' else 'サブミッションで仕留めるか、支配的なポジションにトランジション。動きが自動になるまでドリル。' if lang_code=='ja' else 'Finalize a submissão ou faça transição para uma posição dominante. Treine até o movimento ser automático.'}"
    }}
  ]
}}
</script>
</head>
<body>
<div id="read-progress"></div>
<div class="container">
  <header>
    <a href="../{lang_code}/index.html" class="logo">🥋 BJJ Wiki</a>
    {lang_nav}
  </header>

  <span class="badge">{tech['category']}</span><br>
  <span class="belt belt-{to_str(article.get('belt_level','white')).lower().split('/')[0].strip()}">{to_str(article.get('belt_level','All Levels'))}</span>
  <h1>{to_str(article.get('h1', tech['name']))}</h1>
  {difficulty_html}
  {belt_guide_html}
  <p>{md_to_html(to_str(article.get('technique_overview_md', article.get('intro', ''))))}</p>

  <div id="toc" class="toc">
    <div class="toc-title">{'Contents' if lang_code=='en' else '目次' if lang_code=='ja' else 'Conteúdo'}</div>
    <ul class="toc-list" id="toc-list"></ul>
  </div>

  <h2>{_grips_label}</h2>
  <div class="card">{md_to_html(to_str(article.get('biomechanics_and_grips_md', article.get('how_to', ''))))}</div>

  <h2 style="color:#fca5a5;border-left-color:#dc2626">{_warn_label}</h2>
  <div class="card" style="background:#1a0505;border-color:#dc262640">{md_to_html(to_str(article.get('white_belt_warning_md', article.get('key_details', ''))))}</div>

  <h2>{_drills_label}</h2>
  <div class="card">{md_to_html(to_str(article.get('drill_progressions_md', article.get('variations', ''))))}</div>

  <h2>{_when_counters_label}</h2>
  <div class="card">{md_to_html(to_str(article.get('counters_and_when_to_use_md', article.get('when_to_use', '') + ' ' + article.get('counters', ''))))}</div>

  <h2>{_related_video_label}</h2>
  <div class="card" style="background:#0a0a1a;border-color:#3a3a6a">
    <p style="color:#9ca3af;font-size:.9rem;margin-bottom:12px">{_video_sub_label}</p>
    <a class="yt-search-btn" href="https://www.youtube.com/results?search_query={tech['name'].replace(' ','+')}+BJJ+tutorial" target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24"><path d="M23.495 6.205a3.007 3.007 0 0 0-2.088-2.088c-1.87-.501-9.396-.501-9.396-.501s-7.507-.01-9.396.501A3.007 3.007 0 0 0 .527 6.205a31.247 31.247 0 0 0-.522 5.805 31.247 31.247 0 0 0 .522 5.783 3.007 3.007 0 0 0 2.088 2.088c1.868.502 9.396.502 9.396.502s7.506 0 9.396-.502a3.007 3.007 0 0 0 2.088-2.088 31.247 31.247 0 0 0 .5-5.783 31.247 31.247 0 0 0-.5-5.805zM9.609 15.601V8.408l6.264 3.602z"/></svg>
      {_search_label}{tech['name']}{_search_suffix}
    </a>
    <div style="margin-top:14px;padding:12px 16px;background:#0d2010;border:1px solid #22c55e40;border-radius:8px">
      <p style="color:#86efac;font-size:.85rem;margin:0">
        {_cta_video_msg}
        <a href="https://bjj-app.net/login" style="color:#4ade80;font-weight:700;text-decoration:none">{_cta_video_link}</a>
      </p>
    </div>
  </div>

  {athletes_html}

    {athletes_html}

  {'<!-- Pro Tip --><div class="pro-tip"><div class="pro-tip-label">💡 ' + ('PRO TIP' if lang_code=="en" else 'プロのコツ' if lang_code=="ja" else 'DICA DE PRO') + '</div><p>' + to_str(article.get("pro_tip","")).replace(chr(10),'<br>') + '</p></div>' if article.get('pro_tip') else ''}

  {conditioning_html}
  <!-- ルールセットクロスリンク -->
  <div style="background:#0d1a2e;border-left:4px solid #3a86ff;border-radius:8px;padding:1rem 1.2rem;margin:1.5rem 0">
    <p style="font-size:.9rem;font-weight:700;color:#93c5fd;margin-bottom:.6rem">{"📋 Competition Rules" if lang_code=="en" else "📋 試合ルール" if lang_code=="ja" else "📋 Regras de Competição"}</p>
    <div style="display:flex;gap:.75rem;flex-wrap:wrap">
      <a href="ibjjf-rules.html" style="background:#111827;border:1px solid #1e3a5f;border-radius:6px;padding:.5rem .9rem;color:#93c5fd;text-decoration:none;font-size:.82rem">{"IBJJF Rules →" if lang_code=="en" else "IBJJFルール →" if lang_code=="ja" else "Regras IBJJF →"}</a>
      <a href="adcc-rules.html" style="background:#111827;border:1px solid #1e3a5f;border-radius:6px;padding:.5rem .9rem;color:#93c5fd;text-decoration:none;font-size:.82rem">{"ADCC Rules →" if lang_code=="en" else "ADCCルール →" if lang_code=="ja" else "Regras ADCC →"}</a>
      <a href="bjj-competition-guide.html" style="background:#111827;border:1px solid #1e3a5f;border-radius:6px;padding:.5rem .9rem;color:#93c5fd;text-decoration:none;font-size:.82rem">{"Competition Guide →" if lang_code=="en" else "競技ガイド →" if lang_code=="ja" else "Guia de Competição →"}</a>
    </div>
  </div>
  <!-- 試合準備クロスリンク -->
  <div style="background:#1a0d2e;border-left:4px solid #ff6b6b;border-radius:8px;padding:14px 18px;margin:20px 0">
    <strong style="color:#ff6b6b;font-size:.9rem">{"⚕️ Training Safety & Performance" if lang_code=="en" else "⚕️ トレーニングの安全とパフォーマンス" if lang_code=="ja" else "⚕️ Segurança e Performance no Treino"}</strong>
    <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:10px">
      <a href="bjj-injury-prevention.html" style="background:#2a1a3a;color:#fff;padding:6px 14px;border-radius:20px;text-decoration:none;font-size:.85rem">{"🛡️ Injury Prevention" if lang_code=="en" else "🛡️ 怪我予防" if lang_code=="ja" else "🛡️ Prevenção de Lesões"}</a>
      <a href="bjj-warm-up-routine.html" style="background:#2a1a3a;color:#fff;padding:6px 14px;border-radius:20px;text-decoration:none;font-size:.85rem">{"🔥 Warm-Up" if lang_code=="en" else "🔥 ウォームアップ" if lang_code=="ja" else "🔥 Aquecimento"}</a>
      <a href="bjj-weight-cutting.html" style="background:#2a1a3a;color:#fff;padding:6px 14px;border-radius:20px;text-decoration:none;font-size:.85rem">{"⚖️ Weight Cutting" if lang_code=="en" else "⚖️ 減量" if lang_code=="ja" else "⚖️ Corte de Peso"}</a>
      <a href="bjj-mental-game.html" style="background:#2a1a3a;color:#fff;padding:6px 14px;border-radius:20px;text-decoration:none;font-size:.85rem">{"🧠 Mental Game" if lang_code=="en" else "🧠 メンタル強化" if lang_code=="ja" else "🧠 Jogo Mental"}</a>
      <a href="bjj-competition-prep-checklist.html" style="background:#2a1a3a;color:#fff;padding:6px 14px;border-radius:20px;text-decoration:none;font-size:.85rem">{"📋 Comp Prep" if lang_code=="en" else "📋 試合前チェック" if lang_code=="ja" else "📋 Prep Competição"}</a>
    </div>
  </div>
  <!-- CTA: app registration only (CLAUDE.md: affiliate links prohibited) -->

  {yoga_html}
  {gear_html}

  <!-- FAQ Section (long-tail SEO) -->
  <div style="margin:32px 0">
    <h2>{'Common BJJ Problems & FAQ' if lang_code=='en' else 'よくある質問・トラブル' if lang_code=='ja' else 'Perguntas Frequentes'}</h2>
    {(('<div class="faq"><div class="faq-q">Q: ' + str(article.get('faq_q1','')) + '</div><p>' + str(article.get('faq_a1','')) + '</p></div>') if article.get('faq_q1') else '')}
    {(('<div class="faq"><div class="faq-q">Q: ' + str(article.get('faq_q2','')) + '</div><p>' + str(article.get('faq_a2','')) + '</p></div>') if article.get('faq_q2') else '')}
    {(('<div class="faq"><div class="faq-q">Q: ' + str(article.get('faq_q3','')) + '</div><p>' + str(article.get('faq_a3','')) + '</p></div>') if article.get('faq_q3') else '')}
  </div>

  <!-- Related Techniques Card Grid -->
  <div style="background:#0f1420;border:1px solid #1f2840;border-radius:12px;padding:24px;margin:32px 0">
    <h3 style="font-size:1rem;font-weight:700;color:#7c6af7;margin-bottom:16px">🥋 {'Related Techniques' if lang_code=='en' else '関連技' if lang_code=='ja' else 'Técnicas Relacionadas'}</h3>
    <div style="display:flex;flex-wrap:wrap;gap:8px">
      {related_links}
    </div>
  </div>

  {beehiiv_html}

  <!-- Semantic Dig Deeper (I: Semantic Linking) -->
  {_semantic_links_html}

  <!-- BJJ App CTA Banner (J: Dynamic Contextual CTA) -->
  <div style="background:var(--card,#18181b);border:1px solid rgba(233,69,96,0.3);border-radius:12px;padding:20px 24px;margin:32px 0;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap">
    <div>
      <p style="margin:0 0 4px;font-size:.95rem;font-weight:700;color:#e2e2ee">🥋 {_cta_headline}</p>
      <p style="margin:0;font-size:.82rem;color:#7a7a9a">{_cta_sub}</p>
    </div>
    <a href="https://bjj-app.net/login" target="_blank" rel="noopener" onclick="gtag&&gtag('event','app_cta_click',{{page:location.pathname,lang:'{lang_code}',tech:'{tech['slug']}'}})" style="flex-shrink:0;background:var(--accent2,#e94560);color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-size:.85rem;font-weight:700;white-space:nowrap">{'Try Free →' if lang_code=='en' else '無料で試す →' if lang_code=='ja' else 'Experimente Grátis →'}</a>
  </div>

  <!-- Share Bar -->
  <div class="share-bar">
    <p>{'Share this technique' if lang_code=='en' else 'この技をシェア' if lang_code=='ja' else 'Compartilhar esta técnica'}</p>
    <div class="share-btns">
      <a class="share-btn x" href="https://twitter.com/intent/tweet?url={SITE_URL}/{lang_code}/{tech['slug']}.html&text={urllib.parse.quote_plus(tech['name'])}+%23BJJ+%23bjjwiki" target="_blank" rel="noopener noreferrer">𝕏 {'Post on X' if lang_code=='en' else 'Xに投稿' if lang_code=='ja' else 'Postar no X'}</a>
      <a class="share-btn reddit" href="https://www.reddit.com/submit?url={SITE_URL}/{lang_code}/{tech['slug']}.html&title={urllib.parse.quote_plus(tech['name'])}" target="_blank" rel="noopener noreferrer">⬆ Reddit</a>
      <button class="share-btn copy" onclick="navigator.clipboard.writeText('{SITE_URL}/{lang_code}/{tech['slug']}.html').then(()=>{{this.textContent='✓ {'Copied!' if lang_code=='en' else 'コピー済！' if lang_code=='ja' else 'Copiado!'}';setTimeout(()=>this.textContent='📋 {'Copy Link' if lang_code=='en' else 'リンクコピー' if lang_code=='ja' else 'Copiar'}',2000)}})">📋 {'Copy Link' if lang_code=='en' else 'リンクコピー' if lang_code=='ja' else 'Copiar'}</button>
      <a class="yt-search-btn" href="https://www.youtube.com/results?search_query={tech['name'].replace(' ','+')}+BJJ+tutorial" target="_blank" rel="noopener"><svg viewBox="0 0 24 24"><path d="M23.495 6.205a3.007 3.007 0 0 0-2.088-2.088c-1.87-.501-9.396-.501-9.396-.501s-7.507-.01-9.396.501A3.007 3.007 0 0 0 .527 6.205a31.247 31.247 0 0 0-.522 5.805 31.247 31.247 0 0 0 .522 5.783 3.007 3.007 0 0 0 2.088 2.088c1.868.502 9.396.502 9.396.502s7.506 0 9.396-.502a3.007 3.007 0 0 0 2.088-2.088 31.247 31.247 0 0 0 .5-5.783 31.247 31.247 0 0 0-.5-5.805zM9.609 15.601V8.408l6.264 3.602z"/></svg> {_yt_btn_label}</a>
    </div>
  </div>

  <footer>
    <p>BJJ Wiki — {'The free BJJ technique encyclopedia' if lang_code=='en' else '無料BJJ技術百科事典' if lang_code=='ja' else 'A enciclopédia gratuita de técnicas de BJJ'}</p>
    <p style="margin-top:8px"><a href="../privacy.html" style="color:var(--muted)">Privacy Policy</a></p>
  </footer>
</div>
  <!-- z175: legacy newsletter `id="float-cta"` removed.
       Newsletter signup remains in `<div class="beehiiv-wrap">` mid-article.
       App login floating CTA is added by patch_funnel_cta.py post-generation
       (idempotent insertion as `id="z175-float"`). Avoids visual collision
       with the new login float at bottom-right. -->
  <button id="back-to-top" aria-label="Back to top" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>
  <script>
  (function(){{
    // Reading progress bar
    var prog=document.getElementById('read-progress');
    // Back to top
    var btn=document.getElementById('back-to-top');
    window.addEventListener('scroll',function(){{
      var scrolled=window.scrollY;
      var total=document.body.scrollHeight-window.innerHeight;
      if(total>0){{prog.style.width=(scrolled/total*100)+'%';}}
      if(scrolled>300){{btn.style.display='flex';}}else{{btn.style.display='none';}}
    }},{{passive:true}});
    // Auto TOC from h2 elements
    var headings=document.querySelectorAll('h2');
    if(headings.length>=3){{
      var tocEl=document.getElementById('toc');
      var listEl=document.getElementById('toc-list');
      if(tocEl&&listEl){{
        headings.forEach(function(h,i){{
          if(!h.id)h.id='section-'+i;
          var id=h.id;
          var li=document.createElement('li');
          var a=document.createElement('a');
          a.href='#'+id;
          a.textContent=h.textContent;
          li.appendChild(a);
          listEl.appendChild(li);
        }});
        tocEl.style.display='block';
      }}
    }}
  }})();
  </script>
</body>
</html>"""

# ===== カテゴリ別インデックスページ =====
def generate_category_index(lang_code, techniques_by_category):
    lang = LANGUAGES[lang_code]
    titles = {"en": "All BJJ Techniques", "ja": "全BJJ技一覧", "pt": "Todas as Técnicas de BJJ"}
    descs  = {
        "en": "Complete encyclopedia of Brazilian Jiu-Jitsu techniques. Learn guards, passes, submissions, sweeps and more.",
        "ja": "ブラジリアン柔術（BJJ）の技術百科事典。ガード、パス、絞め技、関節技、スイープを網羅。",
        "pt": "Enciclopédia completa de técnicas de Jiu-Jitsu Brasileiro. Aprenda guardas, passagens, finalizações e muito mais."
    }
    # XSS 対策: title/desc は静的辞書だが将来の拡張に備えて html.escape
    _title_safe = html.escape(titles[lang_code], quote=True)
    _desc_safe = html.escape(descs[lang_code], quote=True)
    _page_url = f"{SITE_URL}/{lang_code}/index.html"

    cards = ""
    for cat, techs in sorted(techniques_by_category.items()):
        links = "".join([f'<a href="{t["slug"]}.html">{t["name"]}</a>' for t in techs])
        cards += f'<div class="cat-card"><h2>{cat}</h2><div class="tech-links">{links}</div></div>'

    # z130/z133/z136/z137/z138 と同等の SEO メタを全て付与 (tech ページ template と同水準)
    _breadcrumb_jsonld = '<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "BJJ Wiki", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": titles[lang_code], "item": _page_url},
        ],
    }, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + '</script>'

    return f"""<!DOCTYPE html>
<html lang="{lang_code}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_title_safe} | BJJ Wiki</title>
<meta name="description" content="{_desc_safe}">
<meta property="og:site_name" content="BJJ Wiki">
<meta property="og:type" content="website">
<meta property="og:url" content="{_page_url}">
<meta property="og:title" content="{_title_safe}">
<meta property="og:description" content="{_desc_safe}">
<meta property="og:image" content="{SITE_URL}/og-image.svg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@bjj_wiki">
<meta name="twitter:title" content="{_title_safe}">
<meta name="twitter:description" content="{_desc_safe}">
<meta name="twitter:image" content="{SITE_URL}/og-image.svg">
<link rel="canonical" href="{_page_url}">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/en/index.html">
<link rel="alternate" hreflang="en" href="{SITE_URL}/en/index.html">
<link rel="alternate" hreflang="ja" href="{SITE_URL}/ja/index.html">
<link rel="alternate" hreflang="pt" href="{SITE_URL}/pt/index.html">
<link rel="icon" href="{SITE_URL}/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" sizes="180x180" href="{SITE_URL}/apple-touch-icon.png">
<link rel="stylesheet" href="/wiki-v2.css">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-7LM8L3TRZM"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-7LM8L3TRZM');</script>
{_breadcrumb_jsonld}
</head>
<body>
<div class="container">
  <header><a href="../index.html" class="logo">BJJ<span>Wiki</span></a></header>
  <h1>{_title_safe}</h1>
  <p class="subtitle">{_desc_safe}</p>
  {cards}
  <footer><p>BJJ Wiki</p></footer>
</div>
</body>
</html>"""

# ===== トップページ =====
def generate_index():
    # z130/z133/z136 水準の SEO メタ + WebSite JSON-LD + hreflang を全装備
    _title = "BJJ Wiki — Brazilian Jiu-Jitsu Technique Encyclopedia"
    _desc = "Free multilingual encyclopedia of Brazilian Jiu-Jitsu techniques. Available in English, Japanese and Portuguese."
    _website_jsonld = '<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "BJJ Wiki",
        "url": f"{SITE_URL}/",
        "description": _desc,
        "inLanguage": ["en", "ja", "pt"],
        "publisher": {"@type": "Organization", "name": "BJJ Wiki", "url": f"{SITE_URL}/"},
    }, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + '</script>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_title}</title>
<meta name="description" content="{_desc}">
<meta property="og:site_name" content="BJJ Wiki">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/">
<meta property="og:title" content="{_title}">
<meta property="og:description" content="{_desc}">
<meta property="og:image" content="{SITE_URL}/og-image.svg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@bjj_wiki">
<meta name="twitter:title" content="{_title}">
<meta name="twitter:description" content="{_desc}">
<meta name="twitter:image" content="{SITE_URL}/og-image.svg">
<link rel="canonical" href="{SITE_URL}/">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/en/index.html">
<link rel="alternate" hreflang="en" href="{SITE_URL}/en/index.html">
<link rel="alternate" hreflang="ja" href="{SITE_URL}/ja/index.html">
<link rel="alternate" hreflang="pt" href="{SITE_URL}/pt/index.html">
<link rel="icon" href="{SITE_URL}/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" sizes="180x180" href="{SITE_URL}/apple-touch-icon.png">
<link rel="stylesheet" href="/wiki-v2.css">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-7LM8L3TRZM"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-7LM8L3TRZM');</script>
{_website_jsonld}
</head>
<body>
<div class="container">
  <div class="logo">BJJ<span>Wiki</span></div>
  <p class="subtitle">The free Brazilian Jiu-Jitsu technique encyclopedia</p>
  <div class="lang-grid">
    <a class="lang-btn" href="en/index.html">
      <div class="lang-flag">🇺🇸</div>
      <div class="lang-name">English</div>
      <div class="lang-sub">Browse in English</div>
    </a>
    <a class="lang-btn" href="ja/index.html">
      <div class="lang-flag">🇯🇵</div>
      <div class="lang-name">日本語</div>
      <div class="lang-sub">日本語で読む</div>
    </a>
    <a class="lang-btn" href="pt/index.html">
      <div class="lang-flag">🇧🇷</div>
      <div class="lang-name">Português</div>
      <div class="lang-sub">Ler em Português</div>
    </a>
  </div>
  <footer><p>BJJ Wiki — Free & Open Knowledge</p></footer>
</div>
</body>
</html>"""

# ===== キャッシュ管理 =====
def load_cache():
    path = os.path.join(SITE_DIR, "cache", "generated.json")
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return {}

def save_cache(cache):
    path = os.path.join(SITE_DIR, "cache", "generated.json")
    with open(path, "w", encoding="utf-8") as f: json.dump(cache, f, ensure_ascii=False, indent=2)

# ===== メイン =====

def _validate_article_structure(html: str, slug: str, lang_code: str) -> bool:
    """
    生成された HTML が最低品質基準を満たしているかチェック。
    基準: H2 >= 4 / 内部リンク >= 2 / FAQ セクション存在
    合格 → True (キャッシュ登録)
    不合格 → False (キャッシュ非登録 → 次回実行で再生成)
    """
    h2_count = len(re.findall(r"<h2[\s>]", html, re.IGNORECASE))
    internal_links = re.findall(r'href=["\']\.\.\/[a-z]{2}\/[a-z][^"\']+\.html["\']', html)
    has_faq = bool(re.search(r'class=["\']faq-q["\']', html))

    ok = h2_count >= 4 and len(internal_links) >= 2 and has_faq
    if not ok:
        print(
            f"[WARN] {lang_code}/{slug}: 品質ゲート不合格 — "
            f"H2:{h2_count}/4+ 内部リンク:{len(internal_links)}/2+ "
            f"FAQ:{'✓' if has_faq else '✗'} → キャッシュ非登録（次回再生成）"
        )
    return ok


def _fetch_low_quality_slugs():
    """F: Supabase から quality_score 低い順にスラッグを取得して優先度付き再生成キューを返す"""
    supabase_url = os.environ.get("SUPABASE_URL", "")
    service_key  = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not supabase_url or not service_key:
        return []
    try:
        proj_id = supabase_url.split("//")[1].split(".")[0]
        mgmt_url = f"https://api.supabase.com/v1/projects/{proj_id}/database/query"
        sql = ("SELECT wp.slug, wt.quality_score FROM wiki_translations wt "
               "JOIN wiki_pages wp ON wp.id = wt.page_id "
               "WHERE wt.language_code = 'en' AND wt.quality_score IS NOT NULL "
               "ORDER BY wt.quality_score ASC LIMIT 200")
        data = json.dumps({"query": sql}).encode()
        req = urllib.request.Request(mgmt_url, data=data,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {service_key}"},
            method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            rows = json.loads(resp.read())
        slugs = [r["slug"] for r in rows if r.get("slug")]
        print(f"[F] 優先度キュー: {len(slugs)}件取得 (quality_score低順)")
        return slugs
    except Exception as e:
        print(f"[F] 優先度キュー取得失敗（スキップ）: {e}")
        return []


def _sort_techniques_by_priority(techniques, priority_slugs):
    """F: priority_slugs の順番で TECHNIQUES を並び替え、未スコアは末尾に"""
    if not priority_slugs:
        return techniques
    slug_order = {slug: i for i, slug in enumerate(priority_slugs)}
    return sorted(techniques, key=lambda t: slug_order.get(t["slug"], len(priority_slugs)))

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="キャッシュ無視して全再生成")
    parser.add_argument("--limit", type=int, default=5, help="1回の実行で生成する最大記事数（コスト管理）")
    parser.add_argument("--lang", default="all", help="生成する言語 (en/ja/pt/all)")
    args = parser.parse_args()

    os.makedirs(SITE_DIR, exist_ok=True)
    cache  = {} if args.force else load_cache()
    langs  = list(LANGUAGES.keys()) if args.lang == "all" else [args.lang]
    count  = 0

    # F: 優先度キュー — quality_score 低順に再生成
    priority_slugs     = _fetch_low_quality_slugs() if args.force else []
    techniques_ordered = _sort_techniques_by_priority(TECHNIQUES, priority_slugs)
    all_slugs          = [t["slug"] for t in TECHNIQUES]

    # トップページ生成
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(generate_index())
    print("[OK] index.html 生成完了")

    # 技ページ生成
    for lang_code in langs:
        lang_dir = os.path.join(SITE_DIR, lang_code)
        os.makedirs(lang_dir, exist_ok=True)
        techniques_by_category = {}

        for tech in techniques_ordered:
            cache_key = f"{lang_code}/{tech['slug']}"
            out_path  = os.path.join(lang_dir, f"{tech['slug']}.html")

            # カテゴリ分類
            cat = tech["category"]
            techniques_by_category.setdefault(cat, []).append(tech)

            # キャッシュ済みかつファイル存在ならスキップ
            if cache_key in cache and os.path.exists(out_path) and not args.force:
                continue

            if count >= args.limit:
                print(f"[INFO] 上限({args.limit}件)に達しました。次回実行で続きを生成します。")
                break

            print(f"[{lang_code}] {tech['name']} 生成中...")
            raw = call_gemini(build_article_prompt(tech, lang_code, all_slugs))
            if not raw:
                print(f"[WARNING] {tech['name']} 生成失敗。スキップ")
                continue

            # JSONパース
            try:
                text    = re.sub(r'^```[a-z]*\n?', '', raw.strip(), flags=re.MULTILINE)
                text    = re.sub(r'\n?```$', '', text, flags=re.MULTILINE)
                article = json.loads(text.strip())
            except Exception as e:
                print(f"[WARNING] JSONパース失敗: {e}")
                continue

            # z255ii: lang-mismatch guard — JA/PT で title/h1 が英語のみなら skip
            # (Gemini が稀に lang_code を ignore して英語 title を出すケースを catch、
            #  既存翻訳済 file を上書きしないことで z254e fix の再発を防ぐ)
            if lang_code in ("ja", "pt"):
                _t = article.get("title", "")
                _h = article.get("h1", "")
                _has_native = False
                if lang_code == "ja":
                    # Hiragana / Katakana / CJK ideographs のいずれかを含むか
                    _has_native = bool(re.search(r"[぀-ゟ゠-ヿ一-鿿]", _t + _h))
                elif lang_code == "pt":
                    # PT 固有 accent or marker 語
                    _has_native = bool(re.search(r"[ãâáàçéêíóôõúÃÂÁÀÇÉÊÍÓÔÕÚ]", _t + _h)) \
                        or any(w in (_t + _h).lower() for w in ["sobre", "guarda", "guia", "para", "como", "no bjj", "do bjj"])
                if not _has_native:
                    print(f"[SKIP] {cache_key}: title/h1 が英語のみで lang={lang_code} 規約違反 → 既存 file を保護")
                    continue

            # HTML生成・保存（内部リンク付与）
            html = article_to_html(tech, lang_code, article, TECHNIQUES)
            html = add_internal_links(html, tech["slug"], lang_code)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)

            # 品質ゲート: 合格時のみキャッシュ登録（不合格は次回再生成）
            if _validate_article_structure(html, tech["slug"], lang_code):
                cache[cache_key] = datetime.datetime.now().isoformat()
            count += 1
            print(f"[OK] {cache_key} → {out_path}")
            # 10件ごとにTelegram進捗通知
            if count % 10 == 0:
                send_telegram(f"📖 BJJ Wiki 生成中: {count}件完了")
            time.sleep(1)  # API負荷軽減

        # カテゴリインデックス生成
        idx_html = generate_category_index(lang_code, techniques_by_category)
        with open(os.path.join(lang_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(idx_html)
        print(f"[OK] {lang_code}/index.html 生成完了")

    save_cache(cache)
    print(f"\n[完了] {count}件の新規記事を生成しました")
    remaining = sum(
        1 for tech in TECHNIQUES
        for lc in langs
        if f"{lc}/{tech['slug']}" not in cache
    )
    print(f"[残り] あと{remaining}件未生成")

if __name__ == "__main__":
    main()
