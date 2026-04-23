#!/usr/bin/env python3
"""Generate ja/pt versions of 5 pillar pages"""
import os, datetime
TODAY = datetime.date.today().isoformat()

CSS = """
:root{--bg:#0a0a0f;--card:#111119;--border:#1e1e2e;--text:#e2e2ee;--muted:#7a7a9a;--accent:#6e40c9}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.7;padding:0 16px}
.container{max-width:800px;margin:0 auto;padding:24px 0 64px}
header{padding:20px 0;border-bottom:1px solid var(--border);margin-bottom:32px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
.logo{font-size:1.4rem;font-weight:800;color:var(--text);text-decoration:none}.logo span{color:var(--accent)}
nav a{color:var(--muted);text-decoration:none;margin-right:12px;font-size:.85rem}nav a:hover{color:var(--text)}
h1{font-size:1.9rem;font-weight:800;margin-bottom:14px;line-height:1.2}
h2{font-size:1.1rem;font-weight:700;margin:32px 0 14px;padding-left:12px;border-left:3px solid var(--accent);color:var(--text)}
p{color:#c2c2d9;margin-bottom:14px;font-size:.97rem}
.intro{font-size:1.05rem;line-height:1.75;color:#d2d2e9;margin-bottom:28px;padding:18px 20px;background:var(--card);border:1px solid var(--border);border-radius:10px}
.tech-list{display:flex;flex-direction:column;gap:10px;margin-bottom:32px}
.tech-pill{display:flex;align-items:center;gap:14px;background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 16px;text-decoration:none;color:var(--text);transition:border-color .2s}
.tech-pill:hover{border-color:var(--accent);background:#13131f;text-decoration:none}
.pill-name{font-weight:700;font-size:.95rem;min-width:160px}
.pill-desc{flex:1;font-size:.85rem;color:var(--muted);line-height:1.4}
.pill-arrow{color:var(--accent);font-weight:700;flex-shrink:0}
.faq-item{background:#0d0d1a;border:1px solid var(--border);border-radius:10px;padding:18px;margin-bottom:12px}
.faq-q{font-weight:700;color:var(--accent);margin-bottom:8px;font-size:.95rem}
.faq-a{color:#c2c2d9;font-size:.9rem;margin:0}
.skill-cta{background:#0f1420;border:1px solid #3b2d6e;border-radius:12px;padding:14px 18px;margin:24px 0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px}
.beehiiv-box{background:linear-gradient(135deg,#0d1225,#1a1040);border:1px solid #3b2d6e;border-radius:14px;padding:24px;margin:32px 0;text-align:center}
footer{border-top:1px solid var(--border);padding:24px 0;text-align:center;color:var(--muted);font-size:.8rem;margin-top:40px}
footer a{color:var(--muted)}
"""

def pill(slug, name, desc):
    return f'<a href="{slug}.html" class="tech-pill"><div class="pill-name">{name}</div><div class="pill-desc">{desc}</div><span class="pill-arrow">→</span></a>'

def faq(q, a):
    return f'<div class="faq-item"><div class="faq-q">❓ {q}</div><p class="faq-a">{a}</p></div>'

def page(lang, slug, title, desc, h1, intro, sections_html, faqs_html, en_slug=None):
    es = en_slug or slug
    beehiiv = {
        "ja": '<h3 style="font-weight:800;margin-bottom:8px">🐝 毎週BJJのヒントを受け取る</h3><p style="color:var(--muted);font-size:.88rem;margin-bottom:16px">BJJ Wikiニュースレター — 技の解説・トレーニングのコツ・限定コンテンツ。無料。</p><a href="https://bjj-wiki.beehiiv.com/subscribe" target="_blank" rel="noopener" style="display:inline-block;background:linear-gradient(135deg,#6e40c9,#4f46e5);color:#fff;padding:10px 28px;border-radius:8px;font-weight:700;text-decoration:none">無料で登録する →</a>',
        "pt": '<h3 style="font-weight:800;margin-bottom:8px">🐝 Dicas Semanais de BJJ</h3><p style="color:var(--muted);font-size:.88rem;margin-bottom:16px">Newsletter do BJJ Wiki — análises de técnicas, dicas de treino e conteúdo exclusivo. Gratuito.</p><a href="https://bjj-wiki.beehiiv.com/subscribe" target="_blank" rel="noopener" style="display:inline-block;background:linear-gradient(135deg,#6e40c9,#4f46e5);color:#fff;padding:10px 28px;border-radius:8px;font-weight:700;text-decoration:none">Inscrever Grátis →</a>',
    }[lang]
    skill_cta = {
        "ja": ('<div style="font-size:.85rem;font-weight:700;color:#a78bfa">📍 進捗を記録する</div><div style="font-size:.78rem;color:var(--muted)">BJJスキルツリーで学んだ技をチェックしよう</div>', 'スキルツリーを開く →'),
        "pt": ('<div style="font-size:.85rem;font-weight:700;color:#a78bfa">📍 Rastreie seu Progresso</div><div style="font-size:.78rem;color:var(--muted)">Marque as técnicas aprendidas na Árvore de Habilidades de BJJ</div>', 'Abrir Árvore →'),
    }[lang]
    nav = {
        "ja": ('ホーム', '全技一覧', '🌳 スキルツリー'),
        "pt": ('Início', 'Todas as Técnicas', '🌳 Árvore de Habilidades'),
    }[lang]
    footer_priv = {"ja":"プライバシーポリシー","pt":"Política de Privacidade"}[lang]
    sim_link = {"ja":"シミュレーター","pt":"Simulador"}[lang]

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://wiki.bjj-app.net/{lang}/{slug}.html">
<meta property="og:image" content="https://wiki.bjj-app.net/og-image.svg">
<meta property="og:type" content="article">
<link rel="canonical" href="https://wiki.bjj-app.net/{lang}/{slug}.html">
<link rel="alternate" hreflang="x-default" href="https://wiki.bjj-app.net/en/{es}.html">
<link rel="alternate" hreflang="en" href="https://wiki.bjj-app.net/en/{es}.html">
<link rel="alternate" hreflang="ja" href="https://wiki.bjj-app.net/ja/{slug}.html">
<link rel="alternate" hreflang="pt" href="https://wiki.bjj-app.net/pt/{slug}.html">
<link rel="alternate" type="application/rss+xml" title="BJJ Wiki RSS" href="../feed.xml">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5529701443220352" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-7LM8L3TRZM"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-7LM8L3TRZM');</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"{h1}","description":"{desc}","datePublished":"{TODAY}","dateModified":"{TODAY}","inLanguage":"{lang}","author":{{"@type":"Organization","name":"BJJ Wiki","url":"https://wiki.bjj-app.net/"}},"publisher":{{"@type":"Organization","name":"BJJ Wiki"}}}}
</script>
<style>{CSS}</style>
</head>
<body>
<div class="container">
  <header>
    <a href="index.html" class="logo">BJJ<span>Wiki</span></a>
    <nav>
      <a href="index.html">{nav[0]}</a>
      <a href="index.html">{nav[1]}</a>
      <a href="skill-tree.html">{nav[2]}</a>
    </nav>
  </header>
  <h1>{h1}</h1>
  <div class="intro">{intro}</div>
  {sections_html}
  <div class="skill-cta">
    <div>{skill_cta[0]}</div>
    <a href="skill-tree.html" style="background:#6e40c9;color:#fff;padding:7px 16px;border-radius:8px;font-weight:700;font-size:.82rem;text-decoration:none">{skill_cta[1]}</a>
  </div>
  <h2>❓ FAQ</h2>
  {faqs_html}
  <div class="beehiiv-box">{beehiiv}</div>
  <footer>
    <p>BJJ Wiki</p>
    <p style="margin-top:8px"><a href="../privacy.html">{footer_priv}</a> · <a href="skill-tree.html">Skill Tree</a> · <a href="sparring-simulator.html">{sim_link}</a></p>
  </footer>
</div>
</body>
</html>"""

# ═══════════════════════════════════════════════
# 1. Best BJJ Techniques for Beginners
# ═══════════════════════════════════════════════
pages = []

# JA
sec1_ja = '<h2>🥋 必須テクニック</h2><div class="tech-list">' + \
    pill("rear-naked-choke","リアネイキッドチョーク","BJJとMMAで最も一般的なサブミッション。バックから最も信頼できるフィニッシュ。") + \
    pill("armbar","アームバー","マウントまたはガードからのクラシックなストレートアームバー。すべての柔術家が習得すべき関節技。") + \
    pill("triangle-choke","トライアングルチョーク","脚を使ったガードからの強力な絞め技。体格差のある相手にも有効。") + \
    pill("closed-guard","クローズドガード","グラウンドでの最初の防御ライン。スイープとサブミッションを習得しよう。") + \
    pill("shrimp-escape","シュリンプエスケープ","BJJで最も重要なエスケープ。自動化するまでドリルしよう。") + \
    pill("guard-pass","ガードパス","支配的なポジションに到達するために必須。") + \
    pill("double-leg-takedown","ダブルレッグテイクダウン","最も基本的なレスリングテイクダウン。") + \
    pill("bridge-and-roll","ブリッジアンドロール","白帯から習得すべきマウント脱出。") + \
    '</div>'
faqs_ja = faq("BJJの基本をマスターするのに何ヶ月かかりますか？","一般的に週3回の練習で6〜12ヶ月で基本的なポジションと主要なサブミッションに慣れます。") + \
    faq("白帯はどのサブミッションから始めるべきですか？","リアネイキッドチョークとアームバーが最適な出発点です。有効で比較的セットアップが簡単で、良いポジショナル習慣を強化します。")

pages.append(("ja","best-bjj-techniques-beginners",
    "BJJ初心者向け最強テクニック（2026年）— 白帯完全ガイド",
    "BJJ白帯が習得すべき15の最重要テクニック。まずこれらの基礎を習得してから青帯へ進もう。",
    "BJJ初心者向け最強テクニック",
    "BJJを始めると、数百の技に圧倒されることがあります。どこから始めるべきか？このガイドでは、次のレベルに進む前にすべての初心者が習得すべき必須テクニックを解説します。",
    sec1_ja, faqs_ja, "best-bjj-techniques-beginners"))

# PT
sec1_pt = '<h2>🥋 Técnicas Essenciais</h2><div class="tech-list">' + \
    pill("rear-naked-choke","Rear Naked Choke","A finalização mais comum no BJJ e MMA. Aprenda primeiro — é seu finish mais confiável das costas.") + \
    pill("armbar","Arm Bar","O armbar reto clássico da montada ou guarda. Todo praticante de BJJ deve dominar esta chave de braço.") + \
    pill("triangle-choke","Triangle Choke","Um potente estrangulamento da guarda usando as pernas. Funciona contra adversários muito maiores.") + \
    pill("closed-guard","Closed Guard","Sua primeira linha de defesa no chão. Aprenda a controlar, raspar e finalizar da guarda fechada primeiro.") + \
    pill("shrimp-escape","Shrimp Escape","O único escape mais importante no BJJ. Drille até ficar automático.") + \
    pill("guard-pass","Passagem de Guarda","Essencial para chegar às posições dominantes.") + \
    pill("double-leg-takedown","Double Leg Takedown","O takedown de wrestling mais fundamental.") + \
    pill("bridge-and-roll","Bridge and Roll","O escape de montada que toda faixa-branca deve aprender.") + \
    '</div>'
faqs_pt = faq("Quanto tempo leva para aprender o básico do BJJ?","A maioria dos iniciantes precisa de 6 a 12 meses de treino consistente (3x por semana) para se sentir confortável com posições fundamentais.") + \
    faq("Qual é a melhor finalização para um iniciante de BJJ?","O rear naked choke e o arm bar são os melhores pontos de partida. São eficazes e relativamente simples de configurar.")

pages.append(("pt","best-bjj-techniques-beginners",
    "Melhores Técnicas de BJJ para Iniciantes (2026) — Guia Completo Faixa-Branca",
    "As 15 técnicas de BJJ mais importantes que toda faixa-branca deve aprender. Domine esses fundamentos primeiro.",
    "Melhores Técnicas de BJJ para Iniciantes",
    "Começar o BJJ pode ser esmagador. Com centenas de técnicas, por onde começar? Este guia explica as técnicas essenciais que todo iniciante precisa dominar antes de avançar.",
    sec1_pt, faqs_pt, "best-bjj-techniques-beginners"))

# ═══════════════════════════════════════════════
# 2. Best No-Gi Techniques
# ═══════════════════════════════════════════════
sec2_ja = '<h2>🤼 ノーギ最強テクニック</h2><div class="tech-list">' + \
    pill("rear-naked-choke","リアネイキッドチョーク","ノーギで最も信頼できるフィニッシュ。バックコントロールから即座にセットアップ。") + \
    pill("guillotine-choke","ギロチンチョーク","スタンドとガードから。袖なしだとセットアップしやすい。") + \
    pill("darce-choke","ダースチョーク","ノーギのグラップラーにとって定番の絞め技。スクランブルから強力。") + \
    pill("heel-hook","ヒールフック","現代ノーギの最強武器。膝と足首に巨大なトルクをかける。") + \
    pill("arm-drag","アームドラッグ","ノーギのバックテイクへの最強セットアップ。スタンドとガードの両方から使える。") + \
    pill("double-leg-takedown","ダブルレッグテイクダウン","ノーギで最も一般的なテイクダウン。低リスクで高確率。") + \
    pill("50-50-guard","50/50ガード","現代ノーギレッグロックの主要ポジション。ヒールフックへの入り口。") + \
    '</div>'
faqs2_ja = faq("ノーギBJJはギBJJより難しいですか？","異なる難しさがあります。ノーギはより速く、スクランブルが多い。ギはより技術的で、グリップが豊富です。") + \
    faq("ノーギBJJで最も重要なテクニックは何ですか？","バックテイクとレッグロックシステムが最も重要です。フラッシュポイントはバック取りとヒールフックです。")

pages.append(("ja","best-no-gi-techniques",
    "ノーギBJJ最強テクニック（2026年）— 完全ガイド",
    "ノーギBJJで最も効果的なテクニック一覧。ヒールフックからバックテイクまで、ノーギグラップリングの必須技を解説。",
    "ノーギBJJ最強テクニック",
    "ノーギBJJは道衣なしで行われるグラップリングで、より速く、よりスクランブルが多いスタイルです。成功するためには、ノーギ特有の技術セットが必要です。",
    sec2_ja, faqs2_ja, "best-no-gi-techniques"))

sec2_pt = '<h2>🤼 Melhores Técnicas de No-Gi</h2><div class="tech-list">' + \
    pill("rear-naked-choke","Rear Naked Choke","O finish mais confiável no no-gi. Setup imediato do controle das costas.") + \
    pill("guillotine-choke","Guilhotina","Em pé e da guarda. Mais fácil de configurar sem gi.") + \
    pill("darce-choke","D'Arce Choke","Estrangulamento padrão para grapplers de no-gi. Poderoso dos scrambles.") + \
    pill("heel-hook","Heel Hook","A arma mais poderosa do no-gi moderno. Torque enorme no joelho e tornozelo.") + \
    pill("arm-drag","Arm Drag","O melhor setup para back take no no-gi. Funciona em pé e da guarda.") + \
    pill("double-leg-takedown","Double Leg Takedown","O takedown mais comum no no-gi. Baixo risco, alta porcentagem.") + \
    pill("50-50-guard","Guarda 50/50","A posição central dos leg locks no no-gi moderno.") + \
    '</div>'
faqs2_pt = faq("O no-gi BJJ é mais difícil que o gi?","São dificuldades diferentes. No-gi é mais rápido, com mais scrambles. O gi é mais técnico, com mais grips.") + \
    faq("Quais são as técnicas mais importantes no no-gi BJJ?","Back takes e o sistema de leg locks são os mais importantes. Os pontos focais são o controle das costas e o heel hook.")

pages.append(("pt","best-no-gi-techniques",
    "Melhores Técnicas de No-Gi BJJ (2026) — Guia Completo",
    "As técnicas mais eficazes no no-gi BJJ. De heel hooks a back takes, as técnicas essenciais do grappling sem kimono.",
    "Melhores Técnicas de No-Gi BJJ",
    "O no-gi BJJ é praticado sem kimono — mais rápido, com mais scrambles. Para ter sucesso, você precisa de um conjunto de habilidades específicas do no-gi.",
    sec2_pt, faqs2_pt, "best-no-gi-techniques"))

# ═══════════════════════════════════════════════
# 3. Best BJJ Leg Locks
# ═══════════════════════════════════════════════
sec3_ja = '<h2>🦵 BJJレッグロック完全リスト</h2><div class="tech-list">' + \
    pill("heel-hook","ヒールフック","現代BJJで最も危険なレッグロック。膝に直接トルクをかける。高度テクニック。") + \
    pill("inside-heel-hook","インサイドヒールフック","現代ノーギの最強武器。メキャニクスをマスターするまで細心の注意が必要。") + \
    pill("outside-heel-hook","アウトサイドヒールフック","スタンダードなヒールフック。50/50とニールからアクセス。") + \
    pill("ankle-lock","アンクルロック","最も基本的なレッグロック。白帯から使えるファーストレッグロック。") + \
    pill("knee-bar","ニーバー","膝を過伸展させるレッグロック。ガードやスクランブルから。") + \
    pill("toe-hold","トーホールド","小さな回転でフィニッシュする足首ロック。") + \
    pill("estima-lock","エスティマロック","ガードパス中に隠れた足ロック。Braulio Estimaの名を冠した技。") + \
    pill("50-50-guard","50/50ガード","現代レッグロックシステムの主要ポジション。") + \
    '</div>'
faqs3_ja = faq("レッグロックを競技で使うのは合法ですか？","競技やベルトレベルによります。ヒールフックとニーバーはIBJJFでは上位ベルトのみ合法。常にルールを確認しましょう。") + \
    faq("どのレッグロックから習得すべきですか？","アンクルロックから始めましょう。白帯から合法で、基本的なメカニクスを教えてくれます。")

pages.append(("ja","best-bjj-leg-locks",
    "BJJレッグロック完全ガイド（2026年）— 全種類の解説",
    "BJJの全レッグロック技一覧。ヒールフックからアンクルロックまで、現代レッグロックシステムを完全解説。",
    "BJJレッグロック完全ガイド",
    "レッグロックは現代BJJとサブミッショングラップリングにおいて最も急速に進化している分野の一つです。基本的なアンクルロックから高度なヒールフックシステムまで、このガイドではすべてをカバーします。",
    sec3_ja, faqs3_ja, "best-bjj-leg-locks"))

sec3_pt = '<h2>🦵 Lista Completa de Leg Locks de BJJ</h2><div class="tech-list">' + \
    pill("heel-hook","Heel Hook","O leg lock mais perigoso no BJJ moderno. Torque direto no joelho. Técnica avançada.") + \
    pill("inside-heel-hook","Inside Heel Hook","A arma mais poderosa do no-gi moderno. Requer cuidado extremo até dominar a mecânica.") + \
    pill("outside-heel-hook","Outside Heel Hook","O heel hook padrão. Acessado do 50/50 e knee line.") + \
    pill("ankle-lock","Ankle Lock","O leg lock mais fundamental. O primeiro leg lock legal na faixa-branca.") + \
    pill("knee-bar","Knee Bar","Leg lock que hiperextende o joelho. Da guarda e dos scrambles.") + \
    pill("toe-hold","Toe Hold","Chave de tornozelo finalizada com uma pequena rotação.") + \
    pill("estima-lock","Estima Lock","Chave de pé escondida na passagem de guarda. Nomeada em homenagem a Braulio Estima.") + \
    pill("50-50-guard","Guarda 50/50","A posição central do sistema de leg locks moderno.") + \
    '</div>'
faqs3_pt = faq("Os leg locks são legais na competição de BJJ?","Depende da competição e do nível de faixa. Heel hooks e knee bars são legais apenas para faixas superiores no IBJJF. Sempre verifique as regras.") + \
    faq("Qual leg lock devo aprender primeiro?","Comece com o ankle lock. É legal na faixa-branca e ensina a mecânica básica.")

pages.append(("pt","best-bjj-leg-locks",
    "Guia Completo de Leg Locks de BJJ (2026) — Todas as Técnicas",
    "Todos os leg locks de BJJ explicados. De heel hooks a ankle locks, o sistema completo de leg locks do BJJ moderno.",
    "Guia Completo de Leg Locks de BJJ",
    "Os leg locks são uma das áreas de mais rápida evolução no BJJ e grappling de submissão modernos. Do ankle lock básico ao avançado sistema de heel hooks, este guia cobre tudo.",
    sec3_pt, faqs3_pt, "best-bjj-leg-locks"))

# ═══════════════════════════════════════════════
# 4. BJJ Competition Guide
# ═══════════════════════════════════════════════
sec4_ja = '<h2>🏆 試合前の準備</h2><div class="tech-list">' + \
    pill("closed-guard","クローズドガード","試合での最初の防御。スイープとサブミッションを磨いておこう。") + \
    pill("guard-pass","ガードパス","ポイント稼ぎの基本。3ポイントを確保するためにトップゲームを鍛えよう。") + \
    pill("double-leg-takedown","ダブルレッグテイクダウン","最初のテイクダウンで2ポイント。アグレッションが評価される。") + \
    pill("rear-naked-choke","リアネイキッドチョーク","バックコントロール（4ポイント）から最高のフィニッシュ。") + \
    pill("armbar","アームバー","マウントからのクラシックなフィニッシュ。高い試合勝率。") + \
    '</div><h2>📊 スコアリングシステム</h2><div class="tech-list">' + \
    pill("closed-guard","テイクダウン：2点","スタンドからの安全な方法でグラウンドへ移行し2ポイント。") + \
    pill("guard-pass","ガードパス：3点","相手のガードをパスしてサイドコントロールで2秒以上。") + \
    pill("mount-escape","マウント：4点","フルマウントポジション。最も強力なポジション点数。") + \
    pill("back-mount","バックコントロール：4点","バックグラブ両フック。最も支配的なポジション。") + \
    '</div>'
faqs4_ja = faq("BJJ試合のルールは？","IBJJF、NAGA、ADCCなど組織によって異なります。ポイントシステムは一般的にテイクダウン2点、スイープ2点、ガードパス3点、マウント/バック4点。") + \
    faq("初めてのBJJ試合に向けてどう準備するか？","1つのテイクダウン、2つのガードスイープ、2つのサブミッションを磨くことに集中しましょう。シンプルに保つことが鍵です。")

pages.append(("ja","bjj-competition-guide",
    "BJJ試合ガイド（2026年）— 初めての試合完全準備ガイド",
    "BJJ試合の準備から当日まで完全ガイド。ルール、スコアリング、試合戦略、必須テクニックを網羅。",
    "BJJ試合ガイド",
    "BJJの試合に出ることは、道場でのスパーリングとは全く異なる体験です。このガイドでは、初めての試合の準備から当日のルールまでをカバーします。",
    sec4_ja, faqs4_ja, "bjj-competition-guide"))

sec4_pt = '<h2>🏆 Preparação para a Competição</h2><div class="tech-list">' + \
    pill("closed-guard","Closed Guard","Sua primeira defesa na competição. Afine suas raspagens e finalizações.") + \
    pill("guard-pass","Passagem de Guarda","Fundamental para acumular pontos. Fortaleça o jogo de cima para garantir 3 pontos.") + \
    pill("double-leg-takedown","Double Leg Takedown","Primeiro takedown vale 2 pontos. A agressividade é recompensada.") + \
    pill("rear-naked-choke","Rear Naked Choke","O melhor finish do controle das costas (4 pontos).") + \
    pill("armbar","Arm Bar","Finish clássico da montada. Alta taxa de vitória em competição.") + \
    '</div><h2>📊 Sistema de Pontuação</h2><div class="tech-list">' + \
    pill("double-leg-takedown","Takedown: 2 pontos","Leve o adversário ao chão de forma segura para 2 pontos.") + \
    pill("guard-pass","Passagem de Guarda: 3 pontos","Passe a guarda do adversário e mantenha o side control por 2 segundos.") + \
    pill("mount-escape","Montada: 4 pontos","Full mount — a pontuação posicional mais poderosa.") + \
    pill("back-mount","Controle das Costas: 4 pontos","Pegue as costas com dois ganchos — posição mais dominante.") + \
    '</div>'
faqs4_pt = faq("Quais são as regras do BJJ em competição?","Variam por organização (IBJJF, NAGA, ADCC). O sistema de pontos geralmente é: takedown 2 pts, raspagem 2 pts, passagem 3 pts, montada/costas 4 pts.") + \
    faq("Como me preparar para minha primeira competição de BJJ?","Foque em dominar 1 takedown, 2 raspagens de guarda e 2 finalizações. Manter simples é a chave.")

pages.append(("pt","bjj-competition-guide",
    "Guia de Competição de BJJ (2026) — Preparação Completa para Iniciantes",
    "Guia completo de preparação para competições de BJJ. Regras, pontuação, estratégia e técnicas essenciais.",
    "Guia de Competição de BJJ",
    "Competir no BJJ é uma experiência totalmente diferente do sparring na academia. Este guia cobre desde a preparação para a primeira competição até as regras do dia da luta.",
    sec4_pt, faqs4_pt, "bjj-competition-guide"))

# ═══════════════════════════════════════════════
# 5. BJJ Takedowns Guide
# ═══════════════════════════════════════════════
sec5_ja = '<h2>🤼 BJJ必須テイクダウン</h2><div class="tech-list">' + \
    pill("double-leg-takedown","ダブルレッグテイクダウン","BJJとMMAで最も一般的なテイクダウン。低リスクで高確率。") + \
    pill("ankle-pick","アンクルピック","精密なハンドファイトから足首を取るテイクダウン。大きな相手にも有効。") + \
    pill("arm-drag","アームドラッグ","テイクダウンへの汎用的なセットアップ。バックテイクとダブルレッグに展開。") + \
    pill("harai-goshi","払腰","柔道のクラシックな払い腰。競技BJJで強力な得点技。") + \
    pill("ippon-seoi-nage","一本背負投","爆発的な肩投げ。相手を完全に空中に浮かせる。") + \
    pill("snap-down","スナップダウン","頭を引き下げるシンプルなレスリングセットアップ。バックテイクかダブルレッグに繋げる。") + \
    '</div>'
faqs5_ja = faq("BJJではどのテイクダウンが最も効果的ですか？","ダブルレッグとアンクルピックは、安全で高確率なため最も実用的です。") + \
    faq("BJJ試合でテイクダウンは必須ですか？","必須ではありませんがポイントになります。ガードプルも戦略的選択肢ですが、常に相手に2ポイントを与えます。")

pages.append(("ja","bjj-takedowns-guide",
    "BJJテイクダウン完全ガイド（2026年）— スタンドゲーム必須技",
    "BJJ競技で使えるテイクダウン技を完全網羅。ダブルレッグから払腰まで、スタンドゲームのすべて。",
    "BJJテイクダウン完全ガイド",
    "スタンドゲームはBJJで見落とされがちな分野ですが、試合での最初の2ポイントはここから始まります。このガイドでは、BJJ競技で実際に機能するテイクダウンをカバーします。",
    sec5_ja, faqs5_ja, "bjj-takedowns-guide"))

sec5_pt = '<h2>🤼 Quedas Essenciais de BJJ</h2><div class="tech-list">' + \
    pill("double-leg-takedown","Double Leg Takedown","O takedown mais comum no BJJ e MMA. Baixo risco, alta porcentagem.") + \
    pill("ankle-pick","Ankle Pick","Takedown de varredura de tornozelo. Eficaz contra adversários maiores.") + \
    pill("arm-drag","Arm Drag","Setup versátil para quedas. Leva ao back take ou double leg.") + \
    pill("harai-goshi","Harai Goshi","O golpe de quadril clássico do judô. Arma de pontuação poderosa no BJJ competitivo.") + \
    pill("ippon-seoi-nage","Ippon Seoi Nage","Arremesso de ombro explosivo. Lança o adversário completamente.") + \
    pill("snap-down","Snap Down","Setup de wrestling que puxa a cabeça para baixo. Leva ao back take ou double leg.") + \
    '</div>'
faqs5_pt = faq("Qual takedown é mais eficaz no BJJ?","O double leg e o ankle pick são os mais práticos — seguros e de alta porcentagem.") + \
    faq("As quedas são obrigatórias no BJJ competitivo?","Não, mas marcam pontos. A puxada de guarda é uma escolha estratégica, mas sempre dá 2 pontos ao adversário.")

pages.append(("pt","bjj-takedowns-guide",
    "Guia Completo de Quedas de BJJ (2026) — Jogo de Pé Essencial",
    "Todas as quedas de BJJ competitivo explicadas. De double leg a harai goshi, tudo sobre o jogo de pé.",
    "Guia Completo de Quedas de BJJ",
    "O jogo de pé é a área mais negligenciada do BJJ, mas os primeiros 2 pontos de uma luta vêm de uma queda. Este guia cobre os takedowns que realmente funcionam na competição de BJJ.",
    sec5_pt, faqs5_pt, "bjj-takedowns-guide"))

# ─────────────────────────────────────────────
# Write all files
# ─────────────────────────────────────────────
for lang, slug, title, desc, h1, intro, sections_html, faqs_html, en_slug in pages:
    html = page(lang, slug, title, desc, h1, intro, sections_html, faqs_html, en_slug)
    path = f"{lang}/{slug}.html"
    with open(path, 'w') as f:
        f.write(html)
    print(f"Created: {path}")

print(f"\nDone: {len(pages)} pillar pages generated")
