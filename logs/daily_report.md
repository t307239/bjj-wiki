## 2026-03-29 分析レポート（00:26 JST 自動タスク実行）

### 状況サマリ
- 📊 rate_limit_state: `2026-03-28, calls=2/80`（前日）
- ⏳ fetch_queue: **0件**（空）
- 📝 fetch.log: **未更新**（最終更新: 2026-03-27 08:00、March 26 のデータのまま）
- 🗄️ youtube_cache: **50件**（変化なし）
  - ✅ 動画ID取得成功: 14件（28%）
  - ⚠️ マッチなし（null）: 36件（72%）

### March 28 の実行分析
rate_limit_state が `2026-03-28, calls=2` に更新されているため、3月28日にスクリプトが実行されたことは確認できる。

**しかし以下の異常あり:**
1. **fetch.log が更新されていない** — cron の stdout リダイレクト（`>> logs/fetch.log 2>&1`）が機能していないか、手動実行された可能性
2. **2 API calls で 9件のキューが空に** — 9件中7件がスキップされた理由が不明
   - キャッシュにあったのは2件のみ（back-mount, backtake → 両方 null）
   - 残り7件（athlete-rafael-lovato-jr, athlete-rafael-mendes, athlete-romulo-barral, athlete-xande-ribeiro-2, athletes, back-defense, back-take）はキャッシュにも存在しない
   - 可能性: ① DB側で video_url が既に設定済み ② 手動でキューをクリア ③ スクリプトがエラーで途中終了
3. **youtube_cache が50件のまま** — 新規キャッシュエントリなし。2件のAPI呼び出し結果がキャッシュされていない

### March 29 の cron 未実行
現在時刻 00:26 JST。cron が 9:10 JST に設定されていれば、本日分はまだ実行されていない。
fetch.log が更新されているかを **本日 10:00 JST 以降に確認する必要あり**。

### 累積進捗（前回と変化なし）
| 指標 | 値 |
|---|---|
| YouTube検索キャッシュ | 50件 |
| 動画ID取得成功 | 14件（28%） |
| マッチなし（null） | 36件（72%） |
| 全ENページ数 | ~1,566 |
| カバレッジ | ~0.9%（14/1,566） |
| キュー残 | 0件 |

### 前回レポート（03/27）からの改善提案ステータス

| # | 提案 | ステータス |
|---|---|---|
| 1 | cron 9:10 JST に変更 | ⚠️ 未確認（fetch.log が更新されておらず検証不可） |
| 2 | ANTI_KEYWORDS 過剰フィルタ見直し | 🔴 未対応（no_match 72% のまま） |
| 3 | クエリ生成ロジック改善 | 🔴 未対応 |

### 改善提案（継続 + 新規）

1. **🚨 [緊急] fetch.log キャプチャ確認（優先度: 最高）**
   cron が正しく `>> logs/fetch.log 2>&1` にリダイレクトしているか確認:
   ```bash
   crontab -l | grep video_fetcher
   ```
   もし `>>` が付いていなければ追加する。ログなしでは日次分析が不可能。

2. **🚨 [緊急] March 28 実行内容の調査（優先度: 高）**
   9件のキューが2 API呼び出しで空になった理由を特定するため、次回実行時に `--dry-run` で確認:
   ```bash
   python3 scripts/local_video_fetcher.py --dry-run --limit 10
   ```
   DB側の video_url 状態（既に他プロセスで設定済みか）を確認する必要がある。

3. **[継続] ANTI_KEYWORDS フィルタ緩和（優先度: 高）**
   no_match 72% の主因。前回レポートで分析済み:
   - `"highlight"` が ANTI_KEYWORDS にあるため、アスリートページの `"{名前} BJJ"` 検索でハイライト動画が全て除外される
   - アスリートページ向けに `ANTI_KEYWORDS` を緩和するか、別のフィルタセットを使う修正が必要
   - **自動修正は今回見送り**（影響範囲が大きく、ユーザー確認が望ましい）

4. **[継続] クエリ生成改善（優先度: 中）**
   基本技（kimura, americana, omoplata）が no_match になっている問題は未解決。

---

## 2026-03-27 分析レポート（08:00 JST cronジョブ実行後・確定版）

### 本日の実行結果（fetch.log より・08:00 JST 実行）
- ✅ 更新: **0件**
- ⚠️ 動画なし（マッチなし）: **0件**
- ❌ エラー: **0件**
- ⏳ キュー追加: **9件**（全件再キュー）
- 📊 API使用: **80/80**（前日残留・リセット未実施）

> 🚨 **根本原因判明: cronタイミングとUTC日付リセットの不整合**
> `local_video_fetcher.py` のレート制限はUTC日付でリセットする。
> JST 8:00 = UTC 23:00（**前日**）のため、cronが8時に実行された時点ではまだ
> `fetch_date: 2026-03-26` のまま（80/80）でリセットされない。
> → **キュー9件が全て再キューされ、本日の処理は実質ゼロ**。
> 修正方法: cronを **9:10 JST（= UTC 00:10）以降** に変更する。
> 例: `10 9 * * * cd ~/Claude/bjj-wiki && python3 scripts/local_video_fetcher.py --limit 50 >> logs/fetch.log 2>&1`

### 累積進捗（youtube_cache.json 解析より）
- YouTube検索キャッシュ: **50件処理済み**
  - ✅ 動画ID取得成功: **14件 / 50件（28%）**
  - ⚠️ マッチなし（no_match）: **36件 / 50件（72%）**
- 全HTMLページ: **1,566ページ（EN）+ 1,566ページ（JA）**

### no_match の傾向分析（36件）
| カテゴリ | 件数 | 代表スラグ |
|---|---|---|
| サブミッション技術 | 13件 | kimura, americana, omoplata, heel-hook, bow-and-arrow-choke... |
| ガードパス | 5件 | torreando-pass, knee-slice-pass, leg-drag-pass... |
| テイクダウン | 5件 | double-leg-takedown, single-leg-takedown, osoto-gari... |
| ガードシステム | 4件 | open-guard, x-guard, rubber-guard, worm-guard |
| スイープ | 4件 | scissor-sweep, hip-bump-sweep, flower-sweep, pendulum-sweep |
| ポジション | 4件 | mount, back-mount, north-south, turtle-position |
| その他 | 1件 | backtake |

**分析コメント**:
- サブミッション（kimura, americana等）は検索クエリ「kimura BJJ tutorial」で豊富に動画があるはず。ANTI_KEYWORDSフィルタが過剰に除外している可能性が高い。
- ポジション系（mount, back-mount）は一般的すぎて検索精度が低い可能性。「BJJ back mount control tutorial」など具体的なクエリが有効。
- ガードパス系はスラグ名がそのままでは認識されにくい（torreando → "torreando pass BJJ"形式に変換が必要）。

### 改善提案

1. **🚨 [緊急] cronタイミング修正（優先度: 最高）**
   `crontab -e` でcronを JST 9:10 以降に変更:
   ```
   10 9 * * * cd ~/Claude/bjj-wiki && python3 scripts/local_video_fetcher.py --limit 50 >> logs/fetch.log 2>&1
   ```
   これにより UTC 00:10 実行 → レート制限が正常にリセット → 毎日80件処理可能になる。

2. **ANTI_KEYWORDS 過剰フィルタの見直し（優先度: 高）**
   no_matchが36/50件（72%）という高い割合は、kimura/americana等の基本技すら動画がヒットしていないことを示す。ANTI_KEYWORDSのリストを確認し、過剰に除外していないか検証する。

3. **クエリ生成ロジックの改善（優先度: 中）**
   - スラグ `torreando-pass` → `"torreando pass BJJ tutorial"` のように動的に変換
   - スラグ `kimura` → `"kimura BJJ technique tutorial"` で検索精度向上
   - ガード系: `"x guard BJJ complete guide"` など完全なフレーズで検索

---

## 2026-03-27 分析レポート（05:01 JST・cronジョブ実行前の暫定版）

### 本日の実行状況
> ⚠️ **fetch.log 未検出**: `logs/` ディレクトリが存在しなかったため、本日のcronジョブの stdout ログは記録されていない。
> スクリプト (`local_video_fetcher.py`) は stdout に出力するのみで、ファイルへの自動保存機能を持たない。
> `rate_limit_state.json` の日付が `2026-03-26` のままであるため、**本日 (2026-03-27) のcron実行はまだ行われていない**か、実行されても rate_limit_state が更新されていない可能性がある。

### 前日 (2026-03-26) の実行結果（rate_limit_state.json より）
- 📊 API使用: **80/80**（日次上限を全消化）
- ⏳ キュー追加: **9件**（翌日処理待ち）

### 本日 (2026-03-27) のキュー内容
キューに残っている9件の内訳:
| カテゴリ | 件数 | スラグ例 |
|---|---|---|
| athlete-* | 4件 | rafael-lovato-jr, rafael-mendes, romulo-barral, xande-ribeiro-2 |
| インデックス | 1件 | athletes（一覧ページ） |
| 技術系 | 4件 | back-defense, back-mount, back-take, backtake |

### 累積進捗（HTMLファイル解析より）
- 動画設定済み: **50件 / 1,566ページ（3.2%）**
- コンテンツタイプ別カバレッジ:
  - Technique: 50/264 (19%) ✅ 最も進んでいる
  - Athlete_Bio: 0/32 (0%) 🔴 全未対応
  - Concept_Strategy: 0/1,008 (0%) 🔴 最大ボリューム・全未対応
  - Equipment_Gear: 0/121 (0%) 🔴 全未対応
  - Drill: 0/92 (0%) 🔴 全未対応

### マッチ失敗の傾向（キュー・HTMLファイル分析より）
- **athlete-* スラグ**: 25ページ中0件が動画設定済み（未処理）
  - キューにも athlete-rafael-lovato-jr 等が残留している
- **back-* スラグ**: back-take / back-control / back-defense の3件がキュー残留
  - 「back take BJJ」など汎用すぎてANTI_KEYWORDSフィルタで弾かれている可能性

### 改善提案

1. **ログファイル自動保存の追加 (優先度: 高)**
   cronジョブのコマンドを以下に変更してログを永続化する:
   ```bash
   cd ~/Claude/bjj-wiki && python3 scripts/local_video_fetcher.py --limit 50 >> logs/fetch.log 2>&1
   ```
   これにより次回の分析から実行結果を正確にトレースできる。

2. **athlete-* 専用クエリ戦略 (優先度: 高)**
   現在 athlete-* ページは 25件中0件が設定済み。選手名でのYouTube検索は
   「名前 BJJ highlight」または「名前 grappling」形式が有効。
   スクリプトの検索クエリに `"{選手名} BJJ highlight"` を追加することを推奨。
   キューにあるrafael-mendes, rafael-lovato-jr等は知名度が高いため動画は豊富なはず。

3. **Concept_Strategy の優先度見直し (優先度: 中)**
   1,008件ある Concept_Strategy ページは全て動画未設定。
   1日80件の上限で消化するには最低13日かかる。
   「bjj 〇〇 explained」「〇〇 tutorial」クエリで検索精度が上がる可能性がある。
   まず上位50件（SEOスコア高）を優先処理するようスクリプトに優先度フィルタを追加検討。

---

<!-- このファイルは bjj-wiki-video-analysis スケジュールタスクにより自動生成 -->
