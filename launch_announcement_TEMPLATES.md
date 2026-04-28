# 🚀 Auto-post launch announcement テンプレート (z226)

> **使い方**: Toshiki が「今 launch する」と決めた時、下のテキストを
> bjj-wiki repo 直下の各 sentinel file に書き込んで commit/push する。
> 翌日の cron で各 platform に **1 回だけ** launch announcement 投稿、
> ファイル削除されて normal Wiki post 再開。

## 投入手順 (5 分)

```bash
cd ~/Claude/bjj-wiki

# 1. X (280 char)
cat > launch_announcement_x.txt <<'EOF'
[ X 用テキストをここに、下のテンプレからコピペ ]
EOF

# 2. Threads (500 char)
cat > launch_announcement_threads.txt <<'EOF'
[ Threads 用テキスト ]
EOF

# 3. Bluesky (300 char)
cat > launch_announcement_bluesky.txt <<'EOF'
[ Bluesky 用テキスト ]
EOF

# 4. Mastodon (500 char)
cat > launch_announcement_mastodon.txt <<'EOF'
[ Mastodon 用テキスト ]
EOF

git add launch_announcement_*.txt
git commit -m "Launch announcement: queue 4 platforms"
git push
```

GH Actions cron (X 3回/日, Threads/Bluesky/Mastodon 2回/日) が次回 run 時に
sentinel を消費 → launch text 投稿 → ファイル削除。
完了後は通常の Wiki page 投稿に戻る。

---

## 📋 テンプレート (そのままコピペ OK)

### X (Twitter) — 280 char
```
I built a free BJJ tracker integrated with a 1,500-page technique wiki.

Indie blue belt project. No VC, no ads. EN/JA/PT.

🥋 bjj-app.net/?ref=x_launch
```
(269 chars)

### Threads — 500 char
```
I built a free BJJ tracker integrated with a 1,500-page technique wiki — solo, 6 months in, 1 real user (me).

What's different from BJJBuddy / BJJ Notes / MatTime: integrated technique knowledge (none of them have a wiki).

Built by an indie blue belt. No VC, no ads. EN / JA / PT.

🥋 https://bjj-app.net/?ref=threads_launch
📚 https://wiki.bjj-app.net (no signup needed)

Honest feedback > anything else right now.
```
(497 chars)

### Bluesky — 300 char (graphemes)
```
I built a free BJJ tracker integrated with a 1,500-page technique wiki.

Indie blue belt, 6 months solo, 1 real user (me).

EN/JA/PT, no VC, no ads.

🥋 bjj-app.net/?ref=bsky_launch
📚 wiki.bjj-app.net (free, no signup)
```
(247 chars)

### Mastodon — 500 char (mastodon.social default)
```
I built a free BJJ tracker integrated with a 1,500-page technique wiki — solo, 6 months in, 1 real user (me).

Different from BJJBuddy / BJJ Notes / MatTime: integrated technique knowledge (none have a wiki).

Indie blue belt project. No VC, no ads. EN / JA / PT.

#BJJ #BrazilianJiuJitsu #IndieDev

🥋 https://bjj-app.net/?ref=mastodon_launch
📚 https://wiki.bjj-app.net
```
(499 chars)

---

## ⚠️ 注意

- **各 sentinel は 1 回だけ消費**。launch 後は normal post 再開。
- **launch 中に通常 cron が走っても OK**: sentinel 検知優先で launch text を post、その cycle 内では Wiki post スキップ。
- **失敗時**: Telegram に「<platform> launch announcement FAILED」通知。sentinel は不確定状態。手動確認後、必要なら再投入。
- **投稿後の monitoring**: AdminPanel /admin (要 ADMIN_EMAIL fix) で `?ref=<platform>_launch` 経由 signup を翌日確認。

## 🔄 timing 戦略

各 cron schedule:
- X: 3回/日 (時刻は yml 参照)
- Threads: 2回/日
- Bluesky: 2回/日
- Mastodon: 2回/日

**全 4 platform 同時 launch** = sentinel 4 ファイルを同時 commit/push。
最大 24h 以内に全 platform に届く (各 cron が次回走る時)。

**段階 launch** = 1 platform ずつ commit。
例: 月 X、火 Threads、水 Bluesky、木 Mastodon → 1 週間で広がる。
段階 launch の方が「なぜ突然 4 platform 全部 talk?」 spam 感を回避できる。
