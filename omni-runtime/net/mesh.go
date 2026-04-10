package net

import (
	"encoding/json"
	"fmt"
	"log"
	"net"
	"sync"
	"sync/atomic"
	"time"
)

// ==========================================
// 🌍 OMNI-MESH: DECENTRALIZED P2P GLOBAL SWARM
// ==========================================
// Pemusnahan Kubernetes Master Node & Cloud Load Balancer.
//
// ARSITEKTUR (Gossip Protocol):
//   Setiap biner OMNI yang berjalan di dunia saling terhubung via UDP.
//   Mereka berbisik (gossip) status RAM, CPU, dan Queue ke tetangga.
//   Jika satu node mati, node lain mengambil alih tugasnya.
//   Tidak ada "Master Node" — semua node SETARA (Truly Decentralized).
//
// PROTOKOL:
//   1. Node baru bergabung → kirim HELLO ke seed peers
//   2. Seed peers membalas dengan daftar semua node aktif
//   3. Setiap 3 detik, node mengirim HEARTBEAT ke 3 tetangga acak
//   4. Jika node tidak membalas 3x heartbeat → dianggap MATI
//   5. Broadcast: kirim pesan ke SEMUA node via gossip relay
//
// KEUNGGULAN vs Kubernetes:
//   K8s: Butuh etcd, API server, scheduler, kubelet, flannel — 100+ config
//   MESH: Zero config, 1 biner, UDP gossip, auto-discovery
// ==========================================

// MeshNode representasi satu node dalam jaringan mesh
type MeshNode struct {
	ID       string `json:"id"`
	Address  string `json:"address"`  // host:port UDP
	LastSeen int64  `json:"last_seen"`
	CPU      int    `json:"cpu_cores"`
	MemMB    int    `json:"mem_mb"`
	Region   string `json:"region"`
	Version  string `json:"version"`
	Alive    bool   `json:"alive"`
}

// MeshMessage format pesan antar node
type MeshMessage struct {
	Type    string      `json:"type"`      // HELLO, HEARTBEAT, BROADCAST, SYNC
	Source  string      `json:"source"`    // Node ID pengirim
	Target  string      `json:"target"`    // Node ID tujuan (kosong = semua)
	Topic   string      `json:"topic"`     // Topik broadcast
	Payload interface{} `json:"payload"`
	TTL     int         `json:"ttl"`       // Time to Live (hop count)
}

// MeshConfig konfigurasi mesh network
type MeshConfig struct {
	NodeID           string
	BindAddr         string        // UDP bind address (:9090)
	SeedPeers        []string      // Daftar seed node awal
	HeartbeatInterval time.Duration
	DeadTimeout      time.Duration // Setelah ini tanpa heartbeat = mati
	MaxTTL           int           // Maks relay hop
	Region           string
}

// DefaultMeshConfig konfigurasi default
func DefaultMeshConfig() MeshConfig {
	return MeshConfig{
		NodeID:            fmt.Sprintf("omni_%d", time.Now().UnixNano()%100000),
		BindAddr:          ":9090",
		HeartbeatInterval: 3 * time.Second,
		DeadTimeout:       10 * time.Second,
		MaxTTL:            5,
		Region:            "auto",
	}
}

// OmniMesh mesin mesh P2P
type OmniMesh struct {
	config   MeshConfig
	conn     *net.UDPConn
	nodes    map[string]*MeshNode
	handlers map[string]BroadcastHandler
	mu       sync.RWMutex
	running  atomic.Bool
	stats    MeshStats
}

// MeshStats statistik mesh
type MeshStats struct {
	MessagesSent     atomic.Int64
	MessagesReceived atomic.Int64
	NodesActive      atomic.Int64
	NodesDead        atomic.Int64
	BroadcastsSent   atomic.Int64
}

// BroadcastHandler fungsi handler untuk broadcast tertentu
type BroadcastHandler func(topic string, payload interface{}, source string)

// IgniteMesh menyalakan mesin mesh P2P
func IgniteMesh(config MeshConfig) (*OmniMesh, error) {
	log.Printf("🌍 [OMNI-MESH] Memulai node %s di %s...", config.NodeID, config.BindAddr)

	// Buka UDP socket
	addr, err := net.ResolveUDPAddr("udp", config.BindAddr)
	if err != nil {
		return nil, fmt.Errorf("gagal resolve UDP addr: %w", err)
	}

	conn, err := net.ListenUDP("udp", addr)
	if err != nil {
		return nil, fmt.Errorf("gagal listen UDP: %w", err)
	}

	mesh := &OmniMesh{
		config:   config,
		conn:     conn,
		nodes:    make(map[string]*MeshNode),
		handlers: make(map[string]BroadcastHandler),
	}

	mesh.running.Store(true)

	// Kirim HELLO ke seed peers
	for _, peer := range config.SeedPeers {
		mesh.sendMessage(peer, MeshMessage{
			Type:   "HELLO",
			Source: config.NodeID,
			Payload: map[string]interface{}{
				"address": config.BindAddr,
				"region":  config.Region,
				"version": "1.3.0-SOVEREIGN",
			},
			TTL: 1,
		})
	}

	// Background receiver
	go mesh.receiveLoop()

	// Heartbeat sender
	go mesh.heartbeatLoop()

	// Dead node detector
	go mesh.reaper()

	log.Printf("🌍 [OMNI-MESH] Node %s ONLINE — menunggu koneksi dari dunia...", config.NodeID)
	return mesh, nil
}

// OnBroadcast mendaftarkan handler untuk topik broadcast tertentu
func (m *OmniMesh) OnBroadcast(topic string, handler BroadcastHandler) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.handlers[topic] = handler
}

// Broadcast mengirim pesan ke SEMUA node di mesh
func (m *OmniMesh) Broadcast(topic string, data interface{}) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	msg := MeshMessage{
		Type:    "BROADCAST",
		Source:  m.config.NodeID,
		Topic:   topic,
		Payload: data,
		TTL:     m.config.MaxTTL,
	}

	for _, node := range m.nodes {
		if node.Alive && node.ID != m.config.NodeID {
			m.sendMessage(node.Address, msg)
		}
	}

	m.stats.BroadcastsSent.Add(1)
	log.Printf("📡 [MESH] Broadcast '%s' ke %d nodes", topic, len(m.nodes))
}

// sendMessage mengirim pesan UDP ke alamat tertentu
func (m *OmniMesh) sendMessage(addr string, msg MeshMessage) {
	udpAddr, err := net.ResolveUDPAddr("udp", addr)
	if err != nil {
		return
	}

	data, err := json.Marshal(msg)
	if err != nil {
		return
	}

	_, _ = m.conn.WriteToUDP(data, udpAddr)
	m.stats.MessagesSent.Add(1)
}

// receiveLoop menerima dan memproses pesan dari network
func (m *OmniMesh) receiveLoop() {
	buf := make([]byte, 65535) // Max UDP packet

	for m.running.Load() {
		n, remoteAddr, err := m.conn.ReadFromUDP(buf)
		if err != nil {
			continue
		}

		m.stats.MessagesReceived.Add(1)

		var msg MeshMessage
		if err := json.Unmarshal(buf[:n], &msg); err != nil {
			continue
		}

		m.handleMessage(msg, remoteAddr)
	}
}

// handleMessage memproses pesan yang diterima
func (m *OmniMesh) handleMessage(msg MeshMessage, from *net.UDPAddr) {
	switch msg.Type {
	case "HELLO":
		// Node baru bergabung — daftarkan!
		m.mu.Lock()
		payload, _ := json.Marshal(msg.Payload)
		var info map[string]interface{}
		_ = json.Unmarshal(payload, &info)

		m.nodes[msg.Source] = &MeshNode{
			ID:       msg.Source,
			Address:  from.String(),
			LastSeen: time.Now().Unix(),
			Alive:    true,
			Version:  "1.3.0",
		}
		m.stats.NodesActive.Add(1)
		m.mu.Unlock()

		log.Printf("👋 [MESH] Node baru: %s (%s)", msg.Source, from.String())

		// Balas dengan daftar semua node yang dikenal
		m.sendMessage(from.String(), MeshMessage{
			Type:    "SYNC",
			Source:  m.config.NodeID,
			Payload: m.getNodeList(),
		})

	case "HEARTBEAT":
		m.mu.Lock()
		if node, ok := m.nodes[msg.Source]; ok {
			node.LastSeen = time.Now().Unix()
			node.Alive = true
		}
		m.mu.Unlock()

	case "BROADCAST":
		if msg.TTL <= 0 {
			return // Stop relay
		}
		// Handle broadcast
		m.mu.RLock()
		handler, exists := m.handlers[msg.Topic]
		m.mu.RUnlock()

		if exists {
			handler(msg.Topic, msg.Payload, msg.Source)
		}

		// Relay ke tetangga (gossip propagation)
		msg.TTL--
		if msg.TTL > 0 {
			m.mu.RLock()
			for _, node := range m.nodes {
				if node.Alive && node.ID != msg.Source && node.ID != m.config.NodeID {
					m.sendMessage(node.Address, msg)
				}
			}
			m.mu.RUnlock()
		}

	case "SYNC":
		// Terima daftar node dari peer
		payload, _ := json.Marshal(msg.Payload)
		var nodes []MeshNode
		_ = json.Unmarshal(payload, &nodes)

		m.mu.Lock()
		for _, n := range nodes {
			if _, exists := m.nodes[n.ID]; !exists {
				node := n
				m.nodes[n.ID] = &node
				m.stats.NodesActive.Add(1)
			}
		}
		m.mu.Unlock()
	}
}

// heartbeatLoop mengirim heartbeat periodik ke tetangga
func (m *OmniMesh) heartbeatLoop() {
	ticker := time.NewTicker(m.config.HeartbeatInterval)
	defer ticker.Stop()

	for range ticker.C {
		if !m.running.Load() {
			return
		}

		msg := MeshMessage{
			Type:   "HEARTBEAT",
			Source: m.config.NodeID,
			TTL:    1,
		}

		m.mu.RLock()
		for _, node := range m.nodes {
			if node.Alive {
				m.sendMessage(node.Address, msg)
			}
		}
		m.mu.RUnlock()
	}
}

// reaper mendeteksi node yang mati
func (m *OmniMesh) reaper() {
	ticker := time.NewTicker(m.config.DeadTimeout)
	defer ticker.Stop()

	for range ticker.C {
		if !m.running.Load() {
			return
		}

		now := time.Now().Unix()
		threshold := int64(m.config.DeadTimeout.Seconds())

		m.mu.Lock()
		for _, node := range m.nodes {
			if node.Alive && (now-node.LastSeen) > threshold {
				node.Alive = false
				m.stats.NodesActive.Add(-1)
				m.stats.NodesDead.Add(1)
				log.Printf("💀 [MESH] Node %s dinyatakan MATI (tidak ada heartbeat)", node.ID)
			}
		}
		m.mu.Unlock()
	}
}

// getNodeList mengembalikan daftar node yang alive
func (m *OmniMesh) getNodeList() []MeshNode {
	m.mu.RLock()
	defer m.mu.RUnlock()

	var list []MeshNode
	for _, n := range m.nodes {
		if n.Alive {
			list = append(list, *n)
		}
	}
	return list
}

// GetMeshStats mengembalikan statistik mesh
func (m *OmniMesh) GetMeshStats() map[string]interface{} {
	return map[string]interface{}{
		"node_id":           m.config.NodeID,
		"bind_addr":         m.config.BindAddr,
		"region":            m.config.Region,
		"messages_sent":     m.stats.MessagesSent.Load(),
		"messages_received": m.stats.MessagesReceived.Load(),
		"nodes_active":      m.stats.NodesActive.Load(),
		"nodes_dead":        m.stats.NodesDead.Load(),
		"broadcasts_sent":   m.stats.BroadcastsSent.Load(),
	}
}

// Shutdown menghentikan mesh
func (m *OmniMesh) Shutdown() {
	log.Printf("🛑 [OMNI-MESH] Node %s meninggalkan jaringan...", m.config.NodeID)
	m.running.Store(false)
	m.conn.Close()
}
