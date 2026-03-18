#!/usr/bin/env python3
"""BJJ Wiki Batch 392-396: 5 new themes x 3 languages = 15 pages"""
import os, re, datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = [
    {
        "slug": "bjj-guard-systems-advanced",
        "en": {
            "title": "Advanced BJJ Guard Systems: Complete Guide | BJJ Wiki",
            "h1": "Advanced BJJ Guard Systems",
            "desc": "A comprehensive guide to advanced guard systems in BJJ: spider guard, lasso guard, worm guard, and modern guard concepts that dominate high-level competition.",
            "category": "Guard",
            "belt": "Blue Belt+",
            "body": """
<p>Advanced guard systems represent the pinnacle of bottom game BJJ. Understanding multiple interconnected guard positions and their transitions creates a layered attack that is extremely difficult to pass.</p>

<h2>Spider Guard System</h2>
<p>Spider guard uses bicep and sleeve control with foot-on-hip frames to create constant off-balancing pressure on the passer.</p>
<h3>Core Mechanics</h3>
<ul>
<li><strong>Sleeve grips:</strong> Both hands controlling opponent's sleeves at the wrist</li>
<li><strong>Foot placement:</strong> One foot on bicep, one on hip for maximum control</li>
<li><strong>Hip movement:</strong> Constant lateral hip shifts to threaten sweeps</li>
<li><strong>Extension cycles:</strong> Push-pull rhythm to break posture and open attacks</li>
</ul>
<h3>Key Attacks from Spider Guard</h3>
<ul>
<li>Triangle choke via hip bump entry</li>
<li>Omoplata over the top leg</li>
<li>Flower sweep (petisco)</li>
<li>Lasso guard transition for backtake</li>
</ul>

<h2>Lasso Guard System</h2>
<p>Lasso guard wraps one arm around the outside of the opponent's arm with your leg threaded through, creating powerful rotational leverage.</p>
<h3>Building the Lasso</h3>
<ul>
<li>Start from spider guard or sitting guard</li>
<li>Thread your leg between opponent's arm and body</li>
<li>Hook your foot on the far hip for control</li>
<li>Maintain sleeve grip with the lasso arm</li>
</ul>
<h3>Lasso Sweep Options</h3>
<ul>
<li><strong>Back sweep:</strong> Push far hip, pull sleeve to sweep backward</li>
<li><strong>Pendulum sweep:</strong> Use lasso as pivot to swing opponent over</li>
<li><strong>Triangle setup:</strong> Release lasso, shoot hip through for triangle</li>
</ul>

<h2>Worm Guard System</h2>
<p>Worm guard uses the lapel threaded under the opponent's leg to create immobilizing control that opens unique attacks unavailable from other guards.</p>
<h3>Establishing Worm Guard</h3>
<ul>
<li>Feed your own lapel under opponent's far leg</li>
<li>Grip the lapel on the outside with your free hand</li>
<li>Control the opposite sleeve with your other hand</li>
<li>Keep constant tension to prevent the lapel being removed</li>
</ul>
<h3>Worm Guard Attacks</h3>
<ul>
<li>Crab ride to back take</li>
<li>Reverse triangle (triangulo reverso)</li>
<li>Knee bar over the trapped leg</li>
<li>Rolling back take</li>
</ul>

<h2>Guard Chaining and Transitions</h2>
<p>Elite guard players don't stay in one system — they chain between guards based on the passer's reactions, creating an ever-changing web of threats.</p>
<ul>
<li>Spider → DLR when passer steps wide</li>
<li>Lasso → Omoplata when grip is broken</li>
<li>Worm → Berimbolo when lapel is heavy</li>
<li>Any guard → Sit-up sweep under pressure</li>
</ul>

<div class="tip-box">
<strong>Pro Tip:</strong> The guard player should be attacking constantly. Every time the passer defends one threat, a new threat should be immediately presented. Guard passing is like defense — guard playing is like offense.
</div>

<h2>Training Advanced Guard Systems</h2>
<ul>
<li>Drill individual guard entries 50+ reps before live rolling</li>
<li>Use positional sparring starting from guard</li>
<li>Study specific competitors known for each guard (Caio Terra for spider, Cobrinha for lasso)</li>
<li>Record your rolls to identify recurring passer strategies</li>
</ul>
"""
        },
        "ja": {
            "title": "BJJ上級ガードシステム完全ガイド | BJJ Wiki",
            "h1": "BJJ上級ガードシステム",
            "desc": "BJJにおける高度なガードシステムの総合ガイド：スパイダーガード、ラッソガード、ワームガード、そして高レベル競技を支配する現代のガードコンセプト。",
            "category": "ガード",
            "belt": "青帯以上",
            "body": """
<p>上級ガードシステムは、BJJのボトムゲームの頂点を表しています。複数の相互に関連したガードポジションとそのトランジションを理解することで、非常に難しいパッシングに対応できる多層的な攻撃が生まれます。</p>

<h2>スパイダーガードシステム</h2>
<p>スパイダーガードは、袖のグリップとフット・オン・ヒップのフレームを使用して、パッサーに対して常にバランスを崩すプレッシャーを生み出します。</p>
<h3>コアメカニクス</h3>
<ul>
<li><strong>袖グリップ：</strong>両手で相手の袖の手首部分をコントロール</li>
<li><strong>足の配置：</strong>片足を二頭筋に、もう片足を腰に置いて最大限のコントロール</li>
<li><strong>ヒップムーブメント：</strong>スウィープを脅かすための絶え間ない横方向のヒップシフト</li>
<li><strong>伸展サイクル：</strong>姿勢を崩して攻撃を開くためのプッシュ・プルのリズム</li>
</ul>
<h3>スパイダーガードからの主要な攻撃</h3>
<ul>
<li>ヒップバンプエントリーによるトライアングルチョーク</li>
<li>上の足を越えるオモプラータ</li>
<li>フラワースウィープ（ペティスコ）</li>
<li>バックテイクのためのラッソガードトランジション</li>
</ul>

<h2>ラッソガードシステム</h2>
<p>ラッソガードは、足を相手の腕と体の間に通して片腕を外側に巻き付け、強力な回転的レバレッジを生み出します。</p>
<h3>ラッソの構築</h3>
<ul>
<li>スパイダーガードまたはシッティングガードからスタート</li>
<li>相手の腕と体の間に足を通す</li>
<li>コントロールのために遠い腰に足をフック</li>
<li>ラッソアームで袖グリップを維持</li>
</ul>

<h2>ワームガードシステム</h2>
<p>ワームガードは、相手の足の下に通した自分の襟を使用して、他のガードでは利用できないユニークな攻撃を開く固定コントロールを作り出します。</p>
<h3>ワームガードの確立</h3>
<ul>
<li>自分の襟を相手の遠い足の下に通す</li>
<li>空いた手で外側から襟を掴む</li>
<li>もう一方の手で反対の袖をコントロール</li>
<li>襟が取り除かれるのを防ぐために常に張力を保つ</li>
</ul>

<h2>ガードの連鎖とトランジション</h2>
<p>エリートのガードプレーヤーは一つのシステムにとどまらず、パッサーの反応に基づいてガードを切り替え、変化し続ける脅威のウェブを作り出します。</p>
<ul>
<li>パッサーが広くステップした時: スパイダー → DLR</li>
<li>グリップが切られた時: ラッソ → オモプラータ</li>
<li>ラペルが重い時: ワーム → ベリンボロ</li>
<li>プレッシャー下: どのガードでも → シットアップスウィープ</li>
</ul>

<div class="tip-box">
<strong>プロのヒント：</strong> ガードプレーヤーは常に攻撃し続けるべきです。パッサーが一つの脅威を防ぐたびに、新しい脅威をすぐに提示する必要があります。
</div>

<h2>上級ガードシステムのトレーニング</h2>
<ul>
<li>ライブローリングの前に個別のガードエントリーを50回以上ドリル</li>
<li>ガードから始めるポジショナルスパーリングを使用</li>
<li>各ガードで有名な競技者を研究する</li>
<li>繰り返しのパッサー戦略を特定するためにロールを録画</li>
</ul>
"""
        },
        "pt": {
            "title": "Sistemas de Guarda Avançados no BJJ: Guia Completo | BJJ Wiki",
            "h1": "Sistemas de Guarda Avançados no BJJ",
            "desc": "Um guia abrangente dos sistemas de guarda avançados no BJJ: guarda aranha, guarda lasso, worm guard e conceitos modernos que dominam a competição de alto nível.",
            "category": "Guarda",
            "belt": "Faixa Azul+",
            "body": """
<p>Os sistemas de guarda avançados representam o ponto mais alto do jogo de baixo no BJJ. Entender múltiplas posições de guarda interconectadas e suas transições cria um ataque em camadas extremamente difícil de passar.</p>

<h2>Sistema de Guarda Aranha</h2>
<p>A guarda aranha usa controle de bíceps e manga com frames de pé-no-quadril para criar pressão constante de desequilíbrio sobre o passador.</p>
<h3>Mecânicas Principais</h3>
<ul>
<li><strong>Pegadas na manga:</strong> Ambas as mãos controlando as mangas do adversário no pulso</li>
<li><strong>Posicionamento dos pés:</strong> Um pé no bíceps, um no quadril para controle máximo</li>
<li><strong>Movimento do quadril:</strong> Constantes mudanças laterais do quadril para ameaçar raspagens</li>
<li><strong>Ciclos de extensão:</strong> Ritmo de empurrar-puxar para quebrar a postura e abrir ataques</li>
</ul>
<h3>Principais Ataques da Guarda Aranha</h3>
<ul>
<li>Triângulo via entrada de bump de quadril</li>
<li>Omoplata sobre a perna de cima</li>
<li>Raspagem de flor (petisco)</li>
<li>Transição para guarda lasso para pegada de costas</li>
</ul>

<h2>Sistema de Guarda Lasso</h2>
<p>A guarda lasso enrola um braço ao redor do lado de fora do braço do adversário com sua perna atravessada, criando uma alavancagem rotacional poderosa.</p>
<h3>Construindo o Lasso</h3>
<ul>
<li>Comece da guarda aranha ou guarda sentada</li>
<li>Passe sua perna entre o braço e o corpo do adversário</li>
<li>Encaixe seu pé no quadril distante para controle</li>
<li>Mantenha a pegada na manga com o braço lasso</li>
</ul>

<h2>Sistema de Worm Guard</h2>
<p>O worm guard usa a lapela passada por baixo da perna do adversário para criar um controle imobilizador que abre ataques únicos indisponíveis em outras guardas.</p>
<h3>Estabelecendo o Worm Guard</h3>
<ul>
<li>Passe sua própria lapela por baixo da perna distante do adversário</li>
<li>Segure a lapela por fora com a mão livre</li>
<li>Controle a manga oposta com a outra mão</li>
<li>Mantenha tensão constante para evitar que a lapela seja removida</li>
</ul>

<h2>Encadeamento e Transições de Guarda</h2>
<p>Jogadores de guarda de elite não ficam em um sistema — eles transitam entre guardas baseados nas reações do passador, criando uma teia sempre mutante de ameaças.</p>
<ul>
<li>Aranha → DLR quando o passador dá um passo largo</li>
<li>Lasso → Omoplata quando a pegada é quebrada</li>
<li>Worm → Berimbolo quando a lapela pesa</li>
<li>Qualquer guarda → Raspagem de sentar sob pressão</li>
</ul>

<div class="tip-box">
<strong>Dica Pro:</strong> O jogador de guarda deve estar atacando constantemente. Toda vez que o passador defende uma ameaça, uma nova ameaça deve ser imediatamente apresentada.
</div>
"""
        }
    },
    {
        "slug": "bjj-pressure-game-mastery",
        "en": {
            "title": "BJJ Pressure Game: Top Control & Crushing Weight | BJJ Wiki",
            "h1": "BJJ Pressure Game Mastery",
            "desc": "Master the BJJ pressure game: using weight distribution, frames, and positional mechanics to crush opponents from top positions and create submission setups.",
            "category": "Top Game",
            "belt": "Blue Belt+",
            "body": """
<p>The pressure game in BJJ uses weight, angles, and friction to make the bottom player uncomfortable and unable to execute their game. When done correctly, it feels like suffocation — relentless weight pressing from every angle.</p>

<h2>Fundamentals of Pressure</h2>
<p>Effective pressure is not just about being heavy. It requires specific hip-to-hip alignment, distributing weight through your center of gravity onto key pressure points.</p>
<h3>Key Pressure Points on the Opponent</h3>
<ul>
<li><strong>Chest and sternum:</strong> Maximum discomfort for breathing</li>
<li><strong>Near-side shoulder:</strong> Prevents hip escape and frame building</li>
<li><strong>Head and far-side neck:</strong> Forces head alignment, limits mobility</li>
<li><strong>Hip pocket:</strong> Prevents framing and guard recovery</li>
</ul>
<h3>Pressure vs. Movement Trade-off</h3>
<p>Heavy pressure creates control but sacrifices mobility. You must constantly cycle between applying pressure to slow the bottom player and moving to maintain positional superiority.</p>

<h2>Side Control Pressure</h2>
<p>Side control is the primary pressure position. The key is chest-to-chest connection with your weight settled into the near-side armpit.</p>
<h3>The "Crossface" Pressure System</h3>
<ul>
<li>Drive your forearm across the opponent's jaw/neck (crossface)</li>
<li>This turns their head away and collapses their defensive frame</li>
<li>Maintain pressure while reaching under for submissions</li>
<li>Your hips should be perpendicular to theirs for maximum control</li>
</ul>
<h3>Side Control to Mount Transition</h3>
<ul>
<li>Use crossface to drive their head away</li>
<li>Swim your near knee across their belly</li>
<li>Post your far foot on the mat for base</li>
<li>Sit up into mount, never losing chest connection</li>
</ul>

<h2>Mount Pressure</h2>
<p>High mount (above the hips) creates intense pressure but is more vulnerable to escape. Low mount (on the hips) is more stable and sustainable.</p>
<h3>Low Mount Mechanics</h3>
<ul>
<li>Sit heavy on opponent's hips, feet hooked under their thighs</li>
<li>Lean forward slightly, posting hands near their shoulders</li>
<li>Keep your weight on your hips, not your hands</li>
<li>React instantly to elbow-knee escape attempts</li>
</ul>
<h3>S-Mount System</h3>
<ul>
<li>Figure-four one leg with the other supporting</li>
<li>Creates immense pressure on the shoulder and arm</li>
<li>Ideal setup for arm triangles and armbar</li>
</ul>

<h2>Knee on Belly Pressure</h2>
<p>KOB applies a single knee across the belly, creating acute pain pressure that forces reactions from the bottom player.</p>
<ul>
<li>Shin parallel to opponent's belt line</li>
<li>Pressure through the shin, not the knee cap</li>
<li>Stay light — ready to adjust when they bridge or frame</li>
<li>Use reactions to transition to mount, side control, or submissions</li>
</ul>

<h2>Combining Pressure with Submissions</h2>
<p>Pressure alone doesn't finish matches — it creates the setups. Use pressure to restrict movement, then flow into submission attempts while they're compromised.</p>
<ul>
<li>Heavy side control → Arm triangle when they post on your head</li>
<li>KOB → Far-side armbar when they push your knee</li>
<li>Mount → Ezekiel choke when they hug your hips</li>
</ul>

<div class="tip-box">
<strong>Training Tip:</strong> Practice pressure game with a larger, stronger partner. If your pressure works on someone who can physically resist, it will work on anyone of similar size.
</div>
"""
        },
        "ja": {
            "title": "BJJプレッシャーゲームマスタリー：トップコントロールと圧倒的な体重 | BJJ Wiki",
            "h1": "BJJプレッシャーゲームマスタリー",
            "desc": "BJJのプレッシャーゲームをマスターする：体重配分、フレーム、ポジショナルメカニクスを使って、トップポジションから相手を圧迫しサブミッションのセットアップを作る方法。",
            "category": "トップゲーム",
            "belt": "青帯以上",
            "body": """
<p>BJJにおけるプレッシャーゲームは、体重、角度、摩擦を使って、ボトムプレーヤーを不快にし自分のゲームを実行できない状態にします。正しく行うと、まるで窒息しているかのような感覚になります。</p>

<h2>プレッシャーの基礎</h2>
<p>効果的なプレッシャーは単に重いだけでは不十分です。特定のヒップ・ツー・ヒップのアライメントと、重心を通して重要なプレッシャーポイントに体重を配分することが必要です。</p>
<h3>相手の主要なプレッシャーポイント</h3>
<ul>
<li><strong>胸と胸骨：</strong>呼吸に最大の不快感</li>
<li><strong>近い側の肩：</strong>ヒップエスケープとフレーム構築を防止</li>
<li><strong>頭と遠い側の首：</strong>頭の向きを制限し、可動性を低下させる</li>
<li><strong>腰のポケット：</strong>フレーミングとガードリカバリーを防止</li>
</ul>

<h2>サイドコントロールのプレッシャー</h2>
<p>サイドコントロールは主要なプレッシャーポジションです。重要なのは、近い側の脇の下に体重をかけた胸・胸の密着です。</p>
<h3>「クロスフェイス」プレッシャーシステム</h3>
<ul>
<li>相手の顎/首にクロスフェイスとして前腕を押し付ける</li>
<li>これにより頭が反対側を向き、防御フレームが崩れる</li>
<li>サブミッションに向けて腕を差し込みながらプレッシャーを維持</li>
<li>最大限のコントロールのためにヒップは相手のヒップに対して垂直であること</li>
</ul>

<h2>マウントのプレッシャー</h2>
<p>ハイマウント（腰の上）は強烈なプレッシャーを生み出しますが、エスケープに対してより脆弱です。ローマウント（腰の上）はより安定しています。</p>
<h3>ローマウントメカニクス</h3>
<ul>
<li>相手の腰に重く座り、足を太ももの下にフック</li>
<li>わずかに前傾み、手を相手の肩の近くにポスト</li>
<li>手ではなく、腰に体重をかける</li>
<li>エルボー・ニーエスケープの試みに即座に反応</li>
</ul>

<h2>ニー・オン・ベリーのプレッシャー</h2>
<p>KOBは単一の膝を腹に当て、ボトムプレーヤーから反応を引き出す鋭い痛みのプレッシャーを作り出します。</p>
<ul>
<li>すねを相手のベルトラインに平行に</li>
<li>膝蓋骨ではなく、すねにプレッシャーをかける</li>
<li>軽くいる — 橋をかけたりフレームを作ったりしたときに調整できるよう</li>
</ul>

<div class="tip-box">
<strong>トレーニングのヒント：</strong> より大きく強い練習パートナーと一緒にプレッシャーゲームを練習してください。体力的に抵抗できる相手にプレッシャーが効くなら、同じサイズの誰にでも効きます。
</div>
"""
        },
        "pt": {
            "title": "Maestria no Jogo de Pressão do BJJ: Controle no Topo | BJJ Wiki",
            "h1": "Maestria no Jogo de Pressão do BJJ",
            "desc": "Domine o jogo de pressão do BJJ: usando distribuição de peso, frames e mecânicas posicionais para esmagar os oponentes das posições de cima e criar configurações de submissão.",
            "category": "Jogo no Topo",
            "belt": "Faixa Azul+",
            "body": """
<p>O jogo de pressão no BJJ usa peso, ângulos e atrito para tornar o jogador de baixo desconfortável e incapaz de executar seu jogo. Quando feito corretamente, parece asfixia.</p>

<h2>Fundamentos da Pressão</h2>
<p>Pressão efetiva não é apenas sobre ser pesado. Requer alinhamento específico de quadril a quadril, distribuindo peso através do seu centro de gravidade sobre pontos de pressão chave.</p>
<h3>Pontos de Pressão Chave no Oponente</h3>
<ul>
<li><strong>Peito e esterno:</strong> Máximo desconforto para respirar</li>
<li><strong>Ombro do lado próximo:</strong> Impede escape de quadril e construção de frames</li>
<li><strong>Cabeça e pescoço do lado distante:</strong> Força alinhamento da cabeça, limita mobilidade</li>
<li><strong>Bolso do quadril:</strong> Impede framing e recuperação da guarda</li>
</ul>

<h2>Pressão no Controle Lateral</h2>
<p>O controle lateral é a principal posição de pressão. A chave é a conexão peito a peito com seu peso assentado na axila do lado próximo.</p>
<h3>O Sistema de Pressão "Cross-face"</h3>
<ul>
<li>Direcione seu antebraço através da mandíbula/pescoço do oponente (cross-face)</li>
<li>Isso vira a cabeça para o lado e colapsa o frame defensivo deles</li>
<li>Mantenha pressão enquanto alcança por baixo para submissões</li>
</ul>

<h2>Pressão na Montada</h2>
<p>Montada alta (acima dos quadris) cria pressão intensa mas é mais vulnerável a escapes. Montada baixa (nos quadris) é mais estável e sustentável.</p>
<ul>
<li>Sente pesado nos quadris do oponente, pés enganchados sob as coxas</li>
<li>Incline-se levemente para frente, apoiando as mãos perto dos ombros deles</li>
<li>Mantenha seu peso nos quadris, não nas mãos</li>
</ul>

<div class="tip-box">
<strong>Dica de Treino:</strong> Pratique o jogo de pressão com um parceiro maior e mais forte. Se sua pressão funciona em alguém que pode resistir fisicamente, funcionará em qualquer um de tamanho similar.
</div>
"""
        }
    },
    {
        "slug": "bjj-back-attacks-advanced",
        "en": {
            "title": "Advanced Back Attacks in BJJ: Finishing Systems | BJJ Wiki",
            "h1": "Advanced Back Attacks in BJJ",
            "desc": "Master advanced back attack systems in BJJ: bow and arrow choke details, collar choke variations, armbar from back, and modern back-retention strategies.",
            "category": "Back Attacks",
            "belt": "Blue Belt+",
            "body": """
<p>The back position is the highest-scoring position in BJJ competition, and for good reason — the attacker controls everything while the defender has no direct offensive options. Advanced back attack systems build multiple simultaneous threats.</p>

<h2>Seatbelt Control Mechanics</h2>
<p>Proper seatbelt control is the foundation of all back attacks. The arm configuration determines both control quality and submission access.</p>
<h3>Standard Seatbelt</h3>
<ul>
<li>Top arm crosses over the shoulder and chest</li>
<li>Bottom arm hooks under the armpit</li>
<li>Hands grip together (gable grip or palm-to-palm)</li>
<li>Both hooks in, feet pointing outward, not crossing</li>
</ul>
<h3>Seatbelt Variations</h3>
<ul>
<li><strong>High seatbelt (over both shoulders):</strong> Access to collar choke, less escape-proof</li>
<li><strong>Body triangle:</strong> Replace hooks with figure-four of the legs, extremely stable</li>
<li><strong>Rear mount with hooks:</strong> Standard control, versatile attack options</li>
</ul>

<h2>Bow and Arrow Choke</h2>
<p>The bow and arrow is arguably the most powerful choke in gi BJJ. It uses the collar plus leg control for exponential leverage.</p>
<h3>Step-by-Step Execution</h3>
<ul>
<li>Establish seatbelt control with both hooks</li>
<li>Obtain deep cross-collar grip with the top hand (4 fingers in)</li>
<li>Use your bottom hand to pull opponent's same-side elbow</li>
<li>Extend your top leg, hooking your foot under opponent's near knee</li>
<li>Drop bottom shoulder to the mat while pulling the elbow</li>
<li>Arch your back like a drawn bow — the leg kick creates the choke's power</li>
</ul>
<h3>Common Mistakes</h3>
<ul>
<li>Not getting the collar deep enough — hand should grip at the base of the skull</li>
<li>Pulling the elbow across instead of down</li>
<li>Forgetting to extend the top leg for the "bow" effect</li>
</ul>

<h2>Rear Naked Choke (RNC) Mechanics</h2>
<p>The RNC is BJJ and MMA's most iconic finishing technique. Proper mechanics require chin-to-neck contact for the choke to cut blood flow.</p>
<h3>Blade of the Forearm vs. Crook of the Elbow</h3>
<ul>
<li>The blade of the forearm goes across the throat (tracheal pressure)</li>
<li>The crook of the elbow aligns with the carotid arteries</li>
<li>Optimal is the crook of the elbow at the trachea — compresses both carotids</li>
<li>The non-choking arm posts behind the opponent's head for amplification</li>
</ul>

<h2>Armbar from Back</h2>
<p>When the opponent defends the choke by tucking their chin or posting their arm, the armbar becomes available.</p>
<h3>Armbar Entry from Seatbelt</h3>
<ul>
<li>Opponent posts their arm on your forearm to block the choke attempt</li>
<li>Capture that arm by closing your elbow on it</li>
<li>Release one hook, swing your leg over their shoulder</li>
<li>Extend hips for armbar, control the wrist</li>
</ul>

<h2>Back Retention Strategies</h2>
<p>Finishing from the back requires maintaining the position when the opponent tries to escape. Understanding escape patterns allows you to stay ahead.</p>
<ul>
<li><strong>Shrimp escape prevention:</strong> Keep your chest glued to their back</li>
<li><strong>Rolling escape prevention:</strong> Stay on top, never let them roll over you</li>
<li><strong>Sit-out escape prevention:</strong> Use body triangle to prevent sitting</li>
<li><strong>Hand-fighting:</strong> Attack the near-side arm before they can grip your arms</li>
</ul>

<div class="tip-box">
<strong>Competition Strategy:</strong> In points-based competition, simply maintaining back position earns you 4 points. Focus on retention before submission — don't rush the finish and lose the position.
</div>
"""
        },
        "ja": {
            "title": "BJJ上級バックアタック：フィニッシングシステム | BJJ Wiki",
            "h1": "BJJ上級バックアタック",
            "desc": "BJJの上級バックアタックシステムをマスターする：ボウ・アンド・アローチョークの詳細、カラーチョークのバリエーション、バックからのアームバー、そして現代のバックリテンション戦略。",
            "category": "バックアタック",
            "belt": "青帯以上",
            "body": """
<p>バックポジションはBJJ競技で最高得点のポジションです。攻撃者がすべてをコントロールしながら、防御者は直接的な攻撃オプションがありません。高度なバックアタックシステムは複数の同時脅威を構築します。</p>

<h2>シートベルトコントロールのメカニクス</h2>
<p>適切なシートベルトコントロールは、すべてのバックアタックの基礎です。腕の配置によってコントロールの質とサブミッションへのアクセスが決まります。</p>
<h3>スタンダードシートベルト</h3>
<ul>
<li>上の腕が肩と胸を横断する</li>
<li>下の腕が脇の下にフックする</li>
<li>手がグリップされる（ゲーブルグリップまたはパーム・ツー・パーム）</li>
<li>両フックが入り、足は外を向き、交差しない</li>
</ul>

<h2>ボウ・アンド・アローチョーク</h2>
<p>ボウ・アンド・アローは、ギBJJで最も強力なチョークと言われています。カラーと脚のコントロールを組み合わせて指数関数的なレバレッジを使用します。</p>
<h3>ステップバイステップの実行</h3>
<ul>
<li>両フックを入れたシートベルトコントロールを確立する</li>
<li>上の手でディープなクロスカラーグリップを取得（4本指を入れる）</li>
<li>下の手を使って相手の同側の肘を引く</li>
<li>上の足を伸ばし、相手の近い側の膝の下に足をフック</li>
<li>肘を引きながら下の肩をマットに落とす</li>
<li>弓を引くように背中をアーチにする — 脚のキックがチョークの力を生む</li>
</ul>

<h2>裸絞め（RNC）のメカニクス</h2>
<p>RNCはBJJとMMAで最もアイコニックなフィニッシング技術です。適切なメカニクスでは、チョークが血流を遮断するために顎から首への接触が必要です。</p>
<ul>
<li>前腕のブレードが喉を横切る</li>
<li>肘の角が頸動脈に整列する</li>
<li>最適な位置は、気管に肘の角 — 両方の頸動脈を圧縮する</li>
</ul>

<h2>バックリテンション戦略</h2>
<p>バックからのフィニッシュには、相手がエスケープしようとするときにポジションを維持することが必要です。エスケープパターンを理解することで先手を打てます。</p>
<ul>
<li><strong>シュリンプエスケープ防止：</strong>胸を相手の背中にくっつけておく</li>
<li><strong>ローリングエスケープ防止：</strong>上にいて、絶対に乗り越えられないようにする</li>
<li><strong>サイトアウトエスケープ防止：</strong>ボディトライアングルを使って座るのを防ぐ</li>
</ul>
"""
        },
        "pt": {
            "title": "Ataques de Costas Avançados no BJJ: Sistemas de Finalização | BJJ Wiki",
            "h1": "Ataques de Costas Avançados no BJJ",
            "desc": "Domine sistemas avançados de ataques de costas no BJJ: detalhes do arco e flecha, variações de estrangulamento de gola, armlock de costas e estratégias modernas de retenção de costas.",
            "category": "Ataques de Costas",
            "belt": "Faixa Azul+",
            "body": """
<p>A posição de costas é a posição de maior pontuação na competição de BJJ, e por boas razões — o atacante controla tudo enquanto o defensor não tem opções ofensivas diretas.</p>

<h2>Mecânicas do Controle de Cinto de Segurança</h2>
<p>O controle de cinto de segurança adequado é a fundação de todos os ataques de costas.</p>
<h3>Cinto de Segurança Padrão</h3>
<ul>
<li>Braço de cima cruza sobre o ombro e peito</li>
<li>Braço de baixo engancha sob a axila</li>
<li>Mãos se unem (grip gable ou palma a palma)</li>
<li>Ambos os ganchos dentro, pés apontando para fora, sem cruzar</li>
</ul>

<h2>Arco e Flecha</h2>
<p>O arco e flecha é indiscutivelmente o estrangulamento mais poderoso no BJJ de kimono.</p>
<h3>Execução Passo a Passo</h3>
<ul>
<li>Estabeleça controle de cinto de segurança com ambos os ganchos</li>
<li>Obtenha pegada profunda na gola cruzada com a mão de cima (4 dedos dentro)</li>
<li>Use a mão de baixo para puxar o cotovelo do mesmo lado do oponente</li>
<li>Estenda sua perna de cima, enganchando seu pé sob o joelho próximo do oponente</li>
<li>Caia o ombro de baixo no tatame enquanto puxa o cotovelo</li>
<li>Arqueie suas costas como um arco desenhado — o chute da perna cria o poder do estrangulamento</li>
</ul>

<h2>Estratégias de Retenção de Costas</h2>
<p>Finalizar a partir das costas requer manter a posição quando o oponente tenta escapar.</p>
<ul>
<li><strong>Prevenção de escape de camarão:</strong> Mantenha seu peito colado nas costas deles</li>
<li><strong>Prevenção de escape rolando:</strong> Fique em cima, nunca deixe-os rolar sobre você</li>
<li><strong>Prevenção de escape sentando:</strong> Use triângulo de corpo para impedir de sentar</li>
</ul>
"""
        }
    },
    {
        "slug": "bjj-escapes-masterclass",
        "en": {
            "title": "BJJ Escapes Masterclass: Survive Every Position | BJJ Wiki",
            "h1": "BJJ Escapes Masterclass",
            "desc": "Master BJJ escapes from every major position: side control, mount, back, and knee on belly. Learn the mechanics, timing, and combinations that make escapes reliable at any level.",
            "category": "Defense",
            "belt": "White Belt+",
            "body": """
<p>In BJJ, the ability to escape bad positions is as important as the ability to attack. Even the best competitors get caught in inferior positions — what separates them is the ability to recover systematically and efficiently.</p>

<h2>Side Control Escapes</h2>
<p>Side control is the most common dominating position encountered in BJJ. Escapes require framing, creating space, and leveraging hip power.</p>
<h3>Elbow-Knee Escape (Elbow Push)</h3>
<ul>
<li>Frame your near elbow into opponent's hip, far hand frames their neck</li>
<li>Bridge and shrimp simultaneously to create space</li>
<li>Bring your far knee to the elbow space</li>
<li>Pull your other knee through to recover guard</li>
<li>Key: the elbow creates the space, the hip escape creates the distance</li>
</ul>
<h3>Granby Roll Escape</h3>
<ul>
<li>When opponent has tight side control, roll to your far shoulder</li>
<li>Invert your hips as you roll</li>
<li>Recover inverted guard or stand to create space</li>
<li>Works best when opponent is very tight and you have no space to frame</li>
</ul>
<h3>Ghost Escape</h3>
<ul>
<li>Best when opponent is too high (head near your head)</li>
<li>Reach your near arm over their back</li>
<li>Turn into them instead of away</li>
<li>Come up to your knees behind them</li>
</ul>

<h2>Mount Escapes</h2>
<p>Mount escapes must be initiated early — waiting until the opponent has established full mount makes escaping much harder.</p>
<h3>Trap and Roll (Upa)</h3>
<ul>
<li>Trap opponent's same-side arm and leg with your arm and leg</li>
<li>Plant your foot and bridge explosively</li>
<li>Roll them over to end in their guard</li>
<li>Only works well if you catch the arm before they post it</li>
</ul>
<h3>Elbow Escape from Mount</h3>
<ul>
<li>Frame with elbows into hip creases</li>
<li>Shrimp your hips to create space</li>
<li>Pull the near knee up through the space</li>
<li>Continue shrimping to recover half guard, then full guard</li>
</ul>
<h3>Timing Escapes</h3>
<ul>
<li>Escape when opponent transitions or commits to submission setup</li>
<li>Bridge when they reach for your collar</li>
<li>Shrimp when they reach for an armbar</li>
</ul>

<h2>Back Escapes</h2>
<p>Back escapes are the most difficult — the attacker has control and visibility while you cannot directly see them. Focus on defending the choke first, then escaping.</p>
<h3>Chin Tuck Defense</h3>
<ul>
<li>Immediately tuck your chin when back is taken</li>
<li>Grip the choking forearm with both hands</li>
<li>Pull down to prevent the choke completing</li>
</ul>
<h3>Roll to Guard</h3>
<ul>
<li>Remove bottom hook by pulling foot off your thigh</li>
<li>Roll over your shoulder to their guard</li>
<li>Better to give up the back and fight from guard than be choked</li>
</ul>
<h3>Seat Escape (Slide Out)</h3>
<ul>
<li>When opponent's hooks are shallow, slide hips out</li>
<li>Turn to face them as you escape</li>
<li>Establish guard position</li>
</ul>

<h2>Knee on Belly Escape</h2>
<p>KOB creates acute pressure — the key is to move before the pain becomes overwhelming.</p>
<ul>
<li><strong>Push the knee:</strong> Frame both hands on the knee, push laterally as you shrimp</li>
<li><strong>Duck under:</strong> Bring near elbow under the knee, turn into turtle</li>
<li><strong>Take the back:</strong> If they over-commit, reach under and take single-leg</li>
</ul>

<div class="tip-box">
<strong>The Golden Rule of Escapes:</strong> Always escape early. The longer you wait in a bad position, the more tired you become and the harder the escape gets. Feel the danger coming and move immediately.
</div>

<h2>Building Escape Reflexes</h2>
<ul>
<li>Positional sparring starting in mounted position</li>
<li>Solo drills: shrimp, bridge, granby roll, technical stand-up</li>
<li>Have training partners apply progressive weight to build tolerance and timing</li>
<li>Study your worst positions on video — identify where you lose the fight</li>
</ul>
"""
        },
        "ja": {
            "title": "BJJエスケープマスタークラス：すべてのポジションから生き残る | BJJ Wiki",
            "h1": "BJJエスケープマスタークラス",
            "desc": "すべての主要ポジションからのBJJエスケープをマスターする：サイドコントロール、マウント、バック、ニー・オン・ベリー。あらゆるレベルで信頼できるエスケープをするためのメカニクス、タイミング、コンビネーション。",
            "category": "ディフェンス",
            "belt": "白帯以上",
            "body": """
<p>BJJでは、悪いポジションからエスケープする能力は攻撃する能力と同じくらい重要です。最高の競技者でも不利なポジションに捕まります — 彼らを区別するのは、系統的かつ効率的に回復する能力です。</p>

<h2>サイドコントロールエスケープ</h2>
<p>サイドコントロールはBJJで最も一般的な支配ポジションです。エスケープにはフレーミング、スペースの作成、腰の力の活用が必要です。</p>
<h3>エルボー・ニーエスケープ</h3>
<ul>
<li>近い肘を相手の腰に、遠い手を相手の首にフレームとして置く</li>
<li>ブリッジとシュリンプを同時に行いスペースを作る</li>
<li>遠い膝を肘のスペースに持ってくる</li>
<li>もう一方の膝を引き通してガードを回復</li>
<li>重要：肘がスペースを作り、ヒップエスケープが距離を作る</li>
</ul>

<h2>マウントエスケープ</h2>
<p>マウントエスケープは早期に開始する必要があります — 相手がフルマウントを確立するまで待つとエスケープがはるかに難しくなります。</p>
<h3>トラップ・アンド・ロール（ウパ）</h3>
<ul>
<li>相手の同側の腕と足を自分の腕と足でトラップ</li>
<li>足を植えて爆発的にブリッジ</li>
<li>彼らを転がしてガード内に入る</li>
</ul>
<h3>マウントからのエルボーエスケープ</h3>
<ul>
<li>ヒップクリースに肘をフレームとして入れる</li>
<li>スペースを作るために腰をシュリンプ</li>
<li>スペースを通して近い膝を引き上げる</li>
<li>ハーフガード、次にフルガードを回復するまでシュリンプを続ける</li>
</ul>

<h2>バックエスケープ</h2>
<p>バックエスケープは最も難しい — 攻撃者はコントロールと視野を持っているが、あなたは直接彼らを見ることができません。チョークを防ぎ、次にエスケープすることに集中してください。</p>
<h3>顎タックディフェンス</h3>
<ul>
<li>バックを取られたらすぐに顎を折り込む</li>
<li>両手でチョーキングの前腕を掴む</li>
<li>チョークが完成しないように引き下げる</li>
</ul>

<div class="tip-box">
<strong>エスケープの黄金律：</strong> 常に早くエスケープする。悪いポジションで待てば待つほど、疲れてエスケープが難しくなります。危険が来るのを感じたらすぐに動きましょう。
</div>
"""
        },
        "pt": {
            "title": "Masterclass de Escapes no BJJ: Sobreviva em Qualquer Posição | BJJ Wiki",
            "h1": "Masterclass de Escapes no BJJ",
            "desc": "Domine os escapes do BJJ de todas as posições principais: controle lateral, montada, costas e joelho no barriga. Aprenda mecânicas, timing e combinações que tornam os escapes confiáveis.",
            "category": "Defesa",
            "belt": "Faixa Branca+",
            "body": """
<p>No BJJ, a capacidade de escapar de posições ruins é tão importante quanto a capacidade de atacar. Mesmo os melhores competidores ficam presos em posições inferiores — o que os separa é a capacidade de se recuperar sistematicamente.</p>

<h2>Escapes do Controle Lateral</h2>
<p>O controle lateral é a posição dominante mais comum encontrada no BJJ. Os escapes requerem framing, criar espaço e alavancar o poder dos quadris.</p>
<h3>Escape de Cotovelo-Joelho</h3>
<ul>
<li>Enquadre seu cotovelo próximo no quadril do oponente, mão distante enquadra o pescoço deles</li>
<li>Ponte e camarão simultaneamente para criar espaço</li>
<li>Traga seu joelho distante ao espaço do cotovelo</li>
<li>Puxe o outro joelho para recuperar a guarda</li>
</ul>

<h2>Escapes da Montada</h2>
<p>Os escapes da montada devem ser iniciados cedo — esperar até que o oponente tenha estabelecido montada completa torna o escape muito mais difícil.</p>
<h3>Armadilha e Rolamento (Upa)</h3>
<ul>
<li>Prenda o braço e a perna do mesmo lado do oponente</li>
<li>Plante seu pé e faça uma ponte explosiva</li>
<li>Role-os para terminar na guarda deles</li>
</ul>

<h2>Escapes de Costas</h2>
<p>Os escapes de costas são os mais difíceis — o atacante tem controle e visibilidade enquanto você não pode vê-los diretamente.</p>
<h3>Defesa de Queixo Abaixado</h3>
<ul>
<li>Imediatamente abaixe o queixo quando as costas forem capturadas</li>
<li>Agarre o antebraço que estrangula com ambas as mãos</li>
<li>Puxe para baixo para impedir que o estrangulamento complete</li>
</ul>

<div class="tip-box">
<strong>A Regra de Ouro dos Escapes:</strong> Sempre escape cedo. Quanto mais você espera em uma posição ruim, mais cansado você fica e mais difícil fica o escape.
</div>
"""
        }
    },
    {
        "slug": "bjj-competition-rules-complete",
        "en": {
            "title": "BJJ Competition Rules: IBJJF, ADCC & More | BJJ Wiki",
            "h1": "BJJ Competition Rules: Complete Guide",
            "desc": "A complete guide to BJJ competition rules covering IBJJF, ADCC, FloGrappling events, submission-only formats, and the key differences between major rulesets.",
            "category": "Competition",
            "belt": "White Belt+",
            "body": """
<p>Understanding BJJ competition rules is essential for anyone who trains with competition in mind. Different organizations use vastly different rulesets, and misunderstanding the rules can cost you matches that you should have won.</p>

<h2>IBJJF Rules Overview</h2>
<p>The International Brazilian Jiu-Jitsu Federation (IBJJF) uses the most widely-recognized ruleset in gi BJJ competition.</p>
<h3>Point System</h3>
<ul>
<li><strong>Takedown:</strong> 2 points (must control for 3 seconds)</li>
<li><strong>Sweep:</strong> 2 points (must control for 3 seconds)</li>
<li><strong>Knee on belly:</strong> 2 points (must control for 3 seconds)</li>
<li><strong>Guard pass:</strong> 3 points (must control for 3 seconds)</li>
<li><strong>Mount:</strong> 4 points (must control for 3 seconds)</li>
<li><strong>Back control (with hooks):</strong> 4 points (must control for 3 seconds)</li>
</ul>
<h3>Advantages</h3>
<p>Advantages are awarded for near-submissions and near-scoring positions. They serve as tiebreakers when scores are equal.</p>
<h3>Illegal Techniques by Belt Level</h3>
<ul>
<li><strong>White/Blue:</strong> No reaping, no heel hooks, no knee locks, no cervical locks</li>
<li><strong>Purple:</strong> Straight knee locks allowed, still no heel hooks or reaping</li>
<li><strong>Brown/Black:</strong> Heel hooks allowed in no-gi, all inside heel hooks allowed</li>
</ul>

<h2>ADCC Rules</h2>
<p>ADCC (Abu Dhabi Combat Club) is the premier no-gi submission wrestling competition. The ruleset is very different from IBJJF.</p>
<h3>ADCC Point System</h3>
<ul>
<li>No points in the first half of the match (time varies by division)</li>
<li>Negative points for pulling guard in the second half</li>
<li>Guard pass: 2 points</li>
<li>Takedown: 2 points</li>
<li>Knee on belly: 2 points</li>
<li>Mount/Back: 3 points</li>
</ul>
<h3>ADCC Technique Legality</h3>
<ul>
<li>All leg locks allowed including heel hooks and reaping</li>
<li>No points for takedown followed immediately by guard pull</li>
<li>Overtime: first submission or first 5 points wins</li>
</ul>

<h2>Submission-Only Formats</h2>
<p>Submission-only (SO) events have grown massively in popularity due to their exciting nature.</p>
<h3>Common SO Rules</h3>
<ul>
<li>No point system — win only by submission</li>
<li>Overtime: usually starts from a specific position (referee's position)</li>
<li>Many SO events allow all leg locks including heel hooks</li>
<li>EBI (Eddie Bravo Invitational) overtime: attacker starts from back take or leg lock</li>
</ul>

<h2>FloGrappling Rules</h2>
<p>FloGrappling hosts many high-profile events with varying rulesets. Events like Who's Number One (WNO) and FloGrappling's Grand Prix use a combination of submission hunting with points available.</p>

<h2>Stalling and Passivity Rules</h2>
<p>Most rulesets penalize stalling — the referee will warn the staller and may award the opponent an advantage or point.</p>
<ul>
<li>IBJJF: Medical clock for bleeding, warnings then DQ for stalling</li>
<li>ADCC: Referee cautions, then penalties for passivity</li>
<li>SO: Usually no stalling rules — must try to submit or advance</li>
</ul>

<h2>Competition Categories</h2>
<p>BJJ tournaments categorize competitors by age, belt, and weight:</p>
<ul>
<li><strong>Adult:</strong> Under 29 years old</li>
<li><strong>Master 1+:</strong> 30 years and older, with sub-divisions</li>
<li><strong>Weight classes:</strong> Vary by organization (IBJJF has 9 male weight classes)</li>
<li><strong>Absolute:</strong> Open weight division, no weight limit</li>
</ul>

<div class="tip-box">
<strong>Competitor Tip:</strong> Always read the specific ruleset for any event you enter. Don't assume all tournaments use the same rules — differences in leg lock legality alone have resulted in many DQs at major events.
</div>

<h2>Match Preparation by Ruleset</h2>
<ul>
<li><strong>IBJJF:</strong> Train guard pulls, improve guard game, understand points timing</li>
<li><strong>ADCC:</strong> Train wrestling and takedowns (guard pull penalized in 2nd half)</li>
<li><strong>Submission-only:</strong> Train from bad positions, deep in submissions, overtime scenarios</li>
</ul>
"""
        },
        "ja": {
            "title": "BJJ競技ルール完全ガイド：IBJJF、ADCC他 | BJJ Wiki",
            "h1": "BJJ競技ルール完全ガイド",
            "desc": "IBJJF、ADCC、FloGrapplingイベント、サブミッションオンリーフォーマットをカバーするBJJ競技ルールの完全ガイド。主要なルールセットの主な違いも解説。",
            "category": "競技",
            "belt": "白帯以上",
            "body": """
<p>BJJの競技ルールを理解することは、競技を意識してトレーニングする人にとって不可欠です。組織によってルールセットが大きく異なるため、ルールの誤解が勝てるはずの試合に負ける原因になることがあります。</p>

<h2>IBJJF ルール概要</h2>
<p>国際ブラジリアン柔術連盟（IBJJF）は、ギBJJ競技で最も広く認知されているルールセットを使用しています。</p>
<h3>ポイントシステム</h3>
<ul>
<li><strong>テイクダウン：</strong> 2点（3秒間コントロールが必要）</li>
<li><strong>スウィープ：</strong> 2点（3秒間コントロールが必要）</li>
<li><strong>ニー・オン・ベリー：</strong> 2点（3秒間コントロールが必要）</li>
<li><strong>ガードパス：</strong> 3点（3秒間コントロールが必要）</li>
<li><strong>マウント：</strong> 4点（3秒間コントロールが必要）</li>
<li><strong>バックコントロール（フック有り）：</strong> 4点（3秒間コントロールが必要）</li>
</ul>
<h3>帯レベル別違反技術</h3>
<ul>
<li><strong>白/青帯：</strong> リーピング禁止、ヒールフック禁止、ニーロック禁止、頸椎ロック禁止</li>
<li><strong>紫帯：</strong> ストレートニーロック可、ヒールフックとリーピングはまだ禁止</li>
<li><strong>茶/黒帯：</strong> ノーギでヒールフック可、インサイドヒールフック全て可</li>
</ul>

<h2>ADCC ルール</h2>
<p>ADCC（アブダビ・コンバット・クラブ）はプレミアノーギサブミッションレスリング競技です。ルールセットはIBJJFと大きく異なります。</p>
<h3>ADCCポイントシステム</h3>
<ul>
<li>試合の前半ではポイントなし</li>
<li>後半でのガードプルはマイナスポイント</li>
<li>ガードパス：2点、テイクダウン：2点</li>
<li>マウント/バック：3点</li>
</ul>

<h2>サブミッションオンリーフォーマット</h2>
<p>サブミッションオンリー（SO）イベントは、そのエキサイティングな性質から大きく人気が高まっています。</p>
<ul>
<li>ポイントシステムなし — サブミッションによる勝利のみ</li>
<li>延長戦：通常は特定のポジションから開始</li>
<li>多くのSOイベントはヒールフックを含む全てのレッグロックを許可</li>
</ul>

<h2>競技カテゴリ</h2>
<p>BJJトーナメントは競技者を年齢、帯、体重によってカテゴライズします：</p>
<ul>
<li><strong>アダルト：</strong> 29歳以下</li>
<li><strong>マスター1以上：</strong> 30歳以上、サブ区分あり</li>
<li><strong>体重クラス：</strong> 組織によって異なる</li>
<li><strong>アブソリュート：</strong> 無差別級</li>
</ul>

<div class="tip-box">
<strong>競技者のヒント：</strong> 参加するイベントの特定のルールセットを必ず読んでください。すべてのトーナメントが同じルールを使用すると仮定しないこと。
</div>
"""
        },
        "pt": {
            "title": "Regras de Competição de BJJ: IBJJF, ADCC e Mais | BJJ Wiki",
            "h1": "Guia Completo de Regras de Competição de BJJ",
            "desc": "Um guia completo sobre as regras de competição de BJJ cobrindo IBJJF, ADCC, eventos FloGrappling, formatos submission-only e as principais diferenças entre os conjuntos de regras.",
            "category": "Competição",
            "belt": "Faixa Branca+",
            "body": """
<p>Entender as regras de competição do BJJ é essencial para qualquer pessoa que treina com a competição em mente. Diferentes organizações usam conjuntos de regras vastamente diferentes.</p>

<h2>Visão Geral das Regras IBJJF</h2>
<p>A Federação Internacional de Brazilian Jiu-Jitsu (IBJJF) usa o conjunto de regras mais amplamente reconhecido na competição de BJJ com kimono.</p>
<h3>Sistema de Pontos</h3>
<ul>
<li><strong>Derrubada:</strong> 2 pontos (deve controlar por 3 segundos)</li>
<li><strong>Raspagem:</strong> 2 pontos (deve controlar por 3 segundos)</li>
<li><strong>Joelho no barriga:</strong> 2 pontos</li>
<li><strong>Passagem de guarda:</strong> 3 pontos</li>
<li><strong>Montada:</strong> 4 pontos</li>
<li><strong>Controle de costas (com ganchos):</strong> 4 pontos</li>
</ul>
<h3>Técnicas Ilegais por Nível de Faixa</h3>
<ul>
<li><strong>Branca/Azul:</strong> Sem falcata, sem footlock de calcanhar, sem locks de joelho</li>
<li><strong>Roxa:</strong> Locks retos de joelho permitidos, ainda sem footlocks de calcanhar</li>
<li><strong>Marrom/Preta:</strong> Footlocks de calcanhar permitidos no no-gi</li>
</ul>

<h2>Regras ADCC</h2>
<p>O ADCC é a principal competição de wrestling submission sem kimono.</p>
<h3>Sistema de Pontos ADCC</h3>
<ul>
<li>Sem pontos na primeira metade da luta</li>
<li>Pontos negativos por puxar guarda na segunda metade</li>
<li>Passagem de guarda: 2 pontos</li>
<li>Montada/Costas: 3 pontos</li>
</ul>

<h2>Formatos Submission-Only</h2>
<ul>
<li>Sem sistema de pontos — ganhe apenas por submissão</li>
<li>Muitos eventos SO permitem todos os leg locks incluindo footlocks de calcanhar</li>
</ul>

<div class="tip-box">
<strong>Dica para Competidores:</strong> Sempre leia o conjunto de regras específico para qualquer evento que você entrar. Não assuma que todos os torneios usam as mesmas regras.
</div>
"""
        }
    }
]

SITE_URL = "https://t307239.github.io/bjj-wiki"


def build_hreflang(slug):
    return f"""  <link rel="alternate" hreflang="en" href="{SITE_URL}/en/{slug}.html">
  <link rel="alternate" hreflang="ja" href="{SITE_URL}/ja/{slug}.html">
  <link rel="alternate" hreflang="pt" href="{SITE_URL}/pt/{slug}.html">
  <link rel="alternate" hreflang="x-default" href="{SITE_URL}/en/{slug}.html">"""


def build_page(slug, lang, data, hreflang):
    lang_attr = {"en": "en", "ja": "ja", "pt": "pt-BR"}[lang]
    title = data["title"]
    desc = data["desc"]
    h1 = data["h1"]
    category = data["category"]
    belt = data["belt"]
    body = data["body"]

    share_label = {"en": "Share on 𝕏", "ja": "𝕏 シェア", "pt": "Compartilhar no 𝕏"}[lang]
    home_label = {"en": "Home", "ja": "ホーム", "pt": "Início"}[lang]
    related_label = {"en": "Related Topics", "ja": "関連トピック", "pt": "Tópicos Relacionados"}[lang]

    html = f"""<!DOCTYPE html>
<html lang="{lang_attr}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{SITE_URL}/{lang}/{slug}.html">
{hreflang}
  <link rel="preconnect" href="https://pagead2.googlesyndication.com" crossorigin>
  <link rel="dns-prefetch" href="https://www.googletagmanager.com">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-7LM8L3TRZM"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-7LM8L3TRZM');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5529701443220352" crossorigin="anonymous"></script>
  <style>
    :root{{--bg:#0a0f1e;--card:#111827;--accent:#e2b714;--text:#e5e7eb;--muted:#9ca3af}}
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',sans-serif;line-height:1.7}}
    header{{background:linear-gradient(135deg,#0f1a2e,#1a1040);padding:20px;text-align:center;border-bottom:2px solid var(--accent)}}
    header h1{{color:var(--accent);font-size:1.8rem;margin-bottom:6px}}
    header p{{color:var(--muted);font-size:.95rem}}
    nav{{background:#111827;padding:10px 20px;display:flex;gap:12px;flex-wrap:wrap;justify-content:center;font-size:.85rem}}
    nav a{{color:var(--muted);text-decoration:none}}nav a:hover{{color:var(--accent)}}
    .container{{max-width:860px;margin:0 auto;padding:24px 16px}}
    h2{{color:var(--accent);margin:28px 0 12px;font-size:1.25rem}}
    h3{{color:#93c5fd;margin:20px 0 8px;font-size:1.05rem}}
    p{{color:var(--text);margin-bottom:12px}}
    ul,ol{{padding-left:20px;margin-bottom:14px}}
    li{{margin-bottom:6px;color:var(--text)}}
    table{{width:100%;border-collapse:collapse;margin:20px 0}}
    th{{background:#1e2a3a;color:var(--accent);padding:10px;text-align:left;font-size:.9rem}}
    td{{padding:10px;border-bottom:1px solid #1e2a3a;font-size:.9rem;color:var(--text)}}
    .tip-box{{background:#0d2d0d;border-left:4px solid #4ade80;border-radius:8px;padding:14px 18px;margin:20px 0}}
    .tip-box strong{{color:#4ade80}}
    .warn-box{{background:#2d1a0d;border-left:4px solid #fb923c;border-radius:8px;padding:14px 18px;margin:20px 0}}
    .warn-box strong{{color:#fb923c}}
    .badge{{display:inline-block;padding:3px 10px;border-radius:20px;font-size:.78rem;font-weight:600;margin:0 4px 4px 0}}
    .badge-cat{{background:#1e3a5f;color:#93c5fd}}
    .badge-belt{{background:#3d2a00;color:#e2b714}}
    .share-bar{{margin:24px 0;display:flex;gap:10px;flex-wrap:wrap}}
    .share-btn{{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;border-radius:8px;text-decoration:none;font-size:.85rem;font-weight:600}}
    .share-x{{background:#111;color:#fff;border:1px solid #333}}
    .app-cta{{background:linear-gradient(135deg,#0f1a2e,#1a1040);border:1px solid var(--accent);border-radius:12px;padding:20px;margin:28px 0;text-align:center}}
    .app-cta h3{{color:var(--accent);margin-bottom:8px}}
    .app-cta p{{color:var(--muted);font-size:.9rem;margin-bottom:14px}}
    .app-cta a{{display:inline-block;background:linear-gradient(135deg,#7c3aed,#2563eb);color:#fff;padding:10px 24px;border-radius:10px;text-decoration:none;font-weight:700;font-size:.9rem}}
    footer{{background:#060d1a;text-align:center;padding:28px;color:var(--muted);font-size:.8rem;margin-top:40px}}
    footer a{{color:var(--muted);text-decoration:none}}
  </style>
</head>
<body>
<header>
  <h1>{h1}</h1>
  <p>
    <span class="badge badge-cat">{category}</span>
    <span class="badge badge-belt">{belt}</span>
  </p>
</header>
<nav>
  <a href="../index.html">{home_label}</a>
  <a href="../{lang}/index.html">BJJ Wiki</a>
</nav>
<main class="container">
{body}

  <div class="share-bar">
    <a class="share-btn share-x" href="https://twitter.com/intent/tweet?text={h1}&url={SITE_URL}/{lang}/{slug}.html&hashtags=BJJ,BrazilianJiuJitsu" target="_blank" rel="noopener">{share_label}</a>
  </div>

  <div class="app-cta">
    <h3>🥋 Track Your BJJ Progress</h3>
    <p>Log sessions, track techniques, and measure your growth with BJJ App — free for all practitioners.</p>
    <a href="https://bjj-app-one.vercel.app" target="_blank" rel="noopener">Try BJJ App Free →</a>
  </div>
</main>
<footer>
  <p>© 2026 BJJ Wiki — <a href="../en/about.html">About</a> · <a href="../en/privacy.html">Privacy</a> · <a href="../feed.xml">RSS</a></p>
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
    for slug in new_slugs:
        for lang in ["en", "ja", "pt"]:
            url = f"{SITE_URL}/{lang}/{slug}.html"
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
        added = new_entries.count("<url>")
        return added
    return 0


def add_index_cards(new_slugs, pages_data):
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

    added = update_sitemap(new_slugs)
    print(f"\nSitemap: +{added} URLs added")

    add_index_cards(new_slugs, PAGES)
    print(f"Index cards updated for {len(new_slugs)} pages")

    print(f"\nTotal pages generated: {generated}")
    print("Batch 392-396 complete ✅")


if __name__ == "__main__":
    main()
