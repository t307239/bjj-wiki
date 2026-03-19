import { defineConfig, devices } from "@playwright/test";
import path from "path";

/**
 * BJJ Wiki — Playwright E2E テスト設定
 *
 * 静的HTMLファイルをローカルHTTPサーバーで配信してテスト。
 *
 * 実行方法:
 *   npx playwright test              # 全テスト
 *   npx playwright test --headed     # ブラウザ表示
 *   npx playwright test e2e/index.spec.ts  # 特定ファイル
 *
 * セットアップ:
 *   npm init -y && npm install --save-dev @playwright/test
 *   npx playwright install chromium
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: "http://localhost:8787",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "mobile",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 375, height: 812 },
        isMobile: true,
      },
    },
  ],
  webServer: {
    command: `npx serve . -l 8787 --no-clipboard`,
    url: "http://localhost:8787",
    reuseExistingServer: !process.env.CI,
    timeout: 15_000,
  },
});
