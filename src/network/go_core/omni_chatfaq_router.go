// Omni ChatFAQ Router (Go)
// Network Layer: RAG + FSM conversational routing.
// Ref: ChatFAQ/ChatFAQ — Open-source conversational AI with RAG.
package network_gocore

import (
	"errors"
	"strings"
	"sync/atomic"
)

type ConvState struct {
	SessionID   string
	CurrentNode string
	History     []string
}
type Router struct{ counter uint64 }

func NewRouter() *Router { return &Router{} }
func (r *Router) Route(state ConvState) (string, error) {
	if state.CurrentNode == "" {
		return "", errors.New("OMNI_ERR: empty node")
	}
	atomic.AddUint64(&r.counter, 1)
	if strings.HasPrefix(state.CurrentNode, "faq_") {
		return "retrieval", nil
	}
	return "generation", nil
}

