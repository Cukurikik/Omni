package network

import (
	"errors"
)

// OMNI MOTHER SYSTEM - CONCURRENCY LAYER
// Biomedical NER gRPC Server

var (
	ErrServerStart = errors.New("OMNI_FATAL: Failed to bind to TCP port")
)
