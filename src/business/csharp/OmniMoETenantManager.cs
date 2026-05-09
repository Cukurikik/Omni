using System;
using System.Collections.Concurrent;
using System.Threading.Tasks;

namespace Omni.Business.Tenancy
{
    /// <summary>
    /// OMNI Framework - MoE Tenant Management (C#)
    /// Handles enterprise constraints, throttling, and routing policy enforcement per tenant.
    /// </summary>
    public class OmniMoETenantManager
    {
        private class TenantData 
        {
            public string Id { get; set; }
            public string SubscriptionTier { get; set; }
            public int CurrentTokenUsage { get; set; }
            public int TokenLimit { get; set; }
            public DateTime LastReset { get; set; }
        }

        private readonly ConcurrentDictionary<string, TenantData> _tenants;

        public OmniMoETenantManager()
        {
            _tenants = new ConcurrentDictionary<string, TenantData>();
            Console.WriteLine("OMNI C# (Business Layer): MoE Tenant Manager initialized.");
        }

        public void RegisterTenant(string tenantId, string tier, int limit)
        {
            var tenant = new TenantData 
            {
                Id = tenantId,
                SubscriptionTier = tier,
                TokenLimit = limit,
                CurrentTokenUsage = 0,
                LastReset = DateTime.UtcNow
            };
            _tenants[tenantId] = tenant;
        }

        /// <summary>
        /// Validates if a tenant is allowed to process a request of N tokens.
        /// Throws exception if quota exceeded.
        /// </summary>
        public async Task AuthorizeRequestAsync(string tenantId, int estimatedTokens)
        {
            if (!_tenants.TryGetValue(tenantId, out var tenant))
            {
                throw new UnauthorizedAccessException($"Tenant {tenantId} not found.");
            }

            // Simulate DB/Cache async latency
            await Task.Delay(5);

            lock (tenant)
            {
                // Reset logic (daily)
                if ((DateTime.UtcNow - tenant.LastReset).TotalDays >= 1)
                {
                    tenant.CurrentTokenUsage = 0;
                    tenant.LastReset = DateTime.UtcNow;
                }

                if (tenant.CurrentTokenUsage + estimatedTokens > tenant.TokenLimit)
                {
                    throw new InvalidOperationException($"Tenant {tenantId} exceeded token quota. Upgrade subscription.");
                }

                tenant.CurrentTokenUsage += estimatedTokens;
            }
        }

        public string GetTenantRoutingProfile(string tenantId)
        {
            if (_tenants.TryGetValue(tenantId, out var tenant))
            {
                // Enterprise tenants might get routed to higher parameter-count experts
                return tenant.SubscriptionTier == "Enterprise" ? "high_precision_experts" : "standard_experts";
            }
            return "standard_experts";
        }
    }
}
