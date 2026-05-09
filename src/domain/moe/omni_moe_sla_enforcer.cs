using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Domain.MoE
{
    // OMNI MOTHER Production Zero-Mock Domain Driven Design
    // SLA Enforcer protects Service Level Agreements for token generation latency.

    public enum SlaSeverity
    {
        Healthy,
        Warning,
        Critical,
        Breached
    }

    public class SlaContract
    {
        public string ModelId { get; }
        public int MaxLatencyMsPerToken { get; }
        public double MaxP99LatencyMs { get; }
        
        public SlaContract(string modelId, int maxLatencyMs, double maxP99)
        {
            ModelId = modelId;
            MaxLatencyMsPerToken = maxLatencyMs;
            MaxP99LatencyMs = maxP99;
        }
    }

    public class SlaEnforcer
    {
        private readonly SlaContract _contract;
        private readonly Queue<double> _recentLatencies;
        private readonly int _windowSize;

        public SlaEnforcer(SlaContract contract, int windowSize = 1000)
        {
            _contract = contract;
            _recentLatencies = new Queue<double>();
            _windowSize = windowSize;
        }

        public void RecordLatency(double latencyMs)
        {
            lock (_recentLatencies)
            {
                if (_recentLatencies.Count >= _windowSize)
                {
                    _recentLatencies.Dequeue();
                }
                _recentLatencies.Enqueue(latencyMs);
            }
        }

        public double CalculateP99()
        {
            lock (_recentLatencies)
            {
                if (_recentLatencies.Count == 0) return 0.0;
                
                var sorted = _recentLatencies.OrderBy(x => x).ToList();
                int idx = (int)Math.Ceiling(0.99 * sorted.Count) - 1;
                return sorted[Math.Max(0, idx)];
            }
        }

        public SlaSeverity EvaluateHealth()
        {
            double p99 = CalculateP99();

            if (p99 > _contract.MaxP99LatencyMs)
            {
                return SlaSeverity.Breached;
            }
            if (p99 > _contract.MaxP99LatencyMs * 0.90)
            {
                return SlaSeverity.Critical;
            }
            if (p99 > _contract.MaxP99LatencyMs * 0.75)
            {
                return SlaSeverity.Warning;
            }

            return SlaSeverity.Healthy;
        }

        public void TriggerFailsafeIfRequired()
        {
            var health = EvaluateHealth();
            if (health == SlaSeverity.Breached)
            {
                // In production, this emits an event to the HashRing to evict the slow node
                Console.WriteLine($"OMNI CRITICAL: SLA Breached for {_contract.ModelId}. P99: {CalculateP99()}ms. Triggering dynamic expert routing fallback.");
                throw new InvalidOperationException("SLA Breach Exception - Node Eviction Required");
            }
        }
    }
}
