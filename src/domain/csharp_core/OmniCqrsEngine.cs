// ===========================================================================
// OMNI CQRS ENGINE (SEMESTER 3 — BATCH 38.7)
// ===========================================================================
// Absorbed From  : MediatR + EventStoreDB + Wolverine + Marten
// Logic Inherited: C# / Domain Layer (CQRS + Event Sourcing)
// ===========================================================================
//
// By studying MediatR and EventStoreDB, Mother learned C# CQRS patterns:
//   1. Commands modify state, Queries read state (separated)
//   2. Events record what happened (immutable facts)
//   3. Event Store replays events to rebuild aggregate state
//   4. Projections transform event streams into read models
//   5. MediatR pipeline enables cross-cutting behaviors

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Omni.Domain.CQRS
{
    // ============================================================
    // PART 1: Core Abstractions
    // ============================================================

    /// <summary>Command marker interface (returns TResult).</summary>
    public interface ICommand<TResult> { }

    /// <summary>Query marker interface (returns TResult).</summary>
    public interface IQuery<TResult> { }

    /// <summary>Domain event (immutable fact).</summary>
    public abstract record DomainEvent
    {
        public Guid EventId { get; init; } = Guid.NewGuid();
        public DateTime OccurredAt { get; init; } = DateTime.UtcNow;
        public int Version { get; init; }
        public string AggregateId { get; init; } = string.Empty;
    }

    /// <summary>Command handler interface.</summary>
    public interface ICommandHandler<TCommand, TResult> where TCommand : ICommand<TResult>
    {
        Task<TResult> HandleAsync(TCommand command, CancellationToken ct = default);
    }

    /// <summary>Query handler interface.</summary>
    public interface IQueryHandler<TQuery, TResult> where TQuery : IQuery<TResult>
    {
        Task<TResult> HandleAsync(TQuery query, CancellationToken ct = default);
    }

    /// <summary>Event handler interface.</summary>
    public interface IEventHandler<TEvent> where TEvent : DomainEvent
    {
        Task HandleAsync(TEvent @event, CancellationToken ct = default);
    }

    // ============================================================
    // PART 2: Aggregate Root (Event-Sourced)
    // ============================================================

    /// <summary>
    /// Base class for event-sourced aggregates.
    /// State is rebuilt by replaying events.
    /// </summary>
    public abstract class AggregateRoot
    {
        public string Id { get; protected set; } = string.Empty;
        public int Version { get; private set; } = 0;

        private readonly List<DomainEvent> _uncommittedEvents = new();

        public IReadOnlyList<DomainEvent> UncommittedEvents => _uncommittedEvents.AsReadOnly();

        /// <summary>Apply a new event (both record and mutate state).</summary>
        protected void RaiseEvent(DomainEvent @event)
        {
            var versioned = @event with
            {
                Version = Version + 1,
                AggregateId = Id
            };
            Apply(versioned);
            _uncommittedEvents.Add(versioned);
            Version++;
        }

        /// <summary>Replay an event from history (mutate state only).</summary>
        public void ReplayEvent(DomainEvent @event)
        {
            Apply(@event);
            Version = @event.Version;
        }

        /// <summary>Clear uncommitted events after persistence.</summary>
        public void ClearUncommittedEvents() => _uncommittedEvents.Clear();

        /// <summary>Override to handle specific event types.</summary>
        protected abstract void Apply(DomainEvent @event);
    }

    // ============================================================
    // PART 3: Event Store (In-Memory)
    // ============================================================

    public class EventStore
    {
        private readonly Dictionary<string, List<EventEnvelope>> _streams = new();
        private readonly List<EventEnvelope> _allEvents = new();
        private long _globalPosition = 0;
        private int _totalAppends = 0;

        public record EventEnvelope(
            DomainEvent Event,
            long GlobalPosition,
            string StreamId,
            DateTime StoredAt
        );

        /// <summary>Append events to a stream (optimistic concurrency).</summary>
        public Task AppendAsync(
            string streamId,
            IEnumerable<DomainEvent> events,
            int expectedVersion)
        {
            if (!_streams.ContainsKey(streamId))
            {
                _streams[streamId] = new List<EventEnvelope>();
            }

            var stream = _streams[streamId];
            var currentVersion = stream.Count > 0
                ? stream.Last().Event.Version
                : 0;

            if (currentVersion != expectedVersion)
            {
                throw new ConcurrencyException(
                    $"Expected version {expectedVersion} but found {currentVersion} for stream '{streamId}'"
                );
            }

            foreach (var @event in events)
            {
                var envelope = new EventEnvelope(
                    @event,
                    Interlocked.Increment(ref _globalPosition),
                    streamId,
                    DateTime.UtcNow
                );
                stream.Add(envelope);
                _allEvents.Add(envelope);
                _totalAppends++;
            }

            return Task.CompletedTask;
        }

        /// <summary>Read all events for a stream.</summary>
        public Task<IReadOnlyList<DomainEvent>> ReadStreamAsync(string streamId)
        {
            if (!_streams.ContainsKey(streamId))
            {
                return Task.FromResult<IReadOnlyList<DomainEvent>>(
                    Array.Empty<DomainEvent>()
                );
            }

            var events = _streams[streamId]
                .Select(e => e.Event)
                .ToList()
                .AsReadOnly();

            return Task.FromResult<IReadOnlyList<DomainEvent>>(events);
        }

        /// <summary>Read all events globally (for projections).</summary>
        public Task<IReadOnlyList<EventEnvelope>> ReadAllAsync(long fromPosition = 0)
        {
            var events = _allEvents
                .Where(e => e.GlobalPosition > fromPosition)
                .ToList()
                .AsReadOnly();

            return Task.FromResult<IReadOnlyList<EventEnvelope>>(events);
        }

        public long GlobalPosition => _globalPosition;
        public int TotalStreams => _streams.Count;
        public int TotalEvents => _allEvents.Count;
    }

    public class ConcurrencyException : Exception
    {
        public ConcurrencyException(string message) : base(message) { }
    }

    // ============================================================
    // PART 4: Repository (Event-Sourced)
    // ============================================================

    public class EventSourcedRepository<T> where T : AggregateRoot, new()
    {
        private readonly EventStore _store;
        private int _totalLoads = 0;
        private int _totalSaves = 0;

        public EventSourcedRepository(EventStore store)
        {
            _store = store;
        }

        /// <summary>Load aggregate by replaying all events.</summary>
        public async Task<T> LoadAsync(string aggregateId)
        {
            _totalLoads++;
            var events = await _store.ReadStreamAsync(aggregateId);
            var aggregate = new T();

            foreach (var @event in events)
            {
                aggregate.ReplayEvent(@event);
            }

            return aggregate;
        }

        /// <summary>Save uncommitted events to the store.</summary>
        public async Task SaveAsync(T aggregate)
        {
            _totalSaves++;
            var uncommitted = aggregate.UncommittedEvents;
            if (uncommitted.Count == 0) return;

            var expectedVersion = aggregate.Version - uncommitted.Count;
            await _store.AppendAsync(aggregate.Id, uncommitted, expectedVersion);
            aggregate.ClearUncommittedEvents();
        }
    }

    // ============================================================
    // PART 5: Mediator (Command/Query Dispatcher)
    // ============================================================

    public class Mediator
    {
        private readonly Dictionary<Type, Func<object, CancellationToken, Task<object>>> _commandHandlers = new();
        private readonly Dictionary<Type, Func<object, CancellationToken, Task<object>>> _queryHandlers = new();
        private readonly Dictionary<Type, List<Func<object, CancellationToken, Task>>> _eventHandlers = new();
        private readonly List<Func<object, CancellationToken, Task<object>, Task<object>>> _pipeline = new();
        private int _totalDispatches = 0;

        /// <summary>Register a command handler.</summary>
        public void RegisterCommand<TCommand, TResult>(
            ICommandHandler<TCommand, TResult> handler
        ) where TCommand : ICommand<TResult>
        {
            _commandHandlers[typeof(TCommand)] = async (cmd, ct) =>
                (object)await handler.HandleAsync((TCommand)cmd, ct)!;
        }

        /// <summary>Register a query handler.</summary>
        public void RegisterQuery<TQuery, TResult>(
            IQueryHandler<TQuery, TResult> handler
        ) where TQuery : IQuery<TResult>
        {
            _queryHandlers[typeof(TQuery)] = async (q, ct) =>
                (object)await handler.HandleAsync((TQuery)q, ct)!;
        }

        /// <summary>Register an event handler.</summary>
        public void RegisterEvent<TEvent>(
            IEventHandler<TEvent> handler
        ) where TEvent : DomainEvent
        {
            var type = typeof(TEvent);
            if (!_eventHandlers.ContainsKey(type))
                _eventHandlers[type] = new();

            _eventHandlers[type].Add(async (e, ct) =>
                await handler.HandleAsync((TEvent)e, ct));
        }

        /// <summary>Add pipeline behavior (middleware).</summary>
        public void AddBehavior(Func<object, CancellationToken, Task<object>, Task<object>> behavior)
        {
            _pipeline.Add(behavior);
        }

        /// <summary>Send a command.</summary>
        public async Task<TResult> SendAsync<TResult>(
            ICommand<TResult> command,
            CancellationToken ct = default)
        {
            _totalDispatches++;
            var type = command.GetType();

            if (!_commandHandlers.TryGetValue(type, out var handler))
                throw new InvalidOperationException($"No handler for command {type.Name}");

            // Build pipeline
            Task<object> final() => handler(command, ct);
            var chain = _pipeline.AsEnumerable().Reverse()
                .Aggregate(
                    (Func<Task<object>>)final,
                    (next, behavior) => () => behavior(command, ct, next())
                );

            var result = await chain();
            return (TResult)result;
        }

        /// <summary>Send a query.</summary>
        public async Task<TResult> QueryAsync<TResult>(
            IQuery<TResult> query,
            CancellationToken ct = default)
        {
            _totalDispatches++;
            var type = query.GetType();

            if (!_queryHandlers.TryGetValue(type, out var handler))
                throw new InvalidOperationException($"No handler for query {type.Name}");

            var result = await handler(query, ct);
            return (TResult)result;
        }

        /// <summary>Publish a domain event (fan-out to all handlers).</summary>
        public async Task PublishAsync(DomainEvent @event, CancellationToken ct = default)
        {
            var type = @event.GetType();

            if (_eventHandlers.TryGetValue(type, out var handlers))
            {
                var tasks = handlers.Select(h => h(@event, ct));
                await Task.WhenAll(tasks);
            }
        }

        public int TotalDispatches => _totalDispatches;
    }

    // ============================================================
    // Diagnostics
    // ============================================================

    public static class CqrsDiagnostics
    {
        public static Dictionary<string, object> GetDiagnostics()
        {
            return new Dictionary<string, object>
            {
                ["engine"] = "OmniCQRSEngine",
                ["layer"] = "C# Domain",
                ["components"] = new[]
                {
                    "AggregateRoot", "EventStore", "EventSourcedRepository",
                    "Mediator", "DomainEvent", "ConcurrencyException"
                },
                ["learned_logic"] = new[]
                {
                    "cqrs-command-query-separation",
                    "event-sourcing-replay-state",
                    "aggregate-root-uncommitted",
                    "optimistic-concurrency-version",
                    "mediatr-pipeline-behaviors",
                    "fan-out-event-handlers",
                    "event-envelope-global-position",
                    "repository-load-save-pattern"
                }
            };
        }
    }
}
