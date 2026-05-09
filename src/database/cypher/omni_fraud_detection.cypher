// OMNI Graph Database Query (Cypher)
// Detects cyclic transaction patterns indicative of money laundering

MATCH (u1:User)-[t1:TRANSFERRED]->(u2:User)
MATCH (u2)-[t2:TRANSFERRED]->(u3:User)
MATCH (u3)-[t3:TRANSFERRED]->(u1)
WHERE t1.amount > 10000 AND t2.amount > 10000 AND t3.amount > 10000
  AND duration.between(t1.timestamp, t3.timestamp).days < 2
WITH u1, u2, u3, t1, t2, t3
MERGE (u1)-[:FLAGGED_FOR_FRAUD {reason: "Cyclic High-Volume Transfer", confidence: 0.95}]->(u2)
RETURN u1.id, u2.id, u3.id, t1.amount
