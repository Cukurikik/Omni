package routes

import (
	"fmt"
	"net/http"
	"sync"

	"github.com/gorilla/websocket"
	"omnitools/services"
)

// ==========================================
// SWARM SIGNALING SERVER (WebRTC P2P Mesh)
// ==========================================
// Menghubungkan browser-browser dalam satu intranet agar bertukar file berat (P2P),
// membebaskan server Golang dari beban Bandwidth!

var upgraderSwarm = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Di tingkat produksi, batasi spesifik ke domain React
	},
}

// Peer merepresentasikan 1 Browser yang terhubung ke jaringan Swarm
type Peer struct {
	ID   string
	Conn *websocket.Conn
}

// SwarmRooms menyimpan daftar fileID -> Daftar Peers yang sedang memiliki atau mengunduh file tersebut.
var SwarmRooms = make(map[string]map[string]*Peer)
var swarmMutex sync.Mutex

type SignallingMessage struct {
	Type     string      `json:"type"`      // 'join', 'offer', 'answer', 'ice_candidate'
	FileID   string      `json:"file_id"`   // "result_9992.mp4"
	SenderID string      `json:"sender_id"` // UUID Klien
	TargetID string      `json:"target_id"` // UUID Target (Jika P2P direct)
	Payload  interface{} `json:"payload"`   // SDP atau ICE Data
}

// WebRTCSwarmHandler adalah endpoint WebSocket: ws://server/ws/swarm
func WebRTCSwarmHandler(w http.ResponseWriter, r *http.Request) {
	conn, err := upgraderSwarm.Upgrade(w, r, nil)
	if err != nil {
		services.WriteLog("SWARM", "ERROR", "Gagal menaikkan koneksi ke Swarm WS.")
		return
	}
	defer conn.Close()

	var clientID string
	var activeFileID string

	for {
		var msg SignallingMessage
		err := conn.ReadJSON(&msg)
		if err != nil {
			break // Klien Disconnect
		}

		swarmMutex.Lock()

		switch msg.Type {
		case "join":
			// Browser masuk ke ruangan per-file
			clientID = msg.SenderID
			activeFileID = msg.FileID

			if SwarmRooms[activeFileID] == nil {
				SwarmRooms[activeFileID] = make(map[string]*Peer)
			}

			// Tambahkan klien ke Swarm
			SwarmRooms[activeFileID][clientID] = &Peer{ID: clientID, Conn: conn}
			services.WriteLog("SWARM", "INFO_JOIN", fmt.Sprintf("Peer %s bergabung ke Swarm File: %s", clientID, activeFileID))

			// Beritahu dia siapa "Tetangga" atau "Seeders" lain yang sedang pegang file ini.
			var neighbors []string
			for pID := range SwarmRooms[activeFileID] {
				if pID != clientID {
					neighbors = append(neighbors, pID)
				}
			}

			// Kirim daftar tetangga agar Browser bisa memulai WebRTC 'Offer'
			conn.WriteJSON(map[string]interface{}{
				"type":      "swarm_neighbors",
				"neighbors": neighbors,
			})

		case "offer", "answer", "ice_candidate":
			// Murni sebagai KURIR/Mak Comblang.
			// Teruskan pesan dari SenderID ke TargetID
			if room, exists := SwarmRooms[msg.FileID]; exists {
				if targetPeer, found := room[msg.TargetID]; found {
					targetPeer.Conn.WriteJSON(msg)
				}
			}
		}

		swarmMutex.Unlock()
	}

	// === CLEANUP SAAT DISCONNECT ===
	if clientID != "" && activeFileID != "" {
		swarmMutex.Lock()
		if room, exists := SwarmRooms[activeFileID]; exists {
			delete(room, clientID)
			services.WriteLog("SWARM", "INFO_LEAVE", fmt.Sprintf("Peer %s meninggalkan Swarm File: %s", clientID, activeFileID))

			// Hancurkan ruangan jika kosong
			if len(room) == 0 {
				delete(SwarmRooms, activeFileID)
			}
		}
		swarmMutex.Unlock()
	}
}
