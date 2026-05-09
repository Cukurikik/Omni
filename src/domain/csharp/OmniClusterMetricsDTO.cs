namespace OmniMoE.Domain
{
    // OMNI MOTHER: Cluster Metrics DTO

    public class OmniClusterMetricsDTO
    {
        public long TotalTokensProcessed { get; set; }
        public double AverageRoutingLatencyMs { get; set; }
        public double ImbalanceFactor { get; set; }
        public int ActiveExperts { get; set; }
        public int OfflineExperts { get; set; }
    }
}
