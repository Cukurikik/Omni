// moe_expert_priority_queue.go — Network / Orchestration
// Layer: Network / Interconnect — QoS Priority Queue
//
// When the MoE cluster is under heavy load (e.g. 99% VRAM util), requests back up.
// This Go module implements a strict Quality-of-Service (QoS) Priority Queue,
// ensuring that Enterprise/VIP tenants are routed to the GPU before Free Tier users.

package network_moe

import (
	"container/heap"
	"fmt"
	"sync"
	"time"
)

// An Item is something we manage in a priority queue.
type QueueItem struct {
	TenantID string
	Priority int // Higher is more urgent (e.g., Enterprise = 100, Free = 10)
	Payload  []float32
	Index    int
	Enqueued time.Time
}

// PriorityQueue implements heap.Interface and holds QueueItems.
type PriorityQueue []*QueueItem

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	// Highest priority first. If equal, FIFO based on Enqueue time.
	if pq[i].Priority == pq[j].Priority {
		return pq[i].Enqueued.Before(pq[j].Enqueued)
	}
	return pq[i].Priority > pq[j].Priority
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].Index = i
	pq[j].Index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*QueueItem)
	item.Index = n
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	old[n-1] = nil  // avoid memory leak
	item.Index = -1 // for safety
	*pq = old[0 : n-1]
	return item
}

// Thread-safe wrapper
type QoSRouter struct {
	pq PriorityQueue
	mu sync.Mutex
}

func NewQoSRouter() *QoSRouter {
	fmt.Println("[QoS Router] Initialized Enterprise Priority Queue.")
	router := &QoSRouter{
		pq: make(PriorityQueue, 0),
	}
	heap.Init(&router.pq)
	return router
}

func (r *QoSRouter) Enqueue(tenantID string, priority int, payload []float32) {
	r.mu.Lock()
	defer r.mu.Unlock()

	item := &QueueItem{
		TenantID: tenantID,
		Priority: priority,
		Payload:  payload,
		Enqueued: time.Now(),
	}
	heap.Push(&r.pq, item)
}

func (r *QoSRouter) Dequeue() *QueueItem {
	r.mu.Lock()
	defer r.mu.Unlock()

	if r.pq.Len() == 0 {
		return nil
	}
	return heap.Pop(&r.pq).(*QueueItem)
}

