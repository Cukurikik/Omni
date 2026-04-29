// OMNI Higgsfield - GPU Topology Graph
// Neo4j Cypher schema for mapping physical GPU interconnects (NVLink/PCIe/RDMA)

// Constraints
CREATE CONSTRAINT gpu_id_unique IF NOT EXISTS ON (g:GPU) ASSERT g.id IS UNIQUE;
CREATE CONSTRAINT node_id_unique IF NOT EXISTS ON (n:Node) ASSERT n.id IS UNIQUE;
CREATE CONSTRAINT switch_id_unique IF NOT EXISTS ON (s:Switch) ASSERT s.id IS UNIQUE;

// Node definitions
// GPU
// CREATE (g:GPU {id: "gpu_0", pcie_addr: "0000:01:00.0", compute_capability: 8.0, memory_gb: 40})

// Compute Node
// CREATE (n:Node {id: "node_0", hostname: "worker-0", datacenter: "us-east-1a"})

// Network Switch
// CREATE (s:Switch {id: "switch_0", type: "Infiniband", bandwidth_gbps: 200})

// Relationships representing interconnects
// NVLink between GPUs on the same node
// MATCH (g1:GPU {id: "gpu_0"}), (g2:GPU {id: "gpu_1"})
// CREATE (g1)-[:NVLINK_CONNECTED {lanes: 12, bandwidth_gbps: 600}]->(g2)

// GPU to Node mapping
// MATCH (g:GPU {id: "gpu_0"}), (n:Node {id: "node_0"})
// CREATE (g)-[:LOCATED_IN]->(n)

// Node to Switch (RDMA/RoCE)
// MATCH (n:Node {id: "node_0"}), (s:Switch {id: "switch_0"})
// CREATE (n)-[:NETWORK_LINK {type: "RDMA", bandwidth_gbps: 100}]->(s)

// Query: Find shortest path between two GPUs to optimize tensor placement
// MATCH p = shortestPath((g1:GPU {id: "gpu_0"})-[*]-(g2:GPU {id: "gpu_15"}))
// RETURN p;
