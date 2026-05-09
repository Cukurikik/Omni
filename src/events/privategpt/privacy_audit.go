package privategpt

import (
	"context"
	"fmt"
	"time"
)

// OMNI PRIVATEGPT: Privacy Audit Logger
// Go routines to log local document access and LLM prompts for compliance purposes.
// Ensures that air-gapped usage can still be audited internally.
// Source: imartinez/privateGPT

type AuditEvent struct {
	Timestamp int64
	User      string
	Action    string
	Document  string
	Prompt    string
}

type AuditLogger struct {
	logChannel chan AuditEvent
}

func NewAuditLogger(bufferSize int) *AuditLogger {
	return &AuditLogger{
		logChannel: make(chan AuditEvent, bufferSize),
	}
}

// Log records an event asynchronously
func (al *AuditLogger) Log(user string, action string, doc string, prompt string) {
	event := AuditEvent{
		Timestamp: time.Now().Unix(),
		User:      user,
		Action:    action,
		Document:  doc,
		Prompt:    prompt,
	}

	select {
	case al.logChannel <- event:
		// Queued successfully
	default:
		// In a highly regulated environment, dropping audit logs is bad.
		// For privateGPT, we might block or write to a fallback file.
		fmt.Println("[SECURITY WARNING] Audit log buffer full, event dropped!")
	}
}

// Start flushes logs to a secure internal file or database
func (al *AuditLogger) Start(ctx context.Context) {
	go func() {
		for {
			select {
			case <-ctx.Done():
				fmt.Println("Shutting down audit logger.")
				return
			case event := <-al.logChannel:
				// Simulated secure write to disk
				fmt.Printf("[AUDIT] %d | User: %s | Action: %s | Doc: %s\n",
					event.Timestamp, event.User, event.Action, event.Document)
			}
		}
	}()
}
