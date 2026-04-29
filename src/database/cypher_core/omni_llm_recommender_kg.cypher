-- Omni LLM Recommender Knowledge Graph (Cypher)
-- Ref: liuqidong07/Awesome-LLM-Enhanced-Recommender-Systems
CREATE (u:User {id: $userId, profile_emb: $profileEmb})
CREATE (i:Item {id: $itemId, text_emb: $textEmb, kg_emb: $kgEmb})
CREATE (u)-[:INTERACTED {score: $score, source: $source, timestamp: datetime()}]->(i)
WITH u, i
MATCH (u)-[r:INTERACTED]->(i)
WHERE r.source = 'knowledge_enhanced'
RETURN u.id, i.id, r.score ORDER BY r.score DESC LIMIT 10;
