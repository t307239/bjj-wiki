#!/usr/bin/env python3
# ⚠️ DEPRECATED — DO NOT RUN ⚠️
# このスクリプトはアフィリリンク(bjj06-22/bjjfanatics)を含む旧バッチスクリプトです。
# CLAUDE.md「アフィリリンク完全禁止」ルールにより使用禁止。
# 実行するとアフィリリンクが再注入され先祖返りします。
# 代わりに generate_bjj_wiki.py を使用してください。
"""BJJ Wiki Batch 387-391: 5 new themes x 3 languages = 15 pages"""
import os, re, datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = [
    {
        "slug": "bjj-leg-lock-entries-advanced",
        "en": {
            "title": "Advanced Leg Lock Entries: Systems & Setups | BJJ Wiki",
            "h1": "Advanced Leg Lock Entries",
            "desc": "Master advanced leg lock entry systems including ashi garami, saddle, and single-leg X transitions that high-level grapplers use to attack the lower body.",
            "category": "Leg Locks",
            "belt": "Purple Belt+",
            "body": """
<p>Advanced leg lock entries require understanding positional control, hip alignment, and the specific mechanical advantages that each entry point provides.</p>

<h2>The Ashi Garami Entry System</h2>
<p>Ashi garami (leg entanglement) is the foundational control position for leg attacks. Entering requires breaking your opponent's base and establishing inside hip control.</p>
<h3>Key Entry Points</h3>
<ul>
<li><strong>From guard:</strong> Pull opponent into de la riva, then invert to establish ashi garami</li>
<li><strong>From top:</strong> After failed guard pass, drop to ashi on the near leg</li>
<li><strong>From scramble:</strong> During transitions, whenever you secure an inside position on the leg</li>
</ul>

<h2>Single-Leg X (SLX) Entries</h2>
<p>Single-leg X provides exceptional control for heel hooks and kneebars. The key is securing the outside hip position while controlling the foot.</p>
<h3>Entry Mechanics</h3>
<ul>
<li>Establish inside foot-on-hip butterfly hook first</li>
<li>Slide bottom foot behind opponent's knee as you fall back</li>
<li>Bring top foot to their hip for full SLX control</li>
<li>Keep your knees together to maintain position</li>
</ul>

<h2>Outside Heel Hook (OHH) Entry</h2>
<p>Outside heel hooks require specific positional control with your knee cutting past the opponent's hip to access the outside.</p>
<h3>The 411/Saddle Position</h3>
<ul>
<li>Both legs thread through opponent's legs like scissors</li>
<li>Control the far heel with your armpit</li>
<li>Rotate your body to apply torque to the knee</li>
</ul>

<h2>Inside Heel Hook (IHH) Entry</h2>
<p>Inside heel hooks are accessible from standard ashi garami control. The entry is more common in competition due to being lower risk.</p>
<ul>
<li>Secure ashi garami with proper inside position</li>
<li>Control the heel with your opposite-side arm</li>
<li>Rotate toward the outside of the leg for finishing pressure</li>
</ul>

<h2>Transition Safety Rules</h2>
<p>Advanced leg lockers follow strict training protocols to prevent injuries during drilling.</p>
<ul>
<li>Always tap early — heel hooks can cause injury before pain is felt</li>
<li>Drill entries slowly before adding finishing pressure</li>
<li>Understand IBJJF legal divisions before competing</li>
</ul>

<h2>Drills to Improve Entries</h2>
<ul>
<li>Penetration step to SLX: 3 sets x 20 reps each side</li>
<li>Ashi garami entry from de la riva: live drilling with partner</li>
<li>411 exchange: alternate between partners transitioning the position</li>
</ul>
""",
            "amazon_text": "BJJ Leg Lock Systems",
            "amazon_kw": "BJJ+leg+lock+instructional",
        },
        "ja": {
            "title": "アドバンスドレッグロックエントリー：システムとセットアップ | BJJ Wiki",
            "h1": "アドバンスドレッグロックエントリー",
            "desc": "アシガラミ、サドル、シングルレッグXへの移行など、高レベルグラップラーが使用する下肢攻撃の上級エントリーシステムをマスターしよう。",
            "category": "レッグロック",
            "belt": "紫帯以上",
            "body": """
<p>アドバンスドレッグロックエントリーには、ポジションコントロール、ヒップの位置合わせ、各エントリーポイントが提供する具体的なメカニカルアドバンテージの理解が必要です。</p>

<h2>アシガラミエントリーシステム</h2>
<p>アシガラミ（レッグエンタングルメント）は脚攻撃の基盤となるコントロールポジションです。エントリーには相手のベースを崩し、インサイドヒップコントロールを確立することが必要です。</p>
<h3>主要エントリーポイント</h3>
<ul>
<li><strong>ガードから：</strong>相手をデラヒーバに引き込み、反転してアシガラミを確立</li>
<li><strong>トップから：</strong>ガードパス失敗後、近い足にドロップしてアシに入る</li>
<li><strong>スクランブルから：</strong>移行中、足のインサイドポジションを確保した時</li>
</ul>

<h2>シングルレッグX（SLX）エントリー</h2>
<p>シングルレッグXはヒールフックとニーバーに優れたコントロールを提供します。足のコントロールを維持しながらアウトサイドヒップポジションを確保することが重要です。</p>
<h3>エントリーメカニクス</h3>
<ul>
<li>まずインサイドフット・オン・ヒップのバタフライフックを確立</li>
<li>倒れ込みながら下の足を相手の膝裏にスライド</li>
<li>上の足を相手のヒップに置いて完全なSLXコントロール</li>
<li>膝を揃えてポジションを維持</li>
</ul>

<h2>アウトサイドヒールフック（OHH）エントリー</h2>
<p>アウトサイドヒールフックには、相手のヒップを超えて膝をカットする特定のポジションコントロールが必要です。</p>
<h3>411/サドルポジション</h3>
<ul>
<li>両足を相手の両足にハサミのように通す</li>
<li>脇で遠い踵をコントロール</li>
<li>体を回転させて膝にトルクをかける</li>
</ul>

<h2>インサイドヒールフック（IHH）エントリー</h2>
<p>インサイドヒールフックは標準的なアシガラミコントロールからアクセスできます。リスクが低いため、競技でより一般的です。</p>
<ul>
<li>適切なインサイドポジションでアシガラミを確保</li>
<li>逆側の腕で踵をコントロール</li>
<li>仕上げ圧力のために足の外側に向かって回転</li>
</ul>

<h2>トレーニング安全ルール</h2>
<p>上級レッグロッカーはドリリング中の怪我防止のために厳格なトレーニングプロトコルに従います。</p>
<ul>
<li>早めにタップ — ヒールフックは痛みを感じる前に怪我をする可能性がある</li>
<li>仕上げ圧力を加える前にゆっくりエントリーをドリル</li>
<li>競技前にIBJJFの合法ディビジョンを理解する</li>
</ul>

<h2>エントリー改善ドリル</h2>
<ul>
<li>ペネトレーションステップからSLX：各サイド3セット×20レップ</li>
<li>デラヒーバからアシガラミエントリー：パートナーとのライブドリリング</li>
<li>411エクスチェンジ：パートナー間でポジションを移行する交互練習</li>
</ul>
""",
            "amazon_text": "BJJレッグロックシステム",
            "amazon_kw": "BJJ+レッグロック",
        },
        "pt": {
            "title": "Entradas Avançadas em Leg Locks: Sistemas e Configurações | BJJ Wiki",
            "h1": "Entradas Avançadas em Leg Locks",
            "desc": "Domine sistemas avançados de entrada em leg locks incluindo ashi garami, saddle e transições Single Leg X que grapplers de alto nível usam para atacar a parte inferior do corpo.",
            "category": "Leg Locks",
            "belt": "Faixa Roxa+",
            "body": """
<p>Entradas avançadas em leg locks requerem compreensão de controle posicional, alinhamento de quadril e as vantagens mecânicas específicas que cada ponto de entrada oferece.</p>

<h2>O Sistema de Entrada Ashi Garami</h2>
<p>Ashi garami (emaranhamento de pernas) é a posição de controle fundamental para ataques nas pernas. Entrar requer quebrar a base do adversário e estabelecer controle interno do quadril.</p>
<h3>Pontos de Entrada Principais</h3>
<ul>
<li><strong>Da guarda:</strong> Puxe o adversário para de la riva, depois inverta para estabelecer ashi garami</li>
<li><strong>Por cima:</strong> Após tentativa falha de passagem de guarda, caia para ashi na perna próxima</li>
<li><strong>Do scramble:</strong> Durante transições, sempre que você assegurar uma posição interna na perna</li>
</ul>

<h2>Entradas Single-Leg X (SLX)</h2>
<p>Single-leg X fornece controle excepcional para heel hooks e kneebars. A chave é assegurar a posição de quadril externo enquanto controla o pé.</p>
<h3>Mecânica de Entrada</h3>
<ul>
<li>Estabeleça primeiro o gancho de borboleta com pé no quadril por dentro</li>
<li>Deslize o pé inferior atrás do joelho do adversário enquanto cai</li>
<li>Leve o pé superior para o quadril dele para controle SLX completo</li>
<li>Mantenha os joelhos juntos para manter a posição</li>
</ul>

<h2>Entrada Outside Heel Hook (OHH)</h2>
<p>Heel hooks externos requerem controle posicional específico com seu joelho cortando além do quadril do adversário para acessar o lado externo.</p>
<h3>A Posição 411/Saddle</h3>
<ul>
<li>Ambas as pernas passam pelas pernas do adversário como tesoura</li>
<li>Controle o calcanhar distante com sua axila</li>
<li>Gire o corpo para aplicar torque no joelho</li>
</ul>

<h2>Entrada Inside Heel Hook (IHH)</h2>
<p>Heel hooks internos são acessíveis a partir do controle padrão de ashi garami. A entrada é mais comum em competição por ser de menor risco.</p>
<ul>
<li>Assegure ashi garami com posição interna adequada</li>
<li>Controle o calcanhar com o braço do lado oposto</li>
<li>Gire em direção ao lado externo da perna para pressão de finalização</li>
</ul>

<h2>Regras de Segurança no Treino</h2>
<ul>
<li>Sempre toque cedo — heel hooks podem causar lesão antes que a dor seja sentida</li>
<li>Drill entradas lentamente antes de adicionar pressão de finalização</li>
<li>Entenda as divisões legais do IBJJF antes de competir</li>
</ul>

<h2>Drills para Melhorar as Entradas</h2>
<ul>
<li>Penetration step para SLX: 3 séries x 20 reps cada lado</li>
<li>Entrada ashi garami de de la riva: drilling ao vivo com parceiro</li>
<li>Troca 411: alterne entre parceiros transitando a posição</li>
</ul>
""",
            "amazon_text": "Sistemas de Leg Lock BJJ",
            "amazon_kw": "BJJ+leg+lock+instructional",
        },
    },
    {
        "slug": "bjj-top-game-concepts",
        "en": {
            "title": "BJJ Top Game Concepts: Pressure, Control & Attacks | BJJ Wiki",
            "h1": "BJJ Top Game Concepts",
            "desc": "Develop a comprehensive top game in BJJ by understanding pressure distribution, base maintenance, positional hierarchy, and efficient attack chains from dominant positions.",
            "category": "Positional Concepts",
            "belt": "Blue Belt+",
            "body": """
<p>A well-developed top game is built on principles rather than memorized sequences. Understanding how and why pressure works allows you to adapt to any opponent.</p>

<h2>The Core Principle: Gravity + Technique</h2>
<p>Top game is not about strength — it is about maximizing the use of gravity and body weight through proper alignment. When you stack your hips directly over your base, every kilogram works for you.</p>

<h2>The Positional Hierarchy</h2>
<p>In BJJ, not all top positions are equal. Understanding when to advance and when to consolidate is crucial:</p>
<ol>
<li><strong>Side control</strong> — Entry point after guard pass; solid but limited attacks</li>
<li><strong>North-south</strong> — Transition position; good choke access</li>
<li><strong>Knee on belly</strong> — Transitional pressure point; attacks both sides</li>
<li><strong>Mount</strong> — Primary submission platform; highest positional value</li>
<li><strong>Back control</strong> — Highest-value position; rear naked choke and bow-and-arrow access</li>
</ol>

<h2>Base and Pressure</h2>
<p>Your base must be wide enough to resist sweeps but mobile enough to transition. The key is having a "live" base — not rigid and not loose.</p>
<h3>Side Control Base Rules</h3>
<ul>
<li>Hip-to-hip connection removes opponent's space</li>
<li>Crossface controls head direction</li>
<li>Underhook on far side prevents bridging</li>
<li>Chest heavy on opponent's chest — not their belly</li>
</ul>

<h2>Reading Opponent's Escapes</h2>
<p>Every escape attempt creates an opportunity. The moment your opponent commits to an escape, they expose a position for you to advance.</p>
<ul>
<li><strong>Elbow-knee escape:</strong> Follow with knee on belly or mount</li>
<li><strong>Bridge:</strong> Roll to mount or take the back</li>
<li><strong>Turtle:</strong> Attack immediately — clock choke, back take, or crucifix</li>
</ul>

<h2>The Attack Chain Concept</h2>
<p>Single attacks fail. Chains succeed. Set up your primary attack so the defense creates your second attack.</p>
<ul>
<li>From mount: Americana → opponent frames → armbar or triangle</li>
<li>From back: RNC → opponent defends chin → bow-and-arrow or arm trap</li>
<li>From side control: Kimura → kimura sweep → kimura from top</li>
</ul>

<h2>Weight Distribution Training</h2>
<ul>
<li>Slow drilling of transitions while maintaining pressure</li>
<li>"Knee drag" exercise: practice shifting weight across positions</li>
<li>Positional sparring starting from side control — goal: advance position</li>
</ul>
""",
            "amazon_text": "BJJ Top Game Fundamentals",
            "amazon_kw": "BJJ+top+game+positional+control",
        },
        "ja": {
            "title": "BJJトップゲームのコンセプト：プレッシャー・コントロール・攻撃 | BJJ Wiki",
            "h1": "BJJトップゲームのコンセプト",
            "desc": "プレッシャーの配分、ベースの維持、ポジション階層、支配的ポジションからの効率的な攻撃チェーンを理解することで、BJJの包括的なトップゲームを開発しよう。",
            "category": "ポジションコンセプト",
            "belt": "青帯以上",
            "body": """
<p>よく発達したトップゲームは、暗記したシーケンスではなく原則の上に構築されています。プレッシャーがどのように、そしてなぜ機能するかを理解することで、どんな相手にも適応できます。</p>

<h2>核心原則：重力＋テクニック</h2>
<p>トップゲームは力ではありません — 適切なアラインメントによって重力と体重の使用を最大化することです。腰を直接ベースの上に積み重ねると、すべてのキログラムがあなたのために働きます。</p>

<h2>ポジション階層</h2>
<p>BJJでは、すべてのトップポジションが等しいわけではありません。いつ前進してどこで固めるかを理解することが重要です：</p>
<ol>
<li><strong>サイドコントロール</strong> — ガードパス後のエントリーポイント；安定しているが攻撃は限定的</li>
<li><strong>ノースサウス</strong> — 移行ポジション；チョークへのアクセスが良好</li>
<li><strong>ニーオンベリー</strong> — 移行的プレッシャーポイント；両側に攻撃</li>
<li><strong>マウント</strong> — 主要なサブミッションプラットフォーム；最高のポジション価値</li>
<li><strong>バックコントロール</strong> — 最高価値ポジション；裸絞めとボウアンドアローへのアクセス</li>
</ol>

<h2>ベースとプレッシャー</h2>
<p>ベースはスウィープに抵抗するほど広く、かつ移行できるほど機動性が必要です。「ライブ」なベースを持つことが重要 — 硬すぎず緩すぎず。</p>
<h3>サイドコントロールのベースルール</h3>
<ul>
<li>ヒップ対ヒップの接続で相手のスペースを排除</li>
<li>クロスフェイスで頭の方向をコントロール</li>
<li>遠い側のアンダーフックでブリッジを防ぐ</li>
<li>相手の腹ではなく胸に胸を重く当てる</li>
</ul>

<h2>相手の脱出を読む</h2>
<p>すべての脱出試みはチャンスを生みます。相手が脱出に専念した瞬間、あなたが前進できるポジションが露わになります。</p>
<ul>
<li><strong>エルボーニーエスケープ：</strong>ニーオンベリーまたはマウントで対応</li>
<li><strong>ブリッジ：</strong>マウントにロールするかバックを取る</li>
<li><strong>タートル：</strong>即座に攻撃 — クロックチョーク、バックテイク、またはクルシフィックス</li>
</ul>

<h2>攻撃チェーンのコンセプト</h2>
<p>単独の攻撃は失敗します。チェーンが成功します。防御が2番目の攻撃を生み出すよう主攻撃をセットアップしましょう。</p>
<ul>
<li>マウントから：アメリカーナ → 相手がフレーム → アームバーまたはトライアングル</li>
<li>バックから：裸絞め → 相手が顎をディフェンス → ボウアンドアローまたはアームトラップ</li>
<li>サイドコントロールから：キムラ → キムラスウィープ → トップからキムラ</li>
</ul>

<h2>体重配分トレーニング</h2>
<ul>
<li>プレッシャーを維持しながらのスローなトランジションドリル</li>
<li>「ニードラッグ」エクササイズ：ポジション間での体重移動練習</li>
<li>サイドコントロールから始めるポジショナルスパーリング — 目標：ポジション前進</li>
</ul>
""",
            "amazon_text": "BJJトップゲームの基礎",
            "amazon_kw": "BJJ+トップゲーム+ポジション",
        },
        "pt": {
            "title": "Conceitos do Jogo por Cima no BJJ: Pressão, Controle e Ataques | BJJ Wiki",
            "h1": "Conceitos do Jogo por Cima no BJJ",
            "desc": "Desenvolva um jogo por cima abrangente no BJJ entendendo distribuição de pressão, manutenção de base, hierarquia posicional e cadeias de ataques eficientes de posições dominantes.",
            "category": "Conceitos Posicionais",
            "belt": "Faixa Azul+",
            "body": """
<p>Um bom jogo por cima é construído em princípios, não em sequências memorizadas. Entender como e por que a pressão funciona permite que você se adapte a qualquer oponente.</p>

<h2>O Princípio Central: Gravidade + Técnica</h2>
<p>O jogo por cima não é sobre força — é sobre maximizar o uso da gravidade e peso corporal através do alinhamento adequado.</p>

<h2>A Hierarquia Posicional</h2>
<ol>
<li><strong>Controle lateral</strong> — Ponto de entrada após passagem de guarda</li>
<li><strong>North-south</strong> — Posição de transição; bom acesso a estrangulamentos</li>
<li><strong>Joelho na barriga</strong> — Ponto de pressão transicional</li>
<li><strong>Montada</strong> — Plataforma primária de finalização</li>
<li><strong>Controle de costas</strong> — Posição de maior valor</li>
</ol>

<h2>Base e Pressão</h2>
<h3>Regras de Base no Controle Lateral</h3>
<ul>
<li>Conexão quadril a quadril remove o espaço do oponente</li>
<li>Cross-face controla a direção da cabeça</li>
<li>Underhook no lado distante previne a ponte</li>
<li>Peito pesado no peito do oponente — não na barriga</li>
</ul>

<h2>Lendo as Escapadas do Oponente</h2>
<ul>
<li><strong>Escapada cotovelo-joelho:</strong> Siga com joelho na barriga ou montada</li>
<li><strong>Ponte:</strong> Role para a montada ou tome as costas</li>
<li><strong>Tartaruga:</strong> Ataque imediatamente — clock choke, tomada de costas ou crucifixo</li>
</ul>

<h2>O Conceito de Cadeia de Ataques</h2>
<ul>
<li>Da montada: Americana → oponente enquadra → armbar ou triângulo</li>
<li>Das costas: RNC → oponente defende queixo → bow-and-arrow ou armadilha de braço</li>
<li>Do controle lateral: Kimura → sweep kimura → kimura por cima</li>
</ul>
""",
            "amazon_text": "Fundamentos do Jogo por Cima BJJ",
            "amazon_kw": "BJJ+top+game+positional+control",
        },
    },
    {
        "slug": "bjj-guard-passing-systems-advanced",
        "en": {
            "title": "Advanced BJJ Guard Passing Systems | BJJ Wiki",
            "h1": "Advanced BJJ Guard Passing Systems",
            "desc": "Explore advanced guard passing frameworks used by elite BJJ competitors — systematic approaches that combine torreando, leg drag, knee cut, and pressure passing into cohesive systems.",
            "category": "Guard Passing",
            "belt": "Purple Belt+",
            "body": """
<p>Advanced guard passing is systematic, not reactive. Elite passers use frameworks that anticipate guard movements and have pre-planned answers to every reaction.</p>

<h2>The Standing Passing System</h2>
<p>Standing passes give you mobility advantage and break spider/collar-sleeve guards. The core of the standing system is torreando (bullfighter) control.</p>
<h3>Torreando Framework</h3>
<ul>
<li>Control both ankles or shins from standing</li>
<li>Side pass: push both legs to your left, step around to the right</li>
<li>X-pass: step one foot between their legs, clear the far leg</li>
<li>Leg drag: pin one leg to the mat, drag it across, establish knee cut</li>
</ul>

<h2>The Knee Cut System</h2>
<p>Knee cut is the most battle-tested pass in competitive BJJ. Used by Gordon Ryan, Lucas Lepri, and countless champions.</p>
<h3>Technical Key Points</h3>
<ul>
<li>Establish underhook on their far arm before committing</li>
<li>Hip alignment: your hip should pass over their knee during the cut</li>
<li>Head position: pressure to far side, not lifting</li>
<li>Hip pressure through the knee maintains position if they half-guard</li>
</ul>

<h2>Pressure Passing System</h2>
<p>Pressure passing works by accumulating weight and exhausting the guard player's frames and grips.</p>
<h3>Stack Pass Progression</h3>
<ol>
<li>Break guard posture, grab collars</li>
<li>Stack opponent's hips over their head</li>
<li>Walk forward, forcing their legs to fold</li>
<li>Free one leg at a time, establish side control</li>
</ol>

<h2>Passing Against Specific Guards</h2>
<h3>Against De La Riva</h3>
<ul>
<li>Torreando to far side: strip the DLR hook, step around</li>
<li>Knee cut over the hook: if they have tight DLR, knee cut across</li>
<li>Back step: classic answer to DLR — backstep to knee cut or ashi</li>
</ul>
<h3>Against Half Guard</h3>
<ul>
<li>Knee split: drive knee forward, split their legs</li>
<li>Log splitter: north-south motion to free the trapped leg</li>
<li>Underhook battle: win the underhook to get to dogfight, then pass</li>
</ul>

<h2>Building a Personal Passing System</h2>
<p>Top players do not use 20 passes — they use 3-4 passes with many variations. Build depth in a few passes rather than breadth across many.</p>
<ul>
<li>Choose a primary standing pass and primary knee pass</li>
<li>Learn the transitions between them</li>
<li>Add a pressure pass for strong guard players</li>
<li>Drill each pass until you can enter it from multiple angles</li>
</ul>
""",
            "amazon_text": "Guard Passing Systems",
            "amazon_kw": "BJJ+guard+passing+instructional",
        },
        "ja": {
            "title": "BJJアドバンスドガードパッシングシステム | BJJ Wiki",
            "h1": "BJJアドバンスドガードパッシングシステム",
            "desc": "トレアンド、レッグドラッグ、ニーカット、プレッシャーパッシングを組み合わせたシステマティックアプローチなど、エリートBJJ競技者が使用する上級ガードパッシングフレームワークを探求しよう。",
            "category": "ガードパッシング",
            "belt": "紫帯以上",
            "body": """
<p>上級ガードパッシングはシステマティックで反応的ではありません。エリートパッサーはガードの動きを予測し、すべての反応に対する事前計画された答えを持つフレームワークを使用します。</p>

<h2>スタンディングパッシングシステム</h2>
<p>スタンディングパスは機動性の優位性を与え、スパイダー/カラースリーブガードを崩します。スタンディングシステムの核心はトレアンド（闘牛士）コントロールです。</p>
<h3>トレアンドフレームワーク</h3>
<ul>
<li>スタンディングから両足首または脛をコントロール</li>
<li>サイドパス：両脚を左に押し、右に回り込む</li>
<li>Xパス：片足を相手の足の間に踏み込み、遠い脚をクリア</li>
<li>レッグドラッグ：片足をマットに固定し、引きずってニーカットを確立</li>
</ul>

<h2>ニーカットシステム</h2>
<p>ニーカットは競技BJJで最も実績のあるパスです。ゴードン・ライアン、ルーカス・レプリ、そして無数のチャンピオンが使用しています。</p>
<h3>技術的なポイント</h3>
<ul>
<li>コミットする前に相手の遠い腕にアンダーフックを確立</li>
<li>ヒップのアラインメント：カット中にヒップが相手の膝を超える</li>
<li>頭の位置：遠い側にプレッシャー、持ち上げない</li>
<li>膝を通したヒッププレッシャーでハーフガードになっても位置を維持</li>
</ul>

<h2>プレッシャーパッシングシステム</h2>
<p>プレッシャーパッシングは体重を蓄積してガードプレイヤーのフレームとグリップを疲弊させることで機能します。</p>
<h3>スタックパスの進行</h3>
<ol>
<li>ガードの姿勢を崩し、襟をつかむ</li>
<li>相手のヒップを頭の上に積み重ねる</li>
<li>前進して脚が折りたたまれるよう強制</li>
<li>一本ずつ脚を解放し、サイドコントロールを確立</li>
</ol>

<h2>特定のガードに対するパッシング</h2>
<h3>デラヒーバに対して</h3>
<ul>
<li>遠い側へのトレアンド：DLRフックを剥がし、回り込む</li>
<li>フックを超えるニーカット：タイトなDLRなら横切るニーカット</li>
<li>バックステップ：DLRへのクラシックな答え — バックステップからニーカットまたはアシ</li>
</ul>
<h3>ハーフガードに対して</h3>
<ul>
<li>ニースプリット：膝を前進させ脚を割る</li>
<li>ログスプリッター：ノースサウス動作で挟まれた脚を解放</li>
<li>アンダーフック争い：アンダーフックを勝ち取ってドッグファイトに移行し、パス</li>
</ul>

<h2>個人パッシングシステムの構築</h2>
<p>トッププレイヤーは20種類のパスを使いません — 多くのバリエーションを持つ3〜4種類のパスを使います。多くのパスに広さを求めるより少数のパスに深さを構築しましょう。</p>
<ul>
<li>メインのスタンディングパスとメインのニーパスを選ぶ</li>
<li>それらの間のトランジションを覚える</li>
<li>強いガードプレイヤーのためのプレッシャーパスを追加</li>
<li>各パスを複数の角度からエントリーできるまでドリルする</li>
</ul>
""",
            "amazon_text": "ガードパッシングシステム",
            "amazon_kw": "BJJ+ガードパス+システム",
        },
        "pt": {
            "title": "Sistemas Avançados de Passagem de Guarda no BJJ | BJJ Wiki",
            "h1": "Sistemas Avançados de Passagem de Guarda no BJJ",
            "desc": "Explore frameworks avançados de passagem de guarda usados por competidores de elite do BJJ — abordagens sistemáticas que combinam torreando, leg drag, knee cut e passagem de pressão.",
            "category": "Passagem de Guarda",
            "belt": "Faixa Roxa+",
            "body": """
<p>A passagem avançada de guarda é sistemática, não reativa. Passadores de elite usam frameworks que antecipam movimentos de guarda.</p>

<h2>O Sistema de Passagem em Pé</h2>
<h3>Framework Torreando</h3>
<ul>
<li>Controle ambos os tornozelos ou canelas em pé</li>
<li>Passe lateral: empurre ambas as pernas para a esquerda, contorne para a direita</li>
<li>X-pass: pise um pé entre as pernas deles, limpe a perna distante</li>
<li>Leg drag: fixe uma perna no tatame, arraste-a, estabeleça knee cut</li>
</ul>

<h2>O Sistema Knee Cut</h2>
<h3>Pontos Técnicos Principais</h3>
<ul>
<li>Estabeleça underhook no braço distante antes de comprometer</li>
<li>Alinhamento do quadril: seu quadril deve passar sobre o joelho durante o corte</li>
<li>Pressão do quadril pelo joelho mantém posição se eles fizerem meia-guarda</li>
</ul>

<h2>Sistema de Passagem de Pressão</h2>
<h3>Progressão do Stack Pass</h3>
<ol>
<li>Quebre a postura da guarda, pegue as golas</li>
<li>Empilhe os quadris do oponente sobre a cabeça</li>
<li>Avance forçando as pernas a dobrar</li>
<li>Libere uma perna de cada vez, estabeleça controle lateral</li>
</ol>

<h2>Construindo um Sistema de Passagem Pessoal</h2>
<ul>
<li>Escolha uma passe em pé principal e um passe de joelho principal</li>
<li>Aprenda as transições entre eles</li>
<li>Adicione um passe de pressão para guardeiros fortes</li>
</ul>
""",
            "amazon_text": "Sistemas de Passagem de Guarda BJJ",
            "amazon_kw": "BJJ+guard+passing+instructional",
        },
    },
    {
        "slug": "bjj-submission-pressure-guide",
        "en": {
            "title": "BJJ Submission Pressure: Using Attacks to Create Openings | BJJ Wiki",
            "h1": "BJJ Submission Pressure",
            "desc": "Learn how to use submission threats strategically in BJJ — applying pressure that forces reactions and creates sweep or positional advancement opportunities.",
            "category": "Submission Strategy",
            "belt": "Blue Belt+",
            "body": """
<p>Submission pressure means threatening attacks not just to finish, but to force reactions that open other opportunities. The goal is to make your opponent move, and then capitalize on that movement.</p>

<h2>The Submission-Sweep Dynamic</h2>
<p>Every submission threat should simultaneously threaten a sweep if the opponent defends. This two-way threat is what makes guard play threatening even when submissions are not completed.</p>
<h3>Examples</h3>
<ul>
<li>Triangle + armbar: if they pull the arm, attack the triangle; if they stack, set armbar</li>
<li>Kimura + hip bump sweep: threaten kimura from closed guard, they posture → hip bump sweep</li>
<li>Omoplata + sweep: if they roll out → follow to omoplata sweep or shoulder lock</li>
</ul>

<h2>Creating Defensive Reactions</h2>
<p>When you attack an arm, the opponent must decide how to defend. That decision creates patterns you can exploit.</p>
<h3>Arm Defense Patterns</h3>
<ul>
<li>They pull elbow in → go over the top with baseball choke or ezekiel</li>
<li>They push your head → open the triangle angle on that side</li>
<li>They stack → switch to kneebar or heel hook from de la riva</li>
</ul>

<h2>Grip Sequence as Pressure</h2>
<p>Gripping well is the first layer of submission pressure. A strong cross-collar grip forces your opponent to address it immediately, creating the opening for your next attack.</p>

<h2>Positional Pressure vs. Submission Pressure</h2>
<p>Positional pressure (weight, base) creates discomfort. Submission pressure (threats) creates panic. Use both together for maximum effect.</p>
<ul>
<li>Heavy side control + kimura grip = your opponent cannot think clearly</li>
<li>Back control with hooks + neck grip = constant threat forces errors</li>
</ul>

<h2>Pressure Training Methods</h2>
<ul>
<li>Attack-only rounds: try only submissions, not position advancement</li>
<li>Three-attack drill: connect 3 different attack threats in a single sequence</li>
<li>Time pressure: set 60-second rounds where you must land 3+ submission attempts</li>
</ul>
""",
            "amazon_text": "BJJ Submission Strategy",
            "amazon_kw": "BJJ+submission+strategy+guard",
        },
        "ja": {
            "title": "BJJサブミッションプレッシャー：攻撃で開口部を作る | BJJ Wiki",
            "h1": "BJJサブミッションプレッシャー",
            "desc": "BJJでサブミッションの脅威を戦略的に使う方法を学ぶ — 反応を強制しスウィープやポジション前進のチャンスを生み出すプレッシャーをかける。",
            "category": "サブミッション戦略",
            "belt": "青帯以上",
            "body": """
<p>サブミッションプレッシャーとは、仕上げだけでなく他のチャンスを開く反応を強制するために攻撃を脅かすことです。目標は相手を動かし、その動きを利用することです。</p>

<h2>サブミッション＝スウィープのダイナミクス</h2>
<p>すべてのサブミッションの脅威は、相手がディフェンスするとスウィープも脅かす必要があります。この両方向の脅威がガードプレイをサブミッションが完成しなくても脅威的にするものです。</p>
<h3>例</h3>
<ul>
<li>トライアングル＋アームバー：腕を引いたらトライアングルを攻める；スタックしたらアームバーをセット</li>
<li>キムラ＋ヒップバンプスウィープ：クローズドガードからキムラを脅かし、相手が姿勢を正す → ヒップバンプスウィープ</li>
<li>オモプラータ＋スウィープ：相手がロールアウトしたら → オモプラータスウィープか肩ロックに従う</li>
</ul>

<h2>防御的反応を作る</h2>
<p>腕を攻撃すると、相手はどのようにディフェンスするかを決めなければなりません。その決定があなたが利用できるパターンを生み出します。</p>
<h3>腕ディフェンスのパターン</h3>
<ul>
<li>肘を引いた → ベースボールチョークかエゼキエルで上から</li>
<li>頭を押した → そちら側のトライアングルの角度を開く</li>
<li>スタックした → デラヒーバからニーバーまたはヒールフックに切り替え</li>
</ul>

<h2>グリップシーケンスをプレッシャーとして</h2>
<p>良いグリップはサブミッションプレッシャーの最初の層です。強いクロスカラーグリップは相手にすぐに対処することを強制し、次の攻撃への開口部を作ります。</p>

<h2>ポジションプレッシャー対サブミッションプレッシャー</h2>
<ul>
<li>重いサイドコントロール＋キムラグリップ = 相手は明確に考えられない</li>
<li>フック付きバックコントロール＋ネックグリップ = 絶え間ない脅威がミスを強制</li>
</ul>

<h2>プレッシャートレーニング方法</h2>
<ul>
<li>攻撃のみのラウンド：ポジション前進ではなくサブミッションのみを試みる</li>
<li>3攻撃ドリル：一つのシーケンスで3つの異なる攻撃の脅威を繋げる</li>
<li>時間プレッシャー：60秒ラウンドで3つ以上のサブミッション試みを目標に</li>
</ul>
""",
            "amazon_text": "BJJサブミッション戦略",
            "amazon_kw": "BJJ+サブミッション+戦略",
        },
        "pt": {
            "title": "Pressão de Finalização no BJJ: Usando Ataques para Criar Aberturas | BJJ Wiki",
            "h1": "Pressão de Finalização no BJJ",
            "desc": "Aprenda a usar ameaças de finalização estrategicamente no BJJ — aplicando pressão que força reações e cria oportunidades de sweep ou avanço posicional.",
            "category": "Estratégia de Finalização",
            "belt": "Faixa Azul+",
            "body": """
<p>Pressão de finalização significa ameaçar ataques não apenas para finalizar, mas para forçar reações que abrem outras oportunidades.</p>

<h2>A Dinâmica Finalização-Sweep</h2>
<h3>Exemplos</h3>
<ul>
<li>Triângulo + armbar: se puxarem o braço, ataque o triângulo; se empilharem, set armbar</li>
<li>Kimura + hip bump sweep: ameace kimura da guarda fechada, eles posturam → hip bump sweep</li>
<li>Omoplata + sweep: se rolarem fora → siga para sweep de omoplata ou chave de ombro</li>
</ul>

<h2>Criando Reações Defensivas</h2>
<h3>Padrões de Defesa de Braço</h3>
<ul>
<li>Puxam o cotovelo → vá por cima com baseball choke ou ezekiel</li>
<li>Empurram sua cabeça → abra o ângulo de triângulo naquele lado</li>
<li>Empilham → mude para kneebar ou heel hook de de la riva</li>
</ul>

<h2>Métodos de Treino de Pressão</h2>
<ul>
<li>Rounds apenas de ataque: tente apenas finalizações, não avanço posicional</li>
<li>Drill de três ataques: conecte 3 ameaças de ataque diferentes em uma sequência</li>
<li>Pressão de tempo: rounds de 60 segundos onde você deve tentar 3+ finalizações</li>
</ul>
""",
            "amazon_text": "Estratégia de Finalização BJJ",
            "amazon_kw": "BJJ+submission+strategy+guard",
        },
    },
    {
        "slug": "bjj-training-intensity-guide",
        "en": {
            "title": "BJJ Training Intensity: Managing Effort for Long-Term Progress | BJJ Wiki",
            "h1": "BJJ Training Intensity Management",
            "desc": "Learn how to calibrate BJJ training intensity through periodization, flow rolling vs. hard drilling, and managing fatigue to maximize long-term improvement without injury.",
            "category": "Training Methodology",
            "belt": "White Belt+",
            "body": """
<p>Training intensity is one of the most misunderstood aspects of BJJ development. Many beginners go too hard all the time; experienced practitioners learn to modulate intensity for maximum long-term gains.</p>

<h2>The Intensity Spectrum</h2>
<p>BJJ training exists on a spectrum from pure flow to maximum competition effort:</p>
<ol>
<li><strong>Solo drilling (0% intensity)</strong> — Pure technique repetition, no resistance</li>
<li><strong>Flow rolling (30-40%)</strong> — Cooperative movement, technique focus, light resistance</li>
<li><strong>Positional drilling (50-60%)</strong> — Resistance in specific positions, problem-solving</li>
<li><strong>Hard sparring (70-85%)</strong> — Competitive training, full resistance but controlled</li>
<li><strong>Competition simulation (90-100%)</strong> — Full intensity, used sparingly</li>
</ol>

<h2>Why Flow Rolling Matters</h2>
<p>Flow rolling allows you to practice transitions and combinations at a speed where your brain can process and learn. High-intensity sparring moves too fast for many technique improvements to occur.</p>
<ul>
<li>Use flow rolling to experiment with new techniques</li>
<li>Try positions that feel uncomfortable when going hard</li>
<li>Focus on movement quality, not winning</li>
</ul>

<h2>Weekly Intensity Distribution</h2>
<p>A well-structured BJJ week might look like:</p>
<ul>
<li><strong>Monday:</strong> Technical drilling + light flow rolling (30-40%)</li>
<li><strong>Wednesday:</strong> Positional rounds + medium sparring (60-70%)</li>
<li><strong>Friday:</strong> Hard sparring rounds (75-85%)</li>
<li><strong>Saturday:</strong> Open mat — mixed intensity based on partners</li>
</ul>

<h2>Signs You Are Training Too Hard</h2>
<ul>
<li>Joint pain that persists between sessions</li>
<li>Dreading training sessions</li>
<li>Plateau or regression in technique quality</li>
<li>Frequent illness (suppressed immune system)</li>
<li>Sleep disturbances after evening training</li>
</ul>

<h2>Periodization for BJJ</h2>
<p>Periodization means planned variation in training load over weeks or months to optimize performance and recovery:</p>
<ul>
<li><strong>Base phase:</strong> 3-4 weeks of moderate volume, technique focus</li>
<li><strong>Build phase:</strong> 3-4 weeks of increasing intensity</li>
<li><strong>Peak phase:</strong> 1-2 weeks of high intensity (pre-competition)</li>
<li><strong>Recovery phase:</strong> 1 week of light drilling and rest</li>
</ul>

<h2>Adjusting Intensity by Injury Status</h2>
<ul>
<li>Active injury: technical drilling only, avoid positions that stress the injury</li>
<li>Recovering: flow rolling with trusted partners who understand your limitations</li>
<li>Healthy: full program with planned hard days</li>
</ul>
""",
            "amazon_text": "BJJ Training Programming",
            "amazon_kw": "BJJ+training+periodization+fitness",
        },
        "ja": {
            "title": "BJJトレーニング強度：長期的な進歩のための努力管理 | BJJ Wiki",
            "h1": "BJJトレーニング強度管理",
            "desc": "ピリオダイゼーション、フローローリング対ハードドリリング、疲労管理を通じてBJJトレーニング強度を調整し、怪我なく長期的な上達を最大化する方法を学ぼう。",
            "category": "トレーニング方法論",
            "belt": "白帯以上",
            "body": """
<p>トレーニング強度はBJJ上達において最も誤解されている側面の一つです。多くの初心者は常に全力で行きすぎます；経験豊富な実践者は最大の長期的利益のために強度を調整することを学びます。</p>

<h2>強度スペクトル</h2>
<p>BJJトレーニングは純粋なフローから最大競技努力までのスペクトルに存在します：</p>
<ol>
<li><strong>ソロドリリング（強度0%）</strong> — 純粋なテクニック繰り返し、抵抗なし</li>
<li><strong>フローローリング（30〜40%）</strong> — 協調的な動き、テクニック重視、軽い抵抗</li>
<li><strong>ポジショナルドリリング（50〜60%）</strong> — 特定のポジションでの抵抗、問題解決</li>
<li><strong>ハードスパーリング（70〜85%）</strong> — 競技的トレーニング、フル抵抗だがコントロールされている</li>
<li><strong>競技シミュレーション（90〜100%）</strong> — フル強度、まれに使用</li>
</ol>

<h2>フローローリングが重要な理由</h2>
<p>フローローリングはあなたの脳が処理して学べる速度でトランジションとコンビネーションを練習できます。高強度スパーリングは多くのテクニック改善が起こるには速すぎます。</p>
<ul>
<li>新しいテクニックを実験するためにフローローリングを使用</li>
<li>全力で行くと不快に感じるポジションを試す</li>
<li>勝つことではなく動きの質に焦点を当てる</li>
</ul>

<h2>週次強度配分</h2>
<p>構造化されたBJJの週はこのようになるかもしれません：</p>
<ul>
<li><strong>月曜：</strong>テクニカルドリリング＋軽いフローローリング（30〜40%）</li>
<li><strong>水曜：</strong>ポジショナルラウンド＋中程度スパーリング（60〜70%）</li>
<li><strong>金曜：</strong>ハードスパーリングラウンド（75〜85%）</li>
<li><strong>土曜：</strong>オープンマット — パートナーに基づいた混合強度</li>
</ul>

<h2>練習しすぎのサイン</h2>
<ul>
<li>セッション間で続く関節痛</li>
<li>練習を恐れる</li>
<li>テクニックの質の停滞または後退</li>
<li>頻繁な病気（抑制された免疫システム）</li>
<li>夜の練習後の睡眠障害</li>
</ul>

<h2>BJJのためのピリオダイゼーション</h2>
<p>ピリオダイゼーションとは、パフォーマンスと回復を最適化するために数週間または数ヶ月にわたってトレーニング負荷を計画的に変化させることです：</p>
<ul>
<li><strong>ベースフェーズ：</strong>テクニック重視の中程度のボリューム3〜4週</li>
<li><strong>ビルドフェーズ：</strong>強度が増加する3〜4週</li>
<li><strong>ピークフェーズ：</strong>高強度の1〜2週（競技前）</li>
<li><strong>回復フェーズ：</strong>軽いドリリングと休息の1週</li>
</ul>
""",
            "amazon_text": "BJJトレーニングプログラミング",
            "amazon_kw": "BJJ+トレーニング+ピリオダイゼーション",
        },
        "pt": {
            "title": "Intensidade do Treinamento de BJJ: Gerenciando o Esforço para Progresso | BJJ Wiki",
            "h1": "Gerenciamento da Intensidade do Treinamento de BJJ",
            "desc": "Aprenda a calibrar a intensidade do treinamento de BJJ através de periodização, flow rolling versus drilling intenso e gerenciamento de fadiga para maximizar o progresso.",
            "category": "Metodologia de Treinamento",
            "belt": "Faixa Branca+",
            "body": """
<p>A intensidade do treinamento é um dos aspectos mais mal compreendidos do desenvolvimento no BJJ. Muitos iniciantes vão muito forte o tempo todo; praticantes experientes aprendem a modular a intensidade.</p>

<h2>O Espectro de Intensidade</h2>
<ol>
<li><strong>Drilling solo (0% intensidade)</strong> — Repetição pura de técnica, sem resistência</li>
<li><strong>Flow rolling (30-40%)</strong> — Movimento cooperativo, foco em técnica</li>
<li><strong>Drilling posicional (50-60%)</strong> — Resistência em posições específicas</li>
<li><strong>Sparring intenso (70-85%)</strong> — Treinamento competitivo, resistência completa mas controlada</li>
<li><strong>Simulação de competição (90-100%)</strong> — Intensidade total, usado raramente</li>
</ol>

<h2>Por Que o Flow Rolling Importa</h2>
<ul>
<li>Use flow rolling para experimentar novas técnicas</li>
<li>Tente posições que parecem desconfortáveis no sparring intenso</li>
<li>Foque na qualidade do movimento, não em ganhar</li>
</ul>

<h2>Distribuição Semanal de Intensidade</h2>
<ul>
<li><strong>Segunda:</strong> Drilling técnico + flow rolling leve (30-40%)</li>
<li><strong>Quarta:</strong> Rounds posicionais + sparring médio (60-70%)</li>
<li><strong>Sexta:</strong> Rounds de sparring intenso (75-85%)</li>
<li><strong>Sábado:</strong> Open mat — intensidade mista</li>
</ul>

<h2>Sinais de Treino Excessivo</h2>
<ul>
<li>Dor articular que persiste entre sessões</li>
<li>Temer as sessões de treino</li>
<li>Platô ou regressão na qualidade técnica</li>
<li>Doenças frequentes (sistema imune suprimido)</li>
</ul>

<h2>Periodização para BJJ</h2>
<ul>
<li><strong>Fase base:</strong> 3-4 semanas de volume moderado, foco em técnica</li>
<li><strong>Fase de construção:</strong> 3-4 semanas de intensidade crescente</li>
<li><strong>Fase de pico:</strong> 1-2 semanas de alta intensidade (pré-competição)</li>
<li><strong>Fase de recuperação:</strong> 1 semana de drilling leve e descanso</li>
</ul>
""",
            "amazon_text": "Programação de Treinamento BJJ",
            "amazon_kw": "BJJ+training+periodization+fitness",
        },
    },
]


def build_hreflang(slug):
    base = "https://wiki.bjj-app.net"
    return f"""
  <link rel="alternate" hreflang="en" href="{base}/en/{slug}.html" />
  <link rel="alternate" hreflang="ja" href="{base}/ja/{slug}.html" />
  <link rel="alternate" hreflang="pt" href="{base}/pt/{slug}.html" />
  <link rel="alternate" hreflang="x-default" href="{base}/en/{slug}.html" />"""


def build_page(slug, lang, data, hreflang):
    base_url = "https://wiki.bjj-app.net"
    page_url = f"{base_url}/{lang}/{slug}.html"
    now = datetime.date.today().isoformat()

    # Amazon domain by language
    if lang == "ja":
        amazon_domain = "amazon.co.jp"
        home_label = "ホーム"
        wiki_label = "BJJ Wiki"
        related_label = "関連ページ"
        share_label = "シェア"
        app_cta = "📱 BJJ練習記録アプリ（無料）→"
        app_url = "https://bjj-app-one.vercel.app"
        app_desc = "練習ログ・テクニック帳・ストリーク機能"
    elif lang == "pt":
        amazon_domain = "amazon.com.br"
        home_label = "Home"
        wiki_label = "BJJ Wiki"
        related_label = "Páginas Relacionadas"
        share_label = "Compartilhar"
        app_cta = "📱 App de Registro BJJ (Gratuito) →"
        app_url = "https://bjj-app-one.vercel.app"
        app_desc = "Registro de treinos, técnicas e streaks"
    else:
        amazon_domain = "amazon.com"
        home_label = "Home"
        wiki_label = "BJJ Wiki"
        related_label = "Related Pages"
        share_label = "Share"
        app_cta = "📱 Free BJJ Training App →"
        app_url = "https://bjj-app-one.vercel.app"
        app_desc = "Log sessions, track techniques, build streaks"

    amazon_url = f"https://www.{amazon_domain}/s?k={data['amazon_kw']}&tag=bjj06-22"

    # Breadcrumb
    breadcrumb_cat = data["category"]
    breadcrumb_html = f"""
<nav class="breadcrumb" aria-label="breadcrumb">
  <ol>
    <li><a href="../index.html">{home_label}</a></li>
    <li><a href="../index.html">{wiki_label}</a></li>
    <li><span>{breadcrumb_cat}</span></li>
    <li><span>{data["h1"]}</span></li>
  </ol>
</nav>"""

    # Beehiiv form
    if lang == "ja":
        bee_title = "BJJニュースレター（2,000人以上登録）"
        bee_desc = "無料BJJ白帯ガイドをもらう"
        bee_btn = "無料で受け取る →"
        bee_note = "迷惑メールなし。いつでも解除可能。"
    elif lang == "pt":
        bee_title = "Newsletter BJJ (2.000+ praticantes)"
        bee_desc = "Receba o Guia Gratuito de Faixa Branca"
        bee_btn = "Acesso Gratuito →"
        bee_note = "Sem spam. Cancele quando quiser."
    else:
        bee_title = "BJJ Newsletter (2,000+ Practitioners)"
        bee_desc = "Get the Free BJJ White Belt Guide"
        bee_btn = "Get Free Access →"
        bee_note = "No spam. Unsubscribe anytime."

    json_ld = f"""{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{data['h1']}",
  "description": "{data['desc']}",
  "url": "{page_url}",
  "datePublished": "{now}",
  "dateModified": "{now}",
  "inLanguage": "{lang}",
  "author": {{"@type": "Organization", "name": "BJJ Wiki"}},
  "publisher": {{"@type": "Organization", "name": "BJJ Wiki", "url": "{base_url}"}}
}}"""

    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" href="https://wiki.bjj-app.net/favicon.svg" type="image/svg+xml">
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{data['title']}</title>
  <meta name="description" content="{data['desc']}" />
  <meta property="og:title" content="{data['title']}" />
  <meta property="og:description" content="{data['desc']}" />
  <meta property="og:url" content="{page_url}" />
  <meta property="og:type" content="article" />
    <meta property="og:site_name" content="BJJ Wiki">
  <meta name="twitter:card" content="summary" />
  {hreflang}
  <link rel="stylesheet" href="../wiki-v2.css" />
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-XXXXXXXXXX');
  </script>
  <script type="application/ld+json">{json_ld}</script>
</head>
<body>
<header>
  <nav class="site-nav">
    <a href="../index.html" class="nav-logo">🥋 BJJ Wiki</a>
  </nav>
</header>
<main class="container">
  {breadcrumb_html}

  <article class="bjj-article">
    <div class="article-meta">
      <span class="category-tag">🥋 {data['category']}</span>
      <span class="belt-tag">{data['belt']}</span>
    </div>
    <h1>{data['h1']}</h1>
    <p class="article-desc">{data['desc']}</p>

    {data['body']}

    <!-- BJJ App CTA -->
    <div class="app-cta-banner" style="background:linear-gradient(135deg,#1a1a2e,#16213e);border:1px solid #e94560;border-radius:12px;padding:20px;margin:32px 0;text-align:center;">
      <a href="{app_url}" target="_blank" rel="noopener" style="color:#e94560;font-weight:bold;font-size:1.1em;" onclick="gtag('event','app_cta_click',{{'page':'{slug}','lang':'{lang}'}})">
        {app_cta}
      </a>
      <p style="color:#aaa;font-size:0.85em;margin:8px 0 0;">{app_desc}</p>
    </div>

    <!-- Affiliate -->
    <div class="affiliate-section" style="background:#0f3460;border-radius:8px;padding:16px;margin:24px 0;">
      <p style="color:#aaa;font-size:0.8em;margin-bottom:8px;">PR</p>
      <a href="{amazon_url}" class="affiliate-link" target="_blank" rel="noopener sponsored"
         onclick="gtag('event','amazon_click',{{'page':'{slug}','lang':'{lang}'}})">
        ➜ Amazon: {data['amazon_text']}
      </a>
    </div>

    <!-- Beehiiv Newsletter -->
    <div class="beehiiv-wrap" style="background:#16213e;border:1px solid #0f3460;border-radius:12px;padding:24px;margin:32px 0;text-align:center;">
      <h3 style="color:#e94560;margin-bottom:8px;">{bee_title}</h3>
      <p style="color:#aaa;font-size:0.9em;margin-bottom:16px;">{bee_desc}</p>
      <iframe src="https://embeds.beehiiv.com/c7b5a1c0-1234-5678-abcd-ef0123456789"
              data-test-id="beehiiv-embed" width="100%" height="52" frameborder="0" scrolling="no"
              style="border-radius:4px;border:1px solid #0f3460;max-width:400px;"></iframe>
      <p style="color:#666;font-size:0.75em;margin-top:8px;">{bee_note}</p>
    </div>

    <!-- Share -->
    <div class="share-bar" style="display:flex;gap:12px;margin:24px 0;flex-wrap:wrap;">
      <a href="https://twitter.com/intent/tweet?text={data['h1']}&url={page_url}&hashtags=BJJ,JiuJitsu"
         target="_blank" rel="noopener" class="share-btn" style="background:#1da1f2;color:white;padding:8px 16px;border-radius:6px;text-decoration:none;font-size:0.85em;">
        𝕏 {share_label}
      </a>
    </div>
  </article>
</main>
<footer>
  <p style="text-align:center;color:#666;font-size:0.8em;padding:24px;">
    © 2024 BJJ Wiki — <a href="../index.html" style="color:#e94560;">Home</a>
  </p>
</footer>
</body>
</html>"""
    return html


def update_sitemap(new_slugs):
    sitemap_path = os.path.join(BASE, "sitemap.xml")
    with open(sitemap_path, encoding="utf-8") as f:
        content = f.read()

    today = datetime.date.today().isoformat()
    new_entries = ""
    base_url = "https://wiki.bjj-app.net"
    for slug in new_slugs:
        for lang in ["en", "ja", "pt"]:
            url = f"{base_url}/{lang}/{slug}.html"
            if url not in content:
                new_entries += f"""  <url>
    <loc>{url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
"""
    if new_entries:
        content = content.replace("</urlset>", new_entries + "</urlset>")
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(content)
        return len(new_entries.strip().split("<url>")) - 1
    return 0


def add_index_cards(new_slugs, pages_data):
    """Add cards to en/ja/pt index.html files"""
    for lang in ["en", "ja", "pt"]:
        index_path = os.path.join(BASE, lang, "index.html")
        if not os.path.exists(index_path):
            continue
        with open(index_path, encoding="utf-8") as f:
            content = f.read()
        new_cards = ""
        for page in pages_data:
            slug = page["slug"]
            d = page[lang]
            if f"{slug}.html" not in content:
                new_cards += f"""
<div class="tech-card">
  <a href="{slug}.html">
    <span class="cat-tag">{d['category']}</span>
    <h3>{d['h1']}</h3>
    <p>{d['desc'][:100]}...</p>
  </a>
</div>
"""
        if new_cards and "</main>" in content:
            content = content.replace("</main>", new_cards + "\n</main>")
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(content)


def main():
    generated = 0
    new_slugs = []
    for page in PAGES:
        slug = page["slug"]
        hreflang = build_hreflang(slug)
        for lang in ["en", "ja", "pt"]:
            out_dir = os.path.join(BASE, lang)
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"{slug}.html")
            if os.path.exists(out_path):
                print(f"  SKIP (exists): {lang}/{slug}.html")
                continue
            html = build_page(slug, lang, page[lang], hreflang)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  CREATED: {lang}/{slug}.html")
            generated += 1
        new_slugs.append(slug)

    # Update sitemap
    added = update_sitemap(new_slugs)
    print(f"\nSitemap: +{added} URLs added")

    # Add index cards
    add_index_cards(new_slugs, PAGES)
    print(f"Index cards updated for {len(new_slugs)} pages")

    print(f"\nTotal pages generated: {generated}")
    print("Batch 387-391 complete ✅")


if __name__ == "__main__":
    main()
