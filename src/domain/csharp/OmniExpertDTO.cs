namespace OmniMoE.Domain
{
    // OMNI MOTHER: Expert Data Transfer Object
    // Used for API serialization.

    public class OmniExpertDTO
    {
        public string Id { get; set; }
        public string IpAddress { get; set; }
        public string Status { get; set; }
        public int MaxCapacity { get; set; }
        public int CurrentLoad { get; set; }
        public string HardwareType { get; set; }
    }
}
