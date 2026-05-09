namespace OmniMoE.Domain
{
    // OMNI MOTHER: System-wide Constants

    public static class OmniMoEConstants
    {
        public const string StatusOnline = "ONLINE";
        public const string StatusOffline = "OFFLINE";
        public const string StatusDraining = "DRAINING";
        public const string StatusFailed = "FAILED";

        public const int DefaultExpertCapacity = 4096;
        public const int MaxTokenLength = 32768;
    }
}
