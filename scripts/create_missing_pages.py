#!/usr/bin/env python3
# ⚠️ DEPRECATED — DO NOT RUN ⚠️
# このスクリプトはアフィリリンク(bjj06-22/bjjfanatics)を含む旧バッチスクリプトです。
# CLAUDE.md「アフィリリンク完全禁止」ルールにより使用禁止。
# 実行するとアフィリリンクが再注入され先祖返りします。
# 代わりに generate_bjj_wiki.py を使用してください。
"""Generate missing technique pages: deep-half-guard, mount-escape"""
import os, datetime

TODAY = datetime.date.today().isoformat()

def page(lang, slug, title, desc, kw, h1, lead, sections, belt, category, related_slugs, related_names, ja_slug=None, pt_slug=None):
    """Build a full HTML page matching the existing BJJ Wiki template."""
    en_slug = slug if lang == 'en' else (ja_slug or slug)
    lang_alts = {
        'en': f'<link rel="alternate" hreflang="en" href="https://wiki.bjj-app.net/en/{slug}.html">\n<link rel="alternate" hreflang="ja" href="https://wiki.bjj-app.net/ja/{slug}.html">\n<link rel="alternate" hreflang="pt" href="https://wiki.bjj-app.net/pt/{slug}.html">',
    }
    belt_class = {'White Belt':'belt-white','Blue Belt':'belt-blue','Purple Belt':'belt-purple','Brown Belt':'belt-brown','Black Belt':'belt-black'}.get(belt,'belt-blue')
    sections_html = ''
    for sec_title, sec_steps in sections:
        steps_html = ''.join(f'<div class="step"><div class="step-num">{i+1}</div><div><strong>{s[0]}</strong> — {s[1]}</div></div>' for i,s in enumerate(sec_steps))
        sections_html += f'<h2>{sec_title}</h2><div class="card">{steps_html}</div>\n'
    related_html = ''.join(f'<a href="{rs}.html">{rn}</a>' for rs,rn in zip(related_slugs, related_names))
    share_url = f'https://wiki.bjj-app.net/{lang}/{slug}.html'
    share_text = {'en': f'Just learned about {title} on BJJ Wiki! {share_url} #BJJ',
                  'ja': f'BJJ Wikiで{title}を学んだ！ {share_url} #BJJ #柔術',
                  'pt': f'Aprendi sobre {title} no BJJ Wiki! {share_url} #BJJ'}[lang]
    nav_home = {'en':'Home','ja':'ホーム','pt':'Início'}[lang]
    nav_index = {'en':'All Techniques','ja':'全技一覧','pt':'Todas as Técnicas'}[lang]
    nav_skill = {'en':'Skill Tree','ja':'スキルツリー','pt':'Árvore'}[lang]
    nav_sim = {'en':'Simulator','ja':'シミュレーター','pt':'Simulador'}[lang]
    related_title = {'en':'Related Techniques','ja':'関連技','pt':'Técnicas Relacionadas'}[lang]
    aff_title = {'en':'Master this position with world-class instruction','ja':'世界チャンピオンからこのポジションを習得','pt':'Domine esta posição com instrução de nível mundial'}[lang]
    aff_sub = {'en':'BJJ Fanatics instructionals — learn from champions who use this daily','ja':'BJJ Fanaticsの教則動画 — この技を使うチャンピオンから学ぶ','pt':'Instrucionais do BJJ Fanatics — aprenda com campeões que usam isso diariamente'}[lang]
    aff_btn = {'en':'Browse Instructionals →','ja':'教則動画を見る →','pt':'Ver Instrucionais →'}[lang]
    share_label = {'en':'Share this technique','ja':'この技をシェア','pt':'Compartilhe esta técnica'}[lang]
    skill_cta = {'en':'📍 Track Your Progress','ja':'📍 進捗を記録する','pt':'📍 Rastreie seu Progresso'}[lang]
    skill_link = {'en':'Open Skill Tree →','ja':'スキルツリーを開く →','pt':'Abrir Árvore de Habilidades →'}[lang]
    footer_privacy = {'en':'Privacy Policy','ja':'プライバシーポリシー','pt':'Política de Privacidade'}[lang]
    footer_news = {'en':'News','ja':'ニュース','pt':'Notícias'}[lang]

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.googletagmanager.com">
<meta charset="UTF-8">
  <link rel="icon" href="https://wiki.bjj-app.net/favicon.svg" type="image/svg+xml">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | BJJ Wiki</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{kw}">
<meta property="og:title" content="{title} | BJJ Wiki">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://wiki.bjj-app.net/og-image.svg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:type" content="article">
    <meta property="og:site_name" content="BJJ Wiki">
<meta property="og:url" content="https://wiki.bjj-app.net/{lang}/{slug}.html">
<link rel="canonical" href="https://wiki.bjj-app.net/{lang}/{slug}.html">
<link rel="alternate" hreflang="x-default" href="https://wiki.bjj-app.net/en/{slug}.html">
<link rel="alternate" hreflang="en" href="https://wiki.bjj-app.net/en/{slug}.html">
<link rel="alternate" hreflang="ja" href="https://wiki.bjj-app.net/ja/{slug}.html">
<link rel="alternate" hreflang="pt" href="https://wiki.bjj-app.net/pt/{slug}.html">
<link rel="alternate" type="application/rss+xml" title="BJJ Wiki RSS" href="../feed.xml">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-7LM8L3TRZM"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-7LM8L3TRZM');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5529701443220352" crossorigin="anonymous"></script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"{title}","description":"{desc}","datePublished":"{TODAY}","dateModified":"{TODAY}","author":{{"@type":"Organization","name":"BJJ Wiki"}},"publisher":{{"@type":"Organization","name":"BJJ Wiki","url":"https://wiki.bjj-app.net/"}}}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"BJJ Wiki","item":"https://wiki.bjj-app.net/"}},{{"@type":"ListItem","position":2,"name":"{category}","item":"https://wiki.bjj-app.net/{lang}/index.html"}},{{"@type":"ListItem","position":3,"name":"{h1}"}}]}}
</script>
<style>
:root{{--bg:#080b12;--surface:#0f1420;--card:#141926;--border:#1f2840;--text:#e8eaf6;--muted:#6b7699;--accent:#7c6af7;--accent2:#a78bfa;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--blue:#3b82f6;}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif;line-height:1.75;padding:0 16px}}
a{{color:var(--accent2);text-decoration:none}}a:hover{{text-decoration:underline}}
.container{{max-width:860px;margin:0 auto;padding-bottom:80px}}
header{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;padding:20px 0;border-bottom:1px solid var(--border);margin-bottom:40px}}
.logo{{font-size:1.3rem;font-weight:800;color:var(--text)}}.logo span{{color:var(--accent)}}
header nav{{display:flex;gap:16px}}
header nav a{{font-size:0.85rem;color:var(--muted);padding:4px 10px;border-radius:6px;border:1px solid transparent}}
header nav a:hover{{color:var(--text);border-color:var(--border);text-decoration:none}}
.badge{{display:inline-block;padding:4px 12px;border-radius:20px;font-size:0.72rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;background:#1f2840;color:var(--accent2);border:1px solid #2d2060}}
.belt{{display:inline-block;padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;margin-left:6px;border:1px solid var(--border)}}
.belt-white{{color:#e8eaf6;border-color:#3a3a4a;background:#1e1e2e}}
.belt-blue{{color:var(--blue);border-color:#1e3a6e;background:#0f1e38}}
.belt-purple{{color:#c084fc;border-color:#4c1d95;background:#1e0f38}}
.belt-brown{{color:#d97706;border-color:#78350f;background:#241500}}
.belt-black{{color:#9ca3af;border-color:#374151;background:#111827}}
h1{{font-size:2.2rem;font-weight:800;line-height:1.25;margin:12px 0 16px;letter-spacing:-0.02em}}
@media(max-width:600px){{h1{{font-size:1.7rem}}}}
h1+p{{font-size:1.05rem;color:#b0b8d4;margin-bottom:32px;line-height:1.8}}
h2{{font-size:1rem;font-weight:700;color:var(--accent2);text-transform:uppercase;letter-spacing:.08em;display:flex;align-items:center;gap:8px;margin:28px 0 12px}}
h2::before{{content:'';width:3px;height:14px;background:linear-gradient(180deg,var(--accent),var(--accent2));border-radius:2px;display:block;flex-shrink:0}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:24px;margin-bottom:8px}}
.card p{{color:#c4cce8;font-size:0.95rem;margin-bottom:0}}.card p+p{{margin-top:12px}}
.card strong{{color:var(--text)}}
.card .step{{display:flex;gap:12px;margin-bottom:14px;align-items:flex-start}}
.card .step:last-child{{margin-bottom:0}}
.step-num{{min-width:26px;height:26px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:700;color:#fff;flex-shrink:0;margin-top:2px}}
.aff-box{{background:linear-gradient(135deg,#141926,#1a1040);border:1px solid #2d2060;border-radius:14px;padding:24px;margin:32px 0;text-align:center}}
.aff-box p{{color:var(--muted);font-size:0.9rem;margin-bottom:14px}}
.aff-btn{{display:inline-block;padding:10px 24px;border-radius:10px;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;font-weight:700;font-size:0.9rem;transition:opacity .2s}}
.aff-btn:hover{{opacity:.88;text-decoration:none}}
.related-links{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}}
.related-links a{{display:flex;align-items:center;justify-content:space-between;padding:11px 16px;background:var(--card);border:1px solid var(--border);border-radius:10px;font-size:0.88rem;color:var(--text);transition:border-color .2s}}
.related-links a::after{{content:'→';color:var(--muted);font-size:0.8rem}}
.related-links a:hover{{border-color:var(--accent);text-decoration:none}}
.share-bar{{margin:32px 0;padding:20px;background:var(--card);border:1px solid var(--border);border-radius:12px;text-align:center}}
.share-bar p{{color:var(--muted);font-size:0.85rem;margin-bottom:12px}}
.share-btns{{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}}
.share-btn{{display:inline-flex;align-items:center;gap:6px;padding:8px 18px;border-radius:8px;font-size:0.85rem;font-weight:700;text-decoration:none;transition:opacity .2s}}
.share-btn:hover{{opacity:.8;text-decoration:none}}
.share-btn.x{{background:#000;color:#fff}}.share-btn.reddit{{background:#ff4500;color:#fff}}
.share-btn.copy{{background:#2d3748;color:#fff;cursor:pointer;border:none;font-family:inherit}}
.skill-cta{{background:linear-gradient(135deg,#1a0a2e,#0d0820);border:1px solid var(--accent);border-radius:12px;padding:16px 20px;margin:24px 0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}}
.skill-cta div p{{color:var(--muted);font-size:.82rem;margin-top:4px}}
.skill-cta a{{background:var(--accent);color:#fff;padding:8px 20px;border-radius:8px;font-weight:700;font-size:.85rem;white-space:nowrap;text-decoration:none}}
.skill-cta a:hover{{opacity:.85;text-decoration:none}}
footer{{padding:28px 0;border-top:1px solid var(--border);text-align:center;color:var(--muted);font-size:0.8rem;margin-top:48px}}
</style>
</head>
<body>
<div class="container">
<header>
  <div class="logo">🥋 <span>BJJ</span> Wiki</div>
  <nav>
    <a href="index.html">{nav_home}</a>
    <a href="index.html">{nav_index}</a>
    <a href="skill-tree.html">{nav_skill}</a>
    <a href="sparring-simulator.html">{nav_sim}</a>
  </nav>
</header>

<span class="badge">{category}</span>
<span class="belt {belt_class}">{belt}</span>
<h1>{h1}</h1>
<p>{lead}</p>

{sections_html}

<div class="skill-cta">
  <div>
    <strong>{skill_cta}</strong>
    <p>{h1}</p>
  </div>
  <a href="skill-tree.html">{skill_link}</a>
</div>

<div class="aff-box">
  <h3 style="font-size:1.05rem;font-weight:800;margin-bottom:10px">{aff_title}</h3>
  <p>{aff_sub}</p>
  <a href="https://bjjfanatics.com/?aff=bjjwiki" target="_blank" rel="noopener" class="aff-btn">{aff_btn}</a>
</div>

<div class="share-bar">
  <p>{share_label}</p>
  <div class="share-btns">
    <a href="https://twitter.com/intent/tweet?text={share_text}" target="_blank" class="share-btn x">𝕏 Share</a>
    <a href="https://reddit.com/submit?url={share_url}&title={title}" target="_blank" class="share-btn reddit">Reddit</a>
  </div>
</div>

<h2>{related_title}</h2>
<div class="related-links">
{related_html}
</div>

<footer>
  <p>🥋 BJJ Wiki &nbsp;·&nbsp; <a href="../privacy.html" style="color:inherit">{footer_privacy}</a> &nbsp;·&nbsp; <a href="../about.html" style="color:inherit">About</a> &nbsp;·&nbsp; <a href="skill-tree.html" style="color:var(--accent2)">{nav_skill}</a> &nbsp;·&nbsp; <a href="sparring-simulator.html" style="color:var(--accent2)">{nav_sim}</a></p>
</footer>
</div>
</body>
</html>"""

# ── Deep Half Guard ────────────────────────────────────────────
deep_half_en = dict(
    lang='en', slug='deep-half-guard',
    title='Deep Half Guard BJJ: Sweeps, Back Takes & Full System Guide',
    desc='Master the Deep Half Guard in BJJ. Complete guide to entries, sweeps (Jeff Glover roll, Old School), back takes, and defenses. Works at every belt level.',
    kw='deep half guard BJJ, deep half sweeps, Jeff Glover roll, deep half back take, BJJ half guard system',
    h1='Deep Half Guard', lead='Deep Half Guard is one of the most powerful guard systems in BJJ — a position that lets a smaller, lighter practitioner completely neutralize a heavier passer and produce high-percentage sweeps and back takes. Popularized by Jeff Glover and Ryan Hall, it rewards patience and leverage over explosiveness.',
    sections=[
        ('What Is Deep Half Guard', [
            ('Definition','You are under your opponent in half guard, but your head has passed under their hip, placing you in a deep underhook position close to their far leg.'),
            ('Why it works','From deep half, your opponent\'s base is severely compromised — they cannot post their far hand without giving you the sweep, and they cannot sprawl without exposing their back.'),
            ('Who uses it','Jeff Glover, Bernardo Faria, Marcelo Garcia. Bernardo Faria is arguably the world\'s best deep half practitioner with multiple ADCC and world championships won from this position.'),
        ]),
        ('How to Enter Deep Half Guard', [
            ('From half guard','From regular half guard, dip your head under their hip, swim your top arm deep along their far leg and grip behind their knee. Your bottom arm controls their ankle.'),
            ('From guard pull','Pull guard and immediately underhook the leg on one side, using your momentum to slide under into deep half.'),
            ('Against the torreando pass','As they grip your hips to torreando, shrimp toward the gripped side, sneak your head under and enter deep half.'),
        ]),
        ('Key Sweeps', [
            ('The Jeff Glover Roll','Roll toward their back — lift their far knee, roll under and through, come up in top position. Fast and unexpected. Works when they are flat-footed.'),
            ('Old School / Waiter Sweep','Block their near leg, drive forward and under, steer their far leg skyward — they roll over your back. Classic high-percentage sweep.'),
            ('Back Take','When they post forward to stop the sweep, shift your hips to their back side, get your hooks in. Back control = 4 points.'),
        ]),
        ('Common Mistakes', [
            ('Head position wrong','If your head stays outside their hip rather than underneath, you lose all the leverage that makes deep half work.'),
            ('Grip too loose','Deep half requires a firm two-on-one grip on their far leg. Loose grips allow them to pull free and re-establish base.'),
            ('Staying too long','Deep half is a transitional position, not a resting spot. Move to the sweep or back take — don\'t stall in it.'),
        ]),
    ],
    belt='Blue Belt', category='Guard',
    related_slugs=['half-guard','butterfly-guard','berimbolo','back-mount','closed-guard'],
    related_names=['Half Guard','Butterfly Guard','Berimbolo','Back Mount','Closed Guard'],
)

deep_half_ja = dict(
    lang='ja', slug='deep-half-guard',
    title='ディープハーフガード BJJ：スイープ・バックテイク完全ガイド',
    desc='BJJのディープハーフガードを完全攻略。エントリー、スイープ（ジェフグローバーロール、オールドスクール）、バックテイク、ディフェンスまで網羅。',
    kw='ディープハーフガード BJJ, ディープハーフ スイープ, バックテイク, 柔術 ハーフガード',
    h1='ディープハーフガード',
    lead='ディープハーフガードは、BJJで最もパワフルなガードシステムの一つです。体格差を無力化し、高確率のスイープとバックテイクを生み出せます。Jeff GloverとRyan Hallが広め、爆発力よりも忍耐とレバレッジを活かすポジションです。',
    sections=[
        ('ディープハーフガードとは', [
            ('定義','ハーフガードの下から、頭を相手のヒップの下に潜り込ませ、遠い足の近くでディープアンダーフックを取ったポジション。'),
            ('なぜ効くか','ディープハーフから相手のベースは大きく崩れる — 遠い手をポストすれば即スイープ、スプロールすれば背中を渡すことになる。'),
            ('使う選手','Jeff Glover, Bernardo Faria, Marcelo Garcia。Bernardo Fariaはこのポジションで複数のADCCと世界選手権を制覇した。'),
        ]),
        ('エントリー方法', [
            ('ハーフガードから','ハーフガードの状態から頭を相手のヒップの下に潜らせ、トップアームを遠い足に深く差し込み膝裏を掴む。'),
            ('ガードプルから','ガードを引き片側の足にアンダーフックを入れ、勢いを使って潜り込む。'),
            ('トレアナパス対策','ヒップをグリップされたらその方向にシュリンプ、頭を潜らせてディープハーフに入る。'),
        ]),
        ('主要スイープ', [
            ('ジェフグローバーロール','相手の遠い膝を持ち上げ、下から丸まりながらロール — トップポジションで起き上がる。相手がフラットフットの時に高確率。'),
            ('オールドスクール / ウェイタースイープ','近い足をブロックし、前進しながら遠い足を空に向けて押し上げる — 背中越しに転がる。定番の高確率スイープ。'),
            ('バックテイク','スイープを止めようと前傾みになった瞬間、背中側にヒップをシフトしてフックを入れる。バックコントロール = 4ポイント。'),
        ]),
        ('よくあるミス', [
            ('頭の位置','ヒップの下ではなく外側に頭があると、ディープハーフの全レバレッジが失われる。'),
            ('グリップが緩い','遠い足への2オン1グリップが緩いと相手に引き抜かれる。'),
            ('長居しすぎ','ディープハーフは過渡的ポジション — スイープかバックテイクへ即移行する。'),
        ]),
    ],
    belt='Blue Belt', category='ガード',
    related_slugs=['half-guard','butterfly-guard','berimbolo','back-mount','closed-guard'],
    related_names=['ハーフガード','バタフライガード','ベリンボロ','バックマウント','クローズドガード'],
)

deep_half_pt = dict(
    lang='pt', slug='deep-half-guard',
    title='Deep Half Guard BJJ: Raspagens, Back Takes e Guia Completo',
    desc='Domine o Deep Half Guard no BJJ. Guia completo de entradas, raspagens (Jeff Glover roll, Old School), back takes e defesas. Funciona em todas as faixas.',
    kw='deep half guard BJJ, raspagens deep half, Jeff Glover roll, back take BJJ, sistema de guarda',
    h1='Deep Half Guard',
    lead='O Deep Half Guard é um dos sistemas de guarda mais poderosos do BJJ — uma posição que permite neutralizar um passador mais pesado e produzir raspagens e back takes de alta porcentagem. Popularizado por Jeff Glover e Ryan Hall, recompensa paciência e alavancagem.',
    sections=[
        ('O Que é o Deep Half Guard', [
            ('Definição','Você está embaixo do adversário no half guard, mas sua cabeça passou sob o quadril dele, colocando-o em posição de underhook profundo perto da perna distante.'),
            ('Por que funciona','Do deep half, a base do adversário fica severamente comprometida — ele não pode postar a mão distante sem dar a raspagem, nem sprawlar sem expor as costas.'),
            ('Quem usa','Jeff Glover, Bernardo Faria, Marcelo Garcia. Bernardo Faria venceu múltiplos ADCCs e mundiais a partir dessa posição.'),
        ]),
        ('Como Entrar no Deep Half Guard', [
            ('Do half guard','Do half guard regular, mergulhe a cabeça sob o quadril, passe o braço de cima profundo na perna distante e segure atrás do joelho.'),
            ('Da puxada de guarda','Puxe guarda e imediatamente underhooke a perna de um lado, usando o momentum para deslizar para o deep half.'),
            ('Contra o toreando','Quando agarrarem seus quadris para o toreando, faça shrimp para o lado agarrado e entre no deep half.'),
        ]),
        ('Principais Raspagens', [
            ('Jeff Glover Roll','Role para as costas deles — levante o joelho distante, role por baixo e saia em posição por cima. Rápido e inesperado.'),
            ('Old School / Waiter Sweep','Bloqueie a perna próxima, avance por baixo e erga a perna distante para o céu — eles rolam por cima de suas costas.'),
            ('Back Take','Quando postarem para frente para parar a raspagem, mude seus quadris para o lado das costas deles e entre os ganchos.'),
        ]),
        ('Erros Comuns', [
            ('Posição da cabeça errada','Se a cabeça ficar do lado de fora do quadril em vez de por baixo, você perde toda a alavancagem.'),
            ('Grip muito frouxo','O deep half requer um grip firme na perna distante. Grips frouxos permitem que eles se soltem.'),
            ('Ficar tempo demais','O deep half é uma posição transitória — mova-se para a raspagem ou back take.'),
        ]),
    ],
    belt='Blue Belt', category='Guarda',
    related_slugs=['half-guard','butterfly-guard','berimbolo','back-mount','closed-guard'],
    related_names=['Half Guard','Butterfly Guard','Berimbolo','Back Mount','Closed Guard'],
)

# ── Mount Escape ───────────────────────────────────────────────
mount_escape_en = dict(
    lang='en', slug='mount-escape',
    title='BJJ Mount Escape: Upa, Elbow-Knee & Trap-and-Roll Techniques',
    desc='Master BJJ mount escapes. Step-by-step upa bridge-and-roll, elbow-knee shrimp, and trap-and-roll. Escape full mount, high mount, and technical mount reliably.',
    kw='BJJ mount escape, upa escape, elbow knee escape, bridge and roll, trap and roll, full mount escape',
    h1='Mount Escape',
    lead='Being mounted is one of the worst positions in BJJ — you are giving up 4 points and are vulnerable to every submission in the book. But with correct technique, mount is escapable even against much larger opponents. There are two primary escapes every grappler must own: the Upa (bridge and roll) and the Elbow-Knee (shrimp) escape.',
    sections=[
        ('Why Mount Is Dangerous', [
            ('Score','In competition, full mount scores 4 points — the highest of any positional score.'),
            ('Submission threat','From mount, the opponent can attack armbar, americana, kimura, rear naked choke (after back take), ezekiel choke, and collar chokes.'),
            ('Priority','Escaping mount is a higher priority than hunting submissions from mount. Survive first, score second.'),
        ]),
        ('Escape 1: Upa (Bridge and Roll)', [
            ('Setup','Wait for your opponent to reach for a submission or post their hands. Trap one of their arms against your body with both hands.'),
            ('Bridge','Plant both feet close to your body. Simultaneously bridge your hips hard and turn — the torque lifts them off.'),
            ('Roll to guard','Use the momentum to roll them over and land in their guard. From here you can work guard passes.'),
            ('Best against','High mount (they are sitting up). Works well when they reach for collar grips.'),
        ]),
        ('Escape 2: Elbow-Knee (Shrimp)', [
            ('Frame first','Create a frame — forearm on their hip/chest, other hand blocking their collar grip. Never cross your arms.'),
            ('Shrimp out','Drive one elbow and the same-side knee together while shrimping your hips away from them. Repeat 2-3 times.'),
            ('Recover half guard','Get your shin in across their hips to capture half guard. From half guard, work your guard recovery.'),
            ('Best against','Low mount (they sit low on your hips). Also effective against high-level opponents who resist the upa.'),
        ]),
        ('Common Mistakes', [
            ('Crossing your arms','Crossing arms under mount is the fastest route to an armbar. Keep elbows tight to your sides.'),
            ('Hipping too small','A timid bridge does nothing. The upa requires an explosive, full-body bridge with your feet close and hips driving high.'),
            ('Stalling flat','Lying flat under mount is passive and gives your opponent time to improve position. Always be framing and shrimping.'),
            ('Wrong timing on upa','Bridging when your opponent is perfectly balanced just creates a rocking motion. Wait for them to post or reach.'),
        ]),
    ],
    belt='White Belt', category='Defense',
    related_slugs=['closed-guard','half-guard','side-control','back-mount','armbar'],
    related_names=['Closed Guard','Half Guard','Side Control','Back Mount','Armbar'],
)

mount_escape_ja = dict(
    lang='ja', slug='mount-escape',
    title='BJJマウントエスケープ：ウパ・エルボーニー完全ガイド',
    desc='BJJのマウント脱出を完全マスター。ウパ（ブリッジ＆ロール）、エルボーニー（シュリンプ）のステップバイステップ解説。フルマウント・ハイマウントを確実に脱出。',
    kw='マウントエスケープ BJJ, ウパ脱出, エルボーニー脱出, ブリッジアンドロール, マウント返し, 柔術',
    h1='マウントエスケープ',
    lead='マウントはBJJで最悪のポジションの一つです — 4ポイントを献上し、あらゆるサブミッションにさらされます。しかし正しいテクニックを使えば、体格差があっても脱出可能です。全グラップラーが習得すべき主要な脱出が2つあります：ウパ（ブリッジ＆ロール）とエルボーニー（シュリンプ）エスケープです。',
    sections=[
        ('なぜマウントは危険か', [
            ('得点','試合では、フルマウントは4ポイント — ポジショナルスコアで最高値。'),
            ('サブミッションの脅威','マウントからアームバー、アメリカーナ、キムラ、リアネイキッドチョーク（バックテイク後）、エゼキエルチョーク、エリチョークが狙える。'),
            ('優先順位','マウントからの脱出は攻撃よりも優先度が高い。まず生き残り、その後ポイントを取る。'),
        ]),
        ('脱出1：ウパ（ブリッジ＆ロール）', [
            ('セットアップ','相手がサブミッションを狙うかポストする瞬間を待つ。片方の腕を両手で身体に引き付けてトラップする。'),
            ('ブリッジ','両足を身体の近くに立て、ヒップを爆発的に持ち上げながら捻る — このトルクで相手が浮き上がる。'),
            ('ガードへ','勢いを使って転がし、ガードに着地。そこからガードパスを狙う。'),
            ('効く状況','ハイマウント（相手が起き上がっている時）。襟を掴みに来た時に特に有効。'),
        ]),
        ('脱出2：エルボーニー（シュリンプ）', [
            ('フレームを作る','腕でフレームを作る — 前腕を相手のヒップ/胸に当て、もう一方の手で襟グリップをブロック。腕を交差させない。'),
            ('シュリンプ','片方の肘と同側の膝を寄せながらヒップをシュリンプする。2〜3回繰り返す。'),
            ('ハーフガード回復','スネを相手のヒップに差し込んでハーフガードをキャプチャー。そこからガード回復へ。'),
            ('効く状況','ローマウント（相手がヒップ低く座っている時）。ウパへの抵抗が強い相手にも有効。'),
        ]),
        ('よくあるミス', [
            ('腕の交差','マウント下での腕の交差はアームバーへの最速ルート。肘は脇に密着させる。'),
            ('ブリッジが小さい','半端なブリッジは無効。ウパには足を近くに立てた爆発的な全身ブリッジが必要。'),
            ('フラットで停滞','マウント下で寝ているだけでは相手にポジション改善の時間を与えるだけ。常にフレームとシュリンプを。'),
            ('タイミングのミス','相手が完全にバランスを取っている時にブリッジしても揺れるだけ。ポストや手を伸ばした瞬間を待つ。'),
        ]),
    ],
    belt='White Belt', category='ディフェンス',
    related_slugs=['closed-guard','half-guard','side-control','back-mount','armbar'],
    related_names=['クローズドガード','ハーフガード','サイドコントロール','バックマウント','アームバー'],
)

mount_escape_pt = dict(
    lang='pt', slug='mount-escape',
    title='Escape da Montada no BJJ: Upa, Cotovelo-Joelho e Guia Completo',
    desc='Domine os escapes da montada no BJJ. Upa (ponte e rolamento), cotovelo-joelho (camarão) passo a passo. Escape da montada alta e baixa com técnica confiável.',
    kw='escape montada BJJ, upa escape, escape cotovelo joelho, bridge and roll BJJ, escape full mount',
    h1='Escape da Montada',
    lead='A montada é uma das piores posições no BJJ — você está cedendo 4 pontos e vulnerável a todas as finalizações do livro. Mas com técnica correta, a montada é escapável mesmo contra oponentes maiores. Há dois escapes primários que todo grappler deve dominar: o Upa (ponte e rolamento) e o Cotovelo-Joelho (camarão).',
    sections=[
        ('Por Que a Montada é Perigosa', [
            ('Pontuação','Em competição, a montada pontua 4 pontos — a maior pontuação posicional.'),
            ('Ameaça de finalização','Da montada, o adversário pode atacar arm bar, americana, kimura, rear naked choke, ezekiel e estrangulamentos de gola.'),
            ('Prioridade','Escapar da montada é prioridade maior do que caçar finalizações. Sobreviva primeiro, pontue depois.'),
        ]),
        ('Escape 1: Upa (Ponte e Rolamento)', [
            ('Setup','Espere o adversário alcançar uma finalização ou postar as mãos. Prenda um dos braços dele contra seu corpo com ambas as mãos.'),
            ('Ponte','Plante os pés próximos ao corpo. Simultaneamente faça a ponte com os quadris e gire — o torque os levanta.'),
            ('Rolar para guarda','Use o momentum para rolá-los e aterrissar em sua guarda. Daqui trabalhe as passagens.'),
            ('Melhor contra','Montada alta (quando estão sentados eretos). Funciona bem quando alcançam os grips de gola.'),
        ]),
        ('Escape 2: Cotovelo-Joelho (Camarão)', [
            ('Frame primeiro','Crie um frame — antebraço no quadril/peito deles, outra mão bloqueando o grip de gola. Nunca cruze os braços.'),
            ('Faça camarão','Conduza um cotovelo e o joelho do mesmo lado enquanto faz camarão para longe deles. Repita 2-3 vezes.'),
            ('Recuperar half guard','Coloque sua canela através dos quadris para capturar o half guard. Daqui trabalhe a recuperação de guarda.'),
            ('Melhor contra','Montada baixa. Também eficaz contra oponentes de alto nível que resistem ao upa.'),
        ]),
        ('Erros Comuns', [
            ('Cruzar os braços','Cruzar braços sob a montada é a rota mais rápida para um arm bar. Mantenha os cotovelos colados às laterais.'),
            ('Ponte muito pequena','Uma ponte tímida não faz nada. O upa requer uma ponte explosiva de corpo inteiro.'),
            ('Ficar deitado passivo','Ficar deitado debaixo da montada dá ao adversário tempo para melhorar posição. Sempre frame e camarão.'),
            ('Timing errado no upa','Fazer ponte quando o adversário está perfeitamente equilibrado cria apenas um movimento de balançar. Espere eles postarem.'),
        ]),
    ],
    belt='White Belt', category='Defesa',
    related_slugs=['closed-guard','half-guard','side-control','back-mount','armbar'],
    related_names=['Closed Guard','Half Guard','Side Control','Back Mount','Armbar'],
)

# ── Generate all files ─────────────────────────────────────────
pages = [deep_half_en, deep_half_ja, deep_half_pt,
         mount_escape_en, mount_escape_ja, mount_escape_pt]

for p in pages:
    html = page(**p)
    outpath = f"{p['lang']}/{p['slug']}.html"
    with open(outpath, 'w') as f:
        f.write(html)
    print(f"Created: {outpath}")

print(f"\nDone: {len(pages)} pages generated.")
EOF
