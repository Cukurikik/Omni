namespace Omni.omni_mollie.Domain
{
    public record EntityId(string Value) { public static EntityId Generate() => new EntityId(Guid.NewGuid().ToString()); }
    public record Money(decimal Amount, string Currency) {
        public Money Add(Money other) => Currency == other.Currency ? new Money(Amount + other.Amount, Currency) : throw new InvalidOperationException("Currency mismatch");
        public Money Subtract(Money other) => Currency == other.Currency ? new Money(Amount - other.Amount, Currency) : throw new InvalidOperationException("Currency mismatch");
    }
    public record Timestamp(long UnixMs) { public static Timestamp Now() => new Timestamp(DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()); public DateTime ToDateTime() => DateTimeOffset.FromUnixTimeMilliseconds(UnixMs).UtcDateTime; }
    public record PageRequest(int Page, int Size, string SortBy, bool Ascending);
    public record PageResponse<T>(IReadOnlyList<T> Items, int Total, int Page, int Size, bool HasNext);
    public enum Status { Active, Inactive, Pending, Failed, Cancelled, Completed, Archived }
    public record AuditInfo(string CreatedBy, Timestamp CreatedAt, string UpdatedBy, Timestamp UpdatedAt);
    public record ErrorDetail(string Code, string Message, string Field);
    public record Config(string Key, string Value, string Env);
    public record Metadata(Dictionary<string, string> Tags);
}