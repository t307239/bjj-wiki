#!/usr/bin/env python3
"""
BJJ Wiki Batch 412-416
5 themes × 3 languages = 15 new pages

Topics:
  412: bjj-open-guard-mastery        — Complete open guard mastery system
  413: bjj-pressure-passing-advanced — Advanced pressure passing strategies
  414: bjj-mount-control-details     — Detailed mount control mechanics
  415: bjj-double-guard-pull         — Double guard pull tactics & strategy
  416: bjj-bottom-game-mastery       — Complete bottom game mastery
"""

import os, re

WIKI_DIR = os.path.join(os.path.dirname(__file__), "..")
BASE_URL  = "https://wiki.bjj-app.net"

TOPICS = [
    {
        "slug": "bjj-open-guard-mastery",
        "en": {
            "title": "BJJ Open Guard Mastery — Complete System",
            "desc": "Master open guard in BJJ with a complete system covering guard maintenance, sweeps, attacks, and transitions from all open guard positions.",
            "difficulty": "intermediate",
            "diff_label": "Intermediate",
            "h1": "BJJ Open Guard Mastery",
            "intro": "Open guard is the foundation of modern BJJ. Unlike closed guard, open guard positions rely on frames, grips, and foot/knee placement to control distance and create attack angles. Mastering open guard means being able to maintain, sweep, attack, and transition between positions fluidly — making you a threat from anywhere on the bottom.",
            "concepts": [
                ("Why Open Guard Wins Matches", "Open guard gives you access to the widest range of sweeps and submissions. When your opponent cannot predict which guard you'll play, they must approach cautiously — giving you the initiative to dictate the pace."),
                ("Frames and Distance Management", "Effective open guard begins with proper framing: using your elbows, knees, and feet as barriers that prevent your opponent from collapsing your guard or passing. Distance management is the invisible skill that separates good open guard players from great ones."),
                ("Grip Hierarchy", "In gi, the dominant grip hierarchy flows from collar → sleeve → pants. The collar grip threatens chokes and sweeps simultaneously. Sleeve grips control arm movement. Pants grips set up leg entanglements and tripod sweeps."),
                ("Guard Maintenance Under Pressure", "When a skilled passer applies pressure, your guard will be tested. Key principles: recover your hips before your opponent can settle, use your knees as primary frames, and always have a re-guard path planned before you need it."),
                ("Chaining Guards Together", "Elite grapplers don't play one guard — they move fluidly between spider, DLR, X-guard, and lasso as the opponent tries to pass. Building a guard system means having transitions between guards that are as dangerous as the guards themselves."),
            ],
            "steps": [
                ("Establish Your Preferred Guard", "From the bottom, choose your primary guard based on opponent size and style. Against bigger opponents, spider or lasso guard; against faster opponents, DLR or shin-on-shin."),
                ("Control the Sleeve or Wrist", "Establish a sleeve grip (gi) or wrist control (no-gi) to prevent your opponent from freely posting and passing. This single control determines the direction of all your attacks."),
                ("Create the Angle", "Never attack straight ahead — shift your hips 30-45 degrees to create a dominant angle. This angle is what transforms a stalemate into a sweep or submission entry."),
                ("Sweep or Attack", "With proper angle and grips established, choose your primary threat: sweep to force a reaction, then attack the submission that opens up. Your opponent cannot defend both simultaneously."),
                ("Maintain During the Scramble", "If swept or if the opponent starts passing, immediately implement your re-guard protocol: post on an elbow, hip escape, and replace your frames before the guard is fully passed."),
            ],
            "cta": "🥋 Track Your Guard Game with BJJ App →",
        },
        "ja": {
            "title": "BJJ オープンガード完全マスター",
            "desc": "BJJのオープンガードを完全に習得するシステム。ガード維持・スウィープ・アタック・ポジション間のトランジションを解説。",
            "difficulty": "intermediate",
            "diff_label": "中級",
            "h1": "BJJ オープンガード マスターシステム",
            "intro": "オープンガードは現代BJJの基盤です。クローズドガードと異なり、フレーム・グリップ・足とひざの配置で距離をコントロールしてアタックの角度を作ります。オープンガードをマスターすることは、維持・スウィープ・アタック・ポジション間のスムーズな移行ができることを意味し、ボトムからどこでも脅威になれます。",
            "concepts": [
                ("なぜオープンガードが試合を制するか", "オープンガードは最も広いスウィープとサブミッションへのアクセスを提供します。対戦相手がどのガードを使うかを予測できなければ、慎重にならざるを得ず、あなたがペースを支配するイニシアティブを得ます。"),
                ("フレームとディスタンス管理", "効果的なオープンガードはフレームから始まります：肘・膝・足をバリアとして使い、相手がガードを崩したりパスしたりするのを防ぎます。ディスタンス管理こそが、良いオープンガードプレイヤーと優れたプレイヤーを分ける目に見えないスキルです。"),
                ("グリップの優先順位", "道衣では、支配的なグリップ階層は衿→袖→ズボンの順です。衿グリップはチョークとスウィープを同時に脅かします。袖グリップは腕の動きをコントロールします。ズボングリップはレッグエンタングルメントとトライポッドスウィープをセットアップします。"),
                ("プレッシャー下でのガード維持", "熟練したパッサーがプレッシャーをかけると、ガードは試されます。主要原則：相手が落ち着く前にヒップをリカバーする、膝を主要フレームとして使う、そして必要になる前にリガードのパスを計画しておく。"),
                ("ガードのチェーン", "一流のグラップラーはひとつのガードをプレイせず、相手がパスしようとするにつれて、スパイダー・DLR・Xガード・ラッソの間を流れるように移動します。ガードシステムを構築することは、ガード自体と同じくらい危険なガード間のトランジションを持つことを意味します。"),
            ],
            "steps": [
                ("好みのガードを確立する", "ボトムから、相手のサイズとスタイルに基づいて主要なガードを選択します。大きな相手にはスパイダーやラッソガード、速い相手にはDLRやシン・オン・シン。"),
                ("袖またはリストをコントロールする", "袖グリップ（道衣）またはリストコントロール（ノーギ）を確立し、相手がポストしてパスするのを防ぎます。このシングルコントロールがすべてのアタックの方向を決定します。"),
                ("角度を作る", "真正面からアタックしない — ヒップを30〜45度シフトして支配的な角度を作ります。この角度が膠着状態をスウィープまたはサブミッションエントリーに変えます。"),
                ("スウィープまたはアタック", "適切な角度とグリップが確立されたら、主要な脅威を選択します：スウィープで反応を引き出し、開いたサブミッションをアタックします。相手は両方を同時に防ぐことができません。"),
                ("スクランブル中の維持", "スウィープされたり相手がパスを開始したりした場合は、すぐにリガードプロトコルを実施します：肘でポスト、ヒップエスケープ、そしてガードが完全にパスされる前にフレームを戻す。"),
            ],
            "cta": "🥋 BJJ Appでガードゲームを記録しよう →",
        },
        "pt": {
            "title": "Maestria na Guarda Aberta de BJJ",
            "desc": "Domine a guarda aberta no BJJ com um sistema completo cobrindo manutenção, raspagens, ataques e transições entre posições.",
            "difficulty": "intermediate",
            "diff_label": "Intermediário",
            "h1": "Maestria na Guarda Aberta de BJJ",
            "intro": "A guarda aberta é a base do BJJ moderno. Ao contrário da guarda fechada, as posições de guarda aberta dependem de frames, pegadas e posicionamento de pés/joelhos para controlar a distância e criar ângulos de ataque. Dominar a guarda aberta significa ser capaz de manter, rapar, atacar e transicionar entre posições fluidamente — tornando-se uma ameaça de qualquer lugar por baixo.",
            "concepts": [
                ("Por que a Guarda Aberta Vence Lutas", "A guarda aberta dá acesso à mais ampla gama de raspagens e finalizações. Quando seu oponente não consegue prever qual guarda você vai jogar, ele deve se aproximar com cautela — dando a você a iniciativa de ditar o ritmo."),
                ("Frames e Gerenciamento de Distância", "A guarda aberta eficaz começa com um enquadramento adequado: usando cotovelos, joelhos e pés como barreiras que impedem seu oponente de colapsar sua guarda ou passar. O gerenciamento de distância é a habilidade invisível que separa bons jogadores de guarda aberta dos grandes."),
                ("Hierarquia de Pegadas", "No gi, a hierarquia dominante de pegadas flui de gola → manga → calça. A pegada na gola ameaça estrangulamentos e raspagens simultaneamente. As pegadas na manga controlam o movimento do braço. As pegadas na calça configuram entrelaçamentos de pernas e raspagens de tripé."),
                ("Manutenção da Guarda Sob Pressão", "Quando um passador habilidoso aplica pressão, sua guarda será testada. Princípios chave: recupere seus quadris antes que seu oponente possa se estabilizar, use seus joelhos como frames primários, e sempre tenha um caminho de re-guarda planejado antes de precisar."),
                ("Encadeando Guardas", "Grapplistas de elite não jogam uma guarda — eles se movem fluidamente entre spider, DLR, X-guard e lasso enquanto o oponente tenta passar. Construir um sistema de guarda significa ter transições entre guardas tão perigosas quanto as guardas em si."),
            ],
            "steps": [
                ("Estabeleça sua Guarda Preferida", "De baixo, escolha sua guarda principal com base no tamanho e estilo do oponente. Contra oponentes maiores, guarda spider ou lasso; contra oponentes mais rápidos, DLR ou shin-on-shin."),
                ("Controle a Manga ou o Pulso", "Estabeleça uma pegada na manga (gi) ou controle do pulso (no-gi) para evitar que seu oponente poste e passe livremente. Este único controle determina a direção de todos os seus ataques."),
                ("Crie o Ângulo", "Nunca ataque de frente — desloque seus quadris 30-45 graus para criar um ângulo dominante. Este ângulo é o que transforma um impasse em uma entrada de raspagem ou finalização."),
                ("Raspar ou Atacar", "Com ângulo e pegadas adequados estabelecidos, escolha sua ameaça principal: raspar para forçar uma reação, depois ataque a finalização que se abre. Seu oponente não pode defender ambas simultaneamente."),
                ("Manter Durante o Scramble", "Se raspado ou se o oponente começar a passar, implemente imediatamente seu protocolo de re-guarda: poste em um cotovelo, escape de quadril, e recoloque seus frames antes que a guarda seja totalmente passada."),
            ],
            "cta": "🥋 Registre seu Jogo de Guarda com BJJ App →",
        },
    },
    {
        "slug": "bjj-pressure-passing-advanced",
        "en": {
            "title": "Advanced Pressure Passing in BJJ — Complete Guide",
            "desc": "Master advanced pressure passing in BJJ. Learn how to shut down modern guards with weight distribution, hip control, and sequential passing attacks.",
            "difficulty": "advanced",
            "diff_label": "Advanced",
            "h1": "Advanced Pressure Passing in BJJ",
            "intro": "Pressure passing is the style of passing that relies on weight, friction, and physicality to flatten and control the bottom player before completing the pass. Unlike speed passing, pressure passing works especially well against flexible, mobile guard players because it removes the space they need to replace guard and attack. Mastering pressure passing creates a guard-breaking system that works at all levels.",
            "concepts": [
                ("The Core Principle: Remove Space", "Pressure passing is fundamentally about eliminating the gap between your body and your opponent's. When space is removed, the bottom player cannot hip escape, replace guard, or generate the movement needed for sweeps and submissions."),
                ("Hip Position Dominance", "In pressure passing, your hips always stay below your opponent's hips or directly over them. This prevents them from generating upward force to replace guard. Low hip position also lets you use your bodyweight efficiently."),
                ("Weight Distribution Science", "The best pressure passers distribute weight precisely: heavy on the opponent's hips/thighs, light on your own feet (allows quick repositioning). Never put all weight in one spot — create a moving pressure that shifts with the opponent."),
                ("Sequential Pressure Attacks", "Single-direction passes are easy to defend. Elite pressure passers chain multiple threats: start with a knee slide, when blocked shift to over-under, when defended pivot to a smash pass. The sequential nature exhausts the bottom player."),
                ("Handling Mobile Guards", "Against spider and lasso guard, break grips first before attempting pressure. Against DLR, stack the hips before trying to pass. The grip-break-then-pressure sequence is standard protocol."),
            ],
            "steps": [
                ("Establish the Initial Grip Break", "Before applying any pressure, strip the most dangerous grip. Against collar-sleeve: break the collar grip. Against spider: peel the foot off your bicep. Only pressure once grips are neutralized."),
                ("Drop Your Weight", "Once grip is broken, drop your weight immediately onto the opponent's thighs/hips. Use the crossface or shoulder pressure to flatten them as you settle your weight."),
                ("Control the Far Hip", "Reach across and pin the far hip to the mat. This prevents the standard hip escape. With both hips flattened, the bottom player's guard options drop dramatically."),
                ("Walk Around to Complete", "With weight settled and hips pinned, slowly walk your legs around toward side control. Keep pressure constant throughout — any lifting of your weight gives the opponent room to re-guard."),
                ("Secure Side Control", "As you clear the legs, drive your chest into the opponent's chest and establish a cross-face. Heavy side control pressure prevents any immediate escape attempts."),
            ],
            "cta": "🥋 Log Your Passing Progress with BJJ App →",
        },
        "ja": {
            "title": "BJJ アドバンストプレッシャーパッシング完全ガイド",
            "desc": "BJJのアドバンストプレッシャーパッシングをマスターする。体重配分・ヒップコントロール・連続パスアタックで現代のガードを封じる方法を学ぶ。",
            "difficulty": "advanced",
            "diff_label": "上級",
            "h1": "BJJ アドバンスト プレッシャーパッシング",
            "intro": "プレッシャーパッシングは、体重・摩擦・フィジカリティに依存して、ボトムプレイヤーを潰してコントロールしてからパスを完成させるパッシングスタイルです。スピードパッシングと異なり、プレッシャーパッシングは特に柔軟でモバイルなガードプレイヤーに対して効果的です。なぜなら、彼らがリガードやアタックに必要なスペースを奪うからです。",
            "concepts": [
                ("核心原則：スペースを取り除く", "プレッシャーパッシングは基本的に、自分の体と相手の体の間の隙間を排除することです。スペースが取り除かれると、ボトムプレイヤーはヒップエスケープ、リガード、スウィープやサブミッションに必要な動きを生成できません。"),
                ("ヒップポジションの支配", "プレッシャーパッシングでは、自分のヒップは常に相手のヒップの下か直接その上に置きます。これにより、相手はガードを戻す上向きの力を生成できません。低いヒップポジションにより、体重を効率的に使えます。"),
                ("体重配分のサイエンス", "最高のプレッシャーパッサーは体重を正確に配分します：相手のヒップ/太ももに重く、自分の足は軽く（素早い位置変更を可能にする）。一か所にすべての体重を置かない — 相手と共に移動する動くプレッシャーを作る。"),
                ("連続プレッシャーアタック", "一方向のパスは防御しやすい。一流のプレッシャーパッサーは複数の脅威をチェーンします：ニースライドから始め、ブロックされたらオーバーアンダーにシフト、防御されたらスマッシュパスにピボット。この連続的な性質がボトムプレイヤーを疲弊させます。"),
                ("モバイルガードの扱い方", "スパイダーやラッソガードに対しては、プレッシャーを試みる前にグリップを崩す。DLRに対しては、パスを試みる前にヒップをスタックする。グリップ崩し→プレッシャーの順序が標準プロトコルです。"),
            ],
            "steps": [
                ("最初のグリップ崩しを確立する", "プレッシャーをかける前に、最も危険なグリップを剥がす。衿・袖に対しては衿グリップを崩す。スパイダーに対しては足を上腕二頭筋から剥がす。グリップが無効化されてからだけプレッシャーをかける。"),
                ("体重を落とす", "グリップが崩れたら、すぐに相手の太もも/ヒップに体重を落とす。クロスフェイスや肩プレッシャーを使って、体重を落としながら相手を平らにする。"),
                ("ファーヒップをコントロールする", "手を伸ばして遠いヒップをマットに固定する。これにより標準的なヒップエスケープが防止される。両ヒップが平らになると、ボトムプレイヤーのガードオプションが大幅に減少する。"),
                ("周りを歩いて完成させる", "体重が安定してヒップが固定されたら、ゆっくりと脚をサイドコントロールの方向に歩かせる。常にプレッシャーを保つ — 体重をリフトすると相手にリガードのスペースを与えてしまう。"),
                ("サイドコントロールを確保する", "脚をクリアするにつれて、胸を相手の胸に押し付けてクロスフェイスを確立する。重いサイドコントロールプレッシャーにより、即座のエスケープの試みが防止される。"),
            ],
            "cta": "🥋 BJJ AppでパッシングをログJしよう →",
        },
        "pt": {
            "title": "Passagem por Pressão Avançada no BJJ",
            "desc": "Domine a passagem por pressão avançada no BJJ. Aprenda a fechar guardas modernas com distribuição de peso, controle de quadril e ataques de passagem sequenciais.",
            "difficulty": "advanced",
            "diff_label": "Avançado",
            "h1": "Passagem por Pressão Avançada no BJJ",
            "intro": "A passagem por pressão é o estilo de passagem que depende de peso, fricção e fisicalidade para achatar e controlar o jogador de baixo antes de completar a passagem. Ao contrário da passagem por velocidade, a passagem por pressão funciona especialmente bem contra jogadores de guarda flexíveis e móveis porque remove o espaço que precisam para repor a guarda e atacar.",
            "concepts": [
                ("O Princípio Central: Remover Espaço", "A passagem por pressão é fundamentalmente sobre eliminar a lacuna entre seu corpo e o do oponente. Quando o espaço é removido, o jogador de baixo não pode escapar de quadril, repor a guarda ou gerar o movimento necessário para raspagens e finalizações."),
                ("Dominância do Posicionamento do Quadril", "Na passagem por pressão, seus quadris ficam sempre abaixo dos quadris do oponente ou diretamente sobre eles. Isso evita que gerem força para cima para repor a guarda. A posição baixa do quadril também permite usar o peso corporal com eficiência."),
                ("Ciência da Distribuição de Peso", "Os melhores passadores por pressão distribuem o peso com precisão: pesado nos quadris/coxas do oponente, leve em seus próprios pés (permite reposicionamento rápido). Nunca coloque todo o peso em um único ponto — crie uma pressão em movimento que se desloca com o oponente."),
                ("Ataques de Pressão Sequenciais", "Passagens de direção única são fáceis de defender. Passadores de pressão de elite encadeiam múltiplas ameaças: começam com knee slide, quando bloqueados mudam para over-under, quando defendidos giram para smash pass. A natureza sequencial exaure o jogador de baixo."),
                ("Lidando com Guardas Móveis", "Contra guarda spider e lasso, quebre as pegadas antes de tentar a pressão. Contra DLR, empilhe os quadris antes de tentar passar. A sequência quebra-pegada-então-pressão é o protocolo padrão."),
            ],
            "steps": [
                ("Estabeleça a Quebra de Pegada Inicial", "Antes de aplicar qualquer pressão, tire a pegada mais perigosa. Contra gola-manga: quebre a pegada na gola. Contra spider: descole o pé do seu bíceps. Pressione apenas depois que as pegadas forem neutralizadas."),
                ("Deixe Cair seu Peso", "Uma vez quebrada a pegada, deixe cair seu peso imediatamente nas coxas/quadris do oponente. Use o crossface ou pressão de ombro para achatá-los enquanto assenta seu peso."),
                ("Controle o Quadril Distante", "Alcance e prenda o quadril distante no tatame. Isso evita o escape de quadril padrão. Com ambos os quadris achatados, as opções de guarda do jogador de baixo caem dramaticamente."),
                ("Caminhe Ao Redor para Completar", "Com o peso assentado e os quadris presos, caminhe lentamente suas pernas em direção ao controle lateral. Mantenha a pressão constante durante todo o processo — qualquer levantamento do seu peso dá ao oponente espaço para re-guardar."),
                ("Assegure o Controle Lateral", "Ao limpar as pernas, empurre seu peito contra o peito do oponente e estabeleça um crossface. A pressão pesada do controle lateral previne qualquer tentativa imediata de fuga."),
            ],
            "cta": "🥋 Registre sua Passagem com BJJ App →",
        },
    },
    {
        "slug": "bjj-mount-control-details",
        "en": {
            "title": "Mount Control Details in BJJ — Dominating from Top",
            "desc": "Learn the detailed mechanics of mount control in BJJ. Master weight distribution, hip position, arm control, and submission chains from the mount.",
            "difficulty": "intermediate",
            "diff_label": "Intermediate",
            "h1": "BJJ Mount Control — Detailed Mechanics",
            "intro": "Mount is one of the highest scoring positions in BJJ, but many practitioners struggle to maintain it effectively. True mount mastery goes beyond just sitting on your opponent — it requires precise weight distribution, proactive hip control, and the ability to switch between high and low mount to maximize pressure while setting up submissions.",
            "concepts": [
                ("High vs. Low Mount", "Low mount (hips near opponent's hips) provides stability and makes escape attempts difficult. High mount (hips near the chest/armpits) opens submission opportunities but is harder to maintain. Elite grapplers switch between the two fluidly."),
                ("Weight Distribution in Mount", "Never post your weight on your hands — keep it all on your hips. Hands should float or be actively attacking. Hip-to-hip contact creates the most stable, heaviest mount. Sink your weight into the mat through the opponent."),
                ("The Grapevine vs. Foot Positions", "Grapevine (feet hooked inside opponent's legs) immobilizes the bottom player completely but limits your mobility. Feet-flat position (feet outside the hips) allows better movement for submission entries. Choose based on opponent's escape attempts."),
                ("Arm Control Hierarchy", "From mount, arm control determines your submission options. Underhook = Ezekiel choke or gift wrap. Overhook = armbar or triangle setup. Both arms free = crossface and collar choke options."),
                ("Preventing the Upa and Elbow Escape", "The two main mount escapes are upa (bridge and roll) and elbow escape. For upa: widen your base and post a hand when you feel the bridge. For elbow escape: keep knees heavy on the ground, float your hips to counter the hip escape."),
            ],
            "steps": [
                ("Establish Base and Weight", "When transitioning to mount, immediately widen your knees and drop your hips. Crossface the head with one arm to control posture and prevent the upa before it starts."),
                ("Choose Your Height", "Assess the situation: opponent is bridging → drop to low mount and widen knees. Opponent is flat → advance to high mount and start working submission grips."),
                ("Control the Arms", "Reach down and collect an underhook, or use a palm-down post on the shoulder to begin working the gift wrap. Arm control is the gateway to every mount submission."),
                ("Attack with Submission Chains", "In high mount, attack the Ezekiel choke first. If defended, work to S-mount for the armbar. If they straighten the arm, transition to the triangle. The chain prevents any single defensive answer."),
                ("Maintain Through Transitions", "When the opponent successfully starts an elbow escape, float your hips and slide your knee back in under their thigh. Constantly readjust your position to stay ahead of the escape attempt."),
            ],
            "cta": "🥋 Track Your Top Game with BJJ App →",
        },
        "ja": {
            "title": "BJJ マウントコントロール詳細解説",
            "desc": "BJJにおけるマウントコントロールの詳細なメカニクスを学ぶ。体重配分・ヒップポジション・アームコントロール・サブミッションチェーンを解説。",
            "difficulty": "intermediate",
            "diff_label": "中級",
            "h1": "BJJ マウントコントロール — 詳細メカニクス",
            "intro": "マウントはBJJで最も高得点のポジションのひとつですが、多くの練習者が効果的に維持することに苦労しています。真のマウントマスタリーは単に相手の上に座ること以上のものです — 正確な体重配分・積極的なヒップコントロール・そしてプレッシャーを最大化しながらサブミッションをセットアップするためにハイとローのマウントを切り替える能力が必要です。",
            "concepts": [
                ("ハイマウント vs ローマウント", "ローマウント（ヒップが相手のヒップ近く）は安定性を提供し、エスケープの試みを難しくします。ハイマウント（ヒップが胸/脇の近く）はサブミッションの機会を開きますが維持が難しい。一流のグラップラーは両者の間を流れるように切り替えます。"),
                ("マウントでの体重配分", "手に体重をポストしない — すべてをヒップに置く。手は浮かせるかアクティブにアタックすべきです。ヒップ対ヒップの接触が最も安定した重いマウントを作ります。相手を通してマットに体重を沈める。"),
                ("グレープバイン vs フットポジション", "グレープバイン（足を相手の足の内側にフック）はボトムプレイヤーを完全に動けなくしますが、自分の機動性を制限します。フラットフット（ヒップの外側）はサブミッションエントリーのための動きを良くします。相手のエスケープの試みに基づいて選択する。"),
                ("アームコントロールの階層", "マウントからのアームコントロールがサブミッションオプションを決定します。アンダーフック = エゼキエルチョークまたはギフトラップ。オーバーフック = アームバーまたはトライアングルセットアップ。両腕フリー = クロスフェイスとカラーチョークオプション。"),
                ("ウパとエルボーエスケープの防止", "主な2つのマウントエスケープはウパ（ブリッジアンドロール）とエルボーエスケープです。ウパに対して：ベースを広げ、ブリッジを感じたら手でポストする。エルボーエスケープに対して：膝をグラウンドに重く保ち、ヒップエスケープに対抗するためヒップを浮かせる。"),
            ],
            "steps": [
                ("ベースと体重を確立する", "マウントにトランジションするとき、すぐに膝を広げてヒップを落とす。ウパが始まる前に防ぐために、片腕で頭をクロスフェイスしてポスチャーをコントロールする。"),
                ("高さを選択する", "状況を評価する：相手がブリッジしている → ローマウントに落として膝を広げる。相手が平らになっている → ハイマウントに進んでサブミッショングリップの作業を始める。"),
                ("アームをコントロールする", "手を伸ばしてアンダーフックを取るか、肩に手掌を下向きにポストしてギフトラップの作業を始める。アームコントロールはすべてのマウントサブミッションへの入り口です。"),
                ("サブミッションチェーンでアタックする", "ハイマウントで、まずエゼキエルチョークをアタックする。防御されたら、アームバーのためにSマウントに移る。腕を伸ばしたら、トライアングルにトランジションする。このチェーンにより、単一の防御的な答えが防止される。"),
                ("トランジション中に維持する", "相手がエルボーエスケープを始めたら、ヒップを浮かせて膝を相手の太ももの下に滑り込ませる。常にポジションを再調整して、エスケープの試みより先を行く。"),
            ],
            "cta": "🥋 BJJ Appでトップゲームを記録しよう →",
        },
        "pt": {
            "title": "Detalhes do Controle de Monte no BJJ",
            "desc": "Aprenda a mecânica detalhada do controle de monte no BJJ. Domine distribuição de peso, posição de quadril, controle de braço e encadeamento de finalizações.",
            "difficulty": "intermediate",
            "diff_label": "Intermediário",
            "h1": "Controle de Monte no BJJ — Mecânica Detalhada",
            "intro": "O monte é uma das posições de maior pontuação no BJJ, mas muitos praticantes têm dificuldade em mantê-lo efetivamente. A verdadeira maestria no monte vai além de apenas sentar no oponente — requer distribuição precisa de peso, controle proativo do quadril e a capacidade de alternar entre monte alto e baixo para maximizar a pressão enquanto configura finalizações.",
            "concepts": [
                ("Monte Alto vs. Monte Baixo", "Monte baixo (quadris perto dos quadris do oponente) proporciona estabilidade e torna as tentativas de fuga difíceis. Monte alto (quadris perto do peito/axilas) abre oportunidades de finalização, mas é mais difícil de manter. Grapplistas de elite alternam entre os dois fluidamente."),
                ("Distribuição de Peso no Monte", "Nunca poste seu peso nas mãos — mantenha tudo nos quadris. As mãos devem flutuar ou estar atacando ativamente. Contato quadril a quadril cria o monte mais estável e pesado. Afunde seu peso no tatame através do oponente."),
                ("Grapevine vs. Posições dos Pés", "Grapevine (pés dentro das pernas do oponente) imobiliza o jogador de baixo completamente, mas limita sua mobilidade. Pés planos (fora dos quadris) permite melhor movimento para entradas de finalização. Escolha com base nas tentativas de fuga do oponente."),
                ("Hierarquia de Controle de Braço", "Do monte, o controle de braço determina suas opções de finalização. Underhook = estrangulamento de Ezequiel ou gift wrap. Overhook = armlock ou triângulo. Ambos os braços livres = opções de crossface e estrangulamento de gola."),
                ("Prevenindo o Upa e o Escape de Cotovelo", "As duas principais fugas do monte são o upa (ponte e rolamento) e o escape de cotovelo. Para o upa: amplie sua base e poste uma mão quando sentir a ponte. Para o escape de cotovelo: mantenha os joelhos pesados no chão, flutue os quadris para contrariar o escape de quadril."),
            ],
            "steps": [
                ("Estabeleça Base e Peso", "Ao transitar para o monte, imediatamente amplie seus joelhos e baixe seus quadris. Faça o crossface da cabeça com um braço para controlar a postura e prevenir o upa antes que comece."),
                ("Escolha Sua Altura", "Avalie a situação: oponente está fazendo ponte → desça para o monte baixo e amplie os joelhos. Oponente está plano → avance para o monte alto e comece a trabalhar as pegadas de finalização."),
                ("Controle os Braços", "Alcance e pegue um underhook, ou use um apoio de palma para baixo no ombro para começar a trabalhar o gift wrap. O controle de braço é a entrada para toda finalização do monte."),
                ("Ataque com Correntes de Finalização", "No monte alto, ataque o estrangulamento de Ezequiel primeiro. Se defendido, trabalhe para o S-monte para o armlock. Se esticarem o braço, transicione para o triângulo. A corrente previne qualquer resposta defensiva única."),
                ("Mantenha Durante as Transições", "Quando o oponente começa com sucesso um escape de cotovelo, flutue seus quadris e deslize seu joelho de volta sob a coxa deles. Reajuste constantemente sua posição para ficar à frente da tentativa de fuga."),
            ],
            "cta": "🥋 Registre seu Jogo de Cima com BJJ App →",
        },
    },
    {
        "slug": "bjj-double-guard-pull",
        "en": {
            "title": "Double Guard Pull in BJJ — Tactics and Strategy",
            "desc": "Master the double guard pull in BJJ competition. Learn how to win from the bottom when both players pull guard, with scoring strategy and sweep/submission sequences.",
            "difficulty": "intermediate",
            "diff_label": "Intermediate",
            "h1": "Double Guard Pull in BJJ — Tactics and Strategy",
            "intro": "The double guard pull happens when both competitors choose to play guard simultaneously. Common in gi competition, the resulting bottom-on-bottom situation requires specific technical and tactical knowledge to navigate successfully. The player who establishes grips, angle, and attacks first almost always wins this exchange.",
            "concepts": [
                ("The Double Pull Dynamic", "When both players pull guard, the first to establish a dominant sitting position gains the initiative. This is usually the player who pulls second — they can choose their entry based on what the opponent establishes."),
                ("Grip Priority in Double Pull", "In gi, the race is to establish a cross grip, collar grip, or sleeve control before the opponent. Whoever gets the dominant grip first controls the pace and attack direction of the double pull exchange."),
                ("The First-to-Sitting Advantage", "The player who sits up first, rather than lying back, controls the distance. From the upright sitting position you can attack the other player who is still leaning back — creating a guard passing opportunity."),
                ("IBJJF Scoring in Double Pull", "In IBJJF rules, neither player scores for pulling guard. The first player to come on top — whether via sweep or stand-up — scores 2 points. Understanding this scoring incentive shapes the entire tactical approach."),
                ("Submission Hunting from Bottom-on-Bottom", "The double pull situation is ideal for heel hooks (no-gi), kneebars, and toehold attacks. In gi, focus on omoplatas, triangles from seated guard, and loop chokes if the opponent reaches forward."),
            ],
            "steps": [
                ("Win the Grip Race", "As soon as both players sit, immediately fight for the dominant grip. Prioritize sleeve control or collar grip. A cross-grip advantage lets you dictate the first sweep or attack attempt."),
                ("Establish Your Angle", "Shift your hips to your dominant side immediately. Playing flat-back in a double pull is passive — create a 45-degree angle to open up your offensive guard."),
                ("Attack Before the Opponent Sits Up", "If the opponent is still leaning back, attack immediately: knee bar, toehold, heel hook (no-gi), or sit up yourself and begin passing their guard."),
                ("Chain Sweeps with Submission Threats", "Sweep attempts force the opponent to post and react. When they post to prevent the sweep, that arm is momentarily vulnerable to an omoplata or triangle. Build sweep-to-submission chains."),
                ("Be Ready to Stand and Pass", "If the exchange becomes neutral, stand up first. Voluntarily coming to top position creates scoring and psychological pressure — the opponent must now defend a guard pass."),
            ],
            "cta": "🥋 Track Your Competition Strategy with BJJ App →",
        },
        "ja": {
            "title": "BJJ ダブルガードプル — タクティクスと戦略",
            "desc": "BJJ競技でのダブルガードプルをマスターする。両者がガードプルした際のボトム状況で勝つ方法、スコアリング戦略、スウィープ・サブミッションシーケンスを解説。",
            "difficulty": "intermediate",
            "diff_label": "中級",
            "h1": "BJJ ダブルガードプル — タクティクスと戦略",
            "intro": "ダブルガードプルは、両方の競技者が同時にガードをプレイすることを選択したときに発生します。道衣の競技でよく見られます。このボトム対ボトムの状況を成功させるには、特定の技術的・戦術的知識が必要です。グリップ・角度・アタックを最初に確立したプレイヤーがほぼ常にこの交換で勝ちます。",
            "concepts": [
                ("ダブルプルのダイナミクス", "両プレイヤーがガードをプルすると、支配的な座りポジションを最初に確立した方がイニシアティブを得ます。これは通常、後からプルしたプレイヤーです — 相手が確立したものに基づいてエントリーを選択できます。"),
                ("ダブルプルでのグリップ優先度", "道衣では、相手より先にクロスグリップ・衿グリップ・袖コントロールを確立するレースになります。最初に支配的なグリップを得た方がダブルプル交換のペースとアタック方向をコントロールします。"),
                ("最初に座る優位性", "仰向けになるのではなく、最初に座り上がるプレイヤーが距離をコントロールします。直立した座りポジションから、まだ後ろに傾いている他のプレイヤーをアタックでき — ガードパスの機会を作ります。"),
                ("ダブルプルでのIBJJFスコアリング", "IBJJFルールでは、どちらのプレイヤーもガードプルでスコアしません。スウィープか立ち上がりかに関わらず、最初にトップに来たプレイヤーが2点を得ます。このスコアリングインセンティブを理解することが戦術的アプローチ全体を形成します。"),
                ("ボトム対ボトムからのサブミッションハンティング", "ダブルプルの状況は、ヒールフック（ノーギ）・ニーバー・トーホールドアタックに最適です。道衣では、座りガードからのオモプラータ・トライアングル、相手が前に手を伸ばした場合のループチョークに焦点を当てる。"),
            ],
            "steps": [
                ("グリップレースに勝つ", "両プレイヤーが座ったらすぐに、支配的なグリップを求めて戦う。袖コントロールまたは衿グリップを優先する。クロスグリップの優位性により、最初のスウィープまたはアタックの試みを指示できます。"),
                ("角度を確立する", "すぐにドミナントサイドにヒップをシフトする。ダブルプルで仰向けになってプレイするのはパッシブです — 攻撃的なガードを開くために45度の角度を作る。"),
                ("相手が座り上がる前にアタックする", "相手がまだ後ろに傾いていたら、すぐにアタックする：ニーバー・トーホールド・ヒールフック（ノーギ）、または自分が座り上がって相手のガードをパスし始める。"),
                ("サブミッションの脅威とスウィープをチェーンする", "スウィープの試みは相手にポストして反応することを強制します。スウィープを防ぐためにポストするとき、その腕は一時的にオモプラータやトライアングルに対して脆弱になります。スウィープ→サブミッションチェーンを構築する。"),
                ("立ち上がってパスする準備をする", "交換がニュートラルになったら、先に立ち上がる。自発的にトップポジションに来ることでスコアリングと心理的プレッシャーを生み出します — 相手は今やガードパスを防御しなければなりません。"),
            ],
            "cta": "🥋 BJJ Appで競技戦略を記録しよう →",
        },
        "pt": {
            "title": "Double Guard Pull no BJJ — Táticas e Estratégia",
            "desc": "Domine o double guard pull na competição de BJJ. Aprenda a vencer por baixo quando ambos os jogadores puxam guarda, com estratégia de pontuação e sequências de raspagem/finalização.",
            "difficulty": "intermediate",
            "diff_label": "Intermediário",
            "h1": "Double Guard Pull no BJJ — Táticas e Estratégia",
            "intro": "O double guard pull acontece quando ambos os competidores escolhem jogar guarda simultaneamente. Comum na competição com gi, a situação resultante de baixo-contra-baixo requer conhecimento técnico e tático específico para navegar com sucesso. O jogador que estabelece pegadas, ângulo e ataques primeiro quase sempre vence essa troca.",
            "concepts": [
                ("A Dinâmica do Double Pull", "Quando ambos os jogadores puxam guarda, o primeiro a estabelecer uma posição sentada dominante ganha a iniciativa. Este é geralmente o jogador que puxa por último — pode escolher sua entrada com base no que o oponente estabelece."),
                ("Prioridade de Pegada no Double Pull", "No gi, a corrida é para estabelecer uma pegada cruzada, pegada na gola ou controle de manga antes do oponente. Quem conseguir a pegada dominante primeiro controla o ritmo e a direção de ataque da troca de double pull."),
                ("A Vantagem de Sentar Primeiro", "O jogador que se senta primeiro, em vez de deitar para trás, controla a distância. Da posição sentada ereta você pode atacar o outro jogador que ainda está inclinado para trás — criando uma oportunidade de passar a guarda."),
                ("Pontuação IBJJF no Double Pull", "Nas regras do IBJJF, nenhum jogador pontua por puxar guarda. O primeiro jogador a ficar por cima — seja via raspagem ou levantamento — marca 2 pontos. Entender esse incentivo de pontuação molda toda a abordagem tática."),
                ("Caça a Finalizações do Fundo-contra-Fundo", "A situação de double pull é ideal para heel hooks (no-gi), kneebars e ataques de toehold. No gi, foque em omoplatas, triângulos da guarda sentada e loop chokes se o oponente alcançar à frente."),
            ],
            "steps": [
                ("Vença a Corrida de Pegadas", "Assim que ambos os jogadores sentarem, imediatamente lute pela pegada dominante. Priorize controle de manga ou pegada na gola. Uma vantagem de pegada cruzada permite ditar a primeira tentativa de raspagem ou ataque."),
                ("Estabeleça Seu Ângulo", "Desloque seus quadris para seu lado dominante imediatamente. Jogar de costas num double pull é passivo — crie um ângulo de 45 graus para abrir sua guarda ofensiva."),
                ("Ataque Antes do Oponente Se Sentar", "Se o oponente ainda estiver inclinado para trás, ataque imediatamente: kneebar, toehold, heel hook (no-gi), ou sente você mesmo e comece a passar a guarda deles."),
                ("Encadeie Raspagens com Ameaças de Finalização", "Tentativas de raspagem forçam o oponente a apostar e reagir. Quando apoiam para prevenir a raspagem, esse braço fica momentaneamente vulnerável a um omoplata ou triângulo. Construa correntes de raspagem para finalização."),
                ("Esteja Pronto para Levantar e Passar", "Se a troca ficar neutra, levante primeiro. Vir voluntariamente para a posição de cima cria pressão de pontuação e psicológica — o oponente agora deve defender uma passagem de guarda."),
            ],
            "cta": "🥋 Registre sua Estratégia de Competição com BJJ App →",
        },
    },
    {
        "slug": "bjj-bottom-game-mastery",
        "en": {
            "title": "BJJ Bottom Game Mastery — Complete Guide",
            "desc": "Master the complete bottom game in BJJ. Sweeps, submissions, guard retention, and positional transitions from all bottom positions.",
            "difficulty": "advanced",
            "diff_label": "Advanced",
            "h1": "BJJ Bottom Game Mastery — Complete System",
            "intro": "The bottom game encompasses everything you do when an opponent has top position. From closed guard to turtle, from under side control to the escapes from mount and back — a complete bottom game player is dangerous from anywhere. This guide presents a systematic framework for developing a world-class bottom game that threatens on every level.",
            "concepts": [
                ("The Bottom Game Mindset", "The most common mistake in bottom positions is playing defensively. World-class bottom players think offensively from the worst positions — looking for submission attacks, guard pulls, and sweeps even from under mount or back control."),
                ("Escape Hierarchy", "Not all bottom positions are equal. From most to least dangerous: back control → mount → side control → turtle → bottom of knee-on-belly → closed guard. Know your current position's danger level and prioritize escaping accordingly."),
                ("Frame Before Movement", "The sequence for every bottom position: establish frames first, then create space, then move. Without frames, movement creates scrambles where the top player has gravitational advantage. Frames give you the space needed for hip movement."),
                ("Active Defense vs. Passive Defense", "Passive defense (just surviving) is a losing strategy. Active defense means simultaneously defending and attacking. From mount, shrimping while reaching for an arm drag is active defense — you're escaping and preparing a counter in the same movement."),
                ("The Sweep-Submission Connection", "Every sweep attempt creates submission opportunity and vice versa. If your opponent defends your scissor sweep by base-widening, their arm extends — perfect for kimura. Design your bottom game so every move has a dual threat."),
            ],
            "steps": [
                ("Assess Your Position", "Before any movement, identify your current bottom position and its primary escape. Under mount = elbow escape or upa. Under side control = frames-to-guard recovery. At turtle = sit-out or roll to guard."),
                ("Create Frame and Space", "Post your inside arm as a frame across the opponent's neck or chest. Use your outside elbow to prevent their hip from settling. Once frames are established, create space with a deliberate hip escape."),
                ("Recover to Guard", "From the space created by hip escape, insert your knee shield or recover both feet to the hips. Closed guard recovery is the baseline — from there you have full offensive options."),
                ("Attack from Guard", "Once in any guard position, immediately attack. The transition from escaped to attacking is the highest-leverage moment — the opponent is off-balance from following your escape, making them most vulnerable."),
                ("Build Your A-Game Sequence", "Identify your 3 best sweeps and 3 best submissions. Build sequences where each sweep creates a submission threat and vice versa. Practice this sequence until it becomes automatic under pressure."),
            ],
            "cta": "🥋 Build Your Bottom Game with BJJ App →",
        },
        "ja": {
            "title": "BJJ ボトムゲーム完全マスターガイド",
            "desc": "BJJの完全なボトムゲームをマスターする。すべてのボトムポジションからのスウィープ・サブミッション・ガードリテンション・ポジショナルトランジションを解説。",
            "difficulty": "advanced",
            "diff_label": "上級",
            "h1": "BJJ ボトムゲーム マスタリー — 完全システム",
            "intro": "ボトムゲームは、相手がトップポジションにいるときに行うすべてのことを包括します。クローズドガードからタートル、サイドコントロール下からマウントとバックからのエスケープまで — 完全なボトムゲームプレイヤーはどこからでも危険です。このガイドは、すべてのレベルで脅威となる世界クラスのボトムゲームを開発するための体系的なフレームワークを提示します。",
            "concepts": [
                ("ボトムゲームのマインドセット", "ボトムポジションで最も一般的な間違いは防御的にプレイすることです。世界クラスのボトムプレイヤーはマウントやバックコントロール下からも攻撃的に考えます — サブミッションアタック・ガードプル・スウィープを探しています。"),
                ("エスケープの階層", "すべてのボトムポジションが同じわけではありません。最も危険なものから：バックコントロール → マウント → サイドコントロール → タートル → ニーオンベリー下 → クローズドガード。現在のポジションの危険レベルを知り、それに応じてエスケープを優先する。"),
                ("動く前にフレーム", "すべてのボトムポジションのシーケンス：最初にフレームを確立し、次にスペースを作り、次に動く。フレームなしでは、動きがスクランブルを作り、トッププレイヤーが重力の優位性を持ちます。フレームはヒップの動きに必要なスペースを与えます。"),
                ("アクティブディフェンス vs パッシブディフェンス", "パッシブディフェンス（ただ生き残ること）は負ける戦略です。アクティブディフェンスは防御と攻撃を同時に行うことを意味します。マウント下から、アームドラッグに手を伸ばしながらシュリンプするのがアクティブディフェンスです — 同じ動きでエスケープと反撃の準備をしています。"),
                ("スウィープとサブミッションのつながり", "すべてのスウィープの試みがサブミッションの機会を作り、逆もまた同様です。シザースウィープをベースを広げることで防御すると、腕が伸びます — キムラに最適。すべての動きがデュアルな脅威を持つようにボトムゲームを設計する。"),
            ],
            "steps": [
                ("ポジションを評価する", "動く前に、現在のボトムポジションとその主要なエスケープを特定する。マウント下 = エルボーエスケープまたはウパ。サイドコントロール下 = フレーム→ガードリカバリー。タートル = シットアウトまたはガードへのロール。"),
                ("フレームとスペースを作る", "相手の首または胸にフレームとして内側の腕をポストする。外側の肘を使って相手のヒップが落ち着くのを防ぐ。フレームが確立されたら、意図的なヒップエスケープでスペースを作る。"),
                ("ガードにリカバーする", "ヒップエスケープで作られたスペースから、ニーシールドを挿入するか両足をヒップに戻す。クローズドガードリカバリーがベースラインです — そこからすべての攻撃オプションがあります。"),
                ("ガードからアタックする", "どのガードポジションに入っても、すぐにアタックする。エスケープからアタックへのトランジションが最高のレバレッジの瞬間です — 相手はエスケープを追ってバランスを崩しており、最も脆弱です。"),
                ("Aゲームシーケンスを構築する", "3つの最良のスウィープと3つの最良のサブミッションを特定する。各スウィープがサブミッションの脅威を作り逆もまた同様なシーケンスを構築する。プレッシャー下で自動的になるまでこのシーケンスを練習する。"),
            ],
            "cta": "🥋 BJJ Appでボトムゲームを構築しよう →",
        },
        "pt": {
            "title": "Maestria no Jogo de Baixo no BJJ",
            "desc": "Domine o jogo de baixo completo no BJJ. Raspagens, finalizações, retenção de guarda e transições posicionais de todas as posições de baixo.",
            "difficulty": "advanced",
            "diff_label": "Avançado",
            "h1": "Maestria no Jogo de Baixo do BJJ — Sistema Completo",
            "intro": "O jogo de baixo abrange tudo que você faz quando um oponente tem a posição de cima. Da guarda fechada à tartaruga, de baixo do controle lateral às fugas do monte e das costas — um jogador completo de baixo é perigoso de qualquer lugar. Este guia apresenta um framework sistemático para desenvolver um jogo de baixo de classe mundial que ameaça em todos os níveis.",
            "concepts": [
                ("A Mentalidade do Jogo de Baixo", "O erro mais comum nas posições de baixo é jogar defensivamente. Jogadores de classe mundial de baixo pensam ofensivamente das piores posições — procurando ataques de finalização, puxadas de guarda e raspagens mesmo de baixo do monte ou controle pelas costas."),
                ("Hierarquia de Fuga", "Nem todas as posições de baixo são iguais. Da mais à menos perigosa: controle pelas costas → monte → controle lateral → tartaruga → baixo do joelho-na-barriga → guarda fechada. Conheça o nível de perigo da sua posição atual e priorize a fuga de acordo."),
                ("Frame Antes do Movimento", "A sequência para cada posição de baixo: estabeleça frames primeiro, então crie espaço, então mova. Sem frames, o movimento cria scrambles onde o jogador de cima tem vantagem gravitacional. Os frames dão o espaço necessário para o movimento de quadril."),
                ("Defesa Ativa vs. Defesa Passiva", "A defesa passiva (apenas sobreviver) é uma estratégia perdedora. A defesa ativa significa defender e atacar simultaneamente. De baixo do monte, camarão enquanto alcança um arm drag é defesa ativa — você está fugindo e preparando um contra no mesmo movimento."),
                ("A Conexão Raspagem-Finalização", "Toda tentativa de raspagem cria oportunidade de finalização e vice-versa. Se seu oponente defende sua raspagem de tesoura ampliando a base, o braço se estende — perfeito para kimura. Projete seu jogo de baixo para que cada movimento tenha uma dupla ameaça."),
            ],
            "steps": [
                ("Avalie Sua Posição", "Antes de qualquer movimento, identifique sua posição de baixo atual e sua fuga principal. Sob o monte = escape de cotovelo ou upa. Sob o controle lateral = recuperação de guarda com frames. Na tartaruga = sit-out ou rolamento para guarda."),
                ("Crie Frame e Espaço", "Poste seu braço interno como frame no pescoço ou peito do oponente. Use seu cotovelo externo para evitar que o quadril deles se assente. Uma vez estabelecidos os frames, crie espaço com um escape de quadril deliberado."),
                ("Recupere para a Guarda", "Do espaço criado pelo escape de quadril, insira seu escudo de joelho ou recupere ambos os pés nos quadris. A recuperação da guarda fechada é a linha de base — a partir daí você tem opções ofensivas completas."),
                ("Ataque da Guarda", "Uma vez em qualquer posição de guarda, ataque imediatamente. A transição de escapado para atacando é o momento de maior alavancagem — o oponente está desequilibrado por seguir sua fuga, tornando-os mais vulneráveis."),
                ("Construa Sua Sequência A-Game", "Identifique suas 3 melhores raspagens e 3 melhores finalizações. Construa sequências onde cada raspagem cria uma ameaça de finalização e vice-versa. Pratique esta sequência até que se torne automática sob pressão."),
            ],
            "cta": "🥋 Construa seu Jogo de Baixo com BJJ App →",
        },
    },
]


def make_html(slug, lang, data, base_url=BASE_URL):
    """Generate a complete HTML page for a given topic/language."""
    title = data["title"]
    desc = data["desc"]
    difficulty = data["difficulty"]
    diff_label = data["diff_label"]
    h1 = data["h1"]
    intro = data["intro"]
    concepts = data["concepts"]
    steps = data["steps"]
    cta_text = data["cta"]

    concepts_html = "\n".join(
        f'<div class="concept-card"><h3>{c[0]}</h3><p>{c[1]}</p></div>'
        for c in concepts
    )
    steps_html = "\n".join(
        f'<div class="step"><h4>Step {i+1}: {s[0]}</h4><p>{s[1]}</p></div>'
        if lang == "en" else
        f'<div class="step"><h4>ステップ {i+1}: {s[0]}</h4><p>{s[1]}</p></div>'
        if lang == "ja" else
        f'<div class="step"><h4>Passo {i+1}: {s[0]}</h4><p>{s[1]}</p></div>'
        for i, s in enumerate(steps)
    )

    share_text = title.replace("", "").replace("", "")
    page_url = f"{base_url}/{lang}/{slug}.html"

    other_langs = {"en": "EN", "ja": "JA", "pt": "PT"}
    lang_nav_links = " | ".join(
        f'<a href="../{l}/{slug}.html">{label}</a>'
        for l, label in other_langs.items()
    )

    hreflang_tags = "\n".join(
        f'    <link rel="alternate" hreflang="{l}" href="{base_url}/{l}/{slug}.html" />'
        for l in ["en", "ja", "pt"]
    ) + f'\n    <link rel="alternate" hreflang="x-default" href="{base_url}/en/{slug}.html" />'

    html_lang = {"en": "en", "ja": "ja", "pt": "pt"}[lang]
    beehiiv_url = "https://embeds.beehiiv.com/6e75e7c9-2d4a-4d64-8eff-47c36f069d6c"

    return f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
  <link rel="icon" href="https://wiki.bjj-app.net/favicon.svg" type="image/svg+xml">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{page_url}">
{hreflang_tags}
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','GTM-WC3DKRB');</script>
</head>
<body>
<div id="read-progress"></div>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WC3DKRB" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<div class="lang-nav">{lang_nav_links}</div>
<article>
<header>
  <span class="diff-badge diff-{difficulty}">{diff_label}</span>
  <h1>{h1}</h1>
  <p class="intro">{intro}</p>
</header>
<div class="cta-banner"><a href="https://bjj-app-one.vercel.app" onclick="gtag('event','cta_click',{{'page':'{slug}'}})"> {cta_text}</a></div>
<section class="concepts">
{concepts_html}
</section>
<section class="steps">
{steps_html}
</section>
<div class="beehiiv-wrap">
  <iframe src="{beehiiv_url}" data-test-id="beehiiv-embed" width="100%" height="320" frameborder="0" scrolling="no" style="border-radius:8px;max-width:600px;margin:0 auto;display:block"></iframe>
</div>
<div class="share-bar">
  <a href="https://twitter.com/intent/tweet?text={share_text}&url={page_url}&hashtags=BJJ,BrazilianJiuJitsu" target="_blank" rel="noopener">&#x1D54F; Share</a>
</div>
</article>
<footer><p>&copy; 2026 BJJ Wiki | <a href="../en/index.html">Back to Index</a></p></footer>
  <button id="back-to-top" aria-label="Back to top" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">&#x2191;</button>
  <script>
  (function(){{
    var prog=document.getElementById('read-progress');
    if(prog){{
      window.addEventListener('scroll',function(){{
        var s=document.documentElement,b=document.body;
        var t=s.scrollTop||b.scrollTop;
        var h=(s.scrollHeight||b.scrollHeight)-s.clientHeight;
        prog.style.width=(h>0?(t/h*100):0)+'%';
      }});
    }}
    var btn=document.getElementById('back-to-top');
    if(btn){{
      window.addEventListener('scroll',function(){{btn.style.display=window.pageYOffset>300?'flex':'none';}});
    }}
    // Sticky Sidebar TOC
    if(window.innerWidth<1200)return;
    var hs=document.querySelectorAll('.container h2, article h2, article h3');
    if(hs.length<2)return;
    hs.forEach(function(h,i){{if(!h.id)h.id='hs'+i;}});
    var sb=document.createElement('nav');
    sb.className='wiki-sidebar';
    var logo=document.createElement('div');
    logo.className='wiki-sidebar-logo';
    logo.innerHTML='BJJ<span>Wiki</span>';
    sb.appendChild(logo);
    var ttl=document.createElement('div');
    ttl.className='wiki-sidebar-title';
    ttl.textContent='On This Page';
    sb.appendChild(ttl);
    hs.forEach(function(h){{
      var a=document.createElement('a');
      a.href='#'+h.id;
      a.textContent=h.textContent;
      a.className='wiki-sidebar-link';
      sb.appendChild(a);
    }});
    document.body.appendChild(sb);
    var io=new IntersectionObserver(function(entries){{
      entries.forEach(function(e){{
        if(e.isIntersecting){{
          sb.querySelectorAll('.wiki-sidebar-link').forEach(function(l){{l.classList.remove('active');}});
          var al=sb.querySelector('a[href="#'+e.target.id+'"]');
          if(al)al.classList.add('active');
        }}
      }});
    }},{{rootMargin:'-20% 0px -60% 0px'}});
    hs.forEach(function(h){{io.observe(h);}});
  }})();
  </script>
</body>
</html>"""


def update_sitemap(wiki_dir, new_slugs, base_url=BASE_URL):
    sitemap_path = os.path.join(wiki_dir, "sitemap.xml")
    with open(sitemap_path, "r", encoding="utf-8") as f:
        content = f.read()

    added = 0
    today = "2026-03-19"
    for slug in new_slugs:
        for lang in ["en", "ja", "pt"]:
            url = f"{base_url}/{lang}/{slug}.html"
            if url in content:
                continue
            new_entry = f"""  <url>
    <loc>{url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
"""
            content = content.replace("</urlset>", new_entry + "</urlset>")
            added += 1

    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(content)
    return added


def main():
    langs = ["en", "ja", "pt"]
    generated = []
    skipped = []

    for topic in TOPICS:
        slug = topic["slug"]
        for lang in langs:
            out_dir = os.path.join(WIKI_DIR, lang)
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"{slug}.html")
            if os.path.exists(out_path):
                print(f"  SKIP (exists): {lang}/{slug}.html")
                skipped.append(f"{lang}/{slug}")
                continue
            html = make_html(slug, lang, topic[lang])
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  ✅ Generated: {lang}/{slug}.html")
            generated.append(f"{lang}/{slug}")

    # Update sitemap
    new_slugs = [t["slug"] for t in TOPICS]
    added = update_sitemap(WIKI_DIR, new_slugs)
    print(f"\nSitemap: +{added} URLs added")
    print(f"\nDone: {len(generated)} generated, {len(skipped)} skipped")

    # Bug sweep
    print("\n=== Bug Sweep ===")
    errors = 0
    for topic in TOPICS:
        slug = topic["slug"]
        for lang in langs:
            path = os.path.join(WIKI_DIR, lang, f"{slug}.html")
            with open(path, "r", encoding="utf-8") as f:
                html = f.read()
            # Check for mojibake
            for bad in ["Ã", "â€", "Â ", "\ufffd"]:
                if bad in html:
                    print(f"  ❌ Mojibake in {lang}/{slug}: {bad!r}")
                    errors += 1
            # Check hreflang
            for l in ["en", "ja", "pt"]:
                if f'hreflang="{l}"' not in html:
                    print(f"  ❌ Missing hreflang={l} in {lang}/{slug}")
                    errors += 1
            # Check CTA
            if "bjj-app-one.vercel.app" not in html:
                print(f"  ❌ Missing CTA in {lang}/{slug}")
                errors += 1
    if errors == 0:
        print("  ✅ TOTAL ISSUES: 0")
    else:
        print(f"  ❌ TOTAL ISSUES: {errors}")


if __name__ == "__main__":
    main()
