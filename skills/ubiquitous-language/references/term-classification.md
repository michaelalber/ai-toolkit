# DDD Term Classification Guide

Examples of each DDD term type to aid extraction and classification.

## Entity

Has a stable identity that persists over time. Two entities with the same attributes
are NOT the same if their identities differ.

Examples:
- `Order` — has OrderId; two orders with same items are different orders
- `Customer` — has CustomerId; identity persists even when address changes
- `Employee` — has EmployeeId; survives attribute changes

Code signals: has an Id field, stored in a database table by row, referenced by FK

## Value Object

Defined entirely by its attributes. No identity. Immutable. Two VOs with identical
attributes ARE the same thing.

Examples:
- `Money(amount=10, currency=USD)` — two Money(10, USD) are equal
- `Address` — defined by street, city, zip; no identity beyond attributes
- `DateRange(start, end)` — defined by its boundaries

Code signals: no Id field, often a record/struct, equality by value

## Aggregate

A cluster of objects treated as a unit for data changes. One root entity controls access.
External objects may only hold a reference to the root.

Examples:
- `Order` aggregate: root=Order, contains OrderLines, ShippingAddress
- `Account` aggregate: root=Account, contains Transactions

Rule: save/load the entire aggregate as one unit. Do not persist child entities separately.

## Domain Event

A fact that happened in the domain. Past tense. Immutable once created.

Examples:
- `OrderPlaced` — happened at a specific point in time
- `PaymentFailed` — captures what went wrong and when
- `CustomerUpgraded` — records the state transition

Code signals: past-tense class name, timestamp field, no setters

## Service

A stateless operation that doesn't naturally belong to any entity or value object.
Operates on domain objects but holds no state itself.

Examples:
- `PricingService.calculateDiscount(order, customer)` — logic spans Order and Customer
- `TransferService.transfer(from, to, amount)` — operates on two Accounts

## Command

An intent to change state. Imperative. May be rejected. Creates a Domain Event if accepted.

Examples:
- `PlaceOrder` → succeeds → emits `OrderPlaced`
- `CancelOrder` → may fail if already shipped → emits `OrderCancelled` or raises error

## Policy

A business rule that reacts to a Domain Event and produces a Command.

Examples:
- When `OrderPlaced`, send confirmation email → `SendConfirmationEmail` command
- When `PaymentFailed` three times, suspend account → `SuspendAccount` command
