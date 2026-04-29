package quanttrading

import (
	"errors"
	"sync"
)

type OmniResult struct {
	Data  interface{}
	Error error
}

type MarketTick struct {
	Symbol    string
	Bid       float64
	Ask       float64
	Timestamp int64
}

type MarketStreamer struct {
	subscribers map[string][]chan MarketTick
	mu          sync.RWMutex
	isActive    bool
}

func NewMarketStreamer() *MarketStreamer {
	return &MarketStreamer{
		subscribers: make(map[string][]chan MarketTick),
		isActive:    true,
	}
}

func (s *MarketStreamer) Subscribe(symbol string) (chan MarketTick, OmniResult) {
	s.mu.Lock()
	defer s.mu.Unlock()

	if !s.isActive {
		return nil, OmniResult{Error: errors.New("streamer is inactive")}
	}

	ch := make(chan MarketTick, 100)
	s.subscribers[symbol] = append(s.subscribers[symbol], ch)
	return ch, OmniResult{Data: "subscribed"}
}

func (s *MarketStreamer) PublishTick(tick MarketTick) OmniResult {
	s.mu.RLock()
	defer s.mu.RUnlock()

	if !s.isActive {
		return OmniResult{Error: errors.New("streamer is inactive")}
	}
	
	if tick.Bid <= 0 || tick.Ask <= 0 || tick.Bid >= tick.Ask {
	    return OmniResult{Error: errors.New("invalid tick data logic")}
	}

	subs, exists := s.subscribers[tick.Symbol]
	if !exists {
		return OmniResult{Data: "no_subscribers"}
	}

	for _, ch := range subs {
		select {
		case ch <- tick:
			// Sent successfully
		default:
			// Dropped to prevent blocking HFT ingestion
		}
	}

	return OmniResult{Data: "published"}
}

func (s *MarketStreamer) Shutdown() {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.isActive = false
	for _, subs := range s.subscribers {
		for _, ch := range subs {
			close(ch)
		}
	}
}
