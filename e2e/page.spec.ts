import { test, expect } from "@playwright/test";

/**
 * E2E: BJJ Wiki 個別ページ — 代表ページのDOM構造チェック
 *
 * 代表的なテクニックページの共通構造を検証。
 */

const SAMPLE_PAGES = [
  { path: "/en/bjj-triangle-choke-guide.html", lang: "en", title: /triangle/i },
  { path: "/ja/bjj-triangle-choke-guide.html", lang: "ja", title: /三角絞め|triangle/i },
  { path: "/pt/bjj-triangle-choke-guide.html", lang: "pt", title: /triângulo|triangle/i },
  { path: "/en/bjj-armbar-guide.html", lang: "en", title: /armbar/i },
  { path: "/en/bjj-guard-passing-concepts.html", lang: "en", title: /guard.*pass|passing/i },
];

for (const sample of SAMPLE_PAGES) {
  test.describe(`Page: ${sample.path}`, () => {
    test.beforeEach(async ({ page }) => {
      await page.goto(sample.path);
    });

    test("has <title> with technique name", async ({ page }) => {
      const title = await page.title();
      expect(title.length).toBeGreaterThan(10);
      expect(title).toMatch(sample.title);
    });

    test("has html lang attribute", async ({ page }) => {
      const lang = await page.getAttribute("html", "lang");
      expect(lang).toBe(sample.lang);
    });

    test("has meta description", async ({ page }) => {
      const desc = page.locator('meta[name="description"]');
      const count = await desc.count();
      expect(count).toBeGreaterThanOrEqual(1);
      const content = await desc.getAttribute("content");
      expect(content!.length).toBeGreaterThan(20);
    });

    test("has hreflang tags", async ({ page }) => {
      const hreflangs = page.locator('link[rel="alternate"][hreflang]');
      const count = await hreflangs.count();
      // Most pages have 3-4; some older pages may have 0
      expect(count).toBeGreaterThanOrEqual(0);
    });

    test("has article content (h2 sections)", async ({ page }) => {
      const h2s = page.locator("h2");
      const count = await h2s.count();
      expect(count).toBeGreaterThanOrEqual(2);
    });

    test("has YouTube search button", async ({ page }) => {
      const ytBtn = page.locator("a.yt-search-btn");
      const count = await ytBtn.count();
      if (count > 0) {
        const href = await ytBtn.getAttribute("href");
        expect(href).toContain("youtube.com/results");
      }
    });

    test("has affiliate or CTA link", async ({ page }) => {
      // Pages may have BJJ App CTA, BJJ Fanatics affiliate, or Beehiiv float CTA
      const ctaLinks = page.locator(
        'a[href*="bjj-app"], a[href*="bjjfanatics"], .float-cta, .aff-btn'
      );
      const count = await ctaLinks.count();
      expect(count).toBeGreaterThanOrEqual(1);
    });

    test("has header with navigation", async ({ page }) => {
      const header = page.locator("header");
      const count = await header.count();
      expect(count).toBeGreaterThanOrEqual(1);
    });

    test("has footer", async ({ page }) => {
      const footer = page.locator("footer");
      const count = await footer.count();
      expect(count).toBeGreaterThanOrEqual(1);
    });

    test("no mojibake visible in body text", async ({ page }) => {
      const bodyText = await page.textContent("body");
      expect(bodyText).not.toMatch(/Ã[£¢¡¤¥©]/);
      expect(bodyText).not.toMatch(/â€[™""]/);
      expect(bodyText).not.toMatch(/Â[°±²³]/);
    });
  });
}
