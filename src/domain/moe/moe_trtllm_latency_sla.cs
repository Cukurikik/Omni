// moe_trtllm_latency_sla.cs — Domain Layer: TensorRT-LLM Latency SLA
// C# business logic defining Service Level Agreements for tail latency constraints.

using System;

namespace Omni.Domain.MoE.TrtLlm
{
    public class LatencySlaMonitor
    {
        public double TargetLatencyMs { get; private set; }
        public double MaxTolerableTailMs { get; private set; }

        public LatencySlaMonitor(double targetMs, double maxTailMs)
        {
            if (targetMs <= 0 || maxTailMs < targetMs)
                throw new ArgumentException("Invalid SLA configuration bounds.");
                
            TargetLatencyMs = targetMs;
            MaxTolerableTailMs = maxTailMs;
        }

        public SlaStatus EvaluateLatency(double currentP99Latency)
        {
            if (currentP99Latency <= TargetLatencyMs)
            {
                return SlaStatus.Healthy;
            }
            else if (currentP99Latency > TargetLatencyMs && currentP99Latency <= MaxTolerableTailMs)
            {
                return SlaStatus.Degraded;
            }
            else
            {
                return SlaStatus.Breached;
            }
        }
    }

    public enum SlaStatus
    {
        Healthy,
        Degraded,
        Breached
    }
}
