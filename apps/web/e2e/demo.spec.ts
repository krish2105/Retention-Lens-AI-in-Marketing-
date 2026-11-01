import path from "node:path";
import { test, type Page } from "@playwright/test";

/**
 * Records a captioned ~90-second walkthrough of the full app (silent; add your own voice-over).
 *   API on :8001 (RL_AUTH_MODE=off) + `npm run dev`, then: E2E_DEMO=1 npx playwright test
 * The video lands in test-results/; scripts copy it to submissions/demo/.
 */
const SAMPLE = path.resolve(__dirname, "../public/samples/synthetic_wholesale_invoices.csv");
const API = process.env.E2E_API ?? "http://localhost:8001";

async function caption(page: Page, text: string, ms = 3200) {
  await page.evaluate((t) => {
    let el = document.getElementById("demo-caption");
    if (!el) {
      el = document.createElement("div");
      el.id = "demo-caption";
      el.style.cssText = "position:fixed;left:50%;top:84px;transform:translateX(-50%);z-index:9999;max-width:80%;padding:12px 20px;border-radius:14px;background:rgba(7,9,18,.86);color:#eef0ff;font:600 20px/1.35 system-ui,sans-serif;text-align:center;box-shadow:0 8px 30px rgba(0,0,0,.4)";
      document.body.appendChild(el);
    }
    el.textContent = t;
  }, text);
  await page.waitForTimeout(ms);
}

test("captioned product walkthrough", async ({ page, request }) => {
  test.setTimeout(240_000);
  await page.addInitScript(() => window.localStorage.setItem("rl-tour-done", "1"));
  await page.goto("/");
  await caption(page, "Trade accounts rarely complain before they leave. They just stop ordering.", 4000);
  await page.mouse.wheel(0, 700);
  await caption(page, "RetentionLens finds them early, explains why, and lets you prove outreach works.");

  await page.goto("/upload");
  await page.locator("#file:not([disabled])").waitFor({ state: "attached" });
  await caption(page, "1 · Upload any invoice export (this file is SYNTHETIC).", 2500);
  await page.setInputFiles("#file", SAMPLE);
  await page.getByRole("heading", { name: "Match your columns" }).waitFor();
  await caption(page, "Columns are matched automatically. You can change any of them.");
  await page.getByRole("button", { name: "Check the file" }).click();
  await page.getByRole("heading", { name: "Your file is ready to score" }).waitFor();
  await caption(page, "Every row that could not be read is listed. Nothing is guessed.");
  await page.getByRole("button", { name: /^Score \d+ accounts$/ }).click();
  await caption(page, "2 · Scoring runs in the background: BG/NBD + Gamma-Gamma with a seasonal correction.", 2500);
  await page.getByRole("heading", { name: /^Scored \d+ accounts$/ }).waitFor({ timeout: 120_000 });
  await caption(page, "Scored, with 80% value ranges checked against the past.");

  await page.getByRole("link", { name: "Open this week's queue" }).click();
  await page.locator(".queue-item").first().waitFor();
  await caption(page, "3 · This week's queue: most spend at risk first. A random fifth is held out to measure impact.", 4200);
  await page.locator(".queue-item").first().click();
  await page.getByText("Why it was flagged").waitFor();
  await caption(page, "Reasons you can say out loud, expected spend with a range, and the order history.", 4200);
  const id = new URL(page.url()).searchParams.get("id") ?? "";

  await page.goto(`/outreach?account=${encodeURIComponent(id)}`);
  await caption(page, "4 · The local AI drafts a check-in from the account's facts only (template mode when the model is offline).", 2500);
  await page.getByLabel("Your initials").first().fill("KM");
  await page.getByRole("button", { name: "Draft email" }).click();
  await page.getByText(/^Draft \d+ · account/).waitFor({ timeout: 90_000 });
  await page.waitForTimeout(1500);
  await caption(page, "Checks block invented numbers, offers, pressure and links. A person approves. There is no send button.", 4500);

  await page.goto("/model-lab");
  await caption(page, "Tested honestly: rolling time cutoffs and a frozen test. Simple models won.", 4000);
  await page.goto("/case-study");
  await caption(page, "Pilot next. Demo and code: retentionlens-demo.vercel.app", 4000);

  for (const ds of await (await request.get(`${API}/api/datasets`)).json()) {
    if (ds.filename === "synthetic_wholesale_invoices.csv") await request.post(`${API}/api/datasets/${ds.id}/delete`, { data: {} });
  }
});
