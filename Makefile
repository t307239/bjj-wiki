# Makefile — z176c (extended z255p): Forcing function for "definition of done"
#
# 「完璧」と宣言する前に必ず `make verify` を実行する。
# 5 つの lint が全パスすれば commit 可能、1 つでも fail なら作業未完了。

.PHONY: verify verify-slow locale-parity gha-regression scan-ja-english scan-pt-english broken-links sitemap-drift hreflang jsonld dup-titles tab-security dup-meta brand-suffix funnel-cta anchors meta-quotes form-endpoints dup-words ja-body-translation title-html-tags cta-text-locale seo-meta-completeness og-image-encoding description-quality h2-id-clobber zindex-hardcode heading-hierarchy all clean

# z262: single-pass file walk (verify_single_pass.py) — 各 HTML を1回だけ読み込み全 per-page check をインライン実行
# Why: ~4,500 × 55 subprocess reads → ~4,500 reads で I/O ~99% 削減。cross-page check 9本は ThreadPoolExecutor で並列 subprocess。
verify:
	@python3 scripts/verify_single_pass.py --ci

# 旧来の逐次実行 (デバッグ用。特定 lint のみ確認したい場合はこちらを使う)
verify-slow: locale-parity gha-regression scan-ja-english scan-pt-english broken-links sitemap-drift hreflang jsonld breadcrumb ui-label lang-switcher breadcrumb-locale h1-brand dup-bjj-prefix ext-noreferrer dup-faq jsonld-url internal-rel tw-img-sync no-meta-keywords analytics-id login-cta-tracking dup-titles tab-security dup-meta brand-suffix funnel-cta anchors meta-quotes form-endpoints dup-words ja-body-translation title-html-tags cta-text-locale seo-meta-completeness dup-related-tech no-nested-p og-locale-completeness mobile-a11y-meta main-tag-present videoobject-when-yt apple-touch-icon-png skip-link pwa-iframe-twitter no-fake-subscriber-claim og-video-when-yt no-generic-h1 thin-content-indexable index-locale-parity no-duplicate-html-id html-quality-minor og-image-encoding description-quality h2-id-clobber zindex-hardcode heading-hierarchy
	@echo ""
	@echo "✅ All anti-regression checks passed."
	@echo "   Safe to commit."

# z176b: 3 locale marker count parity
locale-parity:
	@echo "→ check_locale_parity.py..."
	@python3 scripts/check_locale_parity.py --ci

# z156: GHA generator regression patterns (13 patterns)
gha-regression:
	@echo "→ detect_gha_regression.py..."
	@python3 scripts/detect_gha_regression.py --ci

# z255p: ja static HTML title 英語混入再発検出 (z255k で 100 件再発した class)
scan-ja-english:
	@echo "→ scan_ja_english_mixing.py..."
	@python3 scripts/scan_ja_english_mixing.py --ci

# z255p: pt static HTML title 英語混入検出 (threshold 50 で false positive 許容)
scan-pt-english:
	@echo "→ scan_pt_english_mixing.py..."
	@CI_THRESHOLD=50 python3 scripts/scan_pt_english_mixing.py --ci

# z255q: 内部リンク死活検査 (cross-locale / root-relative / template literal 対応)
broken-links:
	@echo "→ check_broken_links.py..."
	@python3 scripts/check_broken_links.py --ci

# z255r: sitemap.xml と disk HTML の整合性 (sitemap → 404 / orphan HTML 検出)
sitemap-drift:
	@echo "→ check_sitemap_drift.py..."
	@python3 scripts/check_sitemap_drift.py --ci

# z255s: hreflang 整合性 (template 未置換 / 404 / self mismatch / locale 欠落)
hreflang:
	@echo "→ check_hreflang_validity.py..."
	@python3 scripts/check_hreflang_validity.py --ci

# z255t: JSON-LD structured data validity (parse error / missing @context / template residue)
jsonld:
	@echo "→ check_jsonld_validity.py..."
	@python3 scripts/check_jsonld_validity.py --ci

# z255tt: BreadcrumbList JSON-LD presence (SERP breadcrumb navigation 必須)
breadcrumb:
	@echo "→ check_breadcrumb_jsonld.py..."
	@python3 scripts/check_breadcrumb_jsonld.py --ci

# z255uu: JA/PT page で UI label (badge/belt/diff) の EN 残留を catch
ui-label:
	@echo "→ check_ui_label_locale_drift.py..."
	@python3 scripts/check_ui_label_locale_drift.py --ci

# z255ww: lang-switcher 標準 Pattern A (🇺🇸 EN / 🇯🇵 JA / 🇧🇷 PT) 必須
lang-switcher:
	@echo "→ check_lang_switcher_consistency.py..."
	@python3 scripts/check_lang_switcher_consistency.py --ci

# z255xx: JA/PT page で <div class="breadcrumb"> last crumb の EN 残留 catch
breadcrumb-locale:
	@echo "→ check_breadcrumb_locale_drift.py..."
	@python3 scripts/check_breadcrumb_locale_drift.py --ci

# z255zz: <h1> に '| BJJ Wiki' brand suffix 混入 catch (SEO keyword stuffing)
h1-brand:
	@echo "→ check_h1_brand_pollution.py..."
	@python3 scripts/check_h1_brand_pollution.py --ci

# z255aaa:【BJJ】【BJJ】重複 prefix 混入 catch (translation double-stamp)
dup-bjj-prefix:
	@echo "→ check_duplicate_bjj_prefix.py..."
	@python3 scripts/check_duplicate_bjj_prefix.py --ci

# z255ddd: External link で rel="noopener" のみ (noreferrer 不在) catch (privacy/referrer leak)
ext-noreferrer:
	@echo "→ check_external_link_noreferrer.py..."
	@python3 scripts/check_external_link_noreferrer.py --ci

# z255ggg: 同 page で <h2>FAQ heading</h2> 重複 catch (UX/a11y)
dup-faq:
	@echo "→ check_duplicate_faq_heading.py..."
	@python3 scripts/check_duplicate_faq_heading.py --ci

# z255hhh: JSON-LD Article.url ≠ canonical (SEO 帰属先曖昧化)
jsonld-url:
	@echo "→ check_jsonld_url_drift.py..."
	@python3 scripts/check_jsonld_url_drift.py --ci

# z255jjj: body <a> 内 same-locale internal link が absolute URL (perf+UX)
internal-rel:
	@echo "→ check_internal_link_relative.py..."
	@python3 scripts/check_internal_link_relative.py --ci

# z255lll: twitter:image ≠ og:image catch (SNS preview Twitter 不整合)
tw-img-sync:
	@echo "→ check_twitter_image_sync.py..."
	@python3 scripts/check_twitter_image_sync.py --ci

# z255nnn: <meta name="keywords"> 残留 catch (Google 2009 から ignore、bloat 削減)
no-meta-keywords:
	@echo "→ check_no_meta_keywords.py..."
	@python3 scripts/check_no_meta_keywords.py --ci

# z255ppp: GA4 / GTM ID drift catch (placeholder or wrong property ID)
analytics-id:
	@echo "→ check_analytics_id_drift.py..."
	@python3 scripts/check_analytics_id_drift.py --ci

# z255sss: /login CTA に ?ref=wiki&page=X tracking 必須 (Wiki funnel attribution)
login-cta-tracking:
	@echo "→ check_login_cta_tracking.py..."
	@python3 scripts/check_login_cta_tracking.py --ci

# z255u: 同一 locale 内の <title> 衝突 (Google duplicate content 判定回避)
dup-titles:
	@echo "→ check_duplicate_titles.py..."
	@python3 scripts/check_duplicate_titles.py --ci

# z255v: <a target=_blank> rel=noopener 不在 (tabnabbing + Lighthouse 減点回避)
tab-security:
	@echo "→ check_target_blank_security.py..."
	@python3 scripts/check_target_blank_security.py --ci

# z255w: 同 locale 内の <meta description> 衝突 (Google duplicate content 判定回避)
dup-meta:
	@echo "→ check_duplicate_meta_desc.py..."
	@python3 scripts/check_duplicate_meta_desc.py --ci

# z255x: title 内の brand suffix 重複 (— BJJ Wiki | BJJ Wiki 等を keyword stuffing 化阻止)
brand-suffix:
	@echo "→ check_brand_suffix_pollution.py..."
	@python3 scripts/check_brand_suffix_pollution.py --ci

# z255y: bjj-app.net CTA に /login?ref=wiki funnel tracking (naked href 禁止)
funnel-cta:
	@echo "→ check_naked_bjj_app_cta.py..."
	@python3 scripts/check_naked_bjj_app_cta.py --ci

# z255z: ページ内アンカー fragment 死活検査 (#X が同ページ id="X" を持つこと)
anchors:
	@echo "→ check_broken_anchors.py..."
	@python3 scripts/check_broken_anchors.py --ci

# z255aa: <meta description> 内の unescaped `"` 検査 (HTML attribute truncation 防止)
meta-quotes:
	@echo "→ check_meta_attribute_quotes.py..."
	@python3 scripts/check_meta_attribute_quotes.py --ci

# z255bb: form action endpoint misroute / email exposure 検査
form-endpoints:
	@echo "→ check_misrouted_form_endpoints.py..."
	@python3 scripts/check_misrouted_form_endpoints.py --ci

# z255ll: title/h1/og:title 内の同 case 単語連続 (Guide Guide 等の generator drift)
dup-words:
	@echo "→ check_duplicate_word_in_title.py..."
	@python3 scripts/check_duplicate_word_in_title.py --ci

# z255nn: JA body content English-dominant 監視 (WARNING level、CI block しない)
# 既知 94 page、WIKI-8 で fix 予定
ja-body-translation:
	@echo "→ check_ja_body_english_dominant.py..."
	@python3 scripts/check_ja_body_english_dominant.py --strict

# z255kk: <title> 内 inline HTML element (<strong>/<span>等) 混入 catch (SEO scraper truncation)
title-html-tags:
	@echo "→ check_title_html_tags.py..."
	@python3 scripts/check_title_html_tags.py --ci

# z255ll: JA/PT page で nav `>App</a>` / cta `>Start Free →</a>` 等の英語残留 catch
cta-text-locale:
	@echo "→ check_cta_text_locale_drift.py..."
	@python3 scripts/check_cta_text_locale_drift.py --ci

# Quick check (without --ci, shows full output)
# z255jjjj-WW: SEO meta completeness (max-image-preview:large + og:image:alt)
seo-meta-completeness:
	@echo "→ check_seo_meta_completeness.py..."
	@python3 scripts/check_seo_meta_completeness.py --ci

# z255jjjj-WW: duplicate Related Techniques h2 dedup lint
dup-related-tech:
	@echo "→ check_duplicate_related_techniques.py..."
	@python3 scripts/check_duplicate_related_techniques.py --ci

# z255jjjj-WW Round2: nested <p><p> HTML validity lint
no-nested-p:
	@echo "→ check_no_nested_p.py..."
	@python3 scripts/check_no_nested_p.py --ci

# z255jjjj-WW Round3: og:locale + og:locale:alternate completeness lint
og-locale-completeness:
	@echo "→ check_og_locale_completeness.py..."
	@python3 scripts/check_og_locale_completeness.py --ci

# z255jjjj-WW Round4: theme-color / html dir / referrer-policy meta completeness
mobile-a11y-meta:
	@echo "→ check_mobile_a11y_meta.py..."
	@python3 scripts/check_mobile_a11y_meta.py --ci

# z255jjjj-WW Round5: <main> WCAG landmark presence
main-tag-present:
	@echo "→ check_main_tag_present.py..."
	@python3 scripts/check_main_tag_present.py --ci

# z255jjjj-WW Round5: VideoObject schema when YouTube embedded
videoobject-when-yt:
	@echo "→ check_videoobject_when_yt_embed.py..."
	@python3 scripts/check_videoobject_when_yt_embed.py --ci

# z255jjjj-WW Round6: apple-touch-icon must be PNG (Apple iOS spec)
apple-touch-icon-png:
	@echo "→ check_apple_touch_icon_png.py..."
	@python3 scripts/check_apple_touch_icon_png.py --ci

# z255jjjj-WW Round7: WCAG 2.4.1 skip-to-content link
skip-link:
	@echo "→ check_skip_link.py..."
	@python3 scripts/check_skip_link.py --ci

# z255jjjj-WW Round8: PWA manifest + iframe dims + twitter:creator
pwa-iframe-twitter:
	@echo "→ check_pwa_iframe_twitter.py..."
	@python3 scripts/check_pwa_iframe_twitter.py --ci

# z255jjjj-WW Round9: 嘘より沈黙 — fake subscriber/user count claim block
no-fake-subscriber-claim:
	@echo "→ check_no_fake_subscriber_claim.py..."
	@python3 scripts/check_no_fake_subscriber_claim.py --ci

# z255jjjj-WW Round10: og:video + article:author + article:published_time
og-video-when-yt:
	@echo "→ check_og_video_when_yt.py..."
	@python3 scripts/check_og_video_when_yt.py --ci

# z255jjjj-WW Round12: detect generic placeholder h1
no-generic-h1:
	@echo "→ check_no_generic_h1.py..."
	@python3 scripts/check_no_generic_h1.py --ci

# z255jjjj-WW Round14: thin content (indexable EN+PT, <100 words)
thin-content-indexable:
	@echo "→ check_thin_content_indexable.py..."
	@python3 scripts/check_thin_content_indexable.py --ci

# z255jjjj-WW Round15: index.html cat-card locale parity
index-locale-parity:
	@echo "→ check_index_locale_parity.py..."
	@python3 scripts/check_index_locale_parity.py --ci

# z255jjjj-WW Round16: duplicate HTML id detection
no-duplicate-html-id:
	@echo "→ check_no_duplicate_html_id.py..."
	@python3 scripts/check_no_duplicate_html_id.py --ci

# z255jjjj-WW Round18: HTML quality (empty heading + br chain)
html-quality-minor:
	@echo "→ check_html_quality_minor.py..."
	@python3 scripts/check_html_quality_minor.py --ci

# z260j: og:image / twitter:image URL に literal space (URL encoding 漏れ) 検出
og-image-encoding:
	@echo "→ check_og_image_url_encoding.py..."
	@python3 scripts/check_og_image_url_encoding.py --ci

# (h2-id-clobber は description-quality と並列で実行)

# z260w: meta description quality (locale drift / PT athlete concat / length / about-privacy meta)
# 4 classes (A locale drift / B PT athlete concat / C length overflow / D about-privacy)
# 統合 lint — fix_locale_drift_descriptions.py / fix_pt_athlete_desc_concat_drift.py /
#              fix_long_descriptions.py / fix_about_privacy_meta_drift.py の audit logic 永続化
description-quality:
	@echo "→ check_description_quality.py..."
	@python3 scripts/check_description_quality.py --ci

# z260x: 2 つの TOC generator (wiki-sidebar + auto-toc) の h2 id 競合検出
# auto-toc が `h.id = 'section-'+i` で wiki-sidebar の `hs+i` を破壊して 3,856 page で sidebar 死亡を再発防止
h2-id-clobber:
	@echo "→ check_h2_id_clobber.py..."
	@python3 scripts/check_h2_id_clobber.py --ci

# z261f: HTML hardcoded z-index 検出 (allowlist: 2 / 999 z243-float / 9999 modal)
# 任意 z-index 値の新規導入 (例: 100, 500, 9998) を block して layer stacking 一貫性を維持
zindex-hardcode:
	@echo "→ check_zindex_hardcode_in_html.py..."
	@python3 scripts/check_zindex_hardcode_in_html.py --ci

# z261o: heading hierarchy (WCAG 2.4.6 / SEO) — no multi-h1, no missing h1, no skip-level
# h1 → h3 等の skip は screen-reader が context 喪失する典型 a11y 違反
heading-hierarchy:
	@echo "→ check_heading_hierarchy.py..."
	@python3 scripts/check_heading_hierarchy.py --ci

all: verify
	@echo "All checks complete."

clean:
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
