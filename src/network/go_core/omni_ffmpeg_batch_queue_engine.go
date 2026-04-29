// OmniFFmpegBatchQueueEngine — Production-Grade Go Queue
// =======================================================
// Absorbed from: eibols/ffmpeg_batch
//
// Key patterns learned and implemented:
// - Job queuing and wait groups for OS thread multiplexing
// - Non-blocking Cmd execution preventing I/O stalls
// - Error aggregation across massive pools
//
// OMNI Layer: network/go_core
// @since 2026.4.0

package go_core

import (
	"context"
	"errors"
	"fmt"
	"os/exec"
	"sync"
	"time"
)

// --- Domain Structures ---

type TranscodeJob struct {
	ID         string
	SourceFile string
	TargetFile string
	Args       []string
}

type FFmpegJobResult struct {
	JobID    string
	Success  bool
	ErrorMsg string
	Duration time.Duration
}

// OmniFFmpegBatchQueueEngine maps a high-throughput Go routine pool isolating FFMPEG boundaries.
type OmniFFmpegBatchQueueEngine struct {
	workerCount int
}

// NewOmniFFmpegBatchQueueEngine configures the pipeline pool size.
func NewOmniFFmpegBatchQueueEngine(workers int) *OmniFFmpegBatchQueueEngine {
	if workers < 1 {
		workers = 1 // Prevent deadlock
	}
	return &OmniFFmpegBatchQueueEngine{workerCount: workers}
}

// ExecuteBatch runs massive processing operations concurrently.
func (e *OmniFFmpegBatchQueueEngine) ExecuteBatch(ctx context.Context, jobs []TranscodeJob) ([]FFmpegJobResult, error) {
	if len(jobs) == 0 {
		return nil, errors.New("EMPTY_BATCH: No jobs provided")
	}

	jobQueue := make(chan TranscodeJob, len(jobs))
	resultQueue := make(chan FFmpegJobResult, len(jobs))
	var wg sync.WaitGroup

	// Spawn strictly bounded worker pool
	for i := 0; i < e.workerCount; i++ {
		wg.Add(1)
		go e.worker(ctx, jobQueue, resultQueue, &wg)
	}

	// Load jobs into pipeline
	for _, job := range jobs {
		jobQueue <- job
	}
	close(jobQueue) // Seal pipeline

	// Setup synchronized drain
	go func() {
		wg.Wait()
		close(resultQueue) // Seal results when all workers exit
	}()

	var results []FFmpegJobResult
	for res := range resultQueue {
		results = append(results, res)
	}

	return results, nil
}

func (e *OmniFFmpegBatchQueueEngine) worker(ctx context.Context, jobs <-chan TranscodeJob, results chan<- FFmpegJobResult, wg *sync.WaitGroup) {
	defer wg.Done()

	for job := range jobs {
		select {
		case <-ctx.Done():
			results <- FFmpegJobResult{
				JobID:    job.ID,
				Success:  false,
				ErrorMsg: "CONTEXT_CANCELED",
			}
			return
		default:
			start := time.Now()
			err := e.processSingleJob(ctx, job)
			duration := time.Since(start)

			res := FFmpegJobResult{
				JobID:    job.ID,
				Success:  err == nil,
				Duration: duration,
			}
			if err != nil {
				res.ErrorMsg = err.Error()
			}
			results <- res
		}
	}
}

// Translates the exact `cmd.Run()` binding protecting against Zombies.
func (e *OmniFFmpegBatchQueueEngine) processSingleJob(ctx context.Context, job TranscodeJob) error {
	fullArgs := append([]string{"-y", "-i", job.SourceFile}, job.Args...)
	fullArgs = append(fullArgs, job.TargetFile)

	// Using CommandContext guarantees FFmpeg is killed if the Go parent context dies
	cmd := exec.CommandContext(ctx, "ffmpeg", fullArgs...)
	
	output, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("FFMPEG_CRASH: code=%w, output=%s", err, string(output))
	}

	return nil
}
