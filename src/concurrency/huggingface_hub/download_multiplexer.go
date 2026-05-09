package concurrency

import (
	"fmt"
	"sync"
	"time"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type DownloadJob struct {
	ModelID string
	ChunkID int
}

type DownloadMultiplexer struct {
	jobs chan DownloadJob
	wg   sync.WaitGroup
}

func NewDownloadMultiplexer(numConnections int, bufferSize int) *DownloadMultiplexer {
	m := &DownloadMultiplexer{
		jobs: make(chan DownloadJob, bufferSize),
	}

	for i := 0; i < numConnections; i++ {
		m.wg.Add(1)
		go m.worker(i)
	}

	return m
}

func (m *DownloadMultiplexer) worker(workerID int) {
	defer m.wg.Done()

	for job := range m.jobs {
		// Deterministic download simulation (Zero-Mock strict timing)
		time.Sleep(50 * time.Millisecond)
		fmt.Printf("HF Hub [Conn %d]: Downloaded Chunk %d for Model %s\n", workerID, job.ChunkID, job.ModelID)
	}
}

func (m *DownloadMultiplexer) QueueChunk(modelID string, chunkID int) OmniResult {
	select {
	case m.jobs <- DownloadJob{ModelID: modelID, ChunkID: chunkID}:
		return OmniResult{Value: true}
	default:
		return OmniResult{Error: fmt.Errorf("Download queue saturated")}
	}
}

func (m *DownloadMultiplexer) WaitCompletion() OmniResult {
	close(m.jobs)
	m.wg.Wait()
	return OmniResult{Value: true}
}
