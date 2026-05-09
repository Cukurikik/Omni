package streaming

// omni_webrtc_signaling.go — WebRTC Signaling Server
// Layer: Network / Go
//
// Implements a WebSocket-based WebRTC signaling server for OMNI peer-to-peer
// streaming (audio/video/data). Strictly no mock logic.

import (
	"encoding/json"
	"log"
	"net/http"
	"sync"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true }, // Open for OMNI cluster
}

// SignalMessage represents the payload sent between peers.
type SignalMessage struct {
	Type     string `json:"type"`                // offer, answer, candidate, join
	TargetID string `json:"target_id,omitempty"` // The peer to send the message to
	SenderID string `json:"sender_id,omitempty"`
	Payload  string `json:"payload,omitempty"` // SDP or ICE candidate
}

// Client represents a connected WebSocket peer.
type Client struct {
	ID   string
	Conn *websocket.Conn
}

// OmniSignalingHub manages active WebRTC signaling sessions.
type OmniSignalingHub struct {
	clients map[string]*Client
	mutex   sync.RWMutex
}

// NewSignalingHub initializes a new hub.
func NewSignalingHub() *OmniSignalingHub {
	return &OmniSignalingHub{
		clients: make(map[string]*Client),
	}
}

// HandleWebSocket upgrades the HTTP connection and manages the peer lifecycle.
func (hub *OmniSignalingHub) HandleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("Upgrade error:", err)
		return
	}

	clientID := r.URL.Query().Get("id")
	if clientID == "" {
		conn.Close()
		return
	}

	client := &Client{ID: clientID, Conn: conn}

	hub.mutex.Lock()
	hub.clients[clientID] = client
	hub.mutex.Unlock()

	defer func() {
		hub.mutex.Lock()
		delete(hub.clients, clientID)
		hub.mutex.Unlock()
		conn.Close()
	}()

	for {
		_, msgData, err := conn.ReadMessage()
		if err != nil {
			break
		}

		var msg SignalMessage
		if err := json.Unmarshal(msgData, &msg); err != nil {
			continue
		}

		msg.SenderID = clientID

		// Route message to the specific target peer
		if msg.TargetID != "" {
			hub.routeMessage(msg)
		}
	}
}

// routeMessage safely sends a signal to the target peer.
func (hub *OmniSignalingHub) routeMessage(msg SignalMessage) {
	hub.mutex.RLock()
	target, exists := hub.clients[msg.TargetID]
	hub.mutex.RUnlock()

	if exists {
		outData, _ := json.Marshal(msg)
		target.Conn.WriteMessage(websocket.TextMessage, outData)
	}
}

// Broadcast sends a message to all connected peers (useful for room announcements).
func (hub *OmniSignalingHub) Broadcast(msg SignalMessage) {
	outData, _ := json.Marshal(msg)

	hub.mutex.RLock()
	defer hub.mutex.RUnlock()

	for _, client := range hub.clients {
		client.Conn.WriteMessage(websocket.TextMessage, outData)
	}
}

