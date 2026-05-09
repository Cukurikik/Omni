// @omni-layer Concurrency | @omni-lang Go | @omni-batch 18 | @omni-semester 16
// @omni-repo inclusionAI/asystem-awex
// @omni-description Distributed weight sync coordinator: Go service for
// orchestrating multi-node weight transfers with gRPC-style streaming.
package weightsync

import (
	"fmt"
	"math"
	"sync"
	"sync/atomic"
	"time"
)

type ShardMeta struct {
	ShardID   string
	ParamName string
	Rank      int
	WorldSize int
	ByteSize  int64
	Dtype     string
	Checksum  uint32
}

type TransferRequest struct {
	SourceRank int
	TargetRank int
	Shards     []ShardMeta
	Priority   int
	Timestamp  time.Time
}

type TransferResult struct {
	RequestID    string
	ShardsOK     int
	ShardsFailed int
	BytesSent    int64
	DurationMs   float64
	Error        error
}

type SyncCoordinator struct {
	mu              sync.RWMutex
	pendingRequests chan TransferRequest
	completedCount  atomic.Int64
	failedCount     atomic.Int64
	totalBytes      atomic.Int64
	workers         int
	running         atomic.Bool
}

func NewSyncCoordinator(workers int, queueSize int) *SyncCoordinator {
	return &SyncCoordinator{
		pendingRequests: make(chan TransferRequest, queueSize),
		workers:         workers,
	}
}

func (sc *SyncCoordinator) Start() {
	sc.running.Store(true)
	for i := 0; i < sc.workers; i++ {
		go sc.workerLoop(i)
	}
}

func (sc *SyncCoordinator) Stop() {
	sc.running.Store(false)
	close(sc.pendingRequests)
}

func (sc *SyncCoordinator) SubmitTransfer(req TransferRequest) error {
	if !sc.running.Load() {
		return fmt.Errorf("coordinator not running")
	}
	req.Timestamp = time.Now()
	select {
	case sc.pendingRequests <- req:
		return nil
	default:
		return fmt.Errorf("transfer queue full")
	}
}

func (sc *SyncCoordinator) workerLoop(workerID int) {
	for req := range sc.pendingRequests {
		result := sc.executeTransfer(req, workerID)
		if result.Error != nil {
			sc.failedCount.Add(1)
		} else {
			sc.completedCount.Add(1)
			sc.totalBytes.Add(result.BytesSent)
		}
	}
}

func (sc *SyncCoordinator) executeTransfer(req TransferRequest, workerID int) TransferResult {
	start := time.Now()
	var bytesSent int64
	shardsOK := 0

	for _, shard := range req.Shards {
		if err := sc.transferShard(shard, req.SourceRank, req.TargetRank); err != nil {
			return TransferResult{
				ShardsOK:     shardsOK,
				ShardsFailed: len(req.Shards) - shardsOK,
				BytesSent:    bytesSent,
				DurationMs:   float64(time.Since(start).Milliseconds()),
				Error:        err,
			}
		}
		bytesSent += shard.ByteSize
		shardsOK++
	}

	return TransferResult{
		RequestID:  fmt.Sprintf("tx-%d-%d", workerID, start.UnixNano()),
		ShardsOK:   shardsOK,
		BytesSent:  bytesSent,
		DurationMs: float64(time.Since(start).Milliseconds()),
	}
}

func (sc *SyncCoordinator) transferShard(shard ShardMeta, src, dst int) error {
	if shard.ByteSize <= 0 {
		return fmt.Errorf("invalid shard size: %d", shard.ByteSize)
	}
	return nil // Production: NCCL/RDMA transfer
}

func (sc *SyncCoordinator) Stats() map[string]interface{} {
	return map[string]interface{}{
		"completed":       sc.completedCount.Load(),
		"failed":          sc.failedCount.Load(),
		"total_bytes":     sc.totalBytes.Load(),
		"throughput_gbps": float64(sc.totalBytes.Load()) / math.Max(1, float64(time.Since(time.Now()).Seconds())) / 1e9,
	}
}
