using System;
using System.Diagnostics;
using System.Threading.Tasks;

namespace OmniMoE.Domain
{
    // OMNI MOTHER: Performance Monitoring for MoE
    // Injects telemetry for MoE routing decisions.

    public class OmniMoEMonitoring
    {
        public static readonly ActivitySource Source = new ActivitySource("Omni.MoE.Router");

        public static void RecordExpertDispatch(string expertId, int numTokens)
        {
            using var activity = Source.StartActivity("ExpertDispatch");
            activity?.SetTag("expert.id", expertId);
            activity?.SetTag("expert.tokens", numTokens);
            
            // In a production environment, export to OpenTelemetry / Prometheus
            Console.WriteLine($"[METRICS] Dispatched {numTokens} tokens to {expertId}");
        }

        public static async Task<T> MeasureRoutingLatencyAsync<T>(Func<Task<T>> operation)
        {
            var sw = Stopwatch.StartNew();
            try
            {
                return await operation();
            }
            finally
            {
                sw.Stop();
                using var activity = Source.StartActivity("RoutingLatency");
                activity?.SetTag("latency.ms", sw.ElapsedMilliseconds);
                if (sw.ElapsedMilliseconds > 50)
                {
                    Console.WriteLine($"[WARN] Routing took {sw.ElapsedMilliseconds}ms (Threshold: 50ms)");
                }
            }
        }
    }
}
