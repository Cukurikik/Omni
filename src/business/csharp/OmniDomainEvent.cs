using System;

namespace OmniFramework.Domain
{
    public abstract class OmniDomainEvent
    {
        public Guid EventId { get; }
        public DateTime OccurredOn { get; }

        protected OmniDomainEvent()
        {
            EventId = Guid.NewGuid();
            OccurredOn = DateTime.UtcNow;
        }
    }

    public class ModelDeployedEvent : OmniDomainEvent
    {
        public string ModelId { get; }
        public string TargetNode { get; }

        public ModelDeployedEvent(string modelId, string targetNode)
        {
            ModelId = modelId;
            TargetNode = targetNode;
        }
    }

    public class InferenceCompletedEvent : OmniDomainEvent
    {
        public string RequestId { get; }
        public long DurationMs { get; }

        public InferenceCompletedEvent(string requestId, long durationMs)
        {
            RequestId = requestId;
            DurationMs = durationMs;
        }
    }
}
