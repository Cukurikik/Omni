package autogen

import (
	"time"
	"fmt"
	"encoding/json"
)

// OMNI AUTOGEN: State Transition
// Go event producer that tracks the Finite State Machine transitions
// of agents as they pass the conversation baton.
// Source: microsoft/autogen

type FSMTransition struct {
	SessionID   string `json:"session_id"`
	FromAgent   string `json:"from_agent"`
	ToAgent     string `json:"to_agent"`
	Reason      string `json:"reason"`
	TokensSpent int    `json:"tokens_spent"`
	Timestamp   int64  `json:"timestamp"`
}

type StateTracker struct {
	// In production, this would be a Kafka or Redis Stream client
	eventLog []FSMTransition
}

func NewStateTracker() *StateTracker {
	return &StateTracker{
		eventLog: make([]FSMTransition, 0),
	}
}

func (s *StateTracker) RecordTransition(session, from, to, reason string, tokens int) {
	transition := FSMTransition{
		SessionID:   session,
		FromAgent:   from,
		ToAgent:     to,
		Reason:      reason,
		TokensSpent: tokens,
		Timestamp:   time.Now().UnixMilli(),
	}

	s.eventLog = append(s.eventLog, transition)

	// Serialize and emit
	data, _ := json.Marshal(transition)
	fmt.Printf("[OMNI AutoGen] State Transition: %s\n", string(data))
	
	// Example of monadic action: if emission fails, we log locally but do not crash
}

func (s *StateTracker) GetHistory(sessionID string) []FSMTransition {
	var history []FSMTransition
	for _, t := range s.eventLog {
		if t.SessionID == sessionID {
			history = append(history, t)
		}
	}
	return history
}
