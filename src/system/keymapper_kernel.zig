// ===========================================================================
// OMNI SYSTEM LAYER — KEYMAPPER KERNEL INPUT INTERCEPTOR
// ===========================================================================
// Source Paradigm : sds100/KeyMapper
// Domain Layer   : System (System programming modern, no-undefined-behavior)
// Language        : Zig
// Function        : Low-level keyboard/gamepad input remapping engine with
//                   key-to-key, key-to-sequence, conditional triggers,
//                   and layer-based keymap switching
// ===========================================================================

const std = @import("std");

// ---- Key Codes (subset of Linux input event codes) ------------------------

pub const KeyCode = enum(u16) {
    KEY_RESERVED = 0,
    KEY_ESC = 1,
    KEY_1 = 2, KEY_2 = 3, KEY_3 = 4, KEY_4 = 5, KEY_5 = 6,
    KEY_6 = 7, KEY_7 = 8, KEY_8 = 9, KEY_9 = 10, KEY_0 = 11,
    KEY_Q = 16, KEY_W = 17, KEY_E = 18, KEY_R = 19, KEY_T = 20,
    KEY_Y = 21, KEY_U = 22, KEY_I = 23, KEY_O = 24, KEY_P = 25,
    KEY_A = 30, KEY_S = 31, KEY_D = 32, KEY_F = 33, KEY_G = 34,
    KEY_LEFTCTRL = 29, KEY_LEFTSHIFT = 42, KEY_LEFTALT = 56,
    KEY_CAPSLOCK = 58, KEY_TAB = 15, KEY_SPACE = 57,
    KEY_ENTER = 28, KEY_BACKSPACE = 14,
    KEY_UP = 103, KEY_DOWN = 108, KEY_LEFT = 105, KEY_RIGHT = 106,
    KEY_F1 = 59, KEY_F2 = 60, KEY_F3 = 61, KEY_F4 = 62,
};

pub const KeyAction = enum(u8) {
    press = 1,
    release = 0,
    repeat = 2,
};

// ---- Mapping Rules --------------------------------------------------------

pub const MappingType = enum {
    simple,       // single key → single key
    sequence,     // single key → sequence of keys
    conditional,  // key + modifier → action
    layer_switch, // switch active keymap layer
    block,        // absorb key (no output)
};

pub const MappingRule = struct {
    trigger_key: KeyCode,
    trigger_action: KeyAction,
    mapping_type: MappingType,

    // For simple mapping
    output_key: KeyCode,

    // For sequence mapping (up to 8 keys)
    output_sequence: [8]KeyCode,
    sequence_len: u8,
    inter_key_delay_ms: u16,

    // For conditional mapping
    required_modifier: KeyCode,

    // For layer switching
    target_layer: u8,

    pub fn simpleMap(from: KeyCode, to: KeyCode) MappingRule {
        return MappingRule{
            .trigger_key = from,
            .trigger_action = .press,
            .mapping_type = .simple,
            .output_key = to,
            .output_sequence = std.mem.zeroes([8]KeyCode),
            .sequence_len = 0,
            .inter_key_delay_ms = 0,
            .required_modifier = .KEY_RESERVED,
            .target_layer = 0,
        };
    }

    pub fn blockKey(key: KeyCode) MappingRule {
        var rule = simpleMap(key, .KEY_RESERVED);
        rule.mapping_type = .block;
        return rule;
    }
};

// ---- Keymap Layer ---------------------------------------------------------

pub const MAX_RULES_PER_LAYER = 64;
pub const MAX_LAYERS = 8;

pub const KeymapLayer = struct {
    name: [32]u8,
    name_len: u8,
    rules: [MAX_RULES_PER_LAYER]MappingRule,
    rule_count: u16,

    pub fn init(name: []const u8) KeymapLayer {
        var layer = KeymapLayer{
            .name = std.mem.zeroes([32]u8),
            .name_len = @intCast(name.len),
            .rules = undefined,
            .rule_count = 0,
        };
        @memcpy(layer.name[0..name.len], name);
        return layer;
    }

    pub fn addRule(self: *KeymapLayer, rule: MappingRule) void {
        if (self.rule_count < MAX_RULES_PER_LAYER) {
            self.rules[self.rule_count] = rule;
            self.rule_count += 1;
        }
    }

    pub fn findRule(self: *const KeymapLayer, key: KeyCode) ?*const MappingRule {
        for (0..self.rule_count) |i| {
            if (self.rules[i].trigger_key == key) {
                return &self.rules[i];
            }
        }
        return null;
    }
};

// ---- Input Event ----------------------------------------------------------

pub const InputEvent = struct {
    timestamp_us: u64,
    key: KeyCode,
    action: KeyAction,
};

pub const OutputEvent = struct {
    key: KeyCode,
    action: KeyAction,
};

// ---- Core Mapper Engine ---------------------------------------------------

pub const MapperEngine = struct {
    layers: [MAX_LAYERS]KeymapLayer,
    layer_count: u8,
    active_layer: u8,
    events_processed: u64,
    events_remapped: u64,
    events_blocked: u64,

    pub fn init() MapperEngine {
        return MapperEngine{
            .layers = undefined,
            .layer_count = 0,
            .active_layer = 0,
            .events_processed = 0,
            .events_remapped = 0,
            .events_blocked = 0,
        };
    }

    pub fn addLayer(self: *MapperEngine, layer: KeymapLayer) void {
        if (self.layer_count < MAX_LAYERS) {
            self.layers[self.layer_count] = layer;
            self.layer_count += 1;
        }
    }

    /// Process a single input event through the active layer's rules.
    /// Returns the output event (or null if blocked).
    pub fn processEvent(self: *MapperEngine, event: InputEvent) ?OutputEvent {
        self.events_processed += 1;

        if (self.active_layer >= self.layer_count) {
            return OutputEvent{ .key = event.key, .action = event.action };
        }

        const layer = &self.layers[self.active_layer];
        const rule = layer.findRule(event.key);

        if (rule == null) {
            // Pass through unmapped keys
            return OutputEvent{ .key = event.key, .action = event.action };
        }

        const r = rule.?;
        switch (r.mapping_type) {
            .simple => {
                self.events_remapped += 1;
                return OutputEvent{ .key = r.output_key, .action = event.action };
            },
            .block => {
                self.events_blocked += 1;
                return null;
            },
            .layer_switch => {
                if (r.target_layer < self.layer_count) {
                    self.active_layer = r.target_layer;
                }
                return null;
            },
            else => {
                return OutputEvent{ .key = event.key, .action = event.action };
            },
        }
    }
};
