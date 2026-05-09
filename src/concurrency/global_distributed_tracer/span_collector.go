package concurrency

import (
	"sync"
	"time"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type SpanCollector struct {
	mu sync.Mutex
}

func NewSpanCollector() *SpanCollector {
	return &SpanCollector{}
}

func (c *SpanCollector) IngestSpanBatchAsync(batchSize int) OmniResult {
	c.mu.Lock()
	defer c.mu.Unlock()

	// Simulate high-throughput Go routine collecting millions of OpenTelemetry trace spans per second
	// Buffers them in memory and flushes them to a centralized Time-Series Database
	time.Sleep(2 * time.Millisecond)

	return OmniResult{Value: "SPANS_INGESTED"}
}
