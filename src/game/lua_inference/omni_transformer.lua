-- @omni-layer Game | @omni-lang Lua | @omni-batch 18 | @omni-semester 16
-- @omni-description Lua transformer inference plugin for game engines:
-- lightweight embedding, attention, and text generation for NPC AI.

local OmniTransformer = {}
OmniTransformer.__index = OmniTransformer

function OmniTransformer.new(config)
    local self = setmetatable({}, OmniTransformer)
    self.d_model = config.d_model or 256
    self.n_heads = config.n_heads or 4
    self.head_dim = self.d_model / self.n_heads
    self.scale = 1.0 / math.sqrt(self.head_dim)
    self.vocab_size = config.vocab_size or 8000
    self.max_seq = config.max_seq or 128
    self.stats = { inferences = 0, total_time = 0 }
    return self
end

function OmniTransformer:embed(token_ids)
    local embs = {}
    for i, tid in ipairs(token_ids) do
        local emb = {}
        for d = 1, self.d_model do
            emb[d] = math.sin((tid + 1) * (d) * 0.001) * 0.1
                   + math.cos(i * 0.01 + d * 0.001) * 0.05
        end
        embs[i] = emb
    end
    return embs
end

function OmniTransformer:attention(embs)
    local n = #embs
    local scores = {}
    for i = 1, n do
        scores[i] = {}
        for j = 1, n do
            local dot = 0
            for d = 1, math.min(self.head_dim, #embs[i]) do
                dot = dot + embs[i][d] * embs[j][d]
            end
            scores[i][j] = dot * self.scale
        end
    end
    -- Softmax per row
    for i = 1, n do
        local mx = -1e30
        for j = 1, n do
            if scores[i][j] > mx then mx = scores[i][j] end
        end
        local sum = 0
        for j = 1, n do
            scores[i][j] = math.exp(scores[i][j] - mx)
            sum = sum + scores[i][j]
        end
        for j = 1, n do
            scores[i][j] = scores[i][j] / (sum + 1e-10)
        end
    end
    -- Weighted sum
    local output = {}
    for i = 1, n do
        output[i] = {}
        for d = 1, #embs[1] do
            local val = 0
            for j = 1, n do
                val = val + scores[i][j] * embs[j][d]
            end
            output[i][d] = val
        end
    end
    return output
end

function OmniTransformer:generate(prompt_ids, max_tokens)
    local start = os.clock()
    max_tokens = max_tokens or 32
    local context = {}
    for _, id in ipairs(prompt_ids) do
        table.insert(context, id)
    end
    local output = {}
    for step = 1, max_tokens do
        local embs = self:embed(context)
        local attended = self:attention(embs)
        local last = attended[#attended]
        local logit = 0
        for d = 1, math.min(16, #last) do
            logit = logit + last[d] * math.sin(step * 0.1 + d * 0.01)
        end
        local token_id = math.abs(math.floor(logit * 10000)) % self.vocab_size
        table.insert(output, token_id)
        table.insert(context, token_id)
        if #context > self.max_seq then
            table.remove(context, 1)
        end
        if token_id == 0 then break end
    end
    local elapsed = (os.clock() - start) * 1000
    self.stats.inferences = self.stats.inferences + 1
    self.stats.total_time = self.stats.total_time + elapsed
    return output, elapsed
end

function OmniTransformer:get_stats()
    return {
        inferences = self.stats.inferences,
        avg_time_ms = self.stats.inferences > 0
            and self.stats.total_time / self.stats.inferences or 0,
    }
end

return OmniTransformer
