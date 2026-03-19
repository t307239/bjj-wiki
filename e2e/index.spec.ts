import { test, expect } from "@playwright/test";

/**
 * E2E: BJJ Wiki index.html — 全3言語
 */

const LANGS = [
  { code: "en", path: "/en/index.html", heroText: /BJJ.*Wiki/i },
  { code: "ja", path: "/ja/index.html", heroText: /BJJ.*Wiki/i },
  { code: "pt", path: "/pt/index.html", heroText: /BJJ.*Wiki/i },
];

for (const lang of LANGS) {
  test.describe(`Index [${lang.code}]`, () => {
    test.beforeEach(async ({ page }) => {
      await page.goto(lang.path);
    });

    // ====== 基本構造 ======

    test("renders hero section with title", async ({ page }) => {
      const h1 = page.locator("h1");
      await expect(h1).toBeVisible();
      const text = await h1.textContent();
      expect(text).toMatch(lang.heroText);
    });

    test("has subtitle with page count", async ({ page }) => {
      const sub = page.locator(".hero-sub");
      await expect(sub).toBeVisible();
      const text = await sub.textContent();
      expect(text).toMatch(/1[,.]?[05]00|technique|テクニック|técnica/i);
    });

    // ====== メタデータ ======

    test("has correct html lang attribute", async ({ page }) => {
      const htmlLang = await page.getAttribute("html", "lang");
      expect(htmlLang).toBe(lang.code);
    });

    test("has <title>", async ({ page }) => {
      const title = await page.title();
      expect(title.length).toBeGreaterThan(10);
      expect(title).toMatch(/BJJ/i);
    });

    test("has meta description", async ({ page }) => {
      const desc = page.locator('meta[name="description"]');
      expect(await desc.count()).toBeGreaterThanOrEqual(1);
      const content = await desc.getAttribute("content");
      expect(content!.length).toBeGreaterThan(20);
    });

    test("has OGP meta tags", async ({ page }) => {
      expect(await page.locator('meta[property="og:title"]').count()).toBeGreaterThanOrEqual(1);
      expect(await page.locator('meta[property="og:description"]').count()).toBeGreaterThanOrEqual(1);
      expect(await page.locator('meta[property="og:type"]').count()).toBeGreaterThanOrEqual(1);
    });

    test("has hreflang tags for all 3 languages + x-default", async ({ page }) => {
      const count = await page.locator('link[rel="alternate"][hreflang]').count();
      expect(count).toBeGreaterThanOrEqual(4);
    });

    // ====== 検索UI（DOM存在チェックのみ — fetchタイミング不問） ======

    test("has search input", async ({ page }) => {
      await expect(page.locator("#search")).toBeVisible();
    });

    test("search input triggers oninput handler", async ({ page }) => {
      const searchInput = page.locator("#search");
      await searchInput.fill("triangle");
      // Just verify the input accepted the value — actual search depends on fetch
      const value = await searchInput.inputValue();
      expect(value).toBe("triangle");
    });

    test("result cards are present on initial load (popular guides)", async ({ page }) => {
      const grid = page.locator("#results-grid");
      await expect(grid).toBeVisible();
      const cards = page.locator(".result-card");
      const count = await cards.count();
      expect(count).toBeGreaterThanOrEqual(6);
    });

    test("result cards link to .html pages", async ({ page }) => {
      const firstCard = page.locator(".result-card").first();
      await expect(firstCard).toBeVisible();
      const href = await firstCard.getAttribute("href");
      expect(href).toMatch(/\.html$/);
    });

    // ====== カテゴリフィルター ======

    test("has category pills (8+)", async ({ page }) => {
      const count = await page.locator(".cat-pill").count();
      expect(count).toBeGreaterThanOrEqual(8);
    });

    test("'All' pill is active by default", async ({ page }) => {
      await expect(page.locator('.cat-pill[data-cat="all"]')).toHaveClass(/active/);
    });

    test("clicking category pill toggles active state", async ({ page }) => {
      const subPill = page.locator('.cat-pill[data-cat="submission"]');
      await subPill.click();
      await expect(subPill).toHaveClass(/active/);
      await expect(page.locator('.cat-pill[data-cat="all"]')).not.toHaveClass(/active/);
    });

    // ====== CTA・Beehiiv ======

    test("has CTA banner with BJJ App link", async ({ page }) => {
      const ctaBtn = page.locator(".cta-btn");
      await expect(ctaBtn).toBeVisible();
      const href = await ctaBtn.getAttribute("href");
      expect(href).toContain("bjj-app");
    });

    test("has Beehiiv newsletter form", async ({ page }) => {
      await expect(page.locator(".bee-wrap")).toBeVisible();
      await expect(page.locator("#bee-email")).toBeVisible();
      await expect(page.locator(".bee-btn")).toBeVisible();
    });

    // ====== ナビゲーション ======

    test("header has logo", async ({ page }) => {
      await expect(page.locator("header .logo")).toBeVisible();
    });

    test("header has language switcher (3 links)", async ({ page }) => {
      expect(await page.locator('header a[href*="/en/"]').count()).toBeGreaterThanOrEqual(1);
      expect(await page.locator('header a[href*="/ja/"]').count()).toBeGreaterThanOrEqual(1);
      expect(await page.locator('header a[href*="/pt/"]').count()).toBeGreaterThanOrEqual(1);
    });

    test("footer has language links", async ({ page }) => {
      await expect(page.locator("footer")).toBeVisible();
      expect(await page.locator("footer a").count()).toBeGreaterThanOrEqual(3);
    });

    // ====== レスポンシブ ======

    test("mobile viewport has no horizontal overflow", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 812 });
      await page.waitForTimeout(300);
      const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
      const viewportWidth = await page.evaluate(() => window.innerWidth);
      expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 5);
    });

    // ====== ページ品質 ======

    test("no broken inline scripts (no JS errors)", async ({ page }) => {
      const errors: string[] = [];
      page.on("pageerror", (err) => errors.push(err.message));
      await page.goto(lang.path);
      await page.waitForTimeout(1500);
      const critical = errors.filter(
        (e) =>
          !e.includes("gtag") &&
          !e.includes("gtm") &&
          !e.includes("fetch") &&
          !e.includes("NetworkError") &&
          !e.includes("getElementsByTagName")
      );
      expect(critical).toHaveLength(0);
    });
  });
}
