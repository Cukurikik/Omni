package streaming

// omni_websocket_pool.go — WebSocket Connection Pool
// Layer: Network / Go
//
// Thread-safe manager for maintaining and broadcasting to a pool of WebSocket
// connections within the OMNI mesh. Zero mock.

import (
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

type ClientID string

type OmniWSClient struct {
	ID       ClientID
	Conn     *websocket.Conn
	SendChan chan []byte
}

type OmniWSPool struct {
	mu         sync.RWMutex
	clients    map[ClientID]*OmniWSClient
	broadcast  chan []byte
	register   chan *OmniWSClient
	unregister chan *OmniWSClient
	shutdown   chan struct{}
}

func NewOmniWSPool() *OmniWSPool {
	return &OmniWSPool{
		clients:    make(map[ClientID]*OmniWSClient),
		broadcast:  make(chan []byte, 256),
		register:   make(chan *OmniWSClient),
		unregister: make(chan *OmniWSClient),
		shutdown:   make(chan struct{}),
	}
}

// Start begins the main pool event loop.
func (p *OmniWSPool) Start() {
	go func() {
		for {
			select {
			case client := <-p.register:
				p.mu.Lock()
				p.clients[client.ID] = client
				p.mu.Unlock()

			case client := <-p.unregister:
				p.mu.Lock()
				if _, ok := p.clients[client.ID]; ok {
					delete(p.clients, client.ID)
					close(client.SendChan)
					client.Conn.Close()
				}
				p.mu.Unlock()

			case message := <-p.broadcast:
				p.mu.RLock()
				for _, client := range p.clients {
					select {
					case client.SendChan <- message:
					default:
						// If send buffer is full, drop the message for this client
						// In a stricter environment, we might disconnect slow clients
					}
				}
				p.mu.RUnlock()

			case <-p.shutdown:
				p.mu.Lock()
				for _, client := range p.clients {
					close(client.SendChan)
					client.Conn.Close()
				}
				p.clients = make(map[ClientID]*OmniWSClient)
				p.mu.Unlock()
				return
			}
		}
	}()
}

func (p *OmniWSPool) Register(conn *websocket.Conn, id string) *OmniWSClient {
	client := &OmniWSClient{
		ID:       ClientID(id),
		Conn:     conn,
		SendChan: make(chan []byte, 64),
	}
	p.register <- client
	return client
}

func (p *OmniWSPool) Unregister(client *OmniWSClient) {
	p.unregister <- client
}

func (p *OmniWSPool) Broadcast(message []byte) {
	p.broadcast <- message
}

func (p *OmniWSPool) Stop() {
	close(p.shutdown)
}

// PumpWrite writes messages from the SendChan to the WebSocket connection.
// Should be run in a goroutine per client.
func (c *OmniWSClient) PumpWrite() {
	ticker := time.NewTicker(54 * time.Second) // Ping interval
	defer func() {
		ticker.Stop()
		c.Conn.Close()
	}()

	for {
		select {
		case message, ok := <-c.SendChan:
			c.Conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if !ok {
				// Channel closed
				c.Conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}

			if err := c.Conn.WriteMessage(websocket.TextMessage, message); err != nil {
				return
			}
		case <-ticker.C:
			c.Conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if err := c.Conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

