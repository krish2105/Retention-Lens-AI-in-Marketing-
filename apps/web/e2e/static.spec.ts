import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const ROUTES = ["/", "/pricing", "/status", "/signin/", "/legal/privacy/", "/legal/terms/", "/case-study/", "/overview/", "/queue/", "/accounts/", "/segments/",
  "/signals/", "/outreach/", "/product-lab/", "/model-lab/", "/data/", "/upload/", "/evidence/", "/team/", "/privacy/", "/billing/", "/settings/"];
const KEY = ["/", "/pricing/", "/overview/", "/queue/", "/accounts/", "/upload/", "/status/", "/privacy/"];

async function settle(page: Page) {
  await page.addInitScript(() => window.localStorage.setItem("rl-tour-done", "1"));
}

test.describe("every route renders without errors", () => {
  for (const route of ROUTES) {
    test(route, async ({ page }) => {
      const errors: string[] = [];
      page.on("pageerror", (e) => errors.push(e.message));
      // The test server (python http.server) sometimes resets prefetch connections; that is not an app error.
      const serverNoise = /ERR_CONNECTION_RESET|Failed to fetch RSC payload/;
      page.on("console", (m) => { if (m.type() === "error" && !serverNoise.test(m.text())) errors.push(m.text()); });
      await settle(page);
      await page.goto(route);
      await expect(page.locator("h1").first()).toBeVisible();
      await page.waitForLoadState("networkidle");
      expect(errors).toEqual([]);
    });
  }
});

for (const scheme of ["light", "dark"] as const) {
  test.describe(`WCAG 2.2 AA in ${scheme} mode`, () => {
    test.use({ colorScheme: scheme });
    for (const route of KEY) {
      test(route, async ({ page }) => {
        await settle(page);
        await page.goto(route);
        await page.waitForLoadState("networkidle");
        await page.waitForTimeout(600);
        const results = await new AxeBuilder({ page: page as never }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).disableRules(["region"]).analyze();
        expect(results.violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(" ")).join(" | ")}`)).toEqual([]);
      });
    }
  });
}

test.describe("mobile 375px has no horizontal scroll", () => {
  test.use({ viewport: { width: 375, height: 812 } });
  for (const route of KEY) {
    test(route, async ({ page }) => {
      await settle(page);
      await page.goto(route);
      await page.waitForLoadState("networkidle");
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      expect(overflow).toBeLessThanOrEqual(1);
    });
  }
});

test("queue opens an account's evidence", async ({ page }) => {
  await settle(page);
  await page.goto("/queue/");
  const first = page.locator(".queue-item").first();
  await expect(first).toBeVisible();
  await first.click();
  await expect(page.getByRole("heading", { name: /^Account / })).toBeVisible();
  await expect(page.getByText("Why it was flagged")).toBeVisible();
});

test("public demo blocks writes and says why", async ({ page }) => {
  await settle(page);
  await page.goto("/");
  await expect(page.getByText(/cannot store sign-ups/)).toBeVisible();
  await page.goto("/upload/");
  await expect(page.getByText("Uploads need the full app")).toBeVisible();
});

test("onboarding tour can be skipped and stays skipped", async ({ page }) => {
  await page.goto("/overview/");
  await expect(page.getByRole("dialog", { name: "Start with this week" })).toBeVisible();
  await page.getByRole("button", { name: "Skip tour" }).click();
  await page.reload();
  await expect(page.getByRole("dialog")).toHaveCount(0);
});
