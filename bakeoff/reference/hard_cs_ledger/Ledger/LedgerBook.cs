namespace Ledger;

/// <summary>Single-currency-per-account ledger with idempotent postings.</summary>
public sealed class LedgerBook
{
    private sealed record Account(string Currency, decimal OverdraftLimit);
    private sealed record Entry(string Account, DateOnly Date, string Key, decimal Amount, long Seq);
    private sealed record Fingerprint(string Op, string From, string To, Money Amount, DateOnly Date);

    private readonly Dictionary<string, Account> _accounts = new();
    private readonly Dictionary<string, Fingerprint> _keys = new();
    private readonly List<Entry> _entries = new();
    private long _seq;

    public void OpenAccount(string id, string currency, decimal overdraftLimit = 0m)
    {
        if (string.IsNullOrWhiteSpace(id)) throw new ArgumentException("Account id required", nameof(id));
        if (overdraftLimit < 0) throw new ArgumentOutOfRangeException(nameof(overdraftLimit));
        Money.Of(0m, currency); // validates currency
        if (!_accounts.TryAdd(id, new Account(currency, overdraftLimit)))
            throw new InvalidOperationException($"Account {id} already exists");
    }

    public PostingResult Deposit(string key, string account, Money amount, DateOnly date)
    {
        var fp = new Fingerprint("deposit", "", account, amount, date);
        if (IsDuplicate(key, fp)) return PostingResult.Duplicate;
        CheckAmount(amount, Get(account));
        Record(key, fp, (account, amount.Amount));
        return PostingResult.Posted;
    }

    public PostingResult Transfer(string key, string from, string to, Money amount, DateOnly date)
    {
        if (from == to) throw new ArgumentException("Cannot transfer to the same account");
        var fp = new Fingerprint("transfer", from, to, amount, date);
        if (IsDuplicate(key, fp)) return PostingResult.Duplicate;
        var source = Get(from);
        CheckAmount(amount, source);
        CheckAmount(amount, Get(to));
        if (Balance(from) - amount.Amount < -source.OverdraftLimit) throw new InsufficientFundsException(from);
        Record(key, fp, (from, -amount.Amount), (to, amount.Amount));
        return PostingResult.Posted;
    }

    public decimal Balance(string account)
    {
        Get(account);
        return _entries.Where(e => e.Account == account).Sum(e => e.Amount);
    }

    public decimal BalanceAsOf(string account, DateOnly date)
    {
        Get(account);
        return _entries.Where(e => e.Account == account && e.Date <= date).Sum(e => e.Amount);
    }

    public IReadOnlyList<StatementLine> Statement(string account, DateOnly from, DateOnly to)
    {
        if (from > to) throw new ArgumentException("from must not be after to");
        var running = BalanceAsOf(account, from.AddDays(-1));
        var lines = new List<StatementLine>();
        foreach (var e in _entries.Where(e => e.Account == account && e.Date >= from && e.Date <= to)
                                  .OrderBy(e => e.Date).ThenBy(e => e.Seq))
        {
            running += e.Amount;
            lines.Add(new StatementLine(e.Date, e.Key, e.Amount, running));
        }
        return lines;
    }

    private bool IsDuplicate(string key, Fingerprint fp)
    {
        if (string.IsNullOrWhiteSpace(key)) throw new ArgumentException("Idempotency key required", nameof(key));
        if (!_keys.TryGetValue(key, out var existing)) return false;
        return existing == fp ? true : throw new InvalidOperationException($"Key {key} reused with different arguments");
    }

    private Account Get(string id) =>
        _accounts.TryGetValue(id, out var a) ? a : throw new KeyNotFoundException($"Unknown account {id}");

    private static void CheckAmount(Money amount, Account account)
    {
        if (amount.Amount <= 0) throw new ArgumentException("Amount must be positive");
        if (amount.Currency != account.Currency)
            throw new InvalidOperationException($"Currency {amount.Currency} does not match account {account.Currency}");
    }

    private void Record(string key, Fingerprint fp, params (string Account, decimal Amount)[] legs)
    {
        _keys[key] = fp;
        foreach (var (account, amount) in legs)
            _entries.Add(new Entry(account, fp.Date, key, amount, _seq++));
    }
}
