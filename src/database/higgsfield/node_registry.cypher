// OMNI HIGGSFIELD: Node Registry
// Cypher schema for modeling the complex topology of a GPU cluster network.
// Maps Nodes to their internal GPUs and Network Switches to optimize NCCL ring formation.
// Source: higgsfield-ai/higgsfield

// Create physical compute nodes
CREATE CONSTRAINT IF NOT EXISTS ON (n:ComputeNode) ASSERT n.hostname IS UNIQUE;

// Create GPUs
CREATE CONSTRAINT IF NOT EXISTS ON (g:GPU) ASSERT g.uuid IS UNIQUE;

// Create Network Switches (for topology-aware scheduling)
CREATE CONSTRAINT IF NOT EXISTS ON (s:Switch) ASSERT s.ip IS UNIQUE;

// Example Topology Generation
// Node 1
MERGE (n1:ComputeNode {hostname: "worker-1", ip: "10.0.1.10", cpus: 96, ram_gb: 1024})
MERGE (g1:GPU {uuid: "GPU-a1b2", model: "A100", vram_gb: 80})
MERGE (g2:GPU {uuid: "GPU-c3d4", model: "A100", vram_gb: 80})
MERGE (n1)-[:HAS_GPU {pcie_bus: "0000:17:00.0"}]->(g1)
MERGE (n1)-[:HAS_GPU {pcie_bus: "0000:b3:00.0"}]->(g2)
MERGE (g1)-[:NVLINK_CONNECTED {bandwidth_gbps: 600}]->(g2)

// Switch connection
MERGE (sw1:Switch {ip: "10.0.1.1", layer: "ToR"})
MERGE (n1)-[:CONNECTED_TO {speed_gbps: 100}]->(sw1)

// Query to find optimal nodes for a job (Topology Aware)
/*
MATCH (n:ComputeNode)-[:HAS_GPU]->(g:GPU)
WITH n, COUNT(g) as gpu_count
WHERE gpu_count >= 8
RETURN n.hostname
*/
