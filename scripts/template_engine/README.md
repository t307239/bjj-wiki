# Template Engine (REF-2, z255oo+)

Template-driven Wiki page renderer for the bjj-wiki refactor.

## 📖 これは何 (前置き、非技術者向け)

Wiki の page (4,500 枚) を作る方法を **「7 人の料理人がリレーする」**から **「1 人の料理人がレシピ通りに作る」**に変える refactor の中身です。

「料理人」「レシピ」を技術用語に翻訳すると:
- **料理人** = generator script (Python で書かれた page 作成プログラム)
- **レシピ** = template (Jinja2 という Python の標準的な template engine の文法で書かれた HTML 雛形)
- **page の中身** = JSON data (Gemini AI で生成した content を構造化したデータ)
- **言語別の文言** = locale YAML (EN / JA / PT の UI 文字列を一箇所に集約したファイル)

**処理の流れ**:

```
[Gemini AI でコンテンツ生成]
       ↓
[JSON data]   ←─── extract.py が既存 page から抽出することも可能
       ↓
[render.py が template + locale + JSON を合成]
       ↓
[完成した HTML page]
```

**この folder に何があるか**:

| ファイル | 役割 |
|---|---|
| `render.py` | レシピ通りに page を作る本体 |
| `extract.py` | 既存 page から JSON data を抽出 (cutover 検証用) |
| `diff_check.py` | 既存 page と新 page を比較、違いを 7 種類に分類 |
| `batch_verify.py` | 多数 page を一括で verify (extract → render → diff) |
| `cutover_readiness.py` | 3 言語で「切り替えて OK か?」判定 |
| `CUTOVER.md` | 切り替え作業の Day-by-day 手順書 |
| `README.md` (本ファイル) | この folder の総合案内 |

**なぜこんなことを?**

Wiki page を作る script が 7 個もあって、互いに HTML コメント (例: `<!-- z243-bottom-cta -->`) で「自分の作業が済んだか」を伝え合っている。Script 同士の暗黙の前提が衝突して bug が頻発するため、料理人を 1 人 (= 1 個の template) に集約することで bug の発生する空間自体を減らす狙い。**SEO への影響は 0** (URL や hosting は不変、HTML 構造だけ整理される)。

詳細な理由・経緯は `docs/devlog/2026-05.md` の z255mm から z255ss を参照。

## Status

**W1 (foundation) — complete (z255oo, 2026-05-08).**

- ✅ Directory structure: `templates/{archetypes,partials,messages}/`
- ✅ Locale rules YAML for 3 languages (en/ja/pt)
- ✅ Technique archetype Jinja2 template (covers full page structure including z243 markers per WIKI_TEMPLATES.md Marker Contract)
- ✅ Renderer script with CLI
- ✅ Smoke test passing for all 3 locales (armbar.json sample)

## Layout

```
bjj-wiki/
├── templates/
│   ├── archetypes/
│   │   └── technique.html.j2     # Master template for Technique pages
│   ├── partials/                  # (future: shared fragments)
│   ├── messages/
│   │   ├── en.yml                 # English UI strings
│   │   ├── ja.yml                 # Japanese UI strings
│   │   └── pt.yml                 # Portuguese UI strings
│   └── sample_data/
│       └── armbar.json            # Smoke-test sample data
└── scripts/template_engine/
    ├── render.py                  # CLI renderer
    └── README.md                  # This file
```

## Usage

```bash
cd ~/Claude/bjj-wiki

# Render a Technique page in EN
python3 scripts/template_engine/render.py \
    --archetype technique \
    --lang en \
    --data templates/sample_data/armbar.json \
    --output /tmp/armbar_en.html

# Same in JA
python3 scripts/template_engine/render.py \
    --archetype technique \
    --lang ja \
    --data templates/sample_data/armbar.json \
    --output /tmp/armbar_ja.html

# Skip z243 CTA markers (let patch_funnel_cta.py handle them)
python3 scripts/template_engine/render.py \
    --archetype technique \
    --lang en \
    --data templates/sample_data/armbar.json \
    --no-z243-cta \
    --output /tmp/armbar_no_cta.html
```

## Inputs

### Page data JSON schema (Technique archetype)

```json
{
  "slug": "armbar",
  "h1": "Armbar: A White Belt's Biomechanical Guide",
  "h1_simple": "Armbar",
  "seo_title": "...",
  "og_title": "...",
  "og_image_title": "Armbar",
  "description": "...",
  "keywords": "...",
  "category": "Joint Lock",
  "belt_level": "White",
  "difficulty": {"belt": "blue", "stars": "★★★☆☆", "label": "Intermediate"},
  "guide_belt": "blue",
  "intro_paragraphs": ["..."],
  "sections": [
    {"heading": "Grips & Mechanics", "type": "ol", "items": [{"bold": "...", "text": "..."}]},
    {"heading": "Warnings", "type": "ul", "style": "warning", "items": [...]}
  ],
  "athletes": [{"name": "...", "flag": "🇺🇸", "slug": "athlete-..."}],
  "yoga_poses": [{"name": "...", "slug": "..."}],
  "faq": [{"question": "...", "answer": "..."}],
  "related_techs": [{"name": "...", "slug": "..."}],
  "related_concepts": [{"name": "...", "slug": "..."}],
  "video_embed_id": "GshEzcqlUbY",
  "jsonld_article": "...",  // pre-stringified JSON-LD
  "jsonld_breadcrumb": "...",
  "jsonld_faq": "...",
  "howto_steps": true,
  "jsonld_howto": "..."
}
```

### Locale messages YAML schema

See `templates/messages/en.yml` for full schema. Key sections:

- `nav` (logo, lang flag labels)
- `belt_guide_box` (per-belt color + CTA text)
- `toc` (TOC widget heading)
- `related_video` (heading, intro, search button, UGC fallback)
- `athletes` (heading)
- `competition_box` / `safety_box` (cross-link banners)
- `yoga_box` / `gear_box` (sidebar boxes)
- `faq` (heading)
- `related_techs` (heading)
- `newsletter` (Beehiiv signup heading + body + CTA)
- `dig_deeper` (semantic linking section)
- `cta_dynamic` (contextual CTA banner)
- `cta_bottom` (z243-bottom-cta marker block)
- `cta_float` (z243-float-cta marker block)
- `share_bar` (X / Reddit / Copy / YouTube buttons)
- `footer` (tagline + privacy link)
- `site` (base URLs, GA ID, AdSense client, Twitter handle)

**Important**: any new key added to `en.yml` MUST be added to `ja.yml` and `pt.yml` in the same shape. `check_locale_parity.py` will not catch missing locale keys directly (it counts marker occurrences), but the template will fail with `UndefinedError` at render time.

## Marker Contract compliance

Per `docs/WIKI_TEMPLATES.md` §HTML Marker Contract, the template emits:

- `<!-- z243-bottom-cta -->` immediately followed by the CTA `<div>` (footer 直前)
- `<!-- z243-float-cta -->` immediately followed by the floating CTA `<div>` (`</body>` 直前)

Format strictly matches `<!-- z\d{3,}-[\w-]+ -->` regex. Idempotency is the
caller's responsibility (not the template's) — the template assumes the renderer
or downstream patch handles "skip if marker already present" logic.

The `--no-z243-cta` flag suppresses both marker blocks if the caller wants
`patch_funnel_cta.py` to inject them post-render (W4 cutover may use this).

## What's next

- **W2** (next): run renderer on 100 existing Technique pages, byte-diff the output
  against the current page, and iterate until diff = lint-fix-only.
- **W3**: build templates for the other 6 archetypes (Concept_Strategy, Rule,
  Athlete_Bio, Equipment_Gear, Conditioning_Nutrition, Drill).
- **W4**: cutover. Run new generator alongside old generator in dev branch,
  compare daily output, then retire old generator.
- **W5**: cleanup. Archive deprecated `patch_*.py` scripts, consolidate
  duplicated CTA HTML (currently in 9 places).

## Known limitations (W1, will be addressed in W2)

- Output is **not yet byte-equivalent** to current armbar.html (242 vs 333 lines).
  Some sections (duplicated athletes, additional inline styles, etc.) need
  template adjustments. W2 verification will close these gaps.
- Template uses `is defined` guards for optional fields. May need refactoring
  when more page types share the same template.
- No integration with the existing `generate_bjj_wiki.py` Gemini pipeline yet.
  W4 cutover will design how Gemini-generated content flows into the JSON
  data schema.
