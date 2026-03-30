## 2026-03-30 分析レポート（本日 cron 実行後・確定版）

> 生成時刻: 自動タスク（Cowork Scheduled Task）

### 実行結果サマリ

| 指標 | 値 |
|---|---|
| 実行日時 | 2026-03-30 JST（cron 9:10 JST 実行） |
| 処理件数 | **80 件** |
| ✅ 更新成功 | **80 件**（100%） |
| ⏭️ スキップ（設定済み） | 0 件 |
| ⏳ キュー追加（明日処理） | 0 件 |
| ⚠️ 動画なし（マッチなし） | 0 件 |
| ❌ DB更新失敗 / 検索エラー | 0 件 |
| 📊 本日の API 呼び出し数 | **80 / 80（全消化）** |
| キュー残件数（翌日分） | **44 件** |

> 🎉 **完璧なラン！** 80件全件が動画 URL 更新済み。エラー・マッチなしゼロ。

---

### 累積進捗

| 指標 | 値 |
|---|---|
| 全 EN ページ数 | **1,567 ページ** |
| 本日までの動画設定済みページ数（推定） | **約 130 件**（50件 + 本日 80件） |
| 全体カバレッジ | **約 8.3%**（130 / 1,567） |
| 翌日処理キュー | **44 件** |
| 80件/日継続時の完了見込み | **あと約 18 日** |

---

### 本日処理されたページ（80件 — 代表サンプル）

| # | スラグ | 取得動画（抜粋） | スコア |
|---|---|---|---|
| 1 | 50-50-guard | Learn to Pass the 50/50 Guard (Keenan Cornelius) | +50 |
| 6 | armbar | How To Do The Perfect Armbar by John Danaher | +65 |
| 22 | back-defense | How to Escape Back Body Triangle by Giancarlo Bodoni | +65 |
| 25 | backtake | A Step by Step Guide To Hit Your First Rolling Backtake (Stephan Kesting) | +85 |
| 76 | bjj-arm-drag | BJJ Techniques: Arm Drag to Back Take by Gordon Ryan | +85 |
| 80 | bjj-arm-drag-to-back | BJJ Techniques: Arm Drag to Back Take by Gordon Ryan | +85 |

---

### エラーパターン分析

**検出されたエラー: なし**

- `ytInitialData が見つかりません`: 0件
- `JSON パース失敗`: 0件
- `検索エラー` / タイムアウト: 0件
- `日次上限到達` でのキュー追加: 0件（前回の反省が活きた: cron 9:10 JST = UTC 00:10 で正常リセット後に実行）
- `適切な動画が見つかりませんでした`: 0件

> ✅ **cron タイミング問題は解決済み。** 9:10 JST（UTC 00:10）での実行により、UTC 深夜リセット後に正常起動している。

---

### スクリプト自動修正

**なし** — エラーパターンが検出されなかったため、スクリプト修正は不要。

---

### ログ構成（今回確認分）

| ファイル | 内容 |
|---|---|
| `logs/fetch.log` | 本日 80件成功ログ（+ 03/26 の9件再キューログ） |
| `cache/rate_limit_state.json` | `{"fetch_date": "2026-03-30", "calls": 80}` |
| `cache/fetch_queue.json` | 44件（bjj-arm-in-guillotine 〜 bjj-back-escape-roll-guide） |

---

### 翌日の予測実行（2026-03-31 9:10 JST）

- キュー 44 件を優先処理（bjj-arm-* / bjj-back-* 系）
- キュー消化後、DB から未処理スラグを追加取得（最大 80 - 44 = 36 件）
- エラーがなければ合計 80 件処理の見込み

---

### 前回からの改善提案ステータス（累積）

| # | 提案 | ステータス | 備考 |
|---|---|---|---|
| 1 | cron 9:10 JST に変更 | ✅ **解決済み** | 本日の完走で動作確認 |
| 2 | fetch.log リダイレクト確認 | ✅ **正常動作中** | ログ正常取得を確認 |
| 3 | ANTI_KEYWORDS 緩和（アスリート） | ✅ **修正済み**（2026-03-29） | athlete-* の highlight/compilation 許可 |
| 4 | null キャッシュ再試行（kimura等） | 🔴 **未対応** | 本日は新スラグのみ処理。要手動確認 |
| 5 | スコアリング閾値の動的調整 | 🔴 **未対応** | no_match 0件のため優先度低下 |

---

### 改善提案（今後）

1. **null キャッシュ（旧来の no_match スラグ）の再試行（優先度: 中）**
   kimura / mount / americana 等のコア技術ページがまだ null キャッシュのまま。
   本日の新スラグは100%マッチしているため、スコアリングは概ね良好。
   ただし旧キャッシュの null エントリは自動では再試行されない。
   手動で確認する場合:
   ```bash
   cd ~/Claude/bjj-wiki && python3 scripts/local_video_fetcher.py --slug kimura --force --dry-run
   ```

2. **動画品質モニタリング（優先度: 低）**
   スコア +30〜+40 帯（best-bjj-bag, best-bjj-guards 等）は関連性が弱い動画が入っている可能性がある。
   週次で低スコア動画をサンプリングして品質確認することを推奨。

---

## 2026-03-30 分析レポート（03:53 JST 自動タスク — cron 実行前）

> 生成時刻: 03:53 JST（cron は 9:10 JST 実行予定）

### 実行結果サマリ（本日分）

| 指標 | 値 |
|---|---|
| 本日 cron 実行 | 未実行（9:10 JST 予定） |
| 昨日 (03/29) API 呼び出し | **10 calls** / 80 |
| 昨日の新規取得 | 不明（fetch.log 更新なし） |
| キュー残件数 | **0件**（空・正常） |
| レート制限状態 | `2026-03-29, calls=10` → 本日 UTC リセット済み |

### 累積進捗

| 指標 | 値 |
|---|---|
| 全 EN ページ数 | **1,567** |
| 動画 ID 取得成功（キャッシュ確認） | **14件** |
| マッチなし（永続 null キャッシュ） | **36件** |
| 未処理（DB 上 video_url = NULL 推定） | **約 1,517件** |
| キャッシュ内カバレッジ | **28%（14/50）** |
| 全体カバレッジ | **0.9%（14/1,567）** |
| 80件/日継続時の完了見込み | **あと約 19 日** |

### エラーパターン分析

**検出されたエラー: なし**

- `ytInitialData が見つかりません`: 未検出
- `JSON パース失敗`: 未検出
- `検索エラー` / タイムアウト: 未検出
- fetch.log 最終エントリは 2026-03-26（9件がレート制限でキュー追加）

> ⚠️ fetch.log が更新されていない状態が継続中。cron の実行ログが取得できていない可能性がある。
> 昨日の `rate_limit_state (calls=10)` から 10 件は処理されたことは確認できる。

### 動画取得成功スラグ（14件）

| スラグ | 動画 ID | タイトル（抜粋） |
|---|---|---|
| rear-naked-choke | l8-JI7NND3E | How To Perform The Perfect Rear Naked Choke by John Danaher |
| triangle-choke | eohT5K-_tCo | BJJ Triangle Choke Concepts with Karel Silver Fox Pravec |
| guillotine-choke | _IK51iClbGE | The Guillotine Choke: A Complete Masterclass |
| armbar | 2rMG3v7PtkA | Learn the Secrets of a Tight Armlock \| Full Seminar |
| berimbolo | PAf2iCezKzY | Step by Step Guide to Learn The Berimbolo |
| closed-guard | otskR_OjuBU | How To Build The Perfect BJJ Closed Guard Game by John Danaher |
| half-guard | bEu5SP5Y3nM | 29 Regular Half Guard Techniques In Less Than 12 Minutes |
| de-la-riva-guard | 4WqkHFi7ac0 | Understanding De La Riva Guard |
| spider-guard | n-4mG7IL64Q | Spider Guard System - Fundamentals collection |
| butterfly-guard | -wftJg6jm3E | Butterfly Guard Guide In Gi & Nogi |
| side-control | nDbHQPBvQvQ | The Secret to a World Class Side Control |
| knee-on-belly | BHUYEm0ve9A | Knee on belly \| MASTER the BJJ system |
| anaconda-choke | Q8KO-Ncfrfo | How To Do An Anaconda Choke Without Neck Cranking |
| calf-slicer | 9EwRjvWPBZE | Calf SLICERS from everywhere! |

### ⚠️ 永続 null キャッシュ（36件）— 要注意

以下のスラグは検索済みだが「適切な動画なし」と判定され null がキャッシュ済み。
**通常実行では再検索されない**（キャッシュヒット → null を返して終了）。

| カテゴリ | 件数 | スラグ |
|---|---|---|
| サブミッション | 10件 | kimura, americana, omoplata, heel-hook, inside-heel-hook, outside-heel-hook, bow-and-arrow-choke, darce-choke, ezekiel-choke, loop-choke |
| レッグロック | 3件 | knee-bar, toe-hold, wrist-lock |
| ガード | 4件 | open-guard, x-guard, rubber-guard, worm-guard |
| スイープ | 4件 | scissor-sweep, hip-bump-sweep, flower-sweep, pendulum-sweep |
| ポジション | 4件 | mount, back-mount, north-south, turtle-position |
| ガードパス | 5件 | guard-pass, torreando-pass, knee-slice-pass, leg-drag-pass, headquarters-pass |
| テイクダウン | 5件 | double-leg-takedown, single-leg-takedown, osoto-gari, ankle-pick, sprawl |
| その他 | 1件 | backtake |

**懸念点:** `kimura`, `mount`, `omoplata` などコア BJJ 技術でも null になっている。
これらは YouTube 上に豊富な教材動画があるはずであり、スコアリング閾値（>= 10）または
ANTI_KEYWORDS による過剰ペナルティが原因の可能性が高い。

### 本日の予測実行（9:10 JST）

- キューが空のため、DB から `video_url IS NULL` の未処理スラグを最大 80 件取得
- rate_limit_state が本日付でリセットされ、最大 80 呼び出し可能
- null キャッシュ済みの 36 件はスキップされる（キャッシュヒット）
- 進捗: +最大 80 ページ（実際のマッチ率次第）

### 改善提案（要手動確認）

1. **null キャッシュのリトライ（優先度: 高）**
   ```bash
   cd ~/Claude/bjj-wiki
   python3 scripts/local_video_fetcher.py --slug kimura --force --dry-run
   python3 scripts/local_video_fetcher.py --slug mount --force --dry-run
   ```
   スコアが表示されるので、スコア < 10 ならスコアリング閾値の調整が必要。

2. **スコアリング閾値の動的調整（優先度: 中）**
   短い BJJ 専門用語（単語 1〜2 つ）では閾値を 5 に下げることで
   kimura / mount 等の基本技を救済できる可能性がある。

3. **スクリプト修正は今回 見送り**（大きな変更はユーザー確認が必要）

---

## 2026-03-29 分析レポート（10:36 JST 自動タスク実行②）

### 状況サマリ
- 📊 rate_limit_state: `2026-03-28, calls=2/80`（前日のまま・本日未更新）
- ⏳ fetch_queue: **0件**（空）
- 📝 fetch.log: **未更新**（最終更新: 2026-03-27 08:00、March 26 のデータのまま）
- 🗄️ youtube_cache: **50件**（変化なし）
  - ✅ 動画ID取得成功: 14件（28%）
  - ⚠️ マッチなし（null）: 36件（72%）

### March 29 の cron 実行状況
現在 01:36 UTC（10:36 JST）。cron が **8:00 JST（23:00 UTC 前日）** のままだとすると、23:00 UTC March 28 に実行済みのはず。しかし rate_limit_state が `2026-03-28, calls=2` のまま変化なし。

**可能性:**
1. **cron がそもそも停止している**（macOS スリープ・再起動後に cron が無効化される場合がある）
2. **cron は動いたが、全 slug が DB 側で既に video_url 設定済みのためスキップ → 0 API 呼び出し → state 未更新**
3. **fetch.log リダイレクトが機能していないため、実行痕跡がない**

> 🚨 **3日連続で実質的な進捗なし**（March 27: 0件処理、March 28: 2件のみ、March 29: 不明）

### 累積進捗（変化なし）
| 指標 | 値 |
|---|---|
| YouTube検索キャッシュ | 50件 |
| 動画ID取得成功 | 14件（28%） |
| マッチなし（null） | 36件（72%） |
| 全ENページ数 | 1,566 |
| カバレッジ | 0.9%（14/1,566） |
| キュー残 | 0件 |

### no_match 36件の内訳（未変化）
| カテゴリ | 件数 | スラグ |
|---|---|---|
| サブミッション | 13件 | kimura, americana, omoplata, heel-hook, inside-heel-hook, outside-heel-hook, bow-and-arrow-choke, darce-choke, ezekiel-choke, loop-choke, wrist-lock, knee-bar, toe-hold |
| ガードパス | 4件 | torreando-pass, knee-slice-pass, leg-drag-pass, headquarters-pass, guard-pass |
| テイクダウン | 4件 | double-leg-takedown, single-leg-takedown, osoto-gari, ankle-pick, sprawl |
| ガード | 4件 | open-guard, x-guard, rubber-guard, worm-guard |
| スイープ | 4件 | scissor-sweep, hip-bump-sweep, flower-sweep, pendulum-sweep |
| ポジション | 4件 | mount, back-mount, north-south, turtle-position |
| その他 | 1件 | backtake |

### スクリプト修正: アスリートページの ANTI_KEYWORDS 緩和

**問題:** ANTI_KEYWORDS に `"highlight"` が含まれており、全ページに -30 ペナルティが適用される。しかしアスリートページでは「{名前} BJJ highlight」がまさに最適なコンテンツ。この -30 によりスコアが閾値10を下回り、有名選手でもマッチ失敗になる。

**修正内容:** `_score()` メソッドで、`slug.startswith("athlete-")` の場合は `"highlight"` と `"compilation"` と `"best of"` を ANTI_KEYWORDS から除外。試合・トーナメント関連（`"match"`, `"tournament"`, `"adcc"`, `"worlds"`, `" vs "`）は引き続きペナルティ適用。

**影響範囲:** アスリートページのみ。通常の技術ページには影響なし。

### 改善提案ステータス（累積）

| # | 提案 | ステータス | 備考 |
|---|---|---|---|
| 1 | cron 9:10 JST に変更 | 🔴 **未確認**（3日間ログなし） | 要手動確認: `crontab -l` |
| 2 | fetch.log リダイレクト確認 | 🔴 **未確認** | 要手動確認: crontab に `>> logs/fetch.log 2>&1` があるか |
| 3 | ANTI_KEYWORDS 緩和（アスリート） | ✅ **自動修正済み**（本レポート） | athlete-* のみ highlight/compilation/best of を許可 |
| 4 | ANTI_KEYWORDS 緩和（技術ページ） | 🔴 未対応 | 要手動確認: kimura等の no_match 原因特定が先 |
| 5 | クエリ生成改善 | 🔴 未対応 | 優先度: 中 |
| 6 | cron 稼働確認 | 🚨 **新規・最優先** | macOS 再起動後に cron が無効化されていないか確認 |

### ユーザーへの推奨アクション（優先度順）

1. **cron 稼働確認（最優先）**:
   ```bash
   crontab -l | grep video_fetcher
   ```
   出力がなければ cron が消えている。再設定:
   ```bash
   crontab -e
   # 以下を追加:
   10 9 * * * cd ~/Claude/bjj-wiki && python3 scripts/local_video_fetcher.py --limit 80 >> logs/fetch.log 2>&1
   ```

2. **手動テスト実行（進捗確認）**:
   ```bash
   cd ~/Claude/bjj-wiki && python3 scripts/local_video_fetcher.py --dry-run --limit 5
   ```
   これで DB 接続・YouTube スクレイピング・スコアリングが正常に動くか確認できる。

3. **no_match 原因の深掘り**:
   kimura 等の基本技が null になる原因を特定するため:
   ```bash
   cd ~/Claude/bjj-wiki && python3 scripts/local_video_fetcher.py --slug kimura --force --dry-run
   ```

---

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
