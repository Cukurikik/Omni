// ===========================================================================
// OMNI CONNECTION POOL ENGINE (SEMESTER 3 — BATCH 38.5)
// ===========================================================================
// Absorbed From  : pgxpool + HikariCP + database/sql pool concepts
// Logic Inherited: Go / Network Layer (Connection Pool Management)
// ===========================================================================

package go_core

import (
	"context"
	"errors"
	"sync"
	"sync/atomic"
	"time"
)

// Connection represents a pooled connection.
type Connection struct {
	ID        uint64
	CreatedAt time.Time
	LastUsedAt time.Time
	InUse     bool
	Health    bool
}

// PoolConfig configures the connection pool.
type PoolConfig struct {
	MaxOpen     int
	MaxIdle     int
	MaxLifetime time.Duration
	MaxIdleTime time.Duration
	DialTimeout time.Duration
}

func DefaultPoolConfig() PoolConfig {
	return PoolConfig{
		MaxOpen:     25,
		MaxIdle:     5,
		MaxLifetime: 30 * time.Minute,
		MaxIdleTime: 5 * time.Minute,
		DialTimeout: 10 * time.Second,
	}
}

// Pool errors
var (
	ErrPoolClosed    = errors.New("pool is closed")
	ErrPoolExhausted = errors.New("pool exhausted, no connections available")
	ErrConnExpired   = errors.New("connection lifetime exceeded")
	ErrConnStale     = errors.New("connection idle too long")
)

// OmniConnectionPoolEngine manages a pool of reusable connections.
type OmniConnectionPoolEngine struct {
	config PoolConfig
	idle   []*Connection
	mu     sync.Mutex
	cond   *sync.Cond
	closed bool

	nextID        atomic.Uint64
	openCount     atomic.Int64
	inUseCount    atomic.Int64

	totalAcquired  atomic.Uint64
	totalReleased  atomic.Uint64
	totalCreated   atomic.Uint64
	totalClosed    atomic.Uint64
	totalExpired   atomic.Uint64
	totalWaits     atomic.Uint64
	totalTimeouts  atomic.Uint64
}

func NewPool(config PoolConfig) *OmniConnectionPoolEngine {
	p := &OmniConnectionPoolEngine{
		config: config,
		idle:   make([]*Connection, 0, config.MaxIdle),
	}
	p.cond = sync.NewCond(&p.mu)

	// Pre-warm idle connections
	for i := 0; i < config.MaxIdle; i++ {
		conn := p.newConnection()
		p.idle = append(p.idle, conn)
	}

	return p
}

func (p *OmniConnectionPoolEngine) newConnection() *Connection {
	id := p.nextID.Add(1)
	now := time.Now()
	p.openCount.Add(1)
	p.totalCreated.Add(1)
	return &Connection{
		ID:         id,
		CreatedAt:  now,
		LastUsedAt: now,
		InUse:      false,
		Health:     true,
	}
}

// Acquire gets a connection from the pool, waiting if necessary.
func (p *OmniConnectionPoolEngine) Acquire(ctx context.Context) (*Connection, error) {
	p.mu.Lock()
	defer p.mu.Unlock()

	if p.closed {
		return nil, ErrPoolClosed
	}

	for {
		// Try to get an idle connection
		if len(p.idle) > 0 {
			conn := p.idle[len(p.idle)-1]
			p.idle = p.idle[:len(p.idle)-1]

			// Check lifetime
			if time.Since(conn.CreatedAt) > p.config.MaxLifetime {
				p.closeConnection(conn)
				p.totalExpired.Add(1)
				continue
			}

			// Check idle time
			if time.Since(conn.LastUsedAt) > p.config.MaxIdleTime {
				p.closeConnection(conn)
				p.totalExpired.Add(1)
				continue
			}

			conn.InUse = true
			conn.LastUsedAt = time.Now()
			p.inUseCount.Add(1)
			p.totalAcquired.Add(1)
			return conn, nil
		}

		// Create new if under limit
		if p.openCount.Load() < int64(p.config.MaxOpen) {
			conn := p.newConnection()
			conn.InUse = true
			p.inUseCount.Add(1)
			p.totalAcquired.Add(1)
			return conn, nil
		}

		// Wait for a connection to be released
		p.totalWaits.Add(1)

		// Check context before waiting
		select {
		case <-ctx.Done():
			p.totalTimeouts.Add(1)
			return nil, ctx.Err()
		default:
		}

		// Wait on condition variable
		p.cond.Wait()

		if p.closed {
			return nil, ErrPoolClosed
		}
	}
}

// Release returns a connection to the pool.
func (p *OmniConnectionPoolEngine) Release(conn *Connection) {
	p.mu.Lock()
	defer p.mu.Unlock()

	conn.InUse = false
	conn.LastUsedAt = time.Now()
	p.inUseCount.Add(-1)
	p.totalReleased.Add(1)

	if p.closed {
		p.closeConnection(conn)
		return
	}

	// Check if expired
	if time.Since(conn.CreatedAt) > p.config.MaxLifetime {
		p.closeConnection(conn)
		p.totalExpired.Add(1)
		p.cond.Signal()
		return
	}

	// Return to idle pool if not full
	if len(p.idle) < p.config.MaxIdle {
		p.idle = append(p.idle, conn)
	} else {
		p.closeConnection(conn)
	}

	p.cond.Signal()
}

func (p *OmniConnectionPoolEngine) closeConnection(conn *Connection) {
	conn.Health = false
	p.openCount.Add(-1)
	p.totalClosed.Add(1)
}

// Close shuts down the pool and closes all connections.
func (p *OmniConnectionPoolEngine) Close() {
	p.mu.Lock()
	defer p.mu.Unlock()

	p.closed = true
	for _, conn := range p.idle {
		p.closeConnection(conn)
	}
	p.idle = nil
	p.cond.Broadcast()
}

// Stats returns current pool statistics.
func (p *OmniConnectionPoolEngine) Stats() map[string]int64 {
	return map[string]int64{
		"open":    p.openCount.Load(),
		"in_use":  p.inUseCount.Load(),
		"idle":    int64(len(p.idle)),
	}
}

// Diagnostics returns engine diagnostics.
func (p *OmniConnectionPoolEngine) Diagnostics() map[string]interface{} {
	return map[string]interface{}{
		"engine":          "OmniConnectionPoolEngine",
		"layer":           "Go Network",
		"max_open":        p.config.MaxOpen,
		"max_idle":        p.config.MaxIdle,
		"open_count":      p.openCount.Load(),
		"in_use_count":    p.inUseCount.Load(),
		"idle_count":      len(p.idle),
		"total_acquired":  p.totalAcquired.Load(),
		"total_released":  p.totalReleased.Load(),
		"total_created":   p.totalCreated.Load(),
		"total_closed":    p.totalClosed.Load(),
		"total_expired":   p.totalExpired.Load(),
		"total_waits":     p.totalWaits.Load(),
		"total_timeouts":  p.totalTimeouts.Load(),
		"learned_logic": []string{
			"hikaricp-connection-pool",
			"lifo-idle-connection-reuse",
			"max-lifetime-expiration",
			"max-idle-time-eviction",
			"condition-variable-wait",
			"context-timeout-acquire",
			"pre-warm-idle-connections",
			"atomic-open-count-tracking",
		},
	}
}
