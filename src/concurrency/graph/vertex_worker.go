package graph

import (
	"sync"
)

type Result[T any] struct {
	Value T
	Err   error
}

func Ok[T any](v T) Result[T]      { return Result[T]{Value: v, Err: nil} }
func Err[T any](e error) Result[T] { return Result[T]{Value: *new(T), Err: e} }

type Message struct {
	DestVertexID int64
	Payload      float64
}

type Vertex struct {
	ID    int64
	Value float64
	Edges []int64
}

type WorkerPool struct {
	mu       sync.Mutex
	vertices map[int64]*Vertex
	inboxes  map[int64][]Message
	outbox   []Message
}

func NewWorkerPool() *WorkerPool {
	return &WorkerPool{
		vertices: make(map[int64]*Vertex),
		inboxes:  make(map[int64][]Message),
		outbox:   make([]Message, 0),
	}
}

func (w *WorkerPool) AddVertex(v *Vertex) {
	w.mu.Lock()
	defer w.mu.Unlock()
	w.vertices[v.ID] = v
	w.inboxes[v.ID] = make([]Message, 0)
}

// Simulates a single superstep in the Pregel Bulk Synchronous Parallel (BSP) model
func (w *WorkerPool) Superstep(computeFunc func(*Vertex, []Message) Result[[]Message]) Result[int] {
	w.mu.Lock()
	defer w.mu.Unlock()

	newOutbox := make([]Message, 0)
	messagesProcessed := 0

	for id, vertex := range w.vertices {
		messages := w.inboxes[id]

		res := computeFunc(vertex, messages)
		if res.Err != nil {
			return Err[int](res.Err)
		}

		newOutbox = append(newOutbox, res.Value...)
		messagesProcessed += len(messages)
		w.inboxes[id] = w.inboxes[id][:0] // clear inbox
	}

	// Message routing phase
	for _, msg := range newOutbox {
		if _, exists := w.inboxes[msg.DestVertexID]; exists {
			w.inboxes[msg.DestVertexID] = append(w.inboxes[msg.DestVertexID], msg)
		}
	}

	w.outbox = newOutbox
	return Ok(messagesProcessed)
}
