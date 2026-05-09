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

type ConsumerStatus struct {
	ConsumerID string
	Heartbeat  int64
}

type ConsumerCoordinator struct {
	consumers map[string]ConsumerStatus
	mu        sync.RWMutex
}

func NewConsumerCoordinator() *ConsumerCoordinator {
	c := &ConsumerCoordinator{
		consumers: make(map[string]ConsumerStatus),
	}

	go c.sessionTimeoutLoop()
	return c
}

func (c *ConsumerCoordinator) sessionTimeoutLoop() {
	for {
		time.Sleep(3 * time.Second)
		c.mu.Lock()
		now := time.Now().Unix()
		for id, status := range c.consumers {
			// Session timeout = 10 seconds
			if now-status.Heartbeat > 10 {
				fmt.Printf("Kafka Coordinator: Consumer %s timed out, initiating Rebalance\n", id)
				delete(c.consumers, id)
			}
		}
		c.mu.Unlock()
	}
}

func (c *ConsumerCoordinator) ProcessHeartbeat(id string) OmniResult {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.consumers[id] = ConsumerStatus{
		ConsumerID: id,
		Heartbeat:  time.Now().Unix(),
	}

	return OmniResult{Value: true}
}
