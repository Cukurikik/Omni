// ===========================================================================
// OMNI WORKER POOL ENGINE (SEMESTER 3 — BATCH 38.9)
// ===========================================================================
// Absorbed From  : Ants + Tunny + errgroup + semaphore patterns
// Logic Inherited: Go / Network Layer (Goroutine Pool & Fan-Out/Fan-In)
// ===========================================================================
//
// By studying Go concurrency patterns, Mother learned:
//   1. Worker pool bounds goroutine count for resource control
//   2. Channels serve as work queues (jobs in, results out)
//   3. errgroup.Group propagates first error and cancels remaining
//   4. Semaphore pattern limits concurrent access
//   5. Graceful shutdown: close job channel, drain workers, wait

package network_gocore

import (
	"context"
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

// ============================================================
// PART 1: Worker Pool
// ============================================================

// Job represents a unit of work.
type Job struct {
	ID      int64
	Payload interface{}
}

// JobResult represents the result of a processed job.
type JobResult struct {
	JobID    int64
	Result   interface{}
	Error    error
	Duration time.Duration
}

// WorkerFunc processes a job and returns a result.
type WorkerFunc func(ctx context.Context, job Job) (interface{}, error)

// WorkerPool manages a pool of goroutine workers.
type WorkerPool struct {
	workerCount int
	jobQueue    chan Job
	results     chan JobResult
	workerFn    WorkerFunc
	ctx         context.Context
	cancel      context.CancelFunc
	wg          sync.WaitGroup
	running     int32
	// Metrics
	totalSubmitted int64
	totalProcessed int64
	totalErrors    int64
	totalDuration  int64 // nanoseconds
}

// NewWorkerPool creates a new pool with the given worker count and queue size.
func NewWorkerPool(workerCount, queueSize int, fn WorkerFunc) *WorkerPool {
	ctx, cancel := context.WithCancel(context.Background())
	pool := &WorkerPool{
		workerCount: workerCount,
		jobQueue:    make(chan Job, queueSize),
		results:     make(chan JobResult, queueSize),
		workerFn:    fn,
		ctx:         ctx,
		cancel:      cancel,
	}
	return pool
}

// Start launches all workers.
func (p *WorkerPool) Start() {
	for i := 0; i < p.workerCount; i++ {
		p.wg.Add(1)
		atomic.AddInt32(&p.running, 1)
		go p.worker(i)
	}
}

// Submit adds a job to the queue (blocks if queue is full).
func (p *WorkerPool) Submit(job Job) error {
	select {
	case <-p.ctx.Done():
		return fmt.Errorf("pool is shut down")
	case p.jobQueue <- job:
		atomic.AddInt64(&p.totalSubmitted, 1)
		return nil
	}
}

// Results returns the results channel for consumption.
func (p *WorkerPool) Results() <-chan JobResult {
	return p.results
}

// Shutdown gracefully stops the pool.
func (p *WorkerPool) Shutdown() {
	close(p.jobQueue) // Signal workers to stop
	p.wg.Wait()       // Wait for all workers to finish
	close(p.results)  // Close results channel
	p.cancel()
}

// ShutdownWithTimeout attempts graceful shutdown with a deadline.
func (p *WorkerPool) ShutdownWithTimeout(timeout time.Duration) error {
	close(p.jobQueue)

	done := make(chan struct{})
	go func() {
		p.wg.Wait()
		close(done)
	}()

	select {
	case <-done:
		close(p.results)
		p.cancel()
		return nil
	case <-time.After(timeout):
		p.cancel()
		return fmt.Errorf("shutdown timed out after %v", timeout)
	}
}

func (p *WorkerPool) worker(id int) {
	defer func() {
		atomic.AddInt32(&p.running, -1)
		p.wg.Done()
	}()

	for job := range p.jobQueue {
		start := time.Now()
		result, err := p.workerFn(p.ctx, job)
		duration := time.Since(start)

		atomic.AddInt64(&p.totalProcessed, 1)
		atomic.AddInt64(&p.totalDuration, int64(duration))

		if err != nil {
			atomic.AddInt64(&p.totalErrors, 1)
		}

		p.results <- JobResult{
			JobID:    job.ID,
			Result:   result,
			Error:    err,
			Duration: duration,
		}
	}
}

// Stats returns pool metrics.
func (p *WorkerPool) Stats() map[string]interface{} {
	totalProcessed := atomic.LoadInt64(&p.totalProcessed)
	totalDuration := atomic.LoadInt64(&p.totalDuration)
	var avgDuration time.Duration
	if totalProcessed > 0 {
		avgDuration = time.Duration(totalDuration / totalProcessed)
	}

	return map[string]interface{}{
		"workerCount":    p.workerCount,
		"running":        atomic.LoadInt32(&p.running),
		"queueCapacity":  cap(p.jobQueue),
		"queueLength":    len(p.jobQueue),
		"totalSubmitted": atomic.LoadInt64(&p.totalSubmitted),
		"totalProcessed": totalProcessed,
		"totalErrors":    atomic.LoadInt64(&p.totalErrors),
		"avgDuration":    avgDuration.String(),
	}
}

// ============================================================
// PART 2: ErrGroup (First-Error Propagation)
// ============================================================

// ErrGroup runs multiple goroutines and returns the first error.
type ErrGroup struct {
	ctx    context.Context
	cancel context.CancelFunc
	wg     sync.WaitGroup
	once   sync.Once
	err    error
	sem    chan struct{} // concurrency limiter
}

// NewErrGroup creates an error group with optional concurrency limit.
func NewErrGroup(ctx context.Context, maxConcurrency int) *ErrGroup {
	gCtx, cancel := context.WithCancel(ctx)
	var sem chan struct{}
	if maxConcurrency > 0 {
		sem = make(chan struct{}, maxConcurrency)
	}
	return &ErrGroup{
		ctx:    gCtx,
		cancel: cancel,
		sem:    sem,
	}
}

// Go launches a function in the group.
func (g *ErrGroup) Go(fn func(ctx context.Context) error) {
	g.wg.Add(1)

	go func() {
		defer g.wg.Done()

		// Acquire semaphore if set
		if g.sem != nil {
			select {
			case g.sem <- struct{}{}:
				defer func() { <-g.sem }()
			case <-g.ctx.Done():
				return
			}
		}

		if err := fn(g.ctx); err != nil {
			g.once.Do(func() {
				g.err = err
				g.cancel()
			})
		}
	}()
}

// Wait blocks until all goroutines complete and returns the first error.
func (g *ErrGroup) Wait() error {
	g.wg.Wait()
	return g.err
}

// ============================================================
// PART 3: Semaphore (Weighted)
// ============================================================

// Semaphore controls concurrent access to a resource.
type Semaphore struct {
	ch           chan struct{}
	maxWeight    int
	totalAcquire int64
	totalRelease int64
}

// NewSemaphore creates a semaphore with the given weight.
func NewSemaphore(maxWeight int) *Semaphore {
	return &Semaphore{
		ch:        make(chan struct{}, maxWeight),
		maxWeight: maxWeight,
	}
}

// Acquire takes a token (blocks if none available).
func (s *Semaphore) Acquire(ctx context.Context) error {
	select {
	case s.ch <- struct{}{}:
		atomic.AddInt64(&s.totalAcquire, 1)
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

// TryAcquire attempts to take a token without blocking.
func (s *Semaphore) TryAcquire() bool {
	select {
	case s.ch <- struct{}{}:
		atomic.AddInt64(&s.totalAcquire, 1)
		return true
	default:
		return false
	}
}

// Release returns a token.
func (s *Semaphore) Release() {
	<-s.ch
	atomic.AddInt64(&s.totalRelease, 1)
}

// Available returns the number of available tokens.
func (s *Semaphore) Available() int {
	return s.maxWeight - len(s.ch)
}

// ============================================================
// PART 4: Fan-Out / Fan-In
// ============================================================

// FanOut distributes items from input channel to N worker goroutines.
func FanOut[T any, R any](
	ctx context.Context,
	input <-chan T,
	workers int,
	process func(context.Context, T) (R, error),
) <-chan JobResult {
	results := make(chan JobResult, workers)
	var wg sync.WaitGroup
	var jobID int64

	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for item := range input {
				id := atomic.AddInt64(&jobID, 1)
				start := time.Now()
				result, err := process(ctx, item)
				results <- JobResult{
					JobID:    id,
					Result:   result,
					Error:    err,
					Duration: time.Since(start),
				}
			}
		}()
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	return results
}

// FanIn merges multiple channels into one.
func FanIn[T any](ctx context.Context, channels ...<-chan T) <-chan T {
	merged := make(chan T)
	var wg sync.WaitGroup

	for _, ch := range channels {
		wg.Add(1)
		go func(c <-chan T) {
			defer wg.Done()
			for {
				select {
				case val, ok := <-c:
					if !ok {
						return
					}
					select {
					case merged <- val:
					case <-ctx.Done():
						return
					}
				case <-ctx.Done():
					return
				}
			}
		}(ch)
	}

	go func() {
		wg.Wait()
		close(merged)
	}()

	return merged
}

// ============================================================
// Diagnostics
// ============================================================

func WorkerPoolDiagnostics() map[string]interface{} {
	return map[string]interface{}{
		"engine": "OmniWorkerPoolEngine",
		"layer":  "Go Network",
		"components": []string{
			"WorkerPool", "ErrGroup", "Semaphore", "FanOut", "FanIn",
		},
		"learned_logic": []string{
			"worker-pool-bounded-goroutines",
			"channel-job-queue-backpressure",
			"errgroup-first-error-cancel",
			"semaphore-weighted-concurrency",
			"fan-out-distribute-workers",
			"fan-in-merge-channels",
			"graceful-shutdown-drain-wait",
			"generic-type-parameter-go118",
		},
	}
}

