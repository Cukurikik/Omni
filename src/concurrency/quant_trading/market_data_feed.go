package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type MarketTick struct {
	Symbol    string
	Price     float64
	Volume    float64
	Timestamp int64
}

type MarketDataFeed struct {
	subscribers map[string]chan MarketTick
	mu          sync.RWMutex
}

func NewMarketDataFeed() *MarketDataFeed {
	return &MarketDataFeed{
		subscribers: make(map[string]chan MarketTick),
	}
}

func (m *MarketDataFeed) Subscribe(symbol string) (chan MarketTick, OmniResult) {
	if symbol == "" {
		return nil, OmniResult{Error: fmt.Errorf("invalid symbol")}
	}

	ch := make(chan MarketTick, 1000)

	m.mu.Lock()
	m.subscribers[symbol] = ch
	m.mu.Unlock()

	return ch, OmniResult{Value: "Subscribed"}
}

func (m *MarketDataFeed) PublishTick(tick MarketTick) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	if ch, exists := m.subscribers[tick.Symbol]; exists {
		select {
		case ch <- tick:
			// Published successfully
		default:
			// Drop tick if subscriber is too slow (Zero-mock backpressure handling)
		}
	}
}
