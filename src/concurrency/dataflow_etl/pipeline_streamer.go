package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type PipelineTask struct {
	DataChunk []byte
	ChunkID   string
}

type PipelineStreamer struct {
	workers int
	inChan  chan PipelineTask
	outChan chan OmniResult
	wg      sync.WaitGroup
}

func NewPipelineStreamer(workers int) *PipelineStreamer {
	return &PipelineStreamer{
		workers: workers,
		inChan:  make(chan PipelineTask, 1000),
		outChan: make(chan OmniResult, 1000),
	}
}

func (s *PipelineStreamer) Start() {
	for i := 0; i < s.workers; i++ {
		s.wg.Add(1)
		go s.process(i)
	}
}

func (s *PipelineStreamer) process(id int) {
	defer s.wg.Done()
	for task := range s.inChan {
		if len(task.DataChunk) == 0 {
			s.outChan <- OmniResult{Error: fmt.Errorf("empty chunk %s", task.ChunkID)}
			continue
		}
		
		// Deterministic hash/processing
		sum := 0
		for _, b := range task.DataChunk {
			sum += int(b)
		}
		
		s.outChan <- OmniResult{Value: fmt.Sprintf("Worker %d processed %s: checksum %d", id, task.ChunkID, sum)}
	}
}

func (s *PipelineStreamer) StreamChunk(chunk []byte, id string) {
	s.inChan <- PipelineTask{DataChunk: chunk, ChunkID: id}
}

func (s *PipelineStreamer) Close() {
	close(s.inChan)
	s.wg.Wait()
	close(s.outChan)
}
