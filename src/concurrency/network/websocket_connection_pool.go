package network

import (
	"errors"
)

// OMNI MOTHER SYSTEM - CONCURRENCY LAYER
// WebSocket Connection Pool

var (
	ErrClientNotFound = errors.New("OMNI_FATAL: Client ID not found in pool")
)

type WSConnection struct{}
