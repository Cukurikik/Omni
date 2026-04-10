package core

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sort"
	"sync"
	"time"
)

// ==========================================
// 👑 OMNI-NEXUS: DISTRIBUTED FLEET REGISTRY
// ==========================================
// Sistem Orkestrasi Bawaan (Native Orchestration).
// Master Node melacak semua Worker Node secara real-time.
//
// Tanpa Kubernetes. Tanpa Docker Swarm. Tanpa Apache Kafka.
// Kedaulatan penuh: Bare-Metal Orchestration.
// ==========================================

// WorkerNode merepresentasikan satu Prajurit dalam armada NEXUS.
type WorkerNode struct {
	IPAddress   string  `json:"ip_address"`
	NodeName    string  `json:"node_name,omitempty"`
	ActiveJobs  int     `json:"active_jobs"`
	MaxJobs     int     `json:"max_jobs"`
	CPUPercent  float64 `json:"cpu_percent"`
	MemUsedMB   int64   `json:"mem_used_mb"`
	MemTotalMB  int64   `json:"mem_total_mb"`
	LastSeen    int64   `json:"last_seen"`
	UptimeSec   int64   `json:"uptime_seconds"`
	Version     string  `json:"version,omitempty"`
}

// NexusStatus adalah snapshot armada (untuk monitoring/dashboard).
type NexusStatus struct {
	Role         string        `json:"role"`
	TotalWorkers int           `json:"total_workers"`
	AliveWorkers int           `json:"alive_workers"`
	TotalCapacity int          `json:"total_capacity"`
	ActiveJobs   int           `json:"active_jobs"`
	Workers      []*WorkerNode `json:"workers"`
}

var (
	// NexusFleet menyimpan peta seluruh Prajurit yang aktif.
	// Key: IPAddress, Value: WorkerNode
	NexusFleet = make(map[string]*WorkerNode)
	fleetMutex sync.RWMutex
)

// ==========================================
// 📡 HEARTBEAT HANDLER (MASTER ONLY)
// ==========================================
// Menerima laporan detak jantung dari semua Worker Node.
// Worker mengirim POST setiap N detik dengan state mereka.

func NexusHeartbeatHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method Not Allowed", 405)
		return
	}

	// 🛡️ Verifikasi kunci rahasia cluster
	if r.Header.Get("X-NEXUS-KEY") != AppConfig.NexusCluster.ClusterSecret {
		log.Printf("🚨 [NEXUS] Penyusup terdeteksi! IP: %s", r.RemoteAddr)
		http.Error(w, `{"error":"NEXUS_AUTH_FAILED","message":"Penyusup Terdeteksi. Akses Ditolak."}`, 403)
		return
	}

	var node WorkerNode
	if err := json.NewDecoder(r.Body).Decode(&node); err != nil {
		http.Error(w, `{"error":"INVALID_PAYLOAD"}`, 400)
		return
	}

	// Validasi field wajib
	if node.IPAddress == "" {
		http.Error(w, `{"error":"MISSING_IP_ADDRESS"}`, 400)
		return
	}

	node.LastSeen = time.Now().Unix()

	fleetMutex.Lock()
	existing, wasKnown := NexusFleet[node.IPAddress]
	NexusFleet[node.IPAddress] = &node
	fleetMutex.Unlock()

	if !wasKnown || existing == nil {
		log.Printf("🟢 [NEXUS] Prajurit baru bergabung: %s (%s) | Kapasitas: %d job",
			node.IPAddress, node.NodeName, node.MaxJobs)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(200)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": "ACK",
		"time":   time.Now().Unix(),
	})
}

// ==========================================
// 🗑️ FLEET MONITOR (MASTER ONLY)
// ==========================================
// Goroutine yang berjalan tanpa henti di Master Node.
// Setiap 10 detik: Periksa Worker mana yang sudah tidak mengirim heartbeat.
// Jika lebih dari DeadThresholdSec detik tanpa kabar → Node dianggap gugur.

func StartFleetMonitor() {
	deadThreshold := int64(AppConfig.NexusCluster.DeadThresholdSec)
	if deadThreshold <= 0 {
		deadThreshold = 15
	}

	log.Printf("👑 [NEXUS MASTER] Fleet Monitor aktif. Dead threshold: %ds", deadThreshold)

	go func() {
		for {
			time.Sleep(10 * time.Second)
			now := time.Now().Unix()

			fleetMutex.Lock()
			for ip, node := range NexusFleet {
				if now-node.LastSeen > deadThreshold {
					log.Printf("⚠️ [NEXUS] 💀 Prajurit Gugur (Timeout %ds): %s (%s) | Jobs saat mati: %d",
						now-node.LastSeen, ip, node.NodeName, node.ActiveJobs)
					delete(NexusFleet, ip)
				}
			}
			fleetMutex.Unlock()
		}
	}()
}

// ==========================================
// ⚖️ LOAD BALANCER: LEAST CONNECTION ALGORITHM
// ==========================================
// Mencari Worker Node yang paling senggang (ActiveJobs paling sedikit)
// dan masih memiliki kapasitas (ActiveJobs < MaxJobs).
//
// Return:
//   - string: IP Worker terbaik, atau "" jika tidak ada yang tersedia.
//   - *WorkerNode: Detail node, atau nil jika tidak ada.

func GetIdleWorker() (string, *WorkerNode) {
	fleetMutex.RLock()
	defer fleetMutex.RUnlock()

	if len(NexusFleet) == 0 {
		return "", nil
	}

	// Kumpulkan semua worker yang masih ada kapasitas
	type candidate struct {
		ip   string
		node *WorkerNode
	}
	var candidates []candidate

	for ip, node := range NexusFleet {
		if node.ActiveJobs < node.MaxJobs {
			candidates = append(candidates, candidate{ip, node})
		}
	}

	if len(candidates) == 0 {
		return "", nil // Seluruh armada penuh!
	}

	// Sort by ActiveJobs (ascending), lalu pilih yang paling senggang
	sort.Slice(candidates, func(i, j int) bool {
		return candidates[i].node.ActiveJobs < candidates[j].node.ActiveJobs
	})

	best := candidates[0]
	return best.ip, best.node
}

// ==========================================
// 🌐 NEXUS STATUS HANDLER (DASHBOARD API)
// ==========================================
// Endpoint monitoring untuk Dashboard UI:
// GET /api/nexus/status → JSON snapshot seluruh armada.

func NexusStatusHandler(w http.ResponseWriter, r *http.Request) {
	// Opsional: Validasi kunci
	if r.Header.Get("X-NEXUS-KEY") != AppConfig.NexusCluster.ClusterSecret {
		http.Error(w, `{"error":"NEXUS_AUTH_FAILED"}`, 403)
		return
	}

	fleetMutex.RLock()
	defer fleetMutex.RUnlock()

	status := NexusStatus{
		Role:         AppConfig.NexusCluster.Role,
		TotalWorkers: len(NexusFleet),
		Workers:      make([]*WorkerNode, 0, len(NexusFleet)),
	}

	for _, node := range NexusFleet {
		status.Workers = append(status.Workers, node)
		status.TotalCapacity += node.MaxJobs
		status.ActiveJobs += node.ActiveJobs

		now := time.Now().Unix()
		if now-node.LastSeen <= int64(AppConfig.NexusCluster.DeadThresholdSec) {
			status.AliveWorkers++
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(status)
}

// ==========================================
// 🚀 NEXUS DISPATCH: DELEGASI TUGAS KE WORKER
// ==========================================
// Master menerima request dari user → cari Worker terbaik → forward request.
// Jika tidak ada Worker yang tersedia → proses lokal (fallback).

func NexusDispatch(toolID string, payload []byte) (string, error) {
	workerIP, node := GetIdleWorker()

	if workerIP == "" {
		// Tidak ada worker tersedia → proses lokal
		return "local", nil
	}

	log.Printf("🚀 [NEXUS DISPATCH] Mendelegasikan '%s' ke %s (%s) | Load: %d/%d",
		toolID, workerIP, node.NodeName, node.ActiveJobs, node.MaxJobs)

	// Build request ke Worker
	url := fmt.Sprintf("http://%s/api/v1/process?tool_id=%s", workerIP, toolID)
	req, err := http.NewRequest("POST", url, nil) // Payload dikirim oleh caller
	if err != nil {
		return "local", fmt.Errorf("gagal membuat request: %w", err)
	}

	req.Header.Set("X-NEXUS-KEY", AppConfig.NexusCluster.ClusterSecret)
	req.Header.Set("X-NEXUS-DELEGATED", "true")
	req.Header.Set("Content-Type", "application/octet-stream")

	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		log.Printf("⚠️ [NEXUS DISPATCH] Worker %s gagal merespon: %v — Fallback ke lokal", workerIP, err)
		return "local", nil
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		log.Printf("⚠️ [NEXUS DISPATCH] Worker %s return %d — Fallback ke lokal", workerIP, resp.StatusCode)
		return "local", nil
	}

	return workerIP, nil
}

// ==========================================
// 🔢 NEXUS METRICS: ACTIVE JOB COUNTER
// ==========================================
// Counter thread-safe untuk menghitung berapa job yang sedang aktif
// di node ini. Digunakan oleh Worker saat mengirim Heartbeat.

var (
	nexusActiveJobs int
	nexusJobMutex   sync.Mutex
)

// GetCurrentActiveJobs mengembalikan jumlah job yang sedang berjalan.
func GetCurrentActiveJobs() int {
	nexusJobMutex.Lock()
	defer nexusJobMutex.Unlock()
	return nexusActiveJobs
}

// IncrementActiveJobs menambah counter saat job dimulai.
func IncrementActiveJobs() {
	nexusJobMutex.Lock()
	defer nexusJobMutex.Unlock()
	nexusActiveJobs++
}

// DecrementActiveJobs mengurangi counter saat job selesai.
func DecrementActiveJobs() {
	nexusJobMutex.Lock()
	defer nexusJobMutex.Unlock()
	if nexusActiveJobs > 0 {
		nexusActiveJobs--
	}
}

// GetRegisteredWorkerCount mengembalikan jumlah worker nodes yang terdaftar di cluster.
// Digunakan oleh Prometheus metrics.
func GetRegisteredWorkerCount() int {
	fleetMutex.RLock()
	defer fleetMutex.RUnlock()
	return len(NexusFleet)
}


