namespace OmniMoE.Domain
{
    // OMNI MOTHER: PiKV Configuration Wrapper

    public class OmniPiKVSettings
    {
        public int BlockSize { get; set; } = 16;
        public int MaxMemoryGB { get; set; } = 80;
        public string EvictionPolicy { get; set; } = "LRU";
    }
}
