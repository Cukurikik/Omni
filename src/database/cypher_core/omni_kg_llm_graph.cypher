// Omni KG-LLM Graph (Cypher)
// Database Layer: Knowledge graph triple storage and completion queries.
// Ref: yao8839836/kg-llm

CREATE CONSTRAINT entity_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE;

// Insert predicted triple
MERGE (h:Entity {name: $head})
MERGE (t:Entity {name: $tail})
MERGE (h)-[r:RELATION {type: $relation, score: $score}]->(t)
RETURN h.name, type(r), t.name, r.score;
