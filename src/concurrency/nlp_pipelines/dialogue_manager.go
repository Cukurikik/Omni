package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type DialogueMessage struct {
	SessionID string
	Text      string
}

type DialogueManager struct {
	sessions sync.Map
}

func NewDialogueManager() *DialogueManager {
	return &DialogueManager{}
}

func (m *DialogueManager) HandleMessage(msg DialogueMessage) OmniResult {
	if msg.SessionID == "" {
		return OmniResult{Error: fmt.Errorf("missing session ID")}
	}

	// Load or initialize session state
	val, _ := m.sessions.LoadOrStore(msg.SessionID, 0)
	msgCount := val.(int)

	msgCount++
	m.sessions.Store(msg.SessionID, msgCount)

	// Deterministic dialogue state tracking
	response := fmt.Sprintf("Session %s acknowledged message %d: '%s'. Length: %d chars.",
		msg.SessionID, msgCount, msg.Text, len(msg.Text))

	return OmniResult{Value: response}
}
