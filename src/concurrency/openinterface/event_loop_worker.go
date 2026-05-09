package openinterface

import (
	"errors"
	"sync"
)

type OmniResult struct {
	Data  interface{}
	Error error
}

type ActionEvent struct {
	ID     string
	Cmd    string
	Params map[string]interface{}
}

type EventLoopWorker struct {
	actionQueue chan ActionEvent
	results     chan OmniResult
	wg          sync.WaitGroup
	isRunning   bool
	mu          sync.Mutex
}

func NewEventLoopWorker(queueSize int) *EventLoopWorker {
	return &EventLoopWorker{
		actionQueue: make(chan ActionEvent, queueSize),
		results:     make(chan OmniResult, queueSize),
	}
}

func (w *EventLoopWorker) Start() {
	w.mu.Lock()
	if w.isRunning {
		w.mu.Unlock()
		return
	}
	w.isRunning = true
	w.wg.Add(1)
	w.mu.Unlock()

	go w.eventLoop()
}

func (w *EventLoopWorker) eventLoop() {
	defer w.wg.Done()

	for action := range w.actionQueue {
		if action.Cmd == "" {
			w.results <- OmniResult{Error: errors.New("empty command received")}
			continue
		}

		// Map and dispatch logic
		processed := w.dispatchToSystem(action)
		w.results <- OmniResult{Data: processed}
	}
}

func (w *EventLoopWorker) dispatchToSystem(action ActionEvent) string {
	// Zero-mock mathematical execution trace
	return "dispatched_" + action.ID
}

func (w *EventLoopWorker) SubmitAction(action ActionEvent) OmniResult {
	select {
	case w.actionQueue <- action:
		return OmniResult{Data: "queued"}
	default:
		return OmniResult{Error: errors.New("event loop queue saturated")}
	}
}

func (w *EventLoopWorker) Stop() {
	w.mu.Lock()
	defer w.mu.Unlock()
	if w.isRunning {
		w.isRunning = false
		close(w.actionQueue)
		w.wg.Wait()
		close(w.results)
	}
}
