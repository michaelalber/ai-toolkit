# Component templates — presentational, container, form

Skeletons for the three common component kinds. TypeScript `strict` assumed. Drive the real
implementation test-first; these establish the contract and the a11y/test baseline.

## Presentational (default)

```vue
<!-- UserCard.vue -->
<script setup lang="ts">
export type UserCardProps = {
  name: string;
  email: string;
};
defineProps<UserCardProps>();
const emit = defineEmits<{ message: [email: string] }>();
</script>

<template>
  <article class="user-card">
    <h3>{{ name }}</h3>
    <p>{{ email }}</p>
    <button type="button" @click="emit('message', email)">
      Message {{ name }}
    </button>
  </article>
</template>
```

```ts
// UserCard.test.ts (co-located)
import { render, screen } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import UserCard from "./UserCard.vue";

test("emits message with the email", async () => {
  const { emitted } = render(UserCard, { props: { name: "Ada", email: "ada@x.dev" } });
  await userEvent.click(screen.getByRole("button", { name: /message ada/i }));
  expect(emitted().message[0]).toEqual(["ada@x.dev"]);
});
```

## Container (wires data → presentational)

```vue
<!-- UserCardContainer.vue -->
<script setup lang="ts">
import { useUserQuery } from "@/features/users";
import UserCard from "./UserCard.vue";

const props = defineProps<{ userId: string }>();
const { data: user, isLoading, isError } = useUserQuery(props.userId);
</script>

<template>
  <p v-if="isLoading">Loading…</p>
  <p v-else-if="isError || !user" role="alert">Could not load user.</p>
  <UserCard v-else :name="user.name" :email="user.email" />
</template>
```

## Form (controlled + boundary validation)

```vue
<!-- CreateUserForm.vue -->
<script setup lang="ts">
import { ref } from "vue";

const emit = defineEmits<{ submit: [input: { name: string; email: string }] }>();

const name = ref("");
const email = ref("");

function handleSubmit() {
  emit("submit", { name: name.value, email: email.value });
}
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <label for="name">Name</label>
    <input id="name" v-model="name" required />

    <label for="email">Email</label>
    <input id="email" type="email" v-model="email" required />

    <button type="submit">Create</button>
  </form>
</template>
```

## Story (optional, when Storybook is present)

```ts
// UserCard.stories.ts
import type { Meta, StoryObj } from "@storybook/vue3";
import UserCard from "./UserCard.vue";

const meta: Meta<typeof UserCard> = { component: UserCard };
export default meta;
type Story = StoryObj<typeof UserCard>;

export const Default: Story = { args: { name: "Ada", email: "ada@x.dev" } };
export const NoAction: Story = { args: { name: "Grace", email: "grace@x.dev" } };
```

## `index.ts`

```ts
export { default as UserCard } from "./UserCard.vue";
export type { UserCardProps } from "./UserCard.vue";
```

## Notes

- Default to presentational. Reach for a container only when the component needs data/state.
- Every input has an associated `<label for>`; every action is a real `<button>`/`<a>`.
- The test asserts behavior by accessible role/name — if the query can't find the element, fix the
  component's accessibility, not just the test.
