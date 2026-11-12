Implement the stubs in `Ledger/Money.cs` and `Ledger/LedgerBook.cs` (C#, .NET 10). `Ledger/Statement.cs` is complete. Run the tests with the `run_tests` tool (it runs `dotnet test` on `Ledger.Tests`). Do not edit anything under `Ledger.Tests/`.

**Money** (`readonly record struct Money(decimal Amount, string Currency)`)
- `Money.Of(amount, currency)`: currency must be exactly 3 uppercase ASCII letters, otherwise `ArgumentException`. Amount is rounded to 2 decimal places with banker's rounding (`2.345 -> 2.34`, `2.355 -> 2.36`).
- `Add` / `Subtract` return a rounded `Money`; a different currency throws `InvalidOperationException`.
- `Allocate(params int[] ratios)` splits the amount into parts that sum **exactly** to it. Each part is first `amount * ratio / sum` truncated to whole cents. Leftover cents then go one at a time to parts with ratio > 0, largest ratio first, ties to the lower index. Ratios must be non-empty, none negative, with a positive sum (`ArgumentException`). A negative amount throws `InvalidOperationException`.

**LedgerBook**
- `OpenAccount(id, currency, overdraftLimit = 0)`: blank id -> `ArgumentException`; bad currency -> `ArgumentException`; negative limit -> `ArgumentOutOfRangeException`; duplicate id -> `InvalidOperationException`.
- `Deposit(key, account, amount, date)` and `Transfer(key, from, to, amount, date)` return `PostingResult.Posted`. Rules:
  - unknown account -> `KeyNotFoundException`; amount <= 0 -> `ArgumentException`; amount currency differs from an involved account's currency -> `InvalidOperationException`; `from == to` -> `ArgumentException`.
  - A transfer may not take the source account's **current total** balance (all dates) below `-overdraftLimit`: throw `InsufficientFundsException`.
  - **Idempotency:** keys share one space across deposits and transfers. Reusing a key with the identical operation and arguments returns `PostingResult.Duplicate` and changes nothing. Reusing it with anything different throws `InvalidOperationException`. A call that throws does not consume its key. A blank key -> `ArgumentException`.
- `Balance(account)`: sum of all entries. `BalanceAsOf(account, date)`: entries dated on or before `date`; entries may be back-dated. Unknown account -> `KeyNotFoundException`.
- `Statement(account, from, to)`: entries with `from <= date <= to`, ordered by date, then by posting order. `Amount` is signed (+ in, - out). `RunningBalance` starts from the balance as of the day before `from`. `from > to` -> `ArgumentException`.
