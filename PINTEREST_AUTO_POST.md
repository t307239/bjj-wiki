# Pinterest 自動投稿スクリプト

## 概要
BJJ Wikiの英語HTMLページを自動的にスキャンし、最新記事をPinterestに投稿するスクリプトです。

## ファイル構成

### スクリプト
- **`scripts/auto_post_pinterest.py`** (233行)
  - `/en/` ディレクトリから最新のHTMLファイルをスキャン
  - `<title>` と `<meta name="description">` を抽出
  - Pinterest API v5でピンを作成
  - 投稿済みページの重複投稿を防止（`already_posted_pinterest.txt`）
  - Telegram通知で投稿結果を報告

### 投稿済み管理
- **`scripts/already_posted_pinterest.txt`**
  - 投稿済みのページスラッグを行ごとに記録
  - スクリプト実行時に自動更新
  - 重複投稿を防止

### GitHub Actions ワークフロー
- **`.github/workflows/auto_post_pinterest.yml`** (38行)
  - スケジュール: 毎日 JST 10:00 (UTC 01:00)
  - 手動実行対応 (`workflow_dispatch`)
  - 失敗時にTelegram通知

## 主要機能

### 1. HTMLスキャン＆パース
```python
# /en/ ディレクトリの全HTMLファイルを修正時刻でソート（最新順）
html_files = sorted(
    en_dir.glob("*.html"),
    key=lambda f: f.stat().st_mtime,
    reverse=True
)

# titleとdescriptionを抽出
title, description = extract_title_and_desc(html_content)
```

### 2. Pinterest API v5投稿
```python
def post_to_pinterest(title: str, description: str, link: str, board_id: str) -> bool:
    payload = {
        "board_id": board_id,
        "title": title[:100],
        "description": description[:500],
        "link": link,
        "media_source": {
            "source_type": "image_url",
            "url": "https://t307239.github.io/bjj-wiki/og-image.svg"
        },
        "alt_text": title + " - BJJ technique guide"
    }
```

### 3. 重複投稿防止
```python
# 投稿済みslugセットを読み込む
posted_slugs = load_posted_slugs()

# スキップロジック
if slug in posted_slugs:
    print(f"[SKIP] Already posted: {slug}")
    continue

# 投稿後に記録
save_posted_slug(slug)
```

### 4. Telegram通知
```python
msg = f"📌 BJJ Wiki Pinterest: {posted_count} ピン投稿 ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
send_telegram(msg)
```

## 実行方法

### ローカル実行（Dry-run）
```bash
cd /sessions/keen-sharp-davinci/mnt/bjj-wiki
python3 scripts/auto_post_pinterest.py
```

環境変数なしの場合、Dry-runモード（実際には投稿しない）で動作します。

### 実際の投稿
```bash
export PINTEREST_ACCESS_TOKEN="your_token_here"
export PINTEREST_BOARD_ID="your_board_id_here"
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
python3 scripts/auto_post_pinterest.py
```

### GitHub Actions実行
```bash
# 手動実行（GitHub UI）
# Actions > Auto Post to Pinterest > Run workflow

# または GitHub CLIで
gh workflow run auto_post_pinterest.yml --repo t307239/bjj-wiki
```

## 環境変数設定（GitHub Secrets）

GitHub Secretsに以下を登録：

| 変数名 | 説明 |
|--------|------|
| `PINTEREST_ACCESS_TOKEN` | Pinterest API v5アクセストークン |
| `PINTEREST_BOARD_ID` | 投稿先のPinterestボードID |
| `TELEGRAM_BOT_TOKEN` | Telegram Botトークン（通知用） |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID（通知用） |

### Pinterest API トークン取得
1. [Pinterest App Console](https://developers.pinterest.com/apps/)でアプリを作成
2. OAuth 2.0でアクセストークンを取得
3. `PINTEREST_ACCESS_TOKEN` に設定

### ボードID確認
```bash
# Pinterestボード一覧を取得（POST後にログ出力）
curl -X GET "https://api.pinterest.com/v5/boards" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

## 仕様詳細

### 投稿制限
- **1回の実行あたり最大5件投稿** → レート制限対応
- **修正時刻でソート** → 最新記事を優先投稿
- **重複投稿防止** → `already_posted_pinterest.txt` で管理

### スキップルール
- `index`, `about`, `contact`, `404` → スペシャルページはスキップ
- `already_posted_pinterest.txt` に記録済み → スキップ
- `<title>` または `<description>` 不在 → スキップ

### 出力例
```
=== BJJ Wiki Pinterest Auto Poster ===
Time: 2026-03-17 20:34:36

[WARN] PINTEREST_ACCESS_TOKEN or PINTEREST_BOARD_ID not set.
[INFO] Running in dry-run mode (will not post).
Found 1358 HTML files in /sessions/keen-sharp-davinci/mnt/bjj-wiki/en

Already posted: 9 pages

[INFO] Processing: bjj-side-control-escape-drills
  Title: Side Control Escape Drills
  Desc: Develop side control escape proficiency through structured drilling...
  URL: https://t307239.github.io/bjj-wiki/en/bjj-side-control-escape-drills.html
[DRY-RUN] Would post: Side Control Escape Drills

✅ Done! 5 pins posted.
```

## トラブルシューティング

### Pinterest API 403エラー
- トークンの有効期限確認
- ボードIDの正確性確認
- API Quotaの確認

### Telegram通知が来ない
- `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` を確認
- ネットワーク接続を確認
- 通知失敗は無視（ビルド継続）

### HTMLパース失敗
- `/en/` ディレクトリの確認
- HTMLファイルのエンコーディング確認（UTF-8）
- `<title>` タグが存在確認

## 今後の拡張案

1. **複数言語対応**
   - `ja/`, `pt/` ディレクトリも対応
   - 言語ごとに異なるボード投稿

2. **画像カスタマイズ**
   - OGP画像を技名ごとに自動生成
   - 帯別カラー画像（白帯/青帯など）

3. **投稿スケジュール最適化**
   - Pinterest Analytics連携
   - 最高効率の投稿時刻を自動検出

4. **他のSNS連携**
   - Twitter/X自動投稿
   - Instagram Reels自動生成

## 参考

- [Pinterest API v5 Documentation](https://developers.pinterest.com/docs/getting-started/introduction/)
- [既存の auto_post_x.py パターン](./scripts/pinterest/post_to_pinterest.py)
- [generate_bjj_wiki.py Telegram通知パターン](./scripts/generate_bjj_wiki.py#L10-L28)
