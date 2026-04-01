package services

import (
	"fmt"
	"os"
	"strings"
	"sync"
)

var (
	clusterNodes []string
	nodeIndex    int
	clusterMutex sync.Mutex
)

// LoadClusterConfig mengambil daftar IP "Server Budak" (Slave Servers)
// dari variabel sistem: OMNI_CLUSTER_NODES="192.168.1.10,192.168.1.11,10.0.0.5"
// Wajib dipanggil di fungsi init() atau main.go saat server menyala.
func LoadClusterConfig() {
	nodesEnv := os.Getenv("OMNI_CLUSTER_NODES")
	if nodesEnv == "" {
		WriteLog("CLUSTER", "INFO_LOCAL_ONLY", "Variabel OMNI_CLUSTER_NODES kosong. Berjalan murni di Cerebro Master (Localhost).")
		return
	}

	nodes := strings.Split(nodesEnv, ",")
	for _, n := range nodes {
		clean := strings.TrimSpace(n)
		if clean != "" {
			clusterNodes = append(clusterNodes, clean)
		}
	}
	WriteLog("CLUSTER", "INFO_NODES_LOADED", fmt.Sprintf("Berhasil memuat %d Remote Nodes untuk distribusi kerja SSH.", len(clusterNodes)))
}

// GetNextNode membagikan pekerjaan secara adil (Round-Robin Load Balancer) ke setiap Server Budak.
func GetNextNode() string {
	clusterMutex.Lock()
	defer clusterMutex.Unlock()

	// Jika tidak ada Node tambahan, biarkan Master bekerja
	if len(clusterNodes) == 0 {
		return ""
	}

	node := clusterNodes[nodeIndex]
	nodeIndex = (nodeIndex + 1) % len(clusterNodes)
	return node
}
