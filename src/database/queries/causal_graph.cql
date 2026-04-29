MATCH (c:Confounder)-[:INFLUENCES]->(t:Treatment)
MATCH (c)-[:INFLUENCES]->(o:Outcome)
MATCH (t)-[:CAUSES]->(o)
RETURN c, t, o
