package types

import "time"

// Instruction represents a single command in the OMNI-ISA.
type Instruction struct {
	OpCode      string              `json:"opcode"`   // Hex representation, e.g., "0xV01"
	Mnemonic    string              `json:"mnemonic"` // Human-readable, e.g., "VID_TRIM"
	Description string              `json:"description"`
	Engine      string              `json:"engine"`   // "ffmpeg", "python", "node", "wasm"
	Category    string              `json:"category"` // "FAST", "MEDIUM", "HEAVY"
	Constraints ResourceConstraints `json:"constraints"`
}

// ResourceConstraints defines the hardware limits for an instruction.
type ResourceConstraints struct {
	MaxRAMBytes int64         `json:"max_ram_bytes"`
	Timeout     time.Duration `json:"timeout"`
	CPULimit    float64       `json:"cpu_limit"` // e.g., 0.5 for 50% CPU
}

// Operand represents a parameter for an instruction.
type Operand struct {
	Name        string      `json:"name"`
	Type        string      `json:"type"` // "string", "number", "boolean", "file"
	Required    bool        `json:"required"`
	Default     interface{} `json:"default,omitempty"`
	MnemonicRef string      `json:"mnemonic_ref"` // Reference for CLI mapping
}

// ExecutionState represents the current status of an instruction being processed.
type ExecutionState struct {
	TaskID    string    `json:"task_id"`
	OpCode    string    `json:"opcode"`
	Status    string    `json:"status"` // "IDLE", "EXEC", "DONE", "FAIL"
	Progress  float64   `json:"progress"`
	StartedAt time.Time `json:"started_at"`
	UpdatedAt time.Time `json:"updated_at"`
}
