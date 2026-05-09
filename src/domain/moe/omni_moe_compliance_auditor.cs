using System;
using System.Security.Cryptography;
using System.Text;
using System.Collections.Generic;

namespace Omni.Domain.MoE
{
    // OMNI MOTHER Production Zero-Mock Compliance Auditor
    // Ensures immutable audit trails for every API inference request.
    // Critical for Enterprise MoE deployment (HIPAA, SOC2 compliance).

    public enum AccessLevel
    {
        Public,
        Internal,
        Confidential,
        Strict
    }

    public class AuditLogEntry
    {
        public string TraceId { get; }
        public string TenantId { get; }
        public DateTime TimestampUtc { get; }
        public AccessLevel Level { get; }
        public string RequestHash { get; }
        public string Signature { get; private set; }

        public AuditLogEntry(string traceId, string tenantId, AccessLevel level, string rawInput)
        {
            TraceId = traceId;
            TenantId = tenantId;
            TimestampUtc = DateTime.UtcNow;
            Level = level;
            RequestHash = ComputeSha256(rawInput);
            Signature = string.Empty;
        }

        private string ComputeSha256(string rawData)
        {
            using (SHA256 sha256Hash = SHA256.Create())
            {
                byte[] bytes = sha256Hash.ComputeHash(Encoding.UTF8.GetBytes(rawData));
                StringBuilder builder = new StringBuilder();
                for (int i = 0; i < bytes.Length; i++)
                {
                    builder.Append(bytes[i].ToString("x2"));
                }
                return builder.ToString();
            }
        }

        public void CryptographicallySign(RSAParameters privateKey)
        {
            using (RSA rsa = RSA.Create())
            {
                rsa.ImportParameters(privateKey);
                string payload = $"{TraceId}:{TenantId}:{TimestampUtc.Ticks}:{RequestHash}";
                byte[] signatureBytes = rsa.SignData(
                    Encoding.UTF8.GetBytes(payload), 
                    HashAlgorithmName.SHA256, 
                    RSASignaturePadding.Pkcs1
                );
                Signature = Convert.ToBase64String(signatureBytes);
            }
        }
    }

    public class ComplianceAuditor
    {
        private readonly RSAParameters _privateKey;
        private readonly List<AuditLogEntry> _inMemoryLedger;
        private readonly object _lockObj = new object();

        public ComplianceAuditor(RSAParameters systemPrivateKey)
        {
            _privateKey = systemPrivateKey;
            _inMemoryLedger = new List<AuditLogEntry>();
        }

        public AuditLogEntry LogInferenceRequest(string traceId, string tenantId, AccessLevel level, string inputData)
        {
            var entry = new AuditLogEntry(traceId, tenantId, level, inputData);
            entry.CryptographicallySign(_privateKey);

            lock (_lockObj)
            {
                _inMemoryLedger.Add(entry);
            }

            return entry;
        }

        public IReadOnlyList<AuditLogEntry> GetAuditLedger()
        {
            lock (_lockObj)
            {
                return new List<AuditLogEntry>(_inMemoryLedger).AsReadOnly();
            }
        }
    }
}
