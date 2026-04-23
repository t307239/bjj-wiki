#!/usr/bin/env python3
"""
Batch 377-381: 5 themes × 3 languages = 15 pages
- Attacking from turtle (top/bottom turtle attacks, granby roll systems)
- BJJ conditioning science (energy systems, strength training, HRV, periodization)
- Guard setups masterclass (entries into closed/half/butterfly/DLR/spider guard)
- Back control finishing details (RNC variations, bow-and-arrow, body triangle)
- Sweeps to submissions (chaining sweeps into immediate submission attacks)
"""

import os, json, re
from pathlib import Path
from datetime import datetime

# ===== Configuration =====
IS_CI = os.environ.get("GITHUB_ACTIONS") == "true"
SITE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE_URL = "https://wiki.bjj-app.net"

LANGUAGES = {
    "en": {"name": "English", "dir": "en"},
    "ja": {"name": "日本語", "dir": "ja"},
    "pt": {"name": "Português", "dir": "pt"},
}

BELT_BG = {"white": "#e2e2ee", "blue": "#2563eb", "purple": "#7c3aed", "brown": "#92400e", "black": "#111"}
BELT_FG = {"white": "#111", "blue": "#fff", "purple": "#fff", "brown": "#fff", "black": "#fff"}

# ===== 5 Themes Definition =====
ARTICLES = {
    "bjj-attacking-from-turtle": {
        "category": "Techniques",
        "en": {
            "title": "Attacking from Turtle Position - Top & Bottom Turtle Attacks",
            "meta": "Master attacking from turtle position. Learn top turtle attacks (turk ride, turtle pin defense), bottom turtle escapes (granby roll, shrimp), and complete turtle systems.",
            "h1": "Attacking from Turtle Position: Complete System",
            "intro": "Turtle position offers unique offensive opportunities for both top and bottom players. This comprehensive guide covers top turtle attacks, bottom turtle transitions, and the legendary Granby roll system.",
            "how_to": "1. From top position, establish tight control on opponent's hips and clasp hands. 2. Drive shoulders into opponent's back to maintain pressure. 3. Hunt for arm control and back takes. 4. From bottom turtle, use shrimp motion to regain guard. 5. Master the Granby roll to reverse position.",
            "details": "Top player maintains constant pressure while bottom player times hip escape perfectly. Key positions: turk ride (cross face + hip control), rear mount entry, and transition chains.",
            "variations": "Granby roll variations, back take from turtle, arm trap transitions, wrestling underhook entry",
            "belt": "blue", "stars": "★★★★☆", "label": "Intermediate"
        },
        "ja": {
            "title": "[JA] タートルポジションからの攻撃 - トップ&ボトムシステム",
            "meta": "タートルポジション攻撃マスター。トップタートル攻撃・ボトムエスケープ・グランビーロール・完全システム解説。",
            "h1": "タートルポジション攻撃：完全システム",
            "intro": "タートルポジションはトップ・ボトム両プレイヤーにユニークな攻撃機会を提供します。トップタートル攻撃、ボトムタートル遷移、グランビーロールシステムを完全解説。",
            "how_to": "1. トップからの股関節コントロール確立とクラスプ。 2. 肩で背中にプレッシャー。 3. アームコントロール・バックテイク狩り。 4. ボトムからのシュリンプでガード回復。 5. グランビーロールでポジション逆転。",
            "details": "トップは常時プレッシャー維持、ボトムはシュリンプタイミング完璧化。キーポジション：ターク乗り、リアマウント、遷移チェーン。",
            "variations": "グランビーバリエーション、タートルからのバックテイク、アームトラップ、レスリング下手フック",
            "belt": "blue", "stars": "★★★★☆", "label": "中級"
        },
        "pt": {
            "title": "[PT] Ataque da Posição de Tartaruga - Sistemas de Topo e Fundo",
            "meta": "Domine ataques da posição de tartaruga. Aprenda ataques de tartaruga no topo, escapes de fundo, granby roll e sistemas completos.",
            "h1": "Ataque da Posição de Tartaruga: Sistema Completo",
            "intro": "A posição de tartaruga oferece oportunidades ofensivas únicas para jogadores de topo e fundo. Este guia abrangente cobre ataques de tartaruga no topo, transições de tartaruga no fundo e o legendário sistema de granby roll.",
            "how_to": "1. Do topo, estabeleça controle firme dos quadris do oponente e claspe as mãos. 2. Dirija os ombros para as costas para manter pressão. 3. Procure por controles de braço e back takes. 4. Do fundo, use movimento de camarão para recuperar guard. 5. Domine o granby roll para reverter posição.",
            "details": "Jogador de topo mantém pressão constante enquanto jogador de fundo tempera perfectly o hip escape. Posições-chave: turk ride, entrada rear mount, cadeias de transição.",
            "variations": "Variações de granby roll, back take da tartaruga, transições de arm trap, entrada de underhooked wrestling",
            "belt": "blue", "stars": "★★★★☆", "label": "Intermediário"
        }
    },
    "bjj-conditioning-science": {
        "category": "Training",
        "en": {
            "title": "BJJ Conditioning Science - Energy Systems, Strength Training & Periodization",
            "meta": "Understand BJJ conditioning science. Energy systems (aerobic/anaerobic), VO2 max training, HRV monitoring, and scientific periodization for competition.",
            "h1": "BJJ Conditioning Science: Evidence-Based Training Principles",
            "intro": "Modern BJJ conditioning is grounded in sports science. This guide covers the three energy systems utilized in jiu-jitsu, VO2 max development, heart rate variability (HRV) monitoring, and periodization models proven for competitive success.",
            "how_to": "1. Assess your current conditioning baseline with VO2 max testing. 2. Design training blocks: preparation, competition, recovery phases. 3. Train aerobic system with steady-state rolling (60-70% HR max). 4. Develop anaerobic capacity with high-intensity intervals (90%+ HR max). 5. Monitor HRV daily to optimize recovery.",
            "details": "Energy systems: Phosphocreatine (0-15s), glycolytic (15-90s), aerobic (90s+). BJJ requires all three. HRV trends indicate readiness; dropping HRV signals need for recovery.",
            "variations": "Linear periodization, undulating periodization, block periodization, sport-specific conditioning protocols",
            "belt": "blue", "stars": "★★★★★", "label": "Intermediate"
        },
        "ja": {
            "title": "[JA] BJJコンディショニング科学 - エネルギーシステム・強度・ピリオダイゼーション",
            "meta": "BJJコンディショニング科学マスター。エネルギーシステム・VO2max・HRV・科学的ピリオダイゼーション完全解説。",
            "h1": "BJJコンディショニング科学：エビデンスベース原則",
            "intro": "現代BJJコンディショニングはスポーツ科学に基礎。3つのエネルギーシステム、VO2max開発、HRVモニタリング、競技ピリオダイゼーションを完全解説。",
            "how_to": "1. VO2maxテストでベースライン評価。 2. ピリオダイゼーション設計：準備・競技・回復フェーズ。 3. 有酸素トレーニング：60-70%HR低強度。 4. 無酸素開発：90%+HR高強度インターバル。 5. HRV毎日モニタリングで回復最適化。",
            "details": "エネルギーシステム：リン酸化物(0-15s)・糖質無酸素(15-90s)・有酸素(90s+)。BJJは3つ全部使用。HRV低下=回復必要信号。",
            "variations": "リニアピリオダイゼーション、アンジュレーション、ブロックピリオダイゼーション、スポーツ特異的",
            "belt": "blue", "stars": "★★★★★", "label": "中級"
        },
        "pt": {
            "title": "[PT] Ciência do Condicionamento do BJJ - Sistemas de Energia, Força & Periodização",
            "meta": "Domine a ciência do condicionamento do BJJ. Sistemas de energia, treinamento de VO2 max, monitoramento de HRV e periodização científica.",
            "h1": "Ciência do Condicionamento do BJJ: Princípios Baseados em Evidências",
            "intro": "O condicionamento moderno do BJJ é fundamentado na ciência do esporte. Este guia cobre os três sistemas de energia utilizados no jiu-jitsu, desenvolvimento de VO2 máximo, monitoramento de variabilidade da frequência cardíaca (HRV) e modelos de periodização comprovados para sucesso competitivo.",
            "how_to": "1. Avalie seu condicionamento baseline com teste de VO2 máximo. 2. Projete blocos de treinamento: preparação, competição, recuperação. 3. Treine sistema aeróbico com rolling steady-state (60-70% HR max). 4. Desenvolva capacidade anaeróbia com intervalos de alta intensidade (90%+ HR max). 5. Monitore HRV diariamente para otimizar recuperação.",
            "details": "Sistemas de energia: Fosfato (0-15s), glicolítico (15-90s), aeróbico (90s+). O BJJ requer todos os três. Tendências de HRV indicam prontidão; HRV em queda sinaliza necessidade de recuperação.",
            "variations": "Periodização linear, periodização ondulatória, periodização em blocos, protocolos específicos do esporte",
            "belt": "blue", "stars": "★★★★★", "label": "Intermediário"
        }
    },
    "bjj-guard-setups-masterclass": {
        "category": "Techniques",
        "en": {
            "title": "Guard Setups Masterclass - Entries into Closed, Half, Butterfly, DLR & Spider Guard",
            "meta": "Master guard setup entries. Learn systematic approaches to establishing closed guard, half guard, butterfly guard, De La Riva, and spider guard from standing position.",
            "h1": "Guard Setups Masterclass: Complete Entry Systems",
            "intro": "Guard pulling is an art form. This masterclass covers systematic entries into five essential guard types: closed guard, half guard, butterfly guard, De La Riva (DLR), and spider guard. Perfect timing and positioning transform guard pull success.",
            "how_to": "1. From standing, assess opponent's posture and weight distribution. 2. For closed guard pull: grab collar, drop to hips, secure grip. 3. For half guard: outside leg hook, hip angle control. 4. For butterfly guard: use inside legs, maintain chest pressure. 5. For DLR/spider: hook foot, create angle, transition guard.",
            "details": "Guard pull timing: pull when opponent steps forward or attempts to break distance. Key details: collar control preventing upright posture, leg positioning for stability, hip angle for guard retention.",
            "variations": "Sitting guard pull, jumping guard pull, berimbolo entry, collar drag guards, lapel guard entries",
            "belt": "blue", "stars": "★★★★☆", "label": "Intermediate"
        },
        "ja": {
            "title": "[JA] ガードセットアップマスタークラス - クローズド・ハーフ・バタフライ・DLR・スパイダー完全習得",
            "meta": "ガードセットアップ5種類完全マスター。クローズド・ハーフ・バタフライ・DLR・スパイダーのエントリーシステム詳細。",
            "h1": "ガードセットアップマスタークラス：完全エントリーシステム",
            "intro": "ガードプルはアート。5つの必須ガード(クローズド・ハーフ・バタフライ・DLR・スパイダー)への体系的エントリーを完全習得。",
            "how_to": "1. 相手のポスチャー・ウェイト分析。 2. クローズドガード：襟グリップ・ヒップドロップ・安全グリップ。 3. ハーフガード：外脚フック・股関節角度。 4. バタフライガード：内脚・チェストプレッシャー。 5. DLR/スパイダー：フックの足・角度作成・ガード遷移。",
            "details": "プルタイミング：相手がステップ・ディスタンスブレーク時。キー：襟でアップライト防止、脚安定、股関節角度。",
            "variations": "シッティングプル、ジャンピングプル、ベリンボロ、襟ドラッグ、ラペルガードエントリー",
            "belt": "blue", "stars": "★★★★☆", "label": "中級"
        },
        "pt": {
            "title": "[PT] Masterclass de Setups de Guard - Entradas em Guard Fechado, Meio, Borboleta, DLR & Aranha",
            "meta": "Domine entradas de guard. Sistemas de setup para guard fechado, meio guard, butterfly guard, De La Riva e spider guard.",
            "h1": "Masterclass de Setups de Guard: Sistemas Completos de Entrada",
            "intro": "O guard pull é uma forma de arte. Este masterclass cobre entradas sistemáticas em cinco tipos de guard essenciais: guard fechado, meio guard, butterfly guard, De La Riva (DLR) e spider guard.",
            "how_to": "1. Em pé, avalie postura e distribuição de peso do oponente. 2. Para guard fechado: segure colar, derrube nos quadris. 3. Para meio guard: hook na perna externa, controle de ângulo de quadril. 4. Para butterfly guard: use pernas internas, pressão de peito. 5. Para DLR/aranha: hook no pé, crie ângulo, transição de guard.",
            "details": "Timing do guard pull: puxe quando o oponente avança ou tenta quebrar a distância. Detalhes chave: controle de colar impedindo postura ereta, posicionamento de perna para estabilidade, ângulo de quadril para retenção de guard.",
            "variations": "Guard pull sentado, guard pull pulando, entrada de berimbolo, guards de arrasto de colar, entradas de guard de lapela",
            "belt": "blue", "stars": "★★★★☆", "label": "Intermediário"
        }
    },
    "bjj-back-control-finishing": {
        "category": "Techniques",
        "en": {
            "title": "Back Control Finishing Details - RNC Variations, Bow-and-Arrow & Body Triangle",
            "meta": "Master back control finishing. Learn RNC variations, bow-and-arrow choke perfection, body triangle finishes, and choke placement for competition success.",
            "h1": "Back Control Finishing: Advanced Choke Details",
            "intro": "Back control is the most dominant position in jiu-jitsu. This guide covers three finishing methods: the Rear Naked Choke (RNC) with multiple grip variations, the Bow-and-Arrow choke using lapel control, and the body triangle for absolute chest pressure.",
            "how_to": "1. Establish rear mount with seat belt grip. 2. For RNC: sink chin into neck, hips high, rotate shoulders. 3. For Bow-and-Arrow: use lapel, feet in hips, pull hands to create choke. 4. For body triangle: extend legs, feet locked, lean back pressure. 5. Finish with controlled pressure—never jerk.",
            "details": "RNC mechanics: carotid compression (not neck break). Hand placement crucial: thumbs forward for defense awareness. Bow-and-Arrow uses lapel compression and hip pressure. Body triangle requires perfect leg extension and core tension.",
            "variations": "RNC with one arm locked, high elbow RNC, Mataleão choke, bow-and-arrow from side control, body triangle from mount",
            "belt": "blue", "stars": "★★★★★", "label": "Intermediate"
        },
        "ja": {
            "title": "[JA] バックコントロール・フィニッシング詳細 - RNC・ボウアンドアロー・ボディトライアングル",
            "meta": "バックコントロール・フィニッシング完全習得。RNCバリエーション・ボウアンドアロー・ボディトライアングル完全解説。",
            "h1": "バックコントロール・フィニッシング：チョーク完全解説",
            "intro": "バックコントロールはBJJで最もドミナント。RNC・ボウアンドアロー・ボディトライアングル3つのフィニッシング方法を完全習得。",
            "how_to": "1. シートベルトでリアマウント確立。 2. RNC：アゴを首に沈める・ヒップ高・肩回転。 3. ボウアンドアロー：ラペル使用・足で股関節・手で引く。 4. ボディトライアングル：脚延伸・ロック・背中プレッシャー。 5. コントロールプレッシャーでフィニッシュ。",
            "details": "RNCメカニクス：頸動脈圧迫。ハンド配置：親指前で防御意識。ボウアンドアロー=ラペル圧迫+股関節プレッシャー。ボディトライアングル=脚完全延伸+コア張力。",
            "variations": "RNC片腕ロック・ハイエルボーRNC・マタレアン・サイドからのボウアンドアロー・マウントからのボディトライアングル",
            "belt": "blue", "stars": "★★★★★", "label": "中級"
        },
        "pt": {
            "title": "[PT] Detalhes de Acabamento de Controle de Costas - Variações de RNC, Arco-e-Flecha & Triângulo de Corpo",
            "meta": "Domine o acabamento do controle de costas. Aprenda variações de RNC, perfeição do arco-e-flecha e finalizações de triângulo de corpo.",
            "h1": "Acabamento do Controle de Costas: Detalhes Avançados de Choke",
            "intro": "O controle de costas é a posição mais dominante no jiu-jitsu. Este guia cobre três métodos de acabamento: o Rear Naked Choke (RNC) com múltiplas variações de grip, o choke arco-e-flecha usando controle de lapela, e o triângulo de corpo para pressão absoluta de peito.",
            "how_to": "1. Estabeleça rear mount com grip de cinturão de segurança. 2. Para RNC: afunde queixo no pescoço, quadris altos, gire ombros. 3. Para arco-e-flecha: use lapela, pés nos quadris, puxe mãos. 4. Para triângulo de corpo: estenda pernas, pés travados, pressão para trás. 5. Finalize com pressão controlada.",
            "details": "Mecânica de RNC: compressão carótida (não quebra de pescoço). Posicionamento de mão crucial: polegares para frente. Arco-e-flecha usa compressão de lapela e pressão de quadril. Triângulo de corpo requer extensão perfeita de perna e tensão do núcleo.",
            "variations": "RNC com um braço travado, RNC de cotovelo alto, choke Mataleão, arco-e-flecha de side control, triângulo de corpo de mount",
            "belt": "blue", "stars": "★★★★★", "label": "Intermediário"
        }
    },
    "bjj-sweeps-to-submissions": {
        "category": "Techniques",
        "en": {
            "title": "Sweeps to Submissions - Chaining Sweeps into Immediate Submission Attacks",
            "meta": "Master sweep-to-submission chains. Learn how to transition seamlessly from successful sweeps into immediate chokes, armbars, and leg locks for unstoppable attacks.",
            "h1": "Sweeps to Submissions: Seamless Chain Attacks",
            "intro": "The best sweeps create immediate submission opportunities. This guide teaches how to chain successful sweeps into devastating submission attacks before opponent can reset. Develop unstoppable momentum flow.",
            "how_to": "1. Execute sweep with proper timing and hip rotation. 2. Before opponent fully stabilizes, assess position (now top player). 3. Immediately hunt for submission entries: armbars, collars, leg locks. 4. Use opponent's momentum against them for faster finish. 5. Complete submission chain in one fluid motion.",
            "details": "Sweep momentum creates openings: hip bump sweep into armbar from guard, scissor sweep into collar drag into back take, flower sweep into mount armbars. Key: recognize submission opportunity the instant sweep connects.",
            "variations": "Sweep-to-triangle, sweep-to-armbar, sweep-to-back-take, sweep-to-leg-lock, sweep-to-choke chains",
            "belt": "blue", "stars": "★★★★★", "label": "Intermediate"
        },
        "ja": {
            "title": "[JA] スウィープからサブミッションへ - 掃き技から即座のサブミッション攻撃チェーン",
            "meta": "スウィープ・サブミッション・チェーンマスター。掃き技から即座のチョーク・アームバー・レッグロックへの完全習得。",
            "h1": "スウィープからサブミッション：シームレスチェーン攻撃",
            "intro": "最高のスウィープは即座のサブミッション機会を作成。スウィープから相手がリセットする前に即座のサブミッション攻撃へのシームレス遷移を習得。",
            "how_to": "1. 正確なタイミング・股関節回転でスウィープ実行。 2. 相手が完全に安定する前に、ポジション評価（トップになった）。 3. 即座にサブミッション狩り：アームバー・カラー・レッグロック。 4. 相手の勢いを利用。 5. 流体的な1モーションで完全フィニッシュ。",
            "details": "スウィープ勢いで開口部作成：ヒップバンプ→アームバー、シザー→襟ドラッグ→バックテイク、フラワー→マウントアームバー。キー：スウィープが繋がる瞬間にサブミッション機会認識。",
            "variations": "スウィープ→トライアングル、スウィープ→アームバー、スウィープ→バックテイク、スウィープ→レッグロック、スウィープ→チョーク",
            "belt": "blue", "stars": "★★★★★", "label": "中級"
        },
        "pt": {
            "title": "[PT] Sweeps para Submissões - Encadeando Sweeps em Ataques de Submissão Imediatos",
            "meta": "Domine cadeias de sweep-submissão. Aprenda transições contínuas de sweeps bem-sucedidos em ataques de submissão imediatos.",
            "h1": "Sweeps para Submissões: Ataques de Cadeia Contínua",
            "intro": "Os melhores sweeps criam oportunidades de submissão imediata. Este guia ensina como encadear sweeps bem-sucedidos em ataques de submissão devastadores antes do adversário se resetar.",
            "how_to": "1. Execute sweep com timing adequado e rotação de quadril. 2. Antes do adversário se estabilizar completamente, avalie a posição (agora jogador de topo). 3. Imediatamente procure por entradas de submissão: armbars, collars, leg locks. 4. Use o momentum do adversário a seu favor. 5. Complete a cadeia de submissão em um movimento fluido.",
            "details": "O momentum do sweep cria aberturas: hip bump sweep para armbar, scissor sweep para collar drag para back take, flower sweep para mount armbars. Chave: reconhecer oportunidade de submissão no instante que o sweep se conecta.",
            "variations": "Sweep-para-triângulo, sweep-para-armbar, sweep-para-back-take, sweep-para-leg-lock, cadeias sweep-para-choke",
            "belt": "blue", "stars": "★★★★★", "label": "Intermediário"
        }
    }
}

# ===== Helper Functions =====
def slugify(text):
    """Convert text to URL slug."""
    return re.sub(r'[^a-z0-9-]', '', text.lower().replace(' ', '-'))

def generate_html(article_key, lang_code, article_data):
    """Generate single HTML article file."""
    lang_info = article_data[lang_code]

    # Determine belt styling
    belt = lang_info.get("belt", "blue")
    belt_bg = BELT_BG.get(belt, "#2563eb")
    belt_fg = BELT_FG.get(belt, "#fff")
    belt_label_map = {
        "white": "White Belt", "blue": "Blue Belt", "purple": "Purple Belt",
        "brown": "Brown Belt", "black": "Black Belt"
    }

    # Language-specific category map
    category_map = {
        "en": {
            "Pro Athletes": "Pro Athletes",
            "Techniques": "Techniques",
            "Training": "Training",
            "Fundamentals": "Fundamentals",
        },
        "ja": {
            "Pro Athletes": "プロ選手",
            "Techniques": "テクニック",
            "Training": "トレーニング",
            "Fundamentals": "基礎",
        },
        "pt": {
            "Pro Athletes": "Atletas Profissionais",
            "Techniques": "Técnicas",
            "Training": "Treinamento",
            "Fundamentals": "Fundamentos",
        }
    }

    category = article_data.get("category", "Techniques")
    category_display = category_map.get(lang_code, {}).get(category, category)

    # Language selector map
    other_langs = {
        "en": [("ja", "日本語"), ("pt", "Português")],
        "ja": [("en", "English"), ("pt", "Português")],
        "pt": [("en", "English"), ("ja", "日本語")],
    }

    lang_links = ""
    for other_lang, other_label in other_langs[lang_code]:
        lang_links += f'<a href="{article_key}.html" hreflang="{other_lang}">{other_label}</a>'

    # Alternate hreflang links
    alt_links = ""
    for alt_lang in ["en", "ja", "pt"]:
        alt_links += f'<link rel="alternate" hreflang="{alt_lang}" href="{SITE_URL}/{alt_lang}/{article_key}.html">\n'

    # HTML structure
    html = f"""<!DOCTYPE html>
<html lang="{lang_code}">
<head>
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.googletagmanager.com">
<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
<link rel="dns-prefetch" href="https://www.google-analytics.com">
<link rel="dns-prefetch" href="https://fonts.googleapis.com">
<meta charset="UTF-8">
  <link rel="icon" href="https://wiki.bjj-app.net/favicon.svg" type="image/svg+xml">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{lang_info['title']} | BJJ Wiki</title>
<meta name="description" content="{lang_info['meta']}">
<meta property="og:title" content="{lang_info['title']}">
<meta property="og:description" content="{lang_info['meta']}">
<meta property="og:image" content="{SITE_URL}/og-image.svg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:type" content="article">
<meta property="og:url" content="{SITE_URL}/{lang_code}/{article_key}.html">
<link rel="canonical" href="{SITE_URL}/{lang_code}/{article_key}.html">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/en/{article_key}.html">
{alt_links}
<style>
:root{{
  --bg:#080b12;--surface:#0f1420;--card:#141926;
  --border:#1f2840;--text:#e8eaf6;--muted:#6b7699;
  --accent:#7c6af7;--accent2:#a78bfa;
  --green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--blue:#3b82f6;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif;
  line-height:1.75;padding:0 16px}}
a{{color:var(--accent2);text-decoration:none}}
a:hover{{text-decoration:underline}}

.container{{max-width:860px;margin:0 auto;padding-bottom:80px}}
header{{display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:12px;padding:20px 0;border-bottom:1px solid var(--border);
  margin-bottom:40px}}
.logo{{font-size:1.3rem;font-weight:800;color:var(--text)}}
.logo span{{color:var(--accent)}}
header nav{{display:flex;gap:16px}}
header nav a{{font-size:0.85rem;color:var(--muted);padding:4px 10px;
  border-radius:6px;border:1px solid transparent}}
header nav a:hover{{color:var(--text);border-color:var(--border);text-decoration:none}}
.lang-switcher{{font-size:0.82rem;color:var(--muted)}}
.lang-switcher a{{color:var(--muted);padding:3px 8px;border-radius:5px;
  border:1px solid var(--border)}}
.lang-switcher a:hover{{color:var(--text);border-color:var(--accent);text-decoration:none}}

.badge{{display:inline-block;padding:4px 12px;border-radius:20px;
  font-size:0.72rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;
  background:#1f2840;color:var(--accent2);border:1px solid #2d2060}}
.belt{{display:inline-block;padding:3px 10px;border-radius:20px;
  font-size:0.72rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
  margin-left:6px;border:1px solid var(--border)}}
.belt-blue{{color:var(--blue);border-color:#1e3a6e;background:#0f1e38}}

h1{{font-size:2.2rem;font-weight:800;line-height:1.25;margin:12px 0 16px;
  letter-spacing:-0.02em}}
@media(max-width:600px){{h1{{font-size:1.7rem}}}}

h1 + p{{font-size:1.05rem;color:#b0b8d4;margin-bottom:32px;line-height:1.8}}

h2{{font-size:1rem;font-weight:700;color:var(--accent2);
  text-transform:uppercase;letter-spacing:.08em;
  display:flex;align-items:center;gap:8px;
  margin:28px 0 12px}}
h2::before{{content:'';width:3px;height:14px;
  background:linear-gradient(180deg,var(--accent),var(--accent2));
  border-radius:2px;display:block;flex-shrink:0}}

.card{{background:var(--card);border:1px solid var(--border);
  border-radius:14px;padding:24px;margin-bottom:8px}}
.card p{{color:#c4cce8;font-size:0.95rem;margin-bottom:0}}
.card p + p{{margin-top:12px}}
.card strong{{color:var(--text)}}

.card .step{{display:flex;gap:12px;margin-bottom:14px;align-items:flex-start}}
.card .step:last-child{{margin-bottom:0}}
.step-num{{min-width:26px;height:26px;border-radius:50%;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  display:flex;align-items:center;justify-content:center;
  font-size:0.72rem;font-weight:700;color:#fff;flex-shrink:0;margin-top:2px}}

.aff-box{{background:linear-gradient(135deg,#141926,#1a1040);
  border:1px solid #2d2060;border-radius:14px;
  padding:24px;margin:32px 0;text-align:center}}
.aff-box p{{color:var(--muted);font-size:0.9rem;margin-bottom:14px}}
.aff-btn{{display:inline-block;padding:10px 24px;border-radius:10px;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff;font-weight:700;font-size:0.9rem;
  transition:opacity .2s,transform .15s}}
.aff-btn:hover{{opacity:.88;transform:translateY(-1px);text-decoration:none}}

.faq{{background:var(--card);border:1px solid var(--border);
  border-radius:14px;padding:24px;margin-top:8px}}
.faq-q{{font-weight:700;color:var(--accent2);margin-bottom:10px;font-size:0.95rem}}
.faq p{{color:#c4cce8;font-size:0.92rem}}

.related-links{{display:grid;
  grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}}
.related-links a{{display:flex;align-items:center;justify-content:space-between;
  padding:11px 16px;background:var(--card);border:1px solid var(--border);
  border-radius:10px;font-size:0.88rem;color:var(--text);
  transition:border-color .2s,background .2s}}
.related-links a::after{{content:'→';color:var(--muted);font-size:0.8rem;
  transition:color .2s,transform .2s}}
.related-links a:hover{{border-color:var(--accent);background:#1a1e30;
  text-decoration:none}}
.related-links a:hover::after{{color:var(--accent2);transform:translateX(3px)}}

footer{{padding:28px 0;border-top:1px solid var(--border);
  text-align:center;color:var(--muted);font-size:0.8rem;margin-top:48px}}

.difficulty-bar{{display:flex;align-items:center;gap:12px;margin:12px 0 28px;flex-wrap:wrap}}
.belt-tag{{display:inline-flex;align-items:center;gap:6px;padding:5px 14px;border-radius:20px;font-size:0.78rem;font-weight:700;letter-spacing:.05em}}
.stars{{font-size:1.1rem;letter-spacing:2px}}
.diff-label{{font-size:0.8rem;color:#6b7699}}

.share-bar{{margin:32px 0;padding:20px;background:var(--card);border:1px solid var(--border);border-radius:12px;text-align:center}}
.share-bar p{{color:var(--muted);font-size:0.85rem;margin-bottom:12px}}
.share-btns{{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}}
.share-btn{{display:inline-flex;align-items:center;gap:6px;padding:8px 18px;border-radius:8px;font-size:0.85rem;font-weight:700;text-decoration:none;transition:opacity .2s}}
.share-btn:hover{{opacity:.8;text-decoration:none}}
.share-btn.x{{background:#000;color:#fff}}
.share-btn.reddit{{background:#ff4500;color:#fff}}

.cta-banner{{background:linear-gradient(135deg,#1e3a8a,#0f172a);
  border:1px solid #1e40af;border-radius:14px;padding:24px;
  margin:32px 0;text-align:center}}
.cta-banner p{{color:var(--muted);font-size:0.9rem;margin-bottom:16px}}
.cta-btn{{display:inline-block;padding:12px 28px;border-radius:10px;
  background:linear-gradient(135deg,#3b82f6,#60a5fa);
  color:#fff;font-weight:700;font-size:0.9rem;text-decoration:none;
  transition:opacity .2s,transform .15s}}
.cta-btn:hover{{opacity:.9;transform:translateY(-2px);text-decoration:none}}
</style>
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-7LM8L3TRZM"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-7LM8L3TRZM');
  </script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{lang_info['title']}",
  "description": "{lang_info['meta']}",
  "url": "{SITE_URL}/{lang_code}/{article_key}.html",
  "inLanguage": "{lang_code}",
  "author": {{
    "@type": "Organization",
    "name": "BJJ Wiki",
    "url": "{SITE_URL}/"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "BJJ Wiki",
    "url": "{SITE_URL}/"
  }},
  "datePublished": "{datetime.now().isoformat()}",
  "dateModified": "{datetime.now().isoformat()}",
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "{SITE_URL}/{lang_code}/{article_key}.html"
  }}
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{
      "@type": "ListItem",
      "position": 1,
      "name": "BJJ Wiki",
      "item": "{SITE_URL}/{lang_code}/index.html"
    }},
    {{
      "@type": "ListItem",
      "position": 2,
      "name": "{lang_info['title']}",
      "item": "{SITE_URL}/{lang_code}/{article_key}.html"
    }}
  ]
}}
</script>
</head>
<body>
<div class="container">
  <header>
    <a href="../index.html" class="logo">BJJ<span>Wiki</span></a>
    <nav>
      <a href="../index.html">Home</a>
      <a href="index.html">Techniques</a>
    </nav>
  </header>

  <div class="difficulty-bar">
    <span class="badge">{category_display}</span>
    <span class="belt belt-blue">{lang_info.get('label', 'Intermediate')}</span>
    <span class="stars">{lang_info.get('stars', '★★★★☆')}</span>
  </div>

  <h1>{lang_info['h1']}</h1>
  <p>{lang_info['intro']}</p>

  <h2>How To</h2>
  <div class="card">
    <div class="step">
      <div class="step-num">1</div>
      <p><strong>Setup & Positioning:</strong> {lang_info['how_to'].split('. ')[0]}</p>
    </div>
    <div class="step">
      <div class="step-num">2</div>
      <p><strong>Control:</strong> {lang_info['how_to'].split('. ')[1]}</p>
    </div>
    <div class="step">
      <div class="step-num">3</div>
      <p><strong>Technique Execution:</strong> {lang_info['how_to'].split('. ')[2]}</p>
    </div>
    <div class="step">
      <div class="step-num">4</div>
      <p><strong>Pressure Application:</strong> {lang_info['how_to'].split('. ')[3]}</p>
    </div>
    <div class="step">
      <div class="step-num">5</div>
      <p><strong>Finish:</strong> {lang_info['how_to'].split('. ')[4]}</p>
    </div>
  </div>

  <h2>Key Details</h2>
  <div class="card">
    <p>{lang_info['details']}</p>
  </div>

  <h2>Variations</h2>
  <div class="card">
    <p>{lang_info['variations']}</p>
  </div>

  <div class="cta-banner">
    <p>🥋 <strong>Learn more techniques and progress your BJJ game</strong></p>
    <a href="https://bjj-app-one.vercel.app" class="cta-btn" target="_blank" rel="noopener">Open BJJ App</a>
  </div>

  <div class="share-bar">
    <p>Share this technique:</p>
    <div class="share-btns">
      <a href="https://twitter.com/intent/tweet?text={lang_info['title']}&url={SITE_URL}/{lang_code}/{article_key}.html" class="share-btn x" target="_blank" rel="noopener">X</a>
      <a href="https://reddit.com/r/bjj" class="share-btn reddit" target="_blank" rel="noopener">Reddit</a>
    </div>
  </div>

  <footer>
    <p>&copy; 2026 BJJ Wiki. All rights reserved.</p>
  </footer>
</div>
</body>
</html>
"""
    return html

# ===== Main Generation =====
def main():
    """Generate all batch pages."""
    generated_count = 0

    for article_key, article_data in ARTICLES.items():
        for lang_code in ["en", "ja", "pt"]:
            lang_dir = os.path.join(SITE_DIR, LANGUAGES[lang_code]["dir"])
            os.makedirs(lang_dir, exist_ok=True)

            filepath = os.path.join(lang_dir, f"{article_key}.html")
            html_content = generate_html(article_key, lang_code, article_data)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)

            print(f"✅ {lang_code.upper()}: {article_key}")
            generated_count += 1

    print(f"\n✅ Generated {generated_count} pages (5 themes × 3 languages)")

if __name__ == "__main__":
    main()
