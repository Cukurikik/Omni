using System;
using System.Collections.Concurrent;
using System.Threading;

namespace Omni.Domain.MoE
{
    // OMNI MOTHER Production Zero-Mock Quota Manager
    // High-performance token bucket implementation for strict API rate limiting
    // ensuring fair usage across multi-tenant MoE deployments.

    public class TenantQuota
    {
        public string TenantId { get; }
        public long TokensAllowedPerMinute { get; }
        private long _currentTokens;
        private long _lastRefillTicks;

        public TenantQuota(string tenantId, long tokensAllowed)
        {
            TenantId = tenantId;
            TokensAllowedPerMinute = tokensAllowed;
            _currentTokens = tokensAllowed;
            _lastRefillTicks = DateTime.UtcNow.Ticks;
        }

        public bool TryConsume(long tokensNeeded)
        {
            Refill();
            
            // Atomic check and decrement
            long current = Interlocked.Read(ref _currentTokens);
            while (current >= tokensNeeded)
            {
                long newValue = current - tokensNeeded;
                if (Interlocked.CompareExchange(ref _currentTokens, newValue, current) == current)
                {
                    return true;
                }
                current = Interlocked.Read(ref _currentTokens);
            }
            
            return false;
        }

        private void Refill()
        {
            long currentTicks = DateTime.UtcNow.Ticks;
            long lastTicks = Interlocked.Read(ref _lastRefillTicks);
            long elapsedTicks = currentTicks - lastTicks;
            
            // Ticks per minute = 600,000,000
            double minutesElapsed = elapsedTicks / 600000000.0;
            
            if (minutesElapsed > 0.01) // Refill at least every ~0.6 seconds
            {
                long tokensToAdd = (long)(TokensAllowedPerMinute * minutesElapsed);
                if (tokensToAdd > 0)
                {
                    // Update timestamp
                    Interlocked.Exchange(ref _lastRefillTicks, currentTicks);
                    
                    // Add tokens, cap at max
                    long currentTokens;
                    long newTokens;
                    do
                    {
                        currentTokens = Interlocked.Read(ref _currentTokens);
                        newTokens = Math.Min(TokensAllowedPerMinute, currentTokens + tokensToAdd);
                    } while (Interlocked.CompareExchange(ref _currentTokens, newTokens, currentTokens) != currentTokens);
                }
            }
        }
    }

    public class QuotaManager
    {
        private readonly ConcurrentDictionary<string, TenantQuota> _quotas = new();

        public void RegisterTenant(string tenantId, long tokensPerMinute)
        {
            _quotas[tenantId] = new TenantQuota(tenantId, tokensPerMinute);
        }

        public bool AuthorizeRequest(string tenantId, long estimatedTokens)
        {
            if (_quotas.TryGetValue(tenantId, out var quota))
            {
                return quota.TryConsume(estimatedTokens);
            }
            // Deny by default if tenant unknown
            return false;
        }
    }
}
