MATCH (n:Concept)-[:IMPLIES]->(m:Concept) RETURN n, m LIMIT 50;
