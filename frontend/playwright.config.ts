// End-to-end smoke test: a real browser against the real app.
//
// Start the app first (from the repo folder):  docker compose up --build
// Then, from frontend/:                          pnpm test:e2e
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  // Each test starts its own game, but they share one database: keep them in order.
  workers: 1,
  timeout: 30_000,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    // The Docker Compose app by default; override to test something else.
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:8080",
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
