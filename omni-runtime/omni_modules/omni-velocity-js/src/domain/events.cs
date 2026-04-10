namespace Omni.omni_velocity_js.Domain
{
    public class InMemoryEventBus : IEventBus
    {
        private readonly Dictionary<string, List<Action<DomainEvent>>> _handlers = new();
        public void Publish(DomainEvent evt) { if (_handlers.ContainsKey(evt.Name)) foreach (var h in _handlers[evt.Name]) h(evt); }
        public void Subscribe(string topic, Action<DomainEvent> handler) { if (!_handlers.ContainsKey(topic)) _handlers[topic] = new(); _handlers[topic].Add(handler); }
    }
    public class EventStore
    {
        private readonly List<StoredEvent> _events = new();
        public void Append(DomainEvent evt) => _events.Add(new StoredEvent(Guid.NewGuid(), evt.Name, evt.Payload, DateTime.UtcNow));
        public IReadOnlyList<StoredEvent> GetAll() => _events.AsReadOnly();
        public IReadOnlyList<StoredEvent> GetByName(string name) => _events.Where(e => e.Name == name).ToList().AsReadOnly();
    }
    public record StoredEvent(Guid Id, string Name, object Payload, DateTime Timestamp);
}