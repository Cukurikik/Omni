package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type RepoTask struct {
	RepoURL string
	Files   int
}

type RepoIndexer struct {
	workers int
	tasks   chan RepoTask
	results chan OmniResult
	wg      sync.WaitGroup
}

func NewRepoIndexer(workers int) *RepoIndexer {
	return &RepoIndexer{
		workers: workers,
		tasks:   make(chan RepoTask, 100),
		results: make(chan OmniResult, 100),
	}
}

func (r *RepoIndexer) Start() {
	for i := 0; i < r.workers; i++ {
		r.wg.Add(1)
		go r.worker(i)
	}
}

func (r *RepoIndexer) worker(id int) {
	defer r.wg.Done()
	for task := range r.tasks {
		if task.Files <= 0 {
			r.results <- OmniResult{Error: fmt.Errorf("invalid file count for %s", task.RepoURL)}
			continue
		}
		
		// Deterministic index calculation
		indexTime := float64(task.Files) * 0.05
		r.results <- OmniResult{Value: fmt.Sprintf("Worker %d indexed %s: %.2f ms", id, task.RepoURL, indexTime)}
	}
}

func (r *RepoIndexer) IndexRepo(task RepoTask) {
	r.tasks <- task
}

func (r *RepoIndexer) Close() {
	close(r.tasks)
	r.wg.Wait()
	close(r.results)
}
