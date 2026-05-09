package concurrency

import (
	"sync"
	"time"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type LightCurve struct {
	mu sync.Mutex
}

func NewLightCurve() *LightCurve {
	return &LightCurve{}
}

func (l *LightCurve) StreamSpectralPhotometryAsync(starId string) OmniResult {
	l.mu.Lock()
	defer l.mu.Unlock()

	// Simulate high-throughput Go routine aggregating photon counts from a space telescope.
	// We are looking for a 0.01% dip in brightness that lasts for a few hours (a planetary transit),
	// across hundreds of thousands of target stars simultaneously.
	time.Sleep(5 * time.Millisecond)

	return OmniResult{Value: "LIGHT_CURVE_UPDATED"}
}
