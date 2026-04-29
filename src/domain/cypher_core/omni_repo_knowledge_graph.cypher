// Omni GitHub Repository Knowledge Graph (Database Layer)
// Cypher logic for graph relationship mapping of absorbed repos.

CREATE CONSTRAINT repo_id_unique ON (r:Repository) ASSERT r.id IS UNIQUE;

MATCH (o:Owner {name: $owner_name})
MERGE (r:Repository {id: $repo_id, name: $repo_name, language: $language})
MERGE (o)-[:OWNS]->(r)
WITH r
UNWIND $topics AS topic
MERGE (t:Topic {name: topic})
MERGE (r)-[:HAS_TOPIC]->(t)
RETURN r;
