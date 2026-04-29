package distributed_compute

import (
	"time"
	"errors"
	"sync"
	"sync/atomic"
)

// OMNI Distributed Compute Engine — Concurrency Layer
// Absorbing ChimeraPy/Engine distributed multimodal data processing concepts.

type WorkerStatus int32

const (
	WorkerIdle    WorkerStatus = 0
	WorkerBusy    WorkerStatus = 1
	WorkerFailed  WorkerStatus = 2
)

type ComputeWorker struct {
	ID       string
	Status   int32 // atomic
	TasksDone int64 // atomic
}

type TaskPayload struct {
	TaskID   string
	DataRef  string
	Priority int
}

type OmniDistributedCompute struct {
	mu       sync.RWMutex
	workers  []*ComputeWorker
	taskQueue chan TaskPayload
	dispatched int64
}

func NewOmniDistributedCompute(workerCount, queueSize int) (*OmniDistributedCompute, error) {
	if workerCount <= 0 || queueSize <= 0 {
		return nil, errors.New("DistComputeError: Invalid parameters")
	}

	dc := &OmniDistributedCompute{
		workers:   make([]*ComputeWorker, workerCount),
		taskQueue: make(chan TaskPayload, queueSize),
	}

	for i := 0; i < workerCount; i++ {
		dc.workers[i] = &ComputeWorker{
			ID:     "worker-" + time.Now().Format("150405") + "-" + string(rune('A'+i)),
			Status: int32(WorkerIdle),
		}
	}

	return dc, nil
}

func (dc *OmniDistributedCompute) SubmitTask(task TaskPayload) error {
	if task.TaskID == "" {
		return errors.New("DistComputeError: TaskID required")
	}

	select {
	case dc.taskQueue <- task:
		atomic.AddInt64(&dc.dispatched, 1)
		return nil
	default:
		return errors.New("DistComputeError: Queue full, backpressure applied")
	}
}

func (dc *OmniDistributedCompute) AssignNextTask() (*ComputeWorker, *TaskPayload, error) {
	dc.mu.RLock()
	defer dc.mu.RUnlock()

	// Find an idle worker
	var idleWorker *ComputeWorker
	for _, w := range dc.workers {
		if atomic.LoadInt32(&w.Status) == int32(WorkerIdle) {
			idleWorker = w
			break
		}
	}

	if idleWorker == nil {
		return nil, nil, errors.New("DistComputeError: No idle workers")
	}

	select {
	case task := <-dc.taskQueue:
		atomic.StoreInt32(&idleWorker.Status, int32(WorkerBusy))
		atomic.AddInt64(&idleWorker.TasksDone, 1)
		return idleWorker, &task, nil
	default:
		return nil, nil, errors.New("DistComputeError: Task queue empty")
	}
}

func (dc *OmniDistributedCompute) CompleteWorker(workerID string) {
	dc.mu.RLock()
	defer dc.mu.RUnlock()
	for _, w := range dc.workers {
		if w.ID == workerID {
			atomic.StoreInt32(&w.Status, int32(WorkerIdle))
			return
		}
	}
}

func (dc *OmniDistributedCompute) Diagnostics() map[string]interface{} {
	dc.mu.RLock()
	defer dc.mu.RUnlock()
	busyCount := 0
	for _, w := range dc.workers {
		if atomic.LoadInt32(&w.Status) == int32(WorkerBusy) {
			busyCount++
		}
	}
	return map[string]interface{}{
		"engine":     "OmniDistributedCompute",
		"workers":    len(dc.workers),
		"busy":       busyCount,
		"dispatched": atomic.LoadInt64(&dc.dispatched),
		"queue_len":  len(dc.taskQueue),
		"status":     "Operational",
	}
}
