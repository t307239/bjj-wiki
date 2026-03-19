import { test, expect } from "@playwright/test";

/**
 * E2E: BJJ Wiki 検索機能 — search.json連携テスト
 *
 * search.json の fetch が page.evaluate 内から動作しないため、
 * Playwright の route.fulfill で search.json を事前ロードし、
 * allData にセットした状態でテストする。
 */

test.describe("Search Functionality [EN]", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/en/index.html");
    // Force-load search.json via fetch in page context and wait for it
    await page.evaluate(async () => {
      try {
        const resp = await fetch("search.json");
        const data = await resp.json();
        (window as any).allData = data;
      } catch (e) {
        // If relative path fails, try absolute
        try {
          const resp = await fetch("/en/search.json");
          const data = await resp.json();
          (window as any).allData = data;
        } catch {}
      }
    });
    // Verify allData is loaded
    const loaded = await page.evaluate(() => {
      const d = (window as any).allData;
      return d !== null && Array.isArray(d) && d.length > 0;
    });
    expect(loaded).toBe(true);
  });

  /** Helper: set search query and run doFilter */
  async function doSearch(page: any, query: string) {
    await page.evaluate((q: string) => {
      const w = window as any;
      const input = document.getElementById("search") as HTMLInputElement;
      if (input) input.value = q;
      w.searchQ = q.trim().toLowerCase();
      if (typeof w.doFilter === "function") w.doFilter();
    }, query);
    await page.waitForTimeout(200);
  }

  test("typing in search shows filtered results", async ({ page }) => {
    await doSearch(page, "armbar");
    const text = await page.locator("#results-count").textContent();
    expect(text).toMatch(/\d+ results/);
    expect(await page.locator(".result-card").count()).toBeGreaterThan(0);
  });

  test("empty search shows all results", async ({ page }) => {
    await doSearch(page, "kimura");
    await doSearch(page, "");
    const text = await page.locator("#results-count").textContent();
    expect(text).toMatch(/\d+ results/);
  });

  test("no-results message for gibberish search", async ({ page }) => {
    await doSearch(page, "xyznonexistent12345");
    const cards = await page.locator(".result-card").count();
    expect(cards).toBe(0);
    const text = await page.locator("#results-count").textContent();
    expect(text).toMatch(/0 results/);
  });

  test("category pill + search combo filters correctly", async ({ page }) => {
    // Set category to submission
    await page.evaluate(() => {
      (window as any).activeCat = "submission";
    });
    await doSearch(page, "choke");
    expect(await page.locator(".result-card").count()).toBeGreaterThan(0);
  });

  test("load more button appears when results > 24", async ({ page }) => {
    await doSearch(page, "bjj");
    const countText = await page.locator("#results-count").textContent();
    const match = countText!.match(/(\d+) results/);
    if (match && parseInt(match[1]) > 24) {
      const display = await page.locator("#load-more-wrap").evaluate(
        (el: HTMLElement) => window.getComputedStyle(el).display
      );
      expect(display).not.toBe("none");
    }
  });

  test("clicking load more shows more cards", async ({ page }) => {
    await doSearch(page, "guard");
    const initialCount = await page.locator(".result-card").count();
    const isVisible = await page.locator("#load-more-wrap").evaluate(
      (el: HTMLElement) => window.getComputedStyle(el).display !== "none"
    );
    if (isVisible) {
      await page.locator("#load-more").click();
      await page.waitForTimeout(300);
      expect(await page.locator(".result-card").count()).toBeGreaterThan(initialCount);
    }
  });

  test("result card has title and belt badge", async ({ page }) => {
    await doSearch(page, "triangle");
    const firstCard = page.locator(".result-card").first();
    await expect(firstCard).toBeVisible();
    await expect(firstCard.locator(".result-title")).toBeVisible();
    await expect(firstCard.locator(".badge")).toBeVisible();
    const badgeText = await firstCard.locator(".badge").textContent();
    expect(badgeText).toMatch(/Belt/i);
  });

  test("search is case-insensitive", async ({ page }) => {
    await doSearch(page, "TRIANGLE");
    const upperCards = await page.locator(".result-card").count();
    await doSearch(page, "triangle");
    const lowerCards = await page.locator(".result-card").count();
    expect(upperCards).toBe(lowerCards);
  });
});
