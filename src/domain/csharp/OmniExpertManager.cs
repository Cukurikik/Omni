using System;
using System.Collections.Generic;
using System.Linq;

namespace OmniMoE.Domain
{
    /// <summary>
    /// OMNI MOTHER: Expert Aggregate Root
    /// Manages the domain rules, health state, and capacity of individual experts
    /// within the C# Business Logic Layer.
    /// </summary>
    public class OmniExpertManager
    {
        private readonly Dictionary<string, ExpertNode> _experts;

        public OmniExpertManager()
        {
            _experts = new Dictionary<string, ExpertNode>();
        }

        public void RegisterExpert(string expertId, string ipAddress, int maxCapacity)
        {
            if (!_experts.ContainsKey(expertId))
            {
                _experts[expertId] = new ExpertNode(expertId, ipAddress, maxCapacity);
            }
        }

        public void ReportHealth(string expertId, bool isHealthy)
        {
            if (_experts.TryGetValue(expertId, out var node))
            {
                node.UpdateHealth(isHealthy);
            }
        }

        public void UpdateLoad(string expertId, int currentTokens)
        {
            if (_experts.TryGetValue(expertId, out var node))
            {
                node.SetCurrentLoad(currentTokens);
            }
        }

        public List<string> GetAvailableExperts()
        {
            return _experts.Values
                .Where(e => e.IsHealthy && e.CurrentLoad < e.MaxCapacity)
                .Select(e => e.ExpertId)
                .ToList();
        }
    }

    public class ExpertNode
    {
        public string ExpertId { get; }
        public string IpAddress { get; }
        public int MaxCapacity { get; }
        public int CurrentLoad { get; private set; }
        public bool IsHealthy { get; private set; }
        public DateTime LastUpdated { get; private set; }

        public ExpertNode(string id, string ip, int maxCapacity)
        {
            ExpertId = id;
            IpAddress = ip;
            MaxCapacity = maxCapacity;
            IsHealthy = true;
            CurrentLoad = 0;
            LastUpdated = DateTime.UtcNow;
        }

        public void UpdateHealth(bool health)
        {
            IsHealthy = health;
            LastUpdated = DateTime.UtcNow;
        }

        public void SetCurrentLoad(int load)
        {
            CurrentLoad = load;
            LastUpdated = DateTime.UtcNow;
        }
    }
}
