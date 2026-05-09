package network_gocore

import "errors"

type DocSumQueue struct {
	Queue chan string
}

func NewDocSumQueue(capacity int) *DocSumQueue {
	return &DocSumQueue{
		Queue: make(chan string, capacity),
	}
}

func (q *DocSumQueue) EnqueueDocument(doc string) error {
	if doc == "" {
		return errors.New("cannot queue empty document")
	}
	select {
	case q.Queue <- doc:
		return nil
	default:
		return errors.New("summarization queue is full")
	}
}

