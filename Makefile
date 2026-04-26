# Makefile — z176c: Forcing function for "definition of done"
#
# 「完璧」と宣言する前に必ず `make verify` を実行する。
# 4 つの lint が全パスすれば commit 可能、1 つでも fail なら作業未完了。

.PHONY: verify locale-parity gha-regression all clean

# Run all anti-regression checks
verify: locale-parity gha-regression
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

# Quick check (without --ci, shows full output)
all: verify
	@echo "All checks complete."

clean:
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
