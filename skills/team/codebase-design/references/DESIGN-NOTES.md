# Design notes — testability, rejected framings, relationships

Companion depth for `../SKILL.md`. Load when you need the testability heuristics, the
disambiguation of rejected framings, or the relational map of the vocabulary.

## Designing for testability

Good interfaces make testing natural:

1. **Accept dependencies, don't create them.**

   ```typescript
   function processOrder(order, paymentGateway) {}   // testable
   function processOrder(order) {                     // hard to test
     const gateway = new StripeGateway();
   }
   ```

2. **Return results, don't produce side effects.**

   ```typescript
   function calculateDiscount(cart): Discount {}      // testable
   function applyDiscount(cart): void {               // hard to test
     cart.total -= discount;
   }
   ```

3. **Small surface area.** Fewer methods = fewer tests needed. Fewer params = simpler test
   setup.

## Rejected framings

- **Depth as a ratio of implementation-lines to interface-lines** (Ousterhout's original):
  rewards padding the implementation. Use depth-as-leverage instead.
- **"Interface" as the TypeScript `interface` keyword or a class's public methods**: too
  narrow — interface here includes *every* fact a caller must know.
- **"Boundary"**: overloaded with DDD's bounded context. Say **seam** or **interface**.

## Relationships

- A **Module** has exactly one **Interface** (the surface it presents to callers and tests).
- **Depth** is a property of a **Module**, measured against its **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for maintainers.
