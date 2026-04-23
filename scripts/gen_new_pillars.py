#!/usr/bin/env python3
# ⚠️ DEPRECATED — DO NOT RUN ⚠️
# このスクリプトはアフィリリンク(bjj06-22/bjjfanatics)を含む旧バッチスクリプトです。
# CLAUDE.md「アフィリリンク完全禁止」ルールにより使用禁止。
# 実行するとアフィリリンクが再注入され先祖返りします。
# 代わりに generate_bjj_wiki.py を使用してください。
"""
Generate 6 new high-value pillar pages in en/ja/pt.
Pages: bjj-belt-system, bjj-terminology, bjj-rules-for-beginners,
       bjj-vs-wrestling, bjj-training-tips, best-bjj-gi-guide
"""
import os, json
from datetime import date

TODAY = date.today().isoformat()
ADSENSE_ID = 'ca-pub-5529701443220352'
GA4_ID = 'G-7LM8L3TRZM'

PAGES = {
    'bjj-belt-system': {
        'en': {
            'title': 'BJJ Belt System Explained | Ranks, Requirements & Timeline',
            'desc': 'Complete guide to the Brazilian Jiu-Jitsu belt system — from white belt to black belt, requirements, and how long each rank takes.',
            'h1': 'BJJ Belt System: Complete Guide to All Ranks',
            'intro': 'Brazilian Jiu-Jitsu uses a belt ranking system to indicate a practitioner\'s skill level. Unlike many other martial arts, BJJ belts are notoriously difficult to earn — a black belt typically takes 10+ years. Understanding the belt system helps you set realistic goals and appreciate the journey.',
            'faq': [
                ('How long does it take to get a black belt in BJJ?', 'The average time to black belt in BJJ is 10–15 years of consistent training. This is significantly longer than most other martial arts, which is why a BJJ black belt commands enormous respect.'),
                ('What are the BJJ belt ranks in order?', 'The adult BJJ belt ranks in order are: White, Blue, Purple, Brown, and Black. There are also higher degrees of black belt, up to 9th degree (red belt).'),
                ('How many stripes are on each belt?', 'Each belt (except black) has up to 4 stripes, awarded for progression before promotion to the next belt. Stripes represent knowledge, attendance, and contribution to the academy.'),
            ],
            'belts': [
                ('⬜ White Belt', 'No experience required. Focus: survival, basic positions (mount, guard, side control), and fundamental escapes. Average time: 1–2 years.'),
                ('🔵 Blue Belt', 'First major milestone. You have a solid foundation and understand positional hierarchy. Average time: 2–3 years at white belt. Minimum age: 16.'),
                ('🟣 Purple Belt', 'Advanced practitioner. You have a personal game and can teach fundamentals. Average time: 1.5–2 years at blue belt.'),
                ('🟤 Brown Belt', 'Near-expert level. Refining and perfecting your technique. Average time: 1–2 years at purple belt.'),
                ('⬛ Black Belt', 'Expert level. Mastery of all fundamentals and a well-developed personal game. Minimum 10 years total from white belt.'),
            ],
        },
        'ja': {
            'title': 'BJJの帯制度を解説 | 白帯から黒帯まで昇格条件と期間',
            'desc': 'ブラジリアン柔術の帯制度を完全解説。白帯・青帯・紫帯・茶帯・黒帯の条件と平均期間。',
            'h1': 'BJJ帯制度：全ランクの完全ガイド',
        },
        'pt': {
            'title': 'Sistema de Faixas do BJJ | Graus, Requisitos e Tempo',
            'desc': 'Guia completo do sistema de faixas do Brazilian Jiu-Jitsu — da faixa branca à preta, requisitos e quanto tempo leva cada graduação.',
            'h1': 'Sistema de Faixas do BJJ: Guia Completo',
        },
    },
    'bjj-terminology': {
        'en': {
            'title': 'BJJ Terminology & Glossary | 50+ Essential Terms Explained',
            'desc': 'Complete BJJ terminology guide — 50+ Portuguese, Japanese, and English terms every practitioner needs to know.',
            'h1': 'BJJ Terminology: The Ultimate Glossary',
            'intro': 'BJJ has a unique vocabulary mixing Portuguese, Japanese (from judo roots), and English slang. Whether you\'re a beginner confused on the mats or studying for competition, this glossary covers everything you need.',
            'faq': [
                ('What language is most BJJ terminology from?', 'BJJ terminology comes primarily from Portuguese (since BJJ was developed in Brazil) and Japanese (from the judo roots of BJJ). English terms are also common, especially in American BJJ academies.'),
                ('What does "tap" mean in BJJ?', '"Tap" means to submit — to signal that you are caught in a submission and are giving up the round. You can tap by patting your partner, the mat, or verbally saying "tap." Always tap before you get hurt.'),
                ('What is "rolling" in BJJ?', '"Rolling" is the BJJ term for sparring or live drilling. When you "roll" with a partner, you are practicing live grappling against resistance.'),
            ],
            'terms': [
                ('Guard', 'A position where you are on your back using your legs to control your opponent.'),
                ('Mount', 'A dominant top position where you sit on your opponent\'s torso.'),
                ('Side Control', 'A dominant top position beside your opponent\'s hips.'),
                ('Back Take', 'Taking a position behind your opponent with hooks in — one of the most dominant positions.'),
                ('Sweep', 'Reversing position from bottom to top.'),
                ('Pass', 'Getting past your opponent\'s guard to side control, mount, or back.'),
                ('Submission', 'A joint lock or choke that forces your opponent to tap.'),
                ('Tap', 'The act of submitting — patting your partner or saying "tap."'),
                ('Roll', 'To spar/grapple live against a partner.'),
                ('Shrimp', 'A hip escape movement used to create space from bottom.'),
                ('Bridge', 'An explosive hip buck used to escape bottom positions.'),
                ('Clinch', 'A standing grappling grip used to control distance.'),
                ('Sprawl', 'A defensive movement to stop a takedown attempt.'),
                ('Jiu-Jitsu', 'Translates to "gentle art" in Japanese/Portuguese.'),
                ('OSS', 'A BJJ/martial arts greeting expressing respect and acknowledgment.'),
            ],
        },
        'ja': {
            'title': 'BJJ用語集 | 50以上の必須ポルトガル語・英語用語を解説',
            'desc': 'ブラジリアン柔術の用語集。50以上のポルトガル語・日本語・英語の必須用語を完全網羅。',
            'h1': 'BJJ用語集：完全ガイド',
        },
        'pt': {
            'title': 'Terminologia do BJJ | Glossário com +50 Termos Essenciais',
            'desc': 'Guia completo de terminologia do BJJ — mais de 50 termos em português, japonês e inglês que todo praticante precisa saber.',
            'h1': 'Terminologia do BJJ: Glossário Completo',
        },
    },
    'bjj-rules-for-beginners': {
        'en': {
            'title': 'BJJ Rules for Beginners | IBJJF Scoring, Fouls & Competition Guide',
            'desc': 'Learn BJJ competition rules for beginners — IBJJF scoring system, points, advantages, and what techniques are legal at each belt level.',
            'h1': 'BJJ Rules for Beginners: Competition Guide',
            'intro': 'Understanding BJJ competition rules helps you train smarter and compete with confidence. The IBJJF (International Brazilian Jiu-Jitsu Federation) ruleset is the most widely used. Here\'s everything you need to know.',
            'faq': [
                ('How does the BJJ points system work?', 'BJJ uses a points system: Takedown = 2 pts, Guard Pass = 3 pts, Mount = 4 pts, Back Control = 4 pts, Knee on Belly = 2 pts. Advantages are given for near-scoring actions and are used as tiebreakers.'),
                ('What submissions are illegal in BJJ for white belts?', 'At white belt, leg locks (heel hooks, knee bars, toe holds) and spine locks are generally prohibited in IBJJF. Straight ankle locks are allowed for adults. Always check the specific ruleset for your event.'),
                ('How long are BJJ matches?', 'IBJJF match times vary by belt and age: Adults White belt = 5 min, Blue = 6 min, Purple = 7 min, Brown = 8 min, Black = 10 min. Masters divisions typically have slightly shorter matches.'),
            ],
            'rules': [
                ('Takedown (2 pts)', 'Taking your opponent from standing to the ground and maintaining top position for 3 seconds.'),
                ('Guard Pass (3 pts)', 'Passing your opponent\'s guard and establishing a dominant position for 3 seconds.'),
                ('Knee on Belly (2 pts)', 'Placing your knee on your opponent\'s belly while standing.'),
                ('Mount or Back (4 pts)', 'Achieving full mount or back control with both hooks in, held for 3 seconds.'),
                ('Submission Win', 'Making your opponent tap via choke or joint lock. Immediate victory.'),
                ('Advantage', 'Awarded for near-scoring actions. Used as tiebreaker at the end of a match.'),
            ],
        },
        'ja': {
            'title': 'BJJ初心者向けルール解説 | IBJJFスコアリング・反則・試合ガイド',
            'desc': 'BJJの競技ルールを初心者向けに解説。IBJJFのポイント制度、アドバンテージ、反則、ベルト別解禁技を網羅。',
            'h1': 'BJJ競技ルール完全ガイド（初心者向け）',
        },
        'pt': {
            'title': 'Regras do BJJ para Iniciantes | Pontuação IBJJF e Guia de Competição',
            'desc': 'Aprenda as regras de competição do BJJ — sistema de pontos IBJJF, vantagens, faltas e técnicas permitidas em cada faixa.',
            'h1': 'Regras do BJJ para Iniciantes: Guia Completo',
        },
    },
    'bjj-vs-wrestling': {
        'en': {
            'title': 'BJJ vs Wrestling | Key Differences, Similarities & Which to Learn First',
            'desc': 'BJJ vs Wrestling — complete comparison of techniques, rules, scoring, and which martial art suits your goals.',
            'h1': 'BJJ vs Wrestling: Full Comparison Guide',
            'intro': 'BJJ and wrestling share a common foundation in grappling but differ significantly in goals, techniques, and rulesets. Many elite grapplers train both — and for good reason. Here\'s how they compare.',
            'faq': [
                ('Is wrestling good for BJJ?', 'Yes — wrestling is arguably the best base for BJJ. Wrestlers bring superior takedown defense, top pressure, and aggressive positioning. Many BJJ world champions have a strong wrestling background.'),
                ('Does BJJ work in wrestling matches?', 'BJJ submissions are not legal in traditional wrestling. However, BJJ-style guards and leg entanglements may be partially used. For MMA and submission grappling, BJJ is highly complementary to wrestling.'),
                ('Which is better for self-defense, BJJ or wrestling?', 'Both are excellent. Wrestling gives you superior takedowns and the ability to control standing situations. BJJ adds submission finishing skills and guard-based defensive ground fighting. Combined, they are highly effective.'),
            ],
            'comparisons': [
                ('Goal', 'BJJ: Force a submission or outscore on points. | Wrestling: Pin opponent or outscore on points.'),
                ('Ground Game', 'BJJ: Guard, sweeps, submissions are primary. | Wrestling: Turns, pins, and scrambles are primary.'),
                ('Takedowns', 'BJJ: Taught but not always emphasized. | Wrestling: Core focus with double-leg, single-leg, etc.'),
                ('Submissions', 'BJJ: Extensive — chokes, joint locks. | Wrestling: Not legal in traditional rulesets.'),
                ('Competition Format', 'BJJ: Gi or No-Gi, 5–10 minute matches. | Wrestling: Folkstyle, Freestyle, or Greco-Roman formats.'),
                ('Self-Defense Value', 'BJJ: High — especially ground control. | Wrestling: High — especially takedown and clinch control.'),
            ],
        },
        'ja': {
            'title': 'BJJ vs レスリング | 違い・共通点・どちらを先に学ぶべきか',
            'desc': 'BJJとレスリングの完全比較。技術・ルール・スコアリング・どちらがあなたの目標に合うかを解説。',
            'h1': 'BJJ vs レスリング：完全比較ガイド',
        },
        'pt': {
            'title': 'BJJ vs Luta Livre | Diferenças, Semelhanças e O Que Aprender Primeiro',
            'desc': 'Comparação completa entre BJJ e Wrestling — técnicas, regras, pontuação e qual arte marcial se adapta melhor aos seus objetivos.',
            'h1': 'BJJ vs Wrestling: Guia de Comparação Completo',
        },
    },
    'bjj-training-tips': {
        'en': {
            'title': 'BJJ Training Tips | 15 Proven Ways to Improve Faster',
            'desc': '15 proven BJJ training tips to accelerate your progress — from drilling strategy to mindset, recovery, and competition prep.',
            'h1': 'BJJ Training Tips: 15 Ways to Improve Faster',
            'intro': 'Progress in BJJ isn\'t just about mat time — it\'s about quality of training. These 15 tips, used by black belts and competitors worldwide, will help you get more from every session.',
            'faq': [
                ('How many days a week should I train BJJ?', 'Most practitioners improve fastest at 3–4 sessions per week. This allows adequate recovery while maintaining frequency. More than 5 sessions per week risks overtraining and injury, especially for beginners.'),
                ('Should I drill or roll more in BJJ?', 'Both are important. Drilling builds technique precision without fatigue. Rolling (sparring) tests your technique under resistance. A balanced 40/60 drill-to-roll ratio is a solid starting point.'),
                ('How do I get better at BJJ faster?', 'The fastest path to improvement is: consistent training (3–4x/week), quality drilling with intention, watching instructional content and competition footage, asking your instructor targeted questions, and competing regularly.'),
            ],
            'tips': [
                ('Train consistently, not occasionally', 'Three sessions per week beats ten sessions in one week then nothing. Consistency over intensity.'),
                ('Focus on positions before submissions', 'White and blue belts should invest heavily in positional dominance. Submissions follow naturally from good positions.'),
                ('Drill, don\'t just roll', 'Rolling is fun but drilling ingrains technique. Dedicate 20–30 min per session to isolated drilling.'),
                ('Write a training journal', 'Note what worked, what got you submitted, and what you want to drill next. Review before every session.'),
                ('Tap early and often', 'Tapping in practice is learning. Fighting a submission until injury is a waste of mat time.'),
                ('Watch competition footage', 'Study high-level competition on YouTube. Pick one technique and drill it that week.'),
                ('Focus on fundamentals always', 'Black belts win with basics executed flawlessly. Don\'t neglect your closed guard just because it\'s "boring."'),
                ('Rest and recover', 'Sleep 7–9 hours, eat enough protein (1.6g/kg bodyweight), and take rest days seriously.'),
            ],
        },
        'ja': {
            'title': 'BJJトレーニングのコツ | 上達を加速する15の実証済み方法',
            'desc': '15の実証済みBJJトレーニングのコツ。ドリル戦略からメンタル、回復、競技準備まで。',
            'h1': 'BJJトレーニングのコツ：15の上達法',
        },
        'pt': {
            'title': 'Dicas de Treino de BJJ | 15 Formas Comprovadas de Evoluir Mais Rápido',
            'desc': '15 dicas comprovadas de treino de BJJ para acelerar seu progresso — de estratégia de drilling a mentalidade, recuperação e preparação para competição.',
            'h1': 'Dicas de Treino de BJJ: 15 Formas de Melhorar Mais Rápido',
        },
    },
    'best-bjj-gi-guide': {
        'en': {
            'title': 'Best BJJ Gi Guide 2026 | How to Choose the Right Gi for Your Level',
            'desc': 'Complete BJJ gi buying guide — best gi for beginners, competitors, and training. What to look for in weave, collar, and fit.',
            'h1': 'Best BJJ Gi Guide: How to Choose the Right One',
            'intro': 'Your gi (kimono) is your most essential piece of BJJ gear. A good gi fits well, survives hundreds of washes, and doesn\'t limit your movement. This guide explains what to look for and recommends options at every price point.',
            'faq': [
                ('What size gi should I buy for BJJ?', 'Most brands use A0–A5 sizing where A0 is smallest. Gis shrink after washing — choose your size based on the brand\'s specific chart. When in doubt, size up for shrinkage allowance.'),
                ('What is the difference between single and double weave gis?', 'Single weave gis are lighter and better for hot gyms and competition. Double weave gis are heavier and more durable. Pearl weave (most popular) is a middle ground — light, durable, and comfortable.'),
                ('Are expensive BJJ gis worth it?', 'Above $100 USD, diminishing returns apply. Mid-range gis ($80–$150) are usually sufficient for all training needs. Very expensive gis ($200+) are often fashion items with no meaningful performance advantage.'),
            ],
            'picks': [
                ('Best for Beginners', 'Venum Contender Gi — durable, affordable (~$70), comes in all sizes. Great first gi with a comfortable cut and single-weave fabric that holds up to heavy training.'),
                ('Best Mid-Range', 'Fuji All-Around Gi — a community favorite for years. Pearl weave, preshrunk, consistent sizing. ~$90–$110.'),
                ('Best Premium', 'Scramble Athlete Gi — Japanese-cut, lightweight pearl weave, excellent stitching. Ideal for competitors. ~$150–$180.'),
                ('Best No-Gi', 'Rashguard + Spats combo. No standard recommendation — personal preference. Look for durable stretch fabric and flatlock stitching.'),
            ],
        },
        'ja': {
            'title': 'BJJ道衣おすすめガイド 2026 | レベル別の選び方と人気ブランド',
            'desc': 'BJJ道衣（柔術衣）の完全バイヤーズガイド。初心者・競技者・練習用のおすすめと選び方のポイント。',
            'h1': 'BJJ道衣ガイド：自分に合った道衣の選び方',
        },
        'pt': {
            'title': 'Guia do Melhor Kimono de BJJ 2026 | Como Escolher o Gi Certo',
            'desc': 'Guia completo para comprar kimono de BJJ — o melhor gi para iniciantes, competidores e treino. O que avaliar no tecido, gola e caimento.',
            'h1': 'Guia do Melhor Kimono de BJJ: Como Escolher o Certo',
        },
    },
}

def make_page(slug, lang, data, all_data):
    title = data['title']
    desc = data['desc']
    h1 = data['h1']
    intro = all_data['en'].get('intro', '')
    faq = all_data['en'].get('faq', [])

    # Build FAQ JSON-LD
    faq_items = []
    for q, a in faq:
        faq_items.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}
        })
    faq_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faq_items
    }, ensure_ascii=False, indent=2)

    article_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "datePublished": TODAY,
        "dateModified": TODAY,
        "author": {"@type": "Organization", "name": "BJJ Wiki"},
        "publisher": {"@type": "Organization", "name": "BJJ Wiki"}
    }, ensure_ascii=False, indent=2)

    # hreflang
    hreflang = f'''
    <link rel="alternate" hreflang="en" href="https://wiki.bjj-app.net/en/{slug}.html">
    <link rel="alternate" hreflang="ja" href="https://wiki.bjj-app.net/ja/{slug}.html">
    <link rel="alternate" hreflang="pt" href="https://wiki.bjj-app.net/pt/{slug}.html">
    <link rel="alternate" hreflang="x-default" href="https://wiki.bjj-app.net/en/{slug}.html">'''

    # Build body content
    content_sections = ''

    if 'belts' in all_data['en']:
        content_sections += '<h2>Belt Ranks</h2>\n<div style="display:grid;gap:12px;margin:16px 0">'
        for belt, desc_text in all_data['en']['belts']:
            content_sections += f'<div style="background:#0a1428;border:1px solid #1565c0;border-radius:10px;padding:14px 18px"><strong style="color:#64b5f6">{belt}</strong><p style="margin:6px 0 0;font-size:.9rem;color:#b0bec5">{desc_text}</p></div>\n'
        content_sections += '</div>\n'

    if 'terms' in all_data['en']:
        content_sections += '<h2>Essential Terms</h2>\n<div class="related-links" style="display:grid;gap:8px;margin:16px 0">'
        for term, meaning in all_data['en']['terms']:
            content_sections += f'<div style="background:#0a1428;border:1px solid #263238;border-radius:8px;padding:12px 16px"><strong style="color:#80cbc4">{term}</strong> — <span style="color:#b0bec5;font-size:.9rem">{meaning}</span></div>\n'
        content_sections += '</div>\n'

    if 'rules' in all_data['en']:
        content_sections += '<h2>Scoring System</h2>\n<div style="display:grid;gap:10px;margin:16px 0">'
        for rule, explanation in all_data['en']['rules']:
            content_sections += f'<div style="background:#0a1428;border:1px solid #1b5e20;border-radius:8px;padding:12px 16px"><strong style="color:#a5d6a7">{rule}</strong><p style="margin:6px 0 0;font-size:.9rem;color:#b0bec5">{explanation}</p></div>\n'
        content_sections += '</div>\n'

    if 'comparisons' in all_data['en']:
        content_sections += '<h2>Head-to-Head Comparison</h2>\n<div style="display:grid;gap:10px;margin:16px 0">'
        for aspect, comp in all_data['en']['comparisons']:
            content_sections += f'<div style="background:#0a1428;border:1px solid #4a148c;border-radius:8px;padding:12px 16px"><strong style="color:#ce93d8">{aspect}</strong><p style="margin:6px 0 0;font-size:.88rem;color:#b0bec5">{comp}</p></div>\n'
        content_sections += '</div>\n'

    if 'tips' in all_data['en']:
        content_sections += '<h2>Training Tips</h2>\n<div style="display:grid;gap:10px;margin:16px 0">'
        for i, (tip, exp) in enumerate(all_data['en']['tips'], 1):
            content_sections += f'<div style="background:#0a1428;border:1px solid #e65100;border-radius:8px;padding:12px 16px"><strong style="color:#ffcc02">{i}. {tip}</strong><p style="margin:6px 0 0;font-size:.9rem;color:#b0bec5">{exp}</p></div>\n'
        content_sections += '</div>\n'

    if 'picks' in all_data['en']:
        content_sections += '<h2>Our Picks</h2>\n<div style="display:grid;gap:12px;margin:16px 0">'
        for pick, explanation in all_data['en']['picks']:
            content_sections += f'<div style="background:#0a1428;border:1px solid #b71c1c;border-radius:10px;padding:14px 18px"><strong style="color:#ef9a9a">{pick}</strong><p style="margin:6px 0 0;font-size:.9rem;color:#b0bec5">{explanation}</p></div>\n'
        content_sections += '</div>\n'

    # FAQ section
    if faq:
        content_sections += '<h2>FAQ</h2>\n'
        for q, a in faq:
            content_sections += f'<details style="margin:8px 0;background:#0d1f0d;border:1px solid #2e7d32;border-radius:8px;padding:12px 16px"><summary style="font-weight:700;cursor:pointer;color:#a5d6a7">{q}</summary><p style="margin:10px 0 0;color:#b0bec5;font-size:.9rem">{a}</p></details>\n'

    # Fanatics block
    fanatics_block = f'''<div class="aff-box" style="background:linear-gradient(135deg,#0a1428,#0d1f3c);border:1px solid #1565c0;border-radius:12px;padding:20px 24px;margin:32px 0;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;">
  <div>
    <div style="font-size:.8rem;color:#64b5f6;letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px">🎬 Learn from the Best</div>
    <p style="margin:0;color:#e3f2fd;font-size:.95rem">Take your BJJ to the next level with world-class instructionals on BJJ Fanatics.</p>
  </div>
  <a href="https://bjjfanatics.com/?ref=BJJWIKI" target="_blank" rel="noopener sponsored"
     style="background:#1565c0;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:700;white-space:nowrap;font-size:.9rem">
    🎬 Browse Instructionals (20% OFF: BJJWIKI)
  </a>
</div>'''

    beehiiv_block = '''<div class="beehiiv-box" style="background:linear-gradient(135deg,#0a1a0a,#0d2010);border:1px solid #2e7d32;border-radius:12px;padding:20px 24px;margin:32px 0;text-align:center;">
  <div style="font-size:1.05rem;font-weight:700;color:#a5d6a7;margin-bottom:8px">📬 BJJ Wiki Newsletter</div>
  <p style="margin:0 0 16px;color:#c8e6c9;font-size:.9rem">Training tips, new technique breakdowns, and competition insights — weekly, free.</p>
  <a href="https://bjjwiki.beehiiv.com/subscribe" target="_blank" rel="noopener"
     style="background:#2e7d32;color:#fff;padding:10px 24px;border-radius:8px;text-decoration:none;font-weight:700;font-size:.9rem">
    Subscribe Free
  </a>
</div>'''

    nav_lang = '../en' if lang != 'en' else '.'

    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <link rel="icon" href="https://wiki.bjj-app.net/favicon.svg" type="image/svg+xml">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="https://wiki.bjj-app.net/{lang}/{slug}.html">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://wiki.bjj-app.net/{lang}/{slug}.html">
  <meta property="og:image" content="https://wiki.bjj-app.net/og-image.svg">
  <meta name="twitter:card" content="summary_large_image">
  {hreflang}
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>
  <script type="application/ld+json">
{faq_schema}
  </script>
  <script type="application/ld+json">
{article_schema}
  </script>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:#0a0a0a;color:#e0e0e0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.7}}
    header{{background:linear-gradient(135deg,#0d1f3c,#0a0a0a);padding:16px 20px;border-bottom:1px solid #1a2a3a}}
    nav a{{color:#64b5f6;text-decoration:none;margin-right:16px;font-size:.9rem}}
    main{{max-width:860px;margin:0 auto;padding:24px 20px 60px}}
    h1{{font-size:1.8rem;color:#e3f2fd;margin:0 0 16px;line-height:1.3}}
    h2{{font-size:1.2rem;color:#90caf9;margin:28px 0 12px;border-bottom:1px solid #1a2a3a;padding-bottom:6px}}
    p{{margin:0 0 14px;color:#cfd8dc}}
    details summary{{list-style:none}}
    details summary::-webkit-details-marker{{display:none}}
    .breadcrumb{{font-size:.8rem;color:#546e7a;margin-bottom:20px}}
    .breadcrumb a{{color:#546e7a;text-decoration:none}}
    footer{{background:#0d1f3c;padding:20px;text-align:center;font-size:.8rem;color:#546e7a;margin-top:40px}}
    footer a{{color:#64b5f6;text-decoration:none;margin:0 8px}}
  </style>
</head>
<body>
<header>
  <nav>
    <a href="../{lang}/index.html">🥋 BJJ Wiki</a>
    <a href="../{lang}/skill-tree.html">🌳 Skill Tree</a>
    <a href="../{lang}/sparring-simulator.html">🎮 Simulator</a>
  </nav>
</header>
<main>
  <div class="breadcrumb"><a href="../{lang}/index.html">BJJ Wiki</a> › {h1}</div>
  <h1>{h1}</h1>
  <p style="color:#b0bec5;margin-bottom:24px">{intro}</p>

  <article>
  {content_sections}
  {fanatics_block}
  {beehiiv_block}
  </article>

  <div class="related-links" style="margin-top:32px">
    <h2>Related Guides</h2>
    <a href="bjj-belt-system.html" style="color:#64b5f6">BJJ Belt System</a>
    <a href="bjj-terminology.html" style="color:#64b5f6">BJJ Terminology</a>
    <a href="bjj-rules-for-beginners.html" style="color:#64b5f6">BJJ Rules</a>
    <a href="bjj-training-tips.html" style="color:#64b5f6">Training Tips</a>
    <a href="best-bjj-gi-guide.html" style="color:#64b5f6">Best BJJ Gi Guide</a>
    <a href="bjj-vs-wrestling.html" style="color:#64b5f6">BJJ vs Wrestling</a>
  </div>
</main>
<footer>
  <a href="../en/{slug}.html">EN</a> | <a href="../ja/{slug}.html">JA</a> | <a href="../pt/{slug}.html">PT</a><br><br>
  <a href="../en/privacy.html">Privacy Policy</a> | <a href="../en/about.html">About</a>
  <p style="margin-top:10px">© 2026 BJJ Wiki. All rights reserved.</p>
</footer>
</body>
</html>'''

# Generate all pages
total = 0
for slug, langs in PAGES.items():
    for lang in ['en', 'ja', 'pt']:
        data = langs.get(lang, langs['en'])  # fall back to en data for structure
        # For ja/pt, use their title/desc/h1 but en content
        if lang != 'en':
            data_merged = dict(langs['en'])
            data_merged.update(langs[lang])
        else:
            data_merged = langs['en']

        html = make_page(slug, lang, data_merged, langs)
        out_path = f'{lang}/{slug}.html'
        with open(out_path, 'w') as f:
            f.write(html)
        total += 1

print(f"Generated {total} pillar pages")
