// OMNI Cypher Queries for AwesomeLLM4SE Knowledge Graph
// Bounded query depths for Neo4j/Memgraph instances

// Create Paper Node with hardcoded schema validation limits via application layer
CREATE CONSTRAINT ON (p:Paper) ASSERT p.omni_id IS UNIQUE;

// Add Paper to Cluster (from R compute layer output)
// Limits graph depth explicitly
MATCH (c:Cluster {id: $cluster_id})
MERGE (p:Paper {omni_id: $paper_id})
ON CREATE SET p.title = $title, p.added_at = timestamp()
MERGE (p)-[r:BELONGS_TO]->(c)
SET r.confidence = $wss_score;

// Retrieve Top K papers from a cluster
// Strict LIMIT enforced
MATCH (c:Cluster {id: $cluster_id})<-[r:BELONGS_TO]-(p:Paper)
WHERE r.confidence > 0.8
RETURN p.omni_id, p.title, r.confidence
ORDER BY r.confidence DESC
LIMIT 50;

// Semantic path finding with max depth bound
MATCH path = (p1:Paper {omni_id: $start_id})-[:CITES*1..3]->(p2:Paper)
RETURN path
LIMIT 100;
