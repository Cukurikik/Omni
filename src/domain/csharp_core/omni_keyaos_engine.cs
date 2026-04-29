// BATCH 33: keyaos Engine
// OMNI FRAMEWORK COMPLIANT - ZERO MOCK - MONADIC ERROR HANDLING
// DOMAIN LAYER - C#

using System;
using System.Security.Cryptography;
using System.Text;

namespace OmniFramework.Domain.KeyAOS
{
    /// <summary>
    /// Monadic Result implementation for KeyAOS Engine.
    /// </summary>
    public class Result<T, E> where E : Exception
    {
        public bool IsOk { get; }
        public T Value { get; }
        public E Error { get; }

        private Result(T value, bool isOk, E error)
        {
            Value = value;
            IsOk = isOk;
            Error = error;
        }

        public static Result<T, E> Ok(T value) => new Result<T, E>(value, true, null);
        public static Result<T, E> Err(E error) => new Result<T, E>(default, false, error);
    }

    /// <summary>
    /// Exceptions specific to the KeyAOS Domain.
    /// </summary>
    public class KeyAosException : Exception
    {
        public KeyAosException(string message) : base(message) { }
    }

    /// <summary>
    /// Represents access capabilities securely mapped to an entity.
    /// </summary>
    public class AccessCapability
    {
        public string EntityId { get; set; }
        public ulong PermissionsMask { get; set; } // Bitmask of permissions
        public long ExpirationEpoch { get; set; }
        public string Signature { get; set; } // Hex encoded HMAC
    }

    /// <summary>
    /// The Core OS Key generation and validation domain engine.
    /// </summary>
    public class OmniKeyAOSEngine
    {
        private readonly byte[] _masterSecret;

        public OmniKeyAOSEngine(string masterSecretHex)
        {
            if (string.IsNullOrWhiteSpace(masterSecretHex) || masterSecretHex.Length < 64)
            {
                throw new ArgumentException("Master secret must be at least 256 bits (64 hex characters).");
            }
            _masterSecret = Convert.FromHexString(masterSecretHex);
        }

        /// <summary>
        /// Deterministically provisions a capability token for a user.
        /// Zero randomness: The signature is pure mathematical HMAC over the parameters.
        /// </summary>
        public Result<AccessCapability, KeyAosException> ProvisionCapability(string entityId, ulong mask, long ttlSeconds)
        {
            if (string.IsNullOrWhiteSpace(entityId))
            {
                return Result<AccessCapability, KeyAosException>.Err(new KeyAosException("Entity ID cannot be empty."));
            }

            long currentEpoch = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
            long expiration = currentEpoch + ttlSeconds;

            string payload = $"{entityId}:{mask}:{expiration}";
            
            using var hmac = new HMACSHA256(_masterSecret);
            byte[] signatureBytes = hmac.ComputeHash(Encoding.UTF8.GetBytes(payload));
            string signatureHex = Convert.ToHexString(signatureBytes);

            var capability = new AccessCapability
            {
                EntityId = entityId,
                PermissionsMask = mask,
                ExpirationEpoch = expiration,
                Signature = signatureHex
            };

            return Result<AccessCapability, KeyAosException>.Ok(capability);
        }

        /// <summary>
        /// Validates a capability strictly linearly. Zero try/catch blocks masking invalid state.
        /// </summary>
        public Result<bool, KeyAosException> ValidateCapability(AccessCapability cap)
        {
            if (cap == null)
            {
                return Result<bool, KeyAosException>.Err(new KeyAosException("Capability payload is null."));
            }

            long currentEpoch = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
            if (currentEpoch > cap.ExpirationEpoch)
            {
                return Result<bool, KeyAosException>.Err(new KeyAosException("Capability token has expired."));
            }

            // Recompute signature to verify integrity (Zero Trust model)
            string payload = $"{cap.EntityId}:{cap.PermissionsMask}:{cap.ExpirationEpoch}";
            
            using var hmac = new HMACSHA256(_masterSecret);
            byte[] expectedBytes = hmac.ComputeHash(Encoding.UTF8.GetBytes(payload));
            string expectedSignatureHex = Convert.ToHexString(expectedBytes);

            if (!string.Equals(cap.Signature, expectedSignatureHex, StringComparison.OrdinalIgnoreCase))
            {
                return Result<bool, KeyAosException>.Err(new KeyAosException("Cryptographic signature validation failed. Data integrity compromised."));
            }

            return Result<bool, KeyAosException>.Ok(true);
        }
    }
}
