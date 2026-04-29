// OMNI bRAG-langchain: Knowledge Graph Schema (Cypher)
// Constructs the fundamental topological layout for Agentic RAG traversals in Neo4j.
// Source: bragai/bRAG-langchain

// 1. Create Constraints
CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT doc_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE;

// 2. Clear previous test data (Optional / Admin only)
// MATCH (n) DETACH DELETE n;

// 3. Ingest Graph Schema Structure
// A Document HAS_CHUNK Chunk
// A Chunk EXTRACTS Entity
// An Entity RELATES_TO Entity

// Example Ingestion query (called via Database Driver from Python layer)
/*
UNWIND $chunks AS chunk
MERGE (c:Chunk {id: chunk.id})
SET c.text = chunk.text, c.embedding = chunk.embedding

WITH c, chunk
MERGE (d:Document {id: chunk.document_id})
MERGE (d)-[:HAS_CHUNK]->(c)

WITH c, chunk
UNWIND chunk.entities AS entity
MERGE (e:Entity {name: entity.name})
SET e.type = entity.type
MERGE (c)-[:EXTRACTS]->(e)
*/

// 4. Vector Indexing for RAG Retrieval
// Requires Neo4j Graph Data Science or Vector Index capabilities
CREATE VECTOR INDEX chunk_embedding IF NOT EXISTS
FOR (c:Chunk) ON (c.embedding)
OPTIONS {indexConfig: {
 `vector.dimensions`: 1536,
 `vector.similarity_function`: 'cosine'
}};

// 5. Agentic RAG Traversal Example
// Find similar chunks, then traverse to connected entities to expand context
/*
CALL db.index.vector.queryNodes('chunk_embedding', 5, $query_embedding)
YIELD node AS c, score
MATCH (c)-[:EXTRACTS]->(e:Entity)-[r:RELATES_TO]-(e2:Entity)
RETURN c.text AS context, collect(e.name + ' ' + type(r) + ' ' + e2.name) AS graph_context, score
*/
