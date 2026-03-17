#!/usr/bin/env python3
"""
BJJ Wiki - å¤è¨èªæè¡æè¾å¸ èªåçæã¹ã¯ãªãã
- Gemini APIã§è±èª/æ¥æ¬èª/ãã«ãã¬ã«èªã®æè§£èª¬è¨äºãçæ
- éçHTMLã¨ãã¦GitHub Pagesã«ããã­ã¤
"""

import os, json, time, datetime, urllib.request, urllib.error, re

# ===== åé¨ãªã³ã¯è¾æ¸ï¼æåâã¹ã©ãã°ï¼=====
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
        "ã¢ã¼ã ãã¼": "armbar", "ä¸è§çµã": "triangle-choke",
        "è£¸çµã": "rear-naked-choke", "ã®ã­ãã³ãã§ã¼ã¯": "guillotine-choke",
        "æ¨æã­ãã¯": "kimura", "ã¢ã¡ãªã«ã¼ã": "americana", "ãªã¢ãã©ã¼ã¿": "omoplata",
        "ã¯ã­ã¼ãºãã¬ã¼ã": "closed-guard", "ãã¼ãã¬ã¼ã": "half-guard",
        "ãã¿ãã©ã¤ã¬ã¼ã": "butterfly-guard", "ãã©ãã¼ãã¬ã¼ã": "de-la-riva-guard",
        "ããã¯ãã¦ã³ã": "back-mount", "ãµã¤ãã³ã³ãã­ã¼ã«": "side-control",
        "ãã¦ã³ã": "mount", "ãã¼ã«ããã¯": "heel-hook",
        "ã¤ã³ãµã¤ããã¼ã«ããã¯": "inside-heel-hook", "ã¢ã¦ããµã¤ããã¼ã«ããã¯": "outside-heel-hook",
        "ãã¼ãã¼": "knee-bar", "ãã¼ãã¼ã«ã": "toe-hold", "ã¢ã³ã¯ã«ã­ãã¯": "ankle-lock",
        "ãã¼ã·ã¼ãã§ã¼ã¯": "darce-choke", "ã¢ãã³ã³ããã§ã¼ã¯": "anaconda-choke",
        "ã¨ã¼ã­ã¨ã«ãã§ã¼ã¯": "ezekiel-choke", "ã«ã¼ãã¹ã©ã¤ãµã¼": "calf-slicer",
        "ã¹ãã¤ãã¼ã¬ã¼ã": "spider-guard", "ã©ãã¼ã¬ã¼ã": "rubber-guard",
        "ã©ãã½ã¼ã¬ã¼ã": "lasso-guard", "ãã£ã¼ããã¼ãã¬ã¼ã": "deep-half-guard",
        "ãã¬ã¢ã³ããã¹": "torreando-pass", "ãã¼ã¹ã©ã¤ã¹ãã¹": "knee-slice-pass",
        "ã·ã¶ã¼ã¹ã¤ã¼ã": "scissor-sweep", "ããããã³ãã¹ã¤ã¼ã": "hip-bump-sweep",
        "ããã¯ãã¤ã¯": "backtake", "ã·ã¥ãªã³ãã¨ã¹ã±ã¼ã": "shrimp-escape",
        "ã¢ã¼ã ãã©ãã°": "arm-drag", "ããã«ã¬ãã°": "double-leg-takedown",
        "ã¹ãã­ã¼ã«": "sprawl", "ãã¼ã¹ãµã¦ã¹": "north-south",
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
        "BraÃ§adeira": "arm-triangle-choke", "Chave de PÃ©": "ankle-lock",
    },
}

def add_internal_links(html: str, current_slug: str, lang: str) -> str:
    """<p>ã¿ã°åã®æåãåé¨ãªã³ã¯ã«å¤æï¼åæ1åã®ã¿ï¼"""
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
                    f'<a href="{url}" style="color:var(--accent,#7c6af7);text-decoration:underline">{name}</a>',
                    p, count=1)
                linked.add(slug)
                break
        return p

    return re.sub(r'<p[^>]*>.*?</p>', replace_in_p, html, flags=re.DOTALL)

# ===== ~/.secrets ããAPIã­ã¼ãè£å® =====
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

# ===== è¨­å® =====
IS_CI          = os.environ.get("GITHUB_ACTIONS") == "true"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SITE_DIR       = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if IS_CI else os.path.expanduser("~/Claude/bjj-wiki")
SITE_URL       = "https://t307239.github.io/bjj-wiki"
AMAZON_TAG     = "bjj06-22"

LANGUAGES = {
    "en": {"name": "English",    "dir": "en"},
    "ja": {"name": "æ¥æ¬èª",      "dir": "ja"},
    "pt": {"name": "PortuguÃªs",  "dir": "pt"},
}

# ===== æãªã¹ãï¼100æï¼=====
TECHNIQUES = [
    # ã¬ã¼ãç³»
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
    # ãã¹ç³»
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
    # ãã¤ã¯ãã¦ã³
    {"slug": "double-leg-takedown", "name": "Double Leg Takedown", "category": "Takedown"},
    {"slug": "single-leg-takedown", "name": "Single Leg Takedown", "category": "Takedown"},
    {"slug": "osoto-gari",          "name": "Osoto Gari",          "category": "Takedown"},
    {"slug": "ankle-pick",          "name": "Ankle Pick",          "category": "Takedown"},
    {"slug": "harai-goshi",         "name": "Harai Goshi",         "category": "Takedown"},
    {"slug": "ippon-seoi-nage",     "name": "Ippon Seoi Nage",     "category": "Takedown"},
    {"slug": "morote-seoi-nage",    "name": "Morote Seoi Nage",    "category": "Takedown"},
    {"slug": "snap-down",           "name": "Snap Down",           "category": "Takedown"},
    # çµãæ
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
    # é¢ç¯æ
    {"slug": "armbar",              "name": "Armbar",              "category": "Joint Lock"},
    {"slug": "kimura",              "name": "Kimura",              "category": "Joint Lock"},
    {"slug": "americana",           "name": "Americana",           "category": "Joint Lock"},
    {"slug": "omoplata",            "name": "Omoplata",            "category": "Joint Lock"},
    {"slug": "wrist-lock",          "name": "Wrist Lock",          "category": "Joint Lock"},
    {"slug": "straight-armbar",     "name": "Straight Armbar",     "category": "Joint Lock"},
    {"slug": "monoplata",           "name": "Monoplata",           "category": "Joint Lock"},
    # ã¬ãã°ã­ãã¯
    {"slug": "heel-hook",           "name": "Heel Hook",           "category": "Leg Lock"},
    {"slug": "inside-heel-hook",    "name": "Inside Heel Hook",    "category": "Leg Lock"},
    {"slug": "outside-heel-hook",   "name": "Outside Heel Hook",   "category": "Leg Lock"},
    {"slug": "knee-bar",            "name": "Knee Bar",            "category": "Leg Lock"},
    {"slug": "toe-hold",            "name": "Toe Hold",            "category": "Leg Lock"},
    {"slug": "calf-slicer",         "name": "Calf Slicer",         "category": "Leg Lock"},
    {"slug": "ankle-lock",          "name": "Ankle Lock",          "category": "Leg Lock"},
    {"slug": "estima-lock",         "name": "Estima Lock",         "category": "Leg Lock"},
    # ãã¸ã·ã§ã³
    {"slug": "mount",               "name": "Mount",               "category": "Position"},
    {"slug": "back-mount",          "name": "Back Mount",          "category": "Position"},
    {"slug": "side-control",        "name": "Side Control",        "category": "Position"},
    {"slug": "north-south",         "name": "North-South",         "category": "Position"},
    {"slug": "knee-on-belly",       "name": "Knee on Belly",       "category": "Position"},
    {"slug": "s-mount",             "name": "S-Mount",             "category": "Position"},
    {"slug": "modified-mount",      "name": "Modified Mount",      "category": "Position"},
    {"slug": "body-triangle",       "name": "Body Triangle",       "category": "Position"},
    # ã¹ã¤ã¼ã
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
    # ãµãããã·ã§ã³é£æº
    {"slug": "arm-drag",            "name": "Arm Drag",            "category": "Transition"},
    {"slug": "granby-roll",         "name": "Granby Roll",         "category": "Transition"},
    {"slug": "shrimp-escape",       "name": "Shrimp Escape",       "category": "Escape"},
    {"slug": "bridge-and-roll",     "name": "Bridge and Roll",     "category": "Escape"},
    {"slug": "elbow-knee-escape",   "name": "Elbow-Knee Escape",   "category": "Escape"},
    # ãã£ãã§ã³ã¹ã»ã¨ã¹ã±ã¼ã
    {"slug": "guard-retention",     "name": "Guard Retention",     "category": "Defense"},
    {"slug": "hip-escape",          "name": "Hip Escape",          "category": "Defense"},
    {"slug": "frame",               "name": "Frame",               "category": "Defense"},
    {"slug": "sprawl",              "name": "Sprawl",              "category": "Defense"},
    {"slug": "back-defense",        "name": "Back Defense",        "category": "Defense"},
    # ãã©ã³ã¸ã·ã§ã³
    {"slug": "backtake",            "name": "Back Take",           "category": "Transition"},
    {"slug": "turtle-position",     "name": "Turtle Position",     "category": "Position"},
    {"slug": "technical-standup",   "name": "Technical Stand-Up",  "category": "Transition"},
    {"slug": "stand-in-base",       "name": "Stand In Base",       "category": "Transition"},
    {"slug": "sitting-guard",       "name": "Sitting Guard",       "category": "Guard"},
    # ãã¼ã®ç¹å
    {"slug": "seat-belt-control",   "name": "Seat Belt Control",   "category": "Position"},
    {"slug": "front-headlock",      "name": "Front Headlock",      "category": "Position"},
    {"slug": "russian-tie",         "name": "Russian Tie",         "category": "Takedown"},
    {"slug": "underhook",           "name": "Underhook",           "category": "Position"},
    {"slug": "overhook",            "name": "Overhook",            "category": "Position"},
]

# ===== Gemini APIï¼è¤æ°ã¢ãã«ãã©ã¼ã«ããã¯ï¼=====
def call_gemini(prompt):
    # ç¡ætierãåé ­âææ(2.5ç³»)ã¯æçµãã©ã¼ã«ããã¯ã®ã¿
    models = [
        ("gemini-2.0-flash",         "v1beta"),   # ç¡ætier
        ("gemini-2.0-flash",         "v1"),        # ç¡ætier
        ("gemini-2.0-flash-lite-001","v1beta"),    # ç¡ætier
        ("gemini-1.5-flash-latest",  "v1beta"),    # ç¡ætier
        ("gemini-2.5-flash",         "v1beta"),    # ææ(æçµææ®µ)
    ]
    data = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
    }).encode()
    for model, api_ver in models:
        url = f"https://generativelanguage.googleapis.com/{api_ver}/models/{model}:generateContent?key={GEMINI_API_KEY}"
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=60) as res:
                    result = json.loads(res.read())
                    text   = result["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"[OK] [{model}] çææå")
                    return text
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(30 * (attempt + 1))
                else:
                    print(f"[{model}] HTTP {e.code} â æ¬¡ã®ã¢ãã«ã¸"); break
            except Exception as e:
                print(f"[{model}] ã¨ã©ã¼: {e}"); break
    return None

# ===== è¨äºçæãã­ã³ãã =====
def build_article_prompt(technique, lang_code):
    lang_instructions = {
        "en": "Write in English.",
        "ja": "æ¥æ¬èªã§æ¸ãã¦ãã ããã",
        "pt": "Escreva em PortuguÃªs brasileiro.",
    }
    instruction = lang_instructions[lang_code]
    return f"""You are an expert Brazilian Jiu-Jitsu instructor and SEO content writer.
{instruction}

Write a comprehensive BJJ technique guide for: **{technique['name']}** (Category: {technique['category']})

Return ONLY valid JSON with this exact structure (no markdown, no extra text):
{{
  "title": "SEO-optimized page title (include BJJ and technique name)",
  "meta_description": "150-160 char meta description for search engines",
  "h1": "Main heading for the article",
  "intro": "2-3 sentence introduction explaining what this technique is",
  "how_to": "Step-by-step instructions (4-6 steps, each 1-2 sentences)",
  "key_details": "Important details, common mistakes, and tips (3-4 points)",
  "variations": "2-3 common variations or related techniques",
  "when_to_use": "Situations and positions where this technique works best",
  "counters": "2-3 main defenses or counters against this technique",
  "belt_level": "Recommended belt level (White/Blue/Purple/Brown/Black)",
  "pro_tip": "One expert pro tip that most beginners miss (1-2 sentences)",
  "faq_q1": "Frequently asked question about this technique",
  "faq_a1": "Answer to the FAQ",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}}"""

# ===== é£æåº¦ã»é¸æã»Yogaã»ã®ã¢ ãããã³ã° =====
DIFFICULTY_MAP = {
    "armbar":("blue","âââââ","Intermediate"),"triangle-choke":("blue","âââââ","Intermediate"),
    "rear-naked-choke":("white","âââââ","Beginner"),"guillotine-choke":("blue","âââââ","Intermediate"),
    "kimura":("blue","âââââ","Intermediate"),"americana":("white","âââââ","Beginner"),
    "omoplata":("purple","âââââ","Advanced"),"heel-hook":("brown","âââââ","Expert"),
    "inside-heel-hook":("brown","âââââ","Expert"),"outside-heel-hook":("brown","âââââ","Expert"),
    "berimbolo":("purple","âââââ","Advanced"),"rubber-guard":("purple","âââââ","Advanced"),
    "closed-guard":("white","âââââ","Beginner"),"half-guard":("white","âââââ","Beginner"),
    "butterfly-guard":("blue","âââââ","Intermediate"),"de-la-riva-guard":("blue","âââââ","Intermediate"),
    "x-guard":("purple","âââââ","Advanced"),"worm-guard":("purple","âââââ","Advanced"),
    "50-50-guard":("blue","âââââ","Intermediate"),"knee-bar":("purple","âââââ","Advanced"),
    "toe-hold":("blue","âââââ","Intermediate"),"ankle-lock":("blue","âââââ","Intermediate"),
    "bow-and-arrow-choke":("blue","âââââ","Intermediate"),"back-mount":("blue","âââââ","Intermediate"),
    "mount":("white","âââââ","Beginner"),"side-control":("white","âââââ","Beginner"),
    "guard-pass":("blue","âââââ","Intermediate"),"scissor-sweep":("white","âââââ","Beginner"),
    "hip-bump-sweep":("white","âââââ","Beginner"),"shrimp-escape":("white","âââââ","Beginner"),
    "double-leg-takedown":("blue","âââââ","Intermediate"),"single-leg-takedown":("white","âââââ","Beginner"),
    "darce-choke":("blue","âââââ","Intermediate"),"anaconda-choke":("blue","âââââ","Intermediate"),
    "arm-triangle-choke":("blue","âââââ","Intermediate"),"north-south-choke":("purple","âââââ","Advanced"),
    "baseball-choke":("blue","âââââ","Intermediate"),"lasso-guard":("blue","âââââ","Intermediate"),
    "calf-slicer":("purple","âââââ","Advanced"),"wrist-lock":("blue","âââââ","Intermediate"),
    "torreando-pass":("blue","âââââ","Intermediate"),"knee-slice-pass":("blue","âââââ","Intermediate"),
    "north-south":("white","âââââ","Beginner"),"knee-on-belly":("blue","âââââ","Intermediate"),
}
BELT_BG = {"white":"#e2e2ee","blue":"#2563eb","purple":"#7c3aed","brown":"#92400e","black":"#111"}
BELT_FG = {"white":"#111","blue":"#fff","purple":"#fff","brown":"#fff","black":"#fff"}

ATHLETE_MAP = {
    "armbar":[("john-danaher","John Danaher","ðºð¸"),("marcelo-garcia","Marcelo Garcia","ð§ð·"),("gordon-ryan","Gordon Ryan","ðºð¸")],
    "triangle-choke":[("marcelo-garcia","Marcelo Garcia","ð§ð·"),("john-danaher","John Danaher","ðºð¸")],
    "rear-naked-choke":[("gordon-ryan","Gordon Ryan","ðºð¸"),("marcelo-garcia","Marcelo Garcia","ð§ð·")],
    "guillotine-choke":[("marcelo-garcia","Marcelo Garcia","ð§ð·"),("john-danaher","John Danaher","ðºð¸")],
    "kimura":[("marcelo-garcia","Marcelo Garcia","ð§ð·"),("john-danaher","John Danaher","ðºð¸")],
    "heel-hook":[("gordon-ryan","Gordon Ryan","ðºð¸"),("craig-jones","Craig Jones","ð¦ðº"),("john-danaher","John Danaher","ðºð¸")],
    "inside-heel-hook":[("gordon-ryan","Gordon Ryan","ðºð¸"),("craig-jones","Craig Jones","ð¦ðº")],
    "outside-heel-hook":[("gordon-ryan","Gordon Ryan","ðºð¸"),("craig-jones","Craig Jones","ð¦ðº")],
    "berimbolo":[("mikey-musumeci","Mikey Musumeci","ðºð¸"),("caio-terra","Caio Terra","ð§ð·")],
    "closed-guard":[("marcelo-garcia","Marcelo Garcia","ð§ð·"),("bernardo-faria","Bernardo Faria","ð§ð·")],
    "half-guard":[("bernardo-faria","Bernardo Faria","ð§ð·"),("marcelo-garcia","Marcelo Garcia","ð§ð·")],
    "butterfly-guard":[("marcelo-garcia","Marcelo Garcia","ð§ð·"),("john-danaher","John Danaher","ðºð¸")],
    "omoplata":[("caio-terra","Caio Terra","ð§ð·"),("mikey-musumeci","Mikey Musumeci","ðºð¸")],
    "rubber-guard":[("mikey-musumeci","Mikey Musumeci","ðºð¸")],
    "bow-and-arrow-choke":[("marcelo-garcia","Marcelo Garcia","ð§ð·"),("andre-galvao","AndrÃ© GalvÃ£o","ð§ð·")],
    "back-mount":[("gordon-ryan","Gordon Ryan","ðºð¸"),("marcelo-garcia","Marcelo Garcia","ð§ð·")],
    "x-guard":[("marcelo-garcia","Marcelo Garcia","ð§ð·")],
    "de-la-riva-guard":[("caio-terra","Caio Terra","ð§ð·"),("keenan-cornelius","Keenan Cornelius","ðºð¸")],
    "worm-guard":[("keenan-cornelius","Keenan Cornelius","ðºð¸")],
    "lasso-guard":[("keenan-cornelius","Keenan Cornelius","ðºð¸"),("caio-terra","Caio Terra","ð§ð·")],
    "mount":[("andre-galvao","AndrÃ© GalvÃ£o","ð§ð·"),("marcelo-garcia","Marcelo Garcia","ð§ð·")],
    "side-control":[("gordon-ryan","Gordon Ryan","ðºð¸"),("xande-ribeiro","Xande Ribeiro","ð§ð·")],
    "50-50-guard":[("gordon-ryan","Gordon Ryan","ðºð¸"),("craig-jones","Craig Jones","ð¦ðº")],
    "knee-bar":[("gordon-ryan","Gordon Ryan","ðºð¸"),("craig-jones","Craig Jones","ð¦ðº")],
    "double-leg-takedown":[("marcelo-garcia","Marcelo Garcia","ð§ð·"),("andre-galvao","AndrÃ© GalvÃ£o","ð§ð·")],
    "arm-drag":[("marcelo-garcia","Marcelo Garcia","ð§ð·")],
    "anaconda-choke":[("marcelo-garcia","Marcelo Garcia","ð§ð·"),("craig-jones","Craig Jones","ð¦ðº")],
    "darce-choke":[("john-danaher","John Danaher","ðºð¸"),("gordon-ryan","Gordon Ryan","ðºð¸")],
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
    "Guard":[("best-bjj-gi-beginners","ð¥ Best BJJ Gi"),("best-bjj-rashguard","ð Best Rashguard")],
    "Joint Lock":[("best-bjj-gi-beginners","ð¥ Best BJJ Gi"),("best-bjj-mouthguard","ð¦· Best Mouthguard")],
    "Leg Lock":[("best-no-gi-shorts","ð©³ Best No-Gi Shorts"),("best-bjj-knee-pads","ð¦µ Best Knee Pads")],
    "Choke":[("best-bjj-gi-beginners","ð¥ Best BJJ Gi"),("best-bjj-belt","ð½ Best BJJ Belt")],
    "Sweep":[("best-bjj-gi-beginners","ð¥ Best BJJ Gi"),("best-bjj-rashguard","ð Best Rashguard")],
    "Takedown":[("best-no-gi-shorts","ð©³ Best No-Gi Shorts"),("best-bjj-rashguard","ð Best Rashguard")],
    "Passing":[("best-bjj-knee-pads","ð¦µ Best Knee Pads"),("best-bjj-rashguard","ð Best Rashguard")],
    "Position":[("best-bjj-gi-beginners","ð¥ Best BJJ Gi"),("best-bjj-mouthguard","ð¦· Best Mouthguard")],
    "Escape":[("best-bjj-rashguard","ð Best Rashguard"),("best-bjj-knee-pads","ð¦µ Best Knee Pads")],
    "Transition":[("best-bjj-rashguard","ð Best Rashguard"),("best-bjj-gi-beginners","ð¥ Best BJJ Gi")],
    "Defense":[("best-bjj-mouthguard","ð¦· Best Mouthguard"),("best-bjj-rashguard","ð Best Rashguard")],
}

# ===== è¨äºJSONãHTMLã«å¤æ =====
def article_to_html(tech, lang_code, article, all_techniques):
    lang = LANGUAGES[lang_code]
    nav_labels = {
        "en": {"home": "Home", "all": "All Techniques", "category": "Category"},
        "ja": {"home": "ãã¼ã ", "all": "å¨æä¸è¦§", "category": "ã«ãã´ãª"},
        "pt": {"home": "InÃ­cio", "all": "Todas as TÃ©cnicas", "category": "Categoria"},
    }
    labels = nav_labels[lang_code]

    # ãªã¹ã or æå­åãå®å¨ã«æå­ååãããã«ãã¼
    def to_str(v):
        if isinstance(v, list): return "\n".join(str(i) for i in v)
        return str(v) if v else ""

    # åã«ãã´ãªã®é¢é£æãªã³ã¯
    related = [t for t in all_techniques if t["category"] == tech["category"] and t["slug"] != tech["slug"]][:5]
    related_links = "\n".join([
        f'<a href="../{t["slug"]}.html">{t["name"]}</a>'
        for t in related
    ])

    # è¨èªåæ¿ãªã³ã¯
    lang_switcher = " | ".join([
        f'<a href="../{lc}/{tech["slug"]}.html">{LANGUAGES[lc]["name"]}</a>'
        for lc in LANGUAGES if lc != lang_code
    ])

    keywords_str = ", ".join(article.get("keywords", []))

    # --- é£æåº¦ãã¼ ---
    diff = DIFFICULTY_MAP.get(tech["slug"], ("white","âââââ","Intermediate"))
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

    # --- ãã«ãã¬ã¤ãã¯ã­ã¹ãªã³ã¯ ---
    _belt_guide_map = {
        "white": {"en": ("white-belt-bjj-guide.html","White Belt Guide"), "ja": ("white-belt-bjj-guide.html","ç½å¸¯ã¬ã¤ã"), "pt": ("white-belt-bjj-guide.html","Guia Faixa Branca")},
        "blue":  {"en": ("blue-belt-bjj-guide.html","Blue Belt Guide"),  "ja": ("blue-belt-bjj-guide.html","éå¸¯ã¬ã¤ã"),  "pt": ("blue-belt-bjj-guide.html","Guia Faixa Azul")},
        "purple":{"en": ("bjj-purple-belt-requirements.html","Purple Belt Requirements"),"ja": ("bjj-purple-belt-requirements.html","ç´«å¸¯ææ ¼è¦ä»¶"),"pt": ("bjj-purple-belt-requirements.html","Requisitos Faixa Roxa")},
        "brown": {"en": ("bjj-brown-belt-requirements.html","Brown Belt Requirements"),"ja": ("bjj-brown-belt-requirements.html","è¶å¸¯ææ ¼è¦ä»¶"),"pt": ("bjj-brown-belt-requirements.html","Requisitos Faixa Marrom")},
        "black": {"en": ("bjj-black-belt-requirements.html","Black Belt Requirements"),"ja": ("bjj-black-belt-requirements.html","é»å¸¯ææ ¼è¦ä»¶"),"pt": ("bjj-black-belt-requirements.html","Requisitos Faixa Preta")},
    }
    _cta_see_guide = {"en":"ð See Full Guide â","ja":"ð å®å¨ã¬ã¤ããè¦ã â","pt":"ð Ver Guia Completo â"}
    _belt_level_label = {"en":f"{diff_belt.title()} Belt Technique","ja":f"{diff_belt.title()}å¸¯ãã¯ããã¯","pt":f"TÃ©cnica Faixa {diff_belt.title()}"}
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

    # --- é¸æã»ã¯ã·ã§ã³ ---
    athlete_label = {"en":"ð Elite Athletes Who Use This","ja":"ð ãã®æãä½¿ãã¨ãªã¼ãé¸æ","pt":"ð Atletas de Elite"}[lang_code]
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

    # --- Yoga ã¯ã­ã¹ãªã³ã¯ ---
    yoga_poses = YOGA_SLUG_MAP.get(tech["slug"], YOGA_CAT_DEFAULTS.get(tech["category"], []))[:3]
    yoga_label  = {"en":"ð§ Yoga Poses to Improve This Technique","ja":"ð§ ãã®æã«å¹ãã¨ã¬ãã¼ãº","pt":"ð§ Yoga para Esta TÃ©cnica"}[lang_code]
    yoga_sub    = {"en":"These poses build the flexibility & mobility you need:","ja":"å¿è¦ãªæè»æ§ã»å¯ååãé«ãã¾ãï¼","pt":"Melhore sua flexibilidade e mobilidade:"}[lang_code]
    if yoga_poses:
        yoga_chips = "".join([
            f'<a class="yoga-chip" href="https://t307239.github.io/yoga-wiki/en/{sl}.html" target="_blank" rel="noopener">ð§ {nm}</a>'
            for sl, nm in yoga_poses
        ])
        yoga_html = f'<div class="yoga-box"><h3>{yoga_label}</h3><p>{yoga_sub}</p><div class="yoga-chips">{yoga_chips}</div></div>'
    else:
        yoga_html = ""

    # --- ã³ã³ãã£ã·ã§ãã³ã°ããã¯ã¹ ---
    _strength_slugs = {"double-leg-takedown","single-leg-takedown","hip-throw","o-soto-gari",
                       "harai-goshi","ippon-seoi-nage","snap-down","torreando-pass",
                       "knee-slice-pass","leg-drag-pass","x-pass","heel-hook","kimura",
                       "americana","rear-naked-choke","hip-escape","bridge-and-roll",
                       "guard-retention","back-take","deep-half-guard","wrestling"}
    _nutrition_slugs = {"bjj-training-tips","bjj-competition-guide","bjj-belt-system",
                        "white-belt-bjj-guide","blue-belt-bjj-guide","bjj-strength-training",
                        "double-leg-takedown","single-leg-takedown","wrestling",
                        "bjj-competition-calendar-2026"}
    _str_lbl = {"en":("â¡ Strength & Conditioning","Build explosive power for this technique:","bjj-strength-training.html","ðª Strength Training Guide â"),
                "ja":("â¡ ç­ãã¬ã»ã³ã³ãã£ã·ã§ãã³ã°","ãã®æã®ççºåãé«ãããã¬ã¼ãã³ã°:","bjj-strength-training.html","ðª ç­ãã¬ã¬ã¤ããè¦ã â"),
                "pt":("â¡ ForÃ§a & Condicionamento","Desenvolva potÃªncia explosiva para esta tÃ©cnica:","bjj-strength-training.html","ðª Guia de MusculaÃ§Ã£o â")}
    _nut_lbl = {"en":("ð¥ BJJ Nutrition","Fuel your training with the right diet:","bjj-diet-nutrition.html","ð¥ Nutrition Guide â"),
                "ja":("ð¥ BJJæ é¤å­¦","æ­£ããé£äºã§ç·´ç¿ããã©ã¼ãã³ã¹ãæå¤§å:","bjj-diet-nutrition.html","ð¥ æ é¤ã¬ã¤ããè¦ã â"),
                "pt":("ð¥ NutriÃ§Ã£o para BJJ","Alimente seu treino com a dieta certa:","bjj-diet-nutrition.html","ð¥ Guia de NutriÃ§Ã£o â")}
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

    # --- ã®ã¢ããã¯ã¹ ---
    gear_items  = GEAR_CAT_MAP.get(tech["category"], [])
    gear_label  = {"en":"âï¸ Recommended Gear","ja":"âï¸ ããããã®ã¢","pt":"âï¸ Equipamento Recomendado"}[lang_code]
    if gear_items:
        gear_links = "".join([
            f'<a class="gear-link" href="../../gear/{sl}.html">{nm}</a>'
            for sl, nm in gear_items
        ])
        gear_html = f'<div class="gear-box"><h3>{gear_label}</h3><div class="gear-links">{gear_links}</div></div>'
    else:
        gear_html = ""

    # --- Beehiiv CTA ---
    bee_title = {"en":"ð Get Weekly BJJ Tips","ja":"ð é±1BJJãã¯ããã¯ãã¡ã¼ã«ã§","pt":"ð Dicas de BJJ Toda Semana"}[lang_code]
    bee_desc  = {"en":"Join the BJJ Wiki newsletter â technique breakdowns, training tips & exclusive content. Free.","ja":"BJJ Wikiãã¥ã¼ã¹ã¬ã¿ã¼ã«åå ãæè§£èª¬ã»ç·´ç¿ã®ã³ãã»éå®ã³ã³ãã³ããæ¯é±ãå±ãï¼ç¡æï¼ã","pt":"Junte-se Ã  newsletter do BJJ Wiki â anÃ¡lises de tÃ©cnicas, dicas de treino e conteÃºdo exclusivo. GrÃ¡tis."}[lang_code]
    bee_btn   = {"en":"Subscribe Free â","ja":"ç¡æè³¼èª­ â","pt":"Assinar GrÃ¡tis â"}[lang_code]
    beehiiv_html = (
        f'<div class="beehiiv-wrap"><h3>{bee_title}</h3>'
        f'<p>{bee_desc}</p>'
        f'<a class="beehiiv-btn" href="https://bjj-wiki.beehiiv.com/subscribe" target="_blank" rel="noopener">{bee_btn}</a>'
        f'</div>'
    )

    return f"""<!DOCTYPE html>
<html lang="{lang_code}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.googletagmanager.com">
<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
<link rel="dns-prefetch" href="https://www.google-analytics.com">
<title>{article.get('title', tech['name'])} | BJJ Wiki</title>
<meta name="description" content="{article.get('meta_description', '')}">
<meta name="keywords" content="{keywords_str}">
<meta property="og:title" content="{article.get('title', tech['name'])}">
<meta property="og:description" content="{article.get('meta_description', '')}">
<meta property="og:type" content="article">
<meta property="og:url" content="{SITE_URL}/{lang_code}/{tech['slug']}.html">
<meta property="og:image" content="{SITE_URL}/og-image.svg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@bjj_wiki">
<meta name="twitter:title" content="{article.get('title', tech['name'])}">
<meta name="twitter:description" content="{article.get('meta_description', '')[:200]}">
<meta name="twitter:image" content="{SITE_URL}/og-image.svg">
<link rel="canonical" href="{SITE_URL}/{lang_code}/{tech['slug']}.html">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/en/{tech['slug']}.html">
<link rel="alternate" hreflang="en" href="{SITE_URL}/en/{tech['slug']}.html">
<link rel="alternate" hreflang="ja" href="{SITE_URL}/ja/{tech['slug']}.html">
<link rel="alternate" hreflang="pt" href="{SITE_URL}/pt/{tech['slug']}.html">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-7LM8L3TRZM"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-7LM8L3TRZM');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5529701443220352" crossorigin="anonymous"></script>
<style>
  :root {{--bg:#0a0a0f;--card:#111119;--border:#1e1e2e;--text:#e2e2ee;--muted:#7a7a9a;--accent:#6e40c9;--green:#22c55e}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.7;padding:0 16px}}
  .container{{max-width:800px;margin:0 auto;padding:24px 0 64px}}
  header{{padding:20px 0;border-bottom:1px solid var(--border);margin-bottom:32px}}
  .logo{{font-size:1.4rem;font-weight:800;color:var(--text);text-decoration:none}}
  .logo span{{color:var(--accent)}}
  nav{{margin-top:8px;font-size:0.85rem;color:var(--muted)}}
  nav a{{color:var(--muted);text-decoration:none;margin-right:12px}}
  nav a:hover{{color:var(--text)}}
  .lang-switcher{{font-size:0.8rem;color:var(--muted);margin-top:6px}}
  .lang-switcher a{{color:var(--accent);text-decoration:none;margin:0 4px}}
  .badge{{display:inline-block;font-size:0.72rem;padding:2px 10px;border-radius:20px;background:#1e1e2e;color:var(--muted);border:1px solid var(--border);margin-bottom:12px}}
  h1{{font-size:2rem;font-weight:800;margin-bottom:16px;line-height:1.2}}
  h2{{font-size:1.2rem;font-weight:700;margin:32px 0 12px;padding-left:12px;border-left:3px solid var(--accent)}}
  p{{color:#c2c2d9;margin-bottom:16px}}
  .card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px}}
  .belt{{display:inline-block;padding:3px 12px;border-radius:4px;font-size:0.8rem;font-weight:700;margin-bottom:16px}}
  .belt-white{{background:#e2e2ee;color:#111}}
  .belt-blue{{background:#2563eb;color:#fff}}
  .belt-purple{{background:#7c3aed;color:#fff}}
  .belt-brown{{background:#92400e;color:#fff}}
  .belt-black{{background:#111;color:#fff;border:1px solid #444}}
  .faq{{background:#0d0d1a;border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px}}
  .faq-q{{font-weight:700;color:var(--accent);margin-bottom:8px}}
  .related-links{{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}}
  .related-links a{{background:#1e1e2e;color:var(--muted);text-decoration:none;padding:4px 12px;border-radius:6px;font-size:0.85rem;border:1px solid var(--border)}}
  .related-links a:hover{{color:var(--text);border-color:var(--accent)}}
  .aff-box{{background:linear-gradient(135deg,#1a0a2e,#0d0d1a);border:1px solid var(--accent);border-radius:12px;padding:20px;margin:32px 0;text-align:center}}
  .aff-box p{{color:var(--muted);font-size:0.9rem;margin-bottom:12px}}
  .aff-btn{{display:inline-block;background:var(--accent);color:#fff;padding:10px 24px;border-radius:8px;text-decoration:none;font-weight:700;font-size:0.9rem}}
  .pro-tip{{background:linear-gradient(135deg,#0a1a0a,#0f1f0f);border:1px solid #22c55e;border-radius:12px;padding:20px;margin:24px 0}}
  .pro-tip-label{{color:#22c55e;font-size:0.8rem;font-weight:700;letter-spacing:0.05em;margin-bottom:8px}}
  .share-bar{{margin:32px 0;padding:20px;background:var(--card);border:1px solid var(--border);border-radius:12px;text-align:center}}
  .share-bar p{{color:var(--muted);font-size:0.85rem;margin-bottom:12px}}
  .share-btns{{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}}
  .share-btn{{display:inline-flex;align-items:center;gap:6px;padding:8px 18px;border-radius:8px;font-size:0.85rem;font-weight:700;text-decoration:none;transition:opacity .2s}}
  .share-btn:hover{{opacity:.8;text-decoration:none}}
  .share-btn.x{{background:#000;color:#fff}}
  .share-btn.reddit{{background:#ff4500;color:#fff}}
  .share-btn.copy{{background:#2d3748;color:#fff;cursor:pointer;border:none;font-family:inherit}}
  footer{{border-top:1px solid var(--border);padding:24px 0;text-align:center;color:var(--muted);font-size:0.8rem}}
  .difficulty-bar{{margin:12px 0 24px;padding:10px 16px;background:#0f1420;border:1px solid #1f2840;border-radius:10px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}}
  .diff-belt{{display:inline-block;padding:3px 10px;border-radius:4px;font-size:0.75rem;font-weight:700;letter-spacing:.04em}}
  .diff-stars{{color:#f59e0b;font-size:.95rem;letter-spacing:1px}}
  .diff-label{{color:var(--muted);font-size:0.8rem}}
  .athletes-section{{margin:28px 0}}
  .athletes-section h2{{font-size:.9rem;font-weight:700;color:#a78bfa;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px}}
  .athlete-chips{{display:flex;flex-wrap:wrap;gap:10px}}
  .athlete-chip{{display:flex;align-items:center;gap:10px;background:#141926;border:1px solid #1f2840;border-radius:12px;padding:12px 16px;text-decoration:none;color:#e8eaf6;transition:border-color .2s}}
  .athlete-chip:hover{{border-color:#7c6af7;text-decoration:none}}
  .yoga-box{{background:linear-gradient(135deg,#0a1a10,#0f1a0a);border:1px solid #22c55e;border-radius:12px;padding:20px;margin:24px 0}}
  .yoga-box h3{{font-size:.85rem;font-weight:700;color:#22c55e;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}}
  .yoga-box p{{font-size:.85rem;color:#6b9e6b;margin-bottom:12px}}
  .yoga-chips{{display:flex;flex-wrap:wrap;gap:8px}}
  .yoga-chip{{display:inline-block;padding:6px 14px;background:#0d2010;border:1px solid #22c55e40;border-radius:20px;font-size:.82rem;color:#86efac;text-decoration:none;font-weight:600}}
  .yoga-chip:hover{{background:#22c55e;color:#000;text-decoration:none}}
  .gear-box{{background:#0f1420;border:1px solid #1f2840;border-radius:12px;padding:18px;margin:20px 0}}
  .gear-box h3{{font-size:.82rem;font-weight:700;color:#6b7699;text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px}}
  .gear-links{{display:flex;flex-wrap:wrap;gap:8px}}
  .gear-link{{display:inline-block;padding:6px 14px;background:#141926;border:1px solid #1f2840;border-radius:20px;font-size:.82rem;color:#8899bb;text-decoration:none}}
  .gear-link:hover{{border-color:#6b7699;color:#c0cce8;text-decoration:none}}
  .beehiiv-wrap{{background:linear-gradient(135deg,#0d1225,#1a1040);border:1px solid #3b2d6e;border-radius:14px;padding:24px;margin:32px 0;text-align:center}}
  .beehiiv-wrap h3{{font-size:1.05rem;font-weight:800;margin-bottom:10px}}
  .beehiiv-wrap p{{color:var(--muted);font-size:0.88rem;line-height:1.6;margin-bottom:16px}}
  .beehiiv-btn{{display:inline-block;background:linear-gradient(135deg,#6e40c9,#4f46e5);color:#fff;padding:12px 28px;border-radius:10px;font-weight:700;text-decoration:none;font-size:0.9rem}}
  .beehiiv-btn:hover{{opacity:.9;text-decoration:none}}
</style>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{article.get('title', tech['name'])}",
  "description": "{article.get('meta_description', '')}",
  "url": "{SITE_URL}/{lang_code}/{tech['slug']}.html",
  "inLanguage": "{lang_code}",
  "datePublished": "2026-03-13T00:00:00+09:00",
  "dateModified": "{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}",
  "publisher": {{
    "@type": "Organization",
    "name": "BJJ Wiki",
    "url": "{SITE_URL}/"
  }},
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "{SITE_URL}/{lang_code}/{tech['slug']}.html"
  }}
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{
      "@type": "ListItem",
      "position": 1,
      "name": "BJJ Wiki",
      "item": "{SITE_URL}/{lang_code}/index.html"
    }},
    {{
      "@type": "ListItem",
      "position": 2,
      "name": "{article.get('title', tech['name'])}",
      "item": "{SITE_URL}/{lang_code}/{tech['slug']}.html"
    }}
  ]
}}
</script>
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
        "text": "{'It is a fundamental BJJ technique in the ' + tech.get('category','grappling') + ' category. See the full breakdown above.' if lang_code=='en' else '{tech["name"]}ã¯BJJã®æã§ããè©³ç´°ã¯ä¸è¨ãåç§ã' if lang_code=='ja' else '{tech["name"]} Ã© uma tÃ©cnica de BJJ. Veja o detalhamento completo acima.'}"
      }}
    }},
    {{
      "@type": "Question",
      "name": "{'How do I learn ' + tech['name'] + '?' if lang_code=='en' else tech['name'] + 'ã®ç¿å¾æ¹æ³ã¯ï¼' if lang_code=='ja' else 'Como aprender ' + tech['name'] + '?'}",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "{'Follow the step-by-step guide above, drill with a partner, and watch competition footage. BJJ Fanatics instructionals also cover this technique in depth.' if lang_code=='en' else 'ä¸è¨ã®ã¹ããããã¤ã¹ãããã¬ã¤ãã«å¾ãããã¼ããã¼ã¨ããªã«ããè©¦åæ åãè¦ã¦ãã ããã' if lang_code=='ja' else 'Siga o guia passo a passo acima, treine com um parceiro e assista a filmagens de competiÃ§Ã£o.'}"
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
      "name": "{'Set up the position' if lang_code=='en' else 'ãã¸ã·ã§ã³ã®ã»ããã¢ãã' if lang_code=='ja' else 'Configurar a posiÃ§Ã£o'}",
      "text": "{'Position yourself correctly relative to your opponent before attempting the technique.' if lang_code=='en' else 'æãè©¦ã¿ãåã«ç¸æã«å¯¾ãã¦æ­£ãããã¸ã·ã§ã³ãåãã' if lang_code=='ja' else 'Posicione-se corretamente em relaÃ§Ã£o ao seu oponente antes de tentar a tÃ©cnica.'}"
    }},
    {{
      "@type": "HowToStep",
      "name": "{'Execute the technique' if lang_code=='en' else 'æã®å®è¡' if lang_code=='ja' else 'Executar a tÃ©cnica'}",
      "text": "{'Apply the technique with proper mechanics as described in the guide above.' if lang_code=='en' else 'ä¸è¨ã¬ã¤ãã®æ­£ããã¡ã«ãã¯ã¹ã§æãå®è¡ããã' if lang_code=='ja' else 'Aplique a tÃ©cnica com a mecÃ¢nica adequada conforme descrito no guia acima.'}"
    }},
    {{
      "@type": "HowToStep",
      "name": "{'Finish or transition' if lang_code=='en' else 'ãã£ããã·ã¥ã¾ãã¯ãã©ã³ã¸ã·ã§ã³' if lang_code=='ja' else 'Finalizar ou fazer transiÃ§Ã£o'}",
      "text": "{'Finish the submission or transition to a dominant position. Drill until the movement is automatic.' if lang_code=='en' else 'ãµãããã·ã§ã³ã§ä»çããããæ¯éçãªãã¸ã·ã§ã³ã«ãã©ã³ã¸ã·ã§ã³ãåããèªåã«ãªãã¾ã§ããªã«ã' if lang_code=='ja' else 'Finalize a submissÃ£o ou faÃ§a transiÃ§Ã£o para uma posiÃ§Ã£o dominante. Treine atÃ© o movimento ser automÃ¡tico.'}"
    }}
  ]
}}
</script>
</head>
<body>
<div class="container">
  <header>
    <a href="../index.html" class="logo">BJJ<span>Wiki</span></a>
    <nav>
      <a href="../index.html">{labels['home']}</a>
      <a href="../index.html">{labels['all']}</a>
    </nav>
    <div class="lang-switcher">{lang_switcher}</div>
  </header>

  <span class="badge">{tech['category']}</span><br>
  <span class="belt belt-{to_str(article.get('belt_level','white')).lower().split('/')[0].strip()}">{to_str(article.get('belt_level','All Levels'))}</span>
  <h1>{to_str(article.get('h1', tech['name']))}</h1>
  {difficulty_html}
  {belt_guide_html}
  <p>{to_str(article.get('intro', ''))}</p>

  <h2>{'How to Execute' if lang_code=='en' else 'ããæ¹' if lang_code=='ja' else 'Como Executar'}</h2>
  <div class="card"><p>{to_str(article.get('how_to','')).replace(chr(10),'<br>')}</p></div>

  <h2>{'Key Details & Tips' if lang_code=='en' else 'ã³ãã¨æ³¨æç¹' if lang_code=='ja' else 'Detalhes e Dicas'}</h2>
  <div class="card"><p>{to_str(article.get('key_details','')).replace(chr(10),'<br>')}</p></div>

  <h2>{'Variations' if lang_code=='en' else 'ããªã¨ã¼ã·ã§ã³' if lang_code=='ja' else 'VariaÃ§Ãµes'}</h2>
  <div class="card"><p>{to_str(article.get('variations','')).replace(chr(10),'<br>')}</p></div>

  <h2>{'When to Use' if lang_code=='en' else 'ä½¿ãã¿ã¤ãã³ã°' if lang_code=='ja' else 'Quando Usar'}</h2>
  <div class="card"><p>{to_str(article.get('when_to_use','')).replace(chr(10),'<br>')}</p></div>

  <h2>{'Counters & Defenses' if lang_code=='en' else 'ã«ã¦ã³ã¿ã¼ã»é²å¾¡' if lang_code=='ja' else 'Defesas e Contra-ataques'}</h2>
  <div class="card"><p>{to_str(article.get('counters','')).replace(chr(10),'<br>')}</p></div>

  {athletes_html}

  {'<!-- Pro Tip --><div class="pro-tip"><div class="pro-tip-label">ð¡ ' + ('PRO TIP' if lang_code=="en" else 'ãã­ã®ã³ã' if lang_code=="ja" else 'DICA DE PRO') + '</div><p>' + to_str(article.get("pro_tip","")).replace(chr(10),'<br>') + '</p></div>' if article.get('pro_tip') else ''}

  {conditioning_html}
  <!-- ã«ã¼ã«ã»ããã¯ã­ã¹ãªã³ã¯ -->
  <div style="background:#0d1a2e;border-left:4px solid #3a86ff;border-radius:8px;padding:1rem 1.2rem;margin:1.5rem 0">
    <p style="font-size:.9rem;font-weight:700;color:#93c5fd;margin-bottom:.6rem">{"ð Competition Rules" if lang_code=="en" else "ð è©¦åã«ã¼ã«" if lang_code=="ja" else "ð Regras de CompetiÃ§Ã£o"}</p>
    <div style="display:flex;gap:.75rem;flex-wrap:wrap">
      <a href="ibjjf-rules.html" style="background:#111827;border:1px solid #1e3a5f;border-radius:6px;padding:.5rem .9rem;color:#93c5fd;text-decoration:none;font-size:.82rem">{"IBJJF Rules â" if lang_code=="en" else "IBJJFã«ã¼ã« â" if lang_code=="ja" else "Regras IBJJF â"}</a>
      <a href="adcc-rules.html" style="background:#111827;border:1px solid #1e3a5f;border-radius:6px;padding:.5rem .9rem;color:#93c5fd;text-decoration:none;font-size:.82rem">{"ADCC Rules â" if lang_code=="en" else "ADCCã«ã¼ã« â" if lang_code=="ja" else "Regras ADCC â"}</a>
      <a href="bjj-competition-guide.html" style="background:#111827;border:1px solid #1e3a5f;border-radius:6px;padding:.5rem .9rem;color:#93c5fd;text-decoration:none;font-size:.82rem">{"Competition Guide â" if lang_code=="en" else "ç«¶æã¬ã¤ã â" if lang_code=="ja" else "Guia de CompetiÃ§Ã£o â"}</a>
    </div>
  </div>
  <!-- è©¦åæºåã¯ã­ã¹ãªã³ã¯ -->
  <div style="background:#1a0d2e;border-left:4px solid #ff6b6b;border-radius:8px;padding:14px 18px;margin:20px 0">
    <strong style="color:#ff6b6b;font-size:.9rem">{"âï¸ Training Safety & Performance" if lang_code=="en" else "âï¸ ãã¬ã¼ãã³ã°ã®å®å¨ã¨ããã©ã¼ãã³ã¹" if lang_code=="ja" else "âï¸ SeguranÃ§a e Performance no Treino"}</strong>
    <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:10px">
      <a href="bjj-injury-prevention.html" style="background:#2a1a3a;color:#fff;padding:6px 14px;border-radius:20px;text-decoration:none;font-size:.85rem">{"ð¡ï¸ Injury Prevention" if lang_code=="en" else "ð¡ï¸ æªæäºé²" if lang_code=="ja" else "ð¡ï¸ PrevenÃ§Ã£o de LesÃµes"}</a>
      <a href="bjj-warm-up-routine.html" style="background:#2a1a3a;color:#fff;padding:6px 14px;border-radius:20px;text-decoration:none;font-size:.85rem">{"ð¥ Warm-Up" if lang_code=="en" else "ð¥ ã¦ã©ã¼ã ã¢ãã" if lang_code=="ja" else "ð¥ Aquecimento"}</a>
      <a href="bjj-weight-cutting.html" style="background:#2a1a3a;color:#fff;padding:6px 14px;border-radius:20px;text-decoration:none;font-size:.85rem">{"âï¸ Weight Cutting" if lang_code=="en" else "âï¸ æ¸é" if lang_code=="ja" else "âï¸ Corte de Peso"}</a>
      <a href="bjj-mental-game.html" style="background:#2a1a3a;color:#fff;padding:6px 14px;border-radius:20px;text-decoration:none;font-size:.85rem">{"ð§  Mental Game" if lang_code=="en" else "ð§  ã¡ã³ã¿ã«å¼·å" if lang_code=="ja" else "ð§  Jogo Mental"}</a>
      <a href="bjj-competition-prep-checklist.html" style="background:#2a1a3a;color:#fff;padding:6px 14px;border-radius:20px;text-decoration:none;font-size:.85rem">{"ð Comp Prep" if lang_code=="en" else "ð è©¦ååãã§ãã¯" if lang_code=="ja" else "ð Prep CompetiÃ§Ã£o"}</a>
    </div>
  </div>
  <!-- ã¢ãã£ãªã¨ã¤ã -->
  <div class="aff-box" style="display:flex;flex-wrap:wrap;gap:12px;align-items:center">
    <p style="flex:1;min-width:200px">{'Master this technique with world-class instruction' if lang_code=='en' else 'ãã®æãä¸çã¬ãã«ã®æå°ã§ç¿å¾ããã' if lang_code=='ja' else 'Domine esta tÃ©cnica com instruÃ§Ã£o de classe mundial'}</p>
    <div style="display:flex;gap:10px;flex-wrap:wrap">
      <a class="aff-btn" href="https://bjjfanatics.com/search?q={tech['name'].replace(' ','+')}" target="_blank" rel="noopener noreferrer nofollow" onclick="gtag&&gtag('event','fanatics_click',{{technique:'{tech['slug']}',lang:'{lang_code}'}})">
        {'ð¬ Instructionals' if lang_code=='en' else 'ð¬ æååç»' if lang_code=='ja' else 'ð¬ Instrucionais'}
      </a>
      <a class="aff-btn" href="{'https://www.amazon.co.jp/s?k=BJJ+' if lang_code=='ja' else 'https://www.amazon.com/s?k=BJJ+'}{tech['name'].replace(' ','+')}&tag={AMAZON_TAG}" target="_blank" rel="noopener noreferrer nofollow" style="background:#ff9900;color:#111" onclick="gtag&&gtag('event','amazon_click',{{technique:'{tech['slug']}',lang:'{lang_code}'}})">
        {'ð Books on Amazon' if lang_code=='en' else 'ð Amazonã§æ¬ãæ¢ã' if lang_code=='ja' else 'ð Livros na Amazon'}
      </a>
    </div>
  </div>

  {yoga_html}
  {gear_html}

  <div class="faq">
    <div class="faq-q">Q: {article.get('faq_q1','')}</div>
    <p>{article.get('faq_a1','')}</p>
  </div>

  {'<h2>Related Techniques</h2>' if lang_code=='en' else '<h2>é¢é£æ</h2>' if lang_code=='ja' else '<h2>TÃ©cnicas Relacionadas</h2>'}
  <div class="related-links">{related_links}</div>

  <!-- Related Techniques Card Grid -->
  <div style="background:#0f1420;border:1px solid #1f2840;border-radius:12px;padding:24px;margin:32px 0">
    <h3 style="font-size:1rem;font-weight:700;color:#7c6af7;margin-bottom:16px">ð¥ {'Related Techniques' if lang_code=='en' else 'é¢é£æ' if lang_code=='ja' else 'TÃ©cnicas Relacionadas'}</h3>
    <div style="display:flex;flex-wrap:wrap;gap:8px">
      {related_links}
    </div>
  </div>

  {beehiiv_html}

  <!-- Share Bar -->
  <div class="share-bar">
    <p>{'Share this technique' if lang_code=='en' else 'ãã®æãã·ã§ã¢' if lang_code=='ja' else 'Compartilhar esta tÃ©cnica'}</p>
    <div class="share-btns">
      <a class="share-btn x" href="https://twitter.com/intent/tweet?url={SITE_URL}/{lang_code}/{tech['slug']}.html&text={tech['name'].replace(' ','+')}+%23BJJ+%23bjjwiki" target="_blank" rel="noopener noreferrer">ð {'Post on X' if lang_code=='en' else 'Xã«æç¨¿' if lang_code=='ja' else 'Postar no X'}</a>
      <a class="share-btn reddit" href="https://www.reddit.com/submit?url={SITE_URL}/{lang_code}/{tech['slug']}.html&title={tech['name'].replace(' ','+')}" target="_blank" rel="noopener noreferrer">â¬ Reddit</a>
      <button class="share-btn copy" onclick="navigator.clipboard.writeText('{SITE_URL}/{lang_code}/{tech['slug']}.html').then(()=>{{this.textContent='â {'Copied!' if lang_code=='en' else 'ã³ãã¼æ¸ï¼' if lang_code=='ja' else 'Copiado!'}';setTimeout(()=>this.textContent='ð {'Copy Link' if lang_code=='en' else 'ãªã³ã¯ã³ãã¼' if lang_code=='ja' else 'Copiar'}',2000)}})">ð {'Copy Link' if lang_code=='en' else 'ãªã³ã¯ã³ãã¼' if lang_code=='ja' else 'Copiar'}</button>
    </div>
  </div>

  <footer>
    <p>BJJ Wiki â {'The free BJJ technique encyclopedia' if lang_code=='en' else 'ç¡æBJJæè¡ç¾ç§äºå¸' if lang_code=='ja' else 'A enciclopÃ©dia gratuita de tÃ©cnicas de BJJ'}</p>
    <p style="margin-top:8px"><a href="../privacy.html" style="color:var(--muted)">Privacy Policy</a></p>
  </footer>
</div>
  <div id="float-cta" style="position:fixed;bottom:20px;right:20px;z-index:9999;display:none;max-width:280px">
    <div style="background:#1a1a2e;border:1px solid #6e40c9;border-radius:12px;padding:16px;box-shadow:0 4px 20px rgba(0,0,0,.5);position:relative">
      <button onclick="document.getElementById('float-cta').style.display='none';localStorage.setItem('cta_dismissed','1')" style="position:absolute;top:8px;right:10px;background:none;border:none;color:#7a7a9a;font-size:18px;cursor:pointer">Ã</button>
      <p style="margin:0 0 8px;font-size:.85rem;font-weight:700;color:#e2e2ee">ð© Free BJJ Newsletter</p>
      <p style="margin:0 0 12px;font-size:.78rem;color:#7a7a9a">Weekly tips, techniques & drills</p>
      <a href="https://bjjwiki.beehiiv.com/subscribe" target="_blank" rel="noopener" onclick="gtag&&gtag('event','float_cta_click',{{page:location.pathname}})" style="display:block;text-align:center;background:#6e40c9;color:#fff;padding:8px 16px;border-radius:8px;text-decoration:none;font-size:.85rem;font-weight:700">Subscribe Free â</a>
    </div>
  </div>
  <script>
  (function(){{
    if(localStorage.getItem('cta_dismissed')) return;
    var el=document.getElementById('float-cta');
    var shown=false;
    function show(){{if(!shown){{shown=true;el.style.display='block';}}}}
    setTimeout(show,30000);
    window.addEventListener('scroll',function(){{if((window.scrollY/(document.body.scrollHeight-window.innerHeight))>.5)show();}},{{passive:true}});
  }})();
  </script>
</body>
</html>"""

# ===== ã«ãã´ãªå¥ã¤ã³ããã¯ã¹ãã¼ã¸ =====
def generate_category_index(lang_code, techniques_by_category):
    lang = LANGUAGES[lang_code]
    titles = {"en": "All BJJ Techniques", "ja": "å¨BJJæä¸è¦§", "pt": "Todas as TÃ©cnicas de BJJ"}
    descs  = {
        "en": "Complete encyclopedia of Brazilian Jiu-Jitsu techniques. Learn guards, passes, submissions, sweeps and more.",
        "ja": "ãã©ã¸ãªã¢ã³æè¡ï¼BJJï¼ã®æè¡ç¾ç§äºå¸ãã¬ã¼ãããã¹ãçµãæãé¢ç¯æãã¹ã¤ã¼ããç¶²ç¾ã",
        "pt": "EnciclopÃ©dia completa de tÃ©cnicas de Jiu-Jitsu Brasileiro. Aprenda guardas, passagens, finalizaÃ§Ãµes e muito mais."
    }
    cards = ""
    for cat, techs in sorted(techniques_by_category.items()):
        links = "".join([f'<a href="{t["slug"]}.html">{t["name"]}</a>' for t in techs])
        cards += f'<div class="cat-card"><h2>{cat}</h2><div class="tech-links">{links}</div></div>'

    return f"""<!DOCTYPE html>
<html lang="{lang_code}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titles[lang_code]} | BJJ Wiki</title>
<meta name="description" content="{descs[lang_code]}">
<style>
  :root{{--bg:#0a0a0f;--card:#111119;--border:#1e1e2e;--text:#e2e2ee;--muted:#7a7a9a;--accent:#6e40c9}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;padding:0 16px}}
  .container{{max-width:900px;margin:0 auto;padding:24px 0 64px}}
  header{{padding:20px 0;border-bottom:1px solid var(--border);margin-bottom:32px}}
  .logo{{font-size:1.4rem;font-weight:800;color:var(--text);text-decoration:none}}
  .logo span{{color:var(--accent)}}
  h1{{font-size:2rem;font-weight:800;margin-bottom:8px}}
  .subtitle{{color:var(--muted);margin-bottom:32px}}
  .cat-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px}}
  .cat-card h2{{font-size:1rem;font-weight:700;color:var(--accent);margin-bottom:12px}}
  .tech-links{{display:flex;flex-wrap:wrap;gap:8px}}
  .tech-links a{{background:#1e1e2e;color:var(--muted);text-decoration:none;padding:4px 12px;border-radius:6px;font-size:0.85rem;border:1px solid var(--border)}}
  .tech-links a:hover{{color:var(--text);border-color:var(--accent)}}
  footer{{border-top:1px solid var(--border);padding:24px 0;text-align:center;color:var(--muted);font-size:0.8rem}}
</style>
</head>
<body>
<div class="container">
  <header><a href="../index.html" class="logo">BJJ<span>Wiki</span></a></header>
  <h1>{titles[lang_code]}</h1>
  <p class="subtitle">{descs[lang_code]}</p>
  {cards}
  <footer><p>BJJ Wiki</p></footer>
</div>
</body>
</html>"""

# ===== ããããã¼ã¸ =====
def generate_index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BJJ Wiki â Brazilian Jiu-Jitsu Technique Encyclopedia</title>
<meta name="description" content="Free multilingual encyclopedia of Brazilian Jiu-Jitsu techniques. Available in English, Japanese and Portuguese.">
<style>
  :root{--bg:#0a0a0f;--card:#111119;--border:#1e1e2e;--text:#e2e2ee;--muted:#7a7a9a;--accent:#6e40c9}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;padding:0 16px;min-height:100vh;display:flex;align-items:center;justify-content:center}
  .container{max-width:640px;width:100%;text-align:center;padding:48px 0}
  .logo{font-size:3rem;font-weight:900;margin-bottom:16px}
  .logo span{color:var(--accent)}
  .subtitle{color:var(--muted);margin-bottom:48px;font-size:1.1rem}
  .lang-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:32px}
  .lang-btn{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:32px 16px;text-decoration:none;color:var(--text);transition:border-color 0.2s}
  .lang-btn:hover{border-color:var(--accent)}
  .lang-flag{font-size:2.5rem;margin-bottom:8px}
  .lang-name{font-size:1.1rem;font-weight:700}
  .lang-sub{font-size:0.8rem;color:var(--muted);margin-top:4px}
  footer{color:var(--muted);font-size:0.8rem}
</style>
</head>
<body>
<div class="container">
  <div class="logo">BJJ<span>Wiki</span></div>
  <p class="subtitle">The free Brazilian Jiu-Jitsu technique encyclopedia</p>
  <div class="lang-grid">
    <a class="lang-btn" href="en/index.html">
      <div class="lang-flag">ðºð¸</div>
      <div class="lang-name">English</div>
      <div class="lang-sub">Browse in English</div>
    </a>
    <a class="lang-btn" href="ja/index.html">
      <div class="lang-flag">ð¯ðµ</div>
      <div class="lang-name">æ¥æ¬èª</div>
      <div class="lang-sub">æ¥æ¬èªã§èª­ã</div>
    </a>
    <a class="lang-btn" href="pt/index.html">
      <div class="lang-flag">ð§ð·</div>
      <div class="lang-name">PortuguÃªs</div>
      <div class="lang-sub">Ler em PortuguÃªs</div>
    </a>
  </div>
  <footer><p>BJJ Wiki â Free & Open Knowledge</p></footer>
</div>
</body>
</html>"""

# ===== ã­ã£ãã·ã¥ç®¡ç =====
def load_cache():
    path = os.path.join(SITE_DIR, "generated.json")
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return {}

def save_cache(cache):
    path = os.path.join(SITE_DIR, "generated.json")
    with open(path, "w") as f: json.dump(cache, f, ensure_ascii=False, indent=2)

# ===== ã¡ã¤ã³ =====
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="ã­ã£ãã·ã¥ç¡è¦ãã¦å¨åçæ")
    parser.add_argument("--limit", type=int, default=5, help="1åã®å®è¡ã§çæããæå¤§è¨äºæ°ï¼ã³ã¹ãç®¡çï¼")
    parser.add_argument("--lang", default="all", help="çæããè¨èª (en/ja/pt/all)")
    args = parser.parse_args()

    os.makedirs(SITE_DIR, exist_ok=True)
    cache  = {} if args.force else load_cache()
    langs  = list(LANGUAGES.keys()) if args.lang == "all" else [args.lang]
    count  = 0

    # ããããã¼ã¸çæ
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(generate_index())
    print("[OK] index.html çæå®äº")

    # æãã¼ã¸çæ
    for lang_code in langs:
        lang_dir = os.path.join(SITE_DIR, lang_code)
        os.makedirs(lang_dir, exist_ok=True)
        techniques_by_category = {}

        for tech in TECHNIQUES:
            cache_key = f"{lang_code}/{tech['slug']}"
            out_path  = os.path.join(lang_dir, f"{tech['slug']}.html")

            # ã«ãã´ãªåé¡
            cat = tech["category"]
            techniques_by_category.setdefault(cat, []).append(tech)

            # ã­ã£ãã·ã¥æ¸ã¿ãã¤ãã¡ã¤ã«å­å¨ãªãã¹ã­ãã
            if cache_key in cache and os.path.exists(out_path) and not args.force:
                continue

            if count >= args.limit:
                print(f"[INFO] ä¸é({args.limit}ä»¶)ã«éãã¾ãããæ¬¡åå®è¡ã§ç¶ããçæãã¾ãã")
                break

            print(f"[{lang_code}] {tech['name']} çæä¸­...")
            raw = call_gemini(build_article_prompt(tech, lang_code))
            if not raw:
                print(f"[WARNING] {tech['name']} çæå¤±æãã¹ã­ãã")
                continue

            # JSONãã¼ã¹
            try:
                text    = re.sub(r'^```[a-z]*\n?', '', raw.strip(), flags=re.MULTILINE)
                text    = re.sub(r'\n?```$', '', text, flags=re.MULTILINE)
                article = json.loads(text.strip())
            except Exception as e:
                print(f"[WARNING] JSONãã¼ã¹å¤±æ: {e}")
                continue

            # HTMLçæã»ä¿å­ï¼åé¨ãªã³ã¯ä»ä¸ï¼
            html = article_to_html(tech, lang_code, article, TECHNIQUES)
            html = add_internal_links(html, tech["slug"], lang_code)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)

            cache[cache_key] = datetime.datetime.now().isoformat()
            count += 1
            print(f"[OK] {cache_key} â {out_path}")
            time.sleep(1)  # APIè² è·è»½æ¸

        # ã«ãã´ãªã¤ã³ããã¯ã¹çæ
        idx_html = generate_category_index(lang_code, techniques_by_category)
        with open(os.path.join(lang_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(idx_html)
        print(f"[OK] {lang_code}/index.html çæå®äº")

    save_cache(cache)
    print(f"\n[å®äº] {count}ä»¶ã®æ°è¦è¨äºãçæãã¾ãã")
    remaining = sum(
        1 for tech in TECHNIQUES
        for lc in langs
        if f"{lc}/{tech['slug']}" not in cache
    )
    print(f"[æ®ã] ãã¨{remaining}ä»¶æªçæ")

if __name__ == "__main__":
    main()
