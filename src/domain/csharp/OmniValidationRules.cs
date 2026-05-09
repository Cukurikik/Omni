using System.Text.RegularExpressions;

namespace OmniMoE.Domain
{
    // OMNI MOTHER: Domain Validation Rules

    public static class OmniValidationRules
    {
        private static readonly Regex IpRegex = new Regex(@"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$");

        public static bool IsValidIpAddress(string ip)
        {
            if (string.IsNullOrWhiteSpace(ip)) return false;
            return IpRegex.IsMatch(ip);
        }

        public static bool IsValidExpertId(string id)
        {
            if (string.IsNullOrWhiteSpace(id)) return false;
            return id.Length >= 3 && id.Length <= 64 && Regex.IsMatch(id, @"^[a-zA-Z0-9_-]+$");
        }
    }
}
