# Project structure & app-shell files

Full contents for the app shell. TypeScript `strict`. Replace `<app-name>` as needed.

## Directory layout

```
<app-name>/
├── src/
│   ├── app/
│   │   ├── App.vue
│   │   └── routes.ts
│   ├── features/            # vue-feature-slice drops slices here
│   ├── shared/
│   │   └── http.ts          # shared API client (placeholder)
│   ├── test/
│   │   └── setup.ts
│   ├── main.ts
│   └── vite-env.d.ts
├── .env.example
├── .prettierrc
├── eslint.config.js
├── tsconfig.json
├── vite.config.ts
└── vitest.config.ts         # or `test` block inside vite.config.ts
```

## `src/main.ts`

```ts
import { createApp } from "vue";
import App from "./app/App.vue";
import { router } from "./app/routes";

const app = createApp(App);

app.config.errorHandler = (error, instance, info) => {
  // Route to your logger here; never log secrets/PII.
  console.error("Unhandled error", error, info);
};

app.use(router);
app.mount("#app");
```

## `src/app/App.vue` — shell

```vue
<script setup lang="ts"></script>

<template>
  <router-view />
</template>
```

## `src/app/routes.ts` — typed route table

```ts
import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";

const Home = { template: "<main><h1>Home</h1></main>" };
const NotFound = { template: "<main><h1>404 — Not found</h1></main>" };

const routes: RouteRecordRaw[] = [
  { path: "/", component: Home },
  // feature routes: { path: "/orders", component: OrdersPage } via the feature barrel
  { path: "/:pathMatch(.*)*", component: NotFound },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
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

## Smoke test — `src/app/App.test.ts`

```ts
import { render, screen } from "@testing-library/vue";
import App from "./App.vue";
import { router } from "./routes";

test("home renders a heading", async () => {
  router.push("/");
  await router.isReady();
  render(App, { global: { plugins: [router] } });
  expect(await screen.findByRole("heading", { name: /home/i })).toBeInTheDocument();
});
```
