package concurrency

import (
	"fmt"
	"math"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type SensorData struct {
	Timestamp float64
	LidarPts  int
}

type SensorStreamer struct {
	workers int
	inChan  chan SensorData
	outChan chan OmniResult
	wg      sync.WaitGroup
}

func NewSensorStreamer(workers int) *SensorStreamer {
	return &SensorStreamer{
		workers: workers,
		inChan:  make(chan SensorData, 2000),
		outChan: make(chan OmniResult, 2000),
	}
}

func (s *SensorStreamer) Start() {
	for i := 0; i < s.workers; i++ {
		s.wg.Add(1)
		go s.process(i)
	}
}

func (s *SensorStreamer) process(id int) {
	defer s.wg.Done()
	for data := range s.inChan {
		if data.LidarPts < 0 {
			s.outChan <- OmniResult{Error: fmt.Errorf("invalid lidar points")}
			continue
		}
		
		// Deterministic lidar point cloud processing math
		intensity := math.Mod(float64(data.LidarPts), 100.0) / 100.0
		s.outChan <- OmniResult{Value: fmt.Sprintf("Worker %d T=%.2f: Int=%.2f", id, data.Timestamp, intensity)}
	}
}

func (s *SensorStreamer) StreamData(data SensorData) {
	s.inChan <- data
}

func (s *SensorStreamer) Close() {
	close(s.inChan)
	s.wg.Wait()
	close(s.outChan)
}
