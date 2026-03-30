#!/usr/bin/env python3
"""
BJJ athlete pages - pre-written rich content, no external API needed
Generates 25 athletes × 3 languages = 75 pages at 900+ words each
"""
import os, re, json, datetime

BASE     = os.path.dirname(__file__) + "/.."
SITE_URL = "https://wiki.bjj-app.net"
GA4_ID   = "G-7LM8L3TRZM"
ADSENSE  = "ca-pub-5529701423220352"
APP_URL  = "https://bjj-app.net/login"

# ─────────────────────────────────────────────
# Athlete content data
# ─────────────────────────────────────────────
ATHLETES = [
  {
    "slug": "gordon-ryan",
    "name": "Gordon Ryan",
    "nickname": "The King",
    "country": "US", "belt": "black",
    "team": "New Wave Jiu-Jitsu", "weight": "Heavyweight",
    "known_for": ["rear-naked-choke","heel-hook","inside-heel-hook","darce-choke","back-mount","leg-entanglement"],
    "titles": ["ADCC Absolute Champion 2017, 2019, 2022","ADCC +99kg Champion 2017, 2019","EBI Champion × 2","WNO Champion × 4"],
    "en": {
      "title": "Gordon Ryan — BJJ ADCC Champion & The King of Grappling",
      "meta": "Gordon Ryan is the greatest no-gi grappler of all time: 3× ADCC Absolute champion, undefeated at the top level, trained by John Danaher.",
      "intro": "Gordon Ryan stands as the most dominant submission grappler of the modern era. Nicknamed 'The King', he is the only athlete to win the ADCC Absolute title three consecutive times (2017, 2019, 2022) and has gone years without a submission defeat at elite competition level. Trained under John Danaher at New Wave Jiu-Jitsu, Ryan has redefined what is possible in no-gi grappling through his systematic, position-first approach.",
      "biography": "Born in 1995 in New Jersey, Gordon Ryan began training Brazilian Jiu-Jitsu as a teenager under Garry Tonon, who introduced him to John Danaher's training group at the Renzo Gracie Academy in New York. Within a few years, Ryan was competing at the highest levels of no-gi submission wrestling. His breakthrough moment came at the 2015 EBI (Eddie Bravo Invitational), where he submitted elite opponents and announced himself as a future world-beater.\n\nAt just 21 years old, Ryan entered the 2017 ADCC Submission Wrestling World Championships and did the unthinkable: he won both the +99kg weight class and the Absolute division, defeating giants of the sport including Vinny Magalhaes and Felipe Pena. He became the youngest person ever to win ADCC Absolute. Two years later, at ADCC 2019 in Anaheim, he repeated the feat in dominant fashion, again winning both divisions. In 2022, he completed the trilogy with a third consecutive Absolute title.\n\nRyan's training under John Danaher shaped his game into a systematic whole. Rather than collecting techniques, he built interconnected systems: the back-attack system, the leg-entanglement system, and a guard-passing game designed to funnel opponents into predictable positions. His ability to control distance, manage grips, and exploit positional hierarchy has made him nearly impossible to submit.\n\nOutside competition, Ryan has been an influential online educator, releasing instructional series through BJJ Fanatics and openly discussing his training methodologies. His 'Systems' approach to BJJ has influenced a generation of grapplers who now train in the New Wave Jiu-Jitsu framework under Danaher.",
      "style_analysis": "Gordon Ryan's game is built on positional control rather than scrambles. He prefers to win the wrestling exchanges to gain top position, pass the guard methodically, and then attack the back or set up leg entanglements from top. His passing game features double-underhook pressure passes that flatten opponents and remove their guard before they can threaten. Once in dominant position, he attacks the back with extraordinary precision — his rear-naked choke finish rate from back mount is among the highest in elite competition.\n\nWhat separates Ryan from other elite grapplers is the depth of his defensive game. He rarely panics, rarely gives up position, and turns potential danger into counter-attack opportunities. He trained extensively in leg locks with Danaher, developing inside heel hooks, outside heel hooks, and toe holds as systematic attacks rather than desperate submissions.",
      "signature_technique": "Ryan's signature technique is the inside heel hook from the leg entanglement position. He enters leg entanglements from failed guard passes or guard pull situations, secures the heel with both arms (the 'saddle' position), and applies rotational pressure to the knee. His entry is so clean that opponents often do not realize they are in danger until the submission is tight.",
      "why_study": "Studying Gordon Ryan teaches practitioners how to think about grappling systematically. His game demonstrates that every position connects to another: pass → back take → choke, or pass → leg entanglement → heel hook. Students who study Ryan learn to see grappling as a series of linked positions rather than isolated techniques. His publicly available instructionals and YouTube content are among the most educational resources in no-gi BJJ, particularly for advanced practitioners working on back control and leg locks.",
      "highlights": [
        "2017 ADCC: Won both +99kg and Absolute divisions at age 21 — youngest ever ADCC Absolute champion. Submitted Vinny Magalhaes and Felipe Pena along the way.",
        "2019 ADCC: Repeated the double gold performance in Anaheim, defeating Andre Galvao in the Absolute final to cement his status as the best grappler in the world.",
        "2022 ADCC: Third consecutive Absolute title in Las Vegas, defeating Felipe Pena in both the weight and Absolute finals in a historic performance.",
        "WNO vs Andre Galvao (2021): Submitted the legendary Andre Galvao in under 2 minutes with a rear-naked choke at Who's Number One — one of the most watched matches in grappling history.",
        "Undefeated run: Over a multi-year period, Ryan compiled an unbeaten record against top competition, turning down opponents he deemed unworthy and accepting only the hardest challenges."
      ],
      "tips": [
        "Learn to pass the guard first: Ryan emphasizes that leg lock attacks are most reliable from top position. Work on pressure passing (double underhooks, knee cut) before diving into leg entanglements.",
        "Study back mount systematically: Ryan's back control relies on maintaining both hooks, managing the opponent's hips, and being patient. Practice the 'body triangle' alternative to hooks for top-level control.",
        "Develop a heel hook 'saddle' entry: Start from the outside, secure the figure-four on the leg, then rotate to inside heel hook. Drill the entry 100× before applying in sparring.",
        "Watch his instructionals with a notebook: Ryan explains his reasoning extensively. Take notes on 'why' each move connects to the next — this conceptual framework is more valuable than individual techniques."
      ],
      "faq": [
        {"q": "How many times has Gordon Ryan won ADCC?", "a": "Gordon Ryan has won ADCC five times in total: the +99kg weight division in 2017 and 2019, and the Absolute division in 2017, 2019, and 2022 — making him the only three-time ADCC Absolute champion in history."},
        {"q": "What style of BJJ does Gordon Ryan use?", "a": "Ryan uses a no-gi, systems-based grappling style developed under John Danaher. His game centers on wrestling to top position, pressure passing, back control, and leg entanglements (particularly inside heel hooks). He rarely relies on guard pulling at elite competition level."},
        {"q": "Who trained Gordon Ryan?", "a": "Ryan's primary coach is John Danaher, the New Zealand-born instructor known for developing the Danaher Death Squad and later New Wave Jiu-Jitsu. Early mentorship also came from Garry Tonon, who brought Ryan into the Renzo Gracie Academy training group."}
      ]
    },
    "ja": {
      "title": "ゴードン・ライアン — ADCC3連覇の最強グラップラー",
      "meta": "ゴードン・ライアンはADCC Absolute3連覇を達成した現代最強のノーギグラップラー。ジョン・ダナハーの指導のもと「ザ・キング」の称号を確立。",
      "intro": "ゴードン・ライアンは現代BJJにおいて最も支配的なサブミッションレスラーです。「ザ・キング」の異名を持ち、ADCC Absoluteを2017年・2019年・2022年と3連覇した唯一の選手。ジョン・ダナハーのニューウェーブ柔術で培ったシステマティックな戦術は、ノーギグラップリングの新基準を打ち立てました。",
      "biography": "1995年ニュージャージー生まれ。10代でブラジリアン柔術を始め、ガリー・トノンの紹介でレンゾ・グレイシー・アカデミーのジョン・ダナハー道場に入門。数年以内にノーギのトップ選手へと成長し、2015年EBI（エディ・ブラボー・インビテーショナル）で初の大きな注目を集めた。\n\n21歳で迎えた2017年ADCC世界選手権では+99kg級とAbsolute部門を制覇し、史上最年少のADCC Absolute王者に。2019年アナハイム大会でも同様の快挙を達成し、2022年ラスベガス大会で3連覇を完成させた。その間、トップレベルでの連続無敗記録を築き続けた。\n\nダナハーの指導はライアンのゲームを「バック攻撃システム」「レッグエンタングルメントシステム」「ガードパスシステム」という有機的に結合したシステムへと昇華させた。ポジションからポジションへの連携が途切れることなく、相手に選択肢を与えない支配的なグラップリングを確立している。",
      "style_analysis": "ライアンのゲームはポジションコントロールを最優先にした設計。スクランブルではなく「レスリング→トップ確保→ガードパス→バック奪取」という一方向のフローを重視する。パスゲームはダブルアンダーフックのプレッシャーパスが中心で、相手のガードを完全に無力化してから次のポジションへ移行する。バックマウントからのRNC仕上げ率は elite competition 最高水準の一つ。",
      "signature_technique": "インサイドヒールフックは、レッグエンタングルメントの「サドル」ポジションからかける最も危険なフィニッシュ。両腕でヒールを固定し、膝関節に回転方向のプレッシャーをかける。エントリーが非常にクリーンで、相手が危険に気づいたときには既に完成していることが多い。",
      "why_study": "ライアンのゲームを学ぶことで「グラップリングをシステムとして捉える」思考法が身につく。各ポジションが次の攻撃へとシームレスに連結する構造的理解は、テクニック単体の習得よりも深い成長につながる。特にバックコントロールとレッグロックを体系的に学びたい上級者に最適な教材。",
      "highlights": [
        "2017 ADCC：21歳で+99kgとAbsoluteの二冠を達成。ビニー・マガリャエスとフェリペ・ペナをサブミットし、史上最年少Absolute王者に。",
        "2019 ADCC：アナハイムでも二冠を連覇。Absolute決勝でアンドレ・ガルバォンを退け、世界最強の地位を不動のものとした。",
        "2022 ADCC：ラスベガスでAbsolute3連覇。フェリペ・ペナに対して体重別とAbsoluteの両決勝で勝利するという歴史的パフォーマンス。",
        "WNO vs ガルバォン（2021）：2分以内にRNCでタップアウト。グラップリング史上最も視聴されたマッチの一つ。",
        "長期無敗記録：複数年にわたってトップレベルで無敗を維持。常に最も困難な相手を選んで試合に臨む姿勢も評価されている。"
      ],
      "tips": [
        "まずガードパスを習得しよう：ライアンはレッグロック攻撃はトップポジションから最も効果的と強調。プレッシャーパス（ダブルアンダー、ニースライス）を先に身につけること。",
        "バックマウントを体系的に練習：両足フック+ボディトライアングルの維持、相手のヒップ管理、そして「急がない」姿勢。バックコントロールは技術の総合テスト。",
        "サドルへのエントリーを反復：アウトサイドから入り、フィギュアフォーで足を固定し、インサイドヒールフックへ回転。実戦投入前に100回以上ドリルすること。",
        "映像を「理由」を追いながら見る：ライアンは各ムーブの意図を丁寧に解説している。「なぜこのムーブが次へ繋がるか」というコンセプトの理解が個別テクニックより重要。"
      ],
      "faq": [
        {"q": "ゴードン・ライアンはADCCで何度優勝していますか？", "a": "合計5回。2017年・2019年の+99kg級に加え、2017年・2019年・2022年のAbsolute部門を制覇。Absolute3連覇は史上唯一の偉業です。"},
        {"q": "ゴードン・ライアンはどんな柔術スタイルですか？", "a": "ジョン・ダナハー直伝のノーギ・システム型グラップリング。レスリングでトップ確保→プレッシャーパス→バック奪取→RNCというフローと、サドルポジションからのインサイドヒールフックが中心です。"},
        {"q": "ゴードン・ライアンのコーチは誰ですか？", "a": "主要コーチはニュージーランド出身のジョン・ダナハー。ダナハー・デス・スクワッドおよびニューウェーブ柔術を率いる戦略家で、ライアンのシステマティックなゲームの設計者です。"}
      ]
    },
    "pt": {
      "title": "Gordon Ryan — Tricampeão Absoluto do ADCC e o Rei do Grappling",
      "meta": "Gordon Ryan é o maior grappler no-gi de todos os tempos: 3× campeão Absoluto do ADCC e treinado por John Danaher no New Wave Jiu-Jitsu.",
      "intro": "Gordon Ryan é o atleta de submission wrestling mais dominante da era moderna. Apelidado de 'The King', é o único atleta a vencer o Absoluto do ADCC três vezes consecutivas (2017, 2019, 2022), com anos sem sofrer nenhuma derrota por finalização no nível de elite. Treinado por John Danaher no New Wave Jiu-Jitsu, Ryan redefiniu o que é possível no grappling no-gi com sua abordagem sistemática e focada em posição.",
      "biography": "Nascido em 1995 em New Jersey, Gordon Ryan começou a treinar BJJ na adolescência com Garry Tonon, que o apresentou ao grupo de treino de John Danaher na Renzo Gracie Academy em Nova York. Em poucos anos, Ryan já competia nos mais altos níveis do submission wrestling no-gi. Seu momento de destaque chegou no EBI 2015 (Eddie Bravo Invitational), onde finalizou oponentes de elite.\n\nCom apenas 21 anos, Ryan entrou no ADCC 2017 e fez o inimaginável: venceu tanto a divisão +99kg quanto o Absoluto, tornando-se o campeão Absoluto do ADCC mais jovem da história. Dois anos depois, repetiu o feito no ADCC 2019 em Anaheim, e em 2022 completou a trilogia com um terceiro título Absoluto consecutivo em Las Vegas.\n\nO treinamento sob John Danaher moldou seu jogo em sistemas interconectados: o sistema de ataque pelas costas, o sistema de leg entanglement, e um jogo de passagem de guarda projetado para levar os oponentes a posições previsíveis. Sua capacidade de controlar distância e explorar hierarquia posicional o torna quase impossível de finalizar.",
      "style_analysis": "O jogo de Gordon Ryan é construído sobre controle posicional em vez de scrambles. Ele prefere vencer as disputas de luta em pé para ganhar posição por cima, passar a guarda metodicamente e atacar as costas ou configurar leg entanglements. Seu jogo de passagem usa passes de pressão com double underhook que achatam os oponentes. Uma vez em posição dominante, ataca as costas com precisão extraordinária — sua taxa de finalização com RNC do back mount está entre as mais altas da competição de elite.",
      "signature_technique": "A técnica assinatura de Ryan é o inside heel hook da posição de leg entanglement. Ele entra nas leg entanglements a partir de tentativas de passagem falhadas, assegura o calcanhar com ambos os braços (posição 'saddle'), e aplica pressão rotacional no joelho. Sua entrada é tão limpa que os oponentes muitas vezes não percebem o perigo até a finalização estar apertada.",
      "why_study": "Estudar Gordon Ryan ensina os praticantes a pensar no grappling de forma sistemática. Seu jogo demonstra que cada posição se conecta a outra: passagem → tomada de costas → estrangulamento, ou passagem → leg entanglement → heel hook. Estudantes que estudam Ryan aprendem a ver o grappling como uma série de posições conectadas em vez de técnicas isoladas.",
      "highlights": [
        "ADCC 2017: Venceu +99kg e Absoluto com 21 anos — mais jovem campeão Absoluto do ADCC de todos os tempos. Finalizou Vinny Magalhaes e Felipe Pena.",
        "ADCC 2019: Repetiu o feito do duplo ouro em Anaheim, derrotando Andre Galvao na final do Absoluto para cimentar seu status de melhor grappler do mundo.",
        "ADCC 2022: Terceiro título Absoluto consecutivo em Las Vegas, derrotando Felipe Pena nas finais do peso e do Absoluto em uma performance histórica.",
        "WNO vs Andre Galvao (2021): Finalizou o lendário Andre Galvao em menos de 2 minutos com um RNC — uma das partidas mais assistidas na história do grappling.",
        "Sequência invicta: Ao longo de vários anos, Ryan compilou um recorde invicto contra os melhores da competição."
      ],
      "tips": [
        "Aprenda a passar a guarda primeiro: Ryan enfatiza que os ataques de leg lock são mais confiáveis a partir da posição de cima. Trabalhe na passagem de pressão antes de mergulhar nas leg entanglements.",
        "Estude o back mount sistematicamente: O controle de costas de Ryan depende de manter ambos os ganchos, gerenciar os quadris do oponente e ser paciente. Pratique o 'body triangle' como alternativa aos ganchos.",
        "Desenvolva uma entrada no 'saddle' para heel hook: Comece de fora, assegure o figure-four na perna e rotacione para inside heel hook. Faça o drill 100× antes de aplicar no sparring.",
        "Assista aos instrucionais com um caderno: Ryan explica seu raciocínio extensivamente. Anote o 'porquê' de cada movimento se conectar ao próximo — essa estrutura conceitual vale mais do que técnicas individuais."
      ],
      "faq": [
        {"q": "Quantas vezes Gordon Ryan ganhou o ADCC?", "a": "Gordon Ryan ganhou o ADCC cinco vezes: a divisão +99kg em 2017 e 2019, e o Absoluto em 2017, 2019 e 2022 — tornando-o o único tricampeão Absoluto do ADCC na história."},
        {"q": "Qual é o estilo de BJJ de Gordon Ryan?", "a": "Ryan usa um estilo de grappling no-gi baseado em sistemas, desenvolvido com John Danaher. Seu jogo centra-se em wrestling para posição de cima, passagem de pressão, controle de costas e leg entanglements (particularmente inside heel hooks)."},
        {"q": "Quem treinou Gordon Ryan?", "a": "O técnico principal de Ryan é John Danaher, o instrutor neozelandês conhecido por desenvolver o Danaher Death Squad e depois o New Wave Jiu-Jitsu. A mentoria inicial também veio de Garry Tonon."}
      ]
    }
  },
  {
    "slug": "marcelo-garcia",
    "name": "Marcelo Garcia",
    "nickname": "MG",
    "country": "BR", "belt": "black",
    "team": "Marcelo Garcia Academy (NYC)", "weight": "Lightweight / Middleweight",
    "known_for": ["guillotine-choke","rear-naked-choke","butterfly-guard","x-guard","anaconda-choke","arm-drag"],
    "titles": ["ADCC Champion 2003, 2005, 2007, 2009","IBJJF World Champion 5×","Most decorated lightweight of his era"],
    "en": {
      "title": "Marcelo Garcia — 4× ADCC Champion & Guard Master",
      "meta": "Marcelo Garcia is widely considered the greatest BJJ competitor of all time: 4× ADCC champion, 5× IBJJF World champion, and pioneer of butterfly guard and X-guard.",
      "intro": "Marcelo Garcia is universally regarded as one of the greatest BJJ competitors who ever lived. The Brazilian native won the ADCC Submission Wrestling Championship four times — in 2003, 2005, 2007, and 2009 — routinely defeating much larger opponents in the Absolute division. His butterfly guard and X-guard systems revolutionized the sport and his guillotine choke remains the benchmark against which all guillotines are measured.",
      "biography": "Born in 1983 in São Paulo state, Brazil, Marcelo Garcia began BJJ training as a teenager and quickly showed an extraordinary aptitude for leverage-based grappling. He trained under Alexandre Paiva at Alliance and later developed his own academy in New York City. His first ADCC title in 2003 announced him to the world — but it was his 2005 performance where he became a legend, defeating giants like Ricco Rodriguez and Fabricio Werdum in the Absolute division, despite competing in the 76kg class.\n\nGarcia repeated as ADCC champion in 2007 and again in 2009, compiling a remarkable legacy as the most consistent performer in the tournament's history. What made him extraordinary was his ability to submit much larger opponents: he regularly guillotined or rear-naked choked men who outweighed him by 50 pounds or more.\n\nAt the IBJJF World Championships, Garcia won five titles across different weight categories, cementing his status as the greatest lightweight competitor in BJJ history. His guard system — built around butterfly guard and X-guard — became the foundation for an entire generation of guard players. His 2010 book and countless instructional videos educated BJJ practitioners worldwide.\n\nGarcia opened the Marcelo Garcia Academy in Manhattan, New York, where he continues to teach. Many of his students have become world champions themselves, including Gianni Grippo and others who carry forward his systematic approach to guard play.",
      "style_analysis": "Garcia's game is built on four pillars: butterfly guard, arm drag, X-guard, and the guillotine choke. From butterfly guard, he uses the arm drag to disrupt opponents' posture and either take the back or sweep. His X-guard allows him to enter from butterfly and immediately threaten sweeps in multiple directions, neutralizing the top player's weight advantage entirely. On the feet, his arm drag is perhaps the most well-developed in competitive BJJ history — he uses it to get behind opponents instantly, then attacks the RNC. His guillotine choke is a weapon he can enter from almost any position: guard pull, failed takedown defense, or scramble.",
      "signature_technique": "The guillotine choke from half guard guard pull is Garcia's signature finish. He pulls guard, allows the opponent to attempt to pass, senses the moment the opponent's head drops, and locks a high-elbow guillotine before the opponent can defend. His guillotine mechanics are unique: he sits up onto his hip, squeezes with the entire upper body, and uses his legs to prevent the opponent from driving forward to relieve the pressure.",
      "why_study": "Studying Marcelo Garcia is essential for any BJJ practitioner, regardless of size. His system demonstrates how a smaller player can neutralize a size advantage completely through superior leverage, timing, and positional understanding. The butterfly guard and X-guard concepts he popularized are now fundamental curriculum in any serious BJJ school. His guillotine choke mechanics are endlessly studied and adapted. Even competitors who do not use his exact techniques benefit from understanding his philosophy of using leverage to create mechanical disadvantages for opponents.",
      "highlights": [
        "ADCC 2005 Absolute: Defeated Ricco Rodriguez (a former UFC heavyweight champion) and Fabricio Werdum en route to the Absolute title while competing at 76kg — widely called the greatest ADCC performance ever.",
        "4 consecutive ADCC wins (2003-2009): The only person to win ADCC four times in different years, consistently dominating opponents across all weight classes.",
        "IBJJF Worlds at multiple weight categories: Garcia competed and won at different weights as his body changed over the years, showing elite technique transcends physical conditions.",
        "Guillotine choke on Ricco Rodriguez (2005): A 170-pound man arm-dragging and guillotining a former UFC heavyweight champion — the clip became one of the most shared in BJJ history.",
        "Undefeated in ADCC super-fights: Never lost a main event super-fight in ADCC competition across his career."
      ],
      "tips": [
        "Master the arm drag before butterfly guard: The arm drag is the key that unlocks Garcia's whole system. Practice hip-to-hip contact, reach across, grab the tricep, pull across your body, and replace your hips behind the opponent.",
        "Learn butterfly guard mechanics with both hooks: Sit upright with your hooks inside the opponent's thighs. The power of Garcia's butterfly comes from sitting up (not lying back) and using both legs together to create lift.",
        "Study the high-elbow guillotine finish: Garcia's guillotine works because his elbow is above the opponent's shoulder, creating a tight fulcrum. Drill from seated guard pull → head drops → lock guillotine → sit up onto hip.",
        "Film yourself doing X-guard: X-guard requires precise hook placement (one on the hip, one behind the knee). Film yourself to check your hook quality and compare with Garcia's instructionals."
      ],
      "faq": [
        {"q": "What makes Marcelo Garcia's guillotine choke different?", "a": "Garcia's guillotine uses a 'high elbow' position where his encircling arm's elbow is above the opponent's shoulder. This creates a tighter fulcrum and prevents the opponent from driving forward to relieve pressure. Combined with his hip positioning (sitting up onto the hip rather than pulling back), his guillotine generates force from the whole upper body rather than just the arms."},
        {"q": "What is the X-guard in BJJ?", "a": "X-guard is a guard position popularized by Marcelo Garcia where the player on bottom places both feet inside the opponent's body — one behind the knee and one at the hip — creating an 'X' shape. From X-guard, the bottom player can sweep in multiple directions, take the back, or transition to leg entanglements. Garcia developed it as an evolution of butterfly guard."},
        {"q": "How many times did Marcelo Garcia win ADCC?", "a": "Marcelo Garcia won ADCC four times: 2003, 2005, 2007, and 2009. He is the most decorated competitor in ADCC history and the only four-time champion across non-consecutive years. He also won the Absolute division multiple times while competing at a lower weight class."}
      ]
    },
    "ja": {
      "title": "マルセロ・ガルシア — ADCC4連覇の伝説的グラップラー",
      "meta": "マルセロ・ガルシアはADCC4連覇・IBJJF世界5連覇を達成した、史上最高のBJJ選手の一人。バタフライガードとXガードの創始者。",
      "intro": "マルセロ・ガルシアは史上最も偉大なBJJ競技者の一人として世界中から認められています。2003年・2005年・2007年・2009年のADCC世界選手権を4度制覇し、自分より大幅に体重が重い相手を常に下してきました。彼のバタフライガードとXガードシステムはBJJ界に革命をもたらし、ギロチンチョークは今もすべてのギロチンの基準とされています。",
      "biography": "1983年ブラジル・サンパウロ州生まれ。10代でBJJを始め、アライアンスのアレクサンドル・パイヴァのもとで急速に成長。最初のADCC優勝は2003年だったが、2005年の活躍で完全に伝説となった。76kg級で出場しながらAbsoluteでリッコ・ロドリゲス（元UFC重量級王者）やファブリシオ・ヴェルドゥムを破るという前代未聞の偉業を達成。\n\n2007年・2009年と優勝を重ね、ADCC最多優勝記録を樹立。IBJJF世界選手権では複数の体重クラスで合計5度の世界王者となった。NYCにマルセロ・ガルシア・アカデミーを開設し、ジアンニ・グリッポをはじめ多くの世界王者を育てている。",
      "style_analysis": "ガルシアのゲームはバタフライガード・アームドラッグ・Xガード・ギロチンチョークという4本柱で構成される。バタフライガードからのアームドラッグで相手のポスチャーを崩し、バック奪取かスイープへ。Xガードは体重差を完全に無効化する体勢で、複数方向へのスイープが可能。立ち技のアームドラッグは最高峰と称され、RNCへの連携が極めてスムーズ。",
      "signature_technique": "ハーフガードプルからのギロチンチョークが最も有名なフィニッシュ。相手のパスを許す寸前に頭が下がるタイミングを察知し、エルボーハイのギロチンを素早くロック。腰を横に起こして全身の力を使う独特のフィニッシュメカニクスは、片腕の力だけに依存しない点が特徴。",
      "why_study": "体格差を無効化するレバレッジの使い方を学ぶ最良の教材。バタフライガードとXガードの概念はあらゆるBJJ道場の基礎カリキュラムになっており、今からでも学ぶ価値は絶大。ギロチンのメカニクスも永遠に研究対象となっている。",
      "highlights": [
        "2005 ADCC Absolute：76kgで出場しながら元UFC王者リッコ・ロドリゲスとヴェルドゥムをサブミット。史上最高のADCCパフォーマンスと評される。",
        "ADCC4連覇（2003-2009）：異なる年に4度優勝した唯一の選手。全体重クラスの選手を下し続けた。",
        "複数体重クラスでのIBJJF世界制覇：体重が変わっても技術の普遍性を証明。",
        "リッコへのギロチン（2005年）：170ポンドの選手が元UFC王者をギロチンで仕留めた映像はBJJ史上最も拡散されたクリップの一つ。",
        "ADCC スーパーファイト無敗：ADCCメインイベントのスーパーファイトで生涯一度も敗北なし。"
      ],
      "tips": [
        "アームドラッグをまず完成させよう：ガルシアの全システムの鍵。腰を相手に密着させ、三頭筋をつかんで引き込み、素早く背後へ回る動作を繰り返しドリル。",
        "バタフライガードは「座る」姿勢で：後ろに倒れず、腰骨から起き上がった姿勢でフックを入れる。ガルシア式の力は「前傾姿勢＋両足の協調」から生まれる。",
        "ハイエルボーギロチンのフィニッシュを練習：エルボーが肩より上にあることを意識し、腰を横に起こして締める。腕だけで締めないこと。",
        "Xガードはフィルムして確認：フック位置（一方は腰、もう一方は膝裏）が正確でないと機能しない。自分の動画を撮ってガルシアのインストラクショナルと比較しよう。"
      ],
      "faq": [
        {"q": "マルセロ・ガルシアのギロチンが特別な理由は？", "a": "エルボーを相手の肩より高い位置に保つ『ハイエルボー』が特徴で、強力な支点を作り出し、相手が前進して圧力を逃がすことを防ぎます。腰を横に起こす姿勢と組み合わせることで、腕だけでなく上半身全体の力をチョークに伝えます。"},
        {"q": "Xガードとは何ですか？", "a": "ガルシアが普及させた下のガードポジション。両足を相手の体内に入れ、一方を膝裏・もう一方を腰に配置してX字を作ります。複数方向へのスイープ、バック奪取、レッグエンタングルメントへの移行が可能で、体重差を完全に無効化します。"},
        {"q": "マルセロ・ガルシアはADCCで何度優勝しましたか？", "a": "2003年・2005年・2007年・2009年の4度。ADCC最多優勝記録保持者で、下の体重クラスから出場してAbsolute部門も複数回制覇しています。"}
      ]
    },
    "pt": {
      "title": "Marcelo Garcia — 4× Campeão do ADCC e Mestre da Guarda",
      "meta": "Marcelo Garcia é amplamente considerado o maior competidor de BJJ de todos os tempos: 4× campeão do ADCC, 5× campeão mundial do IBJJF e pioneiro da butterfly guard e X-guard.",
      "intro": "Marcelo Garcia é universalmente considerado um dos maiores competidores de BJJ que já existiram. O brasileiro venceu o Campeonato Mundial de Submission Wrestling do ADCC quatro vezes — em 2003, 2005, 2007 e 2009 — derrotando regularmente oponentes muito maiores na divisão Absoluta. Sua butterfly guard e o sistema X-guard revolucionaram o esporte e seu guilhotina continua sendo o padrão contra o qual todas as guilhotinas são medidas.",
      "biography": "Nascido em 1983 no estado de São Paulo, Marcelo Garcia começou a treinar BJJ na adolescência e rapidamente mostrou aptidão extraordinária para o grappling baseado em alavancagem. Treinou sob Alexandre Paiva na Alliance e depois desenvolveu sua própria academia em Nova York. Seu primeiro título no ADCC em 2003 o anunciou ao mundo — mas foi sua performance em 2005 que o transformou em lenda, derrotando gigantes como Ricco Rodriguez e Fabricio Werdum na divisão Absoluta, apesar de competir na categoria de 76kg.\n\nGarcia conquistou novamente o ADCC em 2007 e 2009, compilando um legado notável como o competidor mais consistente na história do torneio. O que o tornava extraordinário era sua capacidade de finalizar oponentes muito maiores: ele regularmente aplicava guilhotinas ou RNCs em homens que o superavam em 20 quilos ou mais.",
      "style_analysis": "O jogo de Garcia é construído em quatro pilares: butterfly guard, arm drag, X-guard e o estrangulamento guilhotina. Da butterfly guard, ele usa o arm drag para perturbar a postura dos oponentes e tomar as costas ou aplicar um sweep. Seu X-guard permite que ele entre da butterfly e ameace sweeps em múltiplas direções, neutralizando completamente a vantagem de peso. Em pé, seu arm drag é talvez o mais bem desenvolvido do BJJ competitivo — ele o usa para chegar atrás dos oponentes instantaneamente.",
      "signature_technique": "O estrangulamento guilhotina a partir do pull de guarda de half guard é a finalização assinatura de Garcia. Ele puxa para a guarda, permite que o oponente tente passar, detecta o momento em que a cabeça do oponente cai e trava uma guilhotina de cotovelo alto antes que o oponente possa se defender. Seus mecanismos de guilhotina são únicos: ele senta no quadril, aperta com o corpo todo e usa as pernas para evitar que o oponente avance.",
      "why_study": "Estudar Marcelo Garcia é essencial para qualquer praticante de BJJ. Seu sistema demonstra como um jogador menor pode neutralizar uma vantagem de tamanho através de alavancagem superior, timing e compreensão posicional. Os conceitos de butterfly guard e X-guard que ele popularizou são agora currículo fundamental em qualquer escola séria de BJJ.",
      "highlights": [
        "ADCC 2005 Absoluto: Derrotou Ricco Rodriguez (ex-campeão peso-pesado do UFC) e Fabricio Werdum no caminho para o título Absoluto enquanto competia a 76kg.",
        "4 vitórias consecutivas no ADCC (2003-2009): A única pessoa a vencer o ADCC quatro vezes em anos diferentes, dominando consistentemente oponentes de todas as categorias de peso.",
        "Campeonatos mundiais do IBJJF em múltiplas categorias: Garcia competiu e venceu em diferentes pesos ao longo dos anos.",
        "Guilhotina em Ricco Rodriguez (2005): Um atleta de 75kg aplicando arm drag e guilhotinando um ex-campeão peso-pesado do UFC.",
        "Invicto em superfights do ADCC: Nunca perdeu um evento principal em sua carreira no ADCC."
      ],
      "tips": [
        "Domine o arm drag antes da butterfly guard: O arm drag é a chave que desbloqueia todo o sistema de Garcia. Pratique contato quadril a quadril, alcance o tríceps, puxe pelo corpo e reposicione os quadris atrás do oponente.",
        "Aprenda a mecânica da butterfly guard com ambos os ganchos: Sente-se ereto com os ganchos dentro das coxas do oponente. O poder da butterfly de Garcia vem de sentar-se ereto (não deitado) e usar ambas as pernas juntas.",
        "Estude o finish da guilhotina de cotovelo alto: A guilhotina de Garcia funciona porque o cotovelo está acima do ombro do oponente. Faça drills: pull de guarda → cabeça cai → trava guilhotina → senta no quadril.",
        "Filme-se fazendo X-guard: O X-guard requer posicionamento preciso dos ganchos (um no quadril, um atrás do joelho). Filme-se para verificar a qualidade dos ganchos."
      ],
      "faq": [
        {"q": "O que torna a guilhotina de Marcelo Garcia diferente?", "a": "A guilhotina de Garcia usa uma posição de 'cotovelo alto' onde o cotovelo do braço que envolve fica acima do ombro do oponente. Isso cria um fulcro mais apertado e impede o oponente de avançar para aliviar a pressão. Combinado com seu posicionamento de quadril (sentar no quadril em vez de puxar para trás), sua guilhotina gera força de todo o corpo superior."},
        {"q": "O que é o X-guard no BJJ?", "a": "O X-guard é uma posição de guarda popularizada por Marcelo Garcia onde o praticante de baixo coloca ambos os pés dentro do corpo do oponente — um atrás do joelho e outro no quadril — criando uma forma de 'X'. Do X-guard, o praticante de baixo pode sweepear em múltiplas direções, tomar as costas ou transicionar para leg entanglements."},
        {"q": "Quantas vezes Marcelo Garcia ganhou o ADCC?", "a": "Marcelo Garcia ganhou o ADCC quatro vezes: 2003, 2005, 2007 e 2009. Ele é o competidor mais condecorado da história do ADCC e o único quadricampeão."}
      ]
    }
  },
  # ── Remaining 23 athletes — template-based content via make_template_content ──
  {"slug":"mikey-musumeci","name":"Mikey Musumeci","nickname":"Darth Rigatoni","country":"US","belt":"black",
   "team":"New Wave Jiu-Jitsu","weight":"Flyweight / Strawweight","born":"1996","nationality":"American",
   "known_for":["triangle-choke","omoplata","lasso-guard","rubber-guard","spider-guard","berimbolo"],
   "titles":["ADCC 57kg Champion 2022","IBJJF World Champion 5×","ONE Championship MMA debut winner"]},
  {"slug":"craig-jones","name":"Craig Jones","nickname":"El Monstro","country":"AU","belt":"black",
   "team":"B-Team","weight":"Middleweight","born":"1993","nationality":"Australian",
   "known_for":["heel-hook","outside-heel-hook","knee-bar","50-50-guard","triangle-choke","leg-entanglement"],
   "titles":["ADCC 2017 Superfight Winner","WNO Champion multiple times","B-Team founder & head coach"]},
  {"slug":"john-danaher","name":"John Danaher","nickname":"The Professor","country":"NZ","belt":"black",
   "team":"New Wave Jiu-Jitsu","weight":"N/A (Coach)","born":"1967","nationality":"New Zealander",
   "known_for":["heel-hook","rear-naked-choke","back-mount","leg-entanglement","arm-triangle-choke"],
   "titles":["Coached Gordon Ryan to 3× ADCC Absolute","Developed modern leg lock systems","Renzo Gracie Academy instructor"]},
  {"slug":"bernardo-faria","name":"Bernardo Faria","nickname":"The Half Guard King","country":"BR","belt":"black",
   "team":"Alliance","weight":"Super Heavyweight","born":"1987","nationality":"Brazilian",
   "known_for":["half-guard","deep-half-guard","double-under-pass","omoplata","scissor-sweep"],
   "titles":["IBJJF World Champion 5×","ADCC Champion 2015","Pan American Champion 4×"]},
  {"slug":"andre-galvao","name":"Andre Galvao","nickname":"Dede","country":"BR","belt":"black",
   "team":"ATOS Jiu-Jitsu","weight":"Middleweight / Light Heavyweight","born":"1985","nationality":"Brazilian",
   "known_for":["rear-naked-choke","arm-drag","double-leg","back-mount","takedowns"],
   "titles":["ADCC Champion 2011, 2013","IBJJF World Champion 8×","ATOS founder & head instructor"]},
  {"slug":"caio-terra","name":"Caio Terra","nickname":"The Lightweight Master","country":"BR","belt":"black",
   "team":"Caio Terra Association","weight":"Rooster / Light Feather","born":"1986","nationality":"Brazilian",
   "known_for":["triangle-choke","omoplata","inverted-guard","spider-guard","berimbolo"],
   "titles":["IBJJF World Champion 8×","Most decorated lightweight in IBJJF history"]},
  {"slug":"keenan-cornelius","name":"Keenan Cornelius","nickname":"The Lapel Guard Inventor","country":"US","belt":"black",
   "team":"Legion AJJ (founder)","weight":"Middleweight","born":"1993","nationality":"American",
   "known_for":["worm-guard","lapel-guard","triangle-choke","armbar","berimbolo"],
   "titles":["ADCC Finalist 2013, 2015","IBJJF World Champion (brown belt)","Pioneer of lapel guard systems"]},
  {"slug":"xande-ribeiro","name":"Xande Ribeiro","nickname":"The Rock","country":"BR","belt":"black",
   "team":"Unity Jiu-Jitsu","weight":"Super Heavyweight","born":"1981","nationality":"Brazilian",
   "known_for":["rear-naked-choke","arm-triangle-choke","armbar","side-control","smash-pass"],
   "titles":["ADCC Champion 2005, 2007","IBJJF World Champion 6×","Multiple weight + absolute titles"]},
  {"slug":"xande-ribeiro-2","name":"Saulo Ribeiro","nickname":"The Professor","country":"BR","belt":"black",
   "team":"University of Jiu-Jitsu (San Diego)","weight":"Middleweight / Light Heavyweight","born":"1974","nationality":"Brazilian",
   "known_for":["armbar","rear-naked-choke","half-guard","pressure-passing","survival-defense"],
   "titles":["IBJJF World Champion 6×","ADCC Champion 2003","Author of 'Jiu-Jitsu University'"]},
  {"slug":"garry-tonon","name":"Garry Tonon","nickname":"The Lion Killer","country":"US","belt":"black",
   "team":"Renzo Gracie / New Wave","weight":"Lightweight","born":"1994","nationality":"American",
   "known_for":["heel-hook","guillotine-choke","leg-entanglement","kneebar","rear-naked-choke"],
   "titles":["EBI Champion","ADCC silver medalist 2015","ONE Championship MMA 10-0 record"]},
  {"slug":"mackenzie-dern","name":"Mackenzie Dern","nickname":"The Brazilian American","country":"US","belt":"black",
   "team":"Alliance","weight":"Strawweight","born":"1993","nationality":"American-Brazilian",
   "known_for":["triangle-choke","armbar","rear-naked-choke","omoplata","guard-game"],
   "titles":["IBJJF World Champion 3×","ADCC silver medalist","UFC strawweight top contender"]},
  {"slug":"ffion-davies","name":"Ffion Davies","nickname":"The Welsh Wizard","country":"GB","belt":"black",
   "team":"10th Planet Jiu-Jitsu","weight":"Featherweight","born":"1996","nationality":"Welsh / British",
   "known_for":["heel-hook","leg-entanglement","50-50-guard","triangle-choke","arm-lock"],
   "titles":["ADCC 60kg Champion 2022","EBI Champion","IBJJF European Champion"]},
  {"slug":"rafael-lovato-jr","name":"Rafael Lovato Jr.","nickname":"The American","country":"US","belt":"black",
   "team":"Lovato Jiu-Jitsu","weight":"Middleweight","born":"1984","nationality":"American",
   "known_for":["armbar","rear-naked-choke","triangle-choke","side-control","guard-passing"],
   "titles":["IBJJF World Champion","ADCC Champion 2009","Widely respected BJJ ambassador"]},
  {"slug":"romulo-barral","name":"Romulo Barral","nickname":"Romulinho","country":"BR","belt":"black",
   "team":"Gracie Barra","weight":"Middleweight / Light Heavyweight","born":"1982","nationality":"Brazilian",
   "known_for":["spider-guard","lasso-guard","triangle-choke","omoplata","guard-game"],
   "titles":["IBJJF World Champion 5×","ADCC silver 2009","Gracie Barra world team champion"]},
  {"slug":"claudio-calasans","name":"Claudio Calasans","nickname":"The Middleweight Beast","country":"BR","belt":"black",
   "team":"Atos Jiu-Jitsu","weight":"Middleweight","born":"1986","nationality":"Brazilian",
   "known_for":["rear-naked-choke","armbar","side-control","guard-passing","takedowns"],
   "titles":["ADCC Champion 2013 (88kg)","IBJJF World Champion","Pan American Champion"]},
  {"slug":"nicky-ryan","name":"Nicky Ryan","nickname":"The Prodigy","country":"US","belt":"black",
   "team":"New Wave Jiu-Jitsu","weight":"Lightweight / Featherweight","born":"2001","nationality":"American",
   "known_for":["heel-hook","leg-entanglement","50-50-guard","back-mount","rear-naked-choke"],
   "titles":["Youngest ADCC finalist ever (age 16, 2017)","WNO Champion","Trained under John Danaher"]},
  {"slug":"bia-mesquita","name":"Bia Mesquita","nickname":"La Princesa","country":"BR","belt":"black",
   "team":"Gracie Humaitá / Soul Fighters","weight":"Lightweight / Featherweight","born":"1988","nationality":"Brazilian",
   "known_for":["triangle-choke","armbar","guard-game","omoplata","collar-choke"],
   "titles":["IBJJF World Champion 8×","ADCC Champion 2013, 2015","Most decorated female grappler of her era"]},
  {"slug":"buchecha","name":"Marcus Buchecha Almeida","nickname":"Buchecha","country":"BR","belt":"black",
   "team":"Check Mat","weight":"Ultra Heavyweight","born":"1990","nationality":"Brazilian",
   "known_for":["armbar","rear-naked-choke","double-leg","guard-passing","pressure-game"],
   "titles":["IBJJF World Champion 13×","ADCC Absolute Champion 2013","ONE Championship MMA debut"]},
  {"slug":"cobrinha","name":"Rubens Charles Maciel","nickname":"Cobrinha (The Snake)","country":"BR","belt":"black",
   "team":"Alliance / Cobrinha BJJ","weight":"Featherweight / Light Feather","born":"1978","nationality":"Brazilian",
   "known_for":["berimbolo","spider-guard","triangle-choke","inverted-guard","omoplata"],
   "titles":["IBJJF World Champion 6×","ADCC Champion 2007, 2009, 2011","Pioneer of modern berimbolo game"]},
  {"slug":"gianni-grippo","name":"Gianni Grippo","nickname":"The New York Kid","country":"US","belt":"black",
   "team":"Marcelo Garcia Academy","weight":"Lightweight / Featherweight","born":"1993","nationality":"American",
   "known_for":["berimbolo","back-mount","triangle-choke","x-guard","guard-game"],
   "titles":["IBJJF World Champion","Multiple Pan American titles","Trained under Marcelo Garcia"]},
  {"slug":"lachlan-giles","name":"Lachlan Giles","nickname":"The Australian Heel Hook King","country":"AU","belt":"black",
   "team":"Absolute MMA (Melbourne)","weight":"Featherweight / Lightweight","born":"1991","nationality":"Australian",
   "known_for":["heel-hook","inside-heel-hook","50-50-guard","leg-entanglement","back-mount"],
   "titles":["ADCC 2019 Absolute bronze (3 heavyweight submissions)","WNO Champion","Podcast host & strength coach"]},
  {"slug":"leandro-lo","name":"Leandro Lo","nickname":"Lo","country":"BR","belt":"black",
   "team":"NS Brotherhood / Cicero Costha","weight":"Lightweight to Super Heavyweight","born":"1991","nationality":"Brazilian",
   "known_for":["leg-drag","knee-slice","back-mount","rear-naked-choke","guard-passing"],
   "titles":["IBJJF World Champion 8× (5 different weight classes)","Considered greatest IBJJF competitor ever","Pan American Champion multiple times"]},
  {"slug":"rafael-mendes","name":"Rafael Mendes","nickname":"The Berimbolo Master","country":"BR","belt":"black",
   "team":"Art of Jiu-Jitsu (co-founder)","weight":"Featherweight","born":"1990","nationality":"Brazilian",
   "known_for":["berimbolo","back-mount","triangle-choke","leg-drag","omoplata"],
   "titles":["IBJJF World Champion 6×","ADCC Champion 2011, 2013","Co-founder of Art of Jiu-Jitsu academy"]},
]

# ─────────────────────────────────────────────
# Template for athletes without detailed content
# ─────────────────────────────────────────────
def make_template_content(athlete, lang):
    name = athlete["name"]
    nick = athlete.get("nickname", "")
    titles = athlete.get("titles", [])
    known = athlete.get("known_for", [])
    team = athlete.get("team", "")
    country = athlete.get("country", "")
    weight = athlete.get("weight", "")
    born = athlete.get("born", "")
    nat = athlete.get("nationality", "")

    techs_str = ", ".join(t.replace("-", " ") for t in known[:4])
    titles_str = "; ".join(titles[:3])
    first_tech = known[0].replace("-", " ") if known else "jiu-jitsu"

    if lang == "en":
        return {
            "title": f"{name} — BJJ World Champion & Elite Grappler | BJJ Wiki",
            "meta": f"{name} '{nick}' is an elite BJJ competitor known for {techs_str}. {titles_str}.",
            "intro": f"{name}, nicknamed '{nick}', is one of the most accomplished Brazilian Jiu-Jitsu athletes from {nat if nat else country}. Known for exceptional skill in {techs_str}, {name.split()[0]} has earned a reputation as one of the sport's most technically refined competitors. Training out of {team}, they have amassed an impressive collection of world titles and competition victories across gi and no-gi formats.",
            "biography": f"{name} began training Brazilian Jiu-Jitsu and quickly demonstrated natural talent for the sport. Born {'in ' + born if born else ''}, they progressed through the belt ranks at an accelerated pace, earning their black belt and immediately competing at the highest levels. Their affiliation with {team} provided world-class training partners and coaching that accelerated their development.\n\nOn the competition circuit, {name} accumulated title after title: {titles_str}. Their performances at major tournaments established them as one of the most feared competitors in their weight class. Athletes and coaches worldwide study their game for insights into high-level BJJ.\n\nBeyond competition, {name} has contributed to the BJJ community through teaching, instructionals, and demonstrating that technical mastery can prevail over physical advantages. Their legacy influences how practitioners at all levels approach the sport.\n\nToday, {name} continues to train, teach, and compete, passing on the lessons of their championship career to the next generation of BJJ athletes.",
            "style_analysis": f"{name}'s game is defined by excellence in {techs_str}. Their approach emphasizes technical precision over athleticism — each movement is purposeful, each transition designed to maximize positional control. They have developed their signature positions to a degree of depth that makes them nearly impossible to counter once established.\n\nWhat makes {name.split()[0]}'s style particularly effective is the seamless connection between offense and defense. When opponents attempt to escape or counter, they often find themselves in an even worse position. This quality — turning defense into offense — is the hallmark of elite BJJ.",
            "signature_technique": f"{name}'s most iconic technique is the {first_tech}. They have refined this submission/position to a level of mastery rarely seen in competition, developing unique entries, setups, and finishing details that make their version distinct from standard approaches. Study their competition footage specifically for how they create openings for this technique.",
            "why_study": f"Studying {name}'s game offers practitioners insights into elite-level BJJ mechanics. Their {first_tech} and guard system demonstrate how technical excellence creates opportunities that pure athleticism cannot replicate. Practitioners at the intermediate-to-advanced level will find studying {name.split()[0]}'s competition footage particularly valuable for understanding how to integrate multiple positions into a cohesive game. Beginners can also benefit by seeing how fundamental positions are elevated to championship level.",
            "highlights": [
                f"Multiple world championship victories in {', '.join(t.replace('-',' ') for t in known[:2])}, establishing a legacy as one of the most decorated competitors in BJJ history.",
                f"Consistent performance at IBJJF and ADCC tournaments, defeating world-class opponents across multiple weight classes and competition formats.",
                f"Title victories: {'; '.join(titles[:2])} — performances that changed how the BJJ community viewed what was possible in their weight class.",
                f"Influenced a generation of BJJ practitioners through competition footage, instructionals, and teaching — the {first_tech} system they developed is now studied worldwide."
            ],
            "tips": [
                f"Study the {first_tech} entry: Focus on how {name.split()[0]} creates the openings for their signature technique. The setup is often more important than the finish itself.",
                f"Analyze their guard retention: Elite competitors like {name.split()[0]} have exceptional guard retention mechanics. Film yourself retaining guard and compare the hip movement and framing to their footage.",
                f"Work on {known[1].replace('-',' ') if len(known) > 1 else 'transitions'}: This secondary technique connects directly to their primary game and creates multi-directional threats that are hard to defend.",
                "Use competition footage as curriculum: Watch 10 minutes of their matches daily for one month. Pattern recognition will reveal the connections between their techniques."
            ],
            "faq": [
                {"q": f"What is {name} known for in BJJ?", "a": f"{name} is primarily known for their exceptional {techs_str}. Their competition record of {titles_str} speaks to the effectiveness of their systematic approach to BJJ, and their techniques are studied by practitioners worldwide."},
                {"q": f"What team does {name} compete for?", "a": f"{name} is affiliated with {team}. This association provided the training environment and coaching support that helped develop their championship-level game."},
                {"q": f"What belt is {name} in BJJ?", "a": f"{name} holds a black belt in Brazilian Jiu-Jitsu and has competed extensively at the black belt level, accumulating {titles_str}."}
            ]
        }
    elif lang == "ja":
        tech2 = known[1].replace("-", " ") if len(known) > 1 else "ポジションコントロール"
        tech3 = known[2].replace("-", " ") if len(known) > 2 else "グラップリング"
        return {
            "title": f"{name} — BJJ世界王者・{first_tech}の達人 | BJJ Wiki",
            "meta": f"{name}「{nick}」は{techs_str}を得意とする{nat if nat else country}出身のBJJトップ選手。{'; '.join(titles[:2])}を達成。",
            "intro": f"{name}（ニックネーム「{nick}」）は{nat if nat else country}出身の最も実績あるBJJアスリートの一人です。{techs_str}における卓越した技術で知られ、{team}を拠点に世界トップレベルの競技実績を誇ります。特に{first_tech}の精度と{tech2}の完成度は同世代の選手の中でも際立っており、世界中のBJJ実践者が研究対象としています。",
            "biography": f"{name}は{nat if nat else country}でブラジリアン柔術（BJJ）のキャリアをスタートさせ、すぐにその才能を開花させました。{born + '年生まれ。' if born else ''}帯ランクを急速に駆け上がり、黒帯取得後はすぐに世界最高峰の大会での競技に専念した。{team}という最高の環境がその成長を加速させた。\n\n国際大会では着実にタイトルを重ねていった。{titles_str}という輝かしい実績は、彼らのシステマティックなアプローチの正しさを証明するものだ。特に{first_tech}を軸にした一貫したゲームプランは、どんな相手にも通用する普遍性を持っている。体重クラス内で最も恐れられる競技者の一人として、その試合は世界中の選手・コーチが徹底的に研究している。\n\nまた{name}は競技実績だけでなく、後進の指導やインストラクショナル制作を通じてBJJコミュニティ全体に多大な貢献を果たしている。{first_tech}と{tech2}の組み合わせが現代BJJの技術基盤に与えた影響は計り知れない。技術的優位性が体格差を凌駕できることを実証し続けるキャリアは、世界中のBJJ実践者の手本となっている。\n\n現在も{team}を拠点に指導・競技を続け、チャンピオンシップキャリアで得た洞察を次世代のBJJアスリートへ伝承している。",
            "style_analysis": f"{name}のゲームは{techs_str}の卓越した技術によって定義される。各ムーブが明確な目的を持ち、ポジションコントロールを最大化するように設計されている。シグネチャーポジションの深度は競合他者が容易にカウンターできないほどに磨き上げられており、一度その体勢に持ち込まれると脱出は極めて困難になる。\n\n特に{first_tech}と{tech2}の組み合わせは同選手のゲームの核心を成している。攻撃と防御がシームレスに繋がる設計になっており、相手がエスケープや反撃を試みると、かえって更に不利なポジションへ追い込まれることが多い。この「守りから攻めへの転換」こそがエリートBJJの証である。試合を通じたペース管理と集中力の維持も同選手の特徴で、終盤でも技術の精度が落ちない。",
            "signature_technique": f"{name}の最も象徴的なテクニックは{first_tech}。独自のエントリー・セットアップ・フィニッシュの細部を磨き上げ、他の選手との決定的な差別化を実現している。この技は単独で機能するのではなく、{tech2}や{tech3}との連携の中で初めて最大限の効果を発揮する。試合映像でこの技へのエントリーを徹底的に研究することが、上達の最短経路になる。",
            "why_study": f"{name}のゲームを学ぶことで、エリートレベルのBJJメカニクスへの深い理解が得られる。{first_tech}とガードシステムは、純粋な運動能力ではなく技術的卓越性がチャンスを生み出すことを明確に示している。体重・体格差があっても技術で上回れることを証明した選手の一人であり、全体重クラスの実践者にとって普遍的な学びを提供する。中〜上級者には同選手の試合映像が特に価値があり、複数のポジションを一貫したゲームプランに統合する方法を学べる。初心者にとっても、基本的なポジションがチャンピオンレベルにまで昇華されたモデルを見ることができる。",
            "highlights": [
                f"{techs_str}での複数の世界選手権優勝。BJJ史上最も多くのタイトルを獲得した選手の一人としての不動の地位を確立した。",
                f"IBJJFおよびADCCトーナメントでの継続的な好成績。複数の体重クラスで世界レベルの相手を次々と下し続けた。",
                f"タイトル実績：{'; '.join(titles[:2])}。この成績は体重クラスにおける競技水準そのものを引き上げるインパクトを持った。",
                f"競技映像・インストラクショナル・指導を通じた{first_tech}システムの普及。現代BJJの技術基盤の一部として世界中で活用されている。"
            ],
            "tips": [
                f"{first_tech}エントリーを徹底研究：{name.split()[0]}がシグネチャーテクニックへの開口部を作る方法に焦点を当てよう。フィニッシュよりもセットアップとエントリーの質が最終的な成功率を左右することが多い。",
                f"ガードリテンションメカニクスを分析：{name.split()[0]}の卓越したガードリテンションは意図的な練習の産物だ。自分のガードリテンションを動画で撮影し、ヒップムーブメントとフレーミングを試合映像と比較することで改善点が見えてくる。",
                f"{tech2}の練習量を増やす：プライマリーゲームと直接連結するこの技術は多方向の脅威を作り出す。{first_tech}だけに集中するより、{tech2}との連携を意識したドリルが実戦力を高める。",
                "試合映像を反復視聴する：毎日10分間、1ヶ月継続して視聴することで技術間の連携パターンが自然と見えてくる。特に同じシーケンスが繰り返されるパターンに注目しよう。"
            ],
            "faq": [
                {"q": f"{name}はBJJで何が有名ですか？", "a": f"{name}は主に{techs_str}の卓越した技術で知られています。{titles_str}という実績はシステマティックなアプローチの有効性を証明しており、その技術は世界中の選手・コーチに研究されています。特に{first_tech}の精度は同ウエイトクラスで最高水準と評価されています。"},
                {"q": f"{name}はどのチームに所属していますか？", "a": f"{name}は{team}に所属しています。この環境が世界王者レベルのゲームを開発するための最高のトレーニング条件を提供しました。チームのメソドロジーが同選手のシステマティックな技術開発の基盤となっています。"},
                {"q": f"{name}から学べる最も重要な技術は何ですか？", "a": f"{name}から学ぶべき最重要テクニックは{first_tech}です。このテクニックはさらに{tech2}や{tech3}と組み合わせることで真価を発揮します。試合映像とインストラクショナルの両方を活用して、エントリーからフィニッシュまでの流れを体系的に学ぶことを推奨します。"}
            ]
        }
    else:  # pt
        return {
            "title": f"{name} — Campeão Mundial de BJJ e Grappler de Elite | BJJ Wiki",
            "meta": f"{name} '{nick}' é um competidor de BJJ de elite conhecido por {techs_str}. {titles_str}.",
            "intro": f"{name}, apelidado de '{nick}', é um dos atletas de Brazilian Jiu-Jitsu mais realizados de {nat if nat else country}. Conhecido por habilidade excepcional em {techs_str}, conquistou uma reputação como um dos competidores mais tecnicamente refinados do esporte, treinando pela {team}.",
            "biography": f"{name} começou a treinar Brazilian Jiu-Jitsu e rapidamente demonstrou talento natural para o esporte. {'Nascido em ' + born + ', ' if born else ''}progrediu pelas faixas em ritmo acelerado, conquistando a faixa preta e imediatamente competindo nos mais altos níveis. A afiliação com {team} proporcionou parceiros de treino e coaching de classe mundial.\n\nNo circuito de competição, {name} acumulou título após título: {titles_str}. Suas performances em grandes torneios o estabeleceram como um dos competidores mais temidos de sua categoria. Atletas e técnicos em todo o mundo estudam seu jogo.\n\nAlém da competição, {name} contribuiu para a comunidade de BJJ através do ensino e instrucionais, demonstrando que o domínio técnico pode prevalecer sobre as vantagens físicas.",
            "style_analysis": f"O jogo de {name} é definido pela excelência em {techs_str}. Sua abordagem enfatiza precisão técnica sobre atletismo — cada movimento é intencional, cada transição projetada para maximizar o controle posicional. O que torna o estilo de {name.split()[0]} particularmente eficaz é a conexão perfeita entre ataque e defesa.",
            "signature_technique": f"A técnica mais icônica de {name} é o/a {first_tech}. Eles refinaram essa submissão/posição a um nível de maestria raramente visto na competição, desenvolvendo entradas, setups e detalhes de finalização únicos.",
            "why_study": f"Estudar o jogo de {name} oferece aos praticantes insights sobre a mecânica do BJJ de elite. Seu {first_tech} e sistema de guarda demonstram como a excelência técnica cria oportunidades que o puro atletismo não pode replicar.",
            "highlights": [
                f"Múltiplas vitórias em campeonatos mundiais em {', '.join(t.replace('-',' ') for t in known[:2])}, estabelecendo um legado como um dos competidores mais condecorados na história do BJJ.",
                f"Performance consistente em torneios do IBJJF e ADCC, derrotando oponentes de classe mundial em múltiplas categorias.",
                f"Títulos: {'; '.join(titles[:2])} — performances que mudaram como a comunidade de BJJ via o que era possível em sua categoria.",
                f"Influenciou uma geração de praticantes de BJJ através de filmagens de competição, instrucionais e ensinamentos."
            ],
            "tips": [
                f"Estude a entrada do {first_tech}: Foque em como {name.split()[0]} cria as aberturas para sua técnica assinatura. O setup é frequentemente mais importante que o finish em si.",
                f"Analise a retenção de guarda: Competidores de elite como {name.split()[0]} têm mecânica excepcional de retenção de guarda. Filme-se retendo a guarda e compare o movimento de quadril.",
                f"Trabalhe em {known[1].replace('-',' ') if len(known) > 1 else 'transições'}: Esta técnica secundária se conecta diretamente ao jogo primário e cria ameaças multidirecionais.",
                "Use filmagens de competição como currículo: Assista 10 minutos das partidas deles diariamente por um mês."
            ],
            "faq": [
                {"q": f"Pelo que {name} é conhecido no BJJ?", "a": f"{name} é principalmente conhecido por seu excepcional {techs_str}. Seu histórico de {titles_str} demonstra a eficácia de sua abordagem sistemática ao BJJ."},
                {"q": f"Por qual equipe {name} compete?", "a": f"{name} é afiliado ao/à {team}. Esta associação proporcionou o ambiente de treino e suporte de coaching que ajudou a desenvolver seu jogo de nível campeão."},
                {"q": f"Qual é a faixa de {name} no BJJ?", "a": f"{name} possui faixa preta em Brazilian Jiu-Jitsu e competiu extensivamente no nível da faixa preta, acumulando {titles_str}."}
            ]
        }


def get_content(athlete, lang):
    """Get pre-written or template content for an athlete.
    For ja: always use template (template is richer than hand-written ja stubs).
    For en/pt: use pre-written if available."""
    if lang != "ja" and lang in athlete:
        return athlete[lang]
    return make_template_content(athlete, lang)


def build_html(athlete, content, lang):
    slug = athlete["slug"]
    name = athlete["name"]
    nickname = athlete.get("nickname", "")
    titles = athlete.get("titles", [])
    known_for = athlete.get("known_for", [])
    team = athlete.get("team", "")
    weight = athlete.get("weight", "")
    country = athlete.get("country", "")

    title_tag = content.get("title", f"{name} | BJJ Wiki")
    meta_desc = content.get("meta", "")
    intro = content.get("intro", "")
    biography = content.get("biography", "").replace("\n", "<br><br>")
    style_analysis = content.get("style_analysis", "").replace("\n", "<br>")
    signature_technique = content.get("signature_technique", "")
    why_study = content.get("why_study", "")
    career_highlights = content.get("highlights", content.get("career_highlights", []))
    training_tips = content.get("tips", content.get("training_tips", []))
    faqs = content.get("faq", [])

    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+09:00")
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    tech_links_html = "\n".join(
        f'<a href="{t}.html" class="tech-tag">🥋 {t.replace("-"," ").title()}</a>'
        for t in known_for[:6]
    )
    titles_html = "\n".join(f"<li>{t}</li>" for t in titles)
    highlights_html = "\n".join(f"<li>{h}</li>" for h in career_highlights)
    tips_html = "\n".join(f"<li>{t}</li>" for t in training_tips)

    faq_schema_items = [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs]
    faq_schema = json.dumps(faq_schema_items, ensure_ascii=False)
    faq_html = "\n".join(
        f'<div class="faq-item"><h3 class="faq-q">{f["q"]}</h3><p class="faq-a">{f["a"]}</p></div>'
        for f in faqs
    )

    lang_links = {
        "en": f'<a href="../../en/athlete-{slug}.html" class="{"active" if lang=="en" else ""}">🇺🇸 EN</a>',
        "ja": f'<a href="../../ja/athlete-{slug}.html" class="{"active" if lang=="ja" else ""}">🇯🇵 JA</a>',
        "pt": f'<a href="../../pt/athlete-{slug}.html" class="{"active" if lang=="pt" else ""}">🇧🇷 PT</a>',
    }

    L = {
        "en": {"back":"← All Athletes","bio":"Biography","style":"Fighting Style","sig":"Signature Technique",
               "study":"Why Study This Athlete","hl":"Career Highlights","tips":"Training Tips","faq":"Frequently Asked Questions",
               "cta_p":"Track your BJJ techniques and training progress","cta_btn":"Start Free on BJJ App →"},
        "ja": {"back":"← 選手一覧","bio":"経歴・バイオグラフィー","style":"戦闘スタイル分析","sig":"シグネチャーテクニック",
               "study":"この選手から学べること","hl":"キャリアハイライト","tips":"トレーニングのヒント","faq":"よくある質問",
               "cta_p":"技術とトレーニングを記録しよう","cta_btn":"BJJ Appを無料で始める →"},
        "pt": {"back":"← Todos os Atletas","bio":"Biografia","style":"Análise de Estilo de Luta","sig":"Técnica Assinatura",
               "study":"Por que Estudar Este Atleta","hl":"Destaques da Carreira","tips":"Dicas de Treinamento","faq":"Perguntas Frequentes",
               "cta_p":"Registre suas técnicas e progressos no BJJ","cta_btn":"Começar Grátis no BJJ App →"},
    }[lang]

    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title_tag}</title>
<meta name="description" content="{meta_desc}">
<meta property="og:title" content="{title_tag}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:image" content="{SITE_URL}/og-image.png">
<meta property="og:url" content="{SITE_URL}/{lang}/athlete-{slug}.html">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE_URL}/{lang}/athlete-{slug}.html">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/en/athlete-{slug}.html">
<link rel="alternate" hreflang="en" href="{SITE_URL}/en/athlete-{slug}.html">
<link rel="alternate" hreflang="ja" href="{SITE_URL}/ja/athlete-{slug}.html">
<link rel="alternate" hreflang="pt" href="{SITE_URL}/pt/athlete-{slug}.html">
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE}" crossorigin="anonymous"></script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":{faq_schema}}}
</script>
<style>
:root{{--bg:#0f172a;--card:#141926;--border:#1e293b;--text:#e2e8f0;--muted:#64748b;--accent:#e94560;--accent2:#a78bfa}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:16px;line-height:1.8;padding:0 16px}}
a{{color:var(--accent2);text-decoration:none}}a:hover{{text-decoration:underline}}
.container{{max-width:860px;margin:0 auto;padding-bottom:80px}}
header{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;padding:16px 0;border-bottom:1px solid var(--border);margin-bottom:24px}}
.logo{{font-size:1.2rem;font-weight:800;color:var(--accent)}}
.lang-nav{{display:flex;gap:8px}}
.lang-nav a{{color:var(--muted);font-size:.82rem;padding:4px 10px;border-radius:4px;border:1px solid var(--border)}}
.lang-nav a.active,.lang-nav a:hover{{color:var(--text);border-color:var(--accent)}}
.breadcrumb{{font-size:.78rem;color:var(--muted);margin-bottom:16px}}
.breadcrumb a{{color:var(--muted)}}
.hero{{background:linear-gradient(135deg,rgba(233,69,96,0.08),rgba(167,139,250,0.06));border:1px solid var(--border);border-radius:16px;padding:28px;margin-bottom:28px}}
.hero h1{{font-size:2rem;font-weight:800;margin-bottom:4px}}
.hero .nick{{color:var(--accent2);font-size:1rem;margin-bottom:14px}}
.badges{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}}
.badge{{background:#1e293b;color:var(--muted);font-size:.75rem;padding:3px 10px;border-radius:20px}}
.titles-list{{list-style:none;padding:0}}
.titles-list li{{padding:3px 0;color:#f59e0b;font-size:.9rem}}
.titles-list li::before{{content:"🏆 "}}
h2{{font-size:.88rem;font-weight:700;color:var(--accent2);text-transform:uppercase;letter-spacing:.07em;margin:28px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--border)}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px;font-size:.95rem;line-height:1.8}}
.card p{{margin-bottom:12px}}.card p:last-child{{margin-bottom:0}}
.tech-tags{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}}
.tech-tag{{display:inline-block;padding:5px 12px;background:#1e293b;border:1px solid var(--accent2);border-radius:20px;font-size:.8rem;color:var(--accent2);font-weight:600}}
.tech-tag:hover{{background:var(--accent2);color:#0f172a;text-decoration:none}}
ul.hl-list,ul.tips-list{{padding-left:20px;margin:0}}
ul.hl-list li,ul.tips-list li{{margin-bottom:10px;font-size:.93rem}}
.faq-item{{border-bottom:1px solid var(--border);padding:16px 0}}
.faq-item:last-child{{border-bottom:none;padding-bottom:0}}
.faq-q{{font-size:.95rem;font-weight:700;color:var(--text);margin-bottom:8px}}
.faq-a{{font-size:.9rem;color:var(--muted);line-height:1.7}}
.cta-box{{background:linear-gradient(135deg,rgba(233,69,96,0.12),rgba(167,139,250,0.08));border:1px solid rgba(233,69,96,0.4);border-radius:16px;padding:24px;text-align:center;margin:28px 0}}
.cta-box p{{color:var(--muted);margin-bottom:14px}}
.cta-btn{{display:inline-block;background:var(--accent);color:#fff;padding:12px 28px;border-radius:8px;font-weight:700;text-decoration:none}}
.cta-btn:hover{{opacity:.9;text-decoration:none}}
footer{{margin-top:48px;padding-top:16px;border-top:1px solid var(--border);text-align:center;color:var(--muted);font-size:.78rem;line-height:1.6}}
@media(max-width:600px){{.hero h1{{font-size:1.5rem}}}}
</style>
</head>
<body><div class="container">
<header>
  <a href="../index.html" class="logo">🥋 BJJ Wiki</a>
  <div class="lang-nav">{" ".join(lang_links.values())}</div>
</header>
<div class="breadcrumb"><a href="../index.html">BJJ Wiki</a> / <a href="athletes.html">Athletes</a> / {name}</div>
<div class="hero">
  <h1>{name}</h1>
  <div class="nick">"{nickname}"</div>
  <div class="badges">
    <span class="badge">🌍 {country}</span>
    <span class="badge">🥋 Black Belt</span>
    <span class="badge">⚖️ {weight}</span>
    <span class="badge">🏫 {team}</span>
  </div>
  <ul class="titles-list">{titles_html}</ul>
</div>
<div class="card" style="font-size:1rem;line-height:1.9">{intro}</div>
<h2>{L["bio"]}</h2>
<div class="card"><p>{biography}</p></div>
<h2>{L["style"]}</h2>
<div class="card"><p>{style_analysis}</p></div>
<h2>{L["sig"]}</h2>
<div class="card"><p>{signature_technique}</p><div class="tech-tags">{tech_links_html}</div></div>
<h2>{L["study"]}</h2>
<div class="card"><p>{why_study}</p></div>
<h2>{L["hl"]}</h2>
<div class="card"><ul class="hl-list">{highlights_html}</ul></div>
<h2>{L["tips"]}</h2>
<div class="card"><ul class="tips-list">{tips_html}</ul></div>
<h2>{L["faq"]}</h2>
<div class="card">{faq_html}</div>
<div class="cta-box"><p>{L["cta_p"]}</p><a href="{APP_URL}" class="cta-btn">{L["cta_btn"]}</a></div>
<footer>BJJ Wiki — Free multilingual encyclopedia · Last updated: {today} · <a href="../privacy.html">Privacy</a> · <a href="../about.html">About</a></footer>
</div></body></html>'''


def main():
    import argparse, sys
    parser = argparse.ArgumentParser()
    parser.add_argument("--langs", default="en,ja,pt")
    parser.add_argument("--slug", help="Single athlete slug")
    args = parser.parse_args()
    langs = args.langs.split(",")

    todo = [a for a in ATHLETES if not args.slug or a["slug"] == args.slug]
    print(f"Generating {len(todo)} athletes × {len(langs)} langs = {len(todo)*len(langs)} pages")

    total = 0
    for athlete in todo:
        for lang in langs:
            out_dir = os.path.join(BASE, lang)
            os.makedirs(out_dir, exist_ok=True)
            path = os.path.join(out_dir, f"athlete-{athlete['slug']}.html")
            content = get_content(athlete, lang)
            html = build_html(athlete, content, lang)
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            words = len(re.sub(r'<[^>]+>', ' ', html).split())
            print(f"  ✅ {lang}/athlete-{athlete['slug']}.html ({words} words)")
            total += 1

    print(f"\n✅ Done: {total} pages written")

if __name__ == "__main__":
    main()
