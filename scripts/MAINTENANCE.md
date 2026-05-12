# scripts/ — Maintenance Guide

> **Purpose**: classify which scripts are still active vs one-time / archived,
> per CLAUDE.md ZERO TOLERANCE rule -4 (リファクタ優先 / 無駄 patch 量産禁止).

Last updated: 2026-05-12 (Wave WW Round 3)

---

## 📂 Categories

### 🔴 Active — DO NOT delete
These scripts are run repeatedly (cron, dev, CI). Their behavior is required ongoing.

**CI / Lint (run by `make verify`)**:
- `check_*` (29 files) — all lints in Makefile target. Anti-regression.

**Generators (run by GitHub Actions cron)**:
- `generate_bjj_wiki.py` — main page generator (legacy, being replaced by template_engine/)
- `template_engine/*.py` — new generator pipeline (extract → render)
- `generate_news_page.py` — weekly /news regeneration (`news_weekly.yml`)
- `generate_news_rss.py` — weekly RSS feed regeneration (`news_weekly.yml`)
- `generate_news_page.py` — weekly /news refresh
- `enrich_sections.py` — content enrichment via Gemini
- `gen_*.py` — index page builders
- `build_search_json.py` — search data
- `audit_wiki_structure.py` — site structure audit

**Idempotent injectors (safe to re-run)**:
- `inject_related_techniques.py` — Related Techniques section (skip-preexisting-section guard)
- `inject_person_schema.py` — Person JSON-LD for athletes (marker-based)
- `patch_funnel_cta.py` — z176/z224 CTA marker bump (idempotent)

**Patch / chrome (idempotent)**:
- `template_engine/chrome_swap.py` — surgical chrome migration
- `template_engine/bulk_rerender.py` — extract → render bulk
- `template_engine/cutover_runner.py` — production pipeline runner
- `patch_preconnect_bjj_app.py` — bjj-app.net preconnect injection
- `patch_seo_meta.py` — max-image-preview + og:image:alt
- `patch_og_locale.py` — og:locale + og:locale:alternate
- `refresh_date_modified.py` — Article schema dateModified bump
- `fix_jsonld_brand_drift.py` — BJJ Wiki → BJJ App Wiki rebrand
- `fix_nested_p_bug.py` — nested <p><p> HTML invalid

**Social media auto-posting**:
- `auto_post_*.py` — X/Bluesky/Mastodon/Threads/Pinterest

### 🟢 Completed AND template-merged (candidates for archive)
These scripts ran their one-time fix AND the underlying issue is now prevented
by template / generator changes + CI lints. They can be archived to
`scripts/archive/` after a 30-day grace period to ensure no regression.

> Status as of 2026-05-12: keep in scripts/ for 30 days, then move.

- `cleanup_duplicate_related_techniques.py` (Wave WW Round 2; bug now lint-blocked)
- `cleanup_legacy_related_techniques.py` (Wave WW Round 2; bug now lint-blocked)
- `cleanup_duplicate_athletes.py` (z200-era one-time)
- `cleanup_misplaced_faq.py` (z255 one-time)
- `fix_breadcrumb_locale_drift.py` (template now correct)
- `fix_broken_anchors.py` (lint enforces)
- `fix_broken_links*.py` (lint enforces)
- `fix_doubled_brand_suffix.py` (lint enforces)
- `fix_duplicate_*` (lint enforces)
- `fix_external_link_noreferrer.py` (lint enforces)
- `fix_h1_brand_pollution.py` (lint enforces)
- `fix_hreflang_drift.py` (lint enforces)
- `fix_jsonld_template_drift.py` (lint enforces)
- `fix_meta_quote_drift.py` (lint enforces)
- `fix_naked_bjj_app_cta.py` (lint enforces)
- `fix_target_blank_noopener.py` (lint enforces)

### 🟡 Legacy (deprecated but kept for reference)
- `add_batch_*` / `add_index_cards_batch_*` — historical batch creation, safe to keep but unlikely to re-run
- `gen_bjj_batch_*` — historical batch generators, replaced by template_engine
- `batch286_295*.py` — one-off, completed
- `_launch_announce.py` — single-event script

### ⚫ Unknown / needs classification
> Run `python3 -m pyflakes scripts/<name>.py` to check if still imported elsewhere.

---

## 📏 Adding a new script — checklist

Per CLAUDE.md rule -4:

1. ☐ Is this fix really needed? Can the template / generator be updated instead?
2. ☐ If patch is needed, is it **idempotent**? (marker / no-op on second run)
3. ☐ Did you also update template / generator so the next regeneration emits clean output?
4. ☐ Did you add a `check_*.py` lint to enforce going forward?
5. ☐ Did you add the lint to `Makefile` `verify` target?
6. ☐ Documented in this MAINTENANCE.md (active / completed-merged / legacy)?

If any ☐ is unchecked → the patch is incomplete.

---

## 🗂 Archive policy

After 30 days of stable production with no regression, scripts in
"Completed AND template-merged" should be moved to `archive/scripts/`
(outside the repo's main path).

Archive directory: `~/Claude/archive/bjj-wiki-scripts/<YYYY-MM>/`
