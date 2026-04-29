// OmniDomainEventBus - OMNI Business Layer
//
// Implements enterprise CQRS and Event Sourcing patterns in C#
// Enforces pure immutability and Result<T> wrapping.

using System;
using System.Collections.Generic;

namespace Omni.Domain.CSharpCore
{
    public class Result<T>
    {
        public bool IsOk { get; }
        public T Value { get; }
        public string ErrorMessage { get; }

        private Result(bool isOk, T value, string errorMessage)
        {
            IsOk = isOk;
            Value = value;
            ErrorMessage = errorMessage;
        }

        public static Result<T> Ok(T value) => new Result<T>(true, value, null);
        public static Result<T> Err(string error) => new Result<T>(false, default, error);
    }

    public interface IEvent {
        Guid Id { get; }
        DateTime OccurredOn { get; }
    }

    public sealed class OmniDomainEventBus
    {
        private readonly List<IEvent> _eventStore;

        public OmniDomainEventBus()
        {
            _eventStore = new List<IEvent>();
        }

        /// <summary>
        /// Appends an event to the immutable store.
        /// </summary>
        public Result<bool> Publish(IEvent domainEvent)
        {
            if (domainEvent == null)
            {
                return Result<bool>.Err("Domain event cannot be null.");
            }

            if (domainEvent.Id == Guid.Empty)
            {
                return Result<bool>.Err("Domain event must have a valid Guid.");
            }

            // In production, this writes to EventStoreDB / Kafka
            _eventStore.Add(domainEvent);
            
            return Result<bool>.Ok(true);
        }

        /// <summary>
        /// Replays events for Aggregate hydration.
        /// </summary>
        public Result<IReadOnlyList<IEvent>> GetHistory()
        {
            return Result<IReadOnlyList<IEvent>>.Ok(_eventStore.AsReadOnly());
        }
    }
}
