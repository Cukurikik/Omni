-- Omni AutoAgents NPC Logic (Lua)
-- Game Engine Layer: Agentic reasoning embedded into NPC behavior

local OmniNPC = {}
OmniNPC.__index = OmniNPC

function OmniNPC.new(name, role)
    local self = setmetatable({}, OmniNPC)
    self.name = name
    self.role = role
    self.state = "IDLE"
    return self
end

function OmniNPC:evaluate_agentic_action(context_threat_level)
    if type(context_threat_level) ~= "number" then
        return nil, "Threat level must be numeric"
    end

    if context_threat_level > 0.8 then
        self.state = "EVADE"
    elseif context_threat_level > 0.4 then
        self.state = "INVESTIGATE"
    else
        self.state = "PATROL"
    end

    return self.state, nil
end

return OmniNPC
