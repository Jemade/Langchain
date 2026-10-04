import { test, expect } from "@playwright/test";
test("dispatcher creates, inspects, approves and exports a request", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByLabel("Reviewer token").fill("browser-test-reviewer-token");
  await page.getByRole("button", { name: "Open workspace" }).click();
  await page
    .getByLabel("Request reference", { exact: true })
    .fill("BROWSER-" + Date.now());
  await page
    .getByLabel("Shipment reference", { exact: true })
    .fill("HRE-BROWSER");
  await page
    .getByLabel("Verified report")
    .fill("Carrier reports a delay. No confirmed delivery time.");
  await page.getByRole("button", { name: "Prepare for review" }).click();
  await expect(page.locator("#status")).toHaveText("awaiting review");
  await page.getByText("delay.md · BM25 score", { exact: false }).click();
  await expect(
    page.getByText("SAMPLE POLICY:", { exact: false }).last(),
  ).toBeVisible();
  await page
    .getByLabel("Review notes")
    .fill("Policy checked; carrier confirmation still needed.");
  await page
    .getByRole("button", { name: "Approve draft", exact: true })
    .click();
  await expect(page.locator("#status")).toHaveText("approved");
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download reviewed draft" }).click();
  expect((await download).suggestedFilename()).toMatch(
    /^freightdesk-.*\.json$/,
  );
  await page.screenshot({ path: "../runtime/workspace.png", fullPage: true });
});
