package snorkel

import (
	"context"
	"log"
)

type DataPoint struct {
	ID   string
	Text string
}

type LabelTask struct {
	Data   DataPoint
	Result chan int
}

type LabelQueue struct {
	tasks chan LabelTask
}

func NewLabelQueue(buffer int) *LabelQueue {
	return &LabelQueue{
		tasks: make(chan LabelTask, buffer),
	}
}

func (q *LabelQueue) Dispatch(ctx context.Context, workers int, applyLF func(string) int) {
	for i := 0; i < workers; i++ {
		go func() {
			for {
				select {
				case <-ctx.Done():
					return
				case task := <-q.tasks:
					// Apply Snorkel weak supervision Labeling Function
					res := applyLF(task.Data.Text)
					task.Result <- res
				}
			}
		}()
	}
	log.Printf("Snorkel LabelQueue started with %d workers", workers)
}
