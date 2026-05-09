using System;
using System.Security.Cryptography;
using System.Text;

namespace Omni.Domain.MoE
{
    public sealed class ModelFingerprinter
    {
        public static string ComputeSignature(string modelConfigJson, long parameterCount)
        {
            using var sha256 = SHA256.Create();
            string combined = $"{modelConfigJson}|{parameterCount}";
            byte[] hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(combined));
            return Convert.ToHexString(hashBytes).ToLowerInvariant();
        }
        
        public static bool VerifySignature(string expected, string config, long parameters)
        {
            return string.Equals(expected, ComputeSignature(config, parameters), StringComparison.OrdinalIgnoreCase);
        }
    }
}
