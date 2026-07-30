# Project structure & app-shell files

Full contents for the app shell. TypeScript `strict`. Replace `<app-name>` as needed.

## Directory layout

```
<app-name>/
├── src/
│   ├── app/
│   │   ├── App.tsx
│   │   ├── routes.tsx
│   │   └── ErrorBoundary.tsx
│   ├── features/            # react-feature-slice drops slices here
│   ├── shared/
│   │   └── http.ts          # shared API client (placeholder)
│   ├── test/
│   │   └── setup.ts
│   ├── main.tsx
│   └── vite-env.d.ts
├── .env.example
├── .prettierrc
├── eslint.config.js
├── tsconfig.json
├── vite.config.ts
└── vitest.config.ts         # or `test` block inside vite.config.ts
```

## `src/main.tsx`

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./app/App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

## `src/app/App.tsx` — shell

```tsx
import { RouterProvider } from "react-router-dom";
import { ErrorBoundary } from "./ErrorBoundary";
import { router } from "./routes";

export function App() {
  return (
    <ErrorBoundary>
      <RouterProvider router={router} />
    </ErrorBoundary>
  );
}
```

## `src/app/routes.tsx` — typed route table

```tsx
import { createBrowserRouter } from "react-router-dom";

function Home() {
  return <main><h1>Home</h1></main>;
}

function NotFound() {
  return <main><h1>404 — Not found</h1></main>;
}

export const router = createBrowserRouter([
  { path: "/", element: <Home /> },
  // feature routes: { path: "/orders", element: <OrdersPage /> } via the feature barrel
  { path: "*", element: <NotFound /> },
]);
```

## `src/app/ErrorBoundary.tsx`

```tsx
import { Component, type ReactNode } from "react";

type Props = { children: ReactNode };
type State = { hasError: boolean };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: unknown) {
    // Route to your logger here; never log secrets/PII.
    console.error("Unhandled error", error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <main role="alert">
          <h1>Something went wrong.</h1>
          <button type="button" onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </main>
      );
    }
    return this.props.children;
  }
}
```

## `src/shared/http.ts` — placeholder API client

```ts
const BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

export const http = {
  async get(path: string) {
    const res = await fetch(`${BASE}${path}`, { credentials: "include" });
    if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
    return { data: await res.json() };
  },
  async post(path: string, body: unknown) {
    const res = await fetch(`${BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
    return { data: await res.json() };
  },
};
```

## `src/vite-env.d.ts` — typed env

```ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  // Add only PUBLIC values here. Secrets never get a VITE_ prefix.
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

## `.env.example`

```
VITE_API_BASE_URL=http://localhost:8000/api
# Never put secrets in VITE_* — they ship to the browser.
```

## Smoke test — `src/app/App.test.tsx`

```tsx
import { render, screen } from "@testing-library/react";
import { Home } from "./routes"; // export Home if you want to test it directly

test("home renders a heading", () => {
  render(<main><h1>Home</h1></main>);
  expect(screen.getByRole("heading", { name: /home/i })).toBeInTheDocument();
});
```
