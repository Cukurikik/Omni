// OmniHealthChecker.cs — Polyglot Service Health Checker
// Layer: Domain / C#
//
// Periodically pings GRPC and REST endpoints across the Elixir, Go, and Python
// compute layers to enforce circuit-breaker patterns on failing nodes.

using System;
using System.Collections.Concurrent;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;

namespace Omni.Domain.Health
{
    public enum ServiceStatus
    {
        Healthy,
        Degraded,
        Offline
    }

    public sealed class ServiceNode
    {
        public string Id { get; init; } = string.Empty;
        public string Url { get; init; } = string.Empty;
        public ServiceStatus Status { get; set; } = ServiceStatus.Offline;
        public int FailureCount { get; set; } = 0;
    }

    /// <summary>
    /// Background service monitoring the OMNI network cluster.
    /// </summary>
    public sealed class OmniHealthChecker : IDisposable
    {
        private readonly ConcurrentDictionary<string, ServiceNode> _registry = new();
        private readonly HttpClient _httpClient = new();
        private CancellationTokenSource _cts = new();

        public void RegisterNode(string id, string url)
        {
            _registry[id] = new ServiceNode { Id = id, Url = url, Status = ServiceStatus.Healthy };
        }

        public void StartMonitoring(TimeSpan interval)
        {
            _cts = new CancellationTokenSource();
            Task.Run(() => MonitorLoopAsync(interval, _cts.Token));
        }

        private async Task MonitorLoopAsync(TimeSpan interval, CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                foreach (var kvp in _registry)
                {
                    var node = kvp.Value;
                    try
                    {
                        var response = await _httpClient.GetAsync($"{node.Url}/health", token);
                        if (response.IsSuccessStatusCode)
                        {
                            node.Status = ServiceStatus.Healthy;
                            node.FailureCount = 0;
                        }
                        else
                        {
                            HandleFailure(node);
                        }
                    }
                    catch
                    {
                        HandleFailure(node);
                    }
                }
                await Task.Delay(interval, token);
            }
        }

        private void HandleFailure(ServiceNode node)
        {
            node.FailureCount++;
            node.Status = node.FailureCount > 3 ? ServiceStatus.Offline : ServiceStatus.Degraded;
            
            if (node.Status == ServiceStatus.Offline)
            {
                Console.WriteLine($"[ALERT] Circuit Breaker Tripped for node {node.Id} at {node.Url}");
                // In production, this emits an event to the Service Registry to reroute traffic.
            }
        }

        public void Dispose()
        {
            _cts.Cancel();
            _httpClient.Dispose();
        }
    }
}
