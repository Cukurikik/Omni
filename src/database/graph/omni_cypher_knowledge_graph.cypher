// OMNI Database & Query Layer
// Cypher query for extracting semantic knowledge graphs formed by the attention heads

// 1. Identify dense subgraphs where Attention Heads heavily correlated across contexts
MATCH (h:AttentionHead)-[r:ATTENDS_TO]->(t:Token)
WHERE r.weight > 0.8
WITH h, count(t) AS high_attention_targets
WHERE high_attention_targets > 5

// 2. Discover conceptual clusters based on co-attention
MATCH (h)-[r1:ATTENDS_TO]->(t1:Token)<-[r2:ATTENDS_TO]-(h2:AttentionHead)
WHERE h <> h2 AND r1.weight > 0.7 AND r2.weight > 0.7

// 3. Project the knowledge graph
MERGE (h)-[c:CO_ATTENDS_WITH {weight: (r1.weight + r2.weight) / 2.0}]->(h2)
RETURN h.layer, h.head_idx, h2.layer, h2.head_idx, c.weight
ORDER BY c.weight DESC
LIMIT 100;
