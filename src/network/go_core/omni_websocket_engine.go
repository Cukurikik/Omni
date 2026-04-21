// ===========================================================================
// OMNI WEBSOCKET ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.7)
// ===========================================================================
// Absorbed From  : gorilla/websocket + nhooyr.io/websocket + gobwas/ws
// Logic Inherited: Go / Network Layer (Room-Based WebSocket Connection Manager)
// Domain Layer   : Network (Go Core)
// ===========================================================================
//
// By studying gorilla/websocket and nhooyr.io/websocket, Mother learned
// that production WebSocket management requires:
//   1. Connection registry with thread-safe map (sync.Map)
//   2. Room-based pub/sub (broadcast to all connections in a room)
//   3. Per-connection write pump with buffered channel
//   4. Heartbeat/ping-pong with configurable intervals
//   5. Graceful shutdown with context cancellation
//
// Go's goroutine-per-connection model scales to 100K+ concurrent
// connections with minimal memory overhead.

package omni_websocket

import (
	"context"
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

// ---- Message Types ----

// MessageType identifies WebSocket frame types.
type MessageType int

const (
	TextMessage   MessageType = 1
	BinaryMessage MessageType = 2
	PingMessage   MessageType = 9
	PongMessage   MessageType = 10
	CloseMessage  MessageType = 8
)

// Message represents a WebSocket message.
type Message struct {
	Type      MessageType
	Payload   []byte
	SenderID  string
	RoomID    string
	Timestamp time.Time
}

// ---- Connection ----

// Connection represents a single WebSocket connection.
type Connection struct {
	ID          string
	UserID      string
	Rooms       map[string]bool
	SendCh      chan Message
	MetaData    map[string]string
	ConnectedAt time.Time
	LastPingAt  time.Time
	IsAlive     int32 // atomic: 1 = alive, 0 = dead
}

// NewConnection creates a managed connection.
func NewConnection(id, userID string, bufferSize int) *Connection {
	return &Connection{
		ID:          id,
		UserID:      userID,
		Rooms:       make(map[string]bool),
		SendCh:      make(chan Message, bufferSize),
		MetaData:    make(map[string]string),
		ConnectedAt: time.Now(),
		LastPingAt:  time.Now(),
		IsAlive:     1,
	}
}

// ---- Room ----

// Room holds connections subscribed to a named channel.
type Room struct {
	ID          string
	Connections sync.Map // connID → *Connection
	CreatedAt   time.Time
}

// ---- Event Handler ----

// EventHandler is called on connection lifecycle events.
type EventHandler struct {
	OnConnect    func(conn *Connection)
	OnDisconnect func(conn *Connection)
	OnMessage    func(conn *Connection, msg Message)
	OnError      func(conn *Connection, err error)
}

// ---- Configuration ----

// WSConfig defines engine parameters.
type WSConfig struct {
	MaxConnections      int
	SendBufferSize      int
	PingInterval        time.Duration
	PongTimeout         time.Duration
	MaxMessageSize      int64
	WriteTimeout        time.Duration
}

// DefaultWSConfig returns production defaults.
func DefaultWSConfig() WSConfig {
	return WSConfig{
		MaxConnections: 100000,
		SendBufferSize: 256,
		PingInterval:   30 * time.Second,
		PongTimeout:    60 * time.Second,
		MaxMessageSize: 1 << 20, // 1MB
		WriteTimeout:   10 * time.Second,
	}
}

// ---- Core Engine ----

// OmniWebSocketEngine manages WebSocket connections and rooms.
type OmniWebSocketEngine struct {
	config      WSConfig
	connections sync.Map // connID → *Connection
	rooms       sync.Map // roomID → *Room
	handler     EventHandler
	ctx         context.Context
	cancel      context.CancelFunc
	wg          sync.WaitGroup
	stats       struct {
		TotalConnections    uint64
		TotalDisconnections uint64
		TotalMessages       uint64
		TotalBroadcasts     uint64
		TotalErrors         uint64
		ActiveConnections   int64
	}
}

// NewOmniWebSocketEngine creates a new WebSocket engine.
func NewOmniWebSocketEngine(cfg WSConfig, handler EventHandler) *OmniWebSocketEngine {
	ctx, cancel := context.WithCancel(context.Background())
	return &OmniWebSocketEngine{
		config:  cfg,
		handler: handler,
		ctx:     ctx,
		cancel:  cancel,
	}
}

// ---- Connection Management ----

// Connect registers a new connection.
func (e *OmniWebSocketEngine) Connect(conn *Connection) error {
	activeCount := atomic.LoadInt64(&e.stats.ActiveConnections)
	if activeCount >= int64(e.config.MaxConnections) {
		return fmt.Errorf("max connections (%d) reached", e.config.MaxConnections)
	}

	e.connections.Store(conn.ID, conn)
	atomic.AddUint64(&e.stats.TotalConnections, 1)
	atomic.AddInt64(&e.stats.ActiveConnections, 1)

	if e.handler.OnConnect != nil {
		e.handler.OnConnect(conn)
	}

	return nil
}

// Disconnect removes a connection & cleans up all room memberships.
func (e *OmniWebSocketEngine) Disconnect(connID string) {
	val, ok := e.connections.LoadAndDelete(connID)
	if !ok {
		return
	}

	conn := val.(*Connection)
	atomic.StoreInt32(&conn.IsAlive, 0)
	close(conn.SendCh)

	// Remove from all rooms
	for roomID := range conn.Rooms {
		e.LeaveRoom(connID, roomID)
	}

	atomic.AddUint64(&e.stats.TotalDisconnections, 1)
	atomic.AddInt64(&e.stats.ActiveConnections, -1)

	if e.handler.OnDisconnect != nil {
		e.handler.OnDisconnect(conn)
	}
}

// GetConnection retrieves a connection by ID.
func (e *OmniWebSocketEngine) GetConnection(connID string) (*Connection, bool) {
	val, ok := e.connections.Load(connID)
	if !ok {
		return nil, false
	}
	return val.(*Connection), true
}

// ---- Room Management ----

// JoinRoom adds a connection to a room, creating the room if needed.
func (e *OmniWebSocketEngine) JoinRoom(connID, roomID string) error {
	val, ok := e.connections.Load(connID)
	if !ok {
		return fmt.Errorf("connection %s not found", connID)
	}
	conn := val.(*Connection)

	// Get or create room
	roomVal, _ := e.rooms.LoadOrStore(roomID, &Room{
		ID:        roomID,
		CreatedAt: time.Now(),
	})
	room := roomVal.(*Room)

	room.Connections.Store(connID, conn)
	conn.Rooms[roomID] = true

	return nil
}

// LeaveRoom removes a connection from a room.
func (e *OmniWebSocketEngine) LeaveRoom(connID, roomID string) {
	val, ok := e.rooms.Load(roomID)
	if !ok {
		return
	}
	room := val.(*Room)
	room.Connections.Delete(connID)

	// Remove room from connection's room set
	connVal, ok := e.connections.Load(connID)
	if ok {
		conn := connVal.(*Connection)
		delete(conn.Rooms, roomID)
	}

	// Clean up empty rooms
	isEmpty := true
	room.Connections.Range(func(_, _ interface{}) bool {
		isEmpty = false
		return false
	})
	if isEmpty {
		e.rooms.Delete(roomID)
	}
}

// ---- Messaging ----

// Send sends a message to a specific connection.
func (e *OmniWebSocketEngine) Send(connID string, msg Message) error {
	val, ok := e.connections.Load(connID)
	if !ok {
		return fmt.Errorf("connection %s not found", connID)
	}
	conn := val.(*Connection)

	if atomic.LoadInt32(&conn.IsAlive) == 0 {
		return fmt.Errorf("connection %s is dead", connID)
	}

	select {
	case conn.SendCh <- msg:
		atomic.AddUint64(&e.stats.TotalMessages, 1)
		return nil
	default:
		atomic.AddUint64(&e.stats.TotalErrors, 1)
		return fmt.Errorf("send buffer full for connection %s", connID)
	}
}

// Broadcast sends a message to all connections in a room.
func (e *OmniWebSocketEngine) Broadcast(roomID string, msg Message) int {
	val, ok := e.rooms.Load(roomID)
	if !ok {
		return 0
	}
	room := val.(*Room)

	msg.RoomID = roomID
	msg.Timestamp = time.Now()
	sent := 0

	room.Connections.Range(func(key, value interface{}) bool {
		conn := value.(*Connection)
		if atomic.LoadInt32(&conn.IsAlive) == 1 {
			select {
			case conn.SendCh <- msg:
				sent++
			default:
				// Buffer full — skip this connection
				atomic.AddUint64(&e.stats.TotalErrors, 1)
			}
		}
		return true
	})

	atomic.AddUint64(&e.stats.TotalBroadcasts, 1)
	atomic.AddUint64(&e.stats.TotalMessages, uint64(sent))

	return sent
}

// BroadcastAll sends a message to ALL connected clients.
func (e *OmniWebSocketEngine) BroadcastAll(msg Message) int {
	msg.Timestamp = time.Now()
	sent := 0

	e.connections.Range(func(key, value interface{}) bool {
		conn := value.(*Connection)
		if atomic.LoadInt32(&conn.IsAlive) == 1 {
			select {
			case conn.SendCh <- msg:
				sent++
			default:
				atomic.AddUint64(&e.stats.TotalErrors, 1)
			}
		}
		return true
	})

	atomic.AddUint64(&e.stats.TotalMessages, uint64(sent))
	return sent
}

// HandleIncoming processes an incoming message from a connection.
func (e *OmniWebSocketEngine) HandleIncoming(connID string, msg Message) {
	val, ok := e.connections.Load(connID)
	if !ok {
		return
	}
	conn := val.(*Connection)
	msg.SenderID = connID
	msg.Timestamp = time.Now()

	if e.handler.OnMessage != nil {
		e.handler.OnMessage(conn, msg)
	}
}

// ---- Heartbeat ----

// StartHeartbeat launches a periodic ping loop for all connections.
func (e *OmniWebSocketEngine) StartHeartbeat() {
	e.wg.Add(1)
	go func() {
		defer e.wg.Done()
		ticker := time.NewTicker(e.config.PingInterval)
		defer ticker.Stop()

		for {
			select {
			case <-e.ctx.Done():
				return
			case <-ticker.C:
				e.runHeartbeat()
			}
		}
	}()
}

func (e *OmniWebSocketEngine) runHeartbeat() {
	now := time.Now()

	e.connections.Range(func(key, value interface{}) bool {
		conn := value.(*Connection)

		// Check pong timeout
		if now.Sub(conn.LastPingAt) > e.config.PongTimeout {
			// Connection timed out — disconnect
			connID := key.(string)
			e.Disconnect(connID)
			return true
		}

		// Send ping
		pingMsg := Message{
			Type:      PingMessage,
			Timestamp: now,
		}
		select {
		case conn.SendCh <- pingMsg:
			conn.LastPingAt = now
		default:
			// Buffer full
		}

		return true
	})
}

// HandlePong updates the last ping timestamp for a connection.
func (e *OmniWebSocketEngine) HandlePong(connID string) {
	val, ok := e.connections.Load(connID)
	if !ok {
		return
	}
	conn := val.(*Connection)
	conn.LastPingAt = time.Now()
}

// ---- Query ----

// GetRoomConnections returns all connection IDs in a room.
func (e *OmniWebSocketEngine) GetRoomConnections(roomID string) []string {
	val, ok := e.rooms.Load(roomID)
	if !ok {
		return nil
	}
	room := val.(*Room)

	ids := make([]string, 0)
	room.Connections.Range(func(key, _ interface{}) bool {
		ids = append(ids, key.(string))
		return true
	})
	return ids
}

// GetRoomCount returns the number of active rooms.
func (e *OmniWebSocketEngine) GetRoomCount() int {
	count := 0
	e.rooms.Range(func(_, _ interface{}) bool {
		count++
		return true
	})
	return count
}

// ---- Lifecycle ----

// Shutdown gracefully disconnects all clients and stops heartbeat.
func (e *OmniWebSocketEngine) Shutdown() {
	e.cancel()

	// Disconnect all
	e.connections.Range(func(key, _ interface{}) bool {
		e.Disconnect(key.(string))
		return true
	})

	e.wg.Wait()
}

// ---- Diagnostics ----

func (e *OmniWebSocketEngine) Diagnostics() map[string]interface{} {
	return map[string]interface{}{
		"engine":               "OmniWebSocketEngine",
		"layer":                "Go Network",
		"active_connections":   atomic.LoadInt64(&e.stats.ActiveConnections),
		"rooms":                e.GetRoomCount(),
		"max_connections":      e.config.MaxConnections,
		"send_buffer_size":     e.config.SendBufferSize,
		"ping_interval":        e.config.PingInterval.String(),
		"pong_timeout":         e.config.PongTimeout.String(),
		"total_connections":    atomic.LoadUint64(&e.stats.TotalConnections),
		"total_disconnections": atomic.LoadUint64(&e.stats.TotalDisconnections),
		"total_messages":       atomic.LoadUint64(&e.stats.TotalMessages),
		"total_broadcasts":     atomic.LoadUint64(&e.stats.TotalBroadcasts),
		"total_errors":         atomic.LoadUint64(&e.stats.TotalErrors),
		"learned_logic": []string{
			"sync-map-concurrent-registry",
			"room-based-pub-sub-broadcast",
			"buffered-channel-write-pump",
			"ping-pong-heartbeat-timeout",
			"context-cancellation-shutdown",
			"atomic-alive-flag-guard",
			"goroutine-per-tick-heartbeat",
		},
	}
}
