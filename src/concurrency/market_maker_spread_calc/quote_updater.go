package concurrency

import (
	"time"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type QuoteUpdater struct {
	mu sync.Mutex
}

func NewQuoteUpdater() *QuoteUpdater {
	return &QuoteUpdater{}
}

func (u *QuoteUpdater) UpdateQuotesAsync(newBid float64, newAsk float64) OmniResult {
	u.mu.Lock()
	defer u.mu.Unlock()

	// Simulate high-throughput Go routine managing active orders on the exchange.
	// As price volatility changes, this worker cancels old limit orders and places new ones
	// continuously at 5,000+ updates per second to maintain the bid/ask spread.
	time.Sleep(200 * time.Microsecond)

	return OmniResult{Value: "QUOTES_UPDATED"}
}
