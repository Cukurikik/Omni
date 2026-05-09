package network

import (
	"errors"
)

// OMNI MOTHER SYSTEM - CONCURRENCY LAYER
// MQTT Publish-Subscribe Broker

var (
	ErrInvalidTopic = errors.New("OMNI_FATAL: Invalid MQTT topic geometry")
)

type Subscri string
