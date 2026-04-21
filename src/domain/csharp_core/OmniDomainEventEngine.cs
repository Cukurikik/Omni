// ===========================================================================
// OMNI DOMAIN EVENT ENGINE (SEMESTER 3 — BATCH 38.2)
// ===========================================================================
// Absorbed From  : MediatR + Wolverine + EventStoreDB concepts
// Logic Inherited: C# / Domain Layer (Event Sourcing + Domain Events)
// ===========================================================================

using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Domain.Events
{
    /// <summary>
    /// Base interface for all domain events.
    /// Events are immutable records of something that happened.
    /// </summary>
    public interface IDomainEvent
    {
        string EventId { get; }
        string EventType { get; }
        DateTime OccurredAt { get; }
        int Version { get; }
    }

    /// <summary>
    /// Abstract base for domain events with auto-generated ID and timestamp.
    /// </summary>
    public abstract record DomainEvent : IDomainEvent
    {
        public string EventId { get; } = Guid.NewGuid().ToString("N")[..8];
        public abstract string EventType { get; }
        public DateTime OccurredAt { get; } = DateTime.UtcNow;
        public int Version { get; init; } = 1;
    }

    /// <summary>
    /// Handles a specific domain event type.
    /// </summary>
    public interface IDomainEventHandler<in TEvent> where TEvent : IDomainEvent
    {
        void Handle(TEvent domainEvent);
    }

    /// <summary>
    /// Event store — append-only log of domain events per aggregate.
    /// </summary>
    public sealed class EventStore
    {
        private readonly Dictionary<string, List<IDomainEvent>> _streams;
        private readonly List<IDomainEvent> _allEvents;
        private long _totalEvents;

        public EventStore()
        {
            _streams = new Dictionary<string, List<IDomainEvent>>();
            _allEvents = new List<IDomainEvent>();
            _totalEvents = 0;
        }

        /// <summary>Append events to an aggregate's stream.</summary>
        public void Append(string streamId, params IDomainEvent[] events)
        {
            if (!_streams.ContainsKey(streamId))
                _streams[streamId] = new List<IDomainEvent>();

            foreach (var evt in events)
            {
                _streams[streamId].Add(evt);
                _allEvents.Add(evt);
                _totalEvents++;
            }
        }

        /// <summary>Read all events for an aggregate stream.</summary>
        public IReadOnlyList<IDomainEvent> ReadStream(string streamId)
        {
            return _streams.TryGetValue(streamId, out var events)
                ? events.AsReadOnly()
                : Array.Empty<IDomainEvent>();
        }

        /// <summary>Read events from a stream starting at a version.</summary>
        public IReadOnlyList<IDomainEvent> ReadStream(string streamId, int fromVersion)
        {
            var stream = ReadStream(streamId);
            return stream.Where(e => e.Version >= fromVersion).ToList().AsReadOnly();
        }

        /// <summary>Read all events globally (for projections).</summary>
        public IReadOnlyList<IDomainEvent> ReadAll() => _allEvents.AsReadOnly();

        public long TotalEvents => _totalEvents;
        public int StreamCount => _streams.Count;
    }

    /// <summary>
    /// Event dispatcher — routes domain events to registered handlers.
    /// Similar to MediatR notification dispatch.
    /// </summary>
    public sealed class EventDispatcher
    {
        private readonly Dictionary<Type, List<object>> _handlers;
        private long _totalDispatched;

        public EventDispatcher()
        {
            _handlers = new Dictionary<Type, List<object>>();
            _totalDispatched = 0;
        }

        /// <summary>Register a handler for a specific event type.</summary>
        public void Register<TEvent>(IDomainEventHandler<TEvent> handler)
            where TEvent : IDomainEvent
        {
            var eventType = typeof(TEvent);
            if (!_handlers.ContainsKey(eventType))
                _handlers[eventType] = new List<object>();

            _handlers[eventType].Add(handler);
        }

        /// <summary>
        /// Dispatch an event to all registered handlers.
        /// Returns the number of handlers that processed the event.
        /// </summary>
        public int Dispatch<TEvent>(TEvent domainEvent) where TEvent : IDomainEvent
        {
            var eventType = typeof(TEvent);
            if (!_handlers.TryGetValue(eventType, out var handlerList))
                return 0;

            int processed = 0;
            foreach (var handler in handlerList)
            {
                if (handler is IDomainEventHandler<TEvent> typedHandler)
                {
                    typedHandler.Handle(domainEvent);
                    processed++;
                }
            }

            _totalDispatched++;
            return processed;
        }

        public long TotalDispatched => _totalDispatched;
        public int HandlerTypeCount => _handlers.Count;
    }

    /// <summary>
    /// Aggregate root base class with built-in event sourcing support.
    /// Aggregates raise events, and state is reconstructed by replaying them.
    /// </summary>
    public abstract class AggregateRoot
    {
        private readonly List<IDomainEvent> _uncommittedEvents = new();
        public string Id { get; protected set; }
        public int Version { get; protected set; }

        /// <summary>Get all uncommitted events (raised since last persist).</summary>
        public IReadOnlyList<IDomainEvent> GetUncommittedEvents()
            => _uncommittedEvents.AsReadOnly();

        /// <summary>Clear uncommitted events after persisting.</summary>
        public void ClearUncommittedEvents() => _uncommittedEvents.Clear();

        /// <summary>
        /// Raise a domain event — applies it to current state
        /// and queues for persistence.
        /// </summary>
        protected void RaiseEvent(IDomainEvent domainEvent)
        {
            Apply(domainEvent);
            _uncommittedEvents.Add(domainEvent);
            Version++;
        }

        /// <summary>
        /// Reconstitute aggregate state from a history of events.
        /// </summary>
        public void LoadFromHistory(IEnumerable<IDomainEvent> events)
        {
            foreach (var evt in events)
            {
                Apply(evt);
                Version++;
            }
        }

        /// <summary>
        /// Apply an event to update the aggregate's internal state.
        /// Subclasses implement this with pattern matching.
        /// </summary>
        protected abstract void Apply(IDomainEvent domainEvent);
    }

    // ---- Projection (Read Model Builder) ----

    /// <summary>
    /// Projection interface — transforms event streams into read models.
    /// </summary>
    public interface IProjection
    {
        string ProjectionName { get; }
        void Apply(IDomainEvent domainEvent);
    }

    /// <summary>
    /// Projection engine — applies events to multiple projections.
    /// </summary>
    public sealed class ProjectionEngine
    {
        private readonly List<IProjection> _projections;
        private long _totalProjected;

        public ProjectionEngine()
        {
            _projections = new List<IProjection>();
            _totalProjected = 0;
        }

        public void Register(IProjection projection) => _projections.Add(projection);

        /// <summary>Project all events from a store to all registered projections.</summary>
        public void ProjectAll(EventStore store)
        {
            foreach (var evt in store.ReadAll())
            {
                foreach (var projection in _projections)
                {
                    projection.Apply(evt);
                    _totalProjected++;
                }
            }
        }

        public long TotalProjected => _totalProjected;
    }

    // ---- Diagnostics ----

    public static class OmniDomainEventEngineDiagnostics
    {
        public static Dictionary<string, object> Diagnostics(
            EventStore store, EventDispatcher dispatcher, ProjectionEngine projections)
        {
            return new Dictionary<string, object>
            {
                ["engine"] = "OmniDomainEventEngine",
                ["layer"] = "C# Domain",
                ["event_store_streams"] = store.StreamCount,
                ["event_store_total_events"] = store.TotalEvents,
                ["dispatcher_total_dispatched"] = dispatcher.TotalDispatched,
                ["dispatcher_handler_types"] = dispatcher.HandlerTypeCount,
                ["projection_total_projected"] = projections.TotalProjected,
                ["learned_logic"] = new[]
                {
                    "event-sourcing-append-only-log",
                    "aggregate-root-raise-event",
                    "reconstitute-from-history",
                    "mediatr-notification-dispatch",
                    "cqrs-read-model-projections",
                    "immutable-record-events",
                    "uncommitted-event-tracking",
                    "stream-per-aggregate-pattern"
                }
            };
        }
    }
}
