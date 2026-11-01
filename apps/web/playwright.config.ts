import { defineConfig, devices } from "@playwright/test";

/**
 * Static suite (CI): builds the public demo (into .next-e2e: a custom distDir also holds the export) and serves it, then checks every route, accessibility
 * in both themes and mobile layout. Live suite (local, E2E_LIVE=1): drives the full app against a
 * running API for the upload, review and approval flows.
 */
const demo = process.env.E2E_DEMO === "1";
const live = process.env.E2E_LIVE === "1" || demo;

export default defineConfig({
  testDir: "./e2e",
  testMatch: demo ? /demo\.spec\.ts/ : live ? /live\.spec\.ts/ : /static\.spec\.ts/,
  timeout: live ? 120_000 : 45_000,
  expect: { timeout: 10_000 },
  retries: process.env.CI ? 1 : 0,
  // python http.server resets connections when many workers prefetch at once; 2 workers keep it honest.
  workers: 2,
  reporter: [["list"]],
  use: {
    baseURL: live ? "http://localhost:3000" : "http://127.0.0.1:4173",
    trace: "retain-on-failure",
    ...(demo ? { video: { mode: "on" as const, size: { width: 1280, height: 720 } }, viewport: { width: 1280, height: 720 }, colorScheme: "dark" as const } : {}),
  },
  // CI downloads Playwright's Chromium; locally the installed Google Chrome is used (PW_CHANNEL= to override).
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"], channel: process.env.CI ? undefined : (process.env.PW_CHANNEL ?? "chrome") } }],
  webServer: live
    ? undefined
    : {
        command: "NEXT_PUBLIC_STATIC=1 NEXT_DIST_DIR=.next-e2e npx next build && python3 -m http.server 4173 --directory .next-e2e",
        url: "http://127.0.0.1:4173",
        timeout: 240_000,
        reuseExistingServer: !process.env.CI,
      },
});
