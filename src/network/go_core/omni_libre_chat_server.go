// Omni Libre Chat Server (Go)
// Network Layer: Self-hosted LLM chat inference bridge.
// Ref: vemonet/libre-chat

package go_core

import (
	"errors"
	"strings"
	"time"
)

type ChatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatResponse struct {
	Reply     string    `json:"reply"`
	Timestamp time.Time `json:"timestamp"`
	TokensUsed int      `json:"tokens_used"`
}

func ValidateMessages(msgs []ChatMessage) error {
	if len(msgs) == 0 {
		return errors.New("empty message list")
	}
	for _, m := range msgs {
		if m.Role == "" || m.Content == "" {
			return errors.New("role and content must be non-empty")
		}
		if m.Role != "system" && m.Role != "user" && m.Role != "assistant" {
			return errors.New("invalid role: " + m.Role)
		}
	}
	return nil
}

func CountTokensApprox(text string) int {
	return len(strings.Fields(text))
}
