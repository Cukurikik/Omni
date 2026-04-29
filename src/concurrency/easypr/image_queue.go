package easypr

import (
	"log"
)

type ImageFrame struct {
	ID        string
	Data      []byte
	Timestamp int64
}

type ProcessQueue struct {
	frames chan ImageFrame
}

func NewProcessQueue(bufferSize int) *ProcessQueue {
	return &ProcessQueue{
		frames: make(chan ImageFrame, bufferSize),
	}
}

func (q *ProcessQueue) Enqueue(frame ImageFrame) {
	q.frames <- frame
}

func (q *ProcessQueue) StartWorker() {
	go func() {
		for frame := range q.frames {
			log.Printf("Processing EasyPR Frame: %s", frame.ID)
			// Trigger C++ plate locator via FFI in reality
		}
	}()
}
