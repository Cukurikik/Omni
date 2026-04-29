// OMNI RAY WORKER POOL
// Domain: Distributed Ray Concurrency
// Origin: ray-project/ray
package concurrency

import "errors"

type WorkerPool struct {
    workers chan struct{}
}

func NewWorkerPool(size int) *WorkerPool {
    return &WorkerPool{
        workers: make(chan struct{}, size),
    }
}

func (w *WorkerPool) Acquire() error {
    select {
    case w.workers <- struct{}{}:
        return nil
    default:
        return errors.New("worker pool exhausted")
    }
}\n