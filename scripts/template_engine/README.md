# Template Engine (REF-2 W1, z255oo)

Template-driven Wiki page renderer for the bjj-wiki refactor.

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
