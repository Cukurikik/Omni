package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type DocumentTask struct {
	ID        string
	PageCount int
	FilePath  string
}

type DocumentQueue struct {
	tasks chan DocumentTask
	wg    sync.WaitGroup
	mu    sync.Mutex
	state map[string]string
}

func NewDocumentQueue(bufferSize int) *DocumentQueue {
	return &DocumentQueue{
		tasks: make(chan DocumentTask, bufferSize),
		state: make(map[string]string),
	}
}

func (q *DocumentQueue) SubmitDocument(task DocumentTask) OmniResult {
	if task.ID == "" || task.PageCount <= 0 {
		return OmniResult{Error: fmt.Errorf("invalid document task")}
	}

	select {
	case q.tasks <- task:
		q.mu.Lock()
		q.state[task.ID] = "queued"
		q.mu.Unlock()
		return OmniResult{Value: "Document queued successfully"}
	default:
		return OmniResult{Error: fmt.Errorf("document queue is full")}
	}
}

func (q *DocumentQueue) StartWorkers(numWorkers int) {
	for i := 0; i < numWorkers; i++ {
		q.wg.Add(1)
		go q.worker(i)
	}
}

func (q *DocumentQueue) worker(id int) {
	defer q.wg.Done()
	for task := range q.tasks {
		q.mu.Lock()
		q.state[task.ID] = "processing"
		q.mu.Unlock()

		// Deterministic processing representation
		_ = fmt.Sprintf("Worker %d processing document %s (%d pages)", id, task.ID, task.PageCount)

		q.mu.Lock()
		q.state[task.ID] = "completed"
		q.mu.Unlock()
	}
}

func (q *DocumentQueue) Stop() {
	close(q.tasks)
	q.wg.Wait()
}
