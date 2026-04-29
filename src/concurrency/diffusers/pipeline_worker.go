package diffusers

import (
	"time"
	"fmt"
	"context"
)

// OMNI DIFFUSERS: Pipeline Worker
// Go concurrency wrapper that manages incoming image generation requests and routes them to a Python inference daemon.
// Source: huggingface/diffusers

type GenRequest struct {
	ID             string
	Prompt         string
	NegativePrompt string
	Width          int
	Height         int
	Steps          int
	ResultChan     chan GenResult
}

type GenResult struct {
	ImageURL string
	Error    error
}

type PipelineWorker struct {
	requestQueue chan GenRequest
}

func NewPipelineWorker(queueSize int) *PipelineWorker {
	return &PipelineWorker{
		requestQueue: make(chan GenRequest, queueSize),
	}
}

func (w *PipelineWorker) Submit(req GenRequest) error {
	select {
	case w.requestQueue <- req:
		return nil
	default:
		return fmt.Errorf("Pipeline worker queue is full")
	}
}

// Starts the worker loop to process diffusion requests sequentially on the assigned GPU
func (w *PipelineWorker) Start(ctx context.Context) {
	go func() {
		fmt.Println("[Diffusers Worker] Started listening for tasks.")
		for {
			select {
			case <-ctx.Done():
				fmt.Println("[Diffusers Worker] Shutting down.")
				return
			case req := <-w.requestQueue:
				// Execute the generation via simulated FFI/RPC to Python Diffusers
				w.executeDiffusion(req)
			}
		}
	}()
}

func (w *PipelineWorker) executeDiffusion(req GenRequest) {
	fmt.Printf("[Diffusers Worker] Starting generation for: %s\n", req.Prompt)
	
	// Simulate GPU execution time (e.g., SDXL takes a few seconds)
	time.Sleep(3 * time.Second)

	// Return the result
	req.ResultChan <- GenResult{
		ImageURL: fmt.Sprintf("s3://omni-images/gen_%s.png", req.ID),
		Error:    nil,
	}
}
