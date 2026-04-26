# Naming and Language Alignment Guide

How to align code naming with the ubiquitous language established in CONTEXT.md
and UBIQUITOUS_LANGUAGE.md.

## The Naming Rule

Every class, method, and variable name should use a term from the ubiquitous language,
or be self-evidently composed of such terms. If a name can't be explained using
domain vocabulary, it's a signal the name (or the concept) needs work.

## Anti-patterns to rename

| Anti-pattern | Why it fails | Fix |
|-------------|-------------|-----|
| `Manager` | Vague — manages what? How? | `OrderProcessor`, `AccountService`, `SessionRegistry` |
| `Helper` | No domain meaning | Name by what it does: `TaxCalculator`, `AddressFormatter` |
| `Util` / `Utils` | Grab-bag — hides design decisions | Extract into purpose-named modules |
| `Data` | Every object is data | Name by domain concept: `OrderDetails`, `CustomerProfile` |
| `Info` | Same as Data | `ShippingAddress`, `PaymentMethod` |
| `Handler` | Vague without context | `OrderCreatedHandler` (include the event it handles) |
| `Processor` | What does it process? | Use the domain noun: `InvoiceGenerator`, `ClaimEvaluator` |
| Generic type names | `T`, `item`, `obj` | Name by role: `order`, `customer`, `paymentAttempt` |

## Naming by type

### Entities
Name by the domain concept they represent. Singular noun.
`Order`, `Customer`, `Employee`, `Invoice`

### Value Objects
Name by what they measure or describe.
`Money`, `EmailAddress`, `DateRange`, `Coordinates`

### Domain Events (past tense)
`OrderPlaced`, `PaymentFailed`, `CustomerUpgraded`, `InventoryDepleted`

### Commands (imperative)
`PlaceOrder`, `CancelSubscription`, `ApproveLeaveRequest`

### Services (verb phrase or noun+Service)
`PricingService`, `NotificationService`, or `calculate_discount()` (action-based)

### Repositories (Aggregate+Repository)
`OrderRepository`, `CustomerRepository` — never `OrderDataAccess` or `OrderDAO`

## Rename procedure

1. Verify the new name is in `CONTEXT.md` or `UBIQUITOUS_LANGUAGE.md`.
   If not: add it to `UBIQUITOUS_LANGUAGE.md` first, with a definition.
2. Use IDE rename refactoring (not find-replace) to catch all usages.
3. Update any documentation, comments, or test names that used the old term.
4. If the old name was part of a public API (HTTP endpoint, event name, DB column):
   - Note the breaking change
   - Plan a migration or versioning strategy before renaming
