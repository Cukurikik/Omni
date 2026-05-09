-- Omni Lua Plugin System (Lua)
-- Scripting & Extensibility Layer
-- Provides dynamic runtime hooks into the Universal Binary execution loop
-- without requiring full recompilation of the C/Rust core.

local OmniPlugin = {}
OmniPlugin.__index = OmniPlugin

function OmniPlugin.new(name)
    local self = setmetatable({}, OmniPlugin)
    self.name = name
    self.hooks = {}
    return self
end

function OmniPlugin:register_hook(event_name, callback)
    if not self.hooks[event_name] then
        self.hooks[event_name] = {}
    end
    table.insert(self.hooks[event_name], callback)
    print(string.format("[%s] Registered hook for event: %s", self.name, event_name))
end

function OmniPlugin:trigger_event(event_name, context)
    local callbacks = self.hooks[event_name]
    if callbacks then
        for _, callback in ipairs(callbacks) do
            -- Safely execute callback
            local status, err = pcall(callback, context)
            if not status then
                print(string.format("[%s] Hook execution error: %s", self.name, err))
            end
        end
    end
end

-- Example Plugin Implementation for Token Logging
local token_logger = OmniPlugin.new("TokenAuditor")

token_logger:register_hook("on_token_generated", function(context)
    -- Context contains token ID, logprobs, and inference latency
    if context.latency_ms > 100 then
        print(string.format("WARN: Slow token generation detected! Latency: %d ms", context.latency_ms))
    end
end)

return OmniPlugin
