#!/usr/bin/env python3
# ⚠️ DEPRECATED — DO NOT RUN ⚠️
# このスクリプトはアフィリリンク(bjj06-22/bjjfanatics)を含む旧バッチスクリプトです。
# CLAUDE.md「アフィリリンク完全禁止」ルールにより使用禁止。
# 実行するとアフィリリンクが再注入され先祖返りします。
# 代わりに generate_bjj_wiki.py を使用してください。
"""
BJJ Wiki Batches 206-220 Generator
15 batches × 5 pages × 3 languages = 225 pages
Topics: Ashi Garami Deep, Clinch Takedowns, Ground Transitions, Submission Prevention,
         Passing Advanced, Physical Attributes, Safety, Sweep System, Competition Experience,
         Classic Submissions Deep, Guard Concepts Deep, Leg Positioning, Physical Game,
         Mental Performance, Legacy and Growth
"""

import os
import json
from urllib.parse import quote

BASE_DIR = '/sessions/keen-sharp-davinci/mnt/bjj-wiki'

BATCHES = {
    206: {
        'anchor': 'bjj-fireman-carry-guide.html',
        'pages': [
            {'slug': 'bjj-ashi-garami-setup', 'title_en': 'Ashi Garami Setups', 'desc_en': 'Learn how to attack ashi garami position with proper entries and control.'},
            {'slug': 'bjj-ashi-garami-defense', 'title_en': 'Defending Ashi Garami', 'desc_en': 'Defend ashi garami attacks with effective escapes and counter-leg lock strategies.'},
            {'slug': 'bjj-outside-ashi-defense', 'title_en': 'Outside Ashi Defense', 'desc_en': 'Escape outside ashi position and prevent leg lock submissions.'},
            {'slug': 'bjj-entanglement-recovery', 'title_en': 'Leg Entanglement Recovery', 'desc_en': 'Safe recovery methods from complex leg entanglement positions.'},
            {'slug': 'bjj-leg-lock-safety-bjj', 'title_en': 'Leg Lock Safety in Training', 'desc_en': 'Injury prevention and safe leg lock practice techniques.'},
        ]
    },
    207: {
        'anchor': 'bjj-leg-lock-safety-bjj.html',
        'pages': [
            {'slug': 'bjj-collar-tie-takedowns', 'title_en': 'Collar Tie Takedown Chains', 'desc_en': 'Dominate standing position using collar tie control and chaining takedowns.'},
            {'slug': 'bjj-pummel-to-takedown', 'title_en': 'Pummeling to Takedown', 'desc_en': 'Progress from pummeling grip to effective clinch takedowns.'},
            {'slug': 'bjj-inside-trip-guide', 'title_en': 'Inside Trip from Clinch', 'desc_en': 'Master the inside trip takedown from clinch position.'},
            {'slug': 'bjj-outside-trip-guide', 'title_en': 'Outside Trip from Clinch', 'desc_en': 'Execute outside trip takedowns with proper clinch control.'},
            {'slug': 'bjj-ankle-pick-guide', 'title_en': 'Ankle Pick Takedown Guide', 'desc_en': 'Learn ankle pick technique for quick standing takedowns.'},
        ]
    },
    208: {
        'anchor': 'bjj-ankle-pick-guide.html',
        'pages': [
            {'slug': 'bjj-guard-to-top-transition', 'title_en': 'Guard to Top Position Transition', 'desc_en': 'Transition from guard to dominant top control positions smoothly.'},
            {'slug': 'bjj-top-to-back-transition', 'title_en': 'Top to Back Control Transition', 'desc_en': 'Move from top position to back control for better submission opportunities.'},
            {'slug': 'bjj-back-to-mount-transition', 'title_en': 'Back to Mount Control Transition', 'desc_en': 'Transition from back control to mount position when opportunity arises.'},
            {'slug': 'bjj-mount-to-side-control', 'title_en': 'Mount to Side Control Transition', 'desc_en': 'Shift from mount to side control while maintaining dominant pressure.'},
            {'slug': 'bjj-side-to-north-south', 'title_en': 'Side Control to North-South Position', 'desc_en': 'Transition from side control to north-south for submission setup.'},
        ]
    },
    209: {
        'anchor': 'bjj-side-to-north-south.html',
        'pages': [
            {'slug': 'bjj-posture-in-closed-guard', 'title_en': 'Posture to Prevent Submissions', 'desc_en': 'Maintain strong posture in closed guard to prevent arm locks and chokes.'},
            {'slug': 'bjj-submission-prevention', 'title_en': 'Submission Prevention Principles', 'desc_en': 'Core principles for defending submissions across all positions.'},
            {'slug': 'bjj-grip-breaking-defense', 'title_en': 'Breaking Opponent Grips', 'desc_en': 'Techniques to break opponent submission grips effectively.'},
            {'slug': 'bjj-arm-defense-guide', 'title_en': 'Arm Defense Principles', 'desc_en': 'Defend against arm locks with proper positioning and movement.'},
            {'slug': 'bjj-neck-defense-guide', 'title_en': 'Neck and Choke Defense', 'desc_en': 'Comprehensive guide to defending neck attacks and chokes.'},
        ]
    },
    210: {
        'anchor': 'bjj-neck-defense-guide.html',
        'pages': [
            {'slug': 'bjj-folding-pass-guide', 'title_en': 'Folding Pass (Smash Pass)', 'desc_en': 'Master the folding/smash pass for breaking closed guard.'},
            {'slug': 'bjj-toreando-variations', 'title_en': 'Toreando Pass Variations', 'desc_en': 'Advanced variations of the toreando guard pass technique.'},
            {'slug': 'bjj-body-lock-pass-guide', 'title_en': 'Body Lock Guard Pass', 'desc_en': 'Use body lock control to pass guard effectively.'},
            {'slug': 'bjj-back-step-pass', 'title_en': 'Back Step Guard Pass', 'desc_en': 'Execute back step pass with proper hip movement and control.'},
            {'slug': 'bjj-floating-pass-bjj', 'title_en': 'Floating Pass Technique', 'desc_en': 'Advanced floating pass guard passing strategy.'},
        ]
    },
    211: {
        'anchor': 'bjj-floating-pass-bjj.html',
        'pages': [
            {'slug': 'bjj-flexibility-training', 'title_en': 'Flexibility Training for BJJ', 'desc_en': 'Improve flexibility for better guard work and leg lock escapes.'},
            {'slug': 'bjj-balance-in-bjj', 'title_en': 'Balance Development in BJJ', 'desc_en': 'Develop balance skills for standing and ground control.'},
            {'slug': 'bjj-coordination-bjj', 'title_en': 'Coordination Drills for BJJ', 'desc_en': 'Drills to improve hand-foot coordination in grappling.'},
            {'slug': 'bjj-proprioception-bjj', 'title_en': 'Proprioception in Grappling', 'desc_en': 'Develop body awareness for better movement control.'},
            {'slug': 'bjj-timing-in-bjj', 'title_en': 'Timing Development in BJJ', 'desc_en': 'Learn to develop proper timing for techniques and counters.'},
        ]
    },
    212: {
        'anchor': 'bjj-timing-in-bjj.html',
        'pages': [
            {'slug': 'bjj-safe-training-guide', 'title_en': 'Safe BJJ Training Guide', 'desc_en': 'Complete guide to safe and injury-free BJJ training.'},
            {'slug': 'bjj-tap-protocols-bjj', 'title_en': 'Tapping Protocols and Etiquette', 'desc_en': 'Proper tapping etiquette and communication in training.'},
            {'slug': 'bjj-overtraining-signs-bjj', 'title_en': 'Recognizing Overtraining in BJJ', 'desc_en': 'Identify signs of overtraining and plan recovery properly.'},
            {'slug': 'bjj-warm-up-importance', 'title_en': 'Importance of Warm-Up', 'desc_en': 'Why warm-up is crucial for safe and effective training.'},
            {'slug': 'bjj-cool-down-guide-bjj', 'title_en': 'Cool Down After Training', 'desc_en': 'Effective cool-down routines after intense BJJ training.'},
        ]
    },
    213: {
        'anchor': 'bjj-cool-down-guide-bjj.html',
        'pages': [
            {'slug': 'bjj-lumberjack-sweep', 'title_en': 'Lumberjack Sweep', 'desc_en': 'Execute lumberjack sweep to escape difficult bottom positions.'},
            {'slug': 'bjj-tomoe-nage-bjj', 'title_en': 'Tomoe Nage for BJJ', 'desc_en': 'Use tomoe nage sweep to reverse mounted opponent.'},
            {'slug': 'bjj-overhead-sweep-bjj', 'title_en': 'Overhead Sweep Technique', 'desc_en': 'Master overhead sweep from guard with proper foot placement.'},
            {'slug': 'bjj-pendulum-sweep-bjj', 'title_en': 'Pendulum Sweep Details', 'desc_en': 'Advanced pendulum sweep mechanics and timing.'},
            {'slug': 'bjj-balloon-sweep-bjj', 'title_en': 'Balloon Sweep (Sumi Gaeshi)', 'desc_en': 'Execute balloon/sumi gaeshi sweep with explosive power.'},
        ]
    },
    214: {
        'anchor': 'bjj-balloon-sweep-bjj.html',
        'pages': [
            {'slug': 'bjj-first-competition-guide', 'title_en': 'First BJJ Competition Guide', 'desc_en': 'Complete preparation guide for your first BJJ competition.'},
            {'slug': 'bjj-competition-warmup-bjj', 'title_en': 'Competition Warm-Up Routine', 'desc_en': 'Effective warm-up routine before BJJ competition matches.'},
            {'slug': 'bjj-between-matches-bjj', 'title_en': 'Managing Between Matches', 'desc_en': 'Strategies for managing energy between competition matches.'},
            {'slug': 'bjj-losing-in-bjj', 'title_en': 'Losing Gracefully in BJJ', 'desc_en': 'Learn from losses and maintain mental resilience in BJJ.'},
            {'slug': 'bjj-after-competition-bjj', 'title_en': 'Post-Competition Analysis', 'desc_en': 'Analyze your performance and plan improvements after competition.'},
        ]
    },
    215: {
        'anchor': 'bjj-after-competition-bjj.html',
        'pages': [
            {'slug': 'bjj-rear-naked-choke-detail', 'title_en': 'Rear Naked Choke Details', 'desc_en': 'Complete mechanics and variations of the rear naked choke.'},
            {'slug': 'bjj-triangle-choke-details', 'title_en': 'Triangle Choke Fine Details', 'desc_en': 'Master triangle choke details and setup variations.'},
            {'slug': 'bjj-armbar-details-bjj', 'title_en': 'Armbar Finishing Details', 'desc_en': 'Complete armbar mechanics from multiple positions.'},
            {'slug': 'bjj-guillotine-details', 'title_en': 'Guillotine Submission Details', 'desc_en': 'Advanced guillotine choke variations and finishes.'},
            {'slug': 'bjj-kimura-details-bjj', 'title_en': 'Kimura Complete Details', 'desc_en': 'Comprehensive kimura submission mechanics and setup.'},
        ]
    },
    216: {
        'anchor': 'bjj-kimura-details-bjj.html',
        'pages': [
            {'slug': 'bjj-guard-engagement-bjj', 'title_en': 'Guard Engagement Principles', 'desc_en': 'Proper guard engagement techniques for control and submission.'},
            {'slug': 'bjj-breaking-down-guard', 'title_en': 'Breaking Down Opponent Guard', 'desc_en': 'Techniques to break posture and break down guard.'},
            {'slug': 'bjj-guard-vs-pressure', 'title_en': 'Guard vs Pressure Passers', 'desc_en': 'Strategies for guard game against pressure-based passers.'},
            {'slug': 'bjj-guard-vs-speed', 'title_en': 'Guard vs Speed Passers', 'desc_en': 'Guard game strategies against fast and technical passers.'},
            {'slug': 'bjj-guard-recovery-deep', 'title_en': 'Deep Guard Recovery Methods', 'desc_en': 'Advanced methods to recover guard from compromised positions.'},
        ]
    },
    217: {
        'anchor': 'bjj-guard-recovery-deep.html',
        'pages': [
            {'slug': 'bjj-leg-pummeling-bjj', 'title_en': 'Leg Pummeling in Guard', 'desc_en': 'Master leg pummeling to improve guard transitions.'},
            {'slug': 'bjj-lasso-guard-system', 'title_en': 'Lasso Guard System', 'desc_en': 'Complete lasso guard system with sweeps and submissions.'},
            {'slug': 'bjj-shin-to-shin-guard', 'title_en': 'Shin to Shin Guard', 'desc_en': 'Advanced shin to shin guard position and attacks.'},
            {'slug': 'bjj-collar-drag-guard', 'title_en': 'Collar Drag Guard', 'desc_en': 'Execute collar drag from guard for back take or sweeps.'},
            {'slug': 'bjj-arm-drag-guard', 'title_en': 'Arm Drag from Guard', 'desc_en': 'Use arm drag from guard to attack back or take top.'},
        ]
    },
    218: {
        'anchor': 'bjj-arm-drag-guard.html',
        'pages': [
            {'slug': 'bjj-explosive-bjj-game', 'title_en': 'Explosive BJJ Game', 'desc_en': 'Develop explosive power for quick takedowns and sweeps.'},
            {'slug': 'bjj-grinding-bjj-game', 'title_en': 'Grinding and Pressure Game', 'desc_en': 'Master grinding strategy and constant pressure techniques.'},
            {'slug': 'bjj-weight-advantage-bjj', 'title_en': 'Using Weight Advantage in BJJ', 'desc_en': 'Leverage weight effectively in BJJ without athleticism.'},
            {'slug': 'bjj-speed-advantage-bjj', 'title_en': 'Using Speed Advantage in BJJ', 'desc_en': 'Develop fast-paced game strategy for speed advantage.'},
            {'slug': 'bjj-endurance-game-bjj', 'title_en': 'Endurance-Based BJJ Game', 'desc_en': 'Build endurance strategy for longer matches and sparring.'},
        ]
    },
    219: {
        'anchor': 'bjj-endurance-game-bjj.html',
        'pages': [
            {'slug': 'bjj-confidence-bjj', 'title_en': 'Building Confidence in BJJ', 'desc_en': 'Develop self-confidence through consistent training and wins.'},
            {'slug': 'bjj-consistency-bjj', 'title_en': 'Consistency in BJJ Training', 'desc_en': 'Maintain consistency for long-term BJJ progress.'},
            {'slug': 'bjj-motivation-bjj', 'title_en': 'Staying Motivated in BJJ', 'desc_en': 'Strategies to stay motivated through plateaus and challenges.'},
            {'slug': 'bjj-plateaus-bjj', 'title_en': 'Overcoming BJJ Plateaus', 'desc_en': 'Break through skill plateaus with strategic training.'},
            {'slug': 'bjj-flow-state-bjj', 'title_en': 'Achieving Flow State in BJJ', 'desc_en': 'Reach flow state for peak BJJ performance.'},
        ]
    },
    220: {
        'anchor': 'bjj-flow-state-bjj.html',
        'pages': [
            {'slug': 'bjj-teaching-bjj', 'title_en': 'Teaching BJJ to Others', 'desc_en': 'Guide for teaching BJJ to beginners and students.'},
            {'slug': 'bjj-curriculum-bjj', 'title_en': 'BJJ Curriculum Design', 'desc_en': 'Design effective BJJ curriculum for gym or class.'},
            {'slug': 'bjj-belt-promotion-criteria', 'title_en': 'Belt Promotion Criteria', 'desc_en': 'Standards and criteria for BJJ belt promotions.'},
            {'slug': 'bjj-stripes-system-bjj', 'title_en': 'Stripes and Interim Grades', 'desc_en': 'Understanding stripe system and interim belt grades.'},
            {'slug': 'bjj-legacy-in-bjj', 'title_en': 'Legacy and Contribution in BJJ', 'desc_en': 'Build your legacy and contribute to BJJ community.'},
        ]
    },
}

def build_page(lang, slug, title, desc, keywords, content_html):
    """Build complete HTML page with all metadata and structure."""
    assert len(desc) <= 160, f"desc too long ({len(desc)}): {desc}"

    lang_attr = {'en': 'en', 'ja': 'ja', 'pt': 'pt'}[lang]
    canonical = f'https://wiki.bjj-app.net/{lang}/{slug}'
    hreflang_en = f'https://wiki.bjj-app.net/en/{slug}'
    hreflang_ja = f'https://wiki.bjj-app.net/ja/{slug}'
    hreflang_pt = f'https://wiki.bjj-app.net/pt/{slug}'

    return f"""<!DOCTYPE html>
<html lang="{lang_attr}">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{keywords}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{hreflang_en}">
<link rel="alternate" hreflang="ja" href="{hreflang_ja}">
<link rel="alternate" hreflang="pt" href="{hreflang_pt}">
<link rel="alternate" hreflang="x-default" href="{hreflang_en}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="https://wiki.bjj-app.net/og-image.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="preconnect" href="https://www.googletagmanager.com">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-7LM8L3TRZM"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-7LM8L3TRZM');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5529701443220352" crossorigin="anonymous"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}body{{background:#0d1117;color:#e2e8f0;font-family:'Segoe UI',sans-serif;line-height:1.7}}
nav{{background:#111827;padding:12px 20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}}
nav a{{color:#e2b714;text-decoration:none;font-weight:700;font-size:.95rem}}
nav .nav-links a{{margin-left:16px;color:#9ca3af;font-size:.85rem}}nav .nav-links a:hover{{color:#e2b714}}
.container{{max-width:860px;margin:0 auto;padding:40px 20px}}
h1{{font-size:2rem;color:#e2b714;margin-bottom:8px}}h2{{font-size:1.3rem;color:#e2b714;margin:32px 0 12px}}
h3{{font-size:1.1rem;color:#93c5fd;margin:20px 0 8px}}p{{margin-bottom:16px;color:#d1d5db}}
ul,ol{{margin:0 0 16px 24px;color:#d1d5db}}li{{margin-bottom:6px}}
.meta{{color:#6b7280;font-size:.85rem;margin-bottom:24px}}
.difficulty-bar{{background:#1e2a3a;border-radius:8px;padding:12px 16px;margin-bottom:24px;display:flex;align-items:center;gap:12px}}
.belt-badge{{padding:4px 10px;border-radius:12px;font-size:.8rem;font-weight:700}}
.belt-blue{{background:#1d4ed8;color:#fff}}.belt-purple{{background:#7c3aed;color:#fff}}
.step-card{{background:#111827;border:1px solid #1e2a3a;border-radius:10px;padding:20px;margin-bottom:16px}}
.step-number{{background:#e2b714;color:#0d1117;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.85rem;margin-bottom:8px}}
.tip-box{{background:#0f2818;border-left:4px solid #22c55e;padding:16px;border-radius:0 8px 8px 0;margin:24px 0}}.tip-box strong{{color:#22c55e}}
.aff-box{{background:#1a1200;border:1px solid #e2b714;border-radius:10px;padding:20px;margin:32px 0;text-align:center}}
.aff-box a{{background:#e2b714;color:#0d1117;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:700;display:inline-block;margin-top:8px}}
.beehiiv-box{{background:#111827;border:1px solid #1e2a3a;border-radius:10px;padding:20px;margin:32px 0;text-align:center}}
.beehiiv-box p{{color:#9ca3af;margin-bottom:12px}}.beehiiv-box input{{background:#0d1117;border:1px solid #374151;border-radius:6px;padding:8px 14px;color:#e2e8f0;width:220px}}
.beehiiv-box button{{background:#e2b714;color:#0d1117;border:none;border-radius:6px;padding:8px 18px;font-weight:700;cursor:pointer;margin-left:8px}}
.lang-switch{{display:flex;gap:8px}}.lang-switch a{{background:#1e2a3a;color:#9ca3af;padding:4px 10px;border-radius:4px;text-decoration:none;font-size:.8rem}}.lang-switch a:hover{{color:#e2b714}}
.share-bar{{display:flex;gap:10px;margin:32px 0}}.share-bar a{{background:#1e2a3a;color:#9ca3af;padding:8px 16px;border-radius:6px;text-decoration:none;font-size:.85rem}}.share-bar a:hover{{color:#e2b714}}
.float-cta{{position:fixed;bottom:24px;right:24px;background:#e2b714;color:#0d1117;border:none;border-radius:50px;padding:12px 20px;font-weight:700;cursor:pointer;font-size:.9rem;z-index:999;text-decoration:none;display:none;box-shadow:0 4px 12px rgba(226,183,20,.4)}}
footer{{background:#111827;padding:40px 20px;margin-top:60px}}
footer .footer-grid{{max-width:860px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:24px}}
footer h4{{color:#e2b714;margin-bottom:12px;font-size:.95rem}}footer a{{color:#9ca3af;text-decoration:none;display:block;margin-bottom:6px;font-size:.85rem}}footer a:hover{{color:#e2b714}}
footer .footer-bottom{{text-align:center;margin-top:32px;color:#4b5563;font-size:.8rem}}
@media(max-width:600px){{h1{{font-size:1.5rem}}}}
</style>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"{title}","description":"{desc}","author":{{"@type":"Organization","name":"BJJ Wiki"}},"publisher":{{"@type":"Organization","name":"BJJ Wiki","url":"https://wiki.bjj-app.net/"}},"datePublished":"2026-03-16","dateModified":"2026-03-16","inLanguage":"{lang_attr}","mainEntityOfPage":"{canonical}"}}
</script>
</head>
<body>
<nav>
  <a href="index.html">🥋 BJJ Wiki</a>
  <div class="nav-links"><a href="index.html">Home</a><a href="techniques-az.html">A-Z</a><a href="bjj-beginners-guide.html">Beginner Guide</a><a href="news.html">News</a></div>
  <div class="lang-switch"><a href="../en/{slug}.html">EN</a><a href="../ja/{slug}.html">JA</a><a href="../pt/{slug}.html">PT</a></div>
</nav>
<div class="container">
{content_html}
<div class="beehiiv-box">
  <p>📧 Get weekly BJJ tips in your inbox</p>
  <form action="https://bjjwiki.beehiiv.com/subscribe" method="POST" target="_blank">
    <input type="email" name="email" placeholder="your@email.com" required>
    <button type="submit">Subscribe Free</button>
  </form>
</div>
<div class="share-bar">
  <a href="https://twitter.com/intent/tweet?url={canonical}&text={quote(title)}" target="_blank" rel="noopener">🐦 Share on X</a>
  <a href="https://reddit.com/submit?url={canonical}&title={quote(title)}" target="_blank" rel="noopener">👾 Reddit</a>
</div>
<div class="aff-box">
  <p>📚 Level up your BJJ</p>
  <a href="https://bjjfanatics.com/?ref=BJJWIKI" target="_blank" rel="noopener">Browse BJJ Instructionals →</a>
</div>
</div>
<a href="https://bjjwiki.beehiiv.com/subscribe" class="float-cta" id="floatCta" target="_blank" rel="noopener">📧 Free BJJ Tips</a>
<script>
setTimeout(function(){{document.getElementById('floatCta').style.display='flex';}},30000);
window.addEventListener('scroll',function(){{if(window.scrollY/document.body.scrollHeight>0.5){{document.getElementById('floatCta').style.display='flex';}}}});
</script>
<footer>
  <div class="footer-grid">
    <div><h4>Guides</h4><a href="bjj-beginners-guide.html">Beginner Guide</a><a href="bjj-belt-system.html">Belt System</a><a href="bjj-training-tips.html">Training Tips</a><a href="bjj-competition-guide.html">Competition Guide</a></div>
    <div><h4>Techniques</h4><a href="techniques-az.html">A-Z Index</a><a href="bjj-guard-types-guide.html">Guard Types</a><a href="bjj-submission-chain-guide.html">Submission Chains</a><a href="bjj-takedowns-guide.html">Takedowns</a></div>
    <div><h4>Tools</h4><a href="skill-tree.html">Skill Tree</a><a href="sparring-simulator.html">Sparring Simulator</a><a href="news.html">BJJ News</a><a href="athletes.html">Athletes</a></div>
  </div>
  <div class="footer-bottom"><a href="../about.html">About</a> · <a href="../privacy.html">Privacy</a> · © 2026 BJJ Wiki</div>
</footer>
</body>
</html>"""

def get_title_ja(title_en):
    """Convert English title to Japanese with 【BJJ】prefix."""
    return f"【BJJ】{title_en}"

def get_title_pt(title_en):
    """Convert English title to Portuguese with suffix."""
    return f"{title_en} | BJJ Wiki Brasil"

def get_desc_pt(desc_en):
    """Translate description to Portuguese (simplified)."""
    translations = {
        'Learn': 'Aprenda',
        'Master': 'Domine',
        'Develop': 'Desenvolva',
        'Build': 'Construa',
        'Guide to': 'Guia para',
        'Defend': 'Defenda',
        'Execute': 'Execute',
        'Improve': 'Melhore',
        'Effective': 'Eficaz',
        'Techniques': 'Técnicas',
        'Training': 'Treinamento',
        'Safety': 'Segurança',
        'Strategy': 'Estratégia',
        'Control': 'Controle',
        'Prevention': 'Prevenção',
    }
    pt_desc = desc_en
    for en, pt in translations.items():
        pt_desc = pt_desc.replace(en, pt)
    return pt_desc[:160]

def generate_content_en(title, slug):
    """Generate English content."""
    return f"""
<h1>{title}</h1>
<div class="meta">Master the fundamentals and advanced strategies of this essential BJJ technique.</div>

<div class="difficulty-bar">
  <span class="belt-badge belt-blue">🥋 Intermediate</span>
  <span style="color:#9ca3af">~5 min read</span>
</div>

<h2>Introduction</h2>
<p>
{title} is a crucial technique in Brazilian Jiu-Jitsu. Whether you're a blue belt working on consistency
or an advanced student refining details, this guide provides comprehensive coverage of the position,
common mistakes, and advanced variations.
</p>

<h2>Key Principles</h2>
<div class="step-card">
  <div class="step-number">1</div>
  <h3>Foundation</h3>
  <p>Start with proper positioning and control. Strong fundamentals are essential for success.</p>
</div>

<div class="step-card">
  <div class="step-number">2</div>
  <h3>Control</h3>
  <p>Maintain dominant control before advancing to the next stage of the technique.</p>
</div>

<div class="step-card">
  <div class="step-number">3</div>
  <h3>Finalization</h3>
  <p>Complete the technique with proper pressure and timing for maximum effectiveness.</p>
</div>

<div class="tip-box">
  <strong>💡 Pro Tip:</strong> Focus on the small details that separate good practitioners from great ones.
  Consistency in fundamentals will dramatically improve your results on the mat.
</div>

<h2>Common Mistakes to Avoid</h2>
<ul>
  <li>Rushing the technique without establishing proper control</li>
  <li>Losing focus on posture and balance</li>
  <li>Failing to recognize defensive counters</li>
  <li>Not adjusting to different body types and styles</li>
  <li>Training with poor partners or ignoring safety protocols</li>
</ul>

<h2>Training Progression</h2>
<p>
Build your skills progressively through focused drilling and live sparring:
</p>
<ul>
  <li><strong>Week 1-2:</strong> Understand the mechanics and ideal positions</li>
  <li><strong>Week 3-4:</strong> Practice combinations and chains</li>
  <li><strong>Week 5-6:</strong> Study defenses and counters</li>
  <li><strong>Week 7-8:</strong> Apply in live rolling</li>
</ul>

<h2>Advanced Variations</h2>
<p>
Once you've mastered the basics, explore advanced variations and combinations that
work at higher levels of competition. These variations allow you to adapt to different
opponents and situations.
</p>

<h2>Related Techniques</h2>
<p>
Explore related positions and techniques to build a complete game:
</p>
<ul>
  <li><a href="bjj-beginners-guide.html">Beginner's Complete Guide</a></li>
  <li><a href="techniques-az.html">Browse All Techniques A-Z</a></li>
  <li><a href="bjj-competition-guide.html">Competition Strategy Guide</a></li>
</ul>

<h2>Conclusion</h2>
<p>
Mastering {title} requires consistent practice and attention to detail. Start with fundamentals,
drill regularly, and gradually add complexity as you progress. With dedication and proper instruction,
you'll develop a powerful tool for your BJJ game.
</p>
"""

def generate_content_ja(title_en):
    """Generate Japanese content."""
    title = get_title_ja(title_en)
    return f"""
<h1>{title}</h1>
<div class="meta">この重要なBJJ技術の基礎と応用戦略をマスターしましょう。</div>

<div class="difficulty-bar">
  <span class="belt-badge belt-blue">🥋 中級</span>
  <span style="color:#9ca3af">5分程度</span>
</div>

<h2>イントロダクション</h2>
<p>
{title_en}はブラジリアン柔術の重要な技術です。青帯で一貫性に取り組んでいる方から
上級者まで、このガイドはポジション、よくある間違い、応用技を包括的にカバーしています。
</p>

<h2>重要な原則</h2>
<div class="step-card">
  <div class="step-number">1</div>
  <h3>基礎</h3>
  <p>適切なポジショニングと制御から始めます。強固な基礎が成功に不可欠です。</p>
</div>

<div class="step-card">
  <div class="step-number">2</div>
  <h3>コントロール</h3>
  <p>次の段階に進む前に、優位なコントロールを維持してください。</p>
</div>

<div class="step-card">
  <div class="step-number">3</div>
  <h3>完成</h3>
  <p>適切なプレッシャーとタイミングで技術を完成させます。</p>
</div>

<div class="tip-box">
  <strong>💡 プロのコツ:</strong> 優れた実践者を区別する小さな詳細に焦点を当てます。
  基礎に一貫性を持つことで、マットでの結果が劇的に改善されます。
</div>

<h2>避けるべき一般的な間違い</h2>
<ul>
  <li>適切なコントロールを確立せずに技術を急ぐ</li>
  <li>体勢とバランスに焦点を失う</li>
  <li>防御的なカウンターを認識できない</li>
  <li>異なる体型やスタイルに調整しない</li>
  <li>安全プロトコルを無視して不適切なパートナーと練習する</li>
</ul>

<h2>トレーニング進捗</h2>
<p>焦点を絞ったドリルとライブスパーリングを通じて段階的にスキルを構築します:</p>
<ul>
  <li><strong>週1-2:</strong> メカニクスと理想的なポジションを理解する</li>
  <li><strong>週3-4:</strong> コンビネーションと連鎖を練習する</li>
  <li><strong>週5-6:</strong> 防御とカウンターを研究する</li>
  <li><strong>週7-8:</strong> ライブローリングに適用する</li>
</ul>

<h2>まとめ</h2>
<p>
{title}をマスターするには、一貫性のある練習と詳細への注意が必要です。基礎から始め、
定期的にドリルを行い、進展に従って段階的に複雑さを増やしてください。
</p>
"""

def generate_content_pt(title_en):
    """Generate Portuguese content."""
    title = get_title_pt(title_en)
    return f"""
<h1>{title}</h1>
<div class="meta">Domine os fundamentos e estratégias avançadas desta técnica essencial de BJJ.</div>

<div class="difficulty-bar">
  <span class="belt-badge belt-blue">🥋 Intermediário</span>
  <span style="color:#9ca3af">~5 min de leitura</span>
</div>

<h2>Introdução</h2>
<p>
{title_en} é uma técnica crucial no Brazilian Jiu-Jitsu. Quer você seja um faixa azul trabalhando na consistência
ou um estudante avançado refinando detalhes, este guia fornece cobertura abrangente da posição,
erros comuns e variações avançadas.
</p>

<h2>Princípios-Chave</h2>
<div class="step-card">
  <div class="step-number">1</div>
  <h3>Fundação</h3>
  <p>Comece com posicionamento e controle adequados. Os fundamentos sólidos são essenciais para o sucesso.</p>
</div>

<div class="step-card">
  <div class="step-number">2</div>
  <h3>Controle</h3>
  <p>Mantenha o controle dominante antes de avançar para o próximo estágio da técnica.</p>
</div>

<div class="step-card">
  <div class="step-number">3</div>
  <h3>Finalização</h3>
  <p>Complete a técnica com pressão e timing adequados para máxima eficácia.</p>
</div>

<div class="tip-box">
  <strong>💡 Dica de Profissional:</strong> Concentre-se nos pequenos detalhes que separam os bons
  praticantes dos ótimos. A consistência nos fundamentos melhorará dramaticamente seus resultados.
</div>

<h2>Erros Comuns a Evitar</h2>
<ul>
  <li>Apressar a técnica sem estabelecer o controle adequado</li>
  <li>Perder o foco na postura e equilíbrio</li>
  <li>Não reconhecer contra-ataques defensivos</li>
  <li>Não se adaptar a diferentes tipos de corpo e estilos</li>
  <li>Treinar com parceiros ruins ou ignorar protocolos de segurança</li>
</ul>

<h2>Progressão do Treinamento</h2>
<p>Construa suas habilidades progressivamente através de treinamento focado e sparring ao vivo:</p>
<ul>
  <li><strong>Semana 1-2:</strong> Compreender a mecânica e posições ideais</li>
  <li><strong>Semana 3-4:</strong> Praticar combinações e cadeias</li>
  <li><strong>Semana 5-6:</strong> Estudar defesas e contra-ataques</li>
  <li><strong>Semana 7-8:</strong> Aplicar em rolling ao vivo</li>
</ul>

<h2>Conclusão</h2>
<p>
Dominar {title_en} requer prática consistente e atenção aos detalhes. Comece com fundamentos,
pratique regularmente e adicione gradualmente complexidade conforme progride.
</p>
"""

def main():
    """Generate all pages for batches 206-220."""
    total_pages = 0

    for batch_num in sorted(BATCHES.keys()):
        batch_data = BATCHES[batch_num]
        pages = batch_data['pages']

        for lang in ['en', 'ja', 'pt']:
            lang_dir = os.path.join(BASE_DIR, lang)
            os.makedirs(lang_dir, exist_ok=True)

            for page_info in pages:
                slug = page_info['slug']
                title_en = page_info['title_en']
                desc_en = page_info['desc_en']

                # Generate language-specific metadata
                if lang == 'en':
                    title = title_en
                    desc = desc_en
                    keywords = f"{title_en}, BJJ technique, Brazilian Jiu-Jitsu, BJJ guide, grappling"
                    content = generate_content_en(title_en, slug)
                elif lang == 'ja':
                    title = get_title_ja(title_en)
                    desc = desc_en[:160]  # Keep same desc
                    keywords = f"【BJJ】, {title_en}, ブラジリアン柔術, グレイプリング"
                    content = generate_content_ja(title_en)
                else:  # pt
                    title = get_title_pt(title_en)
                    desc = get_desc_pt(desc_en)
                    keywords = f"{title_en}, BJJ, Jiu-Jitsu Brasileiro, Grappling"
                    content = generate_content_pt(title_en)

                # Build and write page
                html = build_page(lang, slug, title, desc, keywords, content)
                filepath = os.path.join(lang_dir, f'{slug}.html')

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html)

                total_pages += 1
                print(f"✅ [{lang.upper()}] {slug}.html")

    print(f"\n✅ Generated {total_pages} pages (Batches 206-220)")

if __name__ == '__main__':
    main()
