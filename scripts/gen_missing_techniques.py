#!/usr/bin/env python3
"""Generate 10 missing technique pages × 3 languages = 30 pages"""
import os, datetime

TODAY = datetime.date.today().isoformat()

CSS = """
:root{--bg:#080b12;--surface:#0f1420;--card:#141926;--border:#1f2840;--text:#e8eaf6;--muted:#6b7699;--accent:#7c6af7;--accent2:#a78bfa;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--blue:#3b82f6;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif;line-height:1.75;padding:0 16px}
a{color:var(--accent2);text-decoration:none}a:hover{text-decoration:underline}
.container{max-width:860px;margin:0 auto;padding-bottom:80px}
header{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;padding:20px 0;border-bottom:1px solid var(--border);margin-bottom:40px}
.logo{font-size:1.3rem;font-weight:800;color:var(--text)}.logo span{color:var(--accent)}
header nav{display:flex;gap:16px}
header nav a{font-size:0.85rem;color:var(--muted);padding:4px 10px;border-radius:6px;border:1px solid transparent}
header nav a:hover{color:var(--text);border-color:var(--border);text-decoration:none}
.badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:0.72rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;background:#1f2840;color:var(--accent2);border:1px solid #2d2060}
.belt{display:inline-block;padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;margin-left:6px;border:1px solid var(--border)}
.belt-white{color:#e8eaf6;border-color:#3a3a4a;background:#1e1e2e}
.belt-blue{color:var(--blue);border-color:#1e3a6e;background:#0f1e38}
.belt-purple{color:#c084fc;border-color:#4c1d95;background:#1e0f38}
.belt-brown{color:#d97706;border-color:#78350f;background:#241500}
.belt-black{color:#9ca3af;border-color:#374151;background:#111827}
h1{font-size:2.2rem;font-weight:800;line-height:1.25;margin:12px 0 16px;letter-spacing:-0.02em}
@media(max-width:600px){h1{font-size:1.7rem}}
h1+p{font-size:1.05rem;color:#b0b8d4;margin-bottom:32px;line-height:1.8}
h2{font-size:1rem;font-weight:700;color:var(--accent2);text-transform:uppercase;letter-spacing:.08em;display:flex;align-items:center;gap:8px;margin:28px 0 12px}
h2::before{content:'';width:3px;height:14px;background:linear-gradient(180deg,var(--accent),var(--accent2));border-radius:2px;display:block;flex-shrink:0}
.card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:24px;margin-bottom:8px}
.card p{color:#c4cce8;font-size:0.95rem;margin-bottom:0}.card p+p{margin-top:12px}
.card strong{color:var(--text)}
.card .step{display:flex;gap:12px;margin-bottom:14px;align-items:flex-start}
.card .step:last-child{margin-bottom:0}
.step-num{min-width:26px;height:26px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:700;color:#fff;flex-shrink:0;margin-top:2px}
.aff-box{background:linear-gradient(135deg,#141926,#1a1040);border:1px solid #2d2060;border-radius:14px;padding:24px;margin:32px 0;text-align:center}
.aff-box p{color:var(--muted);font-size:0.9rem;margin-bottom:14px}
.aff-btn{display:inline-block;padding:10px 24px;border-radius:10px;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;font-weight:700;font-size:0.9rem}
.aff-btn:hover{opacity:.88;text-decoration:none}
.related-links{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}
.related-links a{display:flex;align-items:center;justify-content:space-between;padding:11px 16px;background:var(--card);border:1px solid var(--border);border-radius:10px;font-size:0.88rem;color:var(--text)}
.related-links a::after{content:'→';color:var(--muted);font-size:0.8rem}
.related-links a:hover{border-color:var(--accent);text-decoration:none}
.share-bar{margin:32px 0;padding:20px;background:var(--card);border:1px solid var(--border);border-radius:12px;text-align:center}
.share-bar p{color:var(--muted);font-size:0.85rem;margin-bottom:12px}
.share-btns{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.share-btn{display:inline-flex;align-items:center;gap:6px;padding:8px 18px;border-radius:8px;font-size:0.85rem;font-weight:700;text-decoration:none}
.share-btn.x{background:#000;color:#fff}.share-btn.reddit{background:#ff4500;color:#fff}
.skill-cta{background:linear-gradient(135deg,#1a0a2e,#0d0820);border:1px solid var(--accent);border-radius:12px;padding:16px 20px;margin:24px 0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}
.skill-cta a{background:var(--accent);color:#fff;padding:8px 20px;border-radius:8px;font-weight:700;font-size:.85rem;text-decoration:none}
footer{padding:28px 0;border-top:1px solid var(--border);text-align:center;color:var(--muted);font-size:0.8rem;margin-top:48px}
"""

TECHNIQUES = [
  {
    "slug": "ankle-lock",
    "names": {"en":"Ankle Lock","ja":"アンクルロック","pt":"Ankle Lock"},
    "cats": {"en":"Leg Lock","ja":"レッグロック","pt":"Leg Lock"},
    "belts": {"en":"White Belt","ja":"White Belt","pt":"White Belt"},
    "belt_cls": "belt-white",
    "descs": {
      "en": "Learn the straight ankle lock — the first legal leg lock at white belt. Step-by-step entry, finish mechanics, and common defenses.",
      "ja": "ストレートアンクルロックを習得。白帯から使えるファーストレッグロック。エントリー、フィニッシュ、ディフェンスを解説。",
      "pt": "Aprenda o ankle lock — o primeiro leg lock legal na faixa-branca. Entrada, mecânica de finalização e defesas."
    },
    "leads": {
      "en": "The ankle lock (straight ankle lock) is the most fundamental leg lock in Brazilian Jiu-Jitsu — and the only one legal at white belt in most rule sets. Mastering it early gives you a submission threat from guard, half guard, and leg entanglements that most beginners ignore.",
      "ja": "アンクルロック（ストレートアンクルロック）はBJJで最も基本的なレッグロックで、ほとんどのルールセットで白帯から使える唯一のレッグロックです。早期にマスターすることで、多くの初心者が無視するガード、ハーフガード、レッグエンタングルメントからのサブミッション脅威を持てます。",
      "pt": "O ankle lock (straight ankle lock) é o leg lock mais fundamental no BJJ — e o único legal na faixa-branca na maioria dos regulamentos. Dominá-lo cedo dá uma ameaça de finalização da guarda, half guard e entrelaçamentos de pernas."
    },
    "sections": {
      "en": [
        ("Mechanics", [("Foot position","Place the blade of your forearm (ulna bone) across the Achilles tendon — not the ankle bone."),("Body lock","Cradle their leg against your chest: your near arm threads under their calf, your far hand grips your near bicep."),("Finish","Extend your hips forward while pulling their heel toward your chest. The rotation creates torque on the ankle joint — not a yank, a controlled extension.")]),
        ("Key Entries", [("From half guard","When they try to pass, underhook their near leg and fall to the ankle lock position."),("From guard","When they stand to pass, shoot the ankle lock before they establish base."),("From leg entanglement","Any inside-sankaku (inside heel hook control) can transition to ankle lock as a lower-risk option.")]),
        ("Common Mistakes", [("Wrong bone","Using the soft part of the wrist instead of the blade of the forearm — the finish loses all power."),("Pulling the foot","Yanking the foot sideways twists the knee instead of finishing the ankle — illegal and ineffective."),("No hip extension","Arms alone cannot finish the ankle lock. Drive your hips forward simultaneously."),])
      ],
      "ja": [
        ("メカニクス", [("足の位置","前腕の刃（尺骨）をアキレス腱に当てる — 足首の骨ではない。"),("ボディロック","彼らの足を胸に抱える：近い方の腕が脹脛の下を通り、遠い手が近い方の上腕二頭筋を掴む。"),("フィニッシュ","ヒールを胸に引き寄せながらヒップを前方に伸展する。この回転が足首関節にトルクをかける — 引っ張りではなくコントロールされた伸展。")]),
        ("主要エントリー", [("ハーフガードから","相手がパスしようとした時、近い足をアンダーフックしてアンクルロック体勢に落ちる。"),("ガードから","相手が立ち上がってパスしようとする前に、ベースが定まる前にアンクルロックを狙う。"),("レッグエンタングルメントから","インサイドサンカク（インサイドヒールフック）からより低リスクの選択肢としてアンクルロックに移行。")]),
        ("よくあるミス", [("骨の位置","手首の柔らかい部分を使うと力が伝わらない — 前腕の刃を使う。"),("足を引っ張る","横に引っ張ると膝が捻れる — 違法かつ無効。"),("ヒップ伸展なし","腕だけではアンクルロックはフィニッシュできない。ヒップを同時に前方に伸展する。"),])
      ],
      "pt": [
        ("Mecânica", [("Posição do braço","Coloque a lâmina do antebraço (osso ulna) sobre o tendão de Aquiles — não no osso do tornozelo."),("Body lock","Envolva a perna deles contra o peito: braço próximo passa sob a panturrilha, mão distante segura o bíceps próximo."),("Finalização","Estenda os quadris para frente enquanto puxa o calcanhar para o peito. A rotação cria torque na articulação — não uma arrancada, uma extensão controlada.")]),
        ("Principais Entradas", [("Do half guard","Quando tentarem passar, underhooke a perna próxima e caia para a posição de ankle lock."),("Da guarda","Quando ficarem em pé para passar, ataque o ankle lock antes que estabeleçam base."),("Do entrelaçamento","Qualquer inside-sankaku pode transicionar para ankle lock como opção de menor risco.")]),
        ("Erros Comuns", [("Osso errado","Usar a parte mole do pulso em vez da lâmina do antebraço — sem poder."),("Puxar o pé lateralmente","Puxa o joelho e não o tornozelo — ilegal e ineficaz."),("Sem extensão de quadril","Só os braços não finalizam o ankle lock. Empurre os quadris simultaneamente."),])
      ]
    },
    "related": [("heel-hook","Heel Hook"),("knee-bar","Knee Bar"),("half-guard","Half Guard"),("closed-guard","Closed Guard"),("toe-hold","Toe Hold")]
  },
  {
    "slug": "lasso-guard",
    "names": {"en":"Lasso Guard","ja":"ラッソーガード","pt":"Lasso Guard"},
    "cats": {"en":"Guard","ja":"ガード","pt":"Guarda"},
    "belts": {"en":"Blue Belt","ja":"Blue Belt","pt":"Blue Belt"},
    "belt_cls": "belt-blue",
    "descs": {
      "en": "Master the lasso guard in BJJ. Grip configuration, sweeps, triangle entries, and omoplata setups from this powerful grip-dominant guard.",
      "ja": "BJJのラッソーガードを完全攻略。グリップ構成、スイープ、トライアングルとオモプラータへの移行を解説。",
      "pt": "Domine a lasso guard no BJJ. Configuração de grips, raspagens, entradas para triângulo e omoplata."
    },
    "leads": {
      "en": "The lasso guard is a gi-specific guard that uses a rope-like wrap of your arm through the opponent's arm and sleeve grip to create massive control. It's nearly impossible to pass cleanly when well-established, making it a favourite of smaller, flexible grapplers.",
      "ja": "ラッソーガードは、相手の腕にロープのように巻き付くギ専用ガードです。確立されると綺麗にパスするのはほぼ不可能で、小柄で柔軟なグラップラーに人気のガードです。",
      "pt": "A lasso guard é uma guarda específica de gi que usa um enrolamento tipo corda através do braço do adversário para criar controle massivo. Quase impossível de passar quando bem estabelecida."
    },
    "sections": {
      "en": [
        ("Grip Setup", [("Sleeve grip","Grip their sleeve at the wrist with your same-side hand — four fingers inside the sleeve."),("Lasso wrap","Pass your other arm through their arm from the outside, wrapping around like a lasso, and re-grip their sleeve from the inside."),("Foot on hip","Place your lasso-side foot on their hip. The other leg can spider or go to the floor.")]),
        ("Key Sweeps", [("Pendulum sweep","When they posture back, kick your lasso leg across their body and pendulum sweep them over."),("Balloon sweep","Pull their sleeve across your body, plant your foot on their thigh, and push — they balloon over."),("Sit-up sweep","Sit up, underhook their leg, and drive through to top position.")]),
        ("Submission Entries", [("Triangle","When their arm is controlled in the lasso, kick the lasso leg over their shoulder for triangle."),("Omoplata","From lasso, kick your leg over their arm and sit up for the omoplata shoulder lock."),])
      ],
      "ja": [
        ("グリップセットアップ", [("スリーブグリップ","同側の手で相手の袖首を掴む — 4本指を袖の内側に入れる。"),("ラッソー巻き","もう一方の腕を相手の腕の外側から通してラッソーのように巻き付け、内側から袖を再グリップ。"),("足をヒップに","ラッソー側の足を相手のヒップに置く。もう一方の脚はスパイダーにするか床に置く。")]),
        ("主要スイープ", [("ペンデュラムスイープ","相手がポスチャーバックした時、ラッソー脚を身体を横切って振り、ペンデュラムスイープ。"),("バルーンスイープ","相手の袖を身体を横切って引き、太ももに足を当てて押す。"),("シットアップスイープ","起き上がり、相手の脚をアンダーフックしてトップポジションへ。")]),
        ("サブミッションエントリー", [("トライアングル","ラッソーで腕をコントロールしてラッソー脚を肩越しに蹴ってトライアングルへ。"),("オモプラータ","ラッソーから足を相手の腕越しに蹴り出して起き上がりオモプラータへ。"),])
      ],
      "pt": [
        ("Configuração de Grips", [("Grip de manga","Segure a manga no pulso com a mão do mesmo lado — quatro dedos dentro da manga."),("Enrolamento lasso","Passe o outro braço por fora do braço deles, enrolando como um laço, e re-segure a manga por dentro."),("Pé no quadril","Coloque o pé do lado lasso no quadril deles.")]),
        ("Principais Raspagens", [("Pendulum sweep","Quando posturearem para trás, chute a perna lasso através do corpo e faça o pendulum sweep."),("Balloon sweep","Puxe a manga através do corpo, plante o pé na coxa e empurre."),("Sit-up sweep","Sente-se, underhooke a perna e avance para posição por cima.")]),
        ("Entradas para Finalização", [("Triângulo","Com o braço controlado no lasso, chute a perna lasso por cima do ombro para o triângulo."),("Omoplata","Do lasso, chute a perna por cima do braço e sente-se para a omoplata."),])
      ]
    },
    "related": [("spider-guard","Spider Guard"),("de-la-riva-guard","De La Riva Guard"),("closed-guard","Closed Guard"),("triangle-choke","Triangle Choke"),("omoplata","Omoplata")]
  },
  {
    "slug": "50-50-guard",
    "names": {"en":"50/50 Guard","ja":"50/50ガード","pt":"Guarda 50/50"},
    "cats": {"en":"Guard","ja":"ガード","pt":"Guarda"},
    "belts": {"en":"Purple Belt","ja":"Purple Belt","pt":"Purple Belt"},
    "belt_cls": "belt-purple",
    "descs": {
      "en": "Learn the 50/50 guard — the most controversial position in modern BJJ. Heel hook attacks, leg lock entries, and how to avoid the stalemate.",
      "ja": "50/50ガードを習得。現代BJJで最も議論を呼ぶポジション。ヒールフック攻撃、レッグロックエントリー、スタール回避法を解説。",
      "pt": "Aprenda a guarda 50/50 — a posição mais controversa do BJJ moderno. Ataques de heel hook e como evitar o impasse."
    },
    "leads": {
      "en": "The 50/50 guard is a leg entanglement where both athletes have equal leg wraps — hence 50/50. It's the primary position for heel hook attacks in modern no-gi and has revolutionized leg lock systems. Critics call it a stalling position; high-level practitioners use it to systematically hunt heel hooks.",
      "ja": "50/50ガードは、両選手が等しくレッグラップを持つレッグエンタングルメントです。現代ノーギでのヒールフック攻撃の主要ポジションで、レッグロックシステムを革命的に変えました。",
      "pt": "A guarda 50/50 é um entrelaçamento de pernas onde ambos os atletas têm enrolamentos iguais. É a posição primária para ataques de heel hook no no-gi moderno."
    },
    "sections": {
      "en": [
        ("Position Mechanics", [("Entry","Typically entered from outside heel hook position, berimbolo, or when the opponent's leg is between yours."),("Control","Both athletes have the outside heel hook position simultaneously — neither has structural advantage without creating rotation."),("Sweeping","Elevate their outside leg, roll them over your near shoulder to come on top.")]),
        ("Attacks", [("Outside heel hook","Rotate your hips away from them while controlling their heel — the outside heel hook is the primary attack."),("Inside heel hook","When they defend the outside heel hook by straightening their leg, transition to inside heel hook by rolling under."),("Straight ankle lock","If heel hooks are not allowed in competition, the straight ankle lock is the backup finish.")]),
        ("Escaping 50/50", [("Don't hand-fight the leg","Their leg is locked in — work to rotate your body, not fight the entanglement directly."),("The roll-out","When defending heel hook, roll toward their legs — this creates an outside heel hook for you."),])
      ],
      "ja": [
        ("ポジションメカニクス", [("エントリー","通常アウトサイドヒールフックポジション、ベリンボロ、または相手の足が両脚の間にある時に入る。"),("コントロール","両選手が同時にアウトサイドヒールフックポジションを持つ — 回転を生み出さないと構造的優位性はない。"),("スイープ","相手のアウトサイド脚を持ち上げ、近い肩を越えて転がしてトップへ。")]),
        ("攻撃", [("アウトサイドヒールフック","ヒールをコントロールしながらヒップを相手と反対方向に回転させる。"),("インサイドヒールフック","相手が脚を伸ばしてアウトサイドヒールフックを防いだ時、下にロールしてインサイドヒールフックへ移行。"),("ストレートアンクルロック","競技でヒールフックが禁止の場合のバックアップフィニッシュ。")]),
        ("50/50からの脱出", [("足を手で戦わない","足はロックされている — 直接エンタングルメントと戦うのではなく身体を回転させることを優先。"),("ロールアウト","ヒールフックを防ぐ時、相手の足に向かってロールする — これで自分のアウトサイドヒールフックが生まれる。"),])
      ],
      "pt": [
        ("Mecânica da Posição", [("Entrada","Geralmente entrada de posição de outside heel hook, berimbolo, ou quando a perna do adversário está entre as suas."),("Controle","Ambos os atletas têm a posição de outside heel hook simultaneamente — nenhum tem vantagem estrutural sem criar rotação."),("Raspagem","Eleve a perna externa deles, role-os sobre seu ombro próximo para ficar por cima.")]),
        ("Ataques", [("Outside heel hook","Gire os quadris para longe deles controlando o calcanhar — o outside heel hook é o ataque primário."),("Inside heel hook","Quando defenderem endireitando a perna, transite para inside heel hook rolando por baixo."),("Straight ankle lock","Se heel hooks não são permitidos na competição, o ankle lock é o finish reserva.")]),
        ("Escapando do 50/50", [("Não lute contra a perna","Trabalhe para girar seu corpo, não lute o entrelaçamento diretamente."),("O roll-out","Ao defender heel hook, role para as pernas deles — isso cria um outside heel hook para você."),])
      ]
    },
    "related": [("heel-hook","Heel Hook"),("inside-heel-hook","Inside Heel Hook"),("ankle-lock","Ankle Lock"),("berimbolo","Berimbolo"),("de-la-riva-guard","De La Riva Guard")]
  },
  {
    "slug": "shrimp-escape",
    "names": {"en":"Shrimp Escape (Hip Escape)","ja":"シュリンプエスケープ（ヒップエスケープ）","pt":"Shrimp Escape (Fuga de Quadril)"},
    "cats": {"en":"Defense","ja":"ディフェンス","pt":"Defesa"},
    "belts": {"en":"White Belt","ja":"White Belt","pt":"White Belt"},
    "belt_cls": "belt-white",
    "descs": {
      "en": "Master the shrimp escape — the single most important BJJ movement. How to shrimp correctly from side control, mount, and knee-on-belly.",
      "ja": "シュリンプエスケープをマスター — BJJで最も重要な動作。サイドコントロール・マウント・ニーオンベリーからの正しいシュリンプを解説。",
      "pt": "Domine o shrimp escape — o movimento mais importante do BJJ. Como realizar corretamente do side control, montada e joelho na barriga."
    },
    "leads": {
      "en": "The shrimp (hip escape) is the foundational movement of BJJ defense — arguably the single most important drilling exercise in the sport. Every bottom escape — from side control, mount, knee-on-belly — relies on the ability to create hip space through shrimping. Black belts drill it for life.",
      "ja": "シュリンプ（ヒップエスケープ）はBJJディフェンスの基礎動作 — おそらく競技において最も重要なドリルです。サイドコントロール、マウント、ニーオンベリーからのあらゆるボトムエスケープは、シュリンプによるヒップスペース作りに依存しています。",
      "pt": "O shrimp (fuga de quadril) é o movimento fundamental da defesa no BJJ — indiscutivelmente o exercício de drilling mais importante do esporte. Todo escape de baixo depende da capacidade de criar espaço de quadril com o shrimp."
    },
    "sections": {
      "en": [
        ("The Shrimp Movement", [("Starting position","Lie on your back. Feet flat on the mat, arms guarding."),("Bridge phase","Drive one heel into the mat to bridge your hips slightly off the mat — this creates the ability to move."),("Shoot the hips","Shoot your hips sideways (like a shrimp curling) — away from the opponent. Move hips BEFORE your feet chase."),("Reset and repeat","Replace your feet, create the frame, shrimp again. Chain 2-3 shrimps to create guard recovery space.")]),
        ("Shrimp from Side Control", [("Frame first","Forearm on their hip, other hand frames their collar/neck. Create distance before shrimping."),("Shrimp direction","Shrimp away from them, not toward them — you want to put your knee between you and them."),("Recover guard","Once your knee is in, push their hip and recover half or full guard.")]),
        ("Shrimp from Mount", [("Create the frame","Never cross your arms — frame with one forearm on hip, one on chest."),("Shrimp sideways","Shrimp your hips out to one side, bringing the knee up across their hips."),("Half guard","Trap their leg in half guard and continue working guard recovery.")]),
        ("Drilling Tips", [("Drill daily","5 minutes of shrimping down the mat and back is the highest-value BJJ warm-up drill that exists."),("Hip height","Your hips should travel sideways, not just up and down. Aim to move 6 inches per shrimp."),])
      ],
      "ja": [
        ("シュリンプの動作", [("スタートポジション","仰向けになる。足を床に平らに置き、腕でガード。"),("ブリッジフェーズ","片方のカカトを床に押し込んでヒップを軽く浮かせる — これが移動を可能にする。"),("ヒップを射出","エビのように横にヒップを射出する — 相手と反対方向へ。足よりもヒップを先に動かす。"),("リセットして繰り返す","足を戻してフレームを作り、再度シュリンプ。ガード回復スペースを作るために2〜3回繰り返す。")]),
        ("サイドコントロールからのシュリンプ", [("先にフレーム","前腕を相手のヒップに、もう一方の手でカラー/ネックをフレーム。シュリンプ前にスペースを作る。"),("シュリンプの方向","相手から離れる方向にシュリンプ — 相手との間に膝を入れたい。"),("ガード回復","膝が入ったら相手のヒップを押してハーフまたはフルガードを回復。")]),
        ("マウントからのシュリンプ", [("フレームを作る","腕を交差させない — 片方の前腕をヒップに、もう一方を胸にフレーム。"),("横にシュリンプ","ヒップを横にシュリンプして膝を相手のヒップ越しに上げる。"),("ハーフガード","ハーフガードで相手の足をトラップしてガード回復を継続。")]),
        ("ドリルのコツ", [("毎日ドリル","マットを往復する5分のシュリンプドリルは存在する最高価値のBJJウォームアップ。"),("ヒップの高さ","ヒップは上下だけでなく横方向に移動すべき。1回のシュリンプで約15cm移動を目指す。"),])
      ],
      "pt": [
        ("O Movimento Shrimp", [("Posição inicial","Deite de costas. Pés planos no tatame, braços guardando."),("Fase ponte","Empurre um calcanhar no tatame para elevar levemente os quadris — isso cria a capacidade de mover."),("Projete os quadris","Projete os quadris para o lado (como um camarão se curvando) — para longe do adversário. Mova os quadris ANTES dos pés."),("Reset e repita","Recoloque os pés, crie o frame, shrimp novamente. Encadeie 2-3 shrimps para criar espaço de recuperação de guarda.")]),
        ("Shrimp do Side Control", [("Frame primeiro","Antebraço no quadril deles, outra mão faz frame no colarinho/pescoço. Crie distância antes de fazer shrimp."),("Direção do shrimp","Shrimp para longe deles, não em direção — você quer colocar o joelho entre vocês dois."),("Recuperar guarda","Com o joelho dentro, empurre o quadril e recupere half ou full guard.")]),
        ("Shrimp da Montada", [("Crie o frame","Nunca cruze os braços — frame com um antebraço no quadril, um no peito."),("Shrimp para o lado","Projete os quadris para um lado, trazendo o joelho pelos quadris deles."),("Half guard","Prenda a perna no half guard e continue trabalhando a recuperação de guarda.")]),
        ("Dicas de Drilling", [("Drill diário","5 minutos de shrimp pelo tatame é o drill de aquecimento de maior valor no BJJ."),("Altura dos quadris","Seus quadris devem viajar para os lados, não apenas para cima e baixo."),])
      ]
    },
    "related": [("mount-escape","Mount Escape"),("closed-guard","Closed Guard"),("half-guard","Half Guard"),("side-control","Side Control"),("bridge-and-roll","Bridge & Roll")]
  },
  {
    "slug": "arm-drag",
    "names": {"en":"Arm Drag","ja":"アームドラッグ","pt":"Arm Drag"},
    "cats": {"en":"Takedown","ja":"テイクダウン","pt":"Queda"},
    "belts": {"en":"Blue Belt","ja":"Blue Belt","pt":"Blue Belt"},
    "belt_cls": "belt-blue",
    "descs": {
      "en": "Master the arm drag — the most versatile setups in wrestling and BJJ. Back takes, double leg setups, and mat returns from standing and seated positions.",
      "ja": "アームドラッグをマスター — レスリングとBJJで最も汎用性の高いセットアップ。バックテイク、ダブルレッグ、マットリターンを解説。",
      "pt": "Domine o arm drag — o setup mais versátil no wrestling e BJJ. Back takes, setups para double leg e retornos ao tatame."
    },
    "leads": {
      "en": "The arm drag is one of the most valuable offensive tools in grappling — a simple pull of the opponent's arm that instantly turns their back to you. Used from standing, seated guard, and butterfly guard, it's a staple of Marcelo Garcia's world-class game and works at every level from beginner to black belt.",
      "ja": "アームドラッグはグラップリングで最も価値のある攻撃ツールの一つです — 相手の腕を引っ張るだけで即座に背中を向けさせます。スタンド、シーテッドガード、バタフライガードから使え、Marcelo Garciaのゲームの定番で、初心者から黒帯まで使える技です。",
      "pt": "O arm drag é uma das ferramentas ofensivas mais valiosas no grappling — um simples puxão do braço do adversário que instantaneamente vira as costas para você. Usado em pé, da guarda sentada e butterfly guard."
    },
    "sections": {
      "en": [
        ("The Arm Drag Mechanics", [("Grip","Grip their wrist with one hand, their tricep/upper arm with the other."),("Pull and step","Pull their arm across your body sharply — simultaneously step to the outside with your same-side leg."),("Back position","They are now turned away from you — take the back or shoot the double leg.")]),
        ("From Standing", [("Collar tie to arm drag","From collar-and-elbow tie, fake the level change, then snap the arm drag to their back."),("Arm drag double leg","After the arm drag, when they turn back to face you, they leave the far leg exposed — shoot double."),]),
        ("From Seated / Butterfly Guard", [("Seated guard arm drag","Sit upright, control their wrist and tricep, and pull the arm drag — come to their back side for back take or rear mount."),("Butterfly guard entry","From butterfly, arm drag when they post forward — dive under for butterfly hook and sweep or back take."),]),
        ("Common Mistakes", [("Half-hearted pull","The arm drag must be sharp and committed — a weak pull gives them time to react and spin to face you."),("Losing the wrist","Release the wrist immediately after the drag and use that hand to go for the back — two-on-one to back is the chain."),])
      ],
      "ja": [
        ("アームドラッグのメカニクス", [("グリップ","片手で手首を掴み、もう一方で上腕三頭筋/上腕を掴む。"),("引っ張りとステップ","腕を身体を横切って鋭く引っ張る — 同時に同側の足を外側にステップ。"),("バックポジション","相手は今あなたから背を向けた状態 — バックを取るかダブルレッグを狙う。")]),
        ("スタンドから", [("カラータイからアームドラッグ","カラー＆エルボータイからレベルチェンジをフェイントし、アームドラッグで背中へ。"),("アームドラッグダブルレッグ","アームドラッグ後、相手が向き直ろうとすると遠い足が露出する — ダブルを狙う。"),]),
        ("シーテッド/バタフライガードから", [("シーテッドガードアームドラッグ","直立し、手首と上腕三頭筋をコントロール。アームドラッグを引いて背中側へ移動しバックテイク。"),("バタフライガードエントリー","バタフライから相手が前傾みになった時アームドラッグ — バタフライフックに潜り込んでスイープかバックテイク。"),]),
        ("よくあるミス", [("中途半端な引っ張り","アームドラッグは鋭くコミットしたものでなければ — 弱い引っ張りだと相手が反応して向き直る時間を与える。"),("手首を離す","ドラッグ後すぐに手首を離してその手でバックを狙う — 2オン1からバックへの連鎖。"),])
      ],
      "pt": [
        ("Mecânica do Arm Drag", [("Grip","Segure o pulso com uma mão, o trícep/parte superior do braço com a outra."),("Puxar e passar","Puxe o braço através do seu corpo de forma abrupta — simultaneamente passe para o lado externo com a perna do mesmo lado."),("Posição de costas","Eles agora estão de costas para você — pegue as costas ou ataque o double leg.")]),
        ("Em Pé", [("Collar tie para arm drag","Do collar-and-elbow tie, finja o level change, então aplique o arm drag para as costas."),("Arm drag double leg","Após o arm drag, quando girarem para enfrentar, deixam a perna distante exposta — ataque double leg."),]),
        ("Da Guarda Sentada / Butterfly", [("Arm drag da guarda sentada","Sente ereto, controle pulso e trícep, puxe arm drag — vá para o lado das costas para back take."),("Entrada pelo butterfly","Do butterfly, arm drag quando postarem para frente — mergulhe sob para o gancho de butterfly e raspe ou pegue as costas."),]),
        ("Erros Comuns", [("Puxão hesitante","O arm drag deve ser abrupto e comprometido — um puxão fraco dá tempo para reagirem."),("Perder o pulso","Solte o pulso imediatamente após o drag e use essa mão para ir para as costas."),])
      ]
    },
    "related": [("double-leg-takedown","Double Leg Takedown"),("ankle-pick","Ankle Pick"),("butterfly-guard","Butterfly Guard"),("back-mount","Back Mount"),("backtake","Back Take")]
  },
  {
    "slug": "bridge-and-roll",
    "names": {"en":"Bridge and Roll (Upa Escape)","ja":"ブリッジアンドロール（ウパエスケープ）","pt":"Bridge and Roll (Escape Upa)"},
    "cats": {"en":"Defense","ja":"ディフェンス","pt":"Defesa"},
    "belts": {"en":"White Belt","ja":"White Belt","pt":"White Belt"},
    "belt_cls": "belt-white",
    "descs": {
      "en": "Learn the bridge and roll (upa) escape from full mount — the first and most essential mount escape in BJJ. Step-by-step mechanics, timing, and variations.",
      "ja": "フルマウントからのブリッジアンドロール（ウパ）脱出を習得 — BJJで最初かつ最も重要なマウントエスケープ。",
      "pt": "Aprenda o bridge and roll (upa) do full mount — o primeiro e mais essencial escape de montada no BJJ."
    },
    "leads": {
      "en": "The bridge and roll (also called the upa escape or trap-and-roll) is the first mount escape taught in virtually every BJJ curriculum. It exploits a simple physics principle: when your opponent is off-balance, a powerful bridge can flip them over. Master the timing and you can escape mount even against much heavier opponents.",
      "ja": "ブリッジアンドロール（ウパエスケープまたはトラップアンドロールとも呼ばれる）は、ほぼすべてのBJJカリキュラムで最初に教えられるマウントエスケープです。シンプルな物理の原理を利用しています：相手がバランスを崩しているとき、強力なブリッジで転がすことができます。",
      "pt": "O bridge and roll (também chamado de upa escape ou trap-and-roll) é o primeiro escape de montada ensinado em praticamente todo currículo de BJJ. Explora um princípio físico simples: quando o adversário está desequilibrado, uma ponte poderosa pode virá-lo."
    },
    "sections": {
      "en": [
        ("Step-by-Step Execution", [("Trap the arm","When your opponent posts or reaches for a collar grip, grab their same-side wrist with both hands and pin it against your chest."),("Trap the leg","Wrap the same-side leg over their ankle with your own leg — you've now trapped arm and leg on one side."),("Plant your foot","Place your free foot flat on the mat close to your body to give your bridge maximum power."),("Bridge and roll","Simultaneously bridge your hips explosively while turning toward the trapped side. The combination of trapped arm+leg means they cannot post and must roll."),("Land in guard","Come down into their guard. Immediately work to pass.")]),
        ("Timing is Everything", [("Wait for the post","The bridge works when they are off-balance — reaching for collar grips, posting sideways, or adjusting position."),("Don't rush","A premature bridge against a balanced opponent just creates a rocking motion and exhausts you."),("Use head movement","Turn your head strongly in the direction of the roll to add rotational force.")]),
        ("Variations", [("Low mount upa","When they are in low mount, move your hips to the side, trap arm and leg, bridge toward their trapped arm side."),("High mount upa","When they ride high, their legs come forward — bridge more explosively and aim to get your near leg across their hip."),])
      ],
      "ja": [
        ("ステップバイステップの実行", [("腕のトラップ","相手がポストするか襟を掴みに来た時、同側の手首を両手で掴んで胸に固定する。"),("脚のトラップ","同側の足首に自分の脚を巻き付ける — 片側の腕と脚をトラップした。"),("足を立てる","自由な方の足を身体の近くに立てて最大のブリッジパワーを生み出す。"),("ブリッジアンドロール","ヒップを爆発的にブリッジしながらトラップ側に向かって回転する。腕+脚のトラップにより相手はポストできず転がる。"),("ガードに着地","相手のガードに降りる。即座にパスを狙う。")]),
        ("タイミングが全て", [("ポストを待つ","ブリッジが効くのは相手がバランスを崩している時 — 襟グリップを狙う時、横にポストする時、ポジション調整中。"),("急がない","バランスの取れた相手への早まったブリッジは揺れを生み出すだけ。"),("頭の動き","ロール方向に頭を強く向けて回転力を加える。")]),
        ("バリエーション", [("ローマウントウパ","ローマウントの時、ヒップを横にずらして腕と脚をトラップし、トラップした腕側に向かってブリッジ。"),("ハイマウントウパ","相手が高く乗っている時、爆発的にブリッジして近い方の脚を相手のヒップ越しに目指す。"),])
      ],
      "pt": [
        ("Execução Passo a Passo", [("Prenda o braço","Quando postarem ou alcançarem o grip de gola, pegue o pulso do mesmo lado com ambas as mãos e prenda contra o peito."),("Prenda a perna","Envolva a perna do mesmo lado sobre o tornozelo deles com sua própria perna — você prendeu braço e perna de um lado."),("Plante o pé","Coloque o pé livre plano no tatame próximo ao corpo para dar à ponte o máximo de potência."),("Bridge and roll","Simultaneamente faça a ponte com os quadris explosivamente enquanto gira para o lado preso. Braço+perna presos significa que não podem postar e devem rolar."),("Aterrissar na guarda","Desça para a guarda deles. Trabalhe imediatamente a passagem.")]),
        ("Timing é Tudo", [("Espere o post","A ponte funciona quando estão desequilibrados — alcançando grips de gola, postando lateralmente."),("Não se apresse","Uma ponte prematura contra um adversário equilibrado cria apenas um balanço."),("Use o movimento da cabeça","Gire a cabeça fortemente na direção do rolamento para adicionar força rotacional.")]),
        ("Variações", [("Upa da montada baixa","Na montada baixa, mova os quadris para o lado, prenda braço e perna, faça ponte para o lado do braço preso."),("Upa da montada alta","Na montada alta, seja mais explosivo e tente passar a perna próxima pelo quadril deles."),])
      ]
    },
    "related": [("mount-escape","Mount Escape"),("closed-guard","Closed Guard"),("side-control","Side Control"),("shrimp-escape","Shrimp Escape"),("half-guard","Half Guard")]
  },
  {
    "slug": "harai-goshi",
    "names": {"en":"Harai Goshi (Sweeping Hip Throw)","ja":"払腰（ハライゴシ）","pt":"Harai Goshi (Golpe de Quadril)"},
    "cats": {"en":"Takedown","ja":"テイクダウン","pt":"Queda"},
    "belts": {"en":"Blue Belt","ja":"Blue Belt","pt":"Blue Belt"},
    "belt_cls": "belt-blue",
    "descs": {
      "en": "Learn harai goshi — the sweeping hip throw from judo and BJJ. Entry mechanics, kuzushi, and how to finish to top position for BJJ scoring.",
      "ja": "払腰を習得 — 柔道とBJJの払い腰投げ。崩し、エントリー、BJJのスコアリングのためのフィニッシュを解説。",
      "pt": "Aprenda harai goshi — o golpe de varredura de quadril do judô e BJJ. Entrada, kuzushi e como finalizar para pontuação no BJJ."
    },
    "leads": {
      "en": "Harai goshi (払腰, sweeping hip throw) is a classical judo throw that has found a powerful home in BJJ competition. It uses hip rotation and a leg sweep to throw the opponent in a large arc onto their back. When executed correctly, it scores 2 points (or ippon in judo) and puts you in top position for the ground game.",
      "ja": "払腰は古典的な柔道投げ技で、BJJ競技においても強力な技として定着しています。腰の回転と足の払いで相手を大きな弧を描いて投げます。正しく実行されると2ポイント（柔道では一本）を獲得し、グラウンドゲームでトップポジションを取れます。",
      "pt": "Harai goshi (払腰, golpe de varredura de quadril) é um arremesso clássico do judô que encontrou um lugar poderoso na competição de BJJ. Usa rotação de quadril e uma varredura de perna para arremessar o adversário em um grande arco."
    },
    "sections": {
      "en": [
        ("Execution", [("Grip","Standard judo grip: one hand on their collar, one sleeve grip at the elbow — or same-side collar tie and underhook in no-gi."),("Kuzushi (break balance)","Pull them forward and to your right (for right-side harai) — break their balance forward BEFORE turning."),("Entry (tsukuri)","Pivot on your left foot, bring your right foot in front of their legs, and rotate your hips across their hip line."),("Sweep (kake)","Sweep your right leg backward and through theirs in a large arc while pulling them forward and over your hip."),("Follow down","Stay connected and follow them to the ground — land in side control or mount.")]),
        ("Key Points", [("Hip height","Your hip must be lower than theirs at the moment of entry — if your hip is too high, the throw stalls."),("Kuzushi first","No kuzushi = no throw. Breaking forward balance is non-negotiable."),("Continuous pull","Your gripping hands must maintain forward pull throughout the entire throw, not just at the start.")]),
        ("BJJ-Specific Notes", [("Guard pull threat","Harai goshi is most effective when the opponent fears your double leg — the threat creates the kuzushi you need."),("Follow to ground","Unlike judo, in BJJ you must follow the throw to the mat to score 2 points and establish position."),])
      ],
      "ja": [
        ("実行", [("グリップ","標準的な柔道グリップ：片手で襟、もう一方で肘の袖 — ノーギではカラータイとアンダーフック。"),("崩し","前方と右に引く（右払腰の場合） — 回転する前に前方の崩しが不可欠。"),("体捌き（作り）","左足を軸に回転し、右足を相手の足の前に持ち込んで腰を相手の腰ラインを横切らせる。"),("払い（掛け）","右足を後方に払いながら引き込み、腰越しに大きな弧を描かせる。"),("フォローダウン","連結を保って一緒に地面に降りる — サイドコントロールかマウントに着地。")]),
        ("重要ポイント", [("腰の高さ","エントリーの瞬間、自分の腰が相手より低くなければならない。"),("崩しが先","崩しなし = 投げなし。前方の崩しは必須。"),("継続的な引き","グリップの引きは投げの間中ず持続しなければならない。")]),
        ("BJJ特有の注意点", [("ガードプルの脅威","払腰はダブルレッグを恐れている相手に最も効果的 — 脅威が必要な崩しを生み出す。"),("地面までフォロー","柔道と異なり、BJJでは2ポイント獲得とポジション確立のため投げた後も地面についていく必要がある。"),])
      ],
      "pt": [
        ("Execução", [("Grip","Grip padrão de judô: uma mão no colarinho, uma manga no cotovelo — no no-gi, collar tie e underhook."),("Kuzushi (quebrar o equilíbrio)","Puxe para frente e para a direita (harai direito) — quebre o equilíbrio ANTES de girar."),("Entrada (tsukuri)","Gire no pé esquerdo, traga o pé direito à frente das pernas deles, e gire os quadris pela linha de quadril deles."),("Varredura (kake)","Varra a perna direita para trás e através da deles em um grande arco enquanto puxa para frente e sobre o quadril."),("Siga ao chão","Mantenha a conexão e siga ao chão — aterrisse no side control ou montada.")]),
        ("Pontos Chave", [("Altura do quadril","Seu quadril deve estar mais baixo que o deles no momento da entrada."),("Kuzushi primeiro","Sem kuzushi = sem arremesso. Quebrar o equilíbrio para frente é inegociável."),("Puxão contínuo","As mãos devem manter o puxão para frente durante todo o arremesso.")]),
        ("Notas Específicas de BJJ", [("Ameaça de puxada de guarda","Harai goshi é mais eficaz quando o adversário teme seu double leg — a ameaça cria o kuzushi necessário."),("Siga ao chão","No BJJ, você deve seguir o arremesso ao tatame para marcar 2 pontos e estabelecer posição."),])
      ]
    },
    "related": [("double-leg-takedown","Double Leg Takedown"),("ankle-pick","Ankle Pick"),("ippon-seoi-nage","Ippon Seoi Nage"),("closed-guard","Closed Guard"),("side-control","Side Control")]
  },
  {
    "slug": "ippon-seoi-nage",
    "names": {"en":"Ippon Seoi Nage (One-Arm Shoulder Throw)","ja":"一本背負投（イッポンセオイナゲ）","pt":"Ippon Seoi Nage (Arremesso de Ombro)"},
    "cats": {"en":"Takedown","ja":"テイクダウン","pt":"Queda"},
    "belts": {"en":"Blue Belt","ja":"Blue Belt","pt":"Blue Belt"},
    "belt_cls": "belt-blue",
    "descs": {
      "en": "Master ippon seoi nage — the explosive one-arm shoulder throw used in judo and BJJ. Setup, entry mechanics, and adapting for BJJ competition.",
      "ja": "一本背負投を習得 — 柔道とBJJで使われる爆発的な片腕肩投げ。セットアップ、エントリー、BJJ競技への適応を解説。",
      "pt": "Domine o ippon seoi nage — o explosivo arremesso de ombro de um braço usado no judô e BJJ."
    },
    "leads": {
      "en": "Ippon seoi nage (一本背負投, one-arm shoulder throw) is one of the most spectacular throws in judo — and a powerful scoring weapon in BJJ competition. By trapping the opponent's arm and loading them onto your back, you can throw much heavier opponents using leverage and hip rotation rather than raw strength.",
      "ja": "一本背負投は柔道で最も華やかな投げ技の一つであり、BJJ競技においても強力な得点技です。相手の腕をトラップして背中に担ぐことで、純粋な力ではなくレバレッジと腰の回転で体格差のある相手を投げることができます。",
      "pt": "Ippon seoi nage (一本背負投) é um dos arremessos mais espetaculares do judô — e uma arma de pontuação poderosa na competição de BJJ."
    },
    "sections": {
      "en": [
        ("Execution", [("Grip","Grip their sleeve at the elbow with your same-side hand (thumb inside). Your other hand grips their collar or lapel."),("Entry","Pivot sharply on the ball of your foot, turn to face the same direction as them, and drive your throwing arm under their armpit — your elbow bends and traps their arm."),("Load","Bend your knees deeply (lower than their hips), press your back against their chest, and pull their arm tight over your shoulder."),("Throw","Straighten your legs explosively, project your hips backward, and pull their arm down in front of you — they fly over your shoulder.")]),
        ("Kuzushi for Seoi Nage", [("Push-pull kuzushi","Push their elbow up and across while pulling their collar forward and down — this off-balances them for the entry."),("Against the push","When they push into you defensively, use their energy: step in with the seoi nage as they push, adding their force to your throw.")]),
        ("BJJ Considerations", [("Follow to guard","Unlike judo, follow the throw to the ground. Land beside them in side control."),("Arm exposure risk","The entry exposes your back briefly — drill the entry speed to minimize exposure time."),])
      ],
      "ja": [
        ("実行", [("グリップ","同側の手で肘の袖を掴む（親指を内側に）。もう一方の手で襟または前帯を掴む。"),("エントリー","足の母趾球で鋭く回転し、相手と同じ方向を向き、投げる腕を脇の下に差し込む — 肘を曲げて腕をトラップ。"),("担ぎ","膝を深く曲げ（相手の腰より低く）、背中を胸に押し付け、腕を肩越しに引き寄せる。"),("投げ","爆発的に脚を伸ばし、ヒップを後方に突き出し、腕を前方下方に引く — 相手は肩越しに飛ぶ。")]),
        ("一本背負投のための崩し", [("押し引き崩し","肘を上に、そして横に押しながら、襟を前方下方に引く — エントリーのために崩す。"),("押し返しに対して","相手が防御的に押してきた時、その力を利用して一本背負投に入る。")]),
        ("BJJの考慮事項", [("ガードに着地","柔道と異なり、投げた後も地面についていく。サイドコントロールで横に着地。"),("腕の露出リスク","エントリー中一瞬背中が露出する — 露出時間を最小化するためエントリー速度をドリルする。"),])
      ],
      "pt": [
        ("Execução", [("Grip","Segure a manga no cotovelo com a mão do mesmo lado (polegar dentro). A outra mão segura o colarinho."),("Entrada","Gire na ponta do pé, vire para a mesma direção que eles, e passe o braço de arremesso sob a axila deles — cotovelo dobrado prende o braço."),("Carregar","Dobre os joelhos profundamente, pressione as costas contra o peito deles, puxe o braço apertado sobre o ombro."),("Arremesso","Endireite as pernas explosivamente, projete os quadris para trás, puxe o braço para baixo na frente — voam sobre o ombro.")]),
        ("Kuzushi para Seoi Nage", [("Kuzushi empurra-puxa","Empurre o cotovelo para cima e através enquanto puxa o colarinho para frente e baixo."),("Contra o empurrão","Quando empurrarem defensivamente, use a energia deles: entre com o seoi nage enquanto empurram."),]),
        ("Considerações BJJ", [("Siga para o chão","Diferente do judô, siga o arremesso ao chão. Aterrissse no side control."),("Risco de exposição do braço","A entrada expõe as costas brevemente — drille a velocidade de entrada para minimizar."),])
      ]
    },
    "related": [("harai-goshi","Harai Goshi"),("double-leg-takedown","Double Leg Takedown"),("ankle-pick","Ankle Pick"),("side-control","Side Control"),("closed-guard","Closed Guard")]
  },
  {
    "slug": "snap-down",
    "names": {"en":"Snap Down (Neck Snap)","ja":"スナップダウン（ネックスナップ）","pt":"Snap Down"},
    "cats": {"en":"Takedown","ja":"テイクダウン","pt":"Queda"},
    "belts": {"en":"White Belt","ja":"White Belt","pt":"White Belt"},
    "belt_cls": "belt-white",
    "descs": {
      "en": "Learn the snap down — the most effective wrestling setup in BJJ and MMA. Pull the opponent's head down to expose the back or set up the double leg.",
      "ja": "スナップダウンを習得 — BJJとMMAで最も効果的なレスリングセットアップ。相手の頭を引き下げてバック露出やダブルレッグセットアップを作る。",
      "pt": "Aprenda o snap down — o setup de wrestling mais eficaz no BJJ e MMA. Puxe a cabeça do adversário para baixo para expor as costas ou configurar o double leg."
    },
    "leads": {
      "en": "The snap down (also called neck snap or head snap) is one of the highest-percentage wrestling setups in BJJ and MMA. By snapping the opponent's head and posture forward, you create a scramble that exposes their back, sets up the double leg, or creates a front headlock. It requires minimal strength and works against any size opponent.",
      "ja": "スナップダウン（ネックスナップまたはヘッドスナップとも呼ばれる）は、BJJとMMAで最も高確率なレスリングセットアップの一つです。相手の頭とポスチャーを前方にスナップすることで、背中露出、ダブルレッグ、フロントヘッドロックを生み出すスクランブルを作れます。",
      "pt": "O snap down (também chamado de neck snap) é um dos setups de wrestling de maior percentagem no BJJ e MMA. Ao fazer snap da cabeça do adversário para frente, você cria um scramble que expõe as costas ou configura o double leg."
    },
    "sections": {
      "en": [
        ("Execution", [("Grip the head","Collar tie: cup the back of their head with one hand, the other grips their same-side elbow."),("Snap timing","When they posture up or push into you, use that energy — snap their head sharply downward and forward with your collar tie hand."),("Follow the snap","As their head goes down, they expose their back: step to the side and take the back, or circle and shoot the double leg.")]),
        ("Key Setups", [("Against the pushout","When they try to push you back to create space, redirect their energy: snap the head as they push."),("From collar-and-elbow","Standard wrestling collar tie — snap when they go flat-footed or lift their head."),("Repeated snaps","Multiple snaps tire the opponent's neck and make them defensive, opening up level changes and shots.")]),
        ("What to Do After the Snap", [("Back take","Step behind them, get the seatbelt grip, take back."),("Double leg","Snap sends their head down, shoot the double leg on the exposed legs."),("Front headlock","Catch their head in a front headlock and transition to a guillotine or go to the mat."),])
      ],
      "ja": [
        ("実行", [("頭のグリップ","カラータイ：片手で後頭部をカップし、もう一方で同側の肘を掴む。"),("スナップのタイミング","相手がポスチャーアップまたは押してきた時、その力を利用 — カラータイの手で頭を鋭く下前方にスナップ。"),("スナップをフォロー","頭が下がった時、相手の背中が露出する：横にステップしてバックを取るか、回り込んでダブルレッグを狙う。")]),
        ("主要セットアップ", [("プッシュアウトに対して","スペースを作ろうと押してきた時、エネルギーをリダイレクト：押してきた瞬間に頭をスナップ。"),("カラー＆エルボーから","標準的なレスリングカラータイ — フラットフットになるか頭を上げた時にスナップ。"),("連続スナップ","複数回のスナップは相手の首を疲れさせ、レベルチェンジやショットのチャンスを開く。")]),
        ("スナップ後の選択", [("バックテイク","後ろにステップしてシートベルトグリップでバックを取る。"),("ダブルレッグ","スナップで頭が下がり、露出した足にダブルレッグを狙う。"),("フロントヘッドロック","頭をフロントヘッドロックでキャッチしてギロチンへ移行するかマットへ。"),])
      ],
      "pt": [
        ("Execução", [("Segure a cabeça","Collar tie: envolva a nuca com uma mão, a outra segura o cotovelo do mesmo lado."),("Timing do snap","Quando posturearem ou empurrarem, use essa energia — faça snap da cabeça abrupta para baixo e frente."),("Siga o snap","Com a cabeça abaixada, as costas ficam expostas: passe para o lado e pegue as costas, ou gire e ataque o double leg.")]),
        ("Principais Setups", [("Contra o empurrão","Quando tentarem empurrá-lo para criar espaço, redirecione a energia: snap quando empurram."),("Do collar-and-elbow","Collar tie padrão de wrestling — snap quando ficam flat-footed ou levantam a cabeça."),("Snaps repetidos","Múltiplos snaps cansam o pescoço do adversário e o tornam defensivo.")]),
        ("O Que Fazer Após o Snap", [("Back take","Passe para trás, consiga o grip seatbelt, pegue as costas."),("Double leg","O snap manda a cabeça para baixo, ataque o double leg nas pernas expostas."),("Front headlock","Pegue a cabeça em front headlock e transite para guilhotina ou vá ao tatame."),])
      ]
    },
    "related": [("double-leg-takedown","Double Leg Takedown"),("ankle-pick","Ankle Pick"),("harai-goshi","Harai Goshi"),("back-mount","Back Mount"),("guillotine-choke","Guillotine Choke")]
  },
  {
    "slug": "estima-lock",
    "names": {"en":"Estima Lock (Foot Lock Variation)","ja":"エスティマロック（フットロックバリエーション）","pt":"Estima Lock"},
    "cats": {"en":"Leg Lock","ja":"レッグロック","pt":"Leg Lock"},
    "belts": {"en":"Purple Belt","ja":"Purple Belt","pt":"Purple Belt"},
    "belt_cls": "belt-purple",
    "descs": {
      "en": "Learn the Estima lock — the sneaky foot lock hidden in guard passing. Named after Braulio Estima, this submission catches passers off-guard.",
      "ja": "エスティマロックを習得 — ガードパス中に隠れた抜け目ないフットロック。Braulio Estimaの名を冠したこのサブミッションは相手のパスを利用する。",
      "pt": "Aprenda o Estima lock — o foot lock furtivo escondido na passagem de guarda. Nomeado em homenagem a Braulio Estima."
    },
    "leads": {
      "en": "The Estima lock is a sneaky foot lock submission named after Braulio Estima, a multiple world and ADCC champion who used it to defeat Marcelo Garcia at ADCC 2009. What makes it unique: it attacks the foot of someone who is passing your guard — turning their offensive action into a submission trap.",
      "ja": "エスティマロックは、Braulio Estima（BJJ世界&ADCC複数回チャンピオン）の名を冠した抜け目ないフットロックです。2009年ADCCでMarcelo Garciaを破った際に使用しました。ユニークな点：ガードをパスしようとしている相手の足を攻撃 — 相手の攻撃的な動きをサブミッションの罠に変える。",
      "pt": "O Estima lock é um foot lock furtivo nomeado em homenagem a Braulio Estima, múltiplo campeão mundial e do ADCC, que o usou para derrotar Marcelo Garcia no ADCC 2009."
    },
    "sections": {
      "en": [
        ("How It Works", [("Opportunity","The Estima lock appears when your opponent steps their foot forward into your guard space while passing — typically in a toreando or leg-drag pass."),("Trap the foot","Catch their stepping foot by hooking your arm over their shin, trapping the foot against your body. Their toes should point upward."),("Finish","Extend your hips forward while rotating the trapped foot — creates a rotational toe/foot lock. Tap comes fast.")]),
        ("When to Hunt It", [("Toreando pass","Classic entry — as they grip your pants to toreando, their foot is vulnerable as they step."),("Knee slice","As they push your knee to slice, step their leg into the lock position."),("Any forward step","Any time they step a foot forward between your legs, the Estima lock is available.")]),
        ("Legal Status", [("IBJJF","The Estima lock is legal at brown and black belt in gi. Check current rules before competition."),("No-gi submission only","In no-gi, similar footlocks may have different classifications — always check the ruleset."),])
      ],
      "ja": [
        ("仕組み", [("チャンス","エスティマロックは、相手がパス中にガードスペースに足を前進させた時に現れる — 通常はトレアナパスやレッグドラッグパス時。"),("足のトラップ","腕を脛越しにフックして、踏み込んだ足を体に固定してキャッチする。爪先は上を向くべき。"),("フィニッシュ","トラップした足を回転させながらヒップを前方に伸展する — 回転トゥ/フットロックを生み出す。タップは早く来る。")]),
        ("狙うタイミング", [("トレアナパス","定番エントリー — ズボンをグリップしてトレアナする際、ステップする足が弱点になる。"),("ニースライス","膝を押してスライスしようとする際、その足をロックポジションに誘導する。"),("いかなる前進ステップも","両足の間に足を前進させた時はいつでもエスティマロックは使える。")]),
        ("合法性", [("IBJJF","エスティマロックはギの茶帯・黒帯で合法。競技前に現行ルールを確認すること。"),("ノーギ","ノーギでは類似フットロックが異なる分類になる場合がある — 常にルールセットを確認。"),])
      ],
      "pt": [
        ("Como Funciona", [("Oportunidade","O Estima lock aparece quando o adversário avança o pé para o espaço da guarda durante a passagem — tipicamente no toreando ou leg-drag."),("Prenda o pé","Pegue o pé avançado hookeando o braço sobre a canela, prendendo o pé contra o corpo. Os dedos devem apontar para cima."),("Finalização","Estenda os quadris para frente enquanto rotaciona o pé preso — cria um toe/foot lock rotacional. O tap vem rápido.")]),
        ("Quando Caçar", [("Passagem toreando","Entrada clássica — enquanto seguram as calças para o toreando, o pé é vulnerável ao avançar."),("Knee slice","Enquanto empurram o joelho para o slice, leve a perna deles para a posição de lock."),("Qualquer passo para frente","A qualquer momento que avancem um pé entre suas pernas, o Estima lock está disponível.")]),
        ("Status Legal", [("IBJJF","O Estima lock é legal na faixa-marrom e preta no gi. Verifique as regras atuais antes da competição."),("No-gi","No no-gi, footlocks similares podem ter classificações diferentes — sempre verifique o regulamento."),])
      ]
    },
    "related": [("ankle-lock","Ankle Lock"),("heel-hook","Heel Hook"),("toe-hold","Toe Hold"),("closed-guard","Closed Guard"),("half-guard","Half Guard")]
  },
]

BELT_CLASS = {"White Belt":"belt-white","Blue Belt":"belt-blue","Purple Belt":"belt-purple","Brown Belt":"belt-brown","Black Belt":"belt-black"}

LANG_UI = {
    "en": {"home":"Home","techniques":"All Techniques","skill":"Skill Tree","sim":"Simulator",
           "related":"Related Techniques","aff_title":"Master this technique with world-class instruction",
           "aff_sub":"Champion-taught instructionals on BJJ Fanatics — use code BJJWIKI for 20% off",
           "aff_btn":"Browse Instructionals →","share_label":"Share this technique",
           "privacy":"Privacy Policy","skill_cta":"📍 Track Your Progress","skill_link":"Open Skill Tree →"},
    "ja": {"home":"ホーム","techniques":"全技一覧","skill":"スキルツリー","sim":"シミュレーター",
           "related":"関連技","aff_title":"世界チャンピオンからこの技を習得",
           "aff_sub":"BJJ Fanaticsの教則動画 — コードBJJWIKIで20%オフ",
           "aff_btn":"教則動画を見る →","share_label":"この技をシェア",
           "privacy":"プライバシーポリシー","skill_cta":"📍 進捗を記録する","skill_link":"スキルツリーを開く →"},
    "pt": {"home":"Início","techniques":"Todas as Técnicas","skill":"Árvore","sim":"Simulador",
           "related":"Técnicas Relacionadas","aff_title":"Domine esta técnica com instrução de nível mundial",
           "aff_sub":"Instrucionais de campeões no BJJ Fanatics — código BJJWIKI para 20% de desconto",
           "aff_btn":"Ver Instrucionais →","share_label":"Compartilhe esta técnica",
           "privacy":"Política de Privacidade","skill_cta":"📍 Rastreie seu Progresso","skill_link":"Abrir Árvore de Habilidades →"},
}

def make_steps(steps_list):
    out = ''
    for i, (title, body) in enumerate(steps_list):
        out += f'<div class="step"><div class="step-num">{i+1}</div><div><strong>{title}</strong> — {body}</div></div>\n'
    return out

def make_page(tech, lang):
    slug = tech["slug"]
    name = tech["names"][lang]
    cat = tech["cats"][lang]
    belt = tech["belts"][lang]
    belt_cls = tech["belt_cls"]
    desc = tech["descs"][lang]
    lead = tech["leads"][lang]
    secs = tech["sections"][lang]
    related = tech["related"]
    ui = LANG_UI[lang]

    sections_html = ""
    for sec_title, steps in secs:
        sections_html += f"<h2>{sec_title}</h2>\n<div class=\"card\">\n{make_steps(steps)}</div>\n"

    related_html = "\n".join(f'<a href="{rs}.html">{rn}</a>' for rs,rn in related)
    share_url = f"https://t307239.github.io/bjj-wiki/{lang}/{slug}.html"
    share_text = {
        "en": f"Just learned about {name} on BJJ Wiki! {share_url} #BJJ",
        "ja": f"BJJ Wikiで{name}を学んだ！ {share_url} #BJJ #柔術",
        "pt": f"Aprendi sobre {name} no BJJ Wiki! {share_url} #BJJ"
    }[lang]

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.googletagmanager.com">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} | BJJ Wiki</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{name} | BJJ Wiki">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://t307239.github.io/bjj-wiki/og-image.svg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:type" content="article">
<meta property="og:url" content="https://t307239.github.io/bjj-wiki/{lang}/{slug}.html">
<link rel="canonical" href="https://t307239.github.io/bjj-wiki/{lang}/{slug}.html">
<link rel="alternate" hreflang="x-default" href="https://t307239.github.io/bjj-wiki/en/{slug}.html">
<link rel="alternate" hreflang="en" href="https://t307239.github.io/bjj-wiki/en/{slug}.html">
<link rel="alternate" hreflang="ja" href="https://t307239.github.io/bjj-wiki/ja/{slug}.html">
<link rel="alternate" hreflang="pt" href="https://t307239.github.io/bjj-wiki/pt/{slug}.html">
<link rel="alternate" type="application/rss+xml" title="BJJ Wiki RSS" href="../feed.xml">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-7LM8L3TRZM"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-7LM8L3TRZM');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5529701443220352" crossorigin="anonymous"></script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"{name}","description":"{desc}","datePublished":"{TODAY}","dateModified":"{TODAY}","author":{{"@type":"Organization","name":"BJJ Wiki"}}}}
</script>
<style>{CSS}</style>
</head>
<body>
<div class="container">
<header>
  <div class="logo">🥋 <span>BJJ</span> Wiki</div>
  <nav>
    <a href="index.html">{ui['home']}</a>
    <a href="index.html">{ui['techniques']}</a>
    <a href="skill-tree.html">{ui['skill']}</a>
    <a href="sparring-simulator.html">{ui['sim']}</a>
  </nav>
</header>
<span class="badge">{cat}</span>
<span class="belt {belt_cls}">{belt}</span>
<h1>{name}</h1>
<p>{lead}</p>
{sections_html}
<div class="skill-cta">
  <div><strong>{ui['skill_cta']}</strong><p>{name}</p></div>
  <a href="skill-tree.html">{ui['skill_link']}</a>
</div>
<div class="aff-box">
  <h3 style="font-size:1.05rem;font-weight:800;margin-bottom:10px">{ui['aff_title']}</h3>
  <p>{ui['aff_sub']}</p>
  <a href="https://bjjfanatics.com/?aff=bjjwiki" target="_blank" rel="noopener" class="aff-btn">{ui['aff_btn']}</a>
</div>
<div class="share-bar">
  <p>{ui['share_label']}</p>
  <div class="share-btns">
    <a href="https://twitter.com/intent/tweet?text={share_text}" target="_blank" class="share-btn x">𝕏 Share</a>
    <a href="https://reddit.com/submit?url={share_url}&title={name}" target="_blank" class="share-btn reddit">Reddit</a>
  </div>
</div>
<h2>{ui['related']}</h2>
<div class="related-links">
{related_html}
</div>
<footer>
  <p>🥋 BJJ Wiki &nbsp;·&nbsp; <a href="../privacy.html" style="color:inherit">{ui['privacy']}</a> &nbsp;·&nbsp; <a href="../about.html" style="color:inherit">About</a> &nbsp;·&nbsp; <a href="skill-tree.html" style="color:var(--accent2)">{ui['skill']}</a></p>
</footer>
</div>
</body>
</html>"""

count = 0
for tech in TECHNIQUES:
    for lang in ["en","ja","pt"]:
        html = make_page(tech, lang)
        path = f"{lang}/{tech['slug']}.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        count += 1

print(f"Generated {count} pages for {len(TECHNIQUES)} techniques")
