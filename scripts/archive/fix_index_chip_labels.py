#!/usr/bin/env python3
"""
fix_index_chip_labels.py — z255ss (WIKI-9): index.html の chip label 翻訳

z255rr で 3 index page に言語スイッチャー + category heading は翻訳したが、
chip 内の技名 (Rear Naked Choke 等 100+ 件) は EN 残留。

固定辞書で BJJ コミュニティ標準のカタカナ / PT 表記に翻訳。
EN 維持の固有名詞 (Berimbolo / Kimura / Omoplata 等) は EN のまま (BJJ
コミュニティ標準では原語保持が普通)。

Idempotent: 既に翻訳済みの chip は元 EN にも matching しないので不変。
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# 翻訳辞書 (en → ja / pt)
# BJJ コミュニティ標準: 既にカタカナ / PT で定着した訳のみ採用、
# 固有名詞 (Berimbolo / Kimura / Omoplata 等) は両 locale で原語保持
TRANSLATIONS: dict[str, dict[str, str]] = {
    # ── Chokes ──
    "Rear Naked Choke": {"ja": "裸絞め", "pt": "Mata Leão"},
    "Triangle Choke": {"ja": "三角絞め", "pt": "Triângulo"},
    "Guillotine Choke": {"ja": "ギロチンチョーク", "pt": "Guilhotina"},
    "Bow and Arrow Choke": {"ja": "ボウ・アンド・アロー", "pt": "Arco e Flecha"},
    "Ezekiel Choke": {"ja": "エゼキエル", "pt": "Ezequiel"},
    "D'Arce Choke": {"ja": "ダースチョーク", "pt": "D'Arce"},
    "Anaconda Choke": {"ja": "アナコンダチョーク", "pt": "Anaconda"},
    "Loop Choke": {"ja": "ループチョーク", "pt": "Loop Choke"},
    "Arm Triangle Choke": {"ja": "アームトライアングル", "pt": "Triângulo de Braço"},
    "North-South Choke": {"ja": "ノースサウスチョーク", "pt": "Norte-Sul Choke"},
    "Baseball Choke": {"ja": "ベースボールチョーク", "pt": "Baseball Choke"},
    "Cross Collar Choke": {"ja": "十字絞め", "pt": "Cruzado"},
    "Clock Choke": {"ja": "時計絞め", "pt": "Relógio"},
    "Lapel Choke": {"ja": "ラペルチョーク", "pt": "Choke de Lapela"},
    # ── Defense ──
    "Guard Retention": {"ja": "ガードリテンション", "pt": "Recuperação de Guarda"},
    "Hip Escape": {"ja": "シュリンプ", "pt": "Fuga de Quadril"},
    "Frame": {"ja": "フレーム", "pt": "Frame"},
    "Sprawl": {"ja": "スプロール", "pt": "Sprawl"},
    "Back Defense": {"ja": "バック防御", "pt": "Defesa de Costas"},
    # ── Escape ──
    "Shrimp Escape": {"ja": "シュリンプエスケープ", "pt": "Fuga em Camarão"},
    "Bridge and Roll": {"ja": "ブリッジ&ロール", "pt": "Ponte e Rolamento"},
    "Elbow-Knee Escape": {"ja": "肘膝エスケープ", "pt": "Fuga Cotovelo-Joelho"},
    # ── Guard ──
    "Closed Guard": {"ja": "クローズドガード", "pt": "Guarda Fechada"},
    "Open Guard": {"ja": "オープンガード", "pt": "Guarda Aberta"},
    "Half Guard": {"ja": "ハーフガード", "pt": "Meia Guarda"},
    "Spider Guard": {"ja": "スパイダーガード", "pt": "Guarda Aranha"},
    "De La Riva Guard": {"ja": "デラヒーバガード", "pt": "Guarda De La Riva"},
    "Berimbolo": {"ja": "ベリンボロ", "pt": "Berimbolo"},
    "Butterfly Guard": {"ja": "バタフライガード", "pt": "Guarda Borboleta"},
    "Rubber Guard": {"ja": "ラバーガード", "pt": "Guarda de Borracha"},
    "X-Guard": {"ja": "Xガード", "pt": "Guarda X"},
    "Worm Guard": {"ja": "ワームガード", "pt": "Guarda Verme"},
    "Reverse De La Riva": {"ja": "リバースデラヒーバ", "pt": "De La Riva Reversa"},
    "50/50 Guard": {"ja": "50/50ガード", "pt": "Guarda 50/50"},
    "Lasso Guard": {"ja": "ラッソーガード", "pt": "Guarda Laço"},
    "Deep Half Guard": {"ja": "ディープハーフガード", "pt": "Meia Guarda Profunda"},
    "Z-Guard": {"ja": "Zガード", "pt": "Guarda Z"},
    "Sitting Guard": {"ja": "シッティングガード", "pt": "Guarda Sentada"},
    # ── Joint Lock ──
    "Armbar": {"ja": "アームバー", "pt": "Armbar"},
    "Kimura": {"ja": "キムラ", "pt": "Kimura"},
    "Americana": {"ja": "アメリカーナ", "pt": "Americana"},
    "Omoplata": {"ja": "オモプラタ", "pt": "Omoplata"},
    "Wrist Lock": {"ja": "リストロック", "pt": "Chave de Pulso"},
    "Straight Armbar": {"ja": "ストレートアームバー", "pt": "Armbar Reto"},
    "Monoplata": {"ja": "モノプラタ", "pt": "Monoplata"},
    # ── Leg Lock ──
    "Heel Hook": {"ja": "ヒールフック", "pt": "Heel Hook"},
    "Inside Heel Hook": {"ja": "インサイドヒールフック", "pt": "Heel Hook Interno"},
    "Outside Heel Hook": {"ja": "アウトサイドヒールフック", "pt": "Heel Hook Externo"},
    "Knee Bar": {"ja": "ニーバー", "pt": "Knee Bar"},
    "Toe Hold": {"ja": "トーホールド", "pt": "Toe Hold"},
    "Calf Slicer": {"ja": "カーフスライサー", "pt": "Calf Slicer"},
    "Ankle Lock": {"ja": "アンクルロック", "pt": "Chave de Tornozelo"},
    "Estima Lock": {"ja": "エスチマロック", "pt": "Estima Lock"},
    # ── Passing ──
    "Guard Pass": {"ja": "ガードパス", "pt": "Passagem de Guarda"},
    "Torreando Pass": {"ja": "トレアンドパス", "pt": "Passagem Toreador"},
    "Knee Slice Pass": {"ja": "ニースライスパス", "pt": "Passagem com Joelho"},
    "Leg Drag Pass": {"ja": "レッグドラッグパス", "pt": "Passagem Leg Drag"},
    "Headquarters Pass": {"ja": "ヘッドクオーターズパス", "pt": "Passagem Headquarters"},
    "Stack Pass": {"ja": "スタックパス", "pt": "Passagem Empilhada"},
    "Double Under Pass": {"ja": "ダブルアンダーパス", "pt": "Passagem Dupla por Baixo"},
    "Pressure Pass": {"ja": "プレッシャーパス", "pt": "Passagem com Pressão"},
    "Smash Pass": {"ja": "スマッシュパス", "pt": "Smash Pass"},
    "X-Pass": {"ja": "Xパス", "pt": "Passagem X"},
    # ── Position ──
    "Mount": {"ja": "マウント", "pt": "Montada"},
    "Back Mount": {"ja": "バックマウント", "pt": "Pegada de Costas"},
    "Side Control": {"ja": "サイドコントロール", "pt": "Cem Quilos"},
    "North-South": {"ja": "ノースサウス", "pt": "Norte-Sul"},
    "Knee on Belly": {"ja": "ニーオンベリー", "pt": "Joelho na Barriga"},
    "S-Mount": {"ja": "Sマウント", "pt": "Montada S"},
    "Modified Mount": {"ja": "モディファイドマウント", "pt": "Montada Modificada"},
    "Body Triangle": {"ja": "ボディトライアングル", "pt": "Triângulo de Corpo"},
    "Turtle Position": {"ja": "タートルポジション", "pt": "Posição de Tartaruga"},
    "Seat Belt Control": {"ja": "シートベルトコントロール", "pt": "Controle Cinto"},
    "Front Headlock": {"ja": "フロントヘッドロック", "pt": "Headlock Frontal"},
    "Underhook": {"ja": "アンダーフック", "pt": "Underhook"},
    "Overhook": {"ja": "オーバーフック", "pt": "Overhook"},
    # ── Sweep ──
    "Scissor Sweep": {"ja": "シザースイープ", "pt": "Tesoura"},
    "Flower Sweep": {"ja": "フラワースイープ", "pt": "Raspagem da Flor"},
    "Hip Bump Sweep": {"ja": "ヒップバンプスイープ", "pt": "Raspagem do Quadril"},
    "Pendulum Sweep": {"ja": "ペンデュラムスイープ", "pt": "Pêndulo"},
    "Tripod Sweep": {"ja": "トライポッドスイープ", "pt": "Tripé"},
    "Elevator Sweep": {"ja": "エレベータースイープ", "pt": "Elevador"},
    "Sickle Sweep": {"ja": "シックルスイープ", "pt": "Foice"},
    "Overhead Sweep": {"ja": "オーバーヘッドスイープ", "pt": "Raspagem Acima da Cabeça"},
    "Balloon Sweep": {"ja": "バルーンスイープ", "pt": "Balão"},
    "X-Guard Sweep": {"ja": "Xガードスイープ", "pt": "Raspagem da Guarda X"},
    # ── Takedown ──
    "Double Leg Takedown": {"ja": "ダブルレッグ", "pt": "Queda de Pernas Duplas"},
    "Single Leg Takedown": {"ja": "シングルレッグ", "pt": "Queda de Perna Única"},
    "Osoto Gari": {"ja": "大外刈り", "pt": "Osoto Gari"},
    "Ankle Pick": {"ja": "アンクルピック", "pt": "Ankle Pick"},
    "Harai Goshi": {"ja": "払腰", "pt": "Harai Goshi"},
    "Ippon Seoi Nage": {"ja": "一本背負投", "pt": "Ippon Seoi Nage"},
    "Morote Seoi Nage": {"ja": "両手背負投", "pt": "Morote Seoi Nage"},
    "Snap Down": {"ja": "スナップダウン", "pt": "Snap Down"},
    "Russian Tie": {"ja": "ロシアンタイ", "pt": "Russian Tie"},
    # ── Transition ──
    "Arm Drag": {"ja": "アームドラッグ", "pt": "Arrasto de Braço"},
    "Granby Roll": {"ja": "グランビーロール", "pt": "Granby Roll"},
    "Back Take": {"ja": "バックテイク", "pt": "Pegada das Costas"},
    "Technical Stand-Up": {"ja": "テクニカルスタンドアップ", "pt": "Levantada Técnica"},
    "Stand In Base": {"ja": "スタンドインベース", "pt": "Levantada em Base"},
}


def patch_index(lang: str) -> int:
    if lang == "en":
        return 0  # EN は元のまま
    fp = REPO_ROOT / lang / "index.html"
    if not fp.exists():
        return 0
    html = fp.read_text(encoding="utf-8")
    fixed = 0
    # 翻訳長いものから先に置換 (短いものが包含されないよう、e.g.
    # "Hip Escape" を先に置換すれば "Escape" 単独は当たらない)
    for en_name in sorted(TRANSLATIONS.keys(), key=lambda s: -len(s)):
        target = TRANSLATIONS[en_name].get(lang)
        if not target:
            continue
        # \g<1> 名前付き backref 構文を使う
        # (\1 + 数字始まり target で \15 等と誤解される regex bug 回避、
        #  例: target="50/50ガード" だと replacement "\150/50ガード\2" が
        #  \1 + 50 ではなく \150 (backref-150) と interpret される)
        pattern = (
            r'(<a href="[^"]+\.html">)'
            + re.escape(en_name)
            + r"(</a>)"
        )
        # callable replacement で安全に置換
        def make_replacer(t: str):
            return lambda m: m.group(1) + t + m.group(2)
        new, n = re.subn(pattern, make_replacer(target), html)
        fixed += n
        html = new
    fp.write_text(html, encoding="utf-8")
    return fixed


def main():
    print("🔧 fix_index_chip_labels.py — z255ss (WIKI-9)")
    for lang in ("ja", "pt"):
        n = patch_index(lang)
        print(f"  {lang}/index.html: {n} chips translated")


if __name__ == "__main__":
    main()
