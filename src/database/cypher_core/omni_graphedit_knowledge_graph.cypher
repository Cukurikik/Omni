// Omni GraphEdit Knowledge Graph (Cypher)
// Database Layer: LLM-edited graph structure storage.
// Ref: HKUDS/GraphEdit
CREATE CONSTRAINT graphedit_node_unique IF NOT EXISTS FOR (n:GraphNode) REQUIRE n.node_id IS UNIQUE;
MERGE (n:GraphNode {node_id: $node_id})
SET n.embedding = $embedding, n.label = $label, n.updated_at = timestamp()
WITH n
UNWIND $neighbors AS neighbor_id
MATCH (m:GraphNode {node_id: neighbor_id})
MERGE (n)-[:CONNECTS_TO {weight: $weight}]->(m)
RETURN n.node_id;
