package concurrency

import (
	"time"
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type AuthSession struct {
	SessionID string
	State     string
	ExpiresAt int64
}

type SessionTracker struct {
	sessions map[string]AuthSession
	mu       sync.RWMutex
}

func NewSessionTracker() *SessionTracker {
	t := &SessionTracker{
		sessions: make(map[string]AuthSession),
	}
	
	// Start background cleanup routine
	go t.cleanupLoop()
	return t
}

func (t *SessionTracker) cleanupLoop() {
	for {
		time.Sleep(1 * time.Second)
		t.mu.Lock()
		now := time.Now().Unix()
		for id, session := range t.sessions {
			if session.ExpiresAt < now {
				delete(t.sessions, id)
				fmt.Printf("OAuth Tracker: Evicted expired session %s\n", id)
			}
		}
		t.mu.Unlock()
	}
}

func (t *SessionTracker) UpsertSession(session AuthSession) OmniResult {
	t.mu.Lock()
	defer t.mu.Unlock()
	
	t.sessions[session.SessionID] = session
	return OmniResult{Value: true}
}
