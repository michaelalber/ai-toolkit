namespace Ledger;

/// <summary>Single-currency-per-account ledger with idempotent postings.</summary>
public sealed class LedgerBook
{
    public void OpenAccount(string id, string currency, decimal overdraftLimit = 0m) =>
        throw new NotImplementedException();

    public PostingResult Deposit(string key, string account, Money amount, DateOnly date) =>
        throw new NotImplementedException();

    public PostingResult Transfer(string key, string from, string to, Money amount, DateOnly date) =>
        throw new NotImplementedException();

    public decimal Balance(string account) => throw new NotImplementedException();

    public decimal BalanceAsOf(string account, DateOnly date) => throw new NotImplementedException();

    public IReadOnlyList<StatementLine> Statement(string account, DateOnly from, DateOnly to) =>
        throw new NotImplementedException();
}
