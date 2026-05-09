// MoETenantConfig.cs — Business / Domain Layer
// Layer: Domain / Policy — SaaS Multi-Tenancy for MoE
//
// Manages tenant-specific configurations for the MoE Gateway.
// Maps commercial SLAs to MoE routing properties (e.g., priority,
// expert capacity limits, and allowed specialized experts).

using System;
using System.Collections.Generic;

namespace Omni.MoE.Domain
{
    public enum TenantTier
    {
        Free,
        Standard,
        Premium,
        Enterprise
    }

    public class MoETenantSLA
    {
        public string TenantId { get; }
        public TenantTier Tier { get; }
        
        // MoE-specific limits
        public int MaxTokensPerMinute { get; }
        public int RoutingPriority { get; } // 1 (Highest) to 10 (Lowest)
        public bool CanBypassCapacityLimits { get; }
        
        // Allowed Specialized Experts
        // Null means access to all general experts. Specific IDs map to premium/custom experts.
        public HashSet<int> AllowedCustomExperts { get; }

        private MoETenantSLA(
            string tenantId, 
            TenantTier tier, 
            int maxTokens, 
            int priority, 
            bool bypassLimits, 
            HashSet<int> customExperts)
        {
            TenantId = tenantId;
            Tier = tier;
            MaxTokensPerMinute = maxTokens;
            RoutingPriority = priority;
            CanBypassCapacityLimits = bypassLimits;
            AllowedCustomExperts = customExperts ?? new HashSet<int>();
        }

        /// Factory method mapping Tiers to SLA metrics.
        public static MoETenantSLA Create(string tenantId, TenantTier tier, HashSet<int> customExperts = null)
        {
            if (string.IsNullOrWhiteSpace(tenantId))
            {
                throw new ArgumentException("TenantId cannot be null or empty", nameof(tenantId));
            }

            return tier switch
            {
                TenantTier.Free => new MoETenantSLA(tenantId, tier, 10_000, 10, false, new HashSet<int>()),
                TenantTier.Standard => new MoETenantSLA(tenantId, tier, 100_000, 5, false, customExperts),
                TenantTier.Premium => new MoETenantSLA(tenantId, tier, 1_000_000, 2, false, customExperts),
                TenantTier.Enterprise => new MoETenantSLA(tenantId, tier, int.MaxValue, 1, true, customExperts),
                _ => throw new ArgumentOutOfRangeException(nameof(tier), $"Unknown tier: {tier}")
            };
        }

        /// <summary>
        /// Validates if a tenant is allowed to route to a specific expert.
        /// Assumes experts 0-127 are general, and 128+ are premium/custom.
        /// </summary>
        public bool IsExpertAllowed(int expertId)
        {
            // General experts are always allowed
            if (expertId < 128) return true;

            // Free tier cannot access premium experts
            if (Tier == TenantTier.Free) return false;

            // Higher tiers check specific allocations
            return AllowedCustomExperts.Contains(expertId);
        }
    }

    public class TenantSlaRepository
    {
        private readonly Dictionary<string, MoETenantSLA> _store = new();

        public void Upsert(MoETenantSLA sla)
        {
            _store[sla.TenantId] = sla;
        }

        public MoETenantSLA Get(string tenantId)
        {
            if (_store.TryGetValue(tenantId, out var sla))
            {
                return sla;
            }
            // Default to Free if not found
            return MoETenantSLA.Create(tenantId, TenantTier.Free);
        }
    }
}
