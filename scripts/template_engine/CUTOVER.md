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

---

## 🧹 W5: Post-cutover cleanup plan (z255tt)

> **前置き**: cutover が成功して 7 日 monitor も clean だった後、ここで
> 「掃除」をする。**cutover 前に実行する必要は無い** (むしろ cutover 前に
> 古い script を archive すると rollback できなくなって危険)。

### 5.1 Deferred backlog 一気消化 (template 修正のみで全 page 反映)

cutover が完了すると、以下の「ずっと deferred だった backlog」が **template を 1 箇所直すだけで全 4,500 page に反映**される。手順:

#### J-3: Gemini prompt hardening (z255ii で部分実装、cutover で完成)

- 現状: `generate_bjj_wiki.py` line 333 の prompt に lang_instruction + lang-specific examples 追加済 (z255ii)
- cutover 後: 新 pipeline (`render.py` 経由) で同 prompt を維持、Gemini drift で英語混入が起きても template の **lang-mismatch guard** が write 前に reject
- **作業**: 不要 (z255ii で完了済、cutover 後に効果が確実化)

#### WIKI-8: 94 JA page body 翻訳 (英語混入 dominant)

- 問題: 94 JA page で本文が英語のまま (Gemini fallback で生成)
- cutover 後の解決法:
  ```bash
  cd ~/Claude/bjj-wiki
  # 該当 page の JSON data を抽出 → JA 用 prompt で再 generate → render
  python3 scripts/wiki8_retranslate.py --lang ja --pages "$(cat docs/wiki8-failing-pages.txt)"
  # 1 page = 30s × 94 page = ~50 min
  # cost: ~$2 (Gemini Flash)
  ```
- **必要な追加 script**: `scripts/wiki8_retranslate.py` (現状なし、cutover 後に書く)

#### WIKI-10: 4,665 page UI label 翻訳 (Belt/Difficulty/Category)

- 問題: 一部 page で UI label が英語のまま (例: "Difficulty: Intermediate" が JA でも英語)
- cutover 後の解決法: locale rules YAML (`templates/messages/ja.yml`) を 1 箇所修正
  - 例: `difficulty.label.intermediate: "中級"` 追加
  - 全 4,665 page に **次の cron (24h 以内) で自動反映**
- **作業**: YAML 1 ファイル編集 + cron が走るまで待つ (~30 分)

#### F-28: AI citation 最適化 (llms.txt) — z255tt で完了済

- ✅ `scripts/template_engine/gen_llms_txt.py` で `llms.txt` 生成
- 1,563 page を 213 行 / 29.6KB に圧縮、AI 引用最適化
- ChatGPT / Perplexity / Google AI Overviews が site 構造を理解しやすくなる
- **作業 (cutover 後)**: `generate.yml` cron に `python3 scripts/template_engine/gen_llms_txt.py` を追加 (毎日 fresh 維持)

### 5.2 重複 CTA HTML を template に集約 (実コードの絶対量削減)

**現状**: CTA HTML が 9 箇所で重複定義されている:
- `scripts/fix_wiki4.py` の `CTA_EN` / `CTA_JA` / `CTA_PT` (3 箇所)
- `scripts/patch_locale_full.py` line 65-92 の en/ja/pt mapping (3 箇所)
- `scripts/patch_funnel_cta.py` の `bottom_cta_html()` / `float_cta_html()` (3 箇所)

**Cutover 後の整理**:
- `templates/archetypes/technique.html.j2` の z243-bottom-cta / z243-float-cta block が **唯一の source of truth** に
- 上記 3 script は archive へ移動 (もう使われない)
- locale 別 CTA 文言は `templates/messages/{lang}.yml` の `cta_bottom` / `cta_float` セクションが正

**作業**:
```bash
# 1. archive する script を確認
cd ~/Claude/bjj-wiki
mkdir -p scripts/archive/pre-template-cutover
git mv scripts/fix_wiki4.py scripts/archive/pre-template-cutover/
git mv scripts/patch_locale_full.py scripts/archive/pre-template-cutover/

# 2. patch_funnel_cta.py は cutover 後も marker injection で必要なら残す
#    (Marker Contract で template が直接 marker を出す版を採用したら archive)

# 3. commit
echo "z255tt cleanup: archive obsolete CTA scripts (replaced by template)" \
  > .git/CLAUDE_COMMIT_MSG
```

### 5.3 古い generator (`generate_bjj_wiki.py`) の処遇

cutover 後 30 日 (1 ヶ月) で安定確認できたら `archive/` へ。

**理由**: rollback safety net として 30 日は手元に残す。Search Console で月次 indexing 状況の trend を見て、何も regression がなければ archive。

### 5.4 Lint 数縮小 (27 → 5-7 個)

template 化で「もう発生し得ない bug class」を catch する lint は不要になる:

| Lint | 理由 | 処遇 |
|---|---|---|
| `check_cta_text_locale_drift` | template が locale YAML から CTA 出すので drift 不可能 | retire |
| `check_brand_suffix_pollution` | template が brand suffix を 1 箇所で管理 | retire |
| `check_duplicate_titles` | template + JSON data で title 一意 | retire |
| `check_misrouted_form_endpoints` | template に form なし | retire |
| `check_lang_switcher_consistency` | template が 3 locale 同じ component で出力 | retire |
| `check_breadcrumb_locale_drift` | template が breadcrumb を locale 駆動 | retire |
| `check_h1_brand_pollution` | template の h1 は data から | retire |
| `check_duplicate_bjj_prefix` | template が prefix 1 回だけ | retire |
| `check_internal_link_relative` | template の link は relative 統一 | retire |
| `check_external_link_noreferrer` | template が rel 統一 | retire |
| `check_target_blank_security` | template が rel="noopener" 統一 | retire |
| `check_jsonld_validity` | template が JSON-LD を data 経由で出す | retire |
| `check_jsonld_url_drift` | 同上 | retire |
| `check_meta_attribute_quotes` | template が autoescape で出す | retire |
| `check_no_meta_keywords` | template が出さなければ OK | retire |
| `check_twitter_image_sync` | template が og + twitter 同 source 参照 | retire |
| `check_login_cta_tracking` | template の CTA URL は 1 箇所 | retire |
| `check_naked_bjj_app_cta` | template の CTA は wiki tracking 必須 | retire |
| `check_doubled_brand_suffix` | template の title は data 1 回 | retire |
| `check_duplicate_word_in_title` | 同上 | retire |
| `check_duplicate_meta_desc` | template が unique description 必須 | retire |
| `check_title_html_tags` | template の title は plain text | retire |
| `check_broken_anchors` | 残す (dynamic content) |
| `check_broken_links` | 残す (link 動的) |
| `check_sitemap_drift` | 残す (sitemap 別 cron) |
| `check_hreflang_validity` | 残す (template 使うが念のため) |
| `check_breadcrumb_jsonld` | 残す (JSON-LD 構造 verify) |
| `check_ja_body_english_dominant` | 残す (Gemini drift catch) |
| `check_ui_label_locale_drift` | 残す (locale YAML drift catch) |

→ 27 → 6 lint まで縮小可能。**作業**: `Makefile` の verify target から retire 対象を削除、`bjj-wiki/scripts/archive/` へ script を move。

### 5.5 W5 完了基準

- [ ] J-3 / WIKI-8 / WIKI-10 / F-28 BACKLOG が ✅ 化
- [ ] 9 重複 CTA → 1 template に集約 (archive 完了)
- [ ] generate_bjj_wiki.py archive (cutover 後 30 日 monitor で問題なし)
- [ ] Lint 27 → 6 個に縮小
- [ ] BACKLOG REF-2 全 entry ✅ 化
- [ ] devlog に W5 完了 entry 追加

W5 完了で **REF-2 全 (5 週) finish**。Plan A 全体 (REF-1 + REF-2 + REF-3 + REF-4) のうち **REF-1 + REF-2 完了**、残り REF-3 (UI 改善、低 cost project) と REF-4 (bjj-app 同様 refactor) は将来作業。
