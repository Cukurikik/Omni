package network

import (
	"errors"
)

// OMNI MOTHER SYSTEM - CONCURRENCY LAYER
// Distributed Gradient All-Reduce (Ring Topology)

var (
	ErrInvalidNodeCount = errors.New("OMNI_FATAL: All-Reduce requires at least 2 nodes")
)
