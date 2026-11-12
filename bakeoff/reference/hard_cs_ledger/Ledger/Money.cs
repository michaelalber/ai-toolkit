namespace Ledger;

/// <summary>An amount in a currency. Create values with <see cref="Of"/>.</summary>
public readonly record struct Money(decimal Amount, string Currency)
{
    public static Money Of(decimal amount, string currency)
    {
        if (currency is null || currency.Length != 3 || !currency.All(c => c is >= 'A' and <= 'Z'))
            throw new ArgumentException($"Invalid currency '{currency}'", nameof(currency));
        return new Money(Math.Round(amount, 2, MidpointRounding.ToEven), currency);
    }

    public Money Add(Money other) => Of(Amount + SameCurrency(other).Amount, Currency);

    public Money Subtract(Money other) => Of(Amount - SameCurrency(other).Amount, Currency);

    public Money[] Allocate(params int[] ratios)
    {
        if (ratios is null || ratios.Length == 0 || ratios.Any(r => r < 0) || ratios.Sum() <= 0)
            throw new ArgumentException("Ratios must be non-empty, non-negative, with a positive sum", nameof(ratios));
        if (Amount < 0)
            throw new InvalidOperationException("Cannot allocate a negative amount");

        long cents = (long)(Amount * 100m);
        long total = ratios.Sum();
        var parts = ratios.Select(r => cents * r / total).ToArray();
        long left = cents - parts.Sum();
        var order = Enumerable.Range(0, ratios.Length)
            .Where(i => ratios[i] > 0)
            .OrderByDescending(i => ratios[i])
            .ThenBy(i => i);
        foreach (var i in order)
        {
            if (left == 0) break;
            parts[i]++;
            left--;
        }
        var currency = Currency;
        return parts.Select(c => Of(c / 100m, currency)).ToArray();
    }

    private Money SameCurrency(Money other) => other.Currency == Currency
        ? other
        : throw new InvalidOperationException($"Currency mismatch: {Currency} vs {other.Currency}");
}
