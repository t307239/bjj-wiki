# REF-2 W4: Cutover Plan

> **Status (z255ss)**: 全 3 locale で cutover_readiness.py が ✅ GO を返す状態。
> 実 cutover は本 doc の Day-by-day procedure に従って Toshiki さんが執行。

## 📖 この doc は何か (前置き)

「**Cutover** = 古い generator を止めて、新しい template-driven generator に切り替える作業」のことです。料理の例えで言うと:

- **今**: 7 人の料理人 (1 main generator + 6 patch script) が daily cron でリレーして 4,500 page を作っている
- **Cutover 後**: 1 人の料理人 (template-driven pipeline) が同じ 4,500 page を 1 人で作る
- **見た目**: ほぼ完全同一 (PT page だけ head 構造が綺麗に統一される drift cleanup あり)
- **SEO**: URL も hosting も変わらないので影響 0

cutover は **1 日だけの作業**ではなく **1 週間プロセス** (Day 0-Day 5)。
日々の作業は数十分〜数時間、間に shadow mode (parallel run) の **passive monitor 期間 2-3 日**を挟むため。

**この doc を読む順番**:
1. 「What "cutover" means」 で全体像を掴む
2. 「Pre-cutover checklist」 で準備状況を確認
3. 「Day-by-day Cutover Procedure」 を毎日見ながら作業
4. 問題が起きたら 「Rollback Plan」 を 10 分で実行

**前提知識**: この doc を理解するには `scripts/template_engine/README.md` を先に読んで、template / renderer / extractor の役割を理解しておくと良い。技術用語は最小限にしてあるが、`generate.yml` (GitHub Actions の cron 定義) の編集は必要なので、Toshiki さんが自分で git ブランチを切って execute する前提です。

## What "cutover" means

**Before**: `generate.yml` daily cron が `generate_bjj_wiki.py` (1,969 行 monolith) を呼んで Gemini API で content 生成 → HTML を string concat で構築 → 6 patch script chain (faq / internal_links / funnel_cta / video_from_supabase / sitemap / content_depth) で markers + sections injection。

**After**: `generate.yml` daily cron が **template-driven pipeline** を呼ぶ:
1. Gemini API で content 生成 (既存 logic 流用、output を JSON schema に整形)
2. `scripts/template_engine/render.py` で `templates/archetypes/technique.html.j2` + `templates/messages/{lang}.yml` から HTML 構築
3. **6 patch script は引き続き走る** (Marker Contract 準拠で互換性維持。W5 で段階的 absorb)。

URL / hosting / HTML byte-level: 既存と同等または cleaner (PT drift cleanup あり)。
SEO 影響: 0 (URL も hosting も不変)。

## Pre-cutover checklist

- [x] **REF-2 W0 marker contract** (`docs/WIKI_TEMPLATES.md` §HTML Marker Contract) — 完了 (z255nn)
- [x] **REF-2 W1 Jinja2 + 3 locale YAML + renderer** — 完了 (z255oo)
- [x] **REF-2 W2 diff_check.py + 1 page verify** — 完了 (z255pp)
- [x] **REF-2 W2-ext extractor + 77 EN page batch verify** (100% zero TEMPLATE_GAP) — 完了 (z255qq)
- [x] **REF-2 W3 7 archetype 全対応** (universal template + 6 sample data) — 完了 (z255rr)
- [x] **REF-2 W4 3 locale cutover readiness** (EN 100% / JA 100% / PT drift cleanup mode) — 完了 (z255ss)
- [ ] **Cutover sequence below 実行**

## Day-by-day Cutover Procedure

### Day 0: Final readiness check

```bash
cd ~/Claude/bjj-wiki
python3 scripts/template_engine/cutover_readiness.py --sample 200
```

✅ GO 表示を確認 (EN ≥95% / JA ≥95% / PT drift cleanup mode acceptable)。

### Day 1: Generator integration shim

`scripts/template_engine/cutover_runner.py` (将来作成) で以下のループ:

```
for technique in pending_pages:
    content = call_gemini(technique)            # 既存 generate_bjj_wiki.py の Gemini logic 流用
    page_data = adapt_to_json_schema(content)   # 既存 → 新 schema へ変換
    html = render(archetype, lang, page_data)   # scripts/template_engine/render.py
    write(f"{lang}/{slug}.html", html)
```

このシムを **dev branch (--branch=template-cutover-shadow)** にだけ deploy、main 影響なし。

### Day 2-3: Shadow mode (parallel run)

GitHub Actions に shadow workflow `.github/workflows/generate-shadow.yml` を追加:
- 既存 `generate.yml` と同じ schedule で動く
- 新 pipeline で **完全別 directory `shadow/{lang}/*.html`** に出力
- Telegram 通知で完了 alert

毎日 shadow output を `diff -r` で main output と比較:

```bash
# After shadow run
diff -rq en/ shadow/en/ | grep -v 'identical' | head -50
```

期待される diff:
- ✅ PT pages: head structure 統一 (drift cleanup)
- ✅ Some pages: small structural fix (z255 W2-ext で発見した bug fix の効果)
- ❌ Anything else: investigate before cutover

### Day 4: Staging deploy + manual SEO sample

10 pages 手動確認 (mix of EN / JA / PT):
- Browser dev tools で head section 確認 (canonical / hreflang / og 全部正しい)
- Mobile responsive 確認 (320 / 375 / 768px)
- JSON-LD validator で structured data 確認
- Lighthouse SEO score 比較 (cutover 前 vs shadow)

合格基準: Lighthouse SEO score 同等 (±2pt)、JSON-LD 全 valid、視覚的 regression 0。

### Day 5: Production cutover

```bash
cd ~/Claude/bjj-wiki

# 1. Update generate.yml
#    main pipeline = new template-driven (cutover_runner.py)
#    OR
#    generate.yml で if env.USE_NEW_PIPELINE で分岐

# 2. Test on staging branch
git checkout -b cutover-go
# Modify .github/workflows/generate.yml
git commit -m "cutover: switch generate.yml to template-driven pipeline (REF-2 W4)"

# 3. Manual trigger generate.yml on cutover-go branch
# 4. Verify output
# 5. Merge to main
git checkout main
git merge cutover-go
git push  # or use auto-push daemon

# 6. Monitor 24h:
#    - Telegram alerts
#    - Search Console (next-day)
#    - Vercel Analytics (immediate)
```

### Day 6+: Monitor + W5 cleanup

Monitor for 7 days post-cutover:
- Search Console: average position, clicks/impressions per day
- Vercel Analytics: Wiki → App funnel CVR (`?ref=wiki` signups)
- Lighthouse periodic check (optional)

If all green → **REF-2 W5** に進む (cleanup):
- 既存 `generate_bjj_wiki.py` を `archive/` へ移動
- 9 個重複 CTA HTML を template の 1 箇所に集約
- BACKLOG WIKI-8 / WIKI-10 / J-3 / F-28 を template 修正のみで一括消化

## Rollback Plan

cutover 後 24-48h で **重大 regression** 検出時:

### Symptoms triggering rollback

- Search Console で indexed pages 数が 24h で 30%+ 減
- Wiki → App CVR が 50%+ 減 (Vercel Analytics)
- 視覚的 layout 崩壊 (mobile 表示不可)
- JSON-LD invalid で rich snippet 全消失

### Rollback procedure (10 分)

```bash
cd ~/Claude/bjj-wiki

# 1. Revert generate.yml
git revert <cutover commit>
# OR
git checkout HEAD~1 .github/workflows/generate.yml

# 2. Manually trigger generate.yml on main branch
# (will use old generate_bjj_wiki.py + 6 patches)

# 3. Verify all pages re-deploy with old structure
# 4. git push (auto-push daemon picks it up)
```

Rollback 後、新 pipeline の bug を修正 → cutover_readiness.py 再 ✅ → 再度 cutover (Day 1 から)。

## Rollback safety checks

- ✅ 既存 `generate_bjj_wiki.py` は `archive/` に移動しない (cutover 後も rollback で必要)
- ✅ 6 patch scripts は cutover 後も引き続き run (互換性維持)
- ✅ Marker Contract 準拠で marker format 不変 → 旧 / 新 generator 両方が同じ marker を出力
- ✅ Static HTML output に変わりない → GitHub Pages deploy も無変更

## Estimated timeline

| Day | Task | Effort |
|---|---|---|
| 0 | readiness check | 5 min |
| 1 | shim implementation | 4 hours |
| 2-3 | shadow run + diff | 2 days passive |
| 4 | staging + manual SEO | 1 hour |
| 5 | production cutover | 30 min |
| 6-12 | monitor + W5 prep | 1 week passive |

**Total active work: ~6 hours over 1 week**.

## Known risks

| Risk | Severity | Mitigation |
|---|---|---|
| Gemini API output format changes | 🟡 Medium | shim has adapter layer; version-pin Gemini API |
| Shadow output mismatches main beyond drift cleanup | 🔴 High | diff 監視 daily; 不一致 0 まで cutover 延期 |
| GitHub Pages deploy timing変化 | 🟢 Low | static HTML 出力なので deploy 経路同一 |
| 6 patch scripts と新 template の marker 不一致 | 🟡 Medium | Marker Contract (W0) で永久 block、cutover 前 verify |
| Search Console regression | 🟡 Medium | rollback 10 分; 7 日 monitor;  PT drift cleanup は intentional positive change |

## Success criteria (post-cutover)

7 日後:
- ✅ Search Console: indexed pages 同等以上 (drift cleanup で逆に良くなる可能性)
- ✅ Wiki → App CVR: 同等以上 (CTA marker 不変、attribution preserved)
- ✅ Lighthouse SEO: ±2pt
- ✅ Telegram alerts: 0 critical
- ✅ make verify (bjj-wiki): 33/33 lint pass

達成 → ✅ REF-2 W4 完了 → W5 cleanup へ進む。

未達 → rollback or 部分修正 (PT のみ delay 等)。
