-- @omni-domain System Layer (Embedded State Machine)
-- @omni-source lua.org/pil (Production Lua Pattern)
-- @omni-description Lua Embedded State Machine for OMNI runtime event-driven control flow.
-- @omni-requirement zero-mock, monadic-error

local OmniResult = {}
OmniResult.__index = OmniResult

function OmniResult.ok(value)
    return setmetatable({ _ok = true, _value = value, _err = nil }, OmniResult)
end

function OmniResult.err(msg)
    return setmetatable({ _ok = false, _value = nil, _err = msg }, OmniResult)
end

function OmniResult:is_ok() return self._ok end
function OmniResult:unwrap()
    if not self._ok then error("unwrap on error: " .. tostring(self._err)) end
    return self._value
end
function OmniResult:unwrap_err() return self._err end

function OmniResult:and_then(fn)
    if self._ok then return fn(self._value) end
    return self
end

-- State definition
local State = {}
State.__index = State

function State.new(name, on_enter, on_exit, on_update)
    return setmetatable({
        name = name,
        on_enter = on_enter or function() end,
        on_exit = on_exit or function() end,
        on_update = on_update or function() end,
        transitions = {},
    }, State)
end

function State:add_transition(event_name, target_state_name, guard)
    self.transitions[event_name] = {
        target = target_state_name,
        guard = guard or function() return true end,
    }
    return self
end

-- State Machine
local StateMachine = {}
StateMachine.__index = StateMachine

function StateMachine.new(name)
    return setmetatable({
        name = name,
        states = {},
        current_state = nil,
        history = {},
        max_history = 256,
        listeners = {},
        _started = false,
    }, StateMachine)
end

function StateMachine:add_state(state)
    if not state or not state.name then
        return OmniResult.err("invalid state: missing name")
    end
    if self.states[state.name] then
        return OmniResult.err("duplicate state: " .. state.name)
    end
    self.states[state.name] = state
    return OmniResult.ok(self)
end

function StateMachine:set_initial(state_name)
    if not self.states[state_name] then
        return OmniResult.err("unknown state: " .. tostring(state_name))
    end
    self.current_state = self.states[state_name]
    return OmniResult.ok(self)
end

function StateMachine:start()
    if not self.current_state then
        return OmniResult.err("no initial state set")
    end
    self._started = true
    self.current_state.on_enter(self.current_state)
    self:_record("START", nil, self.current_state.name)
    self:_notify("start", self.current_state.name)
    return OmniResult.ok(self.current_state.name)
end

function StateMachine:send_event(event_name, payload)
    if not self._started then
        return OmniResult.err("state machine not started")
    end
    if not self.current_state then
        return OmniResult.err("no current state")
    end

    local transition = self.current_state.transitions[event_name]
    if not transition then
        return OmniResult.err(
            string.format("no transition for event '%s' in state '%s'", event_name, self.current_state.name)
        )
    end

    if not transition.guard(payload) then
        return OmniResult.err(
            string.format("guard rejected event '%s' in state '%s'", event_name, self.current_state.name)
        )
    end

    local target = self.states[transition.target]
    if not target then
        return OmniResult.err("transition target not found: " .. transition.target)
    end

    local from_name = self.current_state.name
    self.current_state.on_exit(self.current_state)
    self.current_state = target
    self.current_state.on_enter(self.current_state, payload)

    self:_record(event_name, from_name, target.name)
    self:_notify("transition", from_name, target.name, event_name)

    return OmniResult.ok(target.name)
end

function StateMachine:update(dt)
    if not self._started or not self.current_state then
        return OmniResult.err("not running")
    end
    self.current_state.on_update(self.current_state, dt)
    return OmniResult.ok(true)
end

function StateMachine:current()
    if self.current_state then
        return OmniResult.ok(self.current_state.name)
    end
    return OmniResult.err("no current state")
end

function StateMachine:on(event_type, callback)
    if not self.listeners[event_type] then
        self.listeners[event_type] = {}
    end
    table.insert(self.listeners[event_type], callback)
end

function StateMachine:get_history()
    return OmniResult.ok(self.history)
end

function StateMachine:reset()
    self._started = false
    self.current_state = nil
    self.history = {}
    return OmniResult.ok(true)
end

function StateMachine:_record(event, from, to)
    table.insert(self.history, {
        event = event,
        from = from,
        to = to,
        timestamp = os.clock(),
    })
    if #self.history > self.max_history then
        table.remove(self.history, 1)
    end
end

function StateMachine:_notify(event_type, ...)
    local cbs = self.listeners[event_type]
    if cbs then
        for _, cb in ipairs(cbs) do
            local ok, err = pcall(cb, ...)
            if not ok then
                io.stderr:write("[StateMachine] listener error: " .. tostring(err) .. "\n")
            end
        end
    end
end

-- Hierarchical State Machine (HSM) support
local HierarchicalStateMachine = {}
HierarchicalStateMachine.__index = HierarchicalStateMachine
setmetatable(HierarchicalStateMachine, { __index = StateMachine })

function HierarchicalStateMachine.new(name)
    local self = StateMachine.new(name)
    setmetatable(self, HierarchicalStateMachine)
    self.sub_machines = {}
    return self
end

function HierarchicalStateMachine:add_sub_machine(state_name, sub_machine)
    if not self.states[state_name] then
        return OmniResult.err("parent state not found: " .. state_name)
    end
    self.sub_machines[state_name] = sub_machine
    return OmniResult.ok(self)
end

function HierarchicalStateMachine:send_event(event_name, payload)
    if self.current_state and self.sub_machines[self.current_state.name] then
        local sub = self.sub_machines[self.current_state.name]
        local result = sub:send_event(event_name, payload)
        if result:is_ok() then return result end
    end
    return StateMachine.send_event(self, event_name, payload)
end

-- Module exports
return {
    OmniResult = OmniResult,
    State = State,
    StateMachine = StateMachine,
    HierarchicalStateMachine = HierarchicalStateMachine,
}
