# Component templates — presentational, container, form

Skeletons for the three common component kinds. TypeScript `strict` assumed. Drive the real
implementation test-first; these establish the contract and the a11y/test baseline.

## Presentational (default)

```tsx
// UserCard.tsx
export type UserCardProps = {
  name: string;
  email: string;
  onMessage?: (email: string) => void;
};

export function UserCard({ name, email, onMessage }: UserCardProps) {
  return (
    <article className="user-card">
      <h3>{name}</h3>
      <p>{email}</p>
      {onMessage && (
        <button type="button" onClick={() => onMessage(email)}>
          Message {name}
        </button>
      )}
    </article>
  );
}
```

```tsx
// UserCard.test.tsx (co-located)
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { UserCard } from "./UserCard";

test("calls onMessage with the email", async () => {
  const onMessage = vi.fn();
  render(<UserCard name="Ada" email="ada@x.dev" onMessage={onMessage} />);
  await userEvent.click(screen.getByRole("button", { name: /message ada/i }));
  expect(onMessage).toHaveBeenCalledWith("ada@x.dev");
});
```

## Container (wires data → presentational)

```tsx
// UserCardContainer.tsx
import { useUserQuery } from "@/features/users";
import { UserCard } from "./UserCard";

export function UserCardContainer({ userId }: { userId: string }) {
  const { data: user, isLoading, isError } = useUserQuery(userId);
  if (isLoading) return <p>Loading…</p>;
  if (isError || !user) return <p role="alert">Could not load user.</p>;
  return <UserCard name={user.name} email={user.email} />;
}
```

## Form (controlled + boundary validation)

```tsx
// CreateUserForm.tsx
import { useState } from "react";

export type CreateUserFormProps = {
  onSubmit: (input: { name: string; email: string }) => void;
};

export function CreateUserForm({ onSubmit }: CreateUserFormProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({ name, email });
  }

  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="name">Name</label>
      <input id="name" value={name} onChange={(e) => setName(e.target.value)} required />

      <label htmlFor="email">Email</label>
      <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />

      <button type="submit">Create</button>
    </form>
  );
}
```

## Story (optional, when Storybook is present)

```tsx
// UserCard.stories.tsx
import type { Meta, StoryObj } from "@storybook/react";
import { UserCard } from "./UserCard";

const meta: Meta<typeof UserCard> = { component: UserCard };
export default meta;
type Story = StoryObj<typeof UserCard>;

export const Default: Story = { args: { name: "Ada", email: "ada@x.dev" } };
export const NoAction: Story = { args: { name: "Grace", email: "grace@x.dev" } };
```

## `index.ts`

```ts
export { UserCard } from "./UserCard";
export type { UserCardProps } from "./UserCard";
```

## Notes

- Default to presentational. Reach for a container only when the component needs data/state.
- Every input has an associated `<label htmlFor>`; every action is a real `<button>`/`<a>`.
- The test asserts behavior by accessible role/name — if the query can't find the element, fix the
  component's accessibility, not just the test.
