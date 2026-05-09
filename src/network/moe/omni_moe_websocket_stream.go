package network_moe

import (
	"encoding/json"
	"log"
	"net/http"
	"sync"

	"github.com/gorilla/websocket"
)

// OMNI MOTHER Production Zero-Mock WebSocket Stream
// Go WebSocket server designed to stream generated MoE tokens
// back to the client interface in real-time with minimal overhead.

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Allow all for Omni API
	},
}

type TokenPayload struct {
	Token   string  `json:"token"`
	Logprob float64 `json:"logprob,omitempty"`
	Expert  string  `json:"expert,omitempty"`
}

type StreamManager struct {
	clients map[*websocket.Conn]bool
	mu      sync.Mutex
}

func NewStreamManager() *StreamManager {
	return &StreamManager{
		clients: make(map[*websocket.Conn]bool),
	}
}

func (sm *StreamManager) HandleConnections(w http.ResponseWriter, r *http.Request) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("OMNI CRITICAL: WebSocket Upgrade Error: %v", err)
		return
	}
	defer ws.Close()

	sm.mu.Lock()
	sm.clients[ws] = true
	sm.mu.Unlock()

	log.Println("OMNI NETWORK: Client connected for token stream.")

	// Keep alive loop
	for {
		_, _, err := ws.ReadMessage()
		if err != nil {
			sm.mu.Lock()
			delete(sm.clients, ws)
			sm.mu.Unlock()
			break
		}
	}
}

func (sm *StreamManager) BroadcastToken(token string, expert string) {
	payload := TokenPayload{
		Token:  token,
		Expert: expert,
	}

	msg, err := json.Marshal(payload)
	if err != nil {
		return
	}

	sm.mu.Lock()
	defer sm.mu.Unlock()

	for client := range sm.clients {
		err := client.WriteMessage(websocket.TextMessage, msg)
		if err != nil {
			client.Close()
			delete(sm.clients, client)
		}
	}
}

