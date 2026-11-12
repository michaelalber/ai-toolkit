namespace Ledger;

/// <summary>An amount in a currency. Create values with <see cref="Of"/>.</summary>
public readonly record struct Money(decimal Amount, string Currency)
{
    public static Money Of(decimal amount, string currency) => throw new NotImplementedException();

    public Money Add(Money other) => throw new NotImplementedException();

    public Money Subtract(Money other) => throw new NotImplementedException();

    public Money[] Allocate(params int[] ratios) => throw new NotImplementedException();
}
