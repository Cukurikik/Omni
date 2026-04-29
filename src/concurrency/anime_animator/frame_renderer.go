package concurrency

import (
	"time"
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type FrameRequest struct {
	FrameID int64
	Yaw     float64
	Pitch   float64
}

type FrameRenderer struct {
	requestQueue chan FrameRequest
	buffer       map[int64]string
	mu           sync.Mutex
	wg           sync.WaitGroup
	fps          int
}

func NewFrameRenderer(bufferSize int, targetFPS int) *FrameRenderer {
	return &FrameRenderer{
		requestQueue: make(chan FrameRequest, bufferSize),
		buffer:       make(map[int64]string),
		fps:          targetFPS,
	}
}

func (r *FrameRenderer) Start(workers int) {
	for i := 0; i < workers; i++ {
		r.wg.Add(1)
		go r.renderLoop(i)
	}
}

func (r *FrameRenderer) SubmitFrame(req FrameRequest) OmniResult {
	select {
	case r.requestQueue <- req:
		return OmniResult{Value: "Frame submitted"}
	default:
		return OmniResult{Error: fmt.Errorf("renderer queue full, dropping frame")}
	}
}

func (r *FrameRenderer) renderLoop(workerID int) {
	defer r.wg.Done()
	
	// Deterministic interval calculation for frame pacing
	frameDuration := time.Second / time.Duration(r.fps)

	for req := range r.requestQueue {
		start := time.Now()
		
		// Deterministic rendering representation
		renderedData := fmt.Sprintf("FRAME_%d_RENDERED[Y:%.2f, P:%.2f]", req.FrameID, req.Yaw, req.Pitch)
		
		r.mu.Lock()
		r.buffer[req.FrameID] = renderedData
		r.mu.Unlock()

		elapsed := time.Since(start)
		if elapsed < frameDuration {
			// Deterministic frame pacing to maintain constant framerate
			time.Sleep(frameDuration - elapsed)
		}
	}
}

func (r *FrameRenderer) Stop() {
	close(r.requestQueue)
	r.wg.Wait()
}
