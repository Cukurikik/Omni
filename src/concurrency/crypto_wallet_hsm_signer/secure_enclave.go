package concurrency

import (
	"time"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type SecureEnclave struct {
	mu sync.Mutex
}

func NewSecureEnclave() *SecureEnclave {
	return &SecureEnclave{}
}

func (e *SecureEnclave) AwaitHardwareApprovalAsync(txId string) OmniResult {
	e.mu.Lock()
	defer e.mu.Unlock()

	// Simulate Go routine blocking while waiting for human interaction.
	// The user must physically look at the tiny screen on their Ledger device,
	// verify the recipient address, and physically press both buttons to approve the signature.
	time.Sleep(2 * time.Second)

	return OmniResult{Value: "HARDWARE_APPROVED"}
}
