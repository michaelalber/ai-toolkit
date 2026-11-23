// <AI-Generated START>
// Held-out tests: same spec as LedgerTests.cs, new inputs. Never copied into the model's workdir.
using Ledger;

namespace Ledger.Tests;

public class HiddenMoneyTests
{
    [Theory]
    [InlineData("0.125", "0.12")]
    [InlineData("0.135", "0.14")]
    [InlineData("-2.345", "-2.34")]
    [InlineData("7", "7.00")]
    public void Of_BankersRounding_MoreCases(string input, string expected) =>
        Assert.Equal(decimal.Parse(expected), Money.Of(decimal.Parse(input), "GBP").Amount);

    [Fact]
    public void Of_RejectsNonAsciiUppercase() =>
        Assert.Throws<ArgumentException>(() => Money.Of(1m, "ÉUR"));

    [Fact]
    public void Subtract_RoundsAndChecksCurrency()
    {
        Assert.Equal(Money.Of(-0.5m, "USD"), Money.Of(1m, "USD").Subtract(Money.Of(1.5m, "USD")));
        Assert.Throws<InvalidOperationException>(() => Money.Of(1m, "USD").Subtract(Money.Of(1m, "JPY")));
    }

    [Fact]
    public void Allocate_TieBreaksToLowerIndexAmongLargestRatios()
    {
        // 11 cents by 2:2:1 truncates to 4+4+2; the one leftover cent goes to index 0, not index 1.
        var parts = Money.Of(0.11m, "USD").Allocate(2, 2, 1);
        Assert.Equal(new[] { 0.05m, 0.04m, 0.02m }, parts.Select(p => p.Amount));
    }

    [Fact]
    public void Allocate_ZeroAmountGivesZeros()
    {
        var parts = Money.Of(0m, "USD").Allocate(2, 1);
        Assert.Equal(new[] { 0m, 0m }, parts.Select(p => p.Amount));
    }

    [Fact]
    public void Allocate_SingleRatioReturnsWhole()
    {
        var parts = Money.Of(9.99m, "EUR").Allocate(7);
        Assert.Equal(new[] { 9.99m }, parts.Select(p => p.Amount));
        Assert.Equal("EUR", parts[0].Currency);
    }

    [Fact]
    public void Allocate_ZeroRatioNeverGetsLeftover()
    {
        var parts = Money.Of(0.02m, "USD").Allocate(0, 1, 1, 1);
        Assert.Equal(new[] { 0m, 0.01m, 0.01m, 0m }, parts.Select(p => p.Amount));
    }
}

public class HiddenLedgerBookTests
{
    private static readonly DateOnly D1 = new(2026, 4, 1);
    private static readonly DateOnly D2 = new(2026, 4, 2);
    private static readonly DateOnly D3 = new(2026, 4, 3);

    private static Money Usd(decimal a) => Money.Of(a, "USD");

    private static LedgerBook Book()
    {
        var b = new LedgerBook();
        b.OpenAccount("a", "USD");
        b.OpenAccount("b", "USD", overdraftLimit: 10m);
        return b;
    }

    [Fact]
    public void Transfer_ToExactOverdraftLimitIsAllowed()
    {
        var b = Book();
        Assert.Equal(PostingResult.Posted, b.Transfer("t1", "b", "a", Usd(10m), D1));
        Assert.Equal(-10m, b.Balance("b"));
    }

    [Fact]
    public void Transfer_UnknownAccounts_Throw()
    {
        var b = Book();
        Assert.Throws<KeyNotFoundException>(() => b.Transfer("t1", "a", "ghost", Usd(1m), D1));
        Assert.Throws<KeyNotFoundException>(() => b.Transfer("t2", "ghost", "a", Usd(1m), D1));
    }

    [Fact]
    public void Transfer_NonPositiveAmount_Throws()
    {
        var b = Book();
        b.Deposit("d", "a", Usd(5m), D1);
        Assert.Throws<ArgumentException>(() => b.Transfer("t1", "a", "b", Usd(-1m), D1));
    }

    [Fact]
    public void KeysAreSharedAcrossDepositsAndTransfers()
    {
        var b = Book();
        b.Transfer("k", "b", "a", Usd(1m), D1);
        Assert.Throws<InvalidOperationException>(() => b.Deposit("k", "a", Usd(1m), D1));
        Assert.Throws<InvalidOperationException>(() => b.Transfer("k", "b", "a", Usd(1m), D2));
        Assert.Throws<InvalidOperationException>(() => b.Transfer("k", "a", "b", Usd(1m), D1));
        Assert.Equal(PostingResult.Duplicate, b.Transfer("k", "b", "a", Usd(1m), D1));
        Assert.Equal(1m, b.Balance("a"));
    }

    [Fact]
    public void FailedValidation_DoesNotConsumeKey()
    {
        var b = Book();
        Assert.Throws<ArgumentException>(() => b.Deposit("k", "a", Usd(0m), D1));
        Assert.Equal(PostingResult.Posted, b.Deposit("k", "a", Usd(3m), D1));
    }

    [Fact]
    public void BlankKeyIsRejectedForTransfers()
    {
        var b = Book();
        Assert.Throws<ArgumentException>(() => b.Transfer("  ", "b", "a", Usd(1m), D1));
    }

    [Fact]
    public void Statement_StartsFromBalanceBeforeRangeAndKeepsPostingOrderWithinADay()
    {
        var b = Book();
        b.Deposit("x1", "a", Usd(50m), D3);
        b.Deposit("x2", "a", Usd(20m), D1);
        b.Transfer("x3", "a", "b", Usd(5m), D3);
        b.Deposit("x4", "a", Usd(1m), D2);

        var lines = b.Statement("a", D2, D3);

        Assert.Equal(new[] { "x4", "x1", "x3" }, lines.Select(l => l.Key));
        Assert.Equal(new[] { 21m, 71m, 66m }, lines.Select(l => l.RunningBalance));
    }

    [Fact]
    public void Statement_SingleDayRangeAndEmptyRange()
    {
        var b = Book();
        b.Deposit("d", "a", Usd(4m), D2);
        Assert.Single(b.Statement("a", D2, D2));
        Assert.Empty(b.Statement("a", D3, D3));
    }
}
// <AI-Generated END>
