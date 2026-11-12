namespace Ledger;

/// <summary>Outcome of a deposit or transfer.</summary>
public enum PostingResult { Posted, Duplicate }

/// <summary>One statement row. <see cref="Amount"/> is signed: positive in, negative out.</summary>
public sealed record StatementLine(DateOnly Date, string Key, decimal Amount, decimal RunningBalance);

/// <summary>A transfer would take the source account below its overdraft limit.</summary>
public sealed class InsufficientFundsException(string account)
    : InvalidOperationException($"Insufficient funds in account {account}")
{
    public string Account { get; } = account;
}
