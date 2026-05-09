package network

import (
	"errors"
)

// OMNI MOTHER SYSTEM - CONCURRENCY LAYER
// gRPC Bidirectional Streaming Multiplexer.

var (
	ErrStreamClosed = errors.New("OMNI_FATAL: The gRPC stream was termina")
)
