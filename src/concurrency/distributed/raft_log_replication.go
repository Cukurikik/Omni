package distributed

import (
	"errors"
)

// OMNI MOTHER SYSTEM - CONCURRENCY LAYER
// Raft Consensus Log Replication

var (
	ErrLogConflict = errors.New("OMNI_FATAL: Term mismatch or log index conflict detected")
)

// AppendEntriesRe
