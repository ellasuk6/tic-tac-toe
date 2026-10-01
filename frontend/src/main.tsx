import "./styles/index.css";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router";

import { routes } from "./pages/routes";

const queryClient = new QueryClient();
const router = createBrowserRouter(routes);

const rootElement = document.getElementById("root");
if (rootElement === null) {
  throw new Error('index.html is missing <div id="root">');
}

createRoot(rootElement).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
);
