using System;

namespace Omni.Events
{
    // OMNI MOTHER: Base Domain Event (Production Grade)
    public abstract class DomainEvent
    {
        public Guid EventId { get; }
        public DateTime OccurredOn { get; }

        protected DomainEvent()
        {
            EventId = Guid.NewGuid();
            OccurredOn = DateTime.UtcNow;
        }
    }

    public class PaymentCompletedEvent : DomainEvent
    {
        public Guid PaymentId { get; }
        
        public PaymentCompletedEvent(Guid paymentId)
        {
            PaymentId = paymentId;
        }
    }
}
