-- Omni KoPA Knowledge Graph Schema (Cypher)
-- Ref: zjukg/KoPA — ACM MM 2024
CREATE CONSTRAINT kopa_entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE;
CREATE (e1:Entity {entity_id: 'entity_1', name: 'Albert Einstein', type: 'Person'})
CREATE (e2:Entity {entity_id: 'entity_2', name: 'Theory of Relativity', type: 'Theory'})
CREATE (e3:Entity {entity_id: 'entity_3', name: 'Princeton University', type: 'Organization'})
CREATE (e1)-[:DEVELOPED {confidence: 0.99}]->(e2)
CREATE (e1)-[:AFFILIATED_WITH {confidence: 0.95}]->(e3);
