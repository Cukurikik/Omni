package core

import (
	"crypto/rand"
	"fmt"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"
)

// ULID-like sortable ID implementation using available dependencies.
// Why ULID? Because it's lexicographically sortable by time, making WAL recovery efficient.
// Since we have google/uuid, we'll combine Time + UUID to ensure uniqueness.

var (
	nodeID     [6]byte
	nodeIDOnce sync.Once
)

func getOrCreateNodeID() [6]byte {
	nodeIDOnce.Do(func() {
		hostname, _ := os.Hostname()
		if hostname != "" {
			copy(nodeID[:], hostname)
		} else {
			_, _ = rand.Read(nodeID[:])
		}
	})
	return nodeID
}

// NewOmniID generates a sortable, unique identifier for OMNI tasks.
// Format: TTTTTTTT-UUUU-UUUU
// Where T is hex timestamp and U is part of UUID.
func NewOmniID() string {
	now := time.Now().UnixNano()
	u := uuid.New().String()

	// Create a sortable prefix (hex timestamp)
	// Base36 or Hex ensures it stays short and sortable.
	// We'll use hex for simplicity and 16 chars for precision.
	timestampHex := fmt.Sprintf("%016x", now)

	return fmt.Sprintf("%s-%s", timestampHex, strings.Split(u, "-")[0])
}

// Note: Using strings.Split requires "strings" package. I will update the imports.
