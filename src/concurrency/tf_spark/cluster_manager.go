package tf_spark

import (
	"fmt"
	"sync"
)

// OMNI TF-SPARK: Cluster Manager
// Go logic simulating the orchestration of TensorFlow worker nodes across an Apache Spark cluster.
// Source: yahoo/TensorFlowOnSpark

type TFNodeRole string

const (
	RoleParameterServer TFNodeRole = "PS"
	RoleWorker          TFNodeRole = "WORKER"
)

type TFNode struct {
	ID       string
	Role     TFNodeRole
	IP       string
	Port     int
	GPUCount int
	Status   string // "PENDING", "RUNNING", "FAILED"
}

type TFClusterManager struct {
	mu     sync.RWMutex
	nodes  map[string]*TFNode
}

func NewTFClusterManager() *TFClusterManager {
	return &TFClusterManager{
		nodes: make(map[string]*TFNode),
	}
}

// Registers a Spark Executor that has spawned a TensorFlow process
func (c *TFClusterManager) RegisterNode(id string, role TFNodeRole, ip string, port int, gpus int) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	if _, exists := c.nodes[id]; exists {
		return fmt.Errorf("TF node %s already registered", id)
	}

	c.nodes[id] = &TFNode{
		ID:       id,
		Role:     role,
		IP:       ip,
		Port:     port,
		GPUCount: gpus,
		Status:   "RUNNING",
	}

	fmt.Printf("[TFOnSpark] Registered %s Node: %s at %s:%d (GPUs: %d)\n", role, id, ip, port, gpus)
	return nil
}

// Generates the TF_CONFIG environment variable payload required by distributed TensorFlow
func (c *TFClusterManager) GenerateTFConfig() map[string][]string {
	c.mu.RLock()
	defer c.mu.RUnlock()

	config := map[string][]string{
		"ps":     {},
		"worker": {},
	}

	for _, node := range c.nodes {
		addr := fmt.Sprintf("%s:%d", node.IP, node.Port)
		if node.Role == RoleParameterServer {
			config["ps"] = append(config["ps"], addr)
		} else {
			config["worker"] = append(config["worker"], addr)
		}
	}

	return config
}
