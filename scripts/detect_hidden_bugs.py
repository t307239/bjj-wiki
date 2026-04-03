#!/usr/bin/env python3
"""
detect_hidden_bugs.py — スコアに表れない「隠れバグ」を自動検知

AUDIT_FRAMEWORK.md のスコアリングでは検知できない、
目視でしか見つからなかった問題を機械的に検出するスクリプト。

検知カテゴリ:
  1. Locale純粋性違反（JAページの英語残存、ENページの日本語残存等）
  2. ヨガセクション表示漏れ（コメントアウト忘れ）
  3. フッターレイアウト崩れ（コンテナ未ラップ）
  4. テンプレート不整合（©年号、CTA言語ミスマッチ）
  5. リンク切れ候補（hrefが空 or # のみ）
  6. HTMLタグ不整合（閉じタグ漏れの兆候）
  7. SEO検証（H1タグ欠落、meta description品質、canonical URL欠落）

使い方:
    python3 scripts/detect_hidden_bugs.py              # 全チェック
    python3 scripts/detect_hidden_bugs.py --lang ja    # JAのみ
    python3 scripts/detect_hidden_bugs.py --fix-hint   # 修正ヒント付き
    python3 scripts/detect_hidden_bugs.py --ci         # CI用（exitcode=違反数）

出力: STDOUT + ~/Claude/bjj-wiki/hidden_bugs_report.txt

依存: Python 3.8+ 標準ライブラリのみ
"""

import os
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

# ─────────────────────────────────────────────────────
# 設定
# ─────────────────────────────────────────────────────

WIKI_ROOT = Path(__file__).parent.parent
LANGUAGES = ["en", "ja"]  # PTは後回し（柔術コンテンツ充実後）
ALL_LANGUAGES = ["en", "ja", "pt"]  # --lang pt で個別指定は可能
CURRENT_YEAR = "2026"

# ── Locale純粋性パターン ──────────────────────────────
# ═══════════════════════════════════════════════════════
# BJJ用語二層ルール
# ───────────────────────────────────────────────────────
# Layer 1: BJJ専門用語（カタカナ・英語ともにどのlocaleでも許容）
#   → 柔術コミュニティで定着した用語。日本語に無理に訳さない。
# Layer 2: UI/ナビゲーション文言（localeに合わせて必ず翻訳）
#   → CTA、フッターリンク、フォーム等のインターフェース文言。
# ═══════════════════════════════════════════════════════

# ── Layer 1: BJJ専門用語（全locale共通で英語/カタカナ許容）──
# カタカナ表記: ディフェンス、ガード、スイープ等は日本語ページでそのまま使ってよい
# 英語表記: Guard, Mount, Submission 等はJAページの本文中で許容

BJJ_TERMS_ENGLISH = re.compile(
    r"""(?x)
    # 組織・大会
    BJJ|MMA|UFC|IBJJF|ADCC|EBI|Gi|No[-\s]?Gi|SJJIF|UAEJJF|
    # サブミッション
    Armbar|Arm[\s]?Bar|Kimura|Americana|Omoplata|Triangle|Guillotine|
    Rear[\s]?Naked[\s]?Choke|RNC|D'?Arce|Anaconda|Ezekiel|
    Gogoplata|Peruvian[\s]?Necktie|Von[\s]?Flue|Baseball[\s]?Choke|
    Bow[\s]?and[\s]?Arrow|Clock[\s]?Choke|Loop[\s]?Choke|Paper[\s]?Cutter|
    Heel[\s]?Hook|Toe[\s]?Hold|Knee[\s]?Bar|Wrist[\s]?Lock|
    Ankle[\s]?Lock|Calf[\s]?Slicer|Straight[\s]?Ankle|Outside[\s]?Heel[\s]?Hook|
    Inside[\s]?Heel[\s]?Hook|Estima[\s]?Lock|Aoki[\s]?Lock|
    # ポジション
    Guard|Mount|Side[\s]?Control|Back[\s]?Control|Half[\s]?Guard|
    Closed[\s]?Guard|Open[\s]?Guard|Butterfly[\s]?Guard|
    De[\s]La[\s]Riva|DLR|Spider[\s]?Guard|Lasso[\s]?Guard|
    X[-\s]?Guard|Rubber[\s]?Guard|Worm[\s]?Guard|
    Z[-\s]?Guard|Deep[\s]?Half|Reverse[\s]?De[\s]La[\s]Riva|RDLR|
    50[-/]50|Ashi[\s]?Garami|Saddle|Inside[\s]?Sankaku|
    Knee[\s]?on[\s]?Belly|KOB|North[-\s]?South|Turtle|Crucifix|Truck|
    Full[\s]?Mount|Back[\s]?Mount|
    # ムーブメント・アクション
    Berimbolo|Sweep|Pass|Guard[\s]?Pass|Takedown|Submission|Escape|
    Hip[\s]?Escape|Bridge|Shrimp|Sprawl|Inversion|Granby|
    Underhook|Overhook|Whizzer|Pummeling|
    Drill|Roll|Spar|Flow[\s]?Roll|Positional[\s]?Sparring|
    # グリップ・パーツ
    Lapel|Collar|Sleeve|Grip|Cross[\s]?Grip|Same[-\s]?Side[\s]?Grip|
    Pistol[\s]?Grip|Butterfly[\s]?Hook|
    Joint[\s]?Lock|Choke|Strangle|
    # コンセプト
    Pressure|Base|Posture|Frame|Hip[\s]?Movement|
    Positional[\s]?Hierarchy|Top[\s]?Game|Bottom[\s]?Game|
    Open[\s]?Mat|Comp|Competition|
    # 人名（著名選手・指導者）
    John[\s]Danaher|Marcelo[\s]Garcia|Gordon[\s]Ryan|
    Roger[\s]Gracie|Helio[\s]Gracie|Rickson[\s]Gracie|
    Marcus[\s]"?Buchecha"?|Andre[\s]Galvao|Bernardo[\s]Faria|
    Craig[\s]Jones|Mikey[\s]Musumeci|Caio[\s]Terra|Cobrinha|
    Keenan[\s]Cornelius|Lachlan[\s]Giles|
    # ブランド・サービス
    YouTube|Instagram|Facebook|Twitter|
    BJJ\s?App|BJJ\s?Wiki|
    ROYDEAN|RoyDean|
    Google|Cloudflare|CDN|
    # テクニカル（HTML/CSS等、検出対象外）
    class=|style=|href=|src=|data-|onclick=|
    https?://|www\.|\.html|\.css|\.js|\.png|\.jpg|\.svg|
    UTF-8|charset|viewport|content=|
    max-width|margin|padding|display|flex|gap|
    font-size|color|text-decoration|border|background|
    none|auto|center|wrap|nowrap|
    div|span|section|header|footer|nav|main|article|
    img|iframe|script|link|meta|
    Pro|Free|CSV|PDF|API|URL|
    Cow[\s]Face[\s]Pose|Eagle[\s]Pose|Pigeon[\s]Pose|
    Technique[\s]Map|Video[\s]Timestamps|
    Privacy[\s]Policy|About|Contact
    """,
    re.IGNORECASE,
)

# JAページで許容するカタカナBJJ用語
# （ディフェンスは防御より自然、パスガードは通過より自然、など）
BJJ_TERMS_KATAKANA = {
    # ポジション
    "ガード", "マウント", "サイドコントロール", "バックコントロール",
    "ハーフガード", "クローズドガード", "オープンガード", "バタフライガード",
    "スパイダーガード", "ラッソガード", "ラバーガード", "ワームガード",
    "デラヒーバ", "ディープハーフ", "タートル",
    # サブミッション
    "アームバー", "キムラ", "アメリカーナ", "オモプラッタ", "トライアングル",
    "ギロチン", "リアネイキドチョーク", "ダースチョーク", "アナコンダ",
    "エゼキエル", "ゴゴプラッタ", "ヒールフック", "トーホールド",
    "ニーバー", "リストロック", "アンクルロック", "カーフスライサー",
    # ムーブメント
    "スイープ", "パス", "パスガード", "テイクダウン", "サブミッション",
    "エスケープ", "ディフェンス", "オフェンス", "トランジション",
    "インバージョン", "ベリンボロ", "グランビー",
    "アンダーフック", "オーバーフック", "ウィザー", "パミリング",
    "ブリッジ", "シュリンプ", "スプロール",
    # グリップ
    "ラペル", "カラー", "スリーブ", "グリップ", "フック",
    # コンセプト
    "プレッシャー", "ベース", "ポスチャー", "フレーム",
    "トップゲーム", "ボトムゲーム", "オープンマット",
    # ドリル・スパーリング
    "ドリル", "スパーリング", "ロール", "フローロール", "ポジショナル",
    # 帯
    "ホワイトベルト", "ブルーベルト", "パープルベルト", "ブラウンベルト", "ブラックベルト",
    # Gi / No-Gi
    "ノーギ",
    # 大会
    "コンペ", "コンペティション", "トーナメント", "マッチ",
    # 体重クラス
    "ルースター", "ライトフェザー", "フェザー", "ライト",
    "ミドル", "ミディアムヘビー", "ヘビー", "スーパーヘビー", "ウルトラヘビー",
}

# ── Layer 2: UI/ナビゲーション（locale別に翻訳必須）──
# JAページで英語が残っていたらCRITICAL
JA_FORBIDDEN_ENGLISH = [
    (r"Related\s+Techniques", "関連テクニック"),
    (r"Related\s+Video", "関連動画"),
    (r"Privacy\s+Policy", "プライバシーポリシー"),
    (r">About<", "概要"),
    (r"Contact\s+Us", "お問い合わせ"),
    (r"Send(?=\s*</)", "送信"),
    (r"Your\s+Name", "お名前"),
    (r"Your\s+Email", "メールアドレス"),
    (r"Your\s+Message", "メッセージ"),
    (r"Track\s+Your\s+BJJ\s+Training", "柔術トレーニングを記録しよう"),
    (r"Free\s+forever", "ずっと無料"),
]

# ENページで検出すべき「日本語が混入している」パターン
EN_FORBIDDEN_JAPANESE = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]{2,}")

# PTページで検出すべき問題パターン
PT_FORBIDDEN_ENGLISH = [
    (r"Related\s+Techniques", "Técnicas Relacionadas"),
    (r"Related\s+Video", "Vídeo Relacionado"),
    (r"Privacy\s+Policy", "Política de Privacidade"),
    (r">About<", "Sobre"),
    (r"Contact\s+Us", "Contato"),
]

PT_FORBIDDEN_JAPANESE = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]{2,}")


# ─────────────────────────────────────────────────────
# ユーティリティ
# ─────────────────────────────────────────────────────

def extract_visible_text(html: str) -> str:
    """HTMLタグ・style・scriptを除去して可視テキストを抽出"""
    # script, style タグ内を除去
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # HTMLコメントを除去
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    # HTMLタグを除去
    text = re.sub(r"<[^>]+>", " ", text)
    # HTML entities
    text = re.sub(r"&\w+;", " ", text)
    return text


def extract_non_code_html(html: str) -> str:
    """コード・属性以外のHTMLテキスト部分を抽出（タグ内属性は除外）"""
    # HTMLコメント内を除去
    text = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    # script, style 内を除去
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", text, flags=re.DOTALL)
    # タグそのもの（属性含む）を除去
    text = re.sub(r"<[^>]+>", "\n", text)
    return text


# ─────────────────────────────────────────────────────
# チェッカー群
# ─────────────────────────────────────────────────────

class BugReport:
    def __init__(self):
        self.bugs = []  # (severity, category, file, detail, fix_hint)

    def add(self, severity: str, category: str, filepath: str, detail: str, fix_hint: str = ""):
        self.bugs.append((severity, category, filepath, detail, fix_hint))

    def count(self, severity: str = None) -> int:
        if severity:
            return sum(1 for b in self.bugs if b[0] == severity)
        return len(self.bugs)


def check_locale_purity_ja(filepath: str, html: str, report: BugReport):
    """JAページのlocale純粋性チェック"""
    visible = extract_non_code_html(html)
    for pattern, expected_ja in JA_FORBIDDEN_ENGLISH:
        matches = re.findall(pattern, visible, re.IGNORECASE)
        if matches:
            report.add(
                "CRITICAL", "LOCALE_JA",
                filepath,
                f"英語残存: '{matches[0]}' (expected: '{expected_ja}')",
                f"'{matches[0]}' → '{expected_ja}' に置換",
            )


def check_locale_purity_en(filepath: str, html: str, report: BugReport):
    """ENページのlocale純粋性チェック（日本語混入検知）"""
    visible = extract_non_code_html(html)
    matches = EN_FORBIDDEN_JAPANESE.findall(visible)
    # ホワイトリスト: 言語セレクター + 柔道固有名詞 + BJJカタカナ用語
    EN_JP_WHITELIST = {
        "日本語", "ポルトガル語", "日本語版",
        # 柔道技名（漢字）
        "一本背負投", "大外刈", "内股", "払腰", "背負投",
        "袖釣込腰", "大内刈", "小内刈", "送足払", "巴投",
        # 人名
        "今成正和",
    } | BJJ_TERMS_KATAKANA  # BJJ用語のカタカナはEN/PTページでも許容
    for m in matches:
        if len(m) <= 2:
            continue
        if m.strip() in EN_JP_WHITELIST:
            continue
        report.add(
            "CRITICAL", "LOCALE_EN",
            filepath,
            f"日本語混入: '{m[:30]}...' ({len(m)}文字)",
            "該当テキストを英語に置換",
        )


def check_locale_purity_pt(filepath: str, html: str, report: BugReport):
    """PTページのlocale純粋性チェック"""
    visible = extract_non_code_html(html)
    for pattern, expected_pt in PT_FORBIDDEN_ENGLISH:
        matches = re.findall(pattern, visible, re.IGNORECASE)
        if matches:
            report.add(
                "CRITICAL", "LOCALE_PT",
                filepath,
                f"英語残存: '{matches[0]}' (expected: '{expected_pt}')",
                f"'{matches[0]}' → '{expected_pt}' に置換",
            )
    # 日本語混入チェック
    PT_JP_WHITELIST = {
        "日本語", "ポルトガル語", "日本語版",
        "一本背負投", "大外刈", "内股", "払腰", "背負投",
        "袖釣込腰", "大内刈", "小内刈", "送足払", "巴投",
        "今成正和",
    } | BJJ_TERMS_KATAKANA
    jp_matches = PT_FORBIDDEN_JAPANESE.findall(visible)
    for m in jp_matches:
        if len(m) <= 2:
            continue
        if m.strip() in PT_JP_WHITELIST:
            continue
        report.add(
            "CRITICAL", "LOCALE_PT",
            filepath,
            f"日本語混入: '{m[:30]}...' ({len(m)}文字)",
            "該当テキストをポルトガル語に置換",
        )


def check_yoga_hidden(filepath: str, html: str, report: BugReport):
    """ヨガセクションがコメントアウトされているかチェック"""
    # yoga-box が表示されている（コメント外）場合はバグ
    if re.search(r'class=["\']yoga-box["\']', html) and "YOGA SECTION HIDDEN" not in html:
        report.add(
            "WARNING", "YOGA_VISIBLE",
            filepath,
            "ヨガセクションがコメントアウトされていない",
            "<!-- YOGA SECTION HIDDEN ... --> でラップ",
        )


def check_footer_layout(filepath: str, html: str, report: BugReport):
    """フッターのComparisons/Toolsがコンテナ内にあるかチェック"""
    # Share Bar後の構造チェック
    if "<!-- Share Bar -->" in html:
        share_bar_pos = html.index("<!-- Share Bar -->")
        after_share = html[share_bar_pos:share_bar_pos + 500]
        # コンテナdivが存在するか
        if "Comparisons" in after_share or "Tools" in after_share:
            if "max-width:860px" not in after_share and "max-width: 860px" not in after_share:
                report.add(
                    "WARNING", "FOOTER_LAYOUT",
                    filepath,
                    "Comparisons/Toolsセクションにコンテナラッパーがない",
                    "max-width:860px;margin:32px auto 0 のdivでラップ",
                )


def check_copyright_year(filepath: str, html: str, report: BugReport):
    """©年号チェック"""
    if re.search(r"&copy;\s*20(?:2[0-5]|1\d)", html):
        old_year = re.search(r"&copy;\s*(20\d{2})", html)
        if old_year:
            report.add(
                "INFO", "COPYRIGHT",
                filepath,
                f"古い著作権年号: © {old_year.group(1)} (should be {CURRENT_YEAR})",
                f"&copy; {old_year.group(1)} → &copy; {CURRENT_YEAR}",
            )


def check_empty_links(filepath: str, html: str, report: BugReport):
    """空リンク・#のみリンク検知（<script>内は除外）"""
    # scriptタグの中身を除去してからチェック（JS内の href='#'+id 等は誤検知）
    html_no_script = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    # JS動的ページ（simulator等）は href="#" を正当に使うため除外
    INTERACTIVE_PAGES = {"sparring-simulator.html", "quiz.html", "game.html"}
    basename = os.path.basename(filepath)
    if basename in INTERACTIVE_PAGES:
        return
    empty_hrefs = re.findall(r'href=["\'](?:#|)["\']', html_no_script)
    if len(empty_hrefs) > 2:  # 目次の#は許容、3つ以上なら問題
        report.add(
            "INFO", "EMPTY_LINKS",
            filepath,
            f"空リンク/# リンクが {len(empty_hrefs)} 件",
            "適切なURLまたはアンカーに修正",
        )


def check_broken_internal_links(filepath: str, html: str, lang: str, report: BugReport):
    """内部リンク切れ検知（存在しない .html ファイルへのリンク）"""
    html_no_script = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html_no_comment = re.sub(r'<!--.*?-->', '', html_no_script, flags=re.DOTALL)

    broken = []
    for href in re.findall(r'href="([^"]+\.html)"', html_no_comment):
        # 外部リンクはスキップ
        if href.startswith('http'):
            continue

        # パス解決:
        # ../en/xxx.html → en/xxx.html (正常な言語切替リンク)
        # ../xxx.html → 言語ディレクトリなし（パス不正、ただしen/xxx.htmlがあれば実害小）
        # xxx.html → 同ディレクトリ内 (lang/xxx.html)
        if '/' in href:
            parts = href.rstrip('/').split('/')
            target_file = parts[-1]
            # 言語ディレクトリが含まれるか
            if len(parts) >= 2 and parts[-2] in ("en", "ja", "pt"):
                target_lang = parts[-2]
            else:
                # ../xxx.html のような不正パス → 同言語で探す
                target_lang = lang
        else:
            target_lang = lang
            target_file = href

        target_path = WIKI_ROOT / target_lang / target_file
        if not target_path.exists():
            broken.append(href)

    if broken:
        broken_unique = sorted(set(broken))
        report.add(
            "WARNING", "BROKEN_LINK",
            filepath,
            f"リンク切れ {len(broken_unique)} 件: {', '.join(broken_unique[:3])}{'...' if len(broken_unique) > 3 else ''}",
            "リンク先ファイルを作成するか、リンクを修正",
        )


def check_bilingual_headers(filepath: str, html: str, lang: str, report: BugReport):
    """「日本語 / English」のような二言語併記ヘッダー検知"""
    patterns = [
        r"お問い合わせ\s*/\s*Contact",
        r"関連動画\s*/\s*Related\s*Video",
        r"関連テクニック\s*/\s*Related\s*Techniques",
        r"送信\s*/\s*Send",
    ]
    for pat in patterns:
        if re.search(pat, html, re.IGNORECASE):
            report.add(
                "CRITICAL", f"BILINGUAL_{lang.upper()}",
                filepath,
                f"二言語併記: '{pat}' が残存",
                "locale に応じた単一言語テキストに修正",
            )


def check_seo_h1(filepath: str, html: str, report: BugReport):
    """H1タグの存在チェック — SEOの基本要素"""
    h1_matches = re.findall(r"<h1[^>]*>", html, re.IGNORECASE)
    if len(h1_matches) == 0:
        report.add(
            "WARNING", "SEO_NO_H1",
            filepath,
            "H1タグが存在しない（SEO必須要素）",
            "<h1>ページタイトル</h1> を追加",
        )
    elif len(h1_matches) > 1:
        report.add(
            "INFO", "SEO_MULTI_H1",
            filepath,
            f"H1タグが {len(h1_matches)} 個ある（推奨: 1個）",
            "H1は1つに統一し、残りはH2に変更",
        )


def check_seo_meta_description(filepath: str, html: str, report: BugReport):
    """meta descriptionの品質チェック"""
    meta_match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']',
        html, re.IGNORECASE
    )
    if not meta_match:
        # content="" が先に来るパターンも検出
        meta_match = re.search(
            r'<meta\s+content=["\']([^"\']*)["\'][\s]+name=["\']description["\']',
            html, re.IGNORECASE
        )

    if not meta_match:
        report.add(
            "WARNING", "SEO_NO_META_DESC",
            filepath,
            "meta descriptionが存在しない",
            '<meta name="description" content="ページの説明文"> を追加',
        )
        return

    desc = meta_match.group(1).strip()
    desc_len = len(desc)

    if desc_len == 0:
        report.add(
            "WARNING", "SEO_EMPTY_META_DESC",
            filepath,
            "meta descriptionが空",
            "50〜160文字の説明文を設定",
        )
    elif desc_len < 50:
        report.add(
            "INFO", "SEO_SHORT_META_DESC",
            filepath,
            f"meta descriptionが短すぎる ({desc_len}文字 < 50文字): '{desc[:40]}...'",
            "50〜160文字の説明文に拡充",
        )
    elif desc_len > 160:
        report.add(
            "INFO", "SEO_LONG_META_DESC",
            filepath,
            f"meta descriptionが長すぎる ({desc_len}文字 > 160文字)",
            "160文字以内にトリミング（検索結果で途切れる）",
        )


def check_seo_canonical(filepath: str, html: str, report: BugReport):
    """canonical URLの存在チェック"""
    canonical_match = re.search(
        r'<link\s+rel=["\']canonical["\']', html, re.IGNORECASE
    )
    if not canonical_match:
        report.add(
            "INFO", "SEO_NO_CANONICAL",
            filepath,
            "canonical URLが未設定（重複コンテンツ防止に推奨）",
            '<link rel="canonical" href="https://wiki.bjj-app.net/lang/page.html"> を追加',
        )


def check_mixed_cta_language(filepath: str, html: str, lang: str, report: BugReport):
    """CTAボタンの言語がlocaleと不一致"""
    if lang == "ja":
        # JAページで英語CTAが残存
        if re.search(r"Start\s+Free|Sign\s+Up\s+Free|Get\s+Started|Try\s+BJJ\s+App\s+Free|Track\s+Your\s+BJJ\s+Progress", html, re.IGNORECASE):
            # floating CTA / pillar page CTA
            report.add(
                "WARNING", "CTA_LANG",
                filepath,
                "JAページに英語CTA ('Start Free' / 'Try BJJ App Free' 等) が残存",
                "「無料で始める」等の日本語CTAに修正",
            )
    elif lang == "pt":
        if re.search(r"Start\s+Free|Sign\s+Up\s+Free|Get\s+Started", html, re.IGNORECASE):
            report.add(
                "WARNING", "CTA_LANG",
                filepath,
                "PTページに英語CTA ('Start Free' 等) が残存",
                "「Comece Grátis」等のPT語CTAに修正",
            )


# ─────────────────────────────────────────────────────
# メインスキャナ
# ─────────────────────────────────────────────────────

def scan_all(langs: list[str] = None, fix_hint: bool = False) -> BugReport:
    """全ページスキャン"""
    if langs is None:
        langs = LANGUAGES

    report = BugReport()
    total_files = 0

    for lang in langs:
        lang_dir = WIKI_ROOT / lang
        if not lang_dir.exists():
            continue

        html_files = sorted(lang_dir.glob("*.html"))
        for fpath in html_files:
            total_files += 1
            try:
                html = fpath.read_text(encoding="utf-8")
            except Exception as e:
                report.add("ERROR", "READ_FAIL", str(fpath), str(e))
                continue

            rel_path = f"{lang}/{fpath.name}"

            # 共通チェック
            check_yoga_hidden(rel_path, html, report)
            check_footer_layout(rel_path, html, report)
            check_copyright_year(rel_path, html, report)
            check_empty_links(rel_path, html, report)
            check_bilingual_headers(rel_path, html, lang, report)
            check_mixed_cta_language(rel_path, html, lang, report)
            check_broken_internal_links(rel_path, html, lang, report)

            # SEOチェック
            check_seo_h1(rel_path, html, report)
            check_seo_meta_description(rel_path, html, report)
            check_seo_canonical(rel_path, html, report)

            # 言語別チェック
            if lang == "ja":
                check_locale_purity_ja(rel_path, html, report)
            elif lang == "en":
                check_locale_purity_en(rel_path, html, report)
            elif lang == "pt":
                check_locale_purity_pt(rel_path, html, report)

    return report, total_files


# ─────────────────────────────────────────────────────
# 出力
# ─────────────────────────────────────────────────────

SEVERITY_COLORS = {
    "CRITICAL": "\033[91m",  # red
    "WARNING": "\033[93m",   # yellow
    "INFO": "\033[94m",      # blue
    "ERROR": "\033[95m",     # magenta
}
RESET = "\033[0m"


def print_report(report: BugReport, total_files: int, fix_hint: bool = False):
    """レポート出力"""
    # サマリー
    crit = report.count("CRITICAL")
    warn = report.count("WARNING")
    info = report.count("INFO")

    print(f"\n{'='*60}")
    print(f"🔍 Hidden Bug Detector — スキャン結果")
    print(f"{'='*60}")
    print(f"  スキャン対象: {total_files} ファイル")
    print(f"  🔴 CRITICAL: {crit}")
    print(f"  🟡 WARNING:  {warn}")
    print(f"  🔵 INFO:     {info}")
    print(f"  合計: {report.count()} 件")

    if report.count() == 0:
        print(f"\n  ✅ 隠れバグなし！全ページクリーン。")
        print(f"{'='*60}\n")
        return

    # カテゴリ別集計
    categories = defaultdict(list)
    for sev, cat, fpath, detail, hint in report.bugs:
        categories[cat].append((sev, fpath, detail, hint))

    for cat, items in sorted(categories.items()):
        print(f"\n  📂 {cat} ({len(items)} 件)")
        print(f"  {'─'*50}")
        # 最大10件表示、残りはサマリー
        shown = items[:10]
        for sev, fpath, detail, hint in shown:
            color = SEVERITY_COLORS.get(sev, "")
            print(f"    {color}[{sev}]{RESET} {fpath}")
            print(f"           {detail}")
            if fix_hint and hint:
                print(f"           💡 {hint}")
        if len(items) > 10:
            print(f"    ... 他 {len(items) - 10} 件")

    print(f"\n{'='*60}\n")


def write_report_file(report: BugReport, total_files: int):
    """レポートファイル出力"""
    report_path = WIKI_ROOT / "hidden_bugs_report.txt"
    lines = []
    lines.append(f"Hidden Bug Detector Report")
    lines.append(f"Scanned: {total_files} files")
    lines.append(f"CRITICAL: {report.count('CRITICAL')}")
    lines.append(f"WARNING: {report.count('WARNING')}")
    lines.append(f"INFO: {report.count('INFO')}")
    lines.append(f"Total: {report.count()}")
    lines.append("")

    for sev, cat, fpath, detail, hint in report.bugs:
        lines.append(f"[{sev}] [{cat}] {fpath}: {detail}")
        if hint:
            lines.append(f"  FIX: {hint}")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"📄 レポート保存: {report_path}")


# ─────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Wiki Hidden Bug Detector")
    parser.add_argument("--lang", choices=ALL_LANGUAGES, help="特定言語のみスキャン（pt含む）")
    parser.add_argument("--fix-hint", action="store_true", help="修正ヒント付き出力")
    parser.add_argument("--ci", action="store_true", help="CI用（exitcode=CRITICAL数）")
    args = parser.parse_args()

    langs = [args.lang] if args.lang else None
    report, total_files = scan_all(langs, args.fix_hint)

    print_report(report, total_files, args.fix_hint)
    write_report_file(report, total_files)

    if args.ci:
        sys.exit(report.count("CRITICAL"))


if __name__ == "__main__":
    main()
