// Runs before every test file (see `test.setupFiles` in vite.config.ts).
import "@testing-library/jest-dom/vitest";

import { cleanup } from "@testing-library/react";
import { afterAll, afterEach, beforeAll } from "vitest";

import { resetFakeBackend, server } from "./src/test/server";

// MSW intercepts fetch() so tests never need a real backend. Any request
// without a handler fails the test instead of silently hanging.
beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  cleanup();
  server.resetHandlers();
  resetFakeBackend();
});
afterAll(() => server.close());
