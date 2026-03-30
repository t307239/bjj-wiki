#!/usr/bin/env python3
"""Generate kneebar.html and d-arce-choke.html for en/ja/pt"""
import os, json, datetime

BASE = os.path.dirname(__file__) + "/.."
SITE = "https://wiki.bjj-app.net"
GA4  = "G-7LM8L3TRZM"
ADS  = "ca-pub-5529701443220352"

CSS = """:root{--bg:#0f172a;--card:#141926;--border:#1e293b;--text:#e2e8f0;--muted:#64748b;--accent:#e94560;--accent2:#a78bfa}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:16px;line-height:1.8;padding:0 16px}
a{color:var(--accent2);text-decoration:none}a:hover{text-decoration:underline}
.container{max-width:860px;margin:0 auto;padding-bottom:80px}
header{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;padding:16px 0;border-bottom:1px solid var(--border);margin-bottom:24px}
.logo{font-size:1.2rem;font-weight:800;color:var(--accent)}
.lang-nav{display:flex;gap:8px}
.lang-nav a{color:var(--muted);font-size:.82rem;padding:4px 10px;border-radius:4px;border:1px solid var(--border)}
.lang-nav a.active,.lang-nav a:hover{color:var(--text);border-color:var(--accent)}
.breadcrumb{font-size:.78rem;color:var(--muted);margin-bottom:16px}
.breadcrumb a{color:var(--muted)}
.meta-badges{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}
.badge{font-size:.75rem;padding:3px 10px;border-radius:12px;font-weight:600;border:1px solid var(--border);background:#1e293b;color:var(--muted)}
h1{font-size:1.8rem;font-weight:800;line-height:1.3;margin-bottom:12px;color:var(--text)}
h2{font-size:1.1rem;font-weight:700;color:var(--accent);margin:28px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--border)}
h3{color:var(--accent2);font-size:1rem;margin:16px 0 8px}
p{color:var(--text);margin-bottom:12px;line-height:1.8}
ul,ol{padding-left:20px;margin-bottom:14px}
li{margin-bottom:6px;color:var(--text)}
.intro{background:var(--card);border-left:3px solid var(--accent);border-radius:0 8px 8px 0;padding:14px 16px;margin-bottom:24px;font-size:1rem;color:var(--muted)}
.tip-box{background:var(--card);border:1px solid rgba(233,69,96,0.2);border-radius:12px;padding:16px 20px;margin:20px 0}
.tip-box h3{font-size:.85rem;text-transform:uppercase;letter-spacing:.05em;color:var(--accent);margin-bottom:10px}
.tip-box ul{list-style:none;padding:0}
.tip-box li{padding:5px 0 5px 20px;position:relative;font-size:.93rem}
.tip-box li::before{content:'▸';position:absolute;left:0;color:var(--accent)}
.cta-box{background:linear-gradient(135deg,rgba(233,69,96,0.12),rgba(167,139,250,0.08));border:1px solid rgba(233,69,96,0.4);border-radius:16px;padding:24px;text-align:center;margin:28px 0}
.cta-box p{color:var(--muted);margin-bottom:14px}
.cta-btn{display:inline-block;background:var(--accent);color:#fff;padding:12px 28px;border-radius:8px;font-weight:700;text-decoration:none}
.cta-btn:hover{opacity:.9;text-decoration:none}
.faq-item{border-bottom:1px solid var(--border);padding:16px 0}
.faq-item:last-child{border-bottom:none}
.faq-q{font-size:.95rem;font-weight:700;margin-bottom:8px}
.faq-a{font-size:.9rem;color:var(--muted);line-height:1.7}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px}
footer{margin-top:48px;padding-top:16px;border-top:1px solid var(--border);text-align:center;color:var(--muted);font-size:.78rem}
@media(max-width:600px){h1{font-size:1.4rem}}"""

PAGES = {
  "kneebar": {
    "en": {
      "title": "Kneebar — Complete BJJ Leg Lock Guide | BJJ Wiki",
      "meta": "The kneebar is a dangerous BJJ leg lock attacking the knee joint. Learn setup, entry, finishing mechanics, and defense in this comprehensive guide.",
      "h1": "Kneebar: The Straight Leg Lock That Targets the Knee",
      "badges": ["🔴 Leg Lock","🥋 Advanced","⚠️ Competition: Check rules"],
      "intro": "The kneebar is a submission hold that attacks the knee joint by hyperextending it using the full body as a lever. Often called the 'armbar of the legs', it is one of the most effective and quickest-finishing leg locks in submission grappling. A properly applied kneebar can end a match in seconds.",
      "body": """<h2>What Is a Kneebar?</h2>
<p>A kneebar (also written knee bar) is a straight leg lock that applies hyperextension pressure to the knee joint. The attacker places the opponent's knee across their hip or torso, secures the foot and ankle, and extends their hips forward while pulling the leg back — creating a mechanical lever that puts severe strain on the posterior cruciate ligament (PCL), the joint capsule, and the lateral structures of the knee.</p>
<p>Unlike heel hooks, which rotate the knee, the kneebar attacks the knee in its natural range of motion through hyperextension. This makes it one of the cleaner leg locks in terms of mechanics, but no less dangerous — competitors tap quickly to a well-applied kneebar or risk serious ligament damage.</p>

<h2>Competition Rules</h2>
<p>The kneebar is <strong>legal in most no-gi submission grappling</strong> competitions including ADCC, EBI, and WNO, typically from a certain age or experience level. In IBJJF gi and no-gi competitions, the kneebar is restricted to brown and black belt divisions. Always check current rules for your specific competition before training it with submission intent.</p>

<h2>How to Perform a Kneebar — Step by Step</h2>
<ol>
<li><strong>Isolate the leg.</strong> From top position (mount, guard pass, top of the leg entanglement), isolate your opponent's leg so you can control it with both arms.</li>
<li><strong>Secure the foot.</strong> Place the opponent's foot into your armpit or between your arm and ribs, securing it with a grip on the shin or ankle. The foot should point upward, not sideways.</li>
<li><strong>Place their knee across your hip.</strong> The kneecap faces up or slightly toward you. Your hip bone acts as the fulcrum for the lever — positioning is critical here.</li>
<li><strong>Grip the shin with both hands.</strong> A two-handed grip above or below the knee controls the leg. Some variations use a figure-four grip for added control.</li>
<li><strong>Extend your hips forward.</strong> While pulling the shin toward your chest, push your hips forward into the back of their knee. This creates the hyperextension. Control the speed — the finish can come very quickly.</li>
</ol>

<h2>Common Entries to the Kneebar</h2>
<p>The kneebar can be entered from many positions:</p>
<ul>
<li><strong>Top of leg entanglement (saddle/411)</strong>: One of the most common no-gi entries. After securing a single leg, transition the knee across your hip.</li>
<li><strong>Failed guard pass</strong>: When an opponent tries to resist your pass and extends their leg, the kneebar entry opens naturally.</li>
<li><strong>Mount/knee-on-belly transition</strong>: As you step over an opponent, their near leg can be isolated for a kneebar.</li>
<li><strong>From bottom guard</strong>: Butterfly guard and x-guard create opportunities to attack the near knee with a kneebar entry.</li>
<li><strong>50/50 guard</strong>: The 50/50 position allows attacks on both opponents' legs including the kneebar.</li>
</ul>

<h2>Finishing Details</h2>
<p>The kneebar finish requires attention to three elements: the knee must be properly positioned across your hip (not your thigh or stomach), your grip must hold the shin firmly above the ankle, and the hip extension must be controlled and steady. Jerking the finish is dangerous — a smooth, increasing pressure gives your training partner time to tap safely.</p>
<p>The classic finish position has your body perpendicular to your opponent, their leg running across your torso. Your toes dig into their glutes or hamstring to prevent them from rolling away. Hip extension is the primary force, not arm strength.</p>

<h2>Defense and Escape</h2>
<p>The primary defense against a kneebar is <em>preventing the entry</em> — keeping your legs away from dangerous positions and avoiding the leg being isolated in the first place. Once the kneebar is locked in, options narrow significantly. Possible escapes include rolling over the trapped leg before the finish is applied, or framing against the hip to buy time. Tapping early is strongly recommended — knee ligament injuries from kneebars are serious and slow to heal.</p>""",
      "tips": ["Always tap early — knee injuries from leg locks heal slowly and can end your BJJ career prematurely.",
               "The hip placement (their knee over your hip bone, not your thigh) is the single most important technical detail.",
               "Learn the kneebar alongside heel hooks to understand the full leg lock system — they share many entries and complement each other.",
               "Film your drilling from the side to check knee alignment across your hip."],
      "faq": [
        {"q": "Is a kneebar dangerous?", "a": "Yes — a kneebar attacks the PCL and joint structures of the knee. It can cause serious ligament damage if not respected. Always tap early, drill at slow speed with a cooperative partner, and only apply with submission intent in appropriate competition formats."},
        {"q": "What is the difference between a kneebar and a heel hook?", "a": "A kneebar hyperextends the knee joint by using the hip as a fulcrum and pulling the shin while pushing the knee. A heel hook attacks the same joint but with a rotational force applied to the heel — targeting the medial or lateral ligaments. Heel hooks are generally considered more dangerous because the rotational damage can occur before pain registers."},
        {"q": "At what level is the kneebar allowed in competition?", "a": "In IBJJF, the kneebar is restricted to brown and black belt divisions. In ADCC, EBI, WNO and most no-gi submission-only events it is generally allowed for adult competitors. Always verify current rules for your specific event."},
      ]
    },
    "ja": {
      "title": "ニーバー — BJJレッグロック完全ガイド | BJJ Wiki",
      "meta": "ニーバーは膝関節を攻撃するBJJの危険なレッグロック。セットアップ・エントリー・フィニッシュメカニクス・ディフェンスを解説。",
      "h1": "ニーバー（Kneebar）：膝関節を攻撃するストレートレッグロック",
      "badges": ["🔴 レッグロック","🥋 上級","⚠️ 競技: ルール確認必須"],
      "intro": "ニーバーは膝関節を過伸展させることでタップを取るサブミッション。「脚のアームバー」とも呼ばれ、適切に決まれば数秒で試合を終わらせる破壊力を持つ。",
      "body": """<h2>ニーバーとは</h2>
<p>ニーバーは相手の膝関節を直線的に過伸展させるストレートレッグロック。攻撃者は相手の膝を腰骨に乗せ、すねを引き寄せながらヒップを前に押し出すことで、後十字靭帯（PCL）・関節包・外側構造に強い負荷をかける。かかとを回転させるヒールフックと違い、ニーバーは関節の自然な動き方向への過伸展なので「クリーン」なロックに分類されるが、危険度は変わらない。上手く決まったニーバーへのタップは迅速に行わなければ靭帯断裂のリスクがある。</p>

<h2>競技ルール</h2>
<p>ADCC・EBI・WNOなどほとんどのノーギ・サブミッションオンリー大会では<strong>成人のニーバーは合法</strong>。IBJJFでは道着・ノーギ共に茶帯・黒帯のみ許可。出場する大会の最新ルールを必ず確認すること。</p>

<h2>ニーバーの手順</h2>
<ol>
<li><strong>脚を孤立させる。</strong> マウント・ガードパス・レッグエンタングルメントのトップから相手の片脚を両腕でコントロールする。</li>
<li><strong>足首を固定する。</strong> 相手の足先を脇の下か腕と肋骨の間に挟み込み、すね・足首をグリップ。足先は横ではなく上を向かせる。</li>
<li><strong>膝を腰骨の上に置く。</strong> 膝蓋骨が上または自分の方向を向くように。腰骨がレバーの支点になるため位置決めが最重要。</li>
<li><strong>両手ですねを掴む。</strong> 膝の上か下に両手グリップ。フィギュアフォーグリップで安定させる方法もある。</li>
<li><strong>腰を前に出しながらすねを胸に引く。</strong> これが過伸展圧力を生む。フィニッシュは速く来ることがある——ゆっくり確実に増圧すること。</li>
</ol>

<h2>主なエントリー</h2>
<ul>
<li><strong>サドル（411）のトップ</strong>: ノーギで最もポピュラー。シングルレッグを確保した後、膝を腰骨越しに移行。</li>
<li><strong>ガードパス失敗</strong>: 相手がパスを防ごうと脚を伸ばした瞬間にエントリーが開く。</li>
<li><strong>マウント・ニーオンベリーの移行中</strong>: 跨ぐ際に近い方の脚を孤立させてニーバーへ。</li>
<li><strong>バタフライガード・Xガードから</strong>: 下から近い膝へのアタックが可能。</li>
<li><strong>50/50ガード</strong>: 両者の脚が絡み合う状態からニーバーを含む複数のアタックが可能。</li>
</ul>

<h2>ディフェンスと脱出</h2>
<p>最大のディフェンスは<em>エントリーを防ぐこと</em>。脚が孤立する体勢を避け、危険なポジションに誘い込まれないよう注意する。ロックされた後の選択肢は限られる。フィニッシュ前にかかった脚側に転がるか、腰にフレームを当てて時間を稼ぐ方法があるが、早めのタップを強く推奨する。</p>""",
      "tips": ["早めにタップ——膝靭帯の回復は遅く、重傷化するとBJJキャリアに長期影響が出る。","腰骨への位置決め（太腿や腹でなく腰骨）が技術的に最も重要なポイント。","ヒールフックと併せて学ぶことでレッグロックシステム全体の理解が深まる。","横からドリルを録画し、膝が腰骨上に正しく乗っているか確認しよう。"],
      "faq": [
        {"q": "ニーバーは危険ですか？", "a": "はい。後十字靭帯や関節構造を攻撃するため、尊重しないと深刻な靭帯損傷につながります。常に早めにタップし、パートナーとのスロードリルで練習してください。"},
        {"q": "ニーバーとヒールフックの違いは？", "a": "ニーバーは腰を支点にすねを引いて膝を過伸展させる直線的なロック。ヒールフックはかかとに回転力を与えて内側・外側の靭帯を攻撃する。ヒールフックは痛みが出る前にダメージが蓄積するため、より危険とされる。"},
        {"q": "ニーバーは何帯から競技で使えますか？", "a": "IBJJFでは茶帯・黒帯のみ許可。ADCCやEBIなどのノーギ大会では一般的に成人競技者に許可されています。出場大会の最新ルールを必ず確認してください。"},
      ]
    },
    "pt": {
      "title": "Kneebar — Guia Completo de Leg Lock no BJJ | BJJ Wiki",
      "meta": "O kneebar é uma chave de perna do BJJ que ataca a articulação do joelho. Aprenda setup, entrada, mecânica de finalização e defesa neste guia completo.",
      "h1": "Kneebar: A Chave de Perna Que Ataca o Joelho",
      "badges": ["🔴 Leg Lock","🥋 Avançado","⚠️ Competição: Verificar regras"],
      "intro": "O kneebar é uma finalização que ataca o joelho por hiperextensão usando o corpo inteiro como alavanca. Chamado de 'armbar da perna', é um dos leg locks mais eficazes no grappling — uma aplicação correta pode terminar uma luta em segundos.",
      "body": """<h2>O que é o Kneebar?</h2>
<p>O kneebar é um leg lock reto que aplica pressão de hiperextensão na articulação do joelho. O atacante coloca o joelho do oponente sobre seu quadril, assegura o pé e o tornozelo, e estende os quadris para frente enquanto puxa a perna de volta — criando uma alavanca mecânica que coloca tensão severa no ligamento cruzado posterior (LCP), na cápsula articular e nas estruturas laterais do joelho.</p>
<p>Ao contrário dos heel hooks, que rotacionam o joelho, o kneebar ataca o joelho em sua amplitude natural de movimento através de hiperextensão. Competidores devem bater rapidamente para um kneebar bem aplicado ou arriscar danos sérios aos ligamentos.</p>

<h2>Regras de Competição</h2>
<p>O kneebar é <strong>legal na maioria das competições de submission wrestling no-gi</strong> incluindo ADCC, EBI e WNO. No IBJJF gi e no-gi, o kneebar é restrito às divisões de faixa marrom e preta. Sempre verifique as regras atuais da sua competição específica.</p>

<h2>Como Executar um Kneebar — Passo a Passo</h2>
<ol>
<li><strong>Isole a perna.</strong> Da posição de cima (montada, passagem de guarda, topo do leg entanglement), isole a perna do oponente para controlá-la com ambos os braços.</li>
<li><strong>Assegure o pé.</strong> Coloque o pé do oponente na sua axila ou entre seu braço e costelas, com um grip na canela ou tornozelo. O pé deve apontar para cima, não para o lado.</li>
<li><strong>Coloque o joelho deles sobre seu quadril.</strong> A patela aponta para cima ou ligeiramente em sua direção. O osso do quadril atua como o fulcro da alavanca.</li>
<li><strong>Segure a canela com ambas as mãos.</strong> Um grip com as duas mãos acima ou abaixo do joelho controla a perna.</li>
<li><strong>Estenda os quadris para frente.</strong> Enquanto puxa a canela em direção ao peito, empurre os quadris para frente contra a parte de trás do joelho deles. Isso cria a hiperextensão.</li>
</ol>

<h2>Entradas Comuns para o Kneebar</h2>
<ul>
<li><strong>Topo do leg entanglement (saddle/411)</strong>: Uma das entradas mais comuns no no-gi.</li>
<li><strong>Passagem de guarda falhada</strong>: Quando o oponente estende a perna para resistir à sua passagem.</li>
<li><strong>Transição de montada/knee-on-belly</strong>: Ao passar por cima, a perna próxima pode ser isolada para um kneebar.</li>
<li><strong>Da guarda butterfly ou x-guard</strong>: Oportunidades para atacar o joelho próximo com entrada de kneebar.</li>
</ul>

<h2>Defesa e Escape</h2>
<p>A principal defesa contra um kneebar é <em>prevenir a entrada</em> — mantendo as pernas longe de posições perigosas. Uma vez que o kneebar está travado, as opções se estreitam significativamente. Bater cedo é fortemente recomendado — lesões no ligamento do joelho por kneebars são sérias e demoram para curar.</p>""",
      "tips": ["Sempre bata cedo — lesões no joelho cicatrizam lentamente e podem encerrar sua carreira prematuramente.","O posicionamento do quadril (joelho deles sobre seu osso do quadril, não sua coxa) é o detalhe técnico mais importante.","Aprenda o kneebar junto com heel hooks para entender o sistema completo de leg locks.","Filme seu drilling de lado para verificar o alinhamento do joelho sobre seu quadril."],
      "faq": [
        {"q": "O kneebar é perigoso?", "a": "Sim — o kneebar ataca o LCP e as estruturas articulares do joelho. Pode causar danos sérios aos ligamentos se não for respeitado. Sempre bata cedo, faça drills em velocidade lenta com um parceiro cooperativo."},
        {"q": "Qual é a diferença entre kneebar e heel hook?", "a": "Um kneebar hiperextende a articulação do joelho usando o quadril como fulcro e puxando a canela enquanto empurra o joelho. Um heel hook ataca a mesma articulação mas com uma força rotacional aplicada ao calcanhar — direcionando os ligamentos mediais ou laterais. Os heel hooks são geralmente considerados mais perigosos porque o dano rotacional pode ocorrer antes que a dor seja registrada."},
        {"q": "Em que nível de faixa o kneebar é permitido em competição?", "a": "No IBJJF, o kneebar é restrito às divisões de faixa marrom e preta. No ADCC, EBI, WNO e na maioria dos eventos de submission no-gi, geralmente é permitido para competidores adultos. Sempre verifique as regras atuais do seu evento específico."},
      ]
    }
  },
  "d-arce-choke": {
    "en": {
      "title": "D'Arce Choke — BJJ Neck Lock Submission Guide | BJJ Wiki",
      "meta": "The D'Arce choke is a powerful arm-in guillotine-style choke from top position. Learn setup, mechanics, entries, and how to defend against it.",
      "h1": "D'Arce Choke: The Arm-In Neck Lock from Top Position",
      "badges": ["🔵 Choke","🥋 Intermediate","✅ Competition legal"],
      "intro": "The D'Arce choke (also called the Joe D'Arce choke or no-gi loop choke) is an arm-in guillotine-type submission applied primarily from top position — making it distinct from most chokes that are applied from guard. Once locked in, the D'Arce cuts blood flow to the brain and produces a rapid tap.",
      "body": """<h2>What Is the D'Arce Choke?</h2>
<p>The D'Arce choke is a blood choke that compresses the carotid arteries by wrapping one arm under the opponent's armpit (the 'arm-in' position), threading it through to the neck, and locking a figure-four or triangle with the other arm. Unlike the guillotine, the D'Arce is typically applied from positions like north-south, side control, or the back — making it a top-position weapon.</p>
<p>It was popularized in competition by Joe D'Arce, a grappler under Renzo Gracie, and quickly became a staple of high-level no-gi and MMA grappling. In the modern game, it is closely related to the Anaconda choke — the two submissions share entries and setups, often in the same scramble.</p>

<h2>Anatomy of the D'Arce</h2>
<p>The choke works by encircling the neck with one arm that threads under the opponent's arm (the arm that is closest to the mat in side control or north-south). Your choking arm goes under their armpit from the front, threads behind their neck, and your hands lock in a figure-four or rear-naked-choke style grip. The pressure of the figure-four closes the blood choke rapidly.</p>
<p>Key detail: the arm must be truly under the armpit (not just around the shoulder) for the choke to reach the neck properly. Hip and shoulder pressure add force to the finish.</p>

<h2>Common Entries</h2>
<p>The D'Arce is set up from several common positions:</p>
<ul>
<li><strong>Side control to north-south</strong>: The most classic setup. From side control, if your opponent tries to create an underhook and bridge, you can shoot the arm in under their armpit and begin the D'Arce entry as you move toward north-south.</li>
<li><strong>North-south</strong>: From north-south, if the opponent attempts to bridge or roll, slip your arm under their near armpit before they complete the escape.</li>
<li><strong>Sprawl/turtle defense</strong>: When your opponent turtles up to defend a takedown, step around to their side, get a whizzer, and thread your arm under the armpit into the D'Arce.</li>
<li><strong>Scramble recovery</strong>: Many D'Arce chokes are caught opportunistically during guard pass scrambles when the opponent exposes their neck while defending.</li>
</ul>

<h2>Finishing the D'Arce</h2>
<p>Lock your hands in a figure-four (rear-naked-choke grip). Your choking arm's bicep should press against one side of the opponent's neck while your forearm presses the other side. Drive your chest/shoulder into the back of their head to add pressure. The opponent should be unable to roll or bridge to relieve pressure if your hip position is correct.</p>
<p>A common mistake is pulling the neck without hip pressure — this allows the opponent to roll away. Keep your hips low and heavy, perpendicular to their body, to prevent escape attempts.</p>

<h2>D'Arce vs Anaconda</h2>
<p>The D'Arce and Anaconda choke are closely related. The primary difference is the arm position: in a D'Arce, the choking arm threads under the armpit from the front (near the face). In the Anaconda, the arm threads from behind (away from the face). Both attack the same neck structures. They are often taught as a pair — if the opponent blocks one, the other becomes available.</p>

<h2>Defense</h2>
<p>The main defenses are: tuck your chin to protect the neck (makes threading the arm harder), maintain an underhook with the near arm to prevent the arm-in entry, and avoid dropping your head when bridging from bottom. If the D'Arce is partially locked, try to spin into your opponent (turning toward them rather than away) to relieve neck pressure before it tightens.</p>""",
      "tips": ["The arm-in entry is everything — drill getting the arm under the armpit, not just around the shoulder.",
               "Pair D'Arce with Anaconda practice: they share the same scramble entry and one always opens when the other is defended.",
               "Keep your hips heavy and low once the choke is locked — this is what prevents the opponent from rolling away.",
               "Practice entry from turtle/sprawl, not just from side control — many match opportunities come from takedown defense."],
      "faq": [
        {"q": "What is the difference between a D'Arce and guillotine?", "a": "Both are arm-in chokes that compress the neck, but the guillotine is applied from bottom/guard with the arm threading from front-to-back, while the D'Arce is applied from top position with the arm going under the armpit. The D'Arce is a top-position weapon; the guillotine primarily a guard position weapon."},
        {"q": "Is the D'Arce choke legal in gi BJJ?", "a": "Yes — the D'Arce choke is legal at all belt levels in both gi and no-gi BJJ competition, including IBJJF events. It is not considered a dangerous technique in the way that certain leg locks are restricted."},
        {"q": "What is a D'Arce choke called in Portuguese?", "a": "In Portuguese and Brazilian BJJ circles, the D'Arce is sometimes called 'chave de ombro' (shoulder lock choke) or simply referenced by its English name. The Anaconda choke, its cousin, is widely used under that same name in Brazil."},
      ]
    },
    "ja": {
      "title": "ダルセチョーク（D'Arce Choke）— BJJサブミッション完全ガイド | BJJ Wiki",
      "meta": "ダルセチョークはトップポジションから決める強力なアームイン系絞め技。セットアップ・メカニクス・エントリー・ディフェンスを解説。",
      "h1": "ダルセチョーク：トップポジションからのアームイン首絞め",
      "badges": ["🔵 絞め技","🥋 中級","✅ 競技合法"],
      "intro": "ダルセチョーク（D'Arce Choke、別名ジョー・ダルセチョーク）はトップポジション主体のアームイン系サブミッション。ガードからかけるギロチンと対照的にサイドコントロールやノーススースからかけるのが特徴で、一度ロックされると頸動脈の血流を遮断して素早いタップを奪う。",
      "body": """<h2>ダルセチョークとは</h2>
<p>ダルセチョークは頸動脈を圧迫するブラッドチョーク。一方の腕を相手の脇の下に差し込み（アームイン）、首の後ろまで通してフィギュアフォーやRNCスタイルのグリップでロックする。ギロチンと違い、サイドコントロール・ノーススース・バックコントロールなどのトップポジションから決めるため「トップの武器」として重宝される。</p>
<p>レンゾ・グレイシー道場のジョー・ダルセが競技で広め、現代のノーギ・MMAグラップリングの定番技になった。アナコンダチョークと密接に関連しており、同じスクランブルで両方を仕掛けることが多い。</p>

<h2>技の解剖学</h2>
<p>チョークは首を囲む腕が相手の脇の下を通ることで機能する（マットに近い側の腕）。絞め腕が前側から脇の下に入り、首の後ろを経由して手をフィギュアフォーでロック。このフォームが頸動脈を素早く圧迫する。</p>
<p>重要ポイント：腕は肩ではなく確実に脇の下を通ること。腰と肩の体重がフィニッシュの力を補助する。</p>

<h2>主なエントリー</h2>
<ul>
<li><strong>サイドコントロール→ノーススース</strong>: 最も典型的なセットアップ。相手がアンダーフックで逃げようとする動きに合わせて腕を差し込みノーススースへ移行。</li>
<li><strong>ノーススースから</strong>: 相手がブリッジやロールで脱出しようとした瞬間に近い方の脇の下に腕を通す。</li>
<li><strong>スプロール・タートルディフェンス</strong>: 相手がタートルになったときに側面に回り込み、脇の下にアームを差し込んでダルセへ。</li>
<li><strong>スクランブル中</strong>: ガードパスのスクランブル中に相手が首を露出した際にオポチュニスティックに決まることが多い。</li>
</ul>

<h2>フィニッシュのコツ</h2>
<p>フィギュアフォー（RNCグリップ）でロック。絞め腕の上腕二頭筋が首の一方に、前腕が逆側に当たるようにする。胸・肩を相手の頭の後ろに押し付けて圧力を加える。腰を低く重く保つことで相手のロールによる脱出を防ぐ。</p>
<p>よくある失敗：腰の体重なしに首だけ引くと相手に転がって脱出されてしまう。腰骨を体に垂直にぴったり密着させることが重要。</p>

<h2>ダルセ vs アナコンダ</h2>
<p>両者は密接に関連する。主な違いは腕の向き——ダルセは顔側（前側）から腕が通り、アナコンダは後ろ側から腕が通る。同じ首の構造を攻撃するため、一方をディフェンスすれば他方が開くという関係にある。セットで練習することを強く推奨する。</p>

<h2>ディフェンス</h2>
<p>主なディフェンスは、あごを引いて首を守ること、近い腕のアンダーフックでアームイン・エントリーを阻止すること。ダルセが半分かかった状態では、相手の方向に向かってスピン（体をひねる）することで首の圧力を緩和できる。</p>""",
      "tips": ["アームインエントリー（肩ではなく脇の下）がすべて。脇の下に腕を通す動きを繰り返しドリル。","アナコンダとセットで練習する——同じエントリーを共有し、一方をディフェンスすると他方が開く。","チョークロック後は腰を低く重く保つ——これが相手のロールによる脱出を防ぐ唯一の方法。","タートル・スプロールからのエントリーを特に練習する——試合ではテイクダウンディフェンス中にチャンスが来ることが多い。"],
      "faq": [
        {"q": "ダルセチョークとギロチンの違いは何ですか？", "a": "両方アームイン系のネックチョークですが、ギロチンは下（ガード）から前後方向に腕を通し、ダルセはトップポジションから脇の下に腕を差し込みます。ギロチンはガードの武器、ダルセはトップの武器という対照的な関係です。"},
        {"q": "ダルセチョークは道着のBJJでも合法ですか？", "a": "はい。ダルセチョークはIBJJFを含む道着・ノーギ両方の全帯レベルで合法です。特定のレッグロックのような制限はありません。"},
        {"q": "ダルセとアナコンダはどちらが難しいですか？", "a": "どちらも習得に時間がかかりますが、一般的にダルセはサイドコントロールからのエントリーが自然でアクセスしやすいとされます。アナコンダはタートル（亀）からのエントリーが独特です。セットで学ぶことで両方の理解が深まります。"},
      ]
    },
    "pt": {
      "title": "D'Arce Choke — Guia Completo de Finalização no BJJ | BJJ Wiki",
      "meta": "O D'Arce choke é um poderoso estrangulamento arm-in aplicado da posição de cima. Aprenda setup, mecânica, entradas e como se defender.",
      "h1": "D'Arce Choke: O Estrangulamento Arm-In da Posição de Cima",
      "badges": ["🔵 Estrangulamento","🥋 Intermediário","✅ Legal em competição"],
      "intro": "O D'Arce choke (também chamado de Joe D'Arce choke) é um estrangulamento arm-in aplicado principalmente da posição de cima — tornando-o distinto da maioria dos estrangulamentos aplicados da guarda. Uma vez travado, o D'Arce corta o fluxo sanguíneo ao cérebro e produz um tap rápido.",
      "body": """<h2>O que é o D'Arce Choke?</h2>
<p>O D'Arce choke é um estrangulamento sanguíneo que comprime as artérias carótidas envolvendo um braço sob a axila do oponente (a posição 'arm-in'), threading-o até o pescoço e travando com o outro braço. Ao contrário da guilhotina, o D'Arce é tipicamente aplicado de posições como north-south, controle lateral ou pelas costas.</p>
<p>Foi popularizado em competição por Joe D'Arce, um grappler sob Renzo Gracie, e tornou-se rapidamente um pilar do grappling no-gi e MMA de alto nível. Está intimamente relacionado ao Anaconda choke — as duas finalizações compartilham entradas e setups.</p>

<h2>Entradas Comuns</h2>
<ul>
<li><strong>Controle lateral para north-south</strong>: O setup mais clássico. Se o oponente tenta criar um underhook e fazer bridge, insira o braço sob a axila ao mover-se para north-south.</li>
<li><strong>North-south</strong>: Se o oponente tenta fazer bridge ou rolar, deslize o braço sob a axila próxima antes de completar a fuga.</li>
<li><strong>Sprawl/defesa de tartaruga</strong>: Quando o oponente fica em tartaruga, dê a volta para o lado, obtenha um whizzer e threading o braço sob a axila.</li>
<li><strong>Recuperação de scramble</strong>: Muitos D'Arce chokes são pegos oportunisticamente durante scrambles de passagem de guarda.</li>
</ul>

<h2>Finalizando o D'Arce</h2>
<p>Trave as mãos em figure-four (grip de rear-naked choke). O bíceps do seu braço de estrangulamento deve pressionar um lado do pescoço do oponente enquanto o antebraço pressiona o outro lado. Empurre o peito/ombro na parte de trás da cabeça deles para adicionar pressão. Mantenha os quadris baixos e pesados para evitar tentativas de fuga.</p>

<h2>D'Arce vs Anaconda</h2>
<p>A principal diferença é a posição do braço: no D'Arce, o braço de estrangulamento threading sob a axila pela frente (próximo ao rosto). No Anaconda, o braço threading por trás. Ambos atacam as mesmas estruturas do pescoço e são frequentemente ensinados como um par.</p>

<h2>Defesa</h2>
<p>As principais defesas são: esconder o queixo para proteger o pescoço, manter um underhook com o braço próximo e evitar derrubar a cabeça ao fazer bridge de baixo. Se o D'Arce estiver parcialmente travado, tente girar em direção ao oponente para aliviar a pressão no pescoço.</p>""",
      "tips": ["A entrada arm-in é tudo — drill passando o braço sob a axila, não apenas em torno do ombro.","Pratique D'Arce junto com Anaconda — eles compartilham a mesma entrada e um sempre abre quando o outro é defendido.","Mantenha os quadris pesados e baixos uma vez que o choke está travado.","Pratique entradas de tartaruga/sprawl, não apenas do controle lateral."],
      "faq": [
        {"q": "Qual é a diferença entre D'Arce e guilhotina?", "a": "Ambos são estrangulamentos arm-in que comprimem o pescoço, mas a guilhotina é aplicada de baixo/guarda com o braço threading de frente para trás, enquanto o D'Arce é aplicado da posição de cima com o braço indo sob a axila. O D'Arce é uma arma da posição de cima; a guilhotina principalmente da guarda."},
        {"q": "O D'Arce choke é legal no BJJ com kimono?", "a": "Sim — o D'Arce choke é legal em todos os níveis de faixa tanto no BJJ com kimono quanto no no-gi, incluindo eventos do IBJJF. Não é considerado uma técnica perigosa da forma que certos leg locks são restritos."},
        {"q": "Qual é mais difícil: D'Arce ou Anaconda?", "a": "Ambos levam tempo para dominar, mas geralmente o D'Arce é considerado mais acessível devido à entrada natural do controle lateral. O Anaconda tem uma entrada única da tartaruga. Aprender ambos juntos é fortemente recomendado, pois se complementam perfeitamente."},
      ]
    }
  }
}

def build_page(slug, lang, data):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+09:00")
    lang_links = {
        "en": f'<a href="../../en/{slug}.html" class="{"active" if lang=="en" else ""}">🇺🇸 EN</a>',
        "ja": f'<a href="../../ja/{slug}.html" class="{"active" if lang=="ja" else ""}">🇯🇵 JA</a>',
        "pt": f'<a href="../../pt/{slug}.html" class="{"active" if lang=="pt" else ""}">🇧🇷 PT</a>',
    }
    badges_html = "".join(f'<span class="badge">{b}</span>' for b in data["badges"])
    tips_html = "".join(f"<li>{t}</li>" for t in data["tips"])
    faqs = data["faq"]
    faq_schema = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":f["q"],"acceptedAnswer":{"@type":"Answer","text":f["a"]}} for f in faqs
    ]}, ensure_ascii=False)
    faq_html = "".join(f'<div class="faq-item"><p class="faq-q">{f["q"]}</p><p class="faq-a">{f["a"]}</p></div>' for f in faqs)
    cta = {"en":("Track your BJJ techniques and training progress","Start Free on BJJ App →"),
           "ja":("技術とトレーニングを記録しよう","BJJ Appを無料で始める →"),
           "pt":("Registre suas técnicas e progressos","Começar Grátis no BJJ App →")}[lang]
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{data["title"]}</title>
<meta name="description" content="{data["meta"]}">
<meta property="og:title" content="{data["title"]}">
<meta property="og:description" content="{data["meta"]}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="og:url" content="{SITE}/{lang}/{slug}.html">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE}/{lang}/{slug}.html">
<link rel="alternate" hreflang="x-default" href="{SITE}/en/{slug}.html">
<link rel="alternate" hreflang="en" href="{SITE}/en/{slug}.html">
<link rel="alternate" hreflang="ja" href="{SITE}/ja/{slug}.html">
<link rel="alternate" hreflang="pt" href="{SITE}/pt/{slug}.html">
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA4}');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADS}" crossorigin="anonymous"></script>
<script type="application/ld+json">{faq_schema}</script>
<style>{CSS}</style>
</head>
<body><div class="container">
<header>
  <a href="../index.html" class="logo">🥋 BJJ Wiki</a>
  <div class="lang-nav">{" ".join(lang_links.values())}</div>
</header>
<div class="breadcrumb"><a href="../index.html">BJJ Wiki</a> / <a href="../index.html">Techniques</a> / {data["h1"].split(":")[0]}</div>
<h1>{data["h1"]}</h1>
<div class="meta-badges">{badges_html}</div>
<div class="intro">{data["intro"]}</div>
{data["body"]}
<div class="tip-box">
  <h3>⚡ Quick Training Tips</h3>
  <ul>{tips_html}</ul>
</div>
<h2>FAQ</h2>
<div class="card">{faq_html}</div>
<div class="cta-box"><p>{cta[0]}</p><a href="https://bjj-app.net/login" class="cta-btn">{cta[1]}</a></div>
<footer>BJJ Wiki · Last updated: {today} · <a href="../privacy.html">Privacy</a> · <a href="../about.html">About</a></footer>
</div></body></html>'''

def main():
    for slug, langs in PAGES.items():
        for lang, data in langs.items():
            out_dir = os.path.join(BASE, lang)
            os.makedirs(out_dir, exist_ok=True)
            path = os.path.join(out_dir, f"{slug}.html")
            html = build_page(slug, lang, data)
            with open(path,'w',encoding='utf-8') as f: f.write(html)
            import re
            words = len(re.sub(r'<[^>]+>',' ',html).split())
            print(f"✅ {lang}/{slug}.html ({words} words)")

if __name__ == "__main__":
    main()
