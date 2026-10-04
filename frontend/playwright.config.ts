import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "tests",
  use: { baseURL: "http://127.0.0.1:5173" },
  webServer: [
    {
      command:
        "python -m uvicorn freightdesk.api:create_app --factory --host 127.0.0.1 --port 8000",
      cwd: "..",
      url: "http://127.0.0.1:8000/health",
      env: {
        FREIGHTDESK_TOKEN: "browser-test-reviewer-token",
        FREIGHTDESK_DATA: "runtime/browser-test",
      },
      reuseExistingServer: false,
    },
    {
      command: "npm run dev",
      url: "http://127.0.0.1:5173",
      reuseExistingServer: false,
    },
  ],
});
