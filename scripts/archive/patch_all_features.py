#!/usr/bin/env python3
"""
既存の技記事ページに yoga-box / gear-box / athlete-section を一括追加
（未挿入ページのみ、既存ページはスキップ）
"""

import os
import glob
import re

SITE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
YOGA_URL  = "https://t307239.github.io/yoga-wiki"

# ===== スラッグ→カテゴリ対応表 =====
SLUG_CATEGORY = {
    "closed-guard":"Guard","open-guard":"Guard","half-guard":"Guard","spider-guard":"Guard",
    "de-la-riva-guard":"Guard","berimbolo":"Guard","butterfly-guard":"Guard","rubber-guard":"Guard",
    "x-guard":"Guard","worm-guard":"Guard","reverse-de-la-riva":"Guard","50-50-guard":"Guard",
    "lasso-guard":"Guard","deep-half-guard":"Guard","z-guard":"Guard","sitting-guard":"Guard",
    "guard-pass":"Passing","torreando-pass":"Passing","knee-slice-pass":"Passing",
    "leg-drag-pass":"Passing","headquarters-pass":"Passing","stack-pass":"Passing",
    "double-under-pass":"Passing","pressure-pass":"Passing","smash-pass":"Passing","x-pass":"Passing",
    "double-leg-takedown":"Takedown","single-leg-takedown":"Takedown","osoto-gari":"Takedown",
    "ankle-pick":"Takedown","harai-goshi":"Takedown","ippon-seoi-nage":"Takedown",
    "morote-seoi-nage":"Takedown","snap-down":"Takedown","russian-tie":"Takedown",
    "rear-naked-choke":"Choke","triangle-choke":"Choke","guillotine-choke":"Choke",
    "bow-and-arrow-choke":"Choke","ezekiel-choke":"Choke","darce-choke":"Choke",
    "anaconda-choke":"Choke","loop-choke":"Choke","arm-triangle-choke":"Choke",
    "north-south-choke":"Choke","baseball-choke":"Choke","cross-collar-choke":"Choke",
    "clock-choke":"Choke","lapel-choke":"Choke",
    "armbar":"Joint Lock","kimura":"Joint Lock","americana":"Joint Lock","omoplata":"Joint Lock",
    "wrist-lock":"Joint Lock","straight-armbar":"Joint Lock","monoplata":"Joint Lock",
    "heel-hook":"Leg Lock","inside-heel-hook":"Leg Lock","outside-heel-hook":"Leg Lock",
    "knee-bar":"Leg Lock","toe-hold":"Leg Lock","calf-slicer":"Leg Lock","ankle-lock":"Leg Lock",
    "estima-lock":"Leg Lock",
    "mount":"Position","back-mount":"Position","side-control":"Position","north-south":"Position",
    "knee-on-belly":"Position","s-mount":"Position","modified-mount":"Position",
    "body-triangle":"Position","seat-belt-control":"Position","front-headlock":"Position",
    "underhook":"Position","overhook":"Position","turtle-position":"Position",
    "scissor-sweep":"Sweep","flower-sweep":"Sweep","hip-bump-sweep":"Sweep","pendulum-sweep":"Sweep",
    "tripod-sweep":"Sweep","elevator-sweep":"Sweep","sickle-sweep":"Sweep",
    "overhead-sweep":"Sweep","balloon-sweep":"Sweep","x-guard-sweep":"Sweep",
    "arm-drag":"Transition","granby-roll":"Transition","backtake":"Transition",
    "technical-standup":"Transition","stand-in-base":"Transition",
    "shrimp-escape":"Escape","bridge-and-roll":"Escape","elbow-knee-escape":"Escape",
    "guard-retention":"Defense","hip-escape":"Defense","frame":"Defense",
    "sprawl":"Defense","back-defense":"Defense",
}

# ===== Yoga マッピング =====
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
    "americana":[("cow-face-pose","Cow Face Pose"),("eagle-pose","Eagle Pose")],
    "back-mount":[("bridge-pose","Bridge Pose"),("boat-pose","Boat Pose")],
    "mount":[("bridge-pose","Bridge Pose"),("boat-pose","Boat Pose")],
    "side-control":[("bridge-pose","Bridge Pose"),("thread-the-needle","Thread the Needle")],
    "ankle-lock":[("happy-baby-pose","Happy Baby Pose"),("reclined-pigeon","Reclined Pigeon")],
    "toe-hold":[("happy-baby-pose","Happy Baby Pose"),("lizard-pose","Lizard Pose")],
    "calf-slicer":[("happy-baby-pose","Happy Baby Pose"),("reclined-pigeon","Reclined Pigeon")],
    "bow-and-arrow-choke":[("cat-cow-pose","Cat-Cow Pose"),("childs-pose","Child's Pose")],
    "darce-choke":[("cat-cow-pose","Cat-Cow Pose"),("childs-pose","Child's Pose")],
    "anaconda-choke":[("cat-cow-pose","Cat-Cow Pose"),("childs-pose","Child's Pose")],
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

# ===== ギアマッピング =====
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

# ===== 選手マッピング =====
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
    "americana":[("marcelo-garcia","Marcelo Garcia","🇧🇷"),("john-danaher","John Danaher","🇺🇸")],
    "ankle-lock":[("gordon-ryan","Gordon Ryan","🇺🇸"),("craig-jones","Craig Jones","🇦🇺")],
}

SKIP_PAGES = {"index","privacy","about","404","athletes","news"}

def get_slug_from_path(path):
    return os.path.splitext(os.path.basename(path))[0]

def detect_lang(path):
    parts = path.split(os.sep)
    for p in parts:
        if p in ("en","ja","pt"): return p
    return "en"

def build_yoga_html(slug, category, lang):
    poses = YOGA_SLUG_MAP.get(slug, YOGA_CAT_DEFAULTS.get(category, []))[:3]
    if not poses: return ""
    label = {"en":"🧘 Yoga Poses to Improve This Technique","ja":"🧘 この技に効くヨガポーズ","pt":"🧘 Yoga para Esta Técnica"}[lang]
    sub   = {"en":"Build the flexibility & mobility you need:","ja":"必要な柔軟性・可動域を高めます：","pt":"Melhore sua flexibilidade:"}[lang]
    chips = "".join([
        f'<a class="yoga-chip" href="{YOGA_URL}/en/{sl}.html" target="_blank" rel="noopener noreferrer">🧘 {nm}</a>'
        for sl, nm in poses
    ])
    return (
        f'\n<style>.yoga-box{{background:linear-gradient(135deg,#0a1a10,#0f1a0a);border:1px solid #22c55e;border-radius:12px;padding:20px;margin:24px 0}}'
        f'.yoga-box h3{{font-size:.85rem;font-weight:700;color:#22c55e;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}}'
        f'.yoga-box p{{font-size:.85rem;color:#6b9e6b;margin-bottom:12px}}'
        f'.yoga-chips{{display:flex;flex-wrap:wrap;gap:8px}}'
        f'.yoga-chip{{display:inline-block;padding:6px 14px;background:#0d2010;border:1px solid #22c55e40;border-radius:20px;font-size:.82rem;color:#86efac;text-decoration:none;font-weight:600}}'
        f'.yoga-chip:hover{{background:#22c55e;color:#000;text-decoration:none}}</style>\n'
        f'<div class="yoga-box"><h3>{label}</h3><p>{sub}</p>'
        f'<div class="yoga-chips">{chips}</div></div>\n'
    )

def build_gear_html(category, lang):
    items = GEAR_CAT_MAP.get(category, [])
    if not items: return ""
    label = {"en":"⚙️ Recommended Gear","ja":"⚙️ おすすめギア","pt":"⚙️ Equipamento Recomendado"}[lang]
    links = "".join([
        f'<a class="gear-link" href="{sl}.html">{nm}</a>'
        for sl, nm in items
    ])
    return (
        f'\n<style>.gear-box{{background:#0f1420;border:1px solid #1f2840;border-radius:12px;padding:18px;margin:20px 0}}'
        f'.gear-box h3{{font-size:.82rem;font-weight:700;color:#6b7699;text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px}}'
        f'.gear-links{{display:flex;flex-wrap:wrap;gap:8px}}'
        f'.gear-link{{display:inline-block;padding:6px 14px;background:#141926;border:1px solid #1f2840;border-radius:20px;font-size:.82rem;color:#8899bb;text-decoration:none}}'
        f'.gear-link:hover{{border-color:#6b7699;color:#c0cce8;text-decoration:none}}</style>\n'
        f'<div class="gear-box"><h3>{label}</h3><div class="gear-links">{links}</div></div>\n'
    )

def build_athlete_html(slug, lang):
    athletes = ATHLETE_MAP.get(slug, [])
    if not athletes: return ""
    label = {"en":"🏆 Elite Athletes Who Use This","ja":"🏆 この技を使うエリート選手","pt":"🏆 Atletas de Elite"}[lang]
    chips = "".join([
        f'<a class="athlete-chip" href="../{lang}/athlete-{s}.html">'
        f'<span style="font-size:1.2rem">{fl}</span>'
        f'<span><strong style="display:block;font-size:.9rem">{nm}</strong></span></a>'
        for s, nm, fl in athletes
    ])
    return (
        f'\n<style>.athletes-section{{margin:28px 0}}'
        f'.athletes-section h2{{font-size:.9rem;font-weight:700;color:#a78bfa;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px}}'
        f'.athlete-chips{{display:flex;flex-wrap:wrap;gap:10px}}'
        f'.athlete-chip{{display:flex;align-items:center;gap:10px;background:#141926;border:1px solid #1f2840;border-radius:12px;padding:12px 16px;text-decoration:none;color:#e8eaf6;transition:border-color .2s}}'
        f'.athlete-chip:hover{{border-color:#7c6af7;text-decoration:none}}</style>\n'
        f'<div class="athletes-section"><h2>{label}</h2><div class="athlete-chips">{chips}</div></div>\n'
    )

def patch_file(path):
    slug = get_slug_from_path(path)
    lang = detect_lang(path)

    # アスリートページ・特別ページはスキップ
    if slug in SKIP_PAGES or slug.startswith("athlete-") or slug.startswith("best-"):
        return False

    category = SLUG_CATEGORY.get(slug, "Guard")

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # ===== 挿入点を見つける（<div class="beehiiv-wrap">の直前）=====
    # beehiiv-wrapの実際のdivタグを探す
    insert_marker = None
    for marker in ['<div class="beehiiv-wrap">', "<div class='beehiiv-wrap'>",
                   '<!-- beehiiv', '<!-- Share Bar -->', '<div class="share-bar">']:
        idx = content.find(marker)
        if idx != -1:
            insert_marker = marker
            break

    if insert_marker is None:
        print(f"  SKIP (no insertion point): {path}")
        return False

    added = False
    inject = ""

    # yoga-box 追加
    if "yoga-box" not in content and "yoga-chip" not in content:
        yoga = build_yoga_html(slug, category, lang)
        if yoga:
            inject += yoga
            added = True

    # gear-box 追加
    if "gear-box" not in content and "gear-link" not in content:
        gear = build_gear_html(category, lang)
        if gear:
            inject += gear
            added = True

    # athlete-section 追加
    if "athletes-section" not in content and "athlete-chip" not in content:
        ath = build_athlete_html(slug, lang)
        if ath:
            inject += ath
            added = True

    if not inject:
        return False  # 何も追加なし

    # 挿入点の前にinjectを追加
    idx = content.find(insert_marker)
    new_content = content[:idx] + inject + content[idx:]

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def main():
    patched = 0
    skipped = 0
    for lang in ["en", "ja", "pt"]:
        files = sorted(glob.glob(os.path.join(SITE_DIR, lang, "*.html")))
        for path in files:
            result = patch_file(path)
            if result:
                patched += 1
            else:
                skipped += 1

    print(f"\n✅ 完了: {patched}ページ更新, {skipped}ページスキップ")

if __name__ == "__main__":
    main()
