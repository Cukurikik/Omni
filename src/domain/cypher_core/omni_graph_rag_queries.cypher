// OmniGraphRAGQueries - OMNI Database Layer
//
// Neo4j Cypher query abstractions used directly by the GraphRAG
// compute engine to discover communities and hierarchies.

// 1. Create a strongly typed document node
CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;

// 2. Discover Knowledge Communities (Louvain method prep)
// Identifies highly connected concept clusters
MATCH (c1:Concept)-[r:RELATES_TO]->(c2:Concept)
WITH c1, c2, count(r) AS weight
WHERE weight > 3
MERGE (c1)-[:STRONG_RELATION {weight: weight}]->(c2)
RETURN c1.name, c2.name, weight
ORDER BY weight DESC
LIMIT 50;

// 3. RAG Retrieval Query (Vector + Graph Hybrid)
// Assuming vector index 'concept_embeddings' exists
CALL db.index.vector.queryNodes('concept_embeddings', 5, $query_embedding)
YIELD node AS anchor, score
MATCH (anchor)-[:RELATES_TO*1..2]-(context:Concept)
WITH anchor, score, collect(context.name) AS expanded_context
RETURN anchor.name, score, expanded_context
ORDER BY score DESC;

// 4. Trace Data Lineage for Olmo Training (Security/Provenance)
MATCH (m:Model {name: "Olmo"})-[:TRAINED_ON]->(d:Dataset)
MATCH (d)<-[:CONTRIBUTED]-(a:Author)
WHERE a.license = "MIT" OR a.license = "Apache"
RETURN m.name, count(d) as safe_datasets
