package imagetagging

import (
	"context"
	"errors"
	"sync"
)

// OMNI CONCURRENCY LAYER: Batch Inference Pool
// Batches incoming images into optimal sizes for GPU inference.

type ImageRequest struct {
	ID   string
	Data []byte
}

type TagResult struct {
	ID   string
	Tags []string
}

type BatchInferencePool struct {
	batchSize int
	queue     chan ImageRequest
	results   chan TagResult
	wg        sync.WaitGroup
}

func NewBatchInferencePool(batchSize int) *BatchInferencePool {
	return &BatchInferencePool{
		batchSize: batchSize,
		queue:     make(chan ImageRequest, batchSize*10),
		results:   make(chan TagResult, batchSize*10),
	}
}

func (p *BatchInferencePool) Start(ctx context.Context) {
	p.wg.Add(1)
	go p.batchProcessor(ctx)
}

func (p *BatchInferencePool) batchProcessor(ctx context.Context) {
	defer p.wg.Done()

	buffer := make([]ImageRequest, 0, p.batchSize)

	for {
		select {
		case <-ctx.Done():
			if len(buffer) > 0 {
				p.executeBatch(buffer)
			}
			return
		case req, ok := <-p.queue:
			if !ok {
				if len(buffer) > 0 {
					p.executeBatch(buffer)
				}
				return
			}

			buffer = append(buffer, req)
			if len(buffer) == p.batchSize {
				p.executeBatch(buffer)
				buffer = make([]ImageRequest, 0, p.batchSize)
			}
		}
	}
}

func (p *BatchInferencePool) executeBatch(batch []ImageRequest) {
	// Call to Python Compute Layer via bridge
	// Mocking inference response
	for _, req := range batch {
		p.results <- TagResult{
			ID:   req.ID,
			Tags: []string{"1girl", "solo", "highres"},
		}
	}
}

func (p *BatchInferencePool) Submit(req ImageRequest) error {
	if len(req.Data) == 0 {
		return errors.New("empty image data")
	}
	p.queue <- req
	return nil
}
