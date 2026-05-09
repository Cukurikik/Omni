namespace OmniMoE.Domain
{
    // OMNI MOTHER: PiKV Health Metrics

    public class OmniPiKVMetrics
    {
        public int FreeBlocks { get; set; }
        public int UsedBlocks { get; set; }
        public double CacheHitRate { get; set; }
        public int EvictionCount { get; set; }
    }
}
