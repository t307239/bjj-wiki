# Makefile — z176c (extended z255p): Forcing function for "definition of done"
#
# 「完璧」と宣言する前に必ず `make verify` を実行する。
# 5 つの lint が全パスすれば commit 可能、1 つでも fail なら作業未完了。

.PHONY: verify locale-parity gha-regression scan-ja-english scan-pt-english broken-links sitemap-drift hreflang jsonld dup-titles tab-security dup-meta brand-suffix funnel-cta anchors meta-quotes form-endpoints dup-words ja-body-translation all clean

# Run all anti-regression checks
verify: locale-parity gha-regression scan-ja-english scan-pt-english broken-links sitemap-drift hreflang jsonld dup-titles tab-security dup-meta brand-suffix funnel-cta anchors meta-quotes form-endpoints dup-words ja-body-translation
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

# Quick check (without --ci, shows full output)
all: verify
	@echo "All checks complete."

clean:
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
