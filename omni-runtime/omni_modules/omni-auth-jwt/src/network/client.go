package omni_auth_jwt

import (
	"context"
	"sync"
	"time"
	"fmt"
)

type ConnectionPool struct {
	mu          sync.RWMutex
	conns       []*Conn
	available   chan *Conn
	maxSize     int
	endpoint    string
	timeout     time.Duration
	created     int
	totalAcq    int64
	totalRel    int64
}

type Conn struct {
	ID       int
	Alive    bool
	Endpoint string
	LastUsed time.Time
}

func NewConnectionPool(endpoint string, maxSize int, timeout time.Duration) *ConnectionPool {
	pool := &ConnectionPool{
		available: make(chan *Conn, maxSize),
		maxSize:   maxSize,
		endpoint:  endpoint,
		timeout:   timeout,
	}
	for i := 0; i < maxSize; i++ {
		c := &Conn{ID: i, Alive: true, Endpoint: endpoint, LastUsed: time.Now()}
		pool.conns = append(pool.conns, c)
		pool.available <- c
		pool.created++
	}
	return pool
}

func (p *ConnectionPool) Acquire(ctx context.Context) (*Conn, error) {
	select {
	case c := <-p.available:
		p.mu.Lock(); p.totalAcq++; p.mu.Unlock()
		c.LastUsed = time.Now()
		return c, nil
	case <-ctx.Done():
		return nil, fmt.Errorf("omni-auth-jwt: pool acquire timeout")
	}
}

func (p *ConnectionPool) Release(c *Conn) {
	p.mu.Lock(); p.totalRel++; p.mu.Unlock()
	p.available <- c
}

func (p *ConnectionPool) Stats() (int64, int64, int) {
	p.mu.RLock(); defer p.mu.RUnlock()
	return p.totalAcq, p.totalRel, len(p.available)
}

func (p *ConnectionPool) Drain() { close(p.available) }