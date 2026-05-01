/**
 * OMNI Engine — Rate Limiter (Sliding Window)
 * Layer: Security
 * Implements: Sliding window log algorithm for rate limiting
 */

export interface OmniResult<T> {
    value?: T;
    error?: string;
    is_ok: boolean;
}

export function ok<T>(value: T): OmniResult<T> {
    return { value, is_ok: true };
}

export function fail<T>(error: string): OmniResult<T> {
    return { error, is_ok: false };
}

export class SlidingWindowRateLimiter {
    private requests: Map<string, number[]>;
    private windowMs: number;
    private maxRequests: number;

    constructor(windowMs: number = 60000, maxRequests: number = 100) {
        this.requests = new Map<string, any>();
        this.windowMs = windowMs;
        this.maxRequests = maxRequests;
    }

    allowRequest(ipAddress: string): OmniResult<{allowed: boolean, remaining: number}> {
        if (!ipAddress) return fail("IP address required");

        const now = Date.now();
        const windowStart = now - this.windowMs;

        let userRequests = this.requests.get(ipAddress) || [];
        
        // Filter out requests older than the window
        userRequests = userRequests.filter(timestamp => timestamp > windowStart);
        
        if (userRequests.length >= this.maxRequests) {
            this.requests.set(ipAddress, userRequests);
            return ok({ allowed: false, remaining: 0 });
        }

        userRequests.push(now);
        this.requests.set(ipAddress, userRequests);

        return ok({ 
            allowed: true, 
            remaining: this.maxRequests - userRequests.length 
        });
    }
}
