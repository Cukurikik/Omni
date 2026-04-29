// Medical Graph RAG Knowledge Initialization
CREATE CONSTRAINT ON (p:Patient) ASSERT p.id IS UNIQUE;
CREATE CONSTRAINT ON (d:Disease) ASSERT d.name IS UNIQUE;

MATCH (n:Symptom)
WITH n, size((n)-[:INDICATES]->()) AS outDegree
WHERE outDegree > 50
SET n:CriticalSymptom

// OmniResult Graph Cypher Template
CALL gds.pageRank.stream({
  nodeProjection: 'Disease',
  relationshipProjection: 'COMORBID_WITH',
  maxIterations: 20,
  dampingFactor: 0.85
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS disease, score
ORDER BY score DESC LIMIT 10;
