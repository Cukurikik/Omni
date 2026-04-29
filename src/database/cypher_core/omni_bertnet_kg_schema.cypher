-- Omni BertNet KG Schema (Cypher)
-- Ref: tanyuqian/knowledge-harvest-from-lms — ACL 2023
CREATE (h:Entity {name: $headName, type: 'head'})
CREATE (t:Entity {name: $tailName, type: 'tail'})
CREATE (h)-[:HAS_RELATION {relation: $relationType, confidence: $confidence, source: 'bertnet'}]->(t)
WITH h, t
MATCH (h)-[r:HAS_RELATION]->(t) WHERE r.confidence > 0.5
RETURN h.name, r.relation, t.name, r.confidence ORDER BY r.confidence DESC;
