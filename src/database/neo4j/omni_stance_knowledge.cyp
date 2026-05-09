// OMNI Framework - Neo4j Cypher Queries for Stance Detection Knowledge Graph

// Create initial entities and relationships
MERGE (cc:Concept {name: 'Climate Change', type: 'Global Issue'})
MERGE (ct:Policy {name: 'Carbon Tax', type: 'Economic Policy'})
MERGE (cc)-[:MITIGATED_BY]->(ct)

// Insert a user's extracted stance from the KE-MLM model
MERGE (u:User {id: 'user_9981'})
MERGE (u)-[:HAS_STANCE {sentiment: 'Favor', confidence: 0.92}]->(cc)
MERGE (u)-[:HAS_STANCE {sentiment: 'Against', confidence: 0.88}]->(ct)

// Query: Find users with contradictory stances based on knowledge graph relationships
MATCH (u:User)-[s1:HAS_STANCE]->(c:Concept)-[:MITIGATED_BY]->(p:Policy)
MATCH (u)-[s2:HAS_STANCE]->(p)
WHERE s1.sentiment = 'Favor' AND s2.sentiment = 'Against'
RETURN u.id AS UserID, c.name AS SupportedConcept, p.name AS OpposedPolicy
