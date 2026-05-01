-- OMNI MOTHER SYSTEM - SECURITY LAYER
-- High-Performance Redis Lua Script for API Rate Limiting
-- Algorithm: Token Bucket (Atomic Evaluation)

-- KEYS[1]: Rate limit key (e.g., "rate:limit:ip:192.168.1.1")
-- ARGV[1]: Maximum bucket capacity (e.g., 100 tokens)
-- ARGV[2]: Refill rate per second (e.g., 10 tokens/sec)
-- ARGV[3]: Current timestamp in microseconds
-- ARGV[4]: Tokens requested (usually 1)

local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

-- Retrieve current state [last_refill_time, current_tokens]
local state = redis.call("HMGET", key, "last_refill", "tokens")

local last_refill = tonumber(state[1])
local tokens = tonumber(state[2])

if not last_refill or not tokens then
    -- First time seeing this key, initialize bucket
    last_refill = now
    tokens = capacity
end

-- Calculate time passed in seconds
local delta_sec = math.max(0, (now - last_refill) / 1000000)

-- Refill tokens based on time passed
local refill_amount = delta_sec * refill_rate
tokens = math.min(capacity, tokens + refill_amount)

-- Check if request can be fulfilled
local allowed = 0
local new_tokens = tokens

if tokens >= requested then
    allowed = 1
    new_tokens = tokens - requested
    -- Update timestamp only if we successfully took a token
    last_refill = now
end

-- Save state back to Redis
redis.call("HMSET", key, "last_refill", last_refill, "tokens", new_tokens)
-- Set TTL to prevent stale keys (time to fill bucket completely * 2)
local ttl = math.ceil((capacity / refill_rate) * 2)
redis.call("EXPIRE", key, ttl)

-- Return format: { Allowed (1/0), Remaining Tokens }
return { allowed, math.floor(new_tokens) }
