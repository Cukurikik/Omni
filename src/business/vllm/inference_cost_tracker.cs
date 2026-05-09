// @omni-layer Business | @omni-source vllm-project/vllm | @omni-lang C#
// @omni-description Inference cost tracker: per-request billing, GPU-hour
// accounting, and usage quota management.
using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.VLLM.Business
{
    public class UsageRecord
    {
        public string RequestId { get; set; }
        public int InputTokens { get; set; }
        public int OutputTokens { get; set; }
        public double GpuMs { get; set; }
        public double CostUsd { get; set; }
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    }

    public class InferenceCostTracker
    {
        private readonly List<UsageRecord> _records = new();
        private double _costPerInputToken = 0.000001;
        private double _costPerOutputToken = 0.000002;
        private double _quotaUsd;

        public InferenceCostTracker(double quotaUsd = 100.0) { _quotaUsd = quotaUsd; }

        public Dictionary<string, object> RecordUsage(string requestId, int inputTok, int outputTok, double gpuMs)
        {
            var cost = inputTok * _costPerInputToken + outputTok * _costPerOutputToken;
            var record = new UsageRecord { RequestId = requestId, InputTokens = inputTok, OutputTokens = outputTok, GpuMs = gpuMs, CostUsd = cost };
            _records.Add(record);
            return new Dictionary<string, object> { ["cost"] = cost, ["remaining_quota"] = _quotaUsd - TotalCost() };
        }

        public double TotalCost() => _records.Sum(r => r.CostUsd);

        public Dictionary<string, object> GetSummary()
        {
            return new Dictionary<string, object>
            {
                ["total_requests"] = _records.Count,
                ["total_input_tokens"] = _records.Sum(r => r.InputTokens),
                ["total_output_tokens"] = _records.Sum(r => r.OutputTokens),
                ["total_cost_usd"] = TotalCost(),
                ["avg_cost_per_request"] = _records.Count > 0 ? TotalCost() / _records.Count : 0,
                ["quota_remaining"] = _quotaUsd - TotalCost(),
                ["quota_used_pct"] = TotalCost() / _quotaUsd * 100
            };
        }
    }
}
