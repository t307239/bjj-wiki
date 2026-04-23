#!/usr/bin/env python3
"""
BJJ Wiki Batch 377-381 Generation
Static content generation without Gemini API
Themes:
- bjj-attacking-from-turtle-advanced
- bjj-conditioning-science
- bjj-guard-setups-masterclass
- bjj-back-control-finishing-details
- bjj-sweeps-to-submissions
"""

import os
import re
import json
from datetime import datetime

WIKI_DIR = "/sessions/keen-sharp-davinci/mnt/bjj-wiki"

# Batch 377-381 themes with static content
BATCH_DATA = {
    "bjj-attacking-from-turtle-advanced": {
        "en": {
            "title": "Attacking from Turtle Position - Advanced System",
            "description": "Master advanced turtle position attacks including back takes, submissions, and transitions.",
            "content": """
<h2>Advanced Turtle Position Attacks</h2>
<p>Turtle position provides unique opportunities for top player attacks. This comprehensive guide covers back takes, submissions, and advanced transitions from turtle control.</p>

<h3>Back Take Fundamentals</h3>
<p>The most valuable attack from turtle position. Establish strong seat belt control before attempting the back take. Key details: hook placement, base stability, and timing.</p>

<h3>Direct Turtle Submissions</h3>
<p>Chokes and locks available directly from turtle position without transitions. Darce choke from turtle top, neck cranks, and arm submissions.</p>

<h3>Arm Triangle from Turtle</h3>
<p>Position your body to lock the arm triangle with the turtle defender's own arm. Common mistake: attempting too early before securing control.</p>

<h3>Transitioning Between Attacks</h3>
<p>Chain attacks together: back take leads to choke, failed back take switches to arm triangle. Understanding these transitions maximizes pressure.</p>

<h3>Common Defenses and Counters</h3>
<p>Turtle players often bridge explosively. Anticipate this movement and adjust your base. Establish underhook control to prevent explosive escapes.</p>
"""
        },
        "ja": {
            "title": "タートルポジション - アドバンスド攻撃システム",
            "description": "タートルポジションからの高度な攻撃技術。バックテイク、サブミッション、トランジションを習得。",
            "content": """
<h2>タートルポジション アドバンスド攻撃</h2>
<p>タートルポジション（カメ型防御）は上からの攻撃に多くの機会を提供します。バックテイク、サブミッション、トランジションを網羅した完全ガイド。</p>

<h3>バックテイク基礎</h3>
<p>タートルポジションで最も価値の高い攻撃。シートベルトコントロール（両手で相手の腕を控制）を確立することが重要。フック配置、ベース安定性、タイミング。</p>

<h3>ダイレクトタートルサブミッション</h3>
<p>トランジションなしにタートルポジションから直接可能なチョーク・ロック。ダースチョーク、ネッククランク、アームサブミッション。</p>

<h3>アームトライアングル・フロム・タートル</h3>
<p>相手自身の腕を使ってアームトライアングルをロック。よくある間違い：コントロールを十分に確立する前に実行すること。</p>

<h3>攻撃のチェーン</h3>
<p>複数の攻撃をつなげる：バックテイクがチョークに繋がる。失敗したバックテイクはアームトライアングルに切り替える。</p>

<h3>一般的な防御とカウンター</h3>
<p>タートル防御者は爆発的なブリッジで逃げることが多い。このムーブメントを予測しベースを調整。アンダーフック制御で爆発的逃げを防止。</p>
"""
        },
        "pt": {
            "title": "Ataques da Posição Tartaruga - Sistema Avançado",
            "description": "Domine ataques avançados da posição tartaruga incluindo costas, submissões e transições.",
            "content": """
<h2>Ataques Avançados da Posição Tartaruga</h2>
<p>A posição tartaruga oferece oportunidades únicas de ataque para o jogador de cima. Guia completo cobrindo costas, submissões e transições avançadas.</p>

<h3>Fundamentos da Tomada de Costas</h3>
<p>O ataque mais valioso da posição tartaruga. Estabeleça forte controle de cinto de segurança antes de tentar a tomada de costas. Detalhes principais: colocação dos hooks, estabilidade da base e timing.</p>

<h3>Submissões Diretas da Tartaruga</h3>
<p>Estrangulamentos e chaves disponíveis diretamente da posição tartaruga sem transições. Darce choke, cranks de pescoço e submissões de braço.</p>

<h3>Triângulo de Braço da Tartaruga</h3>
<p>Posicione seu corpo para travar o triângulo de braço com o próprio braço do defensor. Erro comum: tentar muito cedo antes de garantir controle.</p>

<h3>Transição Entre Ataques</h3>
<p>Encadeie ataques: tomada de costas leva a estrangulamento, falha na tomada de costas muda para triângulo de braço. Compreender essas transições maximiza a pressão.</p>

<h3>Defesas Comuns e Contra-ataques</h3>
<p>Jogadores na tartaruga frequentemente fazem bridges explosivos. Antecipe este movimento e ajuste sua base. Estabeleça controle de underhook para prevenir fugas explosivas.</p>
"""
        }
    },
    "bjj-conditioning-science": {
        "en": {
            "title": "Conditioning Science for BJJ - Evidence-Based Training",
            "description": "Scientific approach to BJJ conditioning including energy systems, work-to-rest ratios, and periodization.",
            "content": """
<h2>BJJ Conditioning Science</h2>
<p>Brazilian Jiu-Jitsu demands unique conditioning demands different from traditional cardio. This evidence-based guide covers energy systems, training variables, and adaptation.</p>

<h3>Energy Systems in BJJ</h3>
<p>Three energy systems power BJJ: ATP-PC (0-10 sec), Anaerobic lactate (10 sec - 3 min), Aerobic (3+ min). Most BJJ matches utilize all three systems.</p>

<h3>Work-to-Rest Ratios</h3>
<p>Training intensity should match match demands. High-intensity intervals with strategic rest periods develop match-specific conditioning. Research shows 1:1 to 1:2 work-to-rest ratios optimize BJJ adaptation.</p>

<h3>Periodization for BJJ</h3>
<p>Structured periodization prevents overtraining and peaks performance for competitions. Macrocycles (yearly), mesocycles (4-6 weeks), and microcycles (1 week) provide organized progression.</p>

<h3>Specific Conditioning Methods</h3>
<p>Gi grip strength endurance, explosive leg power, and sport-specific movements should comprise conditioning program. General fitness alone inadequate for competition BJJ.</p>

<h3>Recovery and Adaptation</h3>
<p>Conditioning adaptations occur during recovery, not during training. Sleep, nutrition, and stress management directly impact conditioning effectiveness.</p>
"""
        },
        "ja": {
            "title": "BJJ コンディショニング科学 - エビデンスベース",
            "description": "エネルギーシステム、ワークレスト比、ピリオダイゼーションを含むBJJコンディショニング科学。",
            "content": """
<h2>BJJコンディショニング科学</h2>
<p>ブラジリアン柔術は伝統的な有酸素運動と異なるユニークなコンディショニングが必要です。エネルギーシステム、トレーニング変数、適応をカバーした証拠ベースのガイド。</p>

<h3>BJJのエネルギーシステム</h3>
<p>3つのエネルギーシステムがBJJを駆動：ATP-PC（0-10秒）、無酸素乳酸（10秒-3分）、有酸素（3分以上）。ほとんどのBJJマッチは全3システムを使用。</p>

<h3>ワークレスト比</h3>
<p>トレーニング強度はマッチ要求にマッチすべき。戦略的な休止を伴う高強度インターバルはマッチ固有のコンディショニングを開発。研究は1:1から1:2のワークレスト比がBJJ適応を最適化することを示唆。</p>

<h3>BJJのためのピリオダイゼーション</h3>
<p>構造化ピリオダイゼーションはオーバートレーニングを防ぎ競技パフォーマンスをピーク化。マクロサイクル（年間）、メソサイクル（4-6週間）、ミクロサイクル（1週間）は組織的な進行を提供。</p>

<h3>特定コンディショニング方法</h3>
<p>道衣グリップ筋力持久力、爆発的な脚力、スポーツ特異的なムーブメントはコンディショニングプログラムを構成すべき。一般的なフィットネスだけは競技BJJには不十分。</p>

<h3>回復と適応</h3>
<p>コンディショニング適応はトレーニング中ではなく回復中に発生。睡眠、栄養、ストレス管理はコンディショニング効果に直接影響。</p>
"""
        },
        "pt": {
            "title": "Ciência do Condicionamento para JJB - Baseado em Evidências",
            "description": "Abordagem científica ao condicionamento do JJB incluindo sistemas de energia, relações trabalho-repouso e periodização.",
            "content": """
<h2>Ciência do Condicionamento para JJB</h2>
<p>O Jiu-Jitsu Brasileiro demanda demandas de condicionamento únicas diferentes do cardio tradicional. Este guia baseado em evidências cobre sistemas de energia, variáveis de treinamento e adaptação.</p>

<h3>Sistemas de Energia no JJB</h3>
<p>Três sistemas de energia alimentam o JJB: ATP-PC (0-10 seg), lactato anaeróbico (10 seg - 3 min), aeróbico (3+ min). A maioria das lutas de JJB utiliza todos os três sistemas.</p>

<h3>Relações Trabalho-Repouso</h3>
<p>A intensidade do treinamento deve corresponder às demandas da luta. Intervalos de alta intensidade com períodos de repouso estratégicos desenvolvem condicionamento específico da luta. Pesquisas mostram que relações trabalho-repouso de 1:1 a 1:2 otimizam a adaptação ao JJB.</p>

<h3>Periodização para JJB</h3>
<p>Periodização estruturada previne overtraining e otimiza o desempenho em competições. Macrociclos (anuais), mesociclos (4-6 semanas) e microciclos (1 semana) fornecem progressão organizada.</p>

<h3>Métodos Específicos de Condicionamento</h3>
<p>Resistência de força de preensão em kimono, poder de perna explosivo e movimentos específicos do esporte devem compor o programa de condicionamento. Apenas aptidão geral é inadequada para JJB de competição.</p>

<h3>Recuperação e Adaptação</h3>
<p>As adaptações de condicionamento ocorrem durante a recuperação, não durante o treinamento. Sono, nutrição e gerenciamento de estresse impactam diretamente a eficácia do condicionamento.</p>
"""
        }
    },
    "bjj-guard-setups-masterclass": {
        "en": {
            "title": "Guard Setups Masterclass - Complete Systems",
            "description": "Comprehensive guide to establishing and maintaining superior guard positions including transitions and setups.",
            "content": """
<h2>Guard Setups Masterclass</h2>
<p>Strong guard begins with proper setup and entry. This masterclass covers systematic approaches to establishing guard positions from various starting points.</p>

<h3>Collar-Sleeve Setup</h3>
<p>One of the most common guard setups. Grip stability on collar and sleeve determines control quality. Balance control crucial to prevent guard break.</p>

<h3>Lasso Guard Entry</h3>
<p>Wrap the leg around opponent's arm to create positional control. Timing and leg placement prevent simple leglock defenses. Essential detail: maintain high hip control.</p>

<h3>Spider Guard Fundamentals</h3>
<p>Feet on both sleeves provide exceptional control and sweep opportunities. Maintain proper distance and foot pressure throughout position.</p>

<h3>De La Riva Guard Setup</h3>
<p>Underhook under far leg creates unique leverage. Sensitive position requiring precise footwork and hand positioning for success.</p>

<h3>Transitioning Between Guards</h3>
<p>Skilled guards transition seamlessly between positions based on opponent's reactions. Understand common guard break attempts and appropriate transitions.</p>

<h3>Guard Retention from Standing</h3>
<p>Preventing guard break before guard is fully established. Hand position, hip movement, and foot placement prevent early sweeps and passes.</p>
"""
        },
        "ja": {
            "title": "ガードセットアップ マスタークラス",
            "description": "ガードセットアップの完全な体系。トランジション、リカバリ、防御を含む。",
            "content": """
<h2>ガードセットアップ マスタークラス</h2>
<p>強いガードは適切なセットアップとエントリーから始まります。様々なスタートポイントからガードポジションを確立するための体系的アプローチを網羅。</p>

<h3>襟スリーブガード セットアップ</h3>
<p>最も一般的なガードセットアップの1つ。襟とスリーブの握り安定性がコントロール品質を決定。バランスコントロールはガードブレイク防止に重要。</p>

<h3>ラッソガード エントリー</h3>
<p>相手の腕に脚を巻き付けてポジショナルコントロールを作成。タイミングと脚配置はシンプルなレッグロック防御を防ぐ。本質的な詳細：高いヒップコントロールを維持。</p>

<h3>スパイダーガード基礎</h3>
<p>両スリーブに足を置くことで例外的なコントロールとスウィープ機会を提供。ポジション全体にわたってそれぞれの距離と足圧力を維持。</p>

<h3>デラヒーバガード セットアップ</h3>
<p>遠い脚の下のアンダーフックはユニークなレバレッジを作成。成功のために正確なフットワークと手配置が必要な繊細なポジション。</p>

<h3>ガード間のトランジション</h3>
<p>熟練したガード選手は相手のリアクションに基づいてポジション間をシームレスに移行。一般的なガードブレイク試みと適切なトランジションを理解。</p>

<h3>スタンディングからのガードリテンション</h3>
<p>ガードが完全に確立される前にガードブレイクを防ぐ。ハンドポジション、ヒップムーブメント、フットプレースメントは早期スウィープとパスを防ぐ。</p>
"""
        },
        "pt": {
            "title": "Guarda Setups Masterclass - Sistemas Completos",
            "description": "Guia completo para estabelecer e manter posições superiores de guarda incluindo transições e setups.",
            "content": """
<h2>Guarda Setups Masterclass</h2>
<p>Guarda forte começa com configuração e entrada adequadas. Este masterclass cobre abordagens sistemáticas para estabelecer posições de guarda de vários pontos de partida.</p>

<h3>Setup de Guarda Gola-Manga</h3>
<p>Um dos setups de guarda mais comuns. Estabilidade de grip na gola e manga determina qualidade de controle. Controle de equilíbrio crucial para prevenir quebra de guarda.</p>

<h3>Entrada de Guarda Lasso</h3>
<p>Enrole a perna ao redor do braço do oponente para criar controle posicional. Timing e colocação de perna previnem defesas simples de leg lock. Detalhe essencial: manter controle alto de quadril.</p>

<h3>Fundamentos de Guarda Aranha</h3>
<p>Pés em ambas as mangas oferecem controle excepcional e oportunidades de varredura. Mantenha distância adequada e pressão de pé em toda a posição.</p>

<h3>Setup de Guarda De La Riva</h3>
<p>Underhook sob perna distante cria alavancagem única. Posição sensível exigindo footwork preciso e posicionamento de mão para sucesso.</p>

<h3>Transitando Entre Guardas</h3>
<p>Guardas hábeis fazem transição perfeita entre posições baseadas nas reações do oponente. Entenda tentativas comuns de quebra de guarda e transições apropriadas.</p>

<h3>Guarda Retention em Pé</h3>
<p>Prevenindo quebra de guarda antes de guarda estar totalmente estabelecida. Posição de mão, movimento de quadril e colocação de pé previnem varreduras e passes iniciais.</p>
"""
        }
    },
    "bjj-back-control-finishing-details": {
        "en": {
            "title": "Back Control Finishing Details - Complete System",
            "description": "Detailed finishing positions and transitions from back control including all major submission variations.",
            "content": """
<h2>Back Control Finishing Details</h2>
<p>Back control provides the highest percentage position for submissions. This guide covers every detail of position maintenance and finishing sequences.</p>

<h3>Seat Belt Control Mastery</h3>
<p>Proper grip placement on ribs and under armpit determines control quality. Maintain constant pressure to prevent explosive escapes and prevent arm removal.</p>

<h3>Rear Naked Choke Mechanics</h3>
<p>Hand placement relative to neck determines choke effectiveness. Proper weight distribution and arm positioning maximizes choke efficiency and prevents defense.</p>

<h3>Bow and Arrow Choke System</h3>
<p>Utilize lapel and leg position to create powerful choke. Requires tight hip control and proper angle. Advanced details of pressure application.</p>

<h3>Arm-In Armlock Finishes</h3>
<p>Transition from back control to arm triangle or armbar. Proper sequencing prevents escape opportunities. Work on smooth transitions maintaining position.</p>

<h3>Multiple Finishing Chains</h3>
<p>Chain submissions together creating inescapable sequences. Opponent's defense against one technique naturally leads to the next submission.</p>

<h3>Back Escape Defense</h3>
<p>Prevent common back escape attempts. Maintain proper hook placement and prevent bridge positioning. Understanding escapes improves finishing defense.</p>
"""
        },
        "ja": {
            "title": "バックコントロール フィニッシング詳細",
            "description": "バックコントロールからのフィニッシングポジションと詳細。全主要サブミッション変種を網羅。",
            "content": """
<h2>バックコントロール フィニッシング詳細</h2>
<p>バックコントロールはサブミッション最高パーセンテージポジション。ポジション維持とフィニッシングシーケンス全詳細をカバー。</p>

<h3>シートベルトコントロール マスタリー</h3>
<p>肋骨と腋下への適切なグリップ配置はコントロール品質を決定。爆発的逃げを防ぐため常に圧力を維持し腕除去を防止。</p>

<h3>裸絞めメカニクス</h3>
<p>首の相対的なハンドプレースメントはチョーク効果を決定。適切な体重分配とアーム配置はチョーク効率を最大化し防御を防止。</p>

<h3>弓と矢のチョークシステム</h3>
<p>襟とレッグポジションを使用して強力なチョークを作成。タイトなヒップコントロールと適切な角度が必要。圧力応用の高度な詳細。</p>

<h3>腕イン アームロック フィニッシュ</h3>
<p>バックコントロールからアームトライアングルやアームバーにトランジション。適切なシーケンシングは逃げ機会を防ぐ。ポジション維持しながらスムーズなトランジションを練習。</p>

<h3>複数フィニッシングチェーン</h3>
<p>サブミッションを一緒にチェーンして逃げ不可能なシーケンスを作成。相手の1つのテクニックに対する防御は自然に次のサブミッションに導く。</p>

<h3>バックエスケープ防御</h3>
<p>一般的なバックエスケープ試みを防ぐ。適切なフック配置を維持しブリッジポジションを防止。エスケープ理解はフィニッシング防御を改善。</p>
"""
        },
        "pt": {
            "title": "Detalhes de Finalização do Controle de Costas",
            "description": "Posições de finalização detalhadas e transições do controle de costas incluindo todas as principais variações de submissão.",
            "content": """
<h2>Detalhes de Finalização do Controle de Costas</h2>
<p>O controle de costas fornece a posição com maior percentual para submissões. Este guia cobre todos os detalhes de manutenção de posição e sequências de finalização.</p>

<h3>Domínio de Controle de Cinto de Segurança</h3>
<p>O posicionamento adequado do grip nas costelas e sob a axila determina a qualidade do controle. Mantenha pressão constante para prevenir fugas explosivas e prevenir remoção de braço.</p>

<h3>Mecânica do Estrangulamento Nú</h3>
<p>O posicionamento da mão em relação ao pescoço determina a efetividade do estrangulamento. Distribuição adequada de peso e posicionamento de braço maximiza eficiência de estrangulamento e previne defesa.</p>

<h3>Sistema de Estrangulamento Arco e Flecha</h3>
<p>Utilize posição de gola e perna para criar estrangulamento poderoso. Requer controle apertado de quadril e ângulo apropriado. Detalhes avançados de aplicação de pressão.</p>

<h3>Finalizações de Armlock com Braço Dentro</h3>
<p>Transição do controle de costas para triângulo de braço ou armbar. O sequenciamento apropriado previne oportunidades de fuga. Trabalhe em transições suaves mantendo posição.</p>

<h3>Múltiplas Cadeias de Finalização</h3>
<p>Encadeie submissões juntas criando sequências inescapáveis. A defesa do oponente contra uma técnica naturalmente leva à próxima submissão.</p>

<h3>Defesa de Fuga de Costas</h3>
<p>Previna tentativas comuns de fuga de costas. Mantenha posicionamento adequado de hook e previna posicionamento de bridge. Compreensão de fugas melhora defesa de finalização.</p>
"""
        }
    },
    "bjj-sweeps-to-submissions": {
        "en": {
            "title": "Sweeps to Submissions - Transition Chains",
            "description": "Master the art of chaining sweeps directly into submissions for seamless offensive sequences.",
            "content": """
<h2>Sweeps to Submissions</h2>
<p>The highest percentage attacks chain sweeps directly into submissions. This system covers transitioning from sweep momentum into controlling submissions.</p>

<h3>Hip Bump Sweep to Triangle</h3>
<p>Execute hip bump sweep and immediately transition upper body into triangle choke position. Momentum from sweep provides entry angle for triangle. Guard their cross arm to prevent escape.</p>

<h3>Scissor Sweep to Armbar</h3>
<p>After scissor sweep topples opponent, secure armbar immediately. Use the same leg positioning for armbar that created the sweep. Smooth transition prevents them from establishing side control.</p>

<h3>Flower Sweep to Submissions</h3>
<p>Flower sweep creates angles for immediate submission attempts. Chain into triangle, armbar, or back take depending on their arm position. Master all three finishing options.</p>

<h3>De La Riva Sweep Finishes</h3>
<p>De La Riva sweep places opponent in vulnerable position. Immediately secure back control or transition to leg lock position. Timing is crucial - catch them before they recover base.</p>

<h3>Lasso Guard Sweep Combinations</h3>
<p>Lasso position allows multiple sweep angles. After sweep, transition into mounted position or back control. Practice smooth foot transitions maintaining control pressure.</p>

<h3>Collar Drag to Back Control</h3>
<p>Collar drag sweep naturally transitions to back control position. Maintain connection with lapel to prevent frame. Practice getting back hooks immediately after sweep.</p>
"""
        },
        "ja": {
            "title": "スウィープからサブミッションへ - トランジションチェーン",
            "description": "スウィープをサブミッションに直接チェーンするオフェンシブシーケンスをマスター。",
            "content": """
<h2>スウィープからサブミッションへ</h2>
<p>最高パーセンテージ攻撃はスウィープをサブミッションに直接チェーン。スウィープモーメンタムからコントロール・サブミッションへのトランジション。</p>

<h3>ヒップバンプスウィープ トゥ トライアングル</h3>
<p>ヒップバンプスウィープ実行後即座に上身をトライアングル位置にトランジション。スウィープのモーメンタムはトライアングルエントリー角を提供。クロスアームを防ぐため監視。</p>

<h3>シザーススウィープ トゥ アームバー</h3>
<p>シザーススウィープが相手を転がした後即座にアームバーをセキュア。アームバーのために相手を転がした同じ脚配置を使用。スムーズなトランジションはサイドコントロール確立を防ぐ。</p>

<h3>フラワースウィープ トゥ サブミッション</h3>
<p>フラワースウィープは即座のサブミッション試みのための角度を作成。トライアングル、アームバー、またはバックテイクにチェーン。全3フィニッシング選択肢をマスター。</p>

<h3>デラヒーバスウィープ フィニッシュ</h3>
<p>デラヒーバスウィープは相手を脆弱なポジションに配置。即座にバックコントロールをセキュアまたはレッグロックポジションにトランジション。回復前にキャッチすることが重要。</p>

<h3>ラッソガード スウィープ コンビネーション</h3>
<p>ラッソポジションは複数のスウィープ角度を可能にする。スウィープ後マウント位置またはバックコントロールにトランジション。スムーズなフットトランジション練習。</p>

<h3>襟ドラッグ トゥ バックコントロール</h3>
<p>襟ドラッグスウィープはバックコントロール位置に自然にトランジション。フレームを防ぐため襟と接続を維持。スウィープ直後にバックフックを即座にセキュア練習。</p>
"""
        },
        "pt": {
            "title": "Varridas para Submissões - Cadeias de Transição",
            "description": "Domine a arte de encadear varridas diretamente em submissões para sequências ofensivas perfeitas.",
            "content": """
<h2>Varridas para Submissões</h2>
<p>Os ataques de maior percentual encadeiam varridas diretamente em submissões. Este sistema cobre transição do momentum da varredura para submissões de controle.</p>

<h3>Varredura de Bump de Quadril para Triângulo</h3>
<p>Execute varredura de bump de quadril e transicione imediatamente a parte superior do corpo para posição de triângulo. O momentum da varredura fornece ângulo de entrada para triângulo. Guarde o braço cruzado para prevenir fuga.</p>

<h3>Varredura de Tesoura para Armbar</h3>
<p>Após varredura de tesoura derrubar oponente, segure armbar imediatamente. Use o mesmo posicionamento de perna para armbar que criou a varredura. Transição suave previne estabelecimento de side control.</p>

<h3>Varredura de Flor para Submissões</h3>
<p>Varredura de flor cria ângulos para tentativas imediatas de submissão. Encadeie em triângulo, armbar ou tomada de costas dependendo da posição do braço. Domine todas as três opções de finalização.</p>

<h3>Finalizações de Varredura De La Riva</h3>
<p>Varredura De La Riva coloca oponente em posição vulnerável. Segure controle de costas imediatamente ou transicione para posição de leg lock. Timing é crucial - pegue antes deles recuperarem base.</p>

<h3>Combinações de Varredura da Guarda Lasso</h3>
<p>Posição lasso permite múltiplos ângulos de varredura. Após varredura, transicione para posição montada ou controle de costas. Pratique transições suaves de pé mantendo pressão de controle.</p>

<h3>Arrastar Gola para Controle de Costas</h3>
<p>Varredura de arrastar gola transiciona naturalmente para posição de controle de costas. Mantenha conexão com gola para prevenir frame. Pratique obter back hooks imediatamente após varredura.</p>
"""
        }
    }
}

def generate_html(slug: str, lang: str, data: dict) -> str:
    """Generate HTML page from template"""
    title = data["title"]
    description = data["description"]
    content = data["content"]

    # Language-specific meta
    lang_names = {"en": "English", "ja": "日本語", "pt": "Português"}
    lang_name = lang_names.get(lang, "English")

    # Build alternates
    alternates = []
    for alt_lang in ["en", "ja", "pt"]:
        alt_url = f"https://wiki.bjj-app.net/{alt_lang}/{slug}.html"
        alternates.append(f'<link rel="alternate" hreflang="{alt_lang}" href="{alt_url}" />')

    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:url" content="https://wiki.bjj-app.net/{lang}/{slug}.html">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="BJJ Wiki">
    {chr(10).join(alternates)}
    <link rel="canonical" href="https://wiki.bjj-app.net/{lang}/{slug}.html">
    <link rel="icon" type="image/png" href="../../favicon.ico">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        h2 {{ color: #2c5282; margin-top: 30px; }}
        h3 {{ color: #2d3748; margin-top: 20px; }}
        p {{ margin: 10px 0; }}
        a {{ color: #2d3748; text-decoration: underline; }}
        .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .meta {{ color: #666; font-size: 14px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="meta">{lang_name} | {slug}</div>
        <h1>{title}</h1>
        <p><em>{description}</em></p>
        {content}
        <hr style="margin-top: 30px; margin-bottom: 20px;">
        <p style="font-size: 12px; color: #999;">
            <a href="../index.html">← Back to BJJ Wiki</a>
        </p>
    </div>
</body>
</html>"""
    return html

def main():
    total_created = 0

    for slug, translations in BATCH_DATA.items():
        for lang, data in translations.items():
            lang_dir = os.path.join(WIKI_DIR, lang)
            os.makedirs(lang_dir, exist_ok=True)

            filepath = os.path.join(lang_dir, f"{slug}.html")
            html = generate_html(slug, lang, data)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

            total_created += 1
            print(f"✅ {lang}/{slug}.html")

    print(f"\n✅ Batch 377-381 complete: {total_created} pages generated")

if __name__ == '__main__':
    main()
