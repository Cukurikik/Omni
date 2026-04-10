namespace Omni.omni_dynamodb_native.Domain
{
    public abstract class AggregateRoot
    {
        public EntityId Id { get; protected set; }
        public int Version { get; private set; } = 0;
        private readonly List<DomainEvent> _uncommitted = new();
        protected void AddEvent(DomainEvent evt) { _uncommitted.Add(evt); Version++; }
        public IReadOnlyList<DomainEvent> GetUncommittedEvents() => _uncommitted.AsReadOnly();
        public void ClearEvents() => _uncommitted.Clear();
    }
}