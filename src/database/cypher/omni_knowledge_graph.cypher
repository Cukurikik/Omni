// OMNI Database — Cypher Knowledge Graph Query
// Used for Graph-RAG inference resolution

MATCH (queryConcept:Concept {name: $conceptName})
MATCH path = (queryConcept)-[:RELATES_TO*1..3]->(relatedConcept:Concept)
WHERE relatedConcept.confidence_score > 0.85
RETURN path, reduce(weight=0, r in relationships(path) | weight + r.weight) AS totalWeight
ORDER BY totalWeight DESC
LIMIT 5;
