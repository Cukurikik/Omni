using System;

namespace OmniMoE.Domain
{
    // OMNI MOTHER: Monadic/Structured Error Definitions for MoE

    public class OmniMoEException : Exception
    {
        public OmniMoEException(string message) : base($"[OMNI EXCEPTION] {message}") { }
        public OmniMoEException(string message, Exception inner) : base($"[OMNI EXCEPTION] {message}", inner) { }
    }

    public class ExpertOfflineException : OmniMoEException
    {
        public string ExpertId { get; }

        public ExpertOfflineException(string expertId) 
            : base($"Expert {expertId} is currently offline or unreachable.")
        {
            ExpertId = expertId;
        }
    }

    public class ClusterCapacityExceededException : OmniMoEException
    {
        public ClusterCapacityExceededException() 
            : base("The MoE cluster has exceeded its maximum token processing capacity.")
        {
        }
    }

    public class InvalidRoutingStrategyException : OmniMoEException
    {
        public InvalidRoutingStrategyException(string strategy) 
            : base($"Routing strategy '{strategy}' is not supported.")
        {
        }
    }
}
