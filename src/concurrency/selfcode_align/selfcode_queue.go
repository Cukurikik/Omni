package selfcode

import (
	"errors"
	"sync"
)

// OmniResult Monadic Implementation
type OmniResult[T any] struct {
	Payload T
	Err     error
	IsOk    bool
}

func Ok[T any](payload T) OmniResult[T] {
	return OmniResult[T]{Payload: payload, IsOk: true}
}

func Err[T any](msg string) OmniResult[T] {
	return OmniResult[T]{Err: errors.New(msg), IsOk: false}
}

type DiffTask struct {
	ASTIdA string
	ASTIdB string
}

// Bounded Concurrent Queue for AST Diff tasks
type DiffQueue struct {
	tasks    chan DiffTask
	capacity int
	mu       sync.Mutex
	closed   bool
}

func NewDiffQueue(capacity int) *DiffQueue {
	return &DiffQueue{
		tasks:    make(chan DiffTask, capacity),
		capacity: capacity,
	}
}

func (q *DiffQueue) Enqueue(task DiffTask) OmniResult[bool] {
	q.mu.Lock()
	defer q.mu.Unlock()

	if q.closed {
		return Err[bool]("OMNI_QUEUE_ERR: Queue is closed.")
	}

	select {
	case q.tasks <- task:
		return Ok(true)
	default:
		return Err[bool]("OMNI_LIMIT: Queue capacity reached. Dropping task.")
	}
}

func (q *DiffQueue) Dequeue() OmniResult[DiffTask] {
	select {
	case task, ok := <-q.tasks:
		if !ok {
			return Err[DiffTask]("OMNI_QUEUE_ERR: Queue is closed and empty.")
		}
		return Ok(task)
	default:
		return Err[DiffTask]("OMNI_QUEUE_EMPTY: No tasks available.")
	}
}

func (q *DiffQueue) Close() {
	q.mu.Lock()
	defer q.mu.Unlock()
	if !q.closed {
		q.closed = true
		close(q.tasks)
	}
}
