import path from "node:path";
import { expect, test } from "@playwright/test";

/**
 * Full-app flows against a running API (RL_AUTH_MODE=off) and `next dev`:
 *   E2E_LIVE=1 npx playwright test
 * Uploads the synthetic sample, scores it, reviews an account from the queue, drafts and approves
 * outreach, then deletes the upload so the local workspace is left as it was.
 */
const SAMPLE = path.resolve(__dirname, "../public/samples/synthetic_wholesale_invoices.csv");
const API = process.env.E2E_API ?? "http://localhost:8001";

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => window.localStorage.setItem("rl-tour-done", "1"));
});

test("upload, map, check, score, review, draft, approve", async ({ page, request }) => {
  await page.goto("/upload");
  await page.setInputFiles("#file", SAMPLE);
  await expect(page.getByRole("heading", { name: "Match your columns" })).toBeVisible();
  await page.getByRole("button", { name: "Check the file" }).click();
  await expect(page.getByRole("heading", { name: "Your file is ready to score" })).toBeVisible();
  await expect(page.getByText(/Rows rejected/)).toBeVisible();
  await page.getByRole("button", { name: /^Score \d+ accounts$/ }).click();
  await expect(page.getByRole("heading", { name: /^Scored \d+ accounts$/ })).toBeVisible({ timeout: 90_000 });

  await page.getByRole("link", { name: "Open this week's queue" }).click();
  const first = page.locator(".queue-item").first();
  const id = (await first.locator("strong").innerText()).replace("Account ", "");
  await first.click();
  await page.getByLabel("Decision").selectOption("contact");
  await page.getByLabel("Why").fill("Called after the e2e check");
  await page.getByLabel("Your name or initials").fill("E2E");
  await page.getByRole("button", { name: "Save decision" }).click();
  await expect(page.getByText("Called after the e2e check")).toBeVisible();

  const draft = await (await request.post(`${API}/api/drafts`, { data: { customer_id: id, tone: "brief" } })).json();
  expect(["pending_approval", "needs_revision"]).toContain(draft.status);
  const decision = await request.post(`${API}/api/drafts/${draft.id}/decision`, {
    headers: { "Idempotency-Key": `e2e-${Date.now()}` },
    data: { decision: "approve", recipient_type: "company", consent_basis: "legitimate_interest_b2b", acknowledge_review: true },
  });
  expect([200, 422]).toContain(decision.status());

  const datasets = await (await request.get(`${API}/api/datasets`)).json();
  for (const ds of datasets.filter((d: { filename: string }) => d.filename === "synthetic_wholesale_invoices.csv")) {
    await request.post(`${API}/api/datasets/${ds.id}/delete`, { data: {} });
  }
});
