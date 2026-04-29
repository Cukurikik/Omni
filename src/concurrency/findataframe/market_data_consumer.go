package findataframe

import (
	"time"
	"errors"
	"context"
	"sync"
)

// OMNI CONCURRENCY LAYER: Market Data Consumer
// Ingests high-frequency trading streams concurrently.

type MarketTick struct {
	Symbol string
	Price  float64
	Volume int64
	Time   time.Time
}

type MarketConsumerPool struct {
	numWorkers int
	stream     <-chan MarketTick
	bufferSize int
	mu         sync.Mutex
	timeseries map[string][]float64
}

type OmniResult struct {
	Ok  *string
	Err error
}

func NewMarketConsumerPool(numWorkers int, stream <-chan MarketTick) *MarketConsumerPool {
	return &MarketConsumerPool{
		numWorkers: numWorkers,
		stream:     stream,
		bufferSize: 10000,
		timeseries: make(map[string][]float64),
	}
}

func (p *MarketConsumerPool) Start(ctx context.Context) {
	var wg sync.WaitGroup
	for i := 0; i < p.numWorkers; i++ {
		wg.Add(1)
		go p.consume(ctx, &wg, i)
	}
	wg.Wait()
}

func (p *MarketConsumerPool) consume(ctx context.Context, wg *sync.WaitGroup, workerID int) {
	defer wg.Done()
	for {
		select {
		case <-ctx.Done():
			return
		case tick, ok := <-p.stream:
			if !ok {
				return
			}
			p.processTick(tick)
		}
	}
}

func (p *MarketConsumerPool) processTick(tick MarketTick) OmniResult {
	if tick.Price <= 0 {
		return OmniResult{Err: errors.New("invalid negative or zero price")}
	}

	p.mu.Lock()
	defer p.mu.Unlock()

	series := p.timeseries[tick.Symbol]
	series = append(series, tick.Price)
	
	// Keep buffer bounded
	if len(series) > p.bufferSize {
		series = series[1:]
	}
	p.timeseries[tick.Symbol] = series

	msg := "processed"
	return OmniResult{Ok: &msg}
}
