// @omni-layer Business | @omni-source facebookresearch/llama | @omni-lang C#
// @omni-description Model serving registry: tracks deployed LLM versions, endpoint
// health, and A/B testing configurations.
using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Llama.Business
{
    public class ModelEndpoint
    {
        public string ModelId { get; set; }
        public string Version { get; set; }
        public string Status { get; set; } = "active";
        public double TrafficWeight { get; set; } = 1.0;
        public int TotalRequests { get; set; }
        public double AvgLatencyMs { get; set; }
        public DateTime DeployedAt { get; set; } = DateTime.UtcNow;
    }

    public class ModelServingRegistry
    {
        private readonly Dictionary<string, ModelEndpoint> _endpoints = new();

        public Dictionary<string, object> RegisterModel(string modelId, string version, double weight)
        {
            var endpoint = new ModelEndpoint { ModelId = modelId, Version = version, TrafficWeight = weight };
            _endpoints[modelId] = endpoint;
            return new Dictionary<string, object> { ["model_id"] = modelId, ["status"] = "registered" };
        }

        public Dictionary<string, object> RouteRequest(string requestId)
        {
            var active = _endpoints.Values.Where(e => e.Status == "active").ToList();
            if (!active.Any()) return new Dictionary<string, object> { ["error"] = "No active endpoints" };
            var totalWeight = active.Sum(e => e.TrafficWeight);
            var r = new Random().NextDouble() * totalWeight;
            double cumul = 0;
            foreach (var ep in active)
            {
                cumul += ep.TrafficWeight;
                if (r <= cumul)
                {
                    ep.TotalRequests++;
                    return new Dictionary<string, object> {
                        ["model_id"] = ep.ModelId, ["version"] = ep.Version,
                        ["request_id"] = requestId
                    };
                }
            }
            return new Dictionary<string, object> { ["model_id"] = active.Last().ModelId };
        }

        public Dictionary<string, object> GetHealth()
        {
            return new Dictionary<string, object> {
                ["total_endpoints"] = _endpoints.Count,
                ["active"] = _endpoints.Values.Count(e => e.Status == "active"),
                ["total_requests"] = _endpoints.Values.Sum(e => e.TotalRequests)
            };
        }
    }
}
