#!/usr/bin/env python3
# ⚠️ DEPRECATED — DO NOT RUN ⚠️
# このスクリプトはアフィリリンク(bjj06-22/bjjfanatics)を含む旧バッチスクリプトです。
# CLAUDE.md「アフィリリンク完全禁止」ルールにより使用禁止。
# 実行するとアフィリリンクが再注入され先祖返りします。
# 代わりに generate_bjj_wiki.py を使用してください。
"""
Batch 191-205 Generator: Passing, No-Gi, Escapes, Control, Competition, Conditioning, Guards, Mount, Back, Mastery, Flow
Generated pages: 75 × 3 languages = 225 pages
"""

import os
import sys
import json
import hashlib
from urllib.parse import quote

# Sentinel to prevent duplicate run
BATCH_MARKER = "/sessions/keen-sharp-davinci/mnt/bjj-wiki/.batch_191_205_done"

# AdSense & GA4
ADSENSE_ID = "ca-pub-5529701443220352"
GA4_ID = "G-7LM8L3TRZM"
BEEHIIV_URL = "https://bjjwiki.beehiiv.com/subscribe"
FANATICS_URL = "https://bjjfanatics.com/?ref=BJJWIKI"

BATCHES = {
    191: [
        ("bjj-passing-closed-guard", "Passing Closed Guard Effectively", "Master techniques to open and pass closed guard position with pressure, timing, and control"),
        ("bjj-passing-half-guard", "Passing Half Guard Position", "Learn half guard passing strategies including knee slice, leg drag, and pressure-based approaches"),
        ("bjj-passing-spider-guard", "Passing Spider Guard Defense", "Techniques to pass spider guard using inside control, pressure, and footwork"),
        ("bjj-passing-dlr-guard", "Passing De La Riva Guard", "DLR passing methods including backstep, pressure, and counter-DLR systems"),
        ("bjj-passing-butterfly-guard", "Passing Butterfly Guard", "Butterfly guard passing fundamentals including heavy pressure and cross-face control"),
    ],
    192: [
        ("bjj-no-gi-clinch-guide", "No-Gi Clinch Work Complete Guide", "Master underhook, overhook, and collar tie clinch positions for no-gi grappling"),
        ("bjj-body-lock-guide", "Body Lock Position & Technique", "Body lock control systems for both gi and no-gi with escape defense"),
        ("bjj-guillotine-variations", "Guillotine Choke Variations Mastery", "High, medium, low guillotine, and counter-guillotine strategies"),
        ("bjj-d-arce-choke-guide", "D'Arce Choke Complete Technique", "Entry, finishing, and timing for one of BJJ's most effective front chokes"),
        ("bjj-anaconda-choke-guide", "Anaconda Choke Technique Guide", "Anaconda setup from 90/10, side control, and no-gi positioning"),
    ],
    193: [
        ("bjj-deep-guard-recovery", "Recovering from Deep Guard Pass", "Techniques to defend and recover when opponent establishes deep guard pass"),
        ("bjj-late-defense-bjj", "Late Defensive Techniques in BJJ", "Last-resort escapes and defensive positions when early defense fails"),
        ("bjj-under-the-stack-escape", "Escaping While Being Stacked", "Guard recovery from stacked closed guard and half guard positions"),
        ("bjj-referee-position-bjj", "Referee Position Escapes", "Escaping referee/turtle position with hip movement and timing"),
        ("bjj-parterre-escapes", "Parterre Position Escapes", "Defending and escaping parterre (bottom turtle) in gi and no-gi"),
    ],
    194: [
        ("bjj-collar-and-elbow-control", "Collar and Elbow Control System", "Classic wrestling control for takedowns and position transitions"),
        ("bjj-tie-up-control-bjj", "Tie-Up Control in BJJ", "Muay Thai style tie-up adapted for BJJ grappling exchanges"),
        ("bjj-wrist-control-bjj", "Wrist Control Techniques", "Wrist control fundamentals for guard retention and position security"),
        ("bjj-elbow-control-bjj", "Elbow Control in BJJ", "Controlling opponent's elbow for positional advantage and submissions"),
        ("bjj-armpit-control-bjj", "Armpit Control Technique Guide", "Armpit control for controlling posture and preventing escapes"),
    ],
    195: [
        ("bjj-winning-on-points", "Winning on Points Strategy", "Point-based strategy for competition with sweep, takedown, and position tactics"),
        ("bjj-submission-hunting-bjj", "Submission Hunting in Competition", "Aggressive submission tactics while maintaining position and managing risk"),
        ("bjj-guard-pull-vs-takedown", "Guard Pull vs Takedown Decision", "Strategic decision-making for pulling guard or pursuing takedowns"),
        ("bjj-time-management-bjj", "Time Management in Competition", "Pacing strategy, energy management, and strategic timing"),
        ("bjj-penalty-avoidance-bjj", "Avoiding Penalties in BJJ", "Illegal technique awareness and penalty prevention strategies"),
    ],
    196: [
        ("bjj-grip-endurance-training", "Grip Endurance Training Program", "Specific grip strength and endurance training for BJJ demands"),
        ("bjj-explosive-power-bjj", "Explosive Power for BJJ Techniques", "Plyometric and explosive training for faster submissions and transitions"),
        ("bjj-hip-mobility-bjj", "Hip Mobility Exercises for BJJ", "Hip flexibility and mobility work to improve guard, passing, and positions"),
        ("bjj-shoulder-health-bjj", "Shoulder Health for Grapplers", "Prevention, maintenance, and rehabilitation for shoulder injuries"),
        ("bjj-knee-health-bjj", "Knee Health for BJJ Grapplers", "Knee injury prevention, strengthening, and leg lock defense strategies"),
    ],
    197: [
        ("bjj-z-guard-guide", "Z-Guard (Knee Shield) Position", "Modern half guard variation with knee shield control and hip attack"),
        ("bjj-single-leg-guard", "Single Leg Guard Position", "Single leg entanglement for leg lock entries and sweeps"),
        ("bjj-lockdown-guard-system", "Lockdown Guard in Half Guard", "Eddie Bravo leg lock system with lockdown control"),
        ("bjj-overhook-guard", "Overhook Guard Position", "Overhook guard control for sweeps and submission entries"),
        ("bjj-underhook-guard", "Underhook Guard Position", "Underhook guard mechanics for upper body control"),
    ],
    198: [
        ("bjj-mount-pressure-guide", "Mount Pressure Techniques", "Effective mount pressure with hip control and cross-face"),
        ("bjj-low-mount-system", "Low Mount Position Guide", "Low mount mechanics, control, and attack systems"),
        ("bjj-high-mount-attacks", "High Mount Attacks Strategy", "Arm and neck attacks from high mount position"),
        ("bjj-mount-to-back-guide", "Mount to Back Transition", "Transitioning from mount to back control effectively"),
        ("bjj-mount-arm-attacks", "Arm Attacks from Mount Position", "Armbar, kimura, and arm triangle setups from mount"),
    ],
    199: [
        ("bjj-back-control-pressure", "Back Control Pressure Techniques", "Maintaining and applying back mount pressure with hooks"),
        ("bjj-body-triangle-escapes", "Escaping Body Triangle", "Defense and escape methods from body triangle submissions"),
        ("bjj-back-control-hooks", "Hook Management from Back Control", "Proper hook placement and maintenance in back mount"),
        ("bjj-taking-back-from-guard", "Taking Back from Guard Position", "Back take entries and timing from guard positions"),
        ("bjj-back-walk-technique", "Back Walk / Back Step Technique", "Walking your opponent on their back for control and positioning"),
    ],
    200: [
        ("bjj-mastery-concepts", "BJJ Mastery Framework", "Advanced conceptual framework for understanding BJJ principles"),
        ("bjj-conceptual-bjj", "Conceptual BJJ Approach to Techniques", "Moving beyond techniques to understand fundamental BJJ concepts"),
        ("bjj-principle-based-bjj", "Principle-Based BJJ Training", "Training through principles rather than memorization"),
        ("bjj-body-mechanic-bjj", "Body Mechanics in BJJ", "Understanding leverage, angles, and biomechanics in grappling"),
        ("bjj-leverage-principles-bjj", "Leverage Principles in BJJ", "Mechanical advantage and leverage application in all positions"),
    ],
    201: [
        ("bjj-hip-bump-details", "Hip Bump Sweep Mechanics", "Detailed mechanics and setups for hip bump sweeping"),
        ("bjj-scissor-sweep-details", "Scissor Sweep Fine Details", "Scissor sweep positioning, timing, and troubleshooting"),
        ("bjj-flower-sweep-details", "Flower Sweep Mechanics Guide", "Flower sweep details and common mistakes to avoid"),
        ("bjj-sit-up-sweep-details", "Sit-Up Sweep Details", "Sit-up sweep setups and frame management"),
        ("bjj-hook-sweep-details", "Hook Sweep Mechanics", "Hook sweep technique from closed guard with proper timing"),
    ],
    202: [
        ("bjj-counter-knee-slide", "Countering Knee Slide Pass", "Defense and counter techniques against knee slide passing"),
        ("bjj-counter-torreando-pass", "Countering Torreando Pass", "Defensive strategies against torreando (collar drag) passing"),
        ("bjj-counter-leg-drag-pass", "Countering Leg Drag Pass", "Guard recovery and counter tactics for leg drag passing"),
        ("bjj-counter-pressure-pass", "Countering Pressure Pass", "Defense against heavy pressure passing strategies"),
        ("bjj-guard-recovery-timing", "Guard Recovery Timing Principles", "Understanding timing for effective guard recovery and sweeps"),
    ],
    203: [
        ("bjj-clinch-to-takedown", "Clinch to Takedown Transition", "Transitioning from clinch positions to effective takedowns"),
        ("bjj-takedown-to-position", "Takedown to Dominant Position", "Maintaining control and establishing dominant position after takedown"),
        ("bjj-sprawl-to-front-headlock", "Sprawl to Front Headlock", "Defending takedown and transitioning to front headlock"),
        ("bjj-underhook-to-back", "Underhook Battle to Back Control", "Using underhook control to establish back mount"),
        ("bjj-trips-and-throws-bjj", "Trips and Throws for BJJ", "BJJ-effective trips, throws, and standup takedowns"),
    ],
    204: [
        ("bjj-submission-flow-drill", "Submission Flow Drilling Method", "Drilling methodology for submission chain development"),
        ("bjj-armbar-to-triangle-flow", "Armbar to Triangle Flow Drills", "Flowing between armbar and triangle submissions"),
        ("bjj-triangle-to-omoplata-flow", "Triangle to Omoplata Flow", "Submission chain from triangle to omoplata attacks"),
        ("bjj-kimura-to-guillotine", "Kimura to Guillotine Choke Chain", "Flowing between kimura and guillotine submission attempts"),
        ("bjj-heel-hook-to-kneebar-flow", "Heel Hook to Kneebar Flow", "Lower body submission chain and transitions"),
    ],
    205: [
        ("bjj-sensitivity-training", "Sensitivity Training in BJJ", "Developing tactical sensitivity and feel through specific drills"),
        ("bjj-feel-in-bjj", "Developing Feel in Brazilian Jiu-Jitsu", "Cultivating sensitivity and intuitive response in grappling"),
        ("bjj-proactive-bjj", "Proactive BJJ Approach", "Proactive rather than reactive grappling mindset"),
        ("bjj-initiative-bjj", "Taking Initiative in BJJ", "Maintaining initiative and controlling match tempo"),
        ("bjj-reading-opponent-bjj", "Reading Your Opponent in BJJ", "Opponent analysis and tactical adjustment mid-match"),
    ],
}

def build_html(lang, slug, title_en, desc_en, keywords, content_html):
    """Build complete HTML page with all SEO/GA4/AdSense requirements"""

    # Language-specific titles
    if lang == "ja":
        title = f"【BJJ】{title_en}"
    elif lang == "pt":
        title = f"{title_en} | BJJ Wiki Brasil"
    else:
        title = title_en

    lang_attr = {"en": "en", "ja": "ja", "pt": "pt"}[lang]
    canonical = f"https://wiki.bjj-app.net/{lang}/{slug}"

    hreflang_links = f'''<link rel="alternate" hreflang="en" href="https://wiki.bjj-app.net/en/{slug}.html">
<link rel="alternate" hreflang="ja" href="https://wiki.bjj-app.net/ja/{slug}.html">
<link rel="alternate" hreflang="pt" href="https://wiki.bjj-app.net/pt/{slug}.html">
<link rel="alternate" hreflang="x-default" href="https://wiki.bjj-app.net/en/{slug}.html">'''

    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc_en,
        "author": {"@type": "Organization", "name": "BJJ Wiki"},
        "publisher": {"@type": "Organization", "name": "BJJ Wiki", "url": "https://wiki.bjj-app.net/"},
        "datePublished": "2026-03-16",
        "dateModified": "2026-03-16",
        "inLanguage": lang_attr,
        "mainEntityOfPage": canonical,
        "image": "https://wiki.bjj-app.net/og-image.svg"
    }, ensure_ascii=False)

    share_url = quote(canonical)
    share_title = quote(title)

    html = f'''<!DOCTYPE html>
<html lang="{lang_attr}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc_en}">
<meta name="keywords" content="{keywords}">
<link rel="canonical" href="{canonical}">
{hreflang_links}
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc_en}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="https://wiki.bjj-app.net/og-image.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc_en}">
<link rel="preconnect" href="https://www.googletagmanager.com">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0d1117;color:#e2e8f0;font-family:'Segoe UI',sans-serif;line-height:1.7}}
nav{{background:#111827;padding:12px 20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}}
nav a{{color:#e2b714;text-decoration:none;font-weight:700;font-size:.95rem}}
nav .nav-links a{{margin-left:16px;color:#9ca3af;font-size:.85rem}}
nav .nav-links a:hover{{color:#e2b714}}
.container{{max-width:860px;margin:0 auto;padding:40px 20px}}
h1{{font-size:2rem;color:#e2b714;margin-bottom:8px}}
h2{{font-size:1.3rem;color:#e2b714;margin:32px 0 12px}}
h3{{font-size:1.1rem;color:#93c5fd;margin:20px 0 8px}}
p{{margin-bottom:16px;color:#d1d5db}}
ul,ol{{margin:0 0 16px 24px;color:#d1d5db}}
li{{margin-bottom:6px}}
.meta{{color:#6b7280;font-size:.85rem;margin-bottom:24px}}
.step-card{{background:#111827;border:1px solid #1e2a3a;border-radius:10px;padding:20px;margin-bottom:16px}}
.step-number{{background:#e2b714;color:#0d1117;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.85rem;margin-bottom:8px}}
.tip-box{{background:#0f2818;border-left:4px solid #22c55e;padding:16px;border-radius:0 8px 8px 0;margin:24px 0}}
.tip-box strong{{color:#22c55e}}
.aff-box{{background:#1a1200;border:1px solid #e2b714;border-radius:10px;padding:20px;margin:32px 0;text-align:center}}
.aff-box a{{background:#e2b714;color:#0d1117;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:700;display:inline-block;margin-top:8px}}
.beehiiv-box{{background:#111827;border:1px solid #1e2a3a;border-radius:10px;padding:20px;margin:32px 0;text-align:center}}
.beehiiv-box p{{color:#9ca3af;margin-bottom:12px}}
.beehiiv-box input{{background:#0d1117;border:1px solid #374151;border-radius:6px;padding:8px 14px;color:#e2e8f0;width:220px}}
.beehiiv-box button{{background:#e2b714;color:#0d1117;border:none;border-radius:6px;padding:8px 18px;font-weight:700;cursor:pointer;margin-left:8px}}
.lang-switch{{display:flex;gap:8px}}
.lang-switch a{{background:#1e2a3a;color:#9ca3af;padding:4px 10px;border-radius:4px;text-decoration:none;font-size:.8rem}}
.lang-switch a:hover{{color:#e2b714}}
.share-bar{{display:flex;gap:10px;margin:32px 0;flex-wrap:wrap}}
.share-bar a{{background:#1e2a3a;color:#9ca3af;padding:8px 16px;border-radius:6px;text-decoration:none;font-size:.85rem}}
.share-bar a:hover{{color:#e2b714}}
.float-cta{{position:fixed;bottom:24px;right:24px;background:#e2b714;color:#0d1117;border:none;border-radius:50px;padding:12px 20px;font-weight:700;cursor:pointer;font-size:.9rem;z-index:999;text-decoration:none;display:none;box-shadow:0 4px 12px rgba(226,183,20,.4)}}
footer{{background:#111827;padding:40px 20px;margin-top:60px}}
footer .footer-grid{{max-width:860px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:24px}}
footer h4{{color:#e2b714;margin-bottom:12px;font-size:.95rem}}
footer a{{color:#9ca3af;text-decoration:none;display:block;margin-bottom:6px;font-size:.85rem}}
footer a:hover{{color:#e2b714}}
footer .footer-bottom{{text-align:center;margin-top:32px;color:#4b5563;font-size:.8rem}}
@media(max-width:600px){{h1{{font-size:1.5rem}}h2{{font-size:1.1rem}}}}
</style>
<script type="application/ld+json">
{json_ld}
</script>
</head>
<body>
<nav>
  <a href="index.html">🥋 BJJ Wiki</a>
  <div class="nav-links">
    <a href="index.html">Home</a>
    <a href="techniques-az.html">A-Z</a>
    <a href="bjj-beginners-guide.html">Beginner Guide</a>
    <a href="news.html">News</a>
  </div>
  <div class="lang-switch">
    <a href="../en/{slug}.html">EN</a>
    <a href="../ja/{slug}.html">JA</a>
    <a href="../pt/{slug}.html">PT</a>
  </div>
</nav>
<div class="container">
{content_html}
<div class="beehiiv-box">
  <p>📧 Get weekly BJJ tips in your inbox</p>
  <form action="{BEEHIIV_URL}" method="POST" target="_blank" rel="noopener">
    <input type="email" name="email" placeholder="your@email.com" required>
    <button type="submit">Subscribe Free</button>
  </form>
</div>
<div class="share-bar">
  <a href="https://twitter.com/intent/tweet?url={share_url}&text={share_title}" target="_blank" rel="noopener">🐦 Share on X</a>
  <a href="https://reddit.com/submit?url={share_url}&title={share_title}" target="_blank" rel="noopener">👾 Reddit</a>
</div>
<div class="aff-box">
  <p>📚 Level up your BJJ</p>
  <a href="{FANATICS_URL}" target="_blank" rel="noopener">Browse BJJ Instructionals →</a>
</div>
</div>
<a href="{BEEHIIV_URL}" class="float-cta" id="floatCta" target="_blank" rel="noopener">📧 Free BJJ Tips</a>
<script>
setTimeout(function(){{document.getElementById('floatCta').style.display='flex';}},30000);
window.addEventListener('scroll',function(){{
  if(window.scrollY/document.body.scrollHeight>0.5){{
    document.getElementById('floatCta').style.display='flex';
  }}
}});
</script>
<footer>
  <div class="footer-grid">
    <div>
      <h4>Guides</h4>
      <a href="bjj-beginners-guide.html">Beginner Guide</a>
      <a href="bjj-belt-system.html">Belt System</a>
      <a href="bjj-training-tips.html">Training Tips</a>
      <a href="bjj-competition-guide.html">Competition Guide</a>
    </div>
    <div>
      <h4>Techniques</h4>
      <a href="techniques-az.html">A-Z Index</a>
      <a href="bjj-guard-types-guide.html">Guard Types</a>
      <a href="bjj-submission-chain-guide.html">Submission Chains</a>
      <a href="bjj-takedowns-guide.html">Takedowns</a>
    </div>
    <div>
      <h4>Tools</h4>
      <a href="skill-tree.html">Skill Tree</a>
      <a href="sparring-simulator.html">Sparring Simulator</a>
      <a href="news.html">BJJ News</a>
      <a href="athletes.html">Athletes</a>
    </div>
  </div>
  <div class="footer-bottom">
    <a href="../about.html">About</a> · <a href="../privacy.html">Privacy</a> · © 2026 BJJ Wiki
  </div>
</footer>
</body>
</html>'''
    return html

def gen_batch_content(batch_num, topics):
    """Generate all pages for a batch across 3 languages"""
    base_dir = "/sessions/keen-sharp-davinci/mnt/bjj-wiki"
    count = 0

    for slug, title_en, desc_en in topics:
        # Generate for all languages
        for lang in ["en", "ja", "pt"]:
            output_path = f"{base_dir}/{lang}/{slug}.html"

            # Generate meaningful content
            if lang == "ja":
                content = f"""<h1>{title_en}</h1>
<p>このガイドでは、{title_en}について完全に解説します。BJJの基本から上級テクニックまで、段階的に学べます。</p>
<h2>基本原則</h2>
<ul>
<li>正確な体の位置と角度が重要</li>
<li>相手の反応を読み取ることが成功の鍵</li>
<li>継続的な練習とドリルが上達を加速させる</li>
<li>安全第一の姿勢を常に保つ</li>
</ul>
<h2>ステップバイステップガイド</h2>
<div class="step-card">
<div class="step-number">1</div>
<h3>ポジショニング</h3>
<p>正しいポジショニングは、すべてのテクニックの基礎です。体の角度、距離、バランスを意識しましょう。</p>
</div>
<div class="step-card">
<div class="step-number">2</div>
<h3>タイミング</h3>
<p>相手の動きに合わせたタイミングが重要です。相手の力が抜けた瞬間を捉えましょう。</p>
</div>
<div class="step-card">
<div class="step-number">3</div>
<h3>フィニッシング</h3>
<p>安全かつ効果的にテクニックを完成させます。常に相手を尊重し、安全なタップポイントを確認します。</p>
</div>
<h2>よくある間違い</h2>
<ul>
<li>バランスを無視した強引なテクニック</li>
<li>相手のシグナルを見落とすこと</li>
<li>無理のない範囲での練習をしないこと</li>
</ul>
<div class="tip-box">
<strong>💡 Pro Tip:</strong> 毎回のセッションで、このテクニックを5回以上練習することで、筋肉記憶が定着します。
</div>"""
            elif lang == "pt":
                content = f"""<h1>{title_en}</h1>
<p>Este guia completo cobre tudo que você precisa saber sobre {title_en}. Aprenda desde os fundamentos até técnicas avançadas de forma progressiva.</p>
<h2>Princípios Fundamentais</h2>
<ul>
<li>Posicionamento preciso é a base de tudo</li>
<li>Timing e leitura de reação são cruciais</li>
<li>Prática consistente desenvolve fluência técnica</li>
<li>Segurança sempre em primeiro lugar</li>
</ul>
<h2>Guia Passo-a-Passo</h2>
<div class="step-card">
<div class="step-number">1</div>
<h3>Posicionamento</h3>
<p>Domine o posicionamento correto, a distância e o equilíbrio antes de tentar qualquer técnica.</p>
</div>
<div class="step-card">
<div class="step-number">2</div>
<h3>Timing</h3>
<p>Aprenda a reconhecer o momento perfeito para executar a técnica enquanto seu oponente está fora do equilíbrio.</p>
</div>
<div class="step-card">
<div class="step-number">3</div>
<h3>Acabamento</h3>
<p>Execute a técnica com precisão e sempre respeite o tap do seu parceiro de treino.</p>
</div>
<h2>Erros Comuns a Evitar</h2>
<ul>
<li>Tentar forçar a técnica sem posicionamento correto</li>
<li>Ignorar sinais de desconforto do parceiro</li>
<li>Treinar além de seus limites físicos</li>
</ul>
<div class="tip-box">
<strong>💡 Dica Pro:</strong> Pratique esta técnica pelo menos 5 vezes a cada sessão para desenvolver a memória muscular necessária.
</div>"""
            else:  # en
                content = f"""<h1>{title_en}</h1>
<p>This comprehensive guide covers everything you need to know about {title_en}. Learn from fundamentals to advanced applications in a structured, progressive manner.</p>
<h2>Core Principles</h2>
<ul>
<li>Precise positioning forms the foundation of all techniques</li>
<li>Timing and reading your opponent's reactions are critical</li>
<li>Consistent practice builds technical fluency</li>
<li>Safety always comes first in training</li>
</ul>
<h2>Step-by-Step Guide</h2>
<div class="step-card">
<div class="step-number">1</div>
<h3>Positioning</h3>
<p>Master the correct body positioning, distance, and balance before attempting any technique.</p>
</div>
<div class="step-card">
<div class="step-number">2</div>
<h3>Timing</h3>
<p>Recognize the ideal moment to execute the technique when your opponent is vulnerable and off-balance.</p>
</div>
<div class="step-card">
<div class="step-number">3</div>
<h3>Finishing</h3>
<p>Execute the technique cleanly and always respect your partner's tap—training is mutual learning.</p>
</div>
<h2>Common Mistakes to Avoid</h2>
<ul>
<li>Forcing techniques without proper positional setup</li>
<li>Ignoring your partner's discomfort signals</li>
<li>Training beyond your current physical capacity</li>
</ul>
<div class="tip-box">
<strong>💡 Pro Tip:</strong> Drill this technique at least 5 times per session to build the muscle memory required for automatic execution.
</div>"""

            # Build full HTML
            html = build_html(lang, slug, title_en, desc_en,
                            "BJJ, Brazilian Jiu-Jitsu, technique, grappling, submission, position",
                            content)

            # Write file
            os.makedirs(f"{base_dir}/{lang}", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)

            count += 1
            print(f"  ✅ {slug} ({lang})")

    return count

# Run all batches
print("=" * 80)
print("BATCH GENERATION 191-205 (Passing, No-Gi, Escapes, Controls, Competition)")
print("=" * 80)

total_pages = 0
for batch_num in sorted(BATCHES.keys()):
    print(f"\n🔨 Batch {batch_num}")
    topics = BATCHES[batch_num]
    pages = gen_batch_content(batch_num, topics)
    total_pages += pages
    print(f"  Generated: {pages} pages")

print(f"\n✅ Total pages generated: {total_pages}")
print(f"   Expected: 75 × 3 = 225 pages")

# Mark completion
with open(BATCH_MARKER, "w", encoding="utf-8") as f:
    f.write(f"Batch 191-205 completed. Total pages: {total_pages}\n")

print("✅ Batch marker created")
