-- OMNI Scripting — Lua Inference Client for Embedded/Game Engines
-- Lightweight inference client for LuaJIT/OpenResty/game engines.

local OmniInference = {}
OmniInference.__index = OmniInference

function OmniInference.new(config)
    local self = setmetatable({}, OmniInference)
    self.endpoint = config.endpoint or "http://localhost:8080/api/v1/infer"
    self.max_tokens = config.max_tokens or 256
    self.temperature = config.temperature or 0.7
    self.timeout = config.timeout or 10
    self.stats = { total = 0, errors = 0, total_latency = 0 }
    return self
end

function OmniInference:softmax(logits)
    local max_val = -math.huge
    for _, v in ipairs(logits) do if v > max_val then max_val = v end end
    local sum = 0
    local result = {}
    for i, v in ipairs(logits) do
        result[i] = math.exp(v - max_val)
        sum = sum + result[i]
    end
    for i = 1, #result do result[i] = result[i] / sum end
    return result
end

function OmniInference:cosine_similarity(a, b)
    local dot, norm_a, norm_b = 0, 0, 0
    for i = 1, #a do
        dot = dot + a[i] * b[i]
        norm_a = norm_a + a[i]^2
        norm_b = norm_b + b[i]^2
    end
    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b) + 1e-8)
end

function OmniInference:build_request(prompt, options)
    options = options or {}
    return {
        prompt = prompt,
        max_tokens = options.max_tokens or self.max_tokens,
        temperature = options.temperature or self.temperature,
        top_p = options.top_p or 0.9,
        stop_sequences = options.stop or {},
    }
end

function OmniInference:infer_sync(prompt, options)
    -- For environments with HTTP support (OpenResty, LÖVE2D with luasocket)
    local request = self:build_request(prompt, options)
    local start_time = os.clock()
    self.stats.total = self.stats.total + 1

    -- Placeholder: actual HTTP call depends on Lua environment
    local ok, result = pcall(function()
        local http = require("socket.http")
        local json = require("cjson")
        local body = json.encode(request)
        local response_body = {}
        local _, code = http.request({
            url = self.endpoint,
            method = "POST",
            headers = { ["Content-Type"] = "application/json", ["Content-Length"] = #body },
            source = require("ltn12").source.string(body),
            sink = require("ltn12").sink.table(response_body),
        })
        if code ~= 200 then error("HTTP " .. tostring(code)) end
        return json.decode(table.concat(response_body))
    end)

    local latency = (os.clock() - start_time) * 1000
    self.stats.total_latency = self.stats.total_latency + latency

    if not ok then
        self.stats.errors = self.stats.errors + 1
        return nil, result
    end

    result.latency_ms = latency
    return result
end

function OmniInference:get_stats()
    return {
        total = self.stats.total,
        errors = self.stats.errors,
        avg_latency_ms = self.stats.total > 0 and (self.stats.total_latency / self.stats.total) or 0,
    }
end

-- Math utilities for on-device processing
function OmniInference:top_k_sample(logits, k)
    k = k or 40
    local indexed = {}
    for i, v in ipairs(logits) do indexed[i] = { idx = i, val = v } end
    table.sort(indexed, function(a, b) return a.val > b.val end)
    local top = {}
    for i = 1, math.min(k, #indexed) do top[i] = indexed[i] end
    local vals = {}
    for i, t in ipairs(top) do vals[i] = t.val end
    local probs = self:softmax(vals)
    local r = math.random()
    local cum = 0
    for i, p in ipairs(probs) do
        cum = cum + p
        if r <= cum then return top[i].idx end
    end
    return top[1].idx
end

return OmniInference
