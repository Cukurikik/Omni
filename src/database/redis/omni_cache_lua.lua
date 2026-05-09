-- OMNI Redis LUA Script for atomic Rate Limiting & Caching
-- KEYS[1] = rate limit key, KEYS[2] = cache key
-- ARGV[1] = rate limit max, ARGV[2] = rate limit window (seconds)
-- ARGV[3] = cache value, ARGV[4] = cache TTL

local rate_key = KEYS[1]
local cache_key = KEYS[2]
local max_req = tonumber(ARGV[1])
local window = tonumber(ARGV[2])

local current = redis.call("INCR", rate_key)
if current == 1 then
    redis.call("EXPIRE", rate_key, window)
end

if current > max_req then
    return {err="RATE_LIMIT_EXCEEDED"}
end

if ARGV[3] ~= "" then
    redis.call("SETEX", cache_key, tonumber(ARGV[4]), ARGV[3])
    return {ok="CACHED"}
end

local cached_value = redis.call("GET", cache_key)
if cached_value then
    return {ok=cached_value}
else
    return {err="CACHE_MISS"}
end
