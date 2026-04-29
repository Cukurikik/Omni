package volcano

import (
	"container/heap"
	"sync"
)

type Job struct {
	ID       string
	Priority int
	MemoryMB int
	CPUCores int
}

type JobQueue []*Job

func (pq JobQueue) Len() int { return len(pq) }
func (pq JobQueue) Less(i, j int) bool {
	// Higher priority jobs pop first
	return pq[i].Priority > pq[j].Priority
}
func (pq JobQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}
func (pq *JobQueue) Push(x interface{}) {
	item := x.(*Job)
	*pq = append(*pq, item)
}
func (pq *JobQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

type VolcanoQueue struct {
	mu sync.Mutex
	pq JobQueue
}

func NewVolcanoQueue() *VolcanoQueue {
	vq := &VolcanoQueue{pq: make(JobQueue, 0)}
	heap.Init(&vq.pq)
	return vq
}

func (vq *VolcanoQueue) Enqueue(job *Job) {
	vq.mu.Lock()
	defer vq.mu.Unlock()
	heap.Push(&vq.pq, job)
}

func (vq *VolcanoQueue) Dequeue() *Job {
	vq.mu.Lock()
	defer vq.mu.Unlock()
	if vq.pq.Len() == 0 {
		return nil
	}
	return heap.Pop(&vq.pq).(*Job)
}
