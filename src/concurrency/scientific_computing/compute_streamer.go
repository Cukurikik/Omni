package concurrency

import (
	"fmt"
	"math"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type ComputeJob struct {
	JobID    string
	DataSize float64
}

type ComputeStreamer struct {
	workers int
	inChan  chan ComputeJob
	outChan chan OmniResult
	wg      sync.WaitGroup
}

func NewComputeStreamer(workers int) *ComputeStreamer {
	return &ComputeStreamer{
		workers: workers,
		inChan:  make(chan ComputeJob, 500),
		outChan: make(chan OmniResult, 500),
	}
}

func (s *ComputeStreamer) Start() {
	for i := 0; i < s.workers; i++ {
		s.wg.Add(1)
		go s.process(i)
	}
}

func (s *ComputeStreamer) process(id int) {
	defer s.wg.Done()
	for job := range s.inChan {
		if job.DataSize <= 0 {
			s.outChan <- OmniResult{Error: fmt.Errorf("invalid data size for job %s", job.JobID)}
			continue
		}
		
		// Deterministic computation (e.g. FFT algorithmic complexity N log N)
		complexity := job.DataSize * math.Log2(job.DataSize)
		s.outChan <- OmniResult{Value: fmt.Sprintf("Worker %d | Job %s | Complexity: %.2f O(N log N)", id, job.JobID, complexity)}
	}
}

func (s *ComputeStreamer) SubmitJob(job ComputeJob) {
	s.inChan <- job
}

func (s *ComputeStreamer) Close() {
	close(s.inChan)
	s.wg.Wait()
	close(s.outChan)
}
