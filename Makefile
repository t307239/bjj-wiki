# Makefile — z176c (extended z255p): Forcing function for "definition of done"
#
# 「完璧」と宣言する前に必ず `make verify` を実行する。
# 5 つの lint が全パスすれば commit 可能、1 つでも fail なら作業未完了。

.PHONY: verify locale-parity gha-regression scan-ja-english scan-pt-english broken-links sitemap-drift hreflang jsonld dup-titles tab-security dup-meta brand-suffix funnel-cta anchors meta-quotes form-endpoints dup-words ja-body-translation title-html-tags cta-text-locale seo-meta-completeness all clean

# Run all anti-regression checks
verify: locale-parity gha-regression scan-ja-english scan-pt-english broken-links sitemap-drift hreflang jsonld breadcrumb ui-label lang-switcher breadcrumb-locale h1-brand dup-bjj-prefix ext-noreferrer dup-faq jsonld-url internal-rel tw-img-sync no-meta-keywords analytics-id login-cta-tracking dup-titles tab-security dup-meta brand-suffix funnel-cta anchors meta-quotes form-endpoints dup-words ja-body-translation title-html-tags cta-text-locale seo-meta-completeness dup-related-tech no-nested-p og-locale-completeness mobile-a11y-meta main-tag-present videoobject-when-yt apple-touch-icon-png skip-link
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

all: verify
	@echo "All checks complete."

clean:
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
