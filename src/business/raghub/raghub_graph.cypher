// RAGHub Neo4j taxonomy
// Cypher query for framework retrieval

// Bound: Limit query to 100 paths to avoid DB exhaustion
MATCH (f:Framework)-[:IMPLEMENTS]->(m:Methodology)
WHERE f.stars > 1000
RETURN f.name, m.name
ORDER BY f.stars DESC
LIMIT 100;
