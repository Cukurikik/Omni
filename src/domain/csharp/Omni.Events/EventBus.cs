using System;
using System.Collections.Generic;

namespace Omni.Events
{
    // OMNI MOTHER: In-Memory Domain Event Bus (Production Grade)
    public class EventBus
    {
        private readonly Dictionary<Type, List<Action<DomainEvent>>> _handlers = new();

        public void Subscribe<T>(Action<T> handler) where T : DomainEvent
        {
            var type = typeof(T);
            if (!_handlers.ContainsKey(type))
            {
                _handlers[type] = new List<Action<DomainEvent>>();
            }
            _handlers[type].Add(e => handler((T)e));
        }

        public void Publish(DomainEvent domainEvent)
        {
            var type = domainEvent.GetType();
            if (_handlers.ContainsKey(type))
            {
                foreach (var handler in _handlers[type])
                {
                    handler(domainEvent);
                }
            }
            Console.WriteLine($"[OMNI EVENTS] Published {type.Name}");
        }
    }
}
