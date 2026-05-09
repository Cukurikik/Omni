package finfact

import (
	"context"
	"errors"
	"sync"
)

type VerificationTask struct {
	ClaimID string
	Claim   string
	Text    string
}

type VerificationResult struct {
	ClaimID string
	IsValid bool
	Score   float64
	Error   error
}

type VerifierPool struct {
	workers int
	tasks   chan VerificationTask
	results chan VerificationResult
	wg      sync.WaitGroup
	quit    chan struct{}
}

func NewVerifierPool(workers int, buffer int) *VerifierPool {
	p := &VerifierPool{
		workers: workers,
		tasks:   make(chan VerificationTask, buffer),
		results: make(chan VerificationResult, buffer),
		quit:    make(chan struct{}),
	}
	p.start()
	return p
}

func (p *VerifierPool) start() {
	for i := 0; i < p.workers; i++ {
		p.wg.Add(1)
		go p.worker()
	}
}

func (p *VerifierPool) worker() {
	defer p.wg.Done()
	for {
		select {
		case <-p.quit:
			return
		case task := <-p.tasks:
			p.process(task)
		}
	}
}

func (p *VerifierPool) process(task VerificationTask) {
	if task.Claim == "" {
		p.results <- VerificationResult{ClaimID: task.ClaimID, Error: errors.New("empty claim")}
		return
	}

	// Simulate NLI or logic verification
	isValid := len(task.Text) > len(task.Claim)

	p.results <- VerificationResult{
		ClaimID: task.ClaimID,
		IsValid: isValid,
		Score:   0.85,
		Error:   nil,
	}
}

func (p *VerifierPool) Submit(ctx context.Context, task VerificationTask) (VerificationResult, error) {
	select {
	case <-ctx.Done():
		return VerificationResult{}, ctx.Err()
	case p.tasks <- task:
	}

	select {
	case <-ctx.Done():
		return VerificationResult{}, ctx.Err()
	case res := <-p.results:
		return res, res.Error
	}
}

func (p *VerifierPool) Close() {
	close(p.quit)
	p.wg.Wait()
}
