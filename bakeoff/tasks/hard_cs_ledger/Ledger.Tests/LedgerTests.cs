using Ledger;

namespace Ledger.Tests;

public class MoneyTests
{
    [Theory]
    [InlineData("2.345", "2.34")]
    [InlineData("2.355", "2.36")]
    [InlineData("-1.005", "-1.00")]
    public void Of_UsesBankersRounding(string input, string expected)
    {
        var m = Money.Of(decimal.Parse(input), "USD");
        Assert.Equal(decimal.Parse(expected), m.Amount);
    }

    [Theory]
    [InlineData("usd")]
    [InlineData("US")]
    [InlineData("USDX")]
    [InlineData("U$D")]
    [InlineData("")]
    public void Of_RejectsInvalidCurrency(string currency) =>
        Assert.Throws<ArgumentException>(() => Money.Of(1m, currency));

    [Fact]
    public void Add_And_Subtract_SameCurrency()
    {
        var a = Money.Of(10.10m, "EUR");
        Assert.Equal(Money.Of(12.35m, "EUR"), a.Add(Money.Of(2.25m, "EUR")));
        Assert.Equal(Money.Of(7.85m, "EUR"), a.Subtract(Money.Of(2.25m, "EUR")));
    }

    [Fact]
    public void Add_DifferentCurrency_Throws() =>
        Assert.Throws<InvalidOperationException>(() => Money.Of(1m, "USD").Add(Money.Of(1m, "EUR")));

    [Fact]
    public void Allocate_EvenSplit_FirstPartGetsLeftoverCent()
    {
        var parts = Money.Of(100m, "USD").Allocate(1, 1, 1);
        Assert.Equal(new[] { 33.34m, 33.33m, 33.33m }, parts.Select(p => p.Amount));
    }

    [Fact]
    public void Allocate_LeftoverGoesToLargestRatioFirst()
    {
        var parts = Money.Of(0.05m, "USD").Allocate(3, 7);
        Assert.Equal(new[] { 0.01m, 0.04m }, parts.Select(p => p.Amount));
    }

    [Fact]
    public void Allocate_ZeroRatioGetsNothing()
    {
        var parts = Money.Of(0.03m, "USD").Allocate(0, 1, 1);
        Assert.Equal(new[] { 0m, 0.02m, 0.01m }, parts.Select(p => p.Amount));
    }

    [Fact]
    public void Allocate_PartsAlwaysSumToTotal()
    {
        var total = Money.Of(1234.57m, "USD");
        var parts = total.Allocate(5, 3, 3, 1, 9, 2);
        Assert.Equal(total.Amount, parts.Sum(p => p.Amount));
        Assert.All(parts, p => Assert.Equal("USD", p.Currency));
    }

    [Theory]
    [InlineData(new int[0])]
    [InlineData(new[] { 0, 0 })]
    [InlineData(new[] { 2, -1 })]
    public void Allocate_InvalidRatios_Throw(int[] ratios) =>
        Assert.Throws<ArgumentException>(() => Money.Of(10m, "USD").Allocate(ratios));

    [Fact]
    public void Allocate_NegativeAmount_Throws() =>
        Assert.Throws<InvalidOperationException>(() => Money.Of(-10m, "USD").Allocate(1, 1));
}

public class LedgerBookTests
{
    private static readonly DateOnly D1 = new(2026, 3, 1);
    private static readonly DateOnly D2 = new(2026, 3, 2);
    private static readonly DateOnly D3 = new(2026, 3, 3);

    private static Money Usd(decimal a) => Money.Of(a, "USD");

    private static LedgerBook Book()
    {
        var b = new LedgerBook();
        b.OpenAccount("alice", "USD");
        b.OpenAccount("bob", "USD", overdraftLimit: 50m);
        b.OpenAccount("eve", "EUR");
        return b;
    }

    [Fact]
    public void OpenAccount_Validation()
    {
        var b = Book();
        Assert.Throws<InvalidOperationException>(() => b.OpenAccount("alice", "USD"));
        Assert.Throws<ArgumentException>(() => b.OpenAccount(" ", "USD"));
        Assert.Throws<ArgumentException>(() => b.OpenAccount("x", "usd"));
        Assert.Throws<ArgumentOutOfRangeException>(() => b.OpenAccount("y", "USD", -1m));
    }

    [Fact]
    public void Deposit_And_Transfer_MoveBalances()
    {
        var b = Book();
        Assert.Equal(PostingResult.Posted, b.Deposit("k1", "alice", Usd(100m), D1));
        Assert.Equal(PostingResult.Posted, b.Transfer("k2", "alice", "bob", Usd(30.25m), D2));
        Assert.Equal(69.75m, b.Balance("alice"));
        Assert.Equal(30.25m, b.Balance("bob"));
    }

    [Fact]
    public void Posting_Validation()
    {
        var b = Book();
        b.Deposit("k1", "alice", Usd(10m), D1);
        Assert.Throws<KeyNotFoundException>(() => b.Deposit("k2", "nobody", Usd(1m), D1));
        Assert.Throws<ArgumentException>(() => b.Deposit("k3", "alice", Usd(0m), D1));
        Assert.Throws<InvalidOperationException>(() => b.Deposit("k4", "alice", Money.Of(1m, "EUR"), D1));
        Assert.Throws<InvalidOperationException>(() => b.Transfer("k5", "alice", "eve", Usd(1m), D1));
        Assert.Throws<ArgumentException>(() => b.Transfer("k6", "alice", "alice", Usd(1m), D1));
        Assert.Throws<ArgumentException>(() => b.Deposit("", "alice", Usd(1m), D1));
        Assert.Equal(10m, b.Balance("alice"));
    }

    [Fact]
    public void Transfer_RespectsOverdraftLimit()
    {
        var b = Book();
        Assert.Throws<InsufficientFundsException>(() => b.Transfer("k1", "alice", "bob", Usd(0.01m), D1));
        Assert.Equal(PostingResult.Posted, b.Transfer("k2", "bob", "alice", Usd(50m), D1));
        Assert.Equal(-50m, b.Balance("bob"));
        var ex = Assert.Throws<InsufficientFundsException>(() => b.Transfer("k3", "bob", "alice", Usd(0.01m), D1));
        Assert.Equal("bob", ex.Account);
    }

    [Fact]
    public void Overdraft_UsesCurrentTotal_NotTransferDate()
    {
        var b = Book();
        b.Deposit("k1", "alice", Usd(100m), D3);
        Assert.Equal(PostingResult.Posted, b.Transfer("k2", "alice", "bob", Usd(100m), D1));
        Assert.Equal(-100m, b.BalanceAsOf("alice", D1));
    }

    [Fact]
    public void SameKeySameArgs_IsDuplicate_NoChange()
    {
        var b = Book();
        b.Deposit("k1", "alice", Usd(100m), D1);
        Assert.Equal(PostingResult.Duplicate, b.Deposit("k1", "alice", Money.Of(100.00m, "USD"), D1));
        b.Transfer("k2", "alice", "bob", Usd(10m), D1);
        Assert.Equal(PostingResult.Duplicate, b.Transfer("k2", "alice", "bob", Usd(10m), D1));
        Assert.Equal(90m, b.Balance("alice"));
        Assert.Equal(10m, b.Balance("bob"));
    }

    [Fact]
    public void SameKeyDifferentArgs_Throws()
    {
        var b = Book();
        b.Deposit("k1", "alice", Usd(100m), D1);
        Assert.Throws<InvalidOperationException>(() => b.Deposit("k1", "alice", Usd(99m), D1));
        Assert.Throws<InvalidOperationException>(() => b.Deposit("k1", "alice", Usd(100m), D2));
        Assert.Throws<InvalidOperationException>(() => b.Transfer("k1", "alice", "bob", Usd(100m), D1));
        Assert.Equal(100m, b.Balance("alice"));
    }

    [Fact]
    public void FailedCall_DoesNotConsumeKey()
    {
        var b = Book();
        Assert.Throws<InsufficientFundsException>(() => b.Transfer("k1", "alice", "bob", Usd(5m), D1));
        b.Deposit("k2", "alice", Usd(5m), D1);
        Assert.Equal(PostingResult.Posted, b.Transfer("k1", "alice", "bob", Usd(5m), D1));
    }

    [Fact]
    public void BalanceAsOf_IncludesBackdatedEntries()
    {
        var b = Book();
        b.Deposit("k1", "alice", Usd(10m), D3);
        b.Deposit("k2", "alice", Usd(5m), D1);
        Assert.Equal(5m, b.BalanceAsOf("alice", D2));
        Assert.Equal(15m, b.BalanceAsOf("alice", D3));
        Assert.Equal(0m, b.BalanceAsOf("alice", D1.AddDays(-1)));
        Assert.Throws<KeyNotFoundException>(() => b.Balance("nobody"));
    }

    [Fact]
    public void Statement_OrderedByDateThenPosting_WithRunningBalance()
    {
        var b = Book();
        b.Deposit("open", "alice", Usd(100m), D1);
        b.Transfer("t-late", "alice", "bob", Usd(20m), D3);
        b.Deposit("d-mid", "alice", Usd(7.5m), D2);
        b.Transfer("t-mid", "alice", "bob", Usd(2.5m), D2);

        var lines = b.Statement("alice", D2, D3);

        Assert.Equal(new[] { "d-mid", "t-mid", "t-late" }, lines.Select(l => l.Key));
        Assert.Equal(new[] { 7.5m, -2.5m, -20m }, lines.Select(l => l.Amount));
        Assert.Equal(new[] { 107.5m, 105m, 85m }, lines.Select(l => l.RunningBalance));
        Assert.Equal(new[] { D2, D2, D3 }, lines.Select(l => l.Date));
    }

    [Fact]
    public void Statement_ForReceivingAccount_ShowsPositiveAmounts()
    {
        var b = Book();
        b.Deposit("open", "alice", Usd(100m), D1);
        b.Transfer("t1", "alice", "bob", Usd(40m), D2);
        var line = Assert.Single(b.Statement("bob", D1, D3));
        Assert.Equal(new StatementLine(D2, "t1", 40m, 40m), line);
    }

    [Fact]
    public void Statement_InvalidRange_Throws() =>
        Assert.Throws<ArgumentException>(() => Book().Statement("alice", D3, D1));
}
