// omni_websocket_stream.go — WebSocket Streaming for Real-Time Inference
// Inspired by: SoundStorm real-time audio streaming + OMNI inference
// Layer: Network / Go
//
// WebSocket server for streaming inference results to clients
// with bidirectional message framing, heartbeat, and backpressure.

package streaming

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"sync/atomic"
	"time"

	"golang.org/x/net/websocket"
)

type MessageType string

const (
	MsgInferenceRequest MessageType = "inference_request"
	MsgInferenceResult  MessageType = "inference_result"
	MsgStreamStart      MessageType = "stream_start"
	MsgStreamChunk      MessageType = "stream_chunk"
	MsgStreamEnd        MessageType = "stream_end"
	MsgHeartbeat        MessageType = "heartbeat"
	MsgError            MessageType = "error"
)

type WSMessage struct {
	Type      MessageType     `json:"type"`
	ID        string          `json:"id"`
	Payload   json.RawMessage `json:"payload,omitempty"`
	Timestamp int64           `json:"timestamp"`
	Sequence  uint64          `json:"sequence,omitempty"`
}

type StreamChunk struct {
	ChunkIndex int       `json:"chunk_index"`
	Data       []float32 `json:"data"`
	IsLast     bool      `json:"is_last"`
	LatencyMs  float64   `json:"latency_ms"`
}

type ClientConn struct {
	ID        string
	ws        *websocket.Conn
	sendCh    chan WSMessage
	done      chan struct{}
	sequence  atomic.Uint64
	createdAt time.Time
	lastPing  time.Time
	mu        sync.Mutex
}

func newClientConn(id string, ws *websocket.Conn, bufferSize int) *ClientConn {
	return &ClientConn{
		ID:        id,
		ws:        ws,
		sendCh:    make(chan WSMessage, bufferSize),
		done:      make(chan struct{}),
		createdAt: time.Now(),
		lastPing:  time.Now(),
	}
}

func (c *ClientConn) Send(msg WSMessage) bool {
	msg.Sequence = c.sequence.Add(1)
	msg.Timestamp = time.Now().UnixMilli()

	select {
	case c.sendCh <- msg:
		return true
	default:
		return false // Backpressure: client too slow
	}
}

func (c *ClientConn) Close() {
	close(c.done)
	c.ws.Close()
}

type InferenceHandler func(ctx context.Context, input json.RawMessage, resultCh chan<- StreamChunk) error

type OmniWSStreamServer struct {
	mu      sync.RWMutex
	clients map[string]*ClientConn
	handler InferenceHandler
	config  WSConfig

	totalConnections atomic.Int64
	activeStreams    atomic.Int64
	totalMessages    atomic.Int64
}

type WSConfig struct {
	MaxClients        int
	SendBufferSize    int
	HeartbeatInterval time.Duration
	ReadTimeout       time.Duration
	WriteTimeout      time.Duration
}

func DefaultWSConfig() WSConfig {
	return WSConfig{
		MaxClients:        1000,
		SendBufferSize:    256,
		HeartbeatInterval: 30 * time.Second,
		ReadTimeout:       60 * time.Second,
		WriteTimeout:      10 * time.Second,
	}
}

func NewWSStreamServer(handler InferenceHandler, config WSConfig) *OmniWSStreamServer {
	return &OmniWSStreamServer{
		clients: make(map[string]*ClientConn),
		handler: handler,
		config:  config,
	}
}

func (s *OmniWSStreamServer) HandleWS(ws *websocket.Conn) {
	clientID := fmt.Sprintf("client_%d_%d",
		time.Now().UnixNano(), s.totalConnections.Add(1))

	s.mu.Lock()
	if len(s.clients) >= s.config.MaxClients {
		s.mu.Unlock()
		errMsg := WSMessage{
			Type:    MsgError,
			Payload: json.RawMessage(`{"error":"max_clients_reached"}`),
		}
		websocket.JSON.Send(ws, errMsg)
		ws.Close()
		return
	}

	client := newClientConn(clientID, ws, s.config.SendBufferSize)
	s.clients[clientID] = client
	s.mu.Unlock()

	log.Printf("Client connected: %s (total: %d)", clientID, len(s.clients))

	defer func() {
		s.mu.Lock()
		delete(s.clients, clientID)
		s.mu.Unlock()
		client.Close()
		log.Printf("Client disconnected: %s", clientID)
	}()

	// Writer goroutine
	go s.writeLoop(client)

	// Heartbeat goroutine
	go s.heartbeatLoop(client)

	// Reader loop (main goroutine for this connection)
	s.readLoop(client)
}

func (s *OmniWSStreamServer) readLoop(client *ClientConn) {
	for {
		var msg WSMessage
		err := websocket.JSON.Receive(client.ws, &msg)
		if err != nil {
			return
		}

		s.totalMessages.Add(1)

		switch msg.Type {
		case MsgInferenceRequest:
			go s.handleInference(client, msg)
		case MsgHeartbeat:
			client.mu.Lock()
			client.lastPing = time.Now()
			client.mu.Unlock()
		}
	}
}

func (s *OmniWSStreamServer) writeLoop(client *ClientConn) {
	for {
		select {
		case msg := <-client.sendCh:
			if err := websocket.JSON.Send(client.ws, msg); err != nil {
				return
			}
		case <-client.done:
			return
		}
	}
}

func (s *OmniWSStreamServer) heartbeatLoop(client *ClientConn) {
	ticker := time.NewTicker(s.config.HeartbeatInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			hb := WSMessage{
				Type:      MsgHeartbeat,
				Timestamp: time.Now().UnixMilli(),
			}
			if !client.Send(hb) {
				return
			}
		case <-client.done:
			return
		}
	}
}

func (s *OmniWSStreamServer) handleInference(client *ClientConn, msg WSMessage) {
	s.activeStreams.Add(1)
	defer s.activeStreams.Add(-1)

	// Send stream start
	client.Send(WSMessage{
		Type: MsgStreamStart,
		ID:   msg.ID,
	})

	resultCh := make(chan StreamChunk, 64)
	ctx, cancel := context.WithTimeout(context.Background(), s.config.ReadTimeout)
	defer cancel()

	// Run inference in background
	go func() {
		defer close(resultCh)
		if err := s.handler(ctx, msg.Payload, resultCh); err != nil {
			errPayload, _ := json.Marshal(map[string]string{"error": err.Error()})
			client.Send(WSMessage{
				Type:    MsgError,
				ID:      msg.ID,
				Payload: errPayload,
			})
		}
	}()

	// Stream results to client
	for chunk := range resultCh {
		payload, _ := json.Marshal(chunk)
		sent := client.Send(WSMessage{
			Type:    MsgStreamChunk,
			ID:      msg.ID,
			Payload: payload,
		})
		if !sent {
			log.Printf("Backpressure: dropping chunk for client %s", client.ID)
		}
	}

	// Send stream end
	client.Send(WSMessage{
		Type: MsgStreamEnd,
		ID:   msg.ID,
	})
}

func (s *OmniWSStreamServer) Stats() map[string]int64 {
	s.mu.RLock()
	numClients := int64(len(s.clients))
	s.mu.RUnlock()

	return map[string]int64{
		"active_clients":    numClients,
		"total_connections": s.totalConnections.Load(),
		"active_streams":    s.activeStreams.Load(),
		"total_messages":    s.totalMessages.Load(),
	}
}

func (s *OmniWSStreamServer) Broadcast(msg WSMessage) int {
	s.mu.RLock()
	defer s.mu.RUnlock()

	sent := 0
	for _, client := range s.clients {
		if client.Send(msg) {
			sent++
		}
	}
	return sent
}

func (s *OmniWSStreamServer) ServeHTTP(mux *http.ServeMux) {
	mux.Handle("/ws/inference", websocket.Handler(s.HandleWS))
}
