// @omni-domain Business Layer (KG-RAG Cypher)
MATCH (u:User)-[:QUERIED]->(d:Document) WHERE d.topic = $topic RETURN u.name, d.title, d.score ORDER BY d.score DESC LIMIT 10;
MATCH (e1:Entity)-[r:RELATED_TO]->(e2:Entity) WHERE e1.name = $seed RETURN e1, r, e2;
MERGE (d:Document {id: $docId}) SET d.title = $title, d.embedding = $embedding, d.indexed_at = datetime();
