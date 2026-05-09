using System;
using System.Collections.Generic;

namespace OmniMoE.Domain
{
    // OMNI MOTHER: Routing Strategy Pattern
    // Defines business rules for fallback routing if the ML model selects
    // a downed expert.

    public interface IRoutingStrategy
    {
        string GetFallbackExpert(string failedExpertId, List<ExpertNode> availableExperts);
    }

    public class RoundRobinFallbackStrategy : IRoutingStrategy
    {
        private int _index = 0;

        public string GetFallbackExpert(string failedExpertId, List<ExpertNode> availableExperts)
        {
            if (availableExperts.Count == 0) return null;
            
            lock (this)
            {
                _index = (_index + 1) % availableExperts.Count;
                return availableExperts[_index].ExpertId;
            }
        }
    }

    public class LeastLoadedFallbackStrategy : IRoutingStrategy
    {
        public string GetFallbackExpert(string failedExpertId, List<ExpertNode> availableExperts)
        {
            if (availableExperts.Count == 0) return null;

            ExpertNode best = availableExperts[0];
            foreach (var node in availableExperts)
            {
                if (node.CurrentLoad < best.CurrentLoad)
                {
                    best = node;
                }
            }

            return best.ExpertId;
        }
    }
}
