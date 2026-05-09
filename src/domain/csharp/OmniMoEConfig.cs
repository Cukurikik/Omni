using System;
using System.IO;
using System.Text.Json;

namespace OmniMoE.Domain
{
    // OMNI MOTHER: Central Configuration Loader for the C# Domain Layer

    public class OmniMoEConfig
    {
        public string ClusterName { get; set; } = "OmniMoE-Production";
        public int GrpcRouterPort { get; set; } = 50050;
        public string RoutingStrategy { get; set; } = "LEAST_LOADED";
        public int MaxExpertsPerNode { get; set; } = 8;
        public bool EnableHardwareTelemetry { get; set; } = true;

        public static OmniMoEConfig Load(string path = "omni_moe_config.json")
        {
            if (!File.Exists(path))
            {
                Console.WriteLine($"[OMNI] Config not found at {path}, using defaults.");
                return new OmniMoEConfig();
            }

            try
            {
                string json = File.ReadAllText(path);
                return JsonSerializer.Deserialize<OmniMoEConfig>(json) ?? new OmniMoEConfig();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[OMNI ERROR] Failed to load config: {ex.Message}");
                return new OmniMoEConfig();
            }
        }
    }
}
