// @omni-layer Database | @omni-lang Cypher (Neo4j) | @omni-batch 17
// @omni-description Knowledge graph schema: Cypher queries for ontology storage,
// taxonomy traversal, and semantic relationship discovery in Neo4j.

// === SCHEMA CREATION ===
// Create constraints
CREATE CONSTRAINT concept_name IF NOT EXISTS
FOR (c:Concept) REQUIRE c.name IS UNIQUE;

CREATE CONSTRAINT model_id IF NOT EXISTS
FOR (m:Model) REQUIRE m.modelId IS UNIQUE;

// Create indexes for performance
CREATE INDEX concept_type IF NOT EXISTS
FOR (c:Concept) ON (c.type);

CREATE INDEX relation_predicate IF NOT EXISTS
FOR ()-[r:RELATES_TO]-() ON (r.predicate);

// === DATA INGESTION ===
// Insert concepts with properties
UNWIND $concepts AS concept
MERGE (c:Concept {name: concept.name})
SET c.type = concept.type,
    c.confidence = concept.confidence,
    c.source = concept.source,
    c.embedding = concept.embedding,
    c.updatedAt = datetime();

// Insert taxonomy edges
UNWIND $taxonomyEdges AS edge
MATCH (child:Concept {name: edge.child})
MATCH (parent:Concept {name: edge.parent})
MERGE (child)-[:IS_A {confidence: edge.confidence}]->(parent);

// Insert semantic relations
UNWIND $relations AS rel
MATCH (s:Concept {name: rel.subject})
MATCH (o:Concept {name: rel.object})
MERGE (s)-[:RELATES_TO {
    predicate: rel.predicate,
    confidence: rel.confidence,
    source: rel.source
}]->(o);

// === QUERIES ===
// 1. Find all ancestors of a concept (transitive IS_A)
MATCH path = (c:Concept {name: $conceptName})-[:IS_A*]->(ancestor:Concept)
RETURN [node IN nodes(path) | node.name] AS ancestorPath,
       length(path) AS depth
ORDER BY depth;

// 2. Find common ancestors of two concepts
MATCH (a:Concept {name: $conceptA})-[:IS_A*]->(common:Concept)
MATCH (b:Concept {name: $conceptB})-[:IS_A*]->(common)
RETURN common.name AS commonAncestor,
       common.type AS type,
       common.confidence AS confidence
ORDER BY common.confidence DESC;

// 3. Find related concepts within N hops
MATCH path = (c:Concept {name: $conceptName})-[*1..3]-(related:Concept)
WHERE related <> c
RETURN DISTINCT related.name AS concept,
       related.type AS type,
       length(path) AS hops,
       [r IN relationships(path) | type(r)] AS relationTypes
ORDER BY hops, related.confidence DESC
LIMIT 20;

// 4. Semantic similarity search (cosine on stored embeddings)
MATCH (c:Concept)
WHERE c.embedding IS NOT NULL
WITH c, gds.similarity.cosine(c.embedding, $queryEmbedding) AS similarity
WHERE similarity > $threshold
RETURN c.name AS concept, c.type AS type, similarity
ORDER BY similarity DESC
LIMIT 10;

// 5. Concept type distribution
MATCH (c:Concept)
RETURN c.type AS type, count(*) AS count, avg(c.confidence) AS avgConfidence
ORDER BY count DESC;

// 6. Most connected concepts (hub analysis)
MATCH (c:Concept)
WITH c, size((c)-[]-()) AS connections
RETURN c.name, c.type, connections
ORDER BY connections DESC
LIMIT 15;
